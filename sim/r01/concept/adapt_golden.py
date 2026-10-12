"""Generate a robot-pluggable copy of the binding golden script, preserving numerical rules."""
from pathlib import Path
import difflib,ast,json
HERE=Path(__file__).resolve().parent;inp=HERE.parents[2]/'inputs/mandoline_golden.py'
s=inp.read_text();orig=s
start=s.index('SIM = HERE.parent');end=s.index('UPRIGHT = ',start)
s=s[:start]+'''import checker as ck
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
'''+s[end:]
s=s.replace('RROOT = root(m.jnt_bodyid[jid["base_x"]])','RROOT = root(m.body("rail_structure").id)')
s=s.replace('return "R" if n.startswith(("r_", "right")) else "L" if n.startswith(("l_", "left")) else None','return "R" if n.startswith("r_") else "L" if n.startswith("l_") else "C" if n.startswith("c_") else None')
s=s.replace('acm_names = json.load(open(C["acm"]))["disabled_robot_pairs"]','')
s=s.replace('if not ra and not rb: continue\n        if WALL',
 'if not ra and not rb: continue\n        if "north_wall" in (gname[a],gname[b]) and any(gname[g].startswith("wall_mount_") for g in (a,b)): continue\n        if WALL')
s=s.replace('    frz = [dadr(n) for n in list(frozen) + C["jaws"]]',
 '    frz = [dadr(n) for n in list(frozen) + C["jaws"] + C["arm_l"] + C["torso"]]\n    freeze_limit=mink.VelocityLimit(m,{m.joint(j).name:0. for j in range(m.njnt) if m.jnt_dofadr[j] in frz})')
s=s.replace('limits=[mink.ConfigurationLimit(m)])','limits=[mink.ConfigurationLimit(m),freeze_limit])')
start=s.index('        q = m.qpos0.copy()',s.index('def run'));end=s.index('        R = grasp_rot',start)
s=s[:start]+'''        q,lpark=parking_checker.initial(rng,k)
'''+s[end:]
# WALL=False means the retained legacy torso branch is never entered.
s=s.replace('    t0 = time.time(); n = int(sys.argv[2]) if len(sys.argv) > 2 else 60',
 '    t0 = time.time(); n = int(sys.argv[2]) if len(sys.argv) > 2 else 96')
s=s.replace('    json.dump(res, open(HERE / f"mandoline_{NAME}.json", "w"), indent=1)',
 '''    result_dir=HERE/"results/golden";result_dir.mkdir(exist_ok=True)
    json.dump(dict(config=CONFIG,seeds=n,ik_seeds=len(ik),collision_free_seeds=len(ok),
      rated_admission_by_force={str(F):int(sum(r.get("ok",False) and r["torque_unrounded"][F]<=1 for r in res)) for F in (40,70,100)},
      rating_status=META["ratings"]["status"],rows=res),open(result_dir/f"{NAME}.json","w"),indent=1)''')
# Retain the original rounded display, with raw values for additional threshold reports.
s=s.replace('        tq = {}','        tq = {}; tq_raw = {}')
s=s.replace('            tq[F] = [round(worst, 3), wj]','            tq[F] = [round(worst, 3), wj]; tq_raw[F] = worst')
s=s.replace('q_start=q1.tolist(), q_end=q2.tolist()))','q_start=q1.tolist(), q_end=q2.tolist(), torque_unrounded=tq_raw))')
(HERE/'golden.py').write_text(s)
(HERE/'audit/golden.diff').write_text(''.join(difflib.unified_diff(orig.splitlines(True),s.splitlines(True),fromfile='inputs/mandoline_golden.py',tofile='concept/golden.py')))
print('golden adaptation written')
