"""Golden-phase study (orchestrator-written): carrot slicing on a clamped mandoline with a food holder.

Question: can the robot stand at the counter, hold the food holder in the right hand and push it over
the mandoline for a full 200 mm stroke, with joints inside their continuous ratings and no forbidden
collisions? The left arm parks beside the torso; the mandoline is clamped (non-slip feet / clamp).

Robots: 'r1pro' (Galaxea R1 Pro from its public URDF, T05) and 't06' (our architecture-B candidate).
Contact rules (real gaps): arm/torso/base vs environment or the other arm >= 10 mm; gripper bodies and
the held holder >= 5 mm; parts of the same arm or torso >= 0 (no interpenetration); parent/child and
same-rigid-body pairs and ACM pairs are skipped; holder vs mandoline/board/counter is intended contact.
Loads: robot gravity, 0.55 kg holder+carrot, and at the holder's food face (80 mm beyond the grasp along
the approach axis): feed reaction -F along the stroke, +20 N up, +/-10 N lateral; F in {40, 70, 100} N.
Usage: python mandoline_golden.py <robot> [seeds]
"""
import json, sys, time
from pathlib import Path
import numpy as np
import mujoco, mink

HERE = Path(__file__).resolve().parent
import checker as ck
from model import SIDES
CONFIG = json.loads(Path(sys.argv[1]).read_text())
ck.configure(CONFIG)
META = ck.META; LIM = ck.LIM; PAD = ck.PAD; BASE = ck.BASE
NAME = CONFIG["arm"] + "x" + str(CONFIG["count"])
MODEL_PATH = HERE / "models" / (NAME + "_golden_base.xml")
# Keep the complete T08 fixture/stored-tool scene. The golden holder is added below.
definition=ck.P06(); parking_checker=ck.Checker(definition,definition["segments"][0])
mujoco.mj_saveLastXML(str(MODEL_PATH),parking_checker.m)
import xml.etree.ElementTree as ET
tree=ET.parse(MODEL_PATH)
for b in tree.getroot().iter("body"):
    for child in list(b):
        if child.get("name", "").startswith("R_held_") or child.get("name") in ("R_work", "R_mass"):
            b.remove(child)
tree.write(MODEL_PATH,encoding="unicode")
C=dict(xml=MODEL_PATH,torso=ck.ARMS.get("C",[]),arm_r=ck.ARMS["R"],arm_l=ck.ARMS["L"],
       site_r="R_prep",site_l="L_prep",jaws=ck.JAWS)
acm_names=ck.ACM_NAMES
WALL=False
UPRIGHT = []   # R1 upper body hung on a wall carriage: base/lower torso are virtual
VIRTUAL = {"base_link", "wheel_motor_link1", "wheel_motor_link2", "wheel_motor_link3", "lidar_chassis_left_link",
           "imu_chassis_link", "torso_link1", "torso_link2", "torso_link3"}

STATION = np.array([0.45, 0.18, 0.865])   # clamped mandoline on the free counter left of the stove
DECK_Z = STATION[2] + 0.06
WORK = 0.08                               # grasp -> holder food face along the approach axis
HELD_KG = 0.55

m0 = mujoco.MjModel.from_xml_path(str(C["xml"])); d0 = mujoco.MjData(m0); mujoco.mj_forward(m0, d0)
sid0 = m0.site(C["site_r"]).id; tool_body = m0.body(m0.site_bodyid[sid0]).name
sp = m0.site_pos[sid0].copy()
APPROACH = sp / np.linalg.norm(sp) if np.linalg.norm(sp) > 1e-6 else np.array([1.0, 0, 0])   # tool frame

