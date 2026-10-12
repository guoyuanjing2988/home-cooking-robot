"""Full-range R05 planner adapter; accepted paths receive independent load replay."""
import os,sys,json,time,math,itertools,hashlib,copy
os.environ['R07_LAYOUT']=sys.argv[1]
import numpy as np,mujoco
from scipy.spatial.transform import Rotation,Slerp
from scipy.optimize import least_squares
import runtime_v4_r07 as v
from planner_r05 import Planner as BasePlanner
from point_bound import PointBound
mo=v.rt.install_motion_policy()
from oriented_motion_v4_r07 import install as install_oriented
install_oriented(mo)
class Planner(BasePlanner):
 def __init__(self,*args,**kw):
  super().__init__(*args,**kw)
  self.limits=np.array([self.ch.m.jnt_range[self.ch.jid[n]] for n in self.names])
mo.Planner=Planner

def continuation_ik(ch,q,targets):
 """Exact Cartesian continuation with carriage redundancy and periodic rebasing."""
 names=[n for side in targets for n in v.s.ck.ARMS[side]+[side+'_carriage_x']];ix=[ch.qa[n] for n in names];limits=np.array([ch.m.jnt_range[ch.jid[n]] for n in names]);out=q.copy()
 for n,i in zip(names,ix):
  if 'carriage' in n:continue
  lo,hi=ch.m.jnt_range[ch.jid[n]];equiv=[q[i]+k*2*np.pi for k in range(-2,3) if lo+1e-7<=q[i]+k*2*np.pi<=hi-1e-7]
  if equiv:out[i]=min(equiv,key=abs)
 seed=out[ix].copy()
 def residual(x):
  out[ix]=x;ch.d.qpos[:]=out;mujoco.mj_kinematics(ch.m,ch.d);values=[]
  for side,(p,r) in targets.items():
   sid=ch.m.site(side+'_prep').id;values.extend((ch.d.site_xpos[sid]-p)*10);values.extend(Rotation.from_matrix(r.T@ch.d.site_xmat[sid].reshape(3,3)).as_rotvec())
  return np.r_[values,(x-seed)*1e-6]
 res=least_squares(residual,np.clip(seed,limits[:,0]+1e-8,limits[:,1]-1e-8),bounds=(limits[:,0],limits[:,1]),max_nfev=150,xtol=1e-11,ftol=1e-11,gtol=1e-11)
 candidate=mo.shortq(ch,q,out)
 if int(v.ID[1:])>=20 and getattr(ch,'working_stroke',False):
  # Keep the Cartesian working target, but allow the inactive arm and both
  # carriages to clear the full scene at intermediate poses. The copied R05
  # checker and final<=4mm replay still decide acceptance.
  from least_analytic_v4_r07 import solve as avoid
  original_hands=ch.hands;hands=copy.deepcopy(original_hands)
  for side,(p,r) in targets.items():
   hands[side].update(pos=np.array(p).tolist(),approach=r[:,0].tolist(),jaw_axis=(-r[:,1]).tolist(),roll_deg=0)
  ch.hands=hands;ch.set_contacts(hands);hits=v.f.contacts(ch,candidate)[0]
  if hits:
   started=time.monotonic();ch.lock_initial_carriage=False;candidate,errors,hh,_=avoid(ch,candidate,hands,0,started+20)
   if not hasattr(ch,'working_ik_diagnostics'):ch.working_ik_diagnostics=[]
   ch.working_ik_diagnostics.append(dict(actual_s=time.monotonic()-started,allocated_s=20,errors=errors,remaining_hits=hh[:5],both_carriages_and_inactive_arm=True))
   ch.hands=original_hands;ch.set_contacts(original_hands)
   return candidate,not hh and all(e['position_mm']<=5 and e['orientation_deg']<=3 for e in errors)
  ch.hands=original_hands;ch.set_contacts(original_hands)
 return candidate,np.linalg.norm(res.fun[:6*len(targets)])<1e-5
mo.ik=continuation_ik

