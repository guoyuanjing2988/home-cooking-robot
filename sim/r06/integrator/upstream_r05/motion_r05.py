"""R05 bounded planning chunks; every attempt and state-model limit is retained."""
import os
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[n]='1'
import json,sys,time,copy,xml.etree.ElementTree as E
import numpy as np,mujoco
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
import final_check as f
from planner_r05 import Planner
import fast_bounds
fast_bounds.install()
s=f.s;H=s.HERE;O=H/'results'
items=[(ph,sg,ph['id']+'__'+sg['label'].replace(' ','_')) for ph in s.P['phases'] for sg in ph['segments']]
def shortq(ch,a,b):
 b=np.array(b).copy()
 for n in s.ck.JOINTS:
  j=ch.qa[n];l,u=ch.m.jnt_range[ch.jid[n]];v=[b[j]+k*2*np.pi for k in range(-2,3) if l<=b[j]+k*2*np.pi<=u];b[j]=min(v,key=lambda x:abs(x-a[j]))
 return b
def signature(hands):
 return {side:tuple(json.dumps(h.get(n),sort_keys=True) for n in ['held','held_kg','product','food_state','object_rotation_deg','food_tool_roll_deg','food_center_local_m','work_offset_m','mass_offset_m','jaw_opening_m']) for side,h in hands.items()}
def windows(ch,q,hands):
 ch.set_contacts(hands);ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d);out=[]
 for side,h in hands.items():
  sid=ch.m.site(side+'_prep').id
  for c in h.get('contacts',[]):
   out.append(dict(side=side,**c,tcp_origin_m=ch.d.site_xpos[sid].tolist(),tcp_rotation=ch.d.site_xmat[sid].reshape(3,3).tolist(),normal=[0,0,1],max_window_mm=50,insertion_axis_reason='Vertical disengagement from open top land/dock or open axial end cups; no neighbouring post or guard permission'))
 return out
def ik(ch,q,targets):
 ix=[ch.qa[n] for side in targets for n in s.ck.ARMS[side]]
 limits=np.array([ch.m.jnt_range[ch.jid[n]] for side in targets for n in s.ck.ARMS[side]]).T
 out=q.copy()
 def residual(x):
  out[ix]=x;ch.d.qpos[:]=out;mujoco.mj_kinematics(ch.m,ch.d);vals=[]
  for side,(p,r) in targets.items():
   sid=ch.m.site(side+'_prep').id;vals.extend((ch.d.site_xpos[sid]-p)*10);vals.extend(Rotation.from_matrix(r.T@ch.d.site_xmat[sid].reshape(3,3)).as_rotvec())
  return np.array(vals)
 res=least_squares(residual,np.clip(q[ix],limits[0]+1e-9,limits[1]-1e-9),bounds=limits,xtol=1e-10,ftol=1e-10,gtol=1e-10,max_nfev=100)
 return out.copy(),np.linalg.norm(res.fun)<1e-5
def lift(ch,q,hands,ws,pl,deadline):
 if not ws:return [q],None
 targets={}
 for w in ws:targets[w['side']]=(np.array(w['tcp_origin_m']),np.array(w['tcp_rotation']))
 path=[q];failure=None
 # The support window requires an actual straight TCP departure. Sparse
 # 10mm Cartesian knots produce visibly curved TCP joint interpolation even
 # when their endpoints are exact. 1mm continuation knots keep that curvature
 # below the existing 20um lateral/0.2mrad rotation window checks; those checks
 # remain unchanged and can still reject a singular branch.
 for mm in range(1,51):
  if time.monotonic()>=deadline:return None,dict(reason='lift continuation budget exhausted')
  tg={side:(p+np.array([0,0,mm/1000]),r) for side,(p,r) in targets.items()};candidate,ok=ik(ch,path[-1],tg)
  if not ok:return None,dict(reason='straight lift IK continuation failed',lift_mm=mm)
  if not pl.edge(path[-1],candidate,hands,hands,deadline):return None,dict(reason='straight support lift blocked',lift_mm=mm,blocker=pl.last)
  path.append(candidate)
  # Permission automatically ends for each pair once it reaches 5mm. Require
  # the full empty-contact transit check to pass before leaving the window.
  old=ch.contact_windows;ch.contact_windows=[];none={side:dict(h,contacts=[]) for side,h in hands.items()};free=pl.state(candidate,none);ch.contact_windows=old
  if free:return path,None
 return None,dict(reason='support did not reach full gap within 50mm',blocker=pl.last)
