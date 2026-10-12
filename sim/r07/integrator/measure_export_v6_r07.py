"""Actual admitted simulation states only; no illustrative meal animation."""
import os,sys,json,hashlib,math,runpy,gc
from pathlib import Path
os.environ['R07_LAYOUT']=sys.argv[1]
import runtime_v6_r07 as v
import numpy as np,mujoco
from motion_v6_r07 import Planner,replay
from point_bound import PointBound
from render_setup import export
H=v.H;O=v.O;R=H/'renders';ID=v.ID;V='v6_'+ID;(R/V).mkdir(exist_ok=True)
def read(n):return json.loads((O/n).read_text())
def write(n,d):(O/n).write_text(json.dumps(d,indent=2,allow_nan=False))
def duration(ch,a,b,pb):
 t=0.
 for name,ix in ch.qa.items():
  distance=abs(b[ix]-a[ix]);speed=.1 if 'carriage' in name else .35;acc=.3 if 'carriage' in name else .35
  t=max(t,2*math.sqrt(distance/acc) if distance<=speed*speed/acc else distance/speed+speed/acc)
 distance=pb.segment_bound(a,b);return max(t,2*math.sqrt(distance/.3) if distance<=.05**2/.3 else distance/.05+.05/.3)
accepted=[read(f'motion_v6/{ID}/'+p.name) for p in (O/'motion_v6'/ID).glob('internal_*.json') if json.loads(p.read_text()).get('ok')];timings=[]
for row in accepted:
 ch=v.scene(row['index']);pb=PointBound(ch);times=[duration(ch,np.array(a),np.array(b),pb) for e in row['edges'] for a,b in zip(e['path'],e['path'][1:])];timings.append(dict(index=row['index'],duration_s=sum(times),segment_times_s=times,source=f'results/motion_v6/{ID}/internal_{row["index"]}.json',states_checked=row['final_replay']['states_checked']));del ch,pb;gc.collect()
schedule=read('schedule.json');schedule.update(accepted_internal_paths=timings,isolated_path_sum_s=sum(r['duration_s'] for r in timings),timing_method='Rest-to-rest sparse waypoint intervals, maximum of joint/rail triangular or trapezoidal travel and model-derived all-point displacement speed cap. Isolated diagnostic sum, not a meal makespan.');write('schedule.json',schedule)
selected=next((r for r in accepted if r['index']==49),max((r for r in accepted if r['final_replay']['states_checked']>1),key=lambda r:r['final_replay']['states_checked']));index=selected['index'];ch=v.scene(index);ph,sg,key=v.items[index];full=replay(ch,sg,selected['endpoint_witness'],selected['edges']);assert full['pass_'];states=full['states'];scope='Complete isolated robot template checked in simulation; NOT A CONNECTED MEAL; appliance processes unqualified.'
write('executed_local_v6.json',dict(ok=True,layout=ID,index=index,model_xml=f'models/{ID}_internal_{index}.xml',model_sha256=hashlib.sha256(ch.xml.encode()).hexdigest(),path_file=f'results/motion_v6/{ID}/internal_{index}.json',source_sha256=hashlib.sha256((O/f'motion_v6/{ID}/internal_{index}.json').read_bytes()).hexdigest(),jaw_axis_branch=selected['jaw_axis_branch'],states=states,states_checked=len(states),max_point_step_mm=full['max_point_step_mm'],scope=scope,meal_pass=False))
clearance=read('clearance.json');clearance['path_state_minimum_reserve_distributions']=[dict(index=r['index'],distribution=r['final_replay'].get('clearance_distribution',{})) for r in accepted];clearance['selected_path_fresh_replay']=full['clearance_distribution'];write('clearance.json',clearance)
def load(path):
 c=object.__new__(v.Checker);c.desc=v.s.ck.hand([0,0,1],held='empty');c.bind_model(mujoco.MjModel.from_xml_path(str(H/path)));c.hands={};c.allowed=[];c.contact_windows=[];c.working_stroke=False;return c
