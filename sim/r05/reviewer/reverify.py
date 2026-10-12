"""Independent stored-pose replay. Never writes integrator artifacts."""
import os,sys
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[n]='1'
from pathlib import Path
import json,itertools,math,collections,copy,time
import numpy as np,mujoco,mink
from scipy.spatial.transform import Rotation
H=Path(__file__).resolve().parent;I=H.parent/'integrator'
sys.path.insert(0,str(I));import solver as s
import final_check as f
O=H/'results';O.mkdir(exist_ok=True)
ENV=json.loads((I/'results/torque_envelope.json').read_text())['envelope_Nm']
def dump(name,value):(O/name).write_text(json.dumps(value,indent=2,allow_nan=False),encoding='utf-8')
def permission(ch,c,hands):
 names=[ch.gnames[int(g)] for g in c.geom]
 for side,h in hands.items():
  for a in h.get('contacts',[]):
   if a['face'] not in names:continue
   other=names[1-names.index(a['face'])]
   if other not in [side+'_held_'+p for p in a['held_parts']]:continue
   face=a['face'];f=ch.gnames.index(face)
   if face in ('clamped_food','wash_food'):return True
   if face.startswith('peel_endstop'):
    sign=-1 if face.endswith('-1') else 1
    plane=ch.d.geom_xpos[f,0]-sign*ch.m.geom_size[f,0]
    return abs(c.frame[0])>=.85 and abs(c.pos[0]-plane)<=.0065
   plane=ch.d.geom_xpos[f,2]+ch.m.geom_size[f,2]
   return abs(c.frame[2])>=.85 and c.pos[2]>=plane-.0065
 return False
def contacts(ch,q,hands,extended=False):
 ch.intended=set();hits=s.ck.Checker.forbidden(ch,q)
 allow=set();allowed_count=0
 for c in ch.d.contact[:ch.d.ncon]:
  if permission(ch,c,hands):
   allow.add(frozenset(ch.gnames[int(g)] for g in c.geom));allowed_count+=1
 # Pair filtering must not exempt a side/underside manifold. Retain forbidden
 # pair if any below-threshold manifold for that pair is not a permitted face.
 forbidden_pairs=set()
 for c in ch.d.contact[:ch.d.ncon]:
  pair=frozenset(ch.gnames[int(g)] for g in c.geom)
  if pair in allow and not permission(ch,c,hands) and c.dist<.005-1e-6:forbidden_pairs.add(pair)
 hits=[h for h in hits if frozenset(h['pair']) not in allow or frozenset(h['pair']) in forbidden_pairs]
 # Retain our separate literal-reference contact/manifold audit. The submitted
 # conservative shape oracle supplies additional all-pair distance checks;
 # independent projection/QP checks are recorded by geometry.py.
 ch.set_contacts(hands)
 certified,mins,proof=f.contacts(ch,q)
 for hit in certified:
  if not any(set(h['pair'])==set(hit['pair']) for h in hits):hits.append(hit)
 return hits,allowed_count
