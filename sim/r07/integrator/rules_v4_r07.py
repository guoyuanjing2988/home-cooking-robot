import os,sys,runpy
from pathlib import Path
H=Path(__file__).resolve().parent;ID=sys.argv[1];os.environ['R07_LAYOUT']=ID
import runtime_v4_r07 as v
v.s.PARK=v.scene(0).m.qpos0.copy()
source=(H/'rules_v3_r07.py').read_text().replace('import runtime_v2_r07 as v','import runtime_v4_r07 as v').replace('v.scene(104)','v.scene(len(v.items)-1)').replace('door_gate_regression_v3.json','door_gate_regression_v4.json').replace("runpy.run_path(str(v.H/'rules_r07.py'))","runpy.run_path(str(v.H/'rules_r07.py'))").replace('r07.v3.exact-active-contact-ledger','r07.v4.exact-active-contact-ledger').replace("f'results/layouts/{v.ID}_process.json'","f'results/layouts/{v.ID}_process_v4.json'")
exec(compile(source,str(H/'rules_v4_generated.py'),'exec'))
# Direct oriented mating-face policy checks, using the full dock frame and own
# held part identity. No working permissions on a nonworking transit path.
import numpy as np,mujoco,json
from types import SimpleNamespace
rows=[]
for i in (5,20):
 ch=v.scene(i);ch.set_contacts(v.items[i][1]['poses'][0]);mujoco.mj_forward(ch.m,ch.d)
 c=ch.allowed[0];g=ch.gnames.index(c['face']);part=ch.gnames.index('R_held_'+c['held_parts'][0]);R=ch.d.geom_xmat[g].reshape(3,3);center=ch.d.geom_xpos[g];sz=ch.m.geom_size[g]
 for label,p,n,expect in [('front',[0,0,sz[2]],[0,0,1],True),('back',[0,0,-sz[2]],[0,0,-1],False),('side',[sz[0],0,0],[1,0,0],False)]:
  contact=SimpleNamespace(geom=[g,part],pos=center+R@p,frame=np.r_[R@n,np.zeros(6)])
  answer=v.f.intentional(ch,contact);rows.append(dict(index=i,test=label,accepted=answer,expected=expect,pass_=answer==expect))
 ch.allowed=[dict(c,object_id='wrong_object')];contact=SimpleNamespace(geom=[g,part],pos=center+R@np.array([0,0,sz[2]]),frame=np.r_[R[:,2],np.zeros(6)])
 rows.append(dict(index=i,test='wrong_object',accepted=v.f.intentional(ch,contact),expected=False,pass_=not v.f.intentional(ch,contact)))
(v.O/'rotated_contact_regression_v4.json').write_text(json.dumps(dict(layout=ID,rows=rows,pass_=all(r['pass_'] for r in rows)),indent=2));assert all(r['pass_'] for r in rows)