manifest=[]
def emit(c,q,name,status,label,focus,scale,size):
 export(c,q,V+'/'+name,status,focus=focus,label=label);p=R/V/f'{name}.scene.json';data=json.loads(p.read_text());data.update(config=read('config.json'),resolution=size,samples=4,camera_scale=scale);data['geoms']=[g for g in data['geoms'] if not g['name'].startswith('idle_full_sweep_cover_')];p.write_text(json.dumps(data));manifest.append(dict(name=name,scene=V+'/'+name+'.scene.json',image=V+'/'+name+'.png',q=np.array(q).tolist(),status=status))
idle=read('idle.json');park=load(idle['doors_model_xml']);qclosed=np.r_[idle['q'],np.zeros(len(idle['doors']))];qopen=np.r_[idle['q'],np.full(len(idle['doors']),np.pi/2)]
emit(ch,np.array(states[len(states)//2]['q']),'overview',ID+' / ISOLATED TEMPLATE CHECKED / FULL MEAL FAIL','Under-cabinet candidate',[-.3,0,1.2],5.5,[1440,960])
emit(park,qopen,'parked_doors_open','ALL DOORS OPEN / SNAPSHOT '+('PASS' if idle['snapshot_pass'] else 'FAIL')+' / CONNECTED IDLE FAIL','Populated park',[-.3,0,1.2],5.5,[1440,960])
emit(park,qclosed,'under_cabinet_band','ONE UR5e / FULL RAIL AND CHAIN / DOOR GATE10MM','Under-cabinet band',[-.75,.4,1.20],1.85,[1440,960])
emit(park,qclosed,'passing','PASSING NOT APPLICABLE / ONE ARM AND ONE CARRIAGE','Single lane, no passing event',[-.3,0,1.2],5.5,[1440,960])
frames=[]
for i,si in enumerate(np.linspace(0,len(states)-1,24).round().astype(int)):
 state=states[si];q=np.array(state['q']);ei=state['edge'];edge=selected['edges'][ei];ha,hb=sg['poses'][ei:ei+2];ch.working_stroke=sg['action']=='process';ch.contact_windows=edge.get('contact_windows',[]);hands=ha if state['segment']==0 and state['alpha']==0 else hb if state['segment']==len(edge['path'])-2 and state['alpha']==1 else {s:dict(h,contacts=[c for c in h.get('contacts',[]) if c in hb[s].get('contacts',[])]) for s,h in ha.items()};pl=Planner(ch,hands,seconds=65);assert pl.state(q,hands)
 emit(ch,q,f'frame_{i:02}',f'CHECKED ISOLATED PATH {i+1}/24 / FULL MEAL FAIL',key,[-.45,.25,1.1],2.4,[500,320]);frames.append(dict(frame=i,state_index=int(si),q=q.tolist()))
write('frame_manifest.json',dict(layout=ID,stroke=key,model_xml=f'models/{ID}_internal_{index}.xml',model_sha256=hashlib.sha256(ch.xml.encode()).hexdigest(),path_file='results/executed_local_v6.json',frames=frames,executed_meal=False,prefix_only=False,scope=scope))
(R/'manifest_v6.json').write_text(json.dumps(dict(CPU_only=True,maximum_px=1500,views=manifest,frame_count=24,source='Full unscaled saved MJCF collision geometry and freshly checked simulated q. No imagined connected meal.',visual_omissions=['Opposite wall/cabinets, outlet access masks and door-sweep covers hidden for display only; all remain checked.']),indent=2))
# Reuse unchanged measurement algorithm with the actual one-arm set.
source=(H/'counter_and_arm_r07.py').read_text().replace('import runtime_v2_r07 as v','import runtime_v6_r07 as v').replace("for side in ('R','L'):","for side in v.s.model.SIDES:")
exec(compile(source,str(H/'counter_and_arm_v4_generated.py'),'exec'))
print('EXPORTED',ID,index,len(states),'states',len(accepted),'internal paths',flush=True)