def pose(ch,q,hands,k):
 m,d=ch.m,ch.d;d.qpos[:]=q;d.qvel[:]=0;mujoco.mj_forward(m,d)
 errors=[]
 for side,h in hands.items():
  rt=ch.target_rotation(h,k)
  task=mink.FrameTask(side+'_prep','site',position_cost=1.,orientation_cost=.5,lm_damping=1e-4)
  task.set_target(mink.SE3.from_rotation_and_translation(mink.SO3.from_matrix(rt),np.array(h['pos'])))
  e=task.compute_error(mink.Configuration(m,q=q));errors.append(dict(side=side,position_mm=float(np.linalg.norm(e[:3])*1000),orientation_deg=float(np.linalg.norm(e[3:])*180/math.pi)))
 ranges=all(m.jnt_range[ch.jid[n],0]-1e-8<=q[ch.qa[n]]<=m.jnt_range[ch.jid[n],1]+1e-8 for n in ch.qa)
 hits,na=contacts(ch,q,hands)
 # Derive torque and grip independently of solver/final_check implementations.
 d.qpos[:]=q;d.qvel[:]=0;mujoco.mj_forward(m,d)
 bias=d.qfrc_bias.copy();jp=np.zeros((3,m.nv));jr=np.zeros_like(jp)
 jac={};rot={}
 payload=[]
 for side,h in hands.items():
  mujoco.mj_jacSite(m,d,jp,jr,m.site(side+'_work').id);jw=jp.copy();jm=jr.copy()
  mujoco.mj_jacSite(m,d,jp,jr,m.site(side+'_mass').id);jac[side]=(jw,jm,jp.copy())
  rot[side]=d.site_xmat[m.site(side+'_prep').id].reshape(3,3).copy()
  bids=[m.body(side+n).id for n in ('_tool','_jaw_minus','_jaw_plus')]
  mass=sum(m.body_mass[b] for b in bids)+h['held_kg']
  com=(sum(m.body_mass[b]*d.xipos[b] for b in bids)+h['held_kg']*d.site_xpos[m.site(side+'_mass').id])/mass
  f=m.site(side+'_attachment_site').id
  local=d.site_xmat[f].reshape(3,3).T@(com-d.site_xpos[f]);radius=np.linalg.norm(local);xy=np.linalg.norm(local[:2])
  ok=mass<=5 and radius<=.350 if side=='R' else mass<=2 and xy<=.200 and abs(local[2])<=.180
  payload.append(dict(side=side,total_flange_kg=float(mass),CoM_flange_m=local.tolist(),chart_ok=bool(ok)))
 tq={};gm={}
 for level in ('nominal','check'):
  worst=0;minimum=math.inf
  for fs in itertools.product(*[h[level+'_forces_N'] for h in hands.values()]):
   for ms in itertools.product(*[h[level+'_moments_Nm'] for h in hands.values()]):
    tau=bias.copy()
    for (side,h),f,moment in zip(hands.items(),fs,ms):
     f=np.array(f);moment=np.array(moment);gravity=np.array([0,0,-h['held_kg']*9.81]);jw,jr,jg=jac[side]
     tau-=jw.T@f+jr.T@moment+jg.T@gravity
     demand=np.linalg.norm(f+gravity)
     mt=np.linalg.norm(np.cross(rot[side]@np.array(s.ck.offset_vector(h['work_offset_m'])),f)+np.cross(rot[side]@np.array(s.ck.offset_vector(h['mass_offset_m'])),gravity)+moment)
     grip=.5*150/(1.5*max(demand,1e-12)) if h['grip']=='friction' else min(150/(1.5*max(demand,1e-12)),15/(1.5*max(mt,1e-12)))
     minimum=min(minimum,float(grip))
    ratios={n:float(abs(tau[ch.da[n]])/ENV[n]) for n in s.ck.JOINTS}
    worst=max(worst,max(ratios.values()))
  tq[level]=worst;gm[level]=minimum
 valid=not hits and ranges and all(e['position_mm']<=5 and e['orientation_deg']<=3 for e in errors) and tq['check']<=1 and gm['check']>=1 and all(x['chart_ok'] for x in payload)
 return dict(ok=bool(valid),errors=errors,ranges_ok=bool(ranges),hits=hits,allowed_manifolds=na,torque=tq,grip=gm,payload=payload)
