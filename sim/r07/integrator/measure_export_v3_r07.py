"""Executed-simulation evidence only; incomplete deployment is labelled as such."""
import os,sys,json,math,hashlib,runpy
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';ID=sys.argv[1];R=H/'renders';(R/'v3').mkdir(exist_ok=True)
accepted=[json.loads(p.read_text()) for p in (O/'motion_v2'/ID).glob('internal_*.json') if json.loads(p.read_text()).get('ok')]
if accepted:
 source=(H/'measure_export_v2_r07.py').read_text().replace("R/'v2'","R/'v3'").replace("'v2/'","'v3/'").replace('manifest_v2.json','manifest_v3.json')
 source=source.replace("'ALL FIVE DOORS OPEN / POPULATED PARK AND FOLD FAIL'","'ALL DOORS OPEN / PARK SNAPSHOT PASS / COMPLETE FOLD UNVERIFIED'")
 source=source.replace("'FULL OEM ARMS AND STORED OBJECTS / REJECTED PARK'","'FULL OEM ARMS / POPULATED PARK SNAPSHOT PASS / MEAL FAIL'")
 source=source.replace("selected=next((r for r in accepted if r['index']==14),accepted[0])","selected=max(accepted,key=lambda r:r['final_replay'].get('states_checked',0))")
 source=source.replace("data.update(resolution=size,samples=4,camera_scale=scale);path.write_text(json.dumps(data))", "data.update(resolution=size,samples=4,camera_scale=scale);data['geoms']=[g for g in data['geoms'] if not g['name'].startswith('idle_full_sweep_cover_')];path.write_text(json.dumps(data))")
 source=source.replace("schema='r07.v2.clearance-reserves'", "schema='r07.v3.clearance-reserves'")
 a=source.index("for candidate in ('L18','L19'):");b=source.index('segments=[]',a);source=source[:a]+source[b:]
 derivative=H/'measure_export_v3_internal_r07.py';derivative.write_text(source);runpy.run_path(str(derivative));sys.exit(0)
os.environ['R07_LAYOUT']=ID
import numpy as np,mujoco
import runtime_v2_r07 as v
from motion_v2_r07 import Planner
from point_bound import PointBound
from render_setup import export
def read(n):return json.loads((O/n).read_text())
def write(n,x):(O/n).write_text(json.dumps(x,indent=2,allow_nan=False))
def load(path):
 ch=object.__new__(v.Checker);ch.desc=v.s.ck.hand([0,0,1],held='empty');ch.bind_model(mujoco.MjModel.from_xml_path(str(H/path)));ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False;return ch
def duration(ch,a,b,pb):
 t=0.
 for name,ix in ch.qa.items():
  d=abs(b[ix]-a[ix]);speed=.1 if 'carriage' in name else .35;acc=.3 if 'carriage' in name else .35
  t=max(t,2*math.sqrt(d/acc) if d<=speed*speed/acc else d/speed+speed/acc)
 d=pb.segment_bound(a,b);return max(t,2*math.sqrt(d/.3) if d<=.05**2/.3 else d/.05+.05/.3)
fold=read(f'layouts/{ID}_fold_continuation.json');options=[(i,a) for i,a in enumerate(fold['attempts']) if len(a['path'])>1 and a.get('states_checked',0)>0];assert options,'No executed checked movement available; cannot fabricate a frame strip.'
ai,attempt=max(options,key=lambda x:x[1]['states_checked']);ch=load(fold['model_xml']);pb=PointBound(ch);path=np.array(attempt['path']);pl=Planner(ch,{});states=[];reserve={};maxstep=0.;ratios=[];times=[]
for si,(a,b) in enumerate(zip(path,path[1:])):
 times.append(duration(ch,a,b,pb));bound=pb.segment_bound(a,b);n=max(1,math.ceil(bound/.004));maxstep=max(maxstep,bound/n)
 for k in range(n+1):
  q=a+(b-a)*k/n;assert pl.state(q,{}),pl.last
  assert all(not ch.m.jnt_limited[ch.jid[name]] or ch.m.jnt_range[ch.jid[name],0]-1e-8<=q[ix]<=ch.m.jnt_range[ch.jid[name],1]+1e-8 for name,ix in ch.qa.items())
  tq=ch.torque_multi(q,{},{});assert tq['ratio']<=1;ratios.append(tq['ratio']);states.append(dict(segment=si,alpha=k/n,q=q.tolist()))
  for cat,ix in ch.bounds.catids.items():
   lower=ch.bounds.last_lower[ix];keep=lower<1000.;reserve.setdefault(cat,[]).extend(((lower[keep]-ch.bounds.need[ix][keep])*1000).tolist())
