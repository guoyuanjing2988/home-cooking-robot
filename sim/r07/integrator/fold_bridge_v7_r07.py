"""Local elastic-band proposals plus full-budget RRT; unchanged final gates."""
import os,sys,json,time,math,hashlib,copy
os.environ['R07_LAYOUT']=sys.argv[1]
import numpy as np,mujoco
from motion_v7_r07 import v,Planner,mo
from point_bound import PointBound
ID=v.ID;H=v.H;O=v.O;idle=json.loads((O/'layouts'/f'{ID}_idle.json').read_text());ch=v.scene(0);ch.xml=(H/'models'/f'{ID}_fold_closed_doors.xml').read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False
source_index=58 if '--meal-end' in sys.argv else 0;source_text=(O/'static_v7'/ID/f'{source_index}.json').read_text();work=json.loads(source_text)['witness'];a=np.array(work['poses'][-1 if source_index==58 else 0]['q']);b=mo.shortq(ch,a,np.array(idle['q']));pb=PointBound(ch);names=v.s.ck.ARMS['R']+['R_carriage_x'];ix=[ch.qa[n] for n in names];di=[ch.da[n] for n in names];lim=np.array([ch.m.jnt_range[ch.jid[n]] for n in names]);rng=np.random.default_rng(984800);start=time.monotonic();budget=240;deadline=start+budget;stats=[];best=None
def repair(q,anchor,until):
 q=q.copy();last=None
 for _ in range(12):
  if time.monotonic()>until:break
  hits=v.f.contacts(ch,q)[0]
  if not hits:return q,True
  last=hits;grad=np.zeros(len(ix));count=0;m,d=ch.m,ch.d;mujoco.mj_comPos(m,d)
  for h in hits[:16]:
   ga,gb=(ch.gnames.index(n) for n in h['pair']);witness=np.zeros(6);gap=mujoco.mj_geomDistance(m,d,ga,gb,.06,witness);normal=witness[:3]-witness[3:];length=np.linalg.norm(normal)
   if length<1e-10:continue
   normal=normal/length*(-1 if gap<0 else 1);ja=np.zeros((3,m.nv));jb=np.zeros_like(ja);jr=np.zeros_like(ja);mujoco.mj_jac(m,d,ja,jr,witness[:3],int(m.geom_bodyid[ga]));mujoco.mj_jac(m,d,jb,jr,witness[3:],int(m.geom_bodyid[gb]));j=normal@(ja-jb)[:,di];den=float(j@j)
   if den<1e-12:continue
   grad+=j*max(0,h['required_gap_mm']/1000+.004-gap)/den;count+=1
  if not count:break
  delta=grad/count;delta*=min(1,.08/max(abs(delta),default=1));q[ix]=np.clip(q[ix]+delta,lim[:,0]+1e-8,lim[:,1]-1e-8)
 return q,False
pl=Planner(ch,{},seconds=65);pl.restarts=1;pl.step=.020
for restart in range(6):
 if time.monotonic()>deadline:break
 path=[a+(b-a)*t for t in np.linspace(0,1,25)];offset=np.zeros_like(a)
 if restart:
  offset[ix]=rng.normal(0,.10 if restart<3 else .25,len(ix));offset[ch.qa['R_carriage_x']]*=.25
 for i in range(1,len(path)-1):path[i]=path[i]+np.sin(np.pi*i/(len(path)-1))*offset;path[i][ix]=np.clip(path[i][ix],lim[:,0]+1e-8,lim[:,1]-1e-8)
 if restart in (1,2,4,5):
  opening=.025 if restart in (1,4) else .04
  for i in range(1,len(path)-1):
   for side in ('minus','plus'):path[i][ch.qa['R_jaw_'+side]]+=np.sin(np.pi*i/(len(path)-1))*opening
 round_deadline=min(deadline,time.monotonic()+40);record=dict(restart=restart,projection_rounds=[],pass_=False)
 for iteration in range(12):
  if time.monotonic()>round_deadline:break
  count=0
  for i in range(1,len(path)-1):
   path[i],ok=repair(path[i],path[i],round_deadline);count+=not ok
   if time.monotonic()>round_deadline:break
  broken=[];added=[]
  for i,(x,y) in enumerate(zip(path,path[1:])):
   if time.monotonic()>round_deadline:break
   if not pl.edge(x,y,{}, {},deadline=round_deadline):
    broken.append(i)
    if len(path)+len(added)<150:added.append((i,(x+y)/2))
  record['projection_rounds'].append(dict(iteration=iteration,invalid_waypoints=count,broken_edges=len(broken),points=len(path)))
  if not broken and time.monotonic()<round_deadline:best=path;record['pass_']=True;break
  for i,q in reversed(added):path.insert(i+1,q)
 stats.append(record);print('BRIDGE_PROPOSAL',ID,restart,record['pass_'],record['projection_rounds'][-1] if record['projection_rounds'] else None,flush=True)
 if best:break
