"""Mechanical, reproducible robot-only adaptation, with full unified diff and AST audit."""
import re,difflib,hashlib,ast,json
from pathlib import Path
HERE=Path(__file__).resolve().parent; INPUT=HERE.parents[2]/'inputs/prep_checker.py'
s=INPUT.read_text(encoding='utf-8'); orig=s
s=s.replace('import argparse','import copy\nimport argparse')
s=s.replace('Each worker is limited to 1140 seconds and 1900 MiB; at most four workers.',
 'Use concept/run.py: at most two foreground CPU workers, each 1140 seconds and 1900 MiB.\nThe retained legacy mobile-base CLI is disabled.')
s=s.replace('if __name__ == "__main__": main()', 'if __name__ == "__main__": raise SystemExit("Use run.py; the legacy mobile-base CLI is disabled.")')
start=s.index('SIM = HERE.parents[1]'); end=s.index('PAD = ',start)
s=s[:start]+'''from model import build, CONFIG, SIDES
TEMPLATE, META = build()
MODEL = HERE / "models" / "standalone.xml"
LIM = META["torque_limits"]
ACM_NAMES = META["disabled_robot_pairs"]
BASE = META["base"]
TORSO = []
ARMS = META["arms"]
JOINTS = sum(ARMS.values(), [])
JAWS = META["jaws"]
def configure(config):
    global TEMPLATE, META, LIM, ACM_NAMES, BASE, ARMS, JOINTS, JAWS
    TEMPLATE, META = build(config)
    LIM=META["torque_limits"]; ACM_NAMES=META["disabled_robot_pairs"]
    BASE=META["base"]; ARMS=META["arms"]; JOINTS=sum(ARMS.values(), []); JAWS=META["jaws"]

'''+s[end:]
s=s.replace('tree = ET.parse(MODEL); root = tree.getroot(); world = root.find("worldbody")',
 'tree = copy.deepcopy(TEMPLATE); root = tree.getroot(); world = root.find("worldbody")')
s=s.replace('rroot = root(m.jnt_bodyid[self.jid["base_x"]])','rroot = root(m.body("rail_structure").id)')
s=s.replace('n.startswith(("R_held_", "L_held_"))','n.startswith(("R_held_", "L_held_", "C_held_"))')
s=s.replace('return "R" if n.startswith(("r_", "right")) else "L" if n.startswith(("l_", "left")) else None',
 'return "R" if n.startswith("r_") else "L" if n.startswith("l_") else "C" if n.startswith("c_") else None')
s=s.replace('if not ra and not rb: continue\n            if (self.held',
 'if not ra and not rb: continue\n            # Sole added intended contact: dedicated wall mounting brackets.\n            if "north_wall" in (self.gnames[a], self.gnames[b]) and any(self.gnames[g].startswith("wall_mount_") for g in (a,b)): continue\n            if (self.held')
start=s.index('    def floor_margin');end=s.index('    def target_rotation',start)
s=s[:start]+'''    def floor_margin(self, q):
        # No floor footprint exists: report minimum mechanical carriage travel margin.
        return min(min(q[self.qa[n]]-self.m.jnt_range[self.jid[n],0],
                       self.m.jnt_range[self.jid[n],1]-q[self.qa[n]]) for n in BASE if n.endswith("carriage_x"))

    def initial(self, rng, k):
        m=self.m; q=m.qpos0.copy()
        x=np.mean([p["R"]["pos"][0] for p in self.seg["poses"]])
        q[self.qa["R_carriage_x"]]=rng.uniform(max(-2.12,x-1.0),min(2.12,x+1.0))
        right_park=META["config"].get("parking","ends")=="right"
        q[self.qa["L_carriage_x"]]=2.12 if right_park else -2.12
        if "C" in ARMS:q[self.qa["C_carriage_x"]]=-2.12 if right_park else 2.12
        for side,names in ARMS.items():
            for nm in names:
                lo,hi=m.jnt_range[self.jid[nm]]
                q[self.qa[nm]]=(lo+hi)/2+rng.uniform(-.5,.5)*(hi-lo)*.5
            opening=self.desc["jaw_opening_m"] if side=="R" else .02
            for label in ("minus","plus"): q[self.qa[f"{side}_jaw_{label}"]]=opening/2
        if not hasattr(self, "parking"):
            self.parking={}; park_rng=np.random.default_rng(811)
            for side,names in ARMS.items():
                if side=="R":continue
                best_candidate=None;best_park_ratio=float("inf")
                for attempt in range(400):
                    candidate=q.copy()
                    for nm in names:
                        lo,hi=m.jnt_range[self.jid[nm]];candidate[self.qa[nm]]=park_rng.uniform(lo,hi)
                    bad=[h for h in self.forbidden(candidate) if any(n.startswith(side+"_") for n in h["pair"])]
                    if not bad:
                        self.d.qpos[:]=candidate;self.d.qvel[:]=0;mujoco.mj_forward(m,self.d)
                        ratio=max(abs(self.d.qfrc_bias[self.da[n]])/LIM[n]["continuous_Nm"] for n in names)
                        if ratio<best_park_ratio:best_park_ratio=ratio;best_candidate=candidate.copy()
                self.parking[side]=[best_candidate[self.qa[n]] for n in names] if best_candidate is not None else [q[self.qa[n]] for n in names]
        for side,values in self.parking.items():
            for nm,value in zip(ARMS[side],values):q[self.qa[nm]]=value
        self.d.qpos[:]=q; mujoco.mj_kinematics(m,self.d)
        return q,self.d.site_xpos[m.site("L_prep").id].copy()

'''+s[end:]
start=s.index('        if "L" not in hands:',s.index('    def solve'));end=s.index('        for _ in range(iters):',start)
s=s[:start]+'''        # Unused arms retain their sampled parking joints and carriage throughout the stroke.
        post = mink.PostureTask(m, cost=1e-3); post.set_target(q0.copy()); tasks.append(post)
        frozen = [self.da[n] for n in BASE + JAWS + sum([names for side,names in ARMS.items() if side not in hands], [])]
        freeze_limit = mink.VelocityLimit(m, {n: 0. for n in self.da if self.da[n] in frozen})
'''+s[end:]
s=s.replace('limits=[mink.ConfigurationLimit(m)])','limits=[mink.ConfigurationLimit(m), freeze_limit])')
# execution replaced by an independently bounded driver; admission code untouched.
dest=HERE/'checker.py';dest.write_text(s,encoding='utf-8')
audit=HERE/'audit';audit.mkdir(exist_ok=True)
(audit/'checker.diff').write_text(''.join(difflib.unified_diff(orig.splitlines(True),s.splitlines(True),fromfile='inputs/prep_checker.py',tofile='concept/checker.py')),encoding='utf-8')
def funcs(code):
    t=ast.parse(code);out={}
    for n in t.body:
        if isinstance(n,(ast.FunctionDef,ast.ClassDef)):
            if isinstance(n,ast.ClassDef):
                for f in n.body:
                    if isinstance(f,ast.FunctionDef):out[n.name+'.'+f.name]=ast.dump(f,include_attributes=False)
            else:out[n.name]=ast.dump(n,include_attributes=False)
    return out
a,b=funcs(orig),funcs(s)
unchanged=[k for k in a if a[k]==b.get(k)]; changed=[k for k in a if a[k]!=b.get(k)]
(audit/'checker_ast.json').write_text(json.dumps(dict(input_sha256=hashlib.sha256(INPUT.read_bytes()).hexdigest(),unchanged=unchanged,changed=changed),indent=2))
print('UNCHANGED',len(unchanged),'CHANGED',changed)