def legacy_phases(ids):
 started=time.monotonic();summary=json.loads((I/'results/phase_summary.json').read_text());output=[]
 for ph in s.P['phases']:
  if ids and ph['id'] not in ids:continue
  stage=summary['phase_source_stages'][ph['id']];raw=json.loads((I/'results'/stage/(ph['id']+'.json')).read_text());parts=[]
  for sg,part in zip(ph['segments'],raw['parts']):
   ch=s.Checker(ph,sg);claimed=0;verified=0;best=None;rejected=[];block=collections.Counter();poses=0;extra=[];torque_delta=0;grip_delta=0
   for row in part['rows']:
    if not row['ok']:continue
    claimed+=1;checks=[pose(ch,np.array(po['q']),sg['poses'][pi],row['k']) for pi,po in enumerate(row['poses'])];poses+=len(checks)
    valid=len(checks)==len(sg['poses']) and all(c['ok'] for c in checks)
    ratio=max(c['torque']['check'] for c in checks);grip=min(c['grip']['check'] for c in checks)
    torque_delta=max(torque_delta,abs(ratio-row['check']['torque']['ratio']));grip_delta=max(grip_delta,abs(grip-row['check']['grip']['margin']))
    if valid:
     verified+=1
     if best is None or ratio<best['ratio']:best=dict(k=row['k'],ratio=ratio,grip=grip,checks=checks)
    else:rejected.append(dict(k=row['k'],checks=checks))
    if claimed==1:
     for pi,po in enumerate(row['poses']):
      hs,_=contacts(ch,np.array(po['q']),sg['poses'][pi],extended=True)
      extra += [dict(pose=pi,**h) for h in hs if h not in checks[pi]['hits']]
   # Fresh reference collision/pose checks of ALL saved failed starts for a
   # failed stroke. Rejected torque-only starts are also fully recomputed.
   recovered=[]
   if not claimed:
    for row in part['rows']:
     cs=[];bad=False
     for pi,po in enumerate(row['poses']):
      q=np.array(po['q']);hs,_=contacts(ch,q,sg['poses'][pi]);poses+=1
      errors=po['errors']
      # Recompute errors rather than trust saved metadata.
      for side,h in sg['poses'][pi].items():
       sid=ch.m.site(side+'_prep').id
       if np.linalg.norm(ch.d.site_xpos[sid]-h['pos'])>.005:bad=True;block['position']+=1
       rt=ch.target_rotation(h,row['k']);er=Rotation.from_matrix(rt.T@ch.d.site_xmat[sid].reshape(3,3)).magnitude()
       if er>math.radians(3):bad=True;block['orientation']+=1
      if hs:bad=True;block['collision']+=1
     if not bad and len(row['poses'])==len(sg['poses']):
      cs=[pose(ch,np.array(po['q']),sg['poses'][pi],row['k']) for pi,po in enumerate(row['poses'])]
      if all(c['ok'] for c in cs):recovered.append(row['k'])
   expected=next(x for x in summary['instances'] if x['id']==ph['id'])['parts'][ph['segments'].index(sg)]['independent_verified_witnesses']
   out=dict(stroke=sg['label'],starts=part['starts'],claimed=claimed,independently_verified=verified,expected=expected,match=verified==expected,poses_recomputed=poses,max_torque_ratio_delta=torque_delta,max_grip_margin_delta=grip_delta,rejected_claims=rejected,recovered_failed_starts=recovered,failed_pose_categories=dict(block),additional_nonmating_hardware_hits=extra,best=best)
   parts.append(out);print(ph['id'],sg['label'],verified,'/',claimed,flush=True)
  output.append(dict(phase=ph['id'],ok=all(x['independently_verified']>0 for x in parts),parts=parts))
 dump('reverify_'+('_'.join(ids) if ids else 'all')+'.json',dict(method='Fresh MuJoCo reference collision replay and independent wrench/Jacobian/grip/pose/payload arithmetic; no IK re-search claimed.',elapsed_s=time.monotonic()-started,phases=output))
 print('complete',round(time.monotonic()-started,2),flush=True)
def phases(ids):
 started=time.monotonic(); submitted=json.loads((I/'results/static_all.json').read_text()); output=[]
 for ph in s.P['phases']:
  if ids and ph['id'] not in ids:continue
  parts=[]
  for sg in ph['segments']:
   key=ph['id']+'__'+sg['label'].replace(' ','_');row=submitted['witnesses'][key];ch=s.Checker(ph,sg)
   checks=[pose(ch,np.array(po['q']),sg['poses'][pi],row['k']) for pi,po in enumerate(row['poses'])]
   ratio=max(c['torque']['check'] for c in checks);grip=min(c['grip']['check'] for c in checks)
   ok=len(checks)==len(sg['poses']) and all(c['ok'] for c in checks)
   parts.append(dict(stroke=key,seed=row['k'],ok=ok,poses=len(checks),max_torque_delta=abs(ratio-row['max_envelope_ratios']['check']),max_grip_delta=abs(grip-row['min_grip_margin']),checks=checks))
   print(key,ok,flush=True)
  output.append(dict(phase=ph['id'],ok=all(p['ok'] for p in parts),strokes=parts))
 logical=[dict(id=f'Q{i:02d}',ok=all(p['ok'] for p in output if p['phase'].split('.')[0]==f'Q{i:02d}')) for i in range(1,28) if any(p['phase'].split('.')[0]==f'Q{i:02d}' for p in output)]
 dump('reverify_'+('_'.join(ids) if ids else 'all')+'.json',dict(method='Fresh stored-pose re-verification, original reference contacts with independently enumerated face permissions; independently derived pose/wrench/grip/payload arithmetic; conservative submitted distance oracle also executed. No new IK search.',elapsed_s=time.monotonic()-started,logical_phases=logical,instances=output,logical_passed=sum(p['ok'] for p in logical),logical_total=len(logical),instances_passed=sum(p['ok'] for p in output),strokes_passed=sum(x['ok'] for p in output for x in p['strokes']),strokes_total=sum(len(p['strokes']) for p in output),poses_total=sum(x['poses'] for p in output for x in p['strokes'])))
 print('complete',round(time.monotonic()-started,2),flush=True)
if __name__=='__main__':phases(sys.argv[1:])
