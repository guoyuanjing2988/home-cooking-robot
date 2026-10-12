"""Search multiple robust park goals from the working posture, then connect them."""
import os,sys,json,runpy,hashlib,time,math,xml.etree.ElementTree as E
from pathlib import Path
ID=sys.argv[1];os.environ['R07_LAYOUT']=ID;H=Path(__file__).resolve().parent;O=H/'results';began=time.monotonic();attempts=[]
import runtime_v6_r07 as v
from idle_model_v6_r07 import completed_scene
original_scene=v.scene
inside=False
def populated_scene(i):
 global inside
 if i!=58 or inside:return original_scene(i)
 inside=True
 try:return completed_scene()[0]
 finally:inside=False
v.scene=populated_scene
import numpy as np,mujoco
from motion_v6_r07 import Planner,mo
from point_bound import PointBound
saved=json.loads((O/'static_v6'/ID/'0.json').read_text());working=np.array(saved['witness']['poses'][0]['q']);idle=json.loads((O/'layouts'/f'{ID}_idle.json').read_text())
source=(H/'park_single_v4_r07.py').read_text().replace('runtime_v4_r07','runtime_v6_r07');marker="q=np.array(p['q'])";source=source.replace(marker,"q=np.array(json.loads((O/'static_v6'/v.ID/'0.json').read_text())['witness']['poses'][0]['q']);q[ch.qa['R_jaw_minus']]=0;q[ch.qa['R_jaw_plus']]=0")
source=source.replace('np.maximum(.241-lo[ids,1],0)','np.maximum(.250-lo[ids,1],0)').replace('np.maximum(hi[ids,1]-.589,0)','np.maximum(hi[ids,1]-.580,0)').replace('np.maximum(hi[ids,2]-1.34,0)','np.maximum(hi[ids,2]-1.330,0)').replace('dist<needs+.004','dist<needs+.014').replace('float(needs[k]+.004)','float(needs[k]+.014)').replace('float(needs[k])+.001-gap','float(needs[k])+(.011 if needs[k]>0 else .001)-gap')
for number,seed in enumerate((7521,7522,7523,7524,7525,7526)):
 if time.monotonic()-began>920:break
 os.environ['R07_PARK_SECONDS']='70';candidate_suffix=f'_park_alternative_{number}'
 code=source.replace('for seed in (711,712,713,714,715,716):',f'for seed in ({seed},):').replace("rt.write('layouts/'+v.ID+'_park_full.json',out)",f"rt.write('layouts/'+v.ID+'{candidate_suffix}.json',out)")
 exec(compile(code,str(H/'park_alternative_generated.py'),'exec'),{'__name__':'__main__','__file__':str(H/'park_single_v4_r07.py')})
 candidate=json.loads((O/'layouts'/f'{ID}{candidate_suffix}.json').read_text());row=dict(candidate_file=f'results/layouts/{ID}{candidate_suffix}.json',seed=seed,snapshot_pass=candidate['pass_'],pass_=False,source_static_sha256=hashlib.sha256((O/'static_v6'/ID/'0.json').read_bytes()).hexdigest(),start_q=working.tolist())
 if candidate['pass_']:
  ch=v.scene(len(v.items)-1);root=E.fromstring((H/idle['model_xml']).read_text());world=root.find('worldbody')
  for g in list(world.findall('geom')):
   if g.get('name','').startswith('idle_full_sweep_cover_'):world.remove(g)
  ch.xml=E.tostring(root,encoding='unicode');motion_model=f'models/{ID}_alternate_fold_closed_doors.xml';(H/motion_model).write_text(ch.xml);row['motion_model_xml']=motion_model;row['motion_model_sha256']=hashlib.sha256(ch.xml.encode()).hexdigest();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False;park=mo.shortq(ch,working,np.array(candidate['q']));v.s.PARK=park.copy();pb=PointBound(ch);pl=Planner(ch,{},seed=seed+100,seconds=65);result=pl.plan(working,park,{},{});row['planner']=result;states=[];ok=result['ok'];step=0.;ratio=0.
  if ok:
   for si,(a,b) in enumerate(zip(np.array(result['path']),np.array(result['path'])[1:])):
    bound=pb.segment_bound(a,b);n=max(1,math.ceil(bound/.004));step=max(step,bound/n)
    for k in range(n+1):
     q=a+(b-a)*k/n;ok=pl.state(q,{}) and all(not ch.m.jnt_limited[ch.jid[name]] or ch.m.jnt_range[ch.jid[name],0]-1e-8<=q[ix]<=ch.m.jnt_range[ch.jid[name],1]+1e-8 for name,ix in ch.qa.items());load=ch.torque_multi(q,{}, {})['ratio'];ratio=max(ratio,load);ok=ok and load<=1;states.append(dict(q=q.tolist(),segment=si,alpha=k/n))
     if not ok:break
    if not ok:break
   if ok:ok=all(pl.state(np.array(state['q']),{}) for state in reversed(states))
  row.update(pass_=ok,states=states,states_checked=len(states),max_point_step_mm=step*1000,max_envelope_ratio=ratio,park_q=park.tolist())
  if ok:
   candidate['q']=park.tolist();(O/'layouts'/f'{ID}_park_full.json').write_text(json.dumps(candidate,indent=2));row['requires_final_snapshot_refresh']=True
 attempts.append(row);(O/'layouts'/f'{ID}_fold_alternatives_v6.json').write_text(json.dumps(dict(layout=ID,attempts=attempts,pass_=any(a['pass_'] for a in attempts),model_xml=idle['model_xml'],model_sha256=hashlib.sha256((H/idle['model_xml']).read_bytes()).hexdigest(),executed_meal_end_return=False,scope='Alternative whole-arm park goals seek10mm reserve beyond gates. Park snapshot uses full door sweeps at10mm for every robot part. Motion uses closed leaves and normal gaps only; final meal not executed.'),indent=2));print('ALTERNATE_FOLD',number,row['snapshot_pass'],row['pass_'],flush=True)
 if row['pass_']:break