for state in reversed(states):assert pl.state(np.array(state['q']),{}),pl.last
validation=dict(schema='r07.v3.accepted-prefix',layout=ID,ok=True,complete_fold_unfold_pass=attempt['pass_'],meal_pass=False,source_file=f'results/layouts/{ID}_fold_continuation.json',attempt=ai,model_xml=fold['model_xml'],model_sha256=hashlib.sha256((H/fold['model_xml']).read_bytes()).hexdigest(),path=path.tolist(),states=states,states_checked=len(states),max_point_step_mm=maxstep*1000,max_hold_ratio=max(ratios),duration_s=sum(times),segment_times_s=times,scope='Independently replayed actual simulated deployment PREFIX, forward and reverse. The requested full deployment target was not reached; not a complete fold, canonical stroke or meal.')
write('executed_prefix.json',validation)
stats={cat:dict(pair_state_count=len(x),min_mm=min(x),p05_mm=float(np.percentile(x,5)),median_mm=float(np.median(x)),p95_mm=float(np.percentile(x,95)),max_mm=max(x)) for cat,x in reserve.items()}
idle=read('idle.json');write('clearance.json',dict(schema='r07.v3.clearance-reserves',layout=ID,scope=validation['scope'],sample_count=len(states),max_point_step_mm=maxstep*1000,distribution=stats,distribution_method='Eligible pair/state conservative lower reserves; intended-contact sentinels excluded. Far pairs dominate percentiles; minima govern. Includes10mm robot/door-sweep gate.',meal_clearance_distribution=None,idle_snapshot_minima=idle['min_clearance'],numeric_tolerance_m=1e-6))
schedule=read('schedule.json');schedule.update(accepted_internal_paths=[],auxiliary_executed_path_time_s=sum(times),auxiliary_scope=validation['scope'],auxiliary_segment_times_s=times,auxiliary_source='results/executed_prefix.json',timing_method='Rest-to-rest segments: joints0.35rad/s and0.35rad/s2; rail0.1m/s and0.3m/s2; all-geometry point bound0.05m/s and0.3m/s2. This is one independently checked simulated prefix, never a meal makespan.');write('schedule.json',schedule)
manifest=[]
def emit(c,q,name,status,label,focus,scale,size):
 export(c,q,'v3/'+name,status,focus=focus,label=label);p=R/'v3'/f'{name}.scene.json';data=json.loads(p.read_text());data.update(config=read('config.json'),resolution=size,samples=4,camera_scale=scale);data['geoms']=[g for g in data['geoms'] if not g['name'].startswith('idle_full_sweep_cover_')];p.write_text(json.dumps(data));manifest.append(dict(name=name,scene='v3/'+name+'.scene.json',image='v3/'+name+'.png',q=np.array(q).tolist(),status=status))
park=load(idle['doors_model_xml']);qclosed=np.r_[idle['q'],np.zeros(len(idle['doors']))];qopen=np.r_[idle['q'],np.full(len(idle['doors']),np.pi/2)]
emit(ch,path[-1],'overview',ID+' / CHECKED DEPLOYMENT PREFIX / FULL MEAL FAIL','overview',[-.3,0,1.2],5.5,[1440,960])
emit(park,qopen,'parked_doors_open','ALL DOORS OPEN / PARK SNAPSHOT PASS / FULL FOLD FAIL','parked',[-.3,0,1.2],5.5,[1440,960])
emit(park,qclosed,'under_cabinet_band','FULL OEM GEOMETRY / PARK SNAPSHOT PASS / DOOR GATE10MM','band',[-.75,.4,1.20],1.85,[1440,960])
passing=read('passing.json');pch=load(passing['model_xml']);emit(pch,np.array(passing['q_crossing']),'passing','ONE-LANE ORDER SWAP REJECTED / POSED CROSSING NOT EXECUTED','passing',[-.3,0,1.2],5.5,[1440,960])
segments=[];total=0.
for si,(a,b) in enumerate(zip(path,path[1:])):
 length=pb.segment_bound(a,b);segments.append((total,total+length,si,a,b));total+=length
frames=[]
for i,position in enumerate(np.linspace(0,total,24)):
 start,end,si,a,b=next((s for s in segments if s[1]>=position),segments[-1]);u=(position-start)/max(1e-15,end-start);q=a+(b-a)*u;assert pl.state(q,{})
 emit(ch,q,f'frame_{i:02}',f'CHECKED PREFIX {i+1}/24 / COMPLETE FOLD AND MEAL FAIL','Empty-hand deployment prefix',[-.45,.25,1.1],2.4,[500,320]);frames.append(dict(frame=i,segment=si,alpha=float(u),q=q.tolist()))
write('frame_manifest.json',dict(layout=ID,stroke='Empty-hand deployment PREFIX; full fold failed',model_xml=fold['model_xml'],path_file='results/executed_prefix.json',frames=frames,executed_meal=False,prefix_only=True,scope=validation['scope']))
(R/'manifest_v3.json').write_text(json.dumps(dict(CPU_only=True,maximum_px=1500,views=manifest,frame_count=24,source='Unscaled saved MJCF collision solids and checked q. Failed full fold and posed passing honestly labelled. Frame strip is a simulated checked prefix only.',visual_omissions=['Opposite wall/cabinets, symbolic access masks and door-sweep supersets hidden for display only; all remain in checking.']),indent=2))
print('PREFIX_EXPORT',ID,len(states),'states',sum(times),'s',flush=True)