def replay(ch,sg,w,edges):
 pb=PointBound(ch);states=[];bad=None;maximum=0.;mingrip=float('inf');step=0.;reserve={}
 for ei,e in enumerate(edges):
  if not e['ok']:return dict(pass_=False,reason='planner rejected edge',edge=ei)
  path=np.array(e['path']);ha,hb=sg['poses'][ei:ei+2];ch.working_stroke=sg['action']=='process';ch.contact_windows=e.get('contact_windows',[])
  pl=Planner(ch,ha,seconds=65);common={side:dict(h,contacts=[c for c in h.get('contacts',[]) if c in hb.get(side,{}).get('contacts',[])]) for side,h in ha.items()}
  if ei and np.max(abs(np.array(edges[ei-1]['path'][-1])-path[0]))>1e-9:return dict(pass_=False,reason='disconnected internal edges')
  old=ch.seg;ch.seg=dict(old,poses=[ha,hb]);endpoint=v.f.replay(ch,dict(k=w['k'],poses=[dict(q=path[0].tolist()),dict(q=path[-1].tolist())]));ch.seg=old
  if not endpoint['ok']:return dict(pass_=False,reason='endpoint reference check',endpoint=endpoint)
  rotations={s:Slerp([0,1],Rotation.from_matrix([ch.target_rotation(ha[s],w['k']),ch.target_rotation(hb[s],w['k'])])) for s in ha}
  for si,(a,b) in enumerate(zip(path,path[1:])):
   bound=pb.segment_bound(a,b);count=max(1,math.ceil(bound/.004));step=max(step,bound/count)
   for k in range(count+1):
    t=k/count;q=a+(b-a)*t;hands=ha if si==0 and k==0 else hb if si==len(path)-2 and k==count else common
    if not pl.state(q,hands):bad=dict(kind='gap',detail=pl.last);break
    for cat,ix in ch.bounds.catids.items():
     lower=ch.bounds.last_lower[ix];keep=lower<1000.
     if np.any(keep):reserve.setdefault(cat,[]).append(float(np.min((lower[keep]-ch.bounds.need[ix][keep])*1000)))
    for fv in itertools.product(*[h['check_forces_N'] for h in hands.values()]):
     for mv in itertools.product(*[h['check_moments_Nm'] for h in hands.values()]):
      forces=dict(zip(hands,fv));moments=dict(zip(hands,mv));tq=ch.torque_multi(q,hands,forces,moments);maximum=max(maximum,tq['ratio']);grips=[ch.grip_side(q,h,forces[s],moments[s],s)['margin'] for s,h in hands.items()];mingrip=min(mingrip,min(grips,default=float('inf')))
      if tq['ratio']>1 or min(grips,default=1)<1:bad=dict(kind='load/grip',torque=tq,grip=min(grips,default=1));break
     if bad:break
    if ch.working_stroke and not bad:
     alpha=(si+t)/(len(path)-1)
     for side in ha:
      sid=ch.m.site(side+'_prep').id;target=(1-alpha)*np.array(ha[side]['pos'])+alpha*np.array(hb[side]['pos']);pe=float(np.linalg.norm(ch.d.site_xpos[sid]-target)*1000);oe=float(np.degrees(np.linalg.norm(Rotation.from_matrix(rotations[side](alpha).as_matrix().T@ch.d.site_xmat[sid].reshape(3,3)).as_rotvec())))
      if pe>5 or oe>3:bad=dict(kind='working line',position_mm=pe,orientation_deg=oe);break
    states.append(dict(edge=ei,segment=si,alpha=t,q=q.tolist()))
    if bad:break
   if bad:break
  if bad:break
 ch.working_stroke=False;ch.contact_windows=[]
 stats={cat:dict(state_minimum_count=len(x),min_mm=min(x),p05_mm=float(np.percentile(x,5)),median_mm=float(np.median(x)),p95_mm=float(np.percentile(x,95)),max_mm=max(x),fraction_at_least10mm=float(np.mean(np.round(np.array(x),9)>=10))) for cat,x in reserve.items()}
 return dict(pass_=bad is None,blocker=bad,states=states,states_checked=len(states),max_point_step_mm=step*1000,max_envelope_ratio=maximum,min_grip_margin=None if math.isinf(mingrip) else mingrip,clearance_distribution=stats,model_sha256=hashlib.sha256(ch.xml.encode()).hexdigest(),meal_state_verified=False)