# Every search has the required >=60s budget; valid proposals can finish early.
# Shortcutting is proposal-only. All acceptance below uses<=4mm and loads.
shortcuts=0
if best:
 for _ in range(16):
  if len(best)<3 or time.monotonic()>deadline:break
  i,j=sorted(rng.choice(len(best),2,replace=False));shortcuts+=1
  if j>i+1 and pl.edge(best[i],best[j],{}, {},deadline=deadline):best=best[:i+1]+best[j:]
fallback=None
if best is None:
 v.s.PARK=b.copy();fallback=Planner(ch,{},seed=984900,seconds=65).plan(a,b,{},{});best=[np.array(q) for q in fallback['path']] if fallback['ok'] else None
states=[];step=0.;ratio=0.;bad=None;verify_deadline=time.monotonic()+450
if best:
 pl.step=.004
 for si,(x,y) in enumerate(zip(best,best[1:])):
  n=max(1,math.ceil(pb.segment_bound(x,y)/.004));step=max(step,pb.segment_bound(x,y)/n)
  for k in range(n+1):
   q=x+(y-x)*k/n
   if time.monotonic()>verify_deadline:bad={'reason':'final replay deadline'};break
   ok=pl.state(q,{}) and all(lim[j,0]-1e-8<=q[idx]<=lim[j,1]+1e-8 for j,idx in enumerate(ix));tq=ch.torque_multi(q,{}, {})['ratio'];ratio=max(ratio,tq)
   if not ok or tq>1:bad=dict(reason='gate or load',blocker=copy.deepcopy(pl.last),ratio=tq);break
   states.append(dict(q=q.tolist(),segment=si,alpha=k/n))
  if bad:break
good=bool(best is not None and bad is None and idle['snapshot_pass']);suffix='return_bridge_v7' if source_index==58 else 'fold_bridge_v7';out=dict(layout=ID,pass_=good,reverse_unfold_pass=good,source_index=source_index,source_static_sha256=hashlib.sha256(source_text.encode()).hexdigest(),start_q=a.tolist(),park_q=b.tolist(),source_static_witness=work,model_xml=f'models/{ID}_fold_closed_doors.xml',model_sha256=hashlib.sha256(ch.xml.encode()).hexdigest(),allocated_budget_s=budget,restarts=stats,shortcut_trials=shortcuts,fallback=fallback,path=[q.tolist() for q in best] if best else [],states=states,max_point_step_mm=step*1000,max_envelope_ratio=ratio,blocker=bad,elapsed_s=time.monotonic()-start,scope='Full populated prospective idle scene, closed leaves; reverse uses identical bounded states and gravity loads. Not an executed meal endpoint.',executed_meal=False)
(O/'layouts'/f'{ID}_{suffix}.json').write_text(json.dumps(out,indent=2));print('BRIDGE_FINAL',ID,good,len(states),flush=True)