def build():
    spec = mujoco.MjSpec.from_file(str(C["xml"]))
    g = spec.worldbody.add_geom(); g.name = "golden_mandoline"; g.type = mujoco.mjtGeom.mjGEOM_BOX
    g.size = [0.165 + PAD, 0.06 + PAD, 0.03 + PAD]; g.pos = [STATION[0], STATION[1], STATION[2] + 0.03]
    tool = spec.find_body(tool_body)
    h = tool.add_geom(); h.name = "held_holder"; h.type = mujoco.mjtGeom.mjGEOM_SPHERE
    h.size = [0.065 + PAD, 0, 0]; h.pos = (sp + APPROACH * (WORK / 2 + 0.015)).tolist(); h.mass = 1e-6
    w = tool.add_site(); w.name = "R_work"; w.pos = (sp + APPROACH * WORK).tolist()
    return spec.compile()

m = build(); d = mujoco.MjData(m)
jid = {m.joint(i).name: i for i in range(m.njnt)}
qadr = lambda n: m.jnt_qposadr[jid[n]]
dadr = lambda n: m.jnt_dofadr[jid[n]]
gname = [m.geom(g).name for g in range(m.ngeom)]
gbody = m.geom_bodyid; weld = m.body_weldid[gbody]
def root(b):
    while m.body_parentid[b] != 0: b = m.body_parentid[b]
    return b
RROOT = root(m.body("rail_structure").id)
is_robot = np.array([root(gbody[g]) == RROOT for g in range(m.ngeom)])
bname = [m.body(gbody[g]).name.lower() for g in range(m.ngeom)]
def side(g):
    n = bname[g]
    return "R" if n.startswith("r_") else "L" if n.startswith("l_") else "C" if n.startswith("c_") else None
def is_gripper(g):
    return any(k in bname[g] for k in ("tool", "jaw", "finger", "gripper"))
HOLDER = gname.index("held_holder")
INTENDED = {gname.index(n) for n in ("golden_mandoline", "mandoline", "cutting_board", "board_mat", "counter_right") if n in gname}

ACM = {tuple(sorted((gname.index(a), gname.index(b)))) for a, b in acm_names if a in gname and b in gname}

def forbidden(q):
    d.qpos[:] = q; mujoco.mj_kinematics(m, d); mujoco.mj_comPos(m, d); mujoco.mj_collision(m, d)
    hits = []
    for c in d.contact[:d.ncon]:
        a, b = int(c.geom[0]), int(c.geom[1])
        ra, rb = is_robot[a], is_robot[b]
        if not ra and not rb: continue
        if "north_wall" in (gname[a],gname[b]) and any(gname[g].startswith("wall_mount_") for g in (a,b)): continue
        if WALL and (m.body(gbody[a]).name in VIRTUAL or m.body(gbody[b]).name in VIRTUAL): continue
        if HOLDER in (a, b) and ({a, b} & INTENDED): continue
        if weld[a] == weld[b] or tuple(sorted((a, b))) in ACM: continue
        wa, wb = weld[a], weld[b]
        if m.body_weldid[m.body_parentid[wa]] == wb or m.body_weldid[m.body_parentid[wb]] == wa: continue
        if "floor" in (gname[a], gname[b]) and (ra or rb) and not (HOLDER in (a, b)):
            other = b if gname[a] == "floor" else a
            if not any(k in bname[other] for k in ("arm", "tool", "gripper", "finger")): continue   # base/wheels on floor
        real = c.dist + 2 * PAD
        if ra and rb:
            if is_gripper(a) and is_gripper(b) and side(a) == side(b): continue   # the two jaws of one gripper close on the held tool
            need = 0.0 if side(a) == side(b) else 0.010
        else:
            rg = a if ra else b
            need = 0.005 if (is_gripper(rg) or rg == HOLDER) else 0.010
        if real < need - 1e-6: hits.append((gname[a], gname[b], round(real * 1000, 1), round(need * 1000)))
    return hits

def torque_ratios(q, F, lat):
    d.qpos[:] = q; d.qvel[:] = 0; mujoco.mj_forward(m, d)
    tau = d.qfrc_bias.copy()
    jp = np.zeros((3, m.nv)); jr = np.zeros((3, m.nv)); mujoco.mj_jacSite(m, d, jp, jr, m.site("R_work").id)
    tau -= jp.T @ (np.array([-F, lat, 20.0]) + np.array([0, 0, -HELD_KG * 9.81]))
    return {n: abs(tau[dadr(n)]) / LIM[n]["continuous_Nm"] for n in C["torso"] + C["arm_r"] + C["arm_l"] if n in LIM}

