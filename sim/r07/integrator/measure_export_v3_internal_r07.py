"""Timing, clearance and exact-state renders from admitted v2 internal paths."""
import os,sys,json,math,copy
os.environ['R07_LAYOUT']=sys.argv[1]
import numpy as np,mujoco
import runtime_v2_r07 as v
from motion_v2_r07 import Planner
from point_bound import PointBound
from render_setup import export
H=v.H;O=v.O;R=H/'renders';(R/'v3').mkdir(exist_ok=True)
def load(path):
 ch=object.__new__(v.Checker);ch.desc=v.s.ck.hand([0,0,1]);ch.bind_model(mujoco.MjModel.from_xml_path(str(path)));ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False;return ch
def duration(ch,a,b,pb,loaded=True):
 t=0.
 for name,ix in ch.qa.items():
  d=abs(b[ix]-a[ix]);speed=(.1 if loaded else .2) if 'carriage' in name else .35;acc=.3 if 'carriage' in name else .35
  t=max(t,2*math.sqrt(d/acc) if d<=speed*speed/acc else d/speed+speed/acc)
 d=pb.segment_bound(a,b);speed=.05;acc=.3
 return max(t,2*math.sqrt(d/acc) if d<=speed*speed/acc else d/speed+speed/acc)
accepted=[];reserve={};checked=0;maxstep=0.;schedules=[]
for file in sorted((O/'motion_v2'/v.ID).glob('internal_*.json')):
 r=json.loads(file.read_text())
 if not r['ok']:continue
 accepted.append(r);ch=v.scene(r['index']);sg=v.items[r['index']][1];pb=PointBound(ch);times=[]
 for ei,e in enumerate(r['edges']):
  times.append([duration(ch,a,b,pb) for a,b in zip(np.array(e['path']),np.array(e['path'])[1:])])
 planners={}
 for sample in r['final_replay']['states']:
  ei=sample['edge'];si=sample['segment'];alpha=sample['alpha'];e=r['edges'][ei];ha,hb=sg['poses'][ei:ei+2];hands=ha if si==0 and alpha==0 else hb if si==len(e['path'])-2 and alpha==1 else {side:dict(h,contacts=[c for c in h.get('contacts',[]) if c in hb.get(side,{}).get('contacts',[])]) for side,h in ha.items()}
  ch.working_stroke=sg['action']=='process';ch.contact_windows=e.get('contact_windows',[])
  if ei not in planners:planners[ei]=Planner(ch,hands,seconds=65)
  pl=planners[ei]
  assert pl.state(np.array(sample['q']),hands),(r['index'],sample)
  for cat,ix in ch.bounds.catids.items():
   # Allowed intended-contact pairs use an infinite sentinel, not a measured
   # reserve; exclude them from distribution rather than reporting1e9mm.
   lower=ch.bounds.last_lower[ix];keep=lower<1000.;reserve.setdefault(cat,[]).append((lower[keep]-ch.bounds.need[ix][keep])*1000)
  checked+=1
  if checked%100==0:print('CLEARANCE_STATES',checked,flush=True)
 maxstep=max(maxstep,r['final_replay']['max_point_step_mm']);schedules.append(dict(index=r['index'],stroke=r['stroke'],duration_s=sum(map(sum,times)),edge_segment_times_s=times,clock_origin_s=0,meal_clock=False,scope='Isolated simulated kinematic path; home-speed rest-to-rest segments, all arms and full geometry-point bound'))
stats={}
for cat,arrays in reserve.items():
 x=np.concatenate(arrays);stats[cat]=dict(pair_state_count=len(x),min_mm=float(min(x)),p05_mm=float(np.percentile(x,5)),median_mm=float(np.median(x)),p95_mm=float(np.percentile(x,95)),max_mm=float(max(x)))
