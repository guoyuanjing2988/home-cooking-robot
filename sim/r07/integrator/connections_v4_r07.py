"""Same-attachment local connections; never substitute for missing meal events."""
import os,sys,json,time,hashlib,math,itertools,copy
os.environ['R07_LAYOUT']=sys.argv[1]
import runtime_v4_r07 as v
import numpy as np,mujoco
from motion_v4_r07 import Planner,mo
from point_bound import PointBound
out=v.O/'motion_v4'/v.ID;out.mkdir(parents=True,exist_ok=True);start=time.monotonic()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fingerprint(ch):
 h=hashlib.sha256('|'.join(ch.gnames).encode())
 for attr in ('geom_pos','geom_quat','geom_size','geom_type','geom_bodyid','body_pos','body_quat','body_mass','body_inertia','jnt_range'):h.update(getattr(ch.m,attr).tobytes())
 return h.hexdigest()
for i in map(int,sys.argv[2:]):
 if time.monotonic()-start>900:break
 files=[out/f'internal_{j}.json' for j in (i,i+1)]
 if not all(p.exists() for p in files):continue
 ms=[json.loads(p.read_text()) for p in files]
 if not all(m['ok'] and m['edges'] for m in ms):continue
 a=np.array(ms[0]['edges'][-1]['path'][-1]);b=np.array(ms[1]['edges'][0]['path'][0]);chs=[v.scene(j) for j in (i,i+1)];ha=copy.deepcopy(v.items[i][1]['poses'][-1]);hb=copy.deepcopy(v.items[i+1][1]['poses'][0])
 row=dict(index=i,from_index=i,to_index=i+1,pass_=False,persistent_meal_pass=False,source_paths=[str(p.relative_to(v.H)) for p in files],source_sha256=[digest(p) for p in files],same_attachment=mo.signature(ha)==mo.signature(hb),same_geometry=fingerprint(chs[0])==fingerprint(chs[1]),scope='Conserved local held-object transition only. Initial acquisition and appliance/event bindings still block full meal credit.')
 if not(row['same_attachment'] and row['same_geometry']):row['status']='BLOCKED_ATTACHMENT_OR_SCENE_CHANGE';(out/f'connection_{i}.json').write_text(json.dumps(row,indent=2));continue
 ch=chs[0];original_b=b.copy();b=mo.shortq(ch,a,b);row['endpoint_periodic_delta_rad']=(b-original_b).tolist()
 # A periodic endpoint is physically equal but must join the subsequent saved
 # joint trajectory without a numerical jump. No connected execution credit if
 # it differs until the whole downstream path is rebased and replayed.
 row['raw_joint_continuity']=bool(np.max(abs(b-original_b))<1e-9)
 for c in chs:c.working_stroke=False;c.contact_windows=[]
 # Endpoint own-support windows only; remove all working declarations.
 for h in (ha,hb):
  for hand in h.values():hand['contacts']=[c for c in hand.get('contacts',[]) if c['kind']=='grasp_release_support'];hand['nominal_forces_N']=[[0,0,0]];hand['check_forces_N']=[[0,0,0]];hand['nominal_moments_Nm']=[[0,0,0]];hand['check_moments_Nm']=[[0,0,0]]
 windows=[w for w in mo.windows(ch,a,ha)+mo.windows(ch,b,hb) if w['kind']=='grasp_release_support'];ch.contact_windows=windows;v.s.PARK=a.copy();pl=Planner(ch,ha,seed=951000+i,seconds=65);result=pl.plan(a,b,ha,hb);row['planner']=result;row['allocated_budget_s']=65;row['contact_windows']=windows
 states=[];bad=None;step=0.;maxratio=0.;mingrip=1e9;pBs=[PointBound(c) for c in chs]
 if result['ok']:
  for c in chs:c.contact_windows=windows
  checkers=[Planner(c,ha,seconds=65) for c in chs]
  for si,(x,y) in enumerate(zip(np.array(result['path']),np.array(result['path'])[1:])):
   bound=max(pb.segment_bound(x,y) for pb in pBs);count=max(1,math.ceil(bound/.004));step=max(step,bound/count)
   for k in range(count+1):
    q=x+(y-x)*k/count;hands=ha if si==0 and k==0 else hb if si==len(result['path'])-2 and k==count else {s:dict(h,contacts=[]) for s,h in ha.items()}
    for c,checker in zip(chs,checkers):
     if not checker.state(q,hands):bad=dict(kind='gap',detail=checker.last);break
     tq=c.torque_multi(q,hands,{s:[0,0,0] for s in hands},{s:[0,0,0] for s in hands});grips=[c.grip_side(q,h,[0,0,0],[0,0,0],s)['margin'] for s,h in hands.items()];maxratio=max(maxratio,tq['ratio']);mingrip=min(mingrip,min(grips,default=1e9))
     if tq['ratio']>1 or min(grips,default=1)<1:bad=dict(kind='load/grip');break
     if not all(not c.m.jnt_limited[c.jid[n]] or c.m.jnt_range[c.jid[n],0]-1e-8<=q[ix]<=c.m.jnt_range[c.jid[n],1]+1e-8 for n,ix in c.qa.items()):bad=dict(kind='range');break
    states.append(dict(q=q.tolist(),segment=si,alpha=k/count))
    if bad:break
   if bad:break
 row.update(pass_=bool(result['ok'] and bad is None and row['raw_joint_continuity']),geometric_path_pass=bool(result['ok'] and bad is None),blocker=bad,states=states,states_checked=len(states),max_point_step_mm=step*1000,max_envelope_ratio=maxratio,min_grip_margin=mingrip if mingrip<1e9 else None,model_xml=f'models/{v.ID}_connection_{i}.xml',model_sha256=hashlib.sha256(ch.xml.encode()).hexdigest())
 (v.H/row['model_xml']).write_text(ch.xml);(out/f'connection_{i}.json').write_text(json.dumps(row,indent=2,allow_nan=False));print('LOCAL_CONNECTION',i,row['pass_'],row['geometric_path_pass'],flush=True)
