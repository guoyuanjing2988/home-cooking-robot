import os,sys,json,collections
os.environ['R07_LAYOUT']=sys.argv[1]
import runtime_v2_r07 as v
import numpy as np,mujoco
ch=v.scene(int(sys.argv[2]) if len(sys.argv)>2 else 0)
q=ch.m.qpos0.copy();ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d)
hits,mins,audit=v.f.contacts(ch,q)
def movable(g):
 b=int(ch.m.geom_bodyid[g])
 while b:
  if ch.m.body_jntnum[b]:return True
  b=int(ch.m.body_parentid[b])
 return False
fixed=[h for h in hits if all(not movable(ch.gnames.index(n)) for n in h['pair'])]
print('FIXED',json.dumps(fixed,indent=2))
print('GEOMETRY',json.dumps([g for g in v.P['installed_geometry'] if g['name'].startswith(('presence','secondary','dock'))],indent=2))
print('ITEMS',json.dumps([dict(index=i,key=k,station=sg['station'],poses=sg['poses']) for i,(ph,sg,k) in enumerate(v.items) if i in (0,1,2,9,18,24,35,40,80,100,104)],indent=2))
(v.O/'layouts'/f'{v.ID}_fixed_probe.json').write_text(json.dumps(dict(fixed=fixed,minima=mins),indent=2))
