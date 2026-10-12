"""Actual all-doors-open geometry of the successful late park snapshots."""
import os,json
os.environ['R07_LAYOUT']='L13'
import numpy as np,mujoco
import runtime_v2_r07 as v
from render_setup import export
R=v.H/'renders';manifest=json.loads((R/'manifest_v2.json').read_text())
for ID in ('L18','L19'):
 idle=json.loads((v.O/'layouts'/f'{ID}_idle.json').read_text());ch=object.__new__(v.Checker);ch.desc=v.s.ck.hand([0,0,1]);ch.bind_model(mujoco.MjModel.from_xml_path(str(v.H/idle['doors_model_xml'])));q=np.r_[idle['q'],np.full(len(idle['doors']),np.pi/2)]
 name=f'comparison_{ID}_parked';status=ID+' / '+('CLEAR PARK SNAPSHOT' if idle['snapshot_pass'] else 'PARK SNAPSHOT FAIL')+' / FOLD '+('PASS' if idle['pass_'] else 'NOT ACCEPTED')
 export(ch,q,'v2/'+name,status,focus=[-.3,0,1.2],label='parked');scene=R/'v2'/f'{name}.scene.json';data=json.loads(scene.read_text());data.update(config=json.loads((v.O/'layouts'/f'{ID}.json').read_text()),resolution=[1440,960],samples=4,camera_scale=5.5);scene.write_text(json.dumps(data));manifest['views']=[r for r in manifest['views'] if r['name']!=name];manifest['views'].append(dict(name=name,scene='v2/'+name+'.scene.json',image='v2/'+name+'.png',q=q.tolist(),status=status))
(R/'manifest_v2.json').write_text(json.dumps(manifest,indent=2));print('COMPARISON_EXPORT',len(manifest['views']),flush=True)