def plan_section(ch,a,b,ha,hb,seed,process=False):
 start=time.monotonic();deadline=start+65;pl=Planner(ch,ha,seed,65);new_endpoint=None
 new_initial=None
 if not process and getattr(ch,'refine_support_endpoints',False) and getattr(ch,'refine_start_allowed',True):
  targets={side:(np.array(h['pos']),ch.target_rotation(h,getattr(ch,'witness_k',0))) for side,h in ha.items() if h.get('contacts')}
  if not targets:targets={side:(np.array(h['pos']),ch.target_rotation(h,getattr(ch,'witness_k',0))) for side,h in ha.items()}
  candidate,success=ik(ch,a,targets)
  if success:
   oldseg=ch.seg;ch.seg=dict(oldseg,poses=[ha]);checked=f.replay(ch,dict(k=getattr(ch,'witness_k',0),poses=[dict(q=candidate.tolist())]));ch.seg=oldseg
   if checked['ok']:a=candidate;new_initial=checked
 if not process:
  ch.d.qpos[:]=b;mujoco.mj_kinematics(ch.m,ch.d);targets={side:(ch.d.site_xpos[ch.m.site(side+'_prep').id].copy(),ch.d.site_xmat[ch.m.site(side+'_prep').id].reshape(3,3).copy()) for side in hb}
  if getattr(ch,'refine_support_endpoints',False):targets={side:(np.array(h['pos']),ch.target_rotation(h,getattr(ch,'witness_k',0))) for side,h in hb.items() if not(ch.seg.get('action')=='helper_index' and side=='R')}
  candidate,success=ik(ch,a,targets)
  alternatives=[(candidate,success)]
  if getattr(ch,'goal_clearance_search',False):
   for shift in (-.12,.12,-.25,.25,-.4,.4):
    seedq=a.copy();ix=ch.qa['L_carriage_x'];seedq[ix]=np.clip(seedq[ix]+shift,*ch.m.jnt_range[ch.jid['L_carriage_x']]);alternatives.append(ik(ch,seedq,targets))
  valid=[]
  for candidate,success in alternatives:
   if not success or not(getattr(ch,'refine_support_endpoints',False) or np.linalg.norm(candidate-a)<np.linalg.norm(b-a)):continue
   oldseg=ch.seg;ch.seg=dict(oldseg,poses=[hb]);checked=f.replay(ch,dict(k=getattr(ch,'witness_k',0),poses=[dict(q=candidate.tolist())]));ch.seg=oldseg
   if checked['ok']:
    margins=checked['poses'][0]['min_clearance'];reserve=min(margins[k]['reserve_mm'] for k in ('robot_environment','held_gripper_environment','arm_arm_or_frame'))
    valid.append((reserve-.5*np.linalg.norm(candidate-a),candidate,checked))
  if not valid and getattr(ch,'goal_clearance_search',False):
   # Fixed-carriage continuation can miss a valid branch near wrist limits.
   # Reuse the copied collision-aware joint+carriage solver, then admit only
   # a fully independent reference endpoint. No solver-side contact shortcut
   # is accepted as endpoint evidence.
   ch.search_carriage=True
   for restart in range(3):
    seedq=a.copy();rng=np.random.default_rng(seed+170000+restart)
    if restart:
     for side in hb:
      for name in s.ck.ARMS[side]:seedq[ch.qa[name]]=np.clip(seedq[ch.qa[name]]+rng.normal(0,.25),*ch.m.jnt_range[ch.jid[name]])
      name=side+'_carriage_x';lo,hi=ch.m.jnt_range[ch.jid[name]];hi=min(hi,.045) if side=='R' else hi;seedq[ch.qa[name]]=np.clip(seedq[ch.qa[name]]+rng.normal(0,.2),lo,hi)
    ch.set_contacts(hb);candidate,errors=ch.solve_least(seedq,hb,getattr(ch,'witness_k',0));oldseg=ch.seg;ch.seg=dict(oldseg,poses=[hb]);checked=f.replay(ch,dict(k=getattr(ch,'witness_k',0),poses=[dict(q=candidate.tolist())]));ch.seg=oldseg
    if checked['ok']:
     margins=checked['poses'][0]['min_clearance'];reserve=min(margins[k]['reserve_mm'] for k in ('robot_environment','held_gripper_environment','arm_arm_or_frame'));valid.append((reserve-.5*np.linalg.norm(candidate-a),candidate,checked));break
  if valid:
   _,b,new_endpoint=max(valid,key=lambda x:x[0])
 wa=windows(ch,a,ha);wb=windows(ch,b,hb);ch.contact_windows=wa+wb
 # Actual food/tool work contacts shared by both endpoints remain only those
 # explicit named pairs. Their unchanged face/normal test runs at every state.
 shared={side:dict(h,contacts=[c for c in h.get('contacts',[]) if c in hb.get(side,{}).get('contacts',[])]) for side,h in ha.items()}
 if process:
  ch.working_stroke=True
  # Do not accept a free-space detour as peeling/rubbing. Solve straight TCP
  # continuation, retaining simultaneous targets when both arms participate.
  ch.d.qpos[:]=a;mujoco.mj_forward(ch.m,ch.d);ta={side:(ch.d.site_xpos[ch.m.site(side+'_prep').id].copy(),ch.d.site_xmat[ch.m.site(side+'_prep').id].reshape(3,3).copy()) for side in ha}
  ch.d.qpos[:]=b;mujoco.mj_forward(ch.m,ch.d);tb={side:(ch.d.site_xpos[ch.m.site(side+'_prep').id].copy(),ch.d.site_xmat[ch.m.site(side+'_prep').id].reshape(3,3).copy()) for side in hb}
  path=[a];failure=None
  for alpha in np.linspace(0,1,25)[1:]:
   tg={side:((1-alpha)*ta[side][0]+alpha*tb[side][0],ta[side][1]@Rotation.from_rotvec(alpha*Rotation.from_matrix(ta[side][1].T@tb[side][1]).as_rotvec()).as_matrix()) for side in ta}
   q,ok=ik(ch,path[-1],tg)
   if not ok or not pl.edge(path[-1],q,shared,shared,deadline):failure=pl.last or dict(reason='working Cartesian continuation IK failure');break
   path.append(q)
  if not failure:
   # A coherent IK branch may reach the required final pose without reaching
   # the arbitrarily selected R04 joint branch. Reverify that actual endpoint
   # through the unchanged reference pose/load/grip logic before retaining it.
   oldseg=ch.seg;ch.seg=dict(oldseg,poses=[hb]);endpoint=f.replay(ch,dict(k=getattr(ch,'witness_k',0),poses=[dict(q=path[-1].tolist())]));ch.seg=oldseg
   if endpoint['ok']:
    pl.restarts=1;return pl.result(True,start,path,route='straight Cartesian working stroke; coherent IK final pose reverified',process_line_verified=True,contact_windows=wa+wb,new_final_static_witness=endpoint)
   failure=dict(reason='Coherent working endpoint failed reference pose/load/grip replay',witness=endpoint)
  # Still give RRT its full budget as a collision diagnostic; a detour does
  # not count as the required working stroke.
  ch.contact_windows=[];ch.working_stroke=False;pl.hands=shared;diag=pl.plan(a,b,ha,hb)
  return dict(diag,ok=False,verified_witnesses=0,working_line_blocker=failure,reason='Working Cartesian path failed; RRT diagnostic cannot replace process geometry',contact_windows=wa+wb)
 pa,fa=lift(ch,a,ha,wa,pl,deadline);pb,fb=lift(ch,b,hb,wb,pl,deadline)
 if pa is not None and pb is not None:
  ch.contact_windows=[];pl.hands={side:dict(h,contacts=[]) for side,h in ha.items()}
  out=pl.plan(pa[-1],pb[-1],pl.hands,pl.hands)
  if out['ok']:
   out['path']=[q.tolist() for q in pa[:-1]]+out['path']+[q.tolist() for q in reversed(pb[:-1])];out['route']='straight <=50mm support windows + '+out['route'];out['contact_windows']=wa+wb;out['planner_time_s']=time.monotonic()-start;out['new_final_static_witness']=new_endpoint;out['new_initial_static_witness']=new_initial
  return out
 # An extraction failure is a geometric blocker. Restarts still receive a
 # full 65s budget to explore a direct window-constrained route.
 out=pl.plan(a,b,ha,hb);out.update(lift_failures=[x for x in (fa,fb) if x],contact_windows=wa+wb,new_final_static_witness=new_endpoint,new_initial_static_witness=new_initial);return out
