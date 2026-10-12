"""Off-centre root grasp: full food geometry/world key poses are preserved.

The8mm inherited grasp leaves fingers near the land during rotated return.
Move the tool grasp to30mm while compensating TCP positions, not food size.
All force vectors/masses/capacities are retained; actual work/CoM offset moves.
"""
import copy,json,sys,time
import numpy as np
import final_check as f,motion_r05 as mo
H=f.s.HERE;O=H/'results';ws=json.loads((O/'static_all.json').read_text())['witnesses'];lo,hi=map(int,sys.argv[1:3]);records=[];t0=time.monotonic()
for index in range(lo,hi):
 ph,base,key=mo.items[index]
 if base['action']!='helper_index':continue
 sg=copy.deepcopy(base);w=ws[key];delta=np.array([.022,0,0]);proof=[]
 for old,new in zip(base['poses'],sg['poses']):
  h=new['L'];rt=f.s.Checker(ph,base).target_rotation(old['L'],w['k']);oldcentre=np.array(old['L']['pos'])+rt@np.array(old['L']['food_center_local_m']);h['pos']=(np.array(h['pos'])-rt@delta).tolist()
  for name in ('food_center_local_m','mass_offset_m','work_offset_m'):h[name]=(f.s.ck.offset_vector(h[name])+delta).tolist()
  newcentre=np.array(h['pos'])+rt@np.array(h['food_center_local_m']);proof.append(dict(old_food_world_center_m=oldcentre.tolist(),new_food_world_center_m=newcentre.tolist(),difference_m=float(np.linalg.norm(oldcentre-newcentre))))
 ch=mo.scene(ph,sg,index);ch.witness_k=w['k'];ch.refine_support_endpoints=True;ch.goal_clearance_search=True;ch.refine_start_allowed=False;q=np.array(w['poses'][0]['q']);source=None;attempts=[]
 # Choose an equivalent source representation away from +/-2pi limits.
 # This is an initial IK seed choice only; no executed joint segment is
 # wrapped or jumped, and every chosen source is reference-reverified.
 for name in f.s.ck.ARMS['L']:
  j=ch.qa[name];lower,upper=ch.m.jnt_range[ch.jid[name]];choices=[q[j]+k*2*np.pi for k in range(-2,3) if lower<=q[j]+k*2*np.pi<=upper]
  q[j]=min(choices,key=abs)
 for seed in range(12):
  a=q.copy()
  if seed:
   rng=np.random.default_rng(60500+index*5+seed)
   for n in f.s.ck.ARMS['L']:a[ch.qa[n]]+=rng.normal(0,.06)
   shift=rng.normal(0,.06) if seed<5 else [.12,-.12,.25,-.25,.4,-.4,.55][seed-5]
   a[ch.qa['L_carriage_x']]=np.clip(a[ch.qa['L_carriage_x']]+shift,-1.7,.2)
  h=sg['poses'][0];a,ok=mo.ik(ch,a,{'L':(np.array(h['L']['pos']),ch.target_rotation(h['L'],w['k']))});oldseg=ch.seg;ch.seg=dict(oldseg,poses=[h]);v=f.replay(ch,dict(k=w['k'],poses=[dict(q=a.tolist())]));ch.seg=oldseg
  look=False
  if ok and v['ok']:
   lifted,lift_ok=mo.ik(ch,a,{'L':(np.array(h['L']['pos'])+[0,0,.045],ch.target_rotation(h['L'],w['k']))});ch.contact_windows=[];test=mo.Planner(ch,h,seed=99500+seed,seconds=65);look=bool(lift_ok and test.state(lifted,{side:dict(hand,contacts=[]) for side,hand in h.items()}))
  attempts.append(dict(seed=seed,ik_exact=ok,reference=v,provisional_45mm_lift_clearance=look,lookahead_scope='Source-selection heuristic only; full straight lift,rotation and return are separately planned and replayed'))
  if ok and v['ok'] and look:q=a;source=v;break
 edges=[]
 if source:
  for j in range(len(sg['poses'])-1):
   a=np.array(edges[-1]['path'][-1]) if edges and edges[-1]['ok'] else q.copy();b=mo.shortq(ch,a,w['poses'][j+1]['q']);out=mo.plan_section(ch,a,b,sg['poses'][j],sg['poses'][j+1],90500+index*7+j);edges.append(out)
 r=dict(kind='internal',index=index,stroke=key,ok=bool(source) and all(e['ok'] for e in edges),edges=edges,segment_override=sg,variant='Full root30mm off-centre grasp; TCP compensated to preserve every full food world key pose',world_food_pose_proof=proof,source_static_witness=source,source_ik_attempts=attempts,simultaneous_arms=['R','L'],meal_state_verified=False,reason=None if source else 'No sufficiently converged, reference-admitted source with a clear45mm lookahead; recorded endpoint errors distinguish solver convergence from physical clearance',force_policy='Identical force/moment vectors, held masses,mu/SF,150N/15Nm; work and mass sites follow the actual translated full food geometry');records.append(r)
 payload=json.dumps(dict(records=records,elapsed_s=time.monotonic()-t0),indent=2,default=lambda x:x.item() if isinstance(x,np.generic) else x.tolist() if isinstance(x,np.ndarray) else str(x))
 target=O/f'motion_internal_grasp_{lo}_{hi}.json';pending=target.with_suffix('.tmp');pending.write_text(payload);pending.replace(target)
 print('GRASP_VARIANT',index,r['ok'],'edges',[x['ok'] for x in edges],'time',round(time.monotonic()-t0,1),flush=True)