idle=json.loads((O/f'layouts/{v.ID}_idle.json').read_text())
v.rt.write('clearance.json',dict(schema='r07.v3.clearance-reserves',layout=v.ID,scope='All independently replayed accepted isolated internal paths on populated template scenes. No full-meal distribution.',sample_count=checked,max_point_step_mm=maxstep,distribution=stats,distribution_method='All eligible non-permitted pair/state lower reserves. Intended-contact sentinel pairs excluded. Distant pairs dominate percentiles. AABB/GJK conservative bounds, not a continuous certificate.',numeric_tolerance_m=1e-6,meal_clearance_distribution=None,idle=dict(pass_=idle['pass_'],door_sweep_pass=idle['door_sweep_pass'],front_chain_gap_mm=10,front_chain_reserve_mm=0,failed_gaps_not_reserves=True)))
schedule=json.loads((O/'schedule.json').read_text());schedule.update(accepted_internal_paths=schedules,isolated_internal_duration_sum_s=sum(r['duration_s'] for r in schedules),timing_method='Per-segment rest-to-rest trapezoid/triangle at0.35rad/s and0.35rad/s2; loaded rail0.1m/s, acceleration0.3m/s2; all-geometry point-speed0.05m/s and0.3m/s2. This catalog does not have a connected meal clock.');v.rt.write('schedule.json',schedule)
assert accepted,'No accepted path available for an executed-path strip'
selected=max(accepted,key=lambda r:r['final_replay'].get('states_checked',0));ch=v.scene(selected['index']);sg=v.items[selected['index']][1];pb=PointBound(ch)
park=load(H/idle['doors_model_xml']);qclosed=np.r_[idle['q'],np.zeros(len(idle['doors']))];qopen=np.r_[idle['q'],np.full(len(idle['doors']),np.pi/2)]
passing=json.loads((O/'passing.json').read_text());pch=load(H/passing['model_xml']);manifest=[]
def emit(c,q,name,status,label,focus,scale,size):
 export(c,q,'v3/'+name,status,focus=focus,label=label);path=R/'v3'/f'{name}.scene.json';data=json.loads(path.read_text());data.update(resolution=size,samples=4,camera_scale=scale);data['geoms']=[g for g in data['geoms'] if not g['name'].startswith('idle_full_sweep_cover_')];path.write_text(json.dumps(data));manifest.append(dict(name=name,scene='v3/'+name+'.scene.json',image='v3/'+name+'.png',q=np.array(q).tolist(),status=status))
emit(ch,np.array(selected['edges'][0]['path'][0]),'overview',v.ID+' / ACCEPTED LOCAL PATH / COMPLETE MEAL FAIL','overview',[-.3,0,1.2],5.5,[1440,960])
emit(park,qopen,'parked_doors_open','ALL DOORS OPEN / PARK SNAPSHOT PASS / COMPLETE FOLD UNVERIFIED','parked',[-.3,0,1.2],5.5,[1440,960])
emit(park,qclosed,'under_cabinet_band','FULL OEM ARMS / POPULATED PARK SNAPSHOT PASS / MEAL FAIL','band',[-.75,.4,1.20],1.85,[1440,960])
emit(pch,np.array(passing['q_crossing']),'passing','REJECTED CARRIAGE-ORDER SWAP / NOT EXECUTED','passing',[-.3,0,1.2],5.5,[1440,960])
segments=[];total=0.
for ei,e in enumerate(selected['edges']):
 for si,(a,b) in enumerate(zip(np.array(e['path']),np.array(e['path'])[1:])):
  length=pb.segment_bound(a,b);segments.append((total,total+length,ei,si,a,b));total+=length
frames=[]
for i,position in enumerate(np.linspace(0,total,24)):
 start,end,ei,si,a,b=next((s for s in segments if s[1]>=position),segments[-1]);u=(position-start)/max(1e-15,end-start);q=a+(b-a)*u;e=selected['edges'][ei];ha,hb=sg['poses'][ei:ei+2];hands=ha if si==0 and u<1e-10 else hb if si==len(e['path'])-2 and u>1-1e-10 else {side:dict(h,contacts=[c for c in h.get('contacts',[]) if c in hb.get(side,{}).get('contacts',[])]) for side,h in ha.items()}
 ch.working_stroke=sg['action']=='process';ch.contact_windows=e.get('contact_windows',[]);assert Planner(ch,hands).state(q,hands)
 emit(ch,q,f'frame_{i:02}',f'CHECKED PATH {i+1}/24 / ISOLATED, NOT MEAL',selected['stroke'],[-.45,.25,1.1],2.4,[500,320]);frames.append(dict(frame=i,edge=ei,segment=si,alpha=float(u),q=q.tolist()))
v.rt.write('frame_manifest.json',dict(layout=v.ID,stroke=selected['stroke'],model_xml=f'models/{v.ID}_internal_{selected["index"]}.xml',path_file=f'results/motion_v2/{v.ID}/internal_{selected["index"]}.json',frames=frames,executed_meal=False,scope='24 samples from one accepted complete isolated path, populated template scene; not a meal or physical robot video.'))
(R/'manifest_v3.json').write_text(json.dumps(dict(CPU_only=True,maximum_px=1500,views=manifest,frame_count=24,source='Actual unscaled MJCF collision geometry. Failed park/passing snapshots labelled; executed strip from admitted path only.',visual_omissions=['Opposite south wall/cabinets and symbolic sweep/access masks hidden only for display']),indent=2))
print('EXPORTED',len(manifest),'paths',len(accepted),'states',checked,'local_s',sum(r['duration_s'] for r in schedules),flush=True)