def scene(ph,sg,index):
 ch=s.Checker(ph,sg);root=E.fromstring(ch.xml);w=root.find('worldbody');active={h['product'] for h in sg['poses'][0].values() if h['held'] in ('root_food','food_cup','cut_cassette','colander','carried_bowl')}
 if w.find("geom[@name='clamped_food']") is not None:active.add(next(iter(sg['poses'][0].values()))['product'])
 # Retain every not-yet-processed whole input as an obstacle, and fill already
 # delivered bowls. These added obstacles are never silently omitted.
 completed={'carrot':index>40,'potato':index>79,'leafy_greens':index>91,'tomato':index>99}
 for prod,x,y in [('carrot',-1.685,.095),('potato',-1.535,.095),('leafy_greens',-1.685,.245),('tomato',-1.535,.245)]:
  if prod in active:continue
  sz=next(a['input_size_m'] for a in s.P['finished_products'] if a['product']==prod)
  if completed[prod]:
   body=w.find("body[@name='stored_bowl_"+prod+"']")
   if body is not None:s.model.box(body,'retained_contents_'+prod,[.179-sz[2]/2,0,0],[sz[2],sz[1],sz[0]],robot=False)
  else:s.model.box(w,'staged_raw_'+prod,[x,y,.942+sz[2]/2],sz,robot=False)
 ch.xml=E.tostring(root,encoding='unicode');ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));return ch