def grasp_rot(jaw_world):
    # Tool-frame approach axis -> world -Z; the remaining tool axes follow jaw_world.
    a_t = APPROACH; b_t = np.cross(a_t, [0, 0, 1.0]) if abs(a_t[2]) < 0.9 else np.cross(a_t, [1.0, 0, 0])
    b_t /= np.linalg.norm(b_t); c_t = np.cross(a_t, b_t)
    a_w = np.array([0, 0, -1.0]); b_w = np.array(jaw_world, float); c_w = np.cross(a_w, b_w)
    return np.column_stack([a_w, b_w, c_w]) @ np.column_stack([a_t, b_t, c_t]).T

def solve(q0, pos, R, lpark, frozen, iters=600):
    cfg = mink.Configuration(m, q=q0.copy())
    t = mink.FrameTask(C["site_r"], "site", position_cost=1.0, orientation_cost=0.5, lm_damping=1e-4)
    t.set_target(mink.SE3.from_rotation_and_translation(mink.SO3.from_matrix(R), pos))
    tl = mink.FrameTask(C["site_l"], "site", position_cost=0.05, orientation_cost=0.0, lm_damping=1e-4)
    tl.set_target(mink.SE3.from_translation(lpark))
    post = mink.PostureTask(m, cost=1e-3); post.set_target(q0.copy())
    frz = [dadr(n) for n in list(frozen) + C["jaws"] + C["arm_l"] + C["torso"]]
    freeze_limit=mink.VelocityLimit(m,{m.joint(j).name:0. for j in range(m.njnt) if m.jnt_dofadr[j] in frz})
    for _ in range(iters):
        v = mink.solve_ik(cfg, [t, tl, post], 0.05, "daqp", 1e-3, limits=[mink.ConfigurationLimit(m),freeze_limit])
        v[frz] = 0; cfg.integrate_inplace(v, 0.05)
        e = t.compute_error(cfg)
        if np.linalg.norm(e[:3]) < 1e-3 and np.linalg.norm(e[3:]) < 2e-3: break
    e = t.compute_error(cfg)
    return cfg.q.copy(), float(np.linalg.norm(e[:3])), float(np.degrees(np.linalg.norm(e[3:])))

