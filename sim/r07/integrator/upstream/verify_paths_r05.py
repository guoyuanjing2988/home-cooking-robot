"""Fresh final replay of each retained path, including unchanged load/grip gates."""
import json,sys,time,itertools,math,hashlib
import numpy as np,mujoco
from scipy.spatial.transform import Rotation,Slerp
import final_check as f,motion_r05 as mo
from planner_r05 import Planner
from point_bound import PointBound
s=f.s;H=s.HERE;O=H/'results';m=json.loads((O/'motion.json').read_text());ws=json.loads((O/'static_all.json').read_text())['witnesses'];lo,hi=map(int,sys.argv[1:3]);records=[];beg=time.monotonic()
for r in m['internal']:
 if not r.get('solver_geometry_ok',r['ok']) or not lo<=r['index']<hi:continue
 digest=hashlib.sha256(json.dumps([x['path'] for x in r['edges']],sort_keys=True).encode()).hexdigest();previous=r.get('final_path_replay',{}) or {}
 if previous.get('pass_') and previous.get('path_sha256')==digest:continue
 ph,sg,key=mo.items[r['index']];sg=r.get('segment_override',sg);ch=mo.scene(ph,sg,r['index']);ch.witness_k=ws[key]['k'];ch.working_stroke=sg['action']=='process';pb=PointBound(ch);states=0;bad=None;maxratio=0;mingrip=1e9;minreserve=1e9
 for edge_index,e in enumerate(r['edges']):
  ch.contact_windows=e.get('contact_windows',[]);pl=Planner(ch,sg['poses'][edge_index],seconds=65);path=np.array(e['path']);ha=sg['poses'][edge_index];hb=sg['poses'][edge_index+1];common={side:dict(h,contacts=[c for c in h.get('contacts',[]) if c in hb.get(side,{}).get('contacts',[])]) for side,h in ha.items()}
  if edge_index and np.max(abs(np.array(r['edges'][edge_index-1]['path'][-1])-path[0]))>1e-9:
   bad=dict(kind='Internal edges are not connected in joint space',edge=edge_index);break
  oldseg=ch.seg;ch.seg=dict(oldseg,poses=[ha,hb]);endpoints=f.replay(ch,dict(k=ws[key]['k'],poses=[dict(q=path[0].tolist()),dict(q=path[-1].tolist())]));ch.seg=oldseg
  if not endpoints['ok']:bad=dict(kind='Unchanged reference endpoint pose/load/grip replay',edge=edge_index,witness=endpoints);break
  if ch.working_stroke:
   rotations={side:Slerp([0,1],Rotation.from_matrix([ch.target_rotation(ha[side],ws[key]['k']),ch.target_rotation(hb[side],ws[key]['k'])])) for side in ha}
  for segment_index,(a,b) in enumerate(zip(path,path[1:])):
   count=max(1,int(math.ceil(pb.segment_bound(a,b)/.004)))
   for k in range(count+1):
    t=k/count;q=a+(b-a)*t;h=ha if segment_index==0 and k==0 else hb if segment_index==len(path)-2 and k==count else common;states+=1
    if not pl.state(q,h):bad=dict(kind='collision',edge=edge_index,segment=segment_index,k=k,blockers=pl.last);break
    # Every provided check-wrench alternative is preserved. No demand value is
    # selected from pass/fail, and the rated envelope remains the only gate.
    for fv in itertools.product(*[x['check_forces_N'] for x in h.values()]):
     for mv in itertools.product(*[x['check_moments_Nm'] for x in h.values()]):
      forces=dict(zip(h,fv));moments=dict(zip(h,mv));torque=ch.torque_multi(q,h,forces,moments);maxratio=max(maxratio,torque['ratio']);grips=[ch.grip_side(q,x,forces[side],moments[side],side)['margin'] for side,x in h.items()];mingrip=min(mingrip,min(grips))
      if torque['ratio']>1 or min(grips)<1:bad=dict(kind='rated-envelope or grip',edge=edge_index,segment=segment_index,k=k,torque=torque,grip_margin=min(grips));break
     if bad:break
    if not bad and ch.working_stroke:
     alpha=(segment_index+t)/(len(path)-1)
     for side in ha:
      sid=ch.m.site(side+'_prep').id;target=(1-alpha)*np.array(ha[side]['pos'])+alpha*np.array(hb[side]['pos']);rt=rotations[side](alpha).as_matrix();pe=np.linalg.norm(ch.d.site_xpos[sid]-target)*1000;oe=np.degrees(np.linalg.norm(Rotation.from_matrix(rt.T@ch.d.site_xmat[sid].reshape(3,3)).as_rotvec()))
      if pe>5 or oe>3:bad=dict(kind='working Cartesian pose',position_mm=float(pe),orientation_deg=float(oe),side=side);break
    if bad:break
   if bad:break
  if bad:break
 row=dict(index=r['index'],stroke=r['stroke'],pass_=bad is None,states_checked=states,max_check_envelope_ratio=maxratio,min_grip_margin=mingrip,blocker=bad,max_point_step_mm=4.,path_sha256=hashlib.sha256(json.dumps([x['path'] for x in r['edges']],sort_keys=True).encode()).hexdigest(),model_sha256=hashlib.sha256(ch.xml.encode()).hexdigest(),positive_margin_discrepancies=getattr(pl,'proximity_discrepancies',[]),full_meal_state_verified=False);records.append(row);print(key,'final path',row['pass_'],'states',states,'ratio',round(maxratio,4),flush=True)
 (O/f'path_replay_{lo}_{hi}.json').write_text(json.dumps(dict(rows=records,elapsed_s=time.monotonic()-beg),indent=2))
print('PATH_REPLAY_COMPLETE',len(records),sum(r['pass_'] for r in records),round(time.monotonic()-beg,1),flush=True)