def main():
 lo,hi=map(int,sys.argv[1:3]);mode=sys.argv[3] if len(sys.argv)>3 else 'all';ws=json.loads((O/'static_all.json').read_text())['witnesses'];records=[];begin=time.monotonic();dest=O/f'motion_{mode}_{lo}_{hi}.json'
 for i in range(lo,min(hi,len(items))):
  ph,sg,key=items[i];w=ws[key]
  if mode=='all' or mode.startswith('internal'):
   ch=scene(ph,sg,i);ch.witness_k=w['k'];ch.refine_support_endpoints='exact' in mode;edges=[]
   for j in range(len(w['poses'])-1):
    ch.refine_start_allowed=j==0 or not edges[-1]['ok']
    a=np.array(edges[-1]['path'][-1]) if edges and edges[-1]['ok'] else np.array(w['poses'][j]['q']);b=shortq(ch,a,w['poses'][j+1]['q']);out=plan_section(ch,a,b,sg['poses'][j],sg['poses'][j+1],50500+i*11+j,process=sg['action']=='process');edges.append(out)
   records.append(dict(kind='internal',index=i,stroke=key,ok=all(e['ok'] for e in edges),edges=edges,simultaneous_arms=list(sg['poses'][0]),scene='full template + other raw inputs/delivered contents',meal_state_verified=False))
  if i+1<len(items) and (mode=='all' or mode.startswith('connection')):
   ph2,sg2,key2=items[i+1];w2=ws[key2];ch=scene(ph,sg,i);ch.witness_k=w2['k'];ch.refine_support_endpoints='exact' in mode;a=np.array(w['poses'][-1]['q']);b=shortq(ch,a,w2['poses'][0]['q']);ha=sg['poses'][-1];hb=sg2['poses'][0]
   compatible=signature(ha)==signature(hb);goal_attempts=[]
   if compatible:
    nextch=scene(ph2,sg2,i+1);nextch.search_carriage=True;nextch.set_contacts(hb);t0=time.monotonic()
    for kk in range(4):
     seedq=a.copy()
     if kk:
      rng=np.random.default_rng(80500+i*4+kk)
      for side in hb:
       for n in s.ck.ARMS[side]:seedq[nextch.qa[n]]=np.clip(seedq[nextch.qa[n]]+rng.normal(0,.15),*nextch.m.jnt_range[nextch.jid[n]])
     candidate,errors=nextch.solve_least(seedq,hb,w2['k']);oldseg=nextch.seg;nextch.seg=dict(oldseg,poses=[hb]);verify=f.replay(nextch,dict(k=w2['k'],poses=[dict(q=candidate.tolist())]));nextch.seg=oldseg
     goal_attempts.append(dict(seed=kk,errors=errors,verified=verify['ok'],q=candidate.tolist()))
     if verify['ok'] and np.linalg.norm(candidate-a)<np.linalg.norm(b-a):b=shortq(ch,a,candidate);break
     if time.monotonic()-t0>12:break
   # No attachment substitution is permitted. Incompatible transitions get a
   # loaded predecessor-scene geometric diagnostic and remain failed until the
   # explicit release/acquire/handoff events have geometric witnesses.
   out=plan_section(ch,a,b,ha,hb if compatible else {side:dict(h,contacts=[]) for side,h in ha.items()},60500+i)
   prior_ok=out['ok'];dual=None
   if compatible and prior_ok:
    ch2=scene(ph2,sg2,i+1);check=Planner(ch2,hb,70500+i,65);ch2.contact_windows=out.get('contact_windows',[]);path=[np.array(q) for q in out['path']]
    dual=all(check.edge(x,y,hb,hb,time.monotonic()+65) for x,y in zip(path,path[1:]));prior_ok=dual
   records.append(dict(kind='connection',index=i,from_stroke=key,to_stroke=key2,ok=compatible and prior_ok,geometry_ok=out['ok'],compatible_attachment=compatible,dual_scene_verified=dual,goal_ik_attempts=goal_attempts,meal_state_verified=False,reason=None if compatible and prior_ok else 'Explicit release/acquire or food/fixture handoff is still required' if not compatible else 'Planner or dual-scene check failed',planner=out))
  print(mode,i,key,'ok',records[-1]['ok'],'elapsed',round(time.monotonic()-begin,1),flush=True);dest.write_text(json.dumps(dict(records=records,elapsed_s=time.monotonic()-begin),indent=2))
if __name__=='__main__':main()