def run(n, seed=0):
    rng = np.random.default_rng(seed)
    stroke = [STATION + [-0.10, 0, 0.06 + WORK], STATION + [0.10, 0, 0.06 + WORK]]
    out = []
    for k in range(n):
        q,lpark=parking_checker.initial(rng,k)
        R = grasp_rot([(0, 1, 0), (0, -1, 0), (1, 0, 0), (-1, 0, 0)][k % 4])
        frozen = BASE
        if WALL:
            ok = False
            if not UPRIGHT:
                for _ in range(20000):   # upright chest torso configurations: (torso q, chest offset in base frame)
                    qq = m.qpos0.copy()
                    for nm in C["torso"]:
                        lo, hi = m.jnt_range[jid[nm]]; qq[qadr(nm)] = rng.uniform(lo, hi)
                    d.qpos[:] = qq; mujoco.mj_kinematics(m, d)
                    Rm = d.body("torso_link4").xmat.reshape(3, 3); p = d.body("torso_link4").xpos.copy()
                    if Rm[2, 2] > float(os.environ.get("UPRIGHT_COS", "0.97")) and abs(Rm[1, 0]) < 0.1 and Rm[0, 0] > 0.5 and 1.05 <= p[2] <= 1.60:
                        UPRIGHT.append(([qq[qadr(nm)] for nm in C["torso"]], p - np.array([qq[qadr("base_x")], qq[qadr("base_y")], 0])))
            tq_, off = UPRIGHT[rng.integers(len(UPRIGHT))]
            if os.environ.get("WALLSIDE", "back") == "back":   # chest hung at the back wall, facing the room
                yaw = -np.pi / 2; chest = np.array([rng.uniform(STATION[0] - 0.5, STATION[0] + 0.5), rng.uniform(0.28, 0.45)])
            else:                                                 # chest hung over the counter front edge, facing the wall
                yaw = np.pi / 2; chest = np.array([rng.uniform(STATION[0] - 0.5, STATION[0] + 0.5), rng.uniform(-0.30, 0.0)])
            cy, sy = np.cos(yaw), np.sin(yaw)
            q[qadr("base_yaw")] = yaw
            q[qadr("base_x")] = chest[0] - (cy * off[0] - sy * off[1]); q[qadr("base_y")] = chest[1] - (sy * off[0] + cy * off[1])
            for nm, v in zip(C["torso"], tq_): q[qadr(nm)] = v
            d.qpos[:] = q; mujoco.mj_kinematics(m, d); ok = True
            if not ok: out.append(dict(k=k, why="no_wall_mount_sample")); continue
            frozen = BASE + C["torso"]
            lpark = np.array([d.body("torso_link4").xpos[0] + 0.30, 0.30, 1.30])
        q1, ep, eo = solve(q, stroke[0], R, lpark, frozen)
        if ep > 0.005 or eo > 3: out.append(dict(k=k, why=f"ik_start {ep*1000:.0f}mm {eo:.1f}deg")); continue
        q2, ep2, eo2 = solve(q1, stroke[1], R, lpark, frozen)
        if ep2 > 0.005 or eo2 > 3: out.append(dict(k=k, why=f"ik_end {ep2*1000:.0f}mm {eo2:.1f}deg")); continue
        hits = forbidden(q1) + forbidden(q2)
        tq = {}; tq_raw = {}
        for F in (40, 70, 100):
            worst, wj = 0, None
            for qq in (q1, q2):
                for lat in (-10, 10):
                    r = torque_ratios(qq, F, lat); j = max(r, key=r.get)
                    if r[j] > worst: worst, wj = r[j], j
            tq[F] = [round(worst, 3), wj]; tq_raw[F] = worst
        out.append(dict(k=k, ok=not hits, hits=hits[:4], torque=tq, base=[round(q1[qadr(x)], 3) for x in BASE],
                        q_start=q1.tolist(), q_end=q2.tolist(), torque_unrounded=tq_raw))
    return out

if __name__ == "__main__":
    t0 = time.time(); n = int(sys.argv[2]) if len(sys.argv) > 2 else 96
    res = run(n)
    ok = [r for r in res if r.get("ok")]; ik = [r for r in res if "torque" in r]
    print(f"[{NAME}] seeds {n}  ik-ok {len(ik)}  collision-free {len(ok)}  ({time.time()-t0:.0f}s)")
    for F in (40, 70, 100):
        pool = ok or ik
        b = min(pool, key=lambda r: r["torque"][F][0]) if pool else None
        print(f"  F={F:3d} N  best torque ratio {'(collision-free)' if ok else '(ignoring collisions)'}:", b["torque"][F] if b else None)
    tally = {}
    for r in res:
        key = r["why"].split()[0] if "why" in r else (f"{r['hits'][0][0]}~{r['hits'][0][1]}" if r.get("hits") else None)
        if key: tally[key] = tally.get(key, 0) + 1
    print("  failures:", sorted(tally.items(), key=lambda kv: -kv[1])[:8])
    result_dir=HERE/"results/golden";result_dir.mkdir(exist_ok=True)
    json.dump(dict(config=CONFIG,seeds=n,ik_seeds=len(ik),collision_free_seeds=len(ok),
      rated_admission_by_force={str(F):int(sum(r.get("ok",False) and r["torque_unrounded"][F]<=1 for r in res)) for F in (40,70,100)},
      rating_status=META["ratings"]["status"],rows=res),open(result_dir/f"{NAME}.json","w"),indent=1)
