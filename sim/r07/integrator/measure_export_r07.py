"""Measure only accepted diagnostic path; export exact geometry with scope labels."""
import json,math,xml.etree.ElementTree as E
import numpy as np,mujoco
import r07_runtime as rt
from point_bound import PointBound
from render_setup import export
H=rt.H;O=rt.O;R=H/'renders';R.mkdir(exist_ok=True)
def read(n):return json.loads((O/n).read_text())
def load(path):
 ch=object.__new__(rt.Checker);ch.desc=rt.s.ck.hand([0,0,1],jaw_axis=[0,1,0]);ch.bind_model(mujoco.MjModel.from_xml_path(str(path)));ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False
 return ch
aux=read('aux_paths.json');ch=load(H/aux['model_xml']);pb=PointBound(ch)
all_reserve={};samples=[]
for sample in aux['samples']:
 q=np.array(sample['q']);hits,mins,audit=rt.f.contacts(ch,q)
 assert not hits
 for cat,ix in ch.bounds.catids.items():all_reserve.setdefault(cat,[]).extend(((ch.bounds.last_lower[ix]-ch.bounds.need[ix])*1000).tolist())
 samples.append(dict(category_minima=mins,eligible_pairs=audit['distance_proof']['eligible_pairs']))
stats={cat:dict(pair_state_count=len(v),min_mm=min(v),p05_mm=float(np.percentile(v,5)),median_mm=float(np.median(v)),p95_mm=float(np.percentile(v,95)),max_mm=max(v)) for cat,v in all_reserve.items()}
idle=read('idle.json')
rt.write('clearance.json',dict(schema='r07.clearance-reserves',scope=aux['scope'],path_pass=aux['pass_'],sample_count=len(samples),max_point_step_mm=aux['planner']['max_point_step_mm'],distribution=stats,distribution_method='Every eligible pair at every accepted <=4mm discrete state: enclosing AABB separation lower bounds, exact-support GJK refinement for near pairs. These are conservative lower reserves, not exact physical distances or a continuous certificate.',per_state_minima=samples,idle=dict(pass_=False,door_sweep_pass=idle['door_sweep_pass'],minimum_vertical_door_gap_mm=min(r['door_sweep_lower_gap_mm'] for r in idle['robot_parts']),front_chain_gap_mm=10,front_chain_reserve_mm=0,populated_snapshot_pass=idle['snapshot_pass'],failed_pose_gaps_are_not_usable_reserves=True),meal_clearance_distribution=None))
path=np.array(aux['path']);segment_times=[]
for a,b in zip(path,path[1:]):
 dq=abs(b-a);t=0
 for n,k in ch.qa.items():
  if dq[k]<1e-12:continue
  v=.2 if 'carriage' in n else .35;acc=.3 if 'carriage' in n else .35;dist=dq[k]
  ti=2*math.sqrt(dist/acc) if dist<=v*v/acc else dist/v+v/acc;t=max(t,ti)
 dist=pb.segment_bound(a,b);v=.05;acc=.3
 t=max(t,2*math.sqrt(dist/acc) if dist<=v*v/acc else dist/v+v/acc)
 segment_times.append(t)
schedule=read('schedule.json');schedule['auxiliary_executed_path_time_s']=sum(segment_times);schedule['auxiliary_segment_times_s']=segment_times;schedule['auxiliary_scope']=aux['scope'];schedule['timing_method']='Home-speed scalar rest-to-rest trapezoid/triangle per path segment, satisfying rail/joint/global-point velocity and acceleration bounds. Simulated kinematic execution only.';rt.write('schedule.json',schedule)
# Candidate parked pose has the populated collision documented in idle.json.
q=np.array(idle['q']);closed=load(H/'models/r07_snapshot.xml')
# Use the actual idle scene (full stored tools, bowls and raw produce), with
# additional real doors: zero angle for overview; 90deg for the parked view.
doors=load(H/'models/idle_doors_open.xml');q_closed=np.r_[q,np.zeros(doors.m.nq-len(q))];q_open=np.r_[q,np.full(doors.m.nq-len(q),np.pi/2)]
views=[('overview',doors,q_closed,'CANDIDATE / STROKES 0 OF 105 / MEAL FAIL','overview',[-.3,0,1.2],5.5),('parked_doors_open',doors,q_open,'ALL FIVE DOORS OPEN / POPULATED PARK FAIL / FOLD FAIL','parked',[-.3,0,1.2],5.5),('under_cabinet_band',doors,q_closed,'EXACT OEM GEOMETRY / STORED-BOWL INTERFERENCE / FAIL','band',[-.75,.40,1.22],1.75),('passing',ch,np.array(read('passing.json')['q_crossing']),'REJECTED CROSSING FRAME / 65 SECOND SEARCH FAILED','passing',[-.3,0,1.2],5.5)]
manifest=[]
def emit(ch,q,name,status,label,focus,scale,resolution):
 export(ch,q,name,status,focus=focus,label=label)
 file=R/(name+'.scene.json');data=json.loads(file.read_text());data.update(resolution=resolution,samples=4,camera_scale=scale);file.write_text(json.dumps(data),encoding='utf-8')
 manifest.append(dict(name=name,scene=name+'.scene.json',image=name+'.png',q=q.tolist(),status=status,source_model='idle_doors_open.xml' if ch is doors else aux['model_xml']))
for name,c,v,status,label,focus,scale in views:emit(c,v,name,status,label,focus,scale,[1440,960])
times=[]
for i in range(24):
 phase=i/23*2;seg=min(1,int(phase));u=phase-seg
 # Smooth interpolation samples the same accepted segment; each frame is
 # rechecked, and remains part of the <=4mm validated 25mm shuttle.
 u=min(1,u);v=path[seg]+(path[seg+1]-path[seg])*u
 assert not rt.f.contacts(ch,v)[0]
 emit(ch,v,f'frame_{i:02d}',f'CHECKED LOCAL SHUTTLE {i+1}/24 / EMPTY FIXED SCENE','local empty shuttle',[-.65,.40,1.20],2.0,[500,320])
 times.append(sum(segment_times[:seg])+u*segment_times[seg])
rt.write('frame_manifest.json',dict(frames=manifest[4:],sample_times_s=times,path_file='results/aux_paths.json',executed_meal=False,scope=aux['scope'],interpolation='Path parameter sampled uniformly. Times are parameter labels, not a captured physical video.'))
(R/'manifest.json').write_text(json.dumps(dict(CPU_only=True,maximum_px=1440,views=manifest,frame_count=24,omissions=['Opposite south wall/cabinets and symbolic sweep/access masks removed from display only; all remain in collision checks'],source='Unscaled actual MJCF collision geometry. No AI imagery. Failed snapshots and passing frame labelled. Only the local diagnostic strip is from accepted paths.'),indent=2),encoding='utf-8')
print('distribution',stats,'aux seconds',sum(segment_times),'scenes',len(manifest))
