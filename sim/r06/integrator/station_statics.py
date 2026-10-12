"""Copied revision2 96-start solver driver, new scene and output namespace."""
from pathlib import Path
source=Path(__file__).with_name('rescue_statics.py').read_text()
source=source.replace('from rescue_spec import *','from station_spec import *').replace("v2/statics","v3/statics").replace("v2/models","v3/models").replace("v2/audit","v3/audit")
source=source.replace("(H/'v3/statics').glob(f'L{a.warm_layout}","(H/('history/v2/v2/statics' if a.warm_layout==17 else 'v3/statics')).glob(f'L{a.warm_layout}")
source=source.replace('warm_cell=Workcell(a.warm_layout,None,loc)','warm_cell=rc.Workcell(a.warm_layout,None,loc) if a.warm_layout==17 else Workcell(a.warm_layout,None,loc)')
anchor=' for k in range(a.seed_lo,a.seed_hi):'
inject='''
 # A checked motion supplies different IK branches; it is a seed, not proof
 # for this new scene. Preserve96 independent perturbations and full recheck.
 motion_warm=[]
 for mp in sorted((H/'v3/motion').glob('L*_persistent.json')):
  mr=json.loads(mp.read_text())
  for st in mr.get('states',[]):
   if not st['event'].endswith(('_key_descent','_seat','_loaded_lift','_empty_retreat')):continue
   z=empty.q0.copy()
   for n in ARM:
    if n in st['every_joint']:z[empty.qa[n]]=st['every_joint'][n][0]
   pp,rr=empty.pose(z)
   if np.linalg.norm(pp-target)<.025:motion_warm.append(dict(pass_=True,poses=[dict(q=z.tolist())]))
 if motion_warm:warm=motion_warm;warm_cell=empty
'''
source=source.replace(anchor,inject+anchor)
# Seeds from a previous geometry are hints only; every final pose re-solved.
exec(compile(source,'<copied v2 static driver / v3 scene>', 'exec'))