if __name__=='__main__':
 mode=sys.argv[2];out=v.O/'motion_v4'/v.ID;out.mkdir(parents=True,exist_ok=True)
 if mode=='internal':
  for index in map(int,sys.argv[3:]):
   saved=json.loads((v.O/'static_v4'/v.ID/f'{index}.json').read_text());w=saved['witness']
   if not w:continue
   ph,sg,key=v.items[index];ch=v.scene(index);ch.witness_k=w['k'];ch.refine_support_endpoints=True;edges=[]
   checkpoint=v.H/'audit'/f'{v.ID}_internal_{index}_partial.json'
   signature=hashlib.sha256((ch.xml+json.dumps(w,sort_keys=True)).encode()).hexdigest()
   if checkpoint.exists():
    old=json.loads(checkpoint.read_text())
    if old.get('signature')==signature:edges=old['edges']
   # R05 staging sampler now draws around an admitted full-scene configuration.
   v.s.PARK=np.array(w['poses'][0]['q'])
   for j in range(len(edges),len(w['poses'])-1):
    a=np.array(edges[-1]['path'][-1]) if edges and edges[-1]['ok'] else np.array(w['poses'][j]['q']);b=mo.shortq(ch,a,w['poses'][j+1]['q']);ch.refine_start_allowed=j==0
    result=mo.plan_section(ch,a,b,sg['poses'][j],sg['poses'][j+1],907000+index*10+j,process=sg['action']=='process');result['working_ik_diagnostics']=getattr(ch,'working_ik_diagnostics',[]);edges.append(result)
    checkpoint.write_text(json.dumps(dict(signature=signature,index=index,layout=v.ID,edges=edges),indent=2));print('EDGE',index,j,result['ok'],flush=True)
   final=replay(ch,sg,w,edges);row=dict(index=index,stroke=key,layout=v.ID,ok=final['pass_'],edges=edges,final_replay=final,meal_state_verified=False,jaw_axis_branch=w['k'],endpoint_witness=w,source_static_sha256=hashlib.sha256((v.O/'static_v4'/v.ID/f'{index}.json').read_bytes()).hexdigest())
   (out/f'internal_{index}.json').write_text(json.dumps(row,indent=2));(v.H/'models'/f'{v.ID}_internal_{index}.xml').write_text(ch.xml)
   print('INTERNAL',index,row['ok'],final.get('states_checked'),flush=True)
 elif mode=='passing':
  # Same populated working scene and attachment throughout. Failed endpoint
  # roots still get a bounded diagnostic; no attachment substitution occurs.
  index=int(sys.argv[3]);saved=json.loads((v.O/'static_v4'/v.ID/f'{index}.json').read_text());w=saved['witness'];ch=v.scene(index);ha=copy.deepcopy(v.items[index][1]['poses'][0]);ha={s:dict(h,contacts=[]) for s,h in ha.items()};a=np.array(w['poses'][0]['q']);b=a.copy();ri,li=[ch.qa[s+'_carriage_x'] for s in ('R','L')];b[ri],b[li]=a[li],a[ri];v.s.PARK=a.copy();ch.working_stroke=False;ch.contact_windows=[]
  result=Planner(ch,ha,seed=907999,seconds=65).plan(a,b,ha,ha)
  row=dict(pass_=False,geometry_proposal_pass=result['ok'],planner=result,q_crossing=((a+b)/2).tolist(),model_xml=f'models/{v.ID}_passing.xml',scope='Full populated carrot-wash scene, held carrot retained; swapping carriage X only is a passing diagnostic. No full meal or idle credit.')
  (out/'passing.json').write_text(json.dumps(row,indent=2));(v.H/'models'/f'{v.ID}_passing.xml').write_text(ch.xml);print('PASSING',result['ok'],flush=True)
