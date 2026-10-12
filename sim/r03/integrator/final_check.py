"""Independent literal-reference replay, narrow geometric contact audit and ledger."""
import os
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[n]='1'
import json,copy,math,hashlib,itertools,csv,sys
from collections import Counter
import numpy as np,mujoco,mink
import solver as s
H=s.HERE;O=H/'results';STAGE=sys.argv[1] if len(sys.argv)>1 else 'final4'

def write(name,p):s.ck.json_write(O/name,p)
def intentional(ch,c):
 a,b=map(int,c.geom);names=[ch.gnames[a],ch.gnames[b]]
 for contact in ch.allowed:
  part=contact['side']+'_held_'
  for name in contact['held_parts']:
   if set(names)!={contact['face'],part+name}:continue
   f=ch.gnames.index(contact['face']);n=contact['face'];normal=np.array(c.frame[:3])
   # A named slab is its top face, not its sides or underside. Contact positions
   # are midpoint witnesses, permitting the specified6mm bristle compression.
   if n in ('clamped_food','wash_food'):return True
   if n.startswith('peel_endstop'):
    sign=-1 if n.endswith('-1') else 1
    face=ch.d.geom_xpos[f,0]-sign*ch.m.geom_size[f,0]
    return abs(normal[0])>=.85 and abs(c.pos[0]-face)<=.0065
   top=ch.d.geom_xpos[f,2]+ch.m.geom_size[f,2]
   return abs(normal[2])>=.85 and c.pos[2]>=top-.0065
 return False

def required(ch,a,b):
 m=ch.m;ra,rb=ch.robot[a],ch.robot[b]
 if not ra and not rb:return None
 ns=[ch.gnames[a],ch.gnames[b]]
 if 'north_wall' in ns and any(n.startswith('wall_mount_') for n in ns):return None
 if ch.weld[a]==ch.weld[b] or tuple(sorted((a,b))) in ch.acm:return None
 wa,wb=ch.weld[a],ch.weld[b]
 if m.body_weldid[m.body_parentid[wa]]==wb or m.body_weldid[m.body_parentid[wb]]==wa:return None
 if 'floor' in ns and not(ch.held[a] or ch.held[b]):
  other=b if ns[0]=='floor' else a
  if not any(k in ch.bnames[other] for k in ('arm','tool','gripper','finger')):return None
 if ra and rb:
  if ch.gripper(a) and ch.gripper(b) and ch.side(a)==ch.side(b):return None
  return (0.,'self') if ch.side(a)==ch.side(b) else (.01,'arm_arm_or_frame')
 g=a if ra else b
 return (.005,'held_gripper_environment') if ch.gripper(g) or ch.held[g] else (.01,'robot_environment')

def contacts(ch,q):
 # The original routine is executed without its broad intended-set shortcut.
 ch.intended=set();literal=s.ck.Checker.forbidden(ch,q);allowed=Counter();mins={};extra=[]
 for c in ch.d.contact[:ch.d.ncon]:
  a,b=map(int,c.geom);req=required(ch,a,b)
  if req is None:continue
  if intentional(ch,c):allowed[frozenset([ch.gnames[a],ch.gnames[b]])]+=1;continue
  need,cat=req;gap=float(c.dist);value=dict(pair=[ch.gnames[a],ch.gnames[b]],clearance_mm=gap*1000,required_mm=need*1000,reserve_mm=(gap-need)*1000,lower_bound=False)
  if cat not in mins or gap<mins[cat]['clearance_mm']/1000:mins[cat]=value
  if gap<need-1e-6:extra.append(dict(pair=value['pair'],real_gap_mm=gap*1000,required_gap_mm=need*1000))
 # All loaded collision geoms have10mm margins: missing contact implies>=20mm.
 for cat,need in [('robot_environment',10),('arm_arm_or_frame',10),('held_gripper_environment',5),('self',0)]:
  if cat not in mins:mins[cat]=dict(pair=None,clearance_mm=20.,required_mm=need,reserve_mm=20-need,lower_bound=True)
 # A newly introduced linear-rail parent must not hide contact between an OEM
 # base/arm and a beam, guide, cover or crossbar that is not its mating face.
 frame_prefix=('rail_beam_','rail_guide_','cable_chain_','wall_crossbar_','lane_hanger_')
 for a,n in enumerate(ch.gnames):
  if not n.startswith(('R_geom_','L_link')):continue
  for b,nn in enumerate(ch.gnames):
   if not nn.startswith(frame_prefix) or required(ch,a,b) is not None:continue
   gap=mujoco.mj_geomDistance(ch.m,ch.d,a,b,.020,None)
   value=dict(pair=[n,nn],clearance_mm=gap*1000,required_mm=10.,reserve_mm=(gap-.010)*1000,lower_bound=gap>=.020)
   if gap<mins['arm_arm_or_frame']['clearance_mm']/1000:mins['arm_arm_or_frame']=value
   if gap<.010-1e-6:extra.append(dict(pair=[n,nn],real_gap_mm=gap*1000,required_gap_mm=10.,reason='non-mating rail/frame geometry; mechanical-parent exclusions cannot exempt this pair'))
 return extra,mins,dict(literal_forbidden_before_contact_mapping=len(literal),geometrically_allowed_contacts=sum(allowed.values()),contact_mapping='Named held part versus named top/axial face, contact-normal and face-position checked; no guard, rail, post or whole fixture exempted')

def payload(ch,q,hands):
 ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d);rows=[]
 for side,h in hands.items():
  ids=[ch.m.body(side+n).id for n in ('_tool','_jaw_minus','_jaw_plus')]
  mass=sum(ch.m.body_mass[b] for b in ids)+h['held_kg']
  com=(sum(ch.m.body_mass[b]*ch.d.xipos[b] for b in ids)+h['held_kg']*ch.d.site_xpos[ch.m.site(side+'_mass').id])/mass
  f=ch.m.site(side+'_attachment_site').id;local=ch.d.site_xmat[f].reshape(3,3).T@(com-ch.d.site_xpos[f])
  xy=float(np.linalg.norm(local[:2]));z=float(abs(local[2]));r=float(np.linalg.norm(local))
  ok=mass<=5 and r<=.350 if side=='R' else mass<=2 and xy<=.200 and z<=.180
  rows.append(dict(side=side,total_flange_kg=mass,EOAT_kg=mass-h['held_kg'],CoM_flange_m=local.tolist(),CoM_radius_m=r,CoM_xy_m=xy,OEM_payload_chart_ok=ok,chart_gate='UR5e <=5kg and <=350mm radius' if side=='R' else 'xArm6 conservative2kg curve: <=200mm radial and <=180mm axial; no use of5kg curve for actual long EOAT'))
 return rows

def replay(ch,row):
 poses=[];ok=len(row['poses'])==len(ch.seg['poses']);worst={};min_grip=1e30
 for i,po in enumerate(row['poses']):
  if i>=len(ch.seg['poses']):ok=False;break
  q=np.array(po['q']);hands=ch.seg['poses'][i];ch.set_contacts(hands);ch.allowed=copy.deepcopy(ch.allowed)
  hits,clearance,contact_audit=contacts(ch,q)
  cfg=mink.Configuration(ch.m,q=q);errors=[]
  for side,h in hands.items():
   task=mink.FrameTask(side+'_prep','site',position_cost=1.,orientation_cost=.5,lm_damping=1e-4)
   task.set_target(mink.SE3.from_rotation_and_translation(mink.SO3.from_matrix(ch.target_rotation(h,row['k'])),np.array(h['pos'])))
   e=task.compute_error(cfg);errors.append(dict(side=side,position_mm=float(np.linalg.norm(e[:3])*1000),orientation_deg=float(np.degrees(np.linalg.norm(e[3:])))))
  ranges=all(ch.m.jnt_range[ch.jid[n],0]-1e-8<=q[ch.qa[n]]<=ch.m.jnt_range[ch.jid[n],1]+1e-8 for n in ch.qa)
  torques={};grips={}
  for level in ('nominal','check'):
   cases=[]
   for fv in itertools.product(*[h[level+'_forces_N'] for h in hands.values()]):
    for mv in itertools.product(*[h[level+'_moments_Nm'] for h in hands.values()]):
     fs=dict(zip(hands,fv));ms=dict(zip(hands,mv));tq=ch.torque_multi(q,hands,fs,ms)
     gs=[ch.grip_side(q,h,fs[side],ms[side],side) for side,h in hands.items()]
     cases.append((tq,gs,fs,ms))
   tc=max(cases,key=lambda x:x[0]['ratio']);gc=min(cases,key=lambda x:min(g['margin'] for g in x[1]))
   torques[level]=dict(tc[0],wrench_forces_N=tc[2],wrench_moments_Nm=tc[3]);grips[level]=gc[1]
   worst[level]=max(worst.get(level,0),tc[0]['ratio']);min_grip=min(min_grip,min(g['margin'] for g in gc[1]))
  pv=payload(ch,q,hands)
  # The OEM table publishes motor torque and gearbox ratio, not continuous
  # joint-output torque. Its ideal projection is reported, never the pass gate.
  diag={n:torques['check']['demand_Nm'][n]/v for n,v in zip(s.ck.ARMS['L'],[64,64,32,32,12,12])}
  valid=not hits and ranges and all(e['position_mm']<=5 and e['orientation_deg']<=3 for e in errors) and torques['check']['ratio']<=1 and all(g['margin']>=1 for g in grips['check']) and all(p['OEM_payload_chart_ok'] for p in pv)
  ok=ok and valid
  poses.append(dict(q=q.tolist(),errors=errors,public_ranges_ok=ranges,forbidden=hits,min_clearance=clearance,contact_audit=contact_audit,torque_ratios=torques,grip=grips,payload=pv,OEM_published_rated_joint_output_ratios=None,xArm_motor_rated_times_gear_ideal_ratios=diag,ideal_ratio_note='1304 motor0.64/0.64/0.32/0.32/0.12/0.12Nm times100:1; gearbox efficiency, thermal output and hardware revision are not certified.'))
 return dict(k=row['k'],ok=ok,poses=poses,max_envelope_ratios=worst,min_grip_margin=min_grip)

def main():
 env=json.loads((O/'envelope_reachability_audit.json').read_text());assert env['all_witnesses_reachable']
 signature=hashlib.sha256((json.dumps(s.P,sort_keys=True)+json.dumps(s.model.CONFIG,sort_keys=True)+(H/'model.py').read_text()+(H/'solver.py').read_text()).encode()).hexdigest()
 trial=json.loads((O/'process_trial_final6.json').read_text()) if STAGE=='final7' else None
 trial_signature=hashlib.sha256((json.dumps(trial,sort_keys=True)+json.dumps(s.model.CONFIG,sort_keys=True)+(H/'model.py').read_text()+(H/'solver.py').read_text()).encode()).hexdigest() if trial else None
 if trial:
  assert all(s.P[k]==trial[k] for k in ('installed_geometry','tools','finished_products','force_models','acceptance'))
 def physics_segment(sg):return {k:v for k,v in sg.items() if k!='loops'}
 source_stages={}
 phases=[];witnesses={};all_starts=0;all_solutions=0
 (O/'witnesses').mkdir(exist_ok=True)
 for ph in s.P['phases']:
  stage=STAGE if (O/STAGE/(ph['id']+'.json')).exists() else 'final6';source_stages[ph['id']]=stage
  file=O/stage/(ph['id']+'.json');raw=json.loads(file.read_text());parts=[]
  assert raw['complete'] and len(raw['parts'])==len(ph['segments'])
  for sg,part in zip(ph['segments'],raw['parts']):
   assert part['starts']>=96
   if part['signature']!=signature:
    assert trial and part['signature']==trial_signature
    oldph=next(p for p in trial['phases'] if p['id']==ph['id']);oldsg=next(a for a in oldph['segments'] if a['label']==sg['label'])
    assert physics_segment(oldsg)==physics_segment(sg),'Changed geometric/force stroke cannot inherit old solver starts'
   ch=s.Checker(ph,sg);all_starts+=part['starts'];all_solutions+=part['solutions_found']
   # Replay every claimed good start with the stricter explicit-face check.
   good=[r for r in part['rows'] if r['ok']];audited=[replay(ch,r) for r in good];valid=[r for r in audited if r['ok']]
   witness=min(valid,key=lambda r:r['max_envelope_ratios']['check']) if valid else None
   key=ph['id']+'__'+sg['label'].replace(' ','_')
   item=dict(id=key,label=sg['label'],source_stage=stage,starts=part['starts'],solver_solutions_found=part['solutions_found'],independent_verified_witnesses=len(valid),ok=bool(valid),original_blocker=part['best'].get('blocker'),replay_rejected=len(good)-len(valid),witness=witness)
   parts.append(item)
   if witness:
    witnesses[key]=dict(phase=ph['id'],label=sg['label'],**witness)
    (O/'witnesses'/(key+'.xml')).write_text(ch.xml,encoding='utf-8');write('witnesses/'+key+'.json',witness)
   print(key,'verified',len(valid),'/',part['starts'],flush=True)
  phases.append(dict(id=ph['id'],logical_id=ph['id'].split('.')[0],name=ph['name'],replaces_P=ph['replaces_P'],ok=all(p['ok'] for p in parts),parts=parts))
 logical=[]
 for i in range(1,28):
  q=f'Q{i:02d}';ps=[p for p in phases if p['logical_id']==q];logical.append(dict(id=q,ok=bool(ps) and all(p['ok'] for p in ps),instances=[p['id'] for p in ps],failed_strokes=[x['id'] for p in ps for x in p['parts'] if not x['ok']],replaces_P=sorted(set(a for p in ps for a in p['replaces_P']))))
 summary=dict(schema='r03.final.reference_replay',stage=STAGE,config=s.model.CONFIG,logical_passed=sum(p['ok'] for p in logical),logical_total=27,instances_passed=sum(p['ok'] for p in phases),instances_total=len(phases),strokes_passed=sum(x['ok'] for p in phases for x in p['parts']),strokes_total=sum(len(p['parts']) for p in phases),starts_total=all_starts,solutions_found=all_solutions,verified_witnesses=sum(x['independent_verified_witnesses'] for p in phases for x in p['parts']),logical_phases=logical,instances=phases,
  acceptance=s.P['acceptance'],scope='Reference pose, public joint ranges, exact-face contacts, static rated-envelope torque and grip gates. Counts are static stroke acceptance, not a complete meal or food-quality certification.',golden_mandoline=dict(required=False,reason='No mandoline installed; OEM rotary disc used for root slices.'),process_sha256=hashlib.sha256((O/'process_v3.json').read_bytes()).hexdigest(),solver_signature=signature,phase_source_stages=source_stages,cache_proof='Unchanged105-stroke final6 geometry/forces/targets inherit96starts and are independently replayed; changed potato feed has fresh final7 starts. Only recipe loop/timer annotations are excluded from the byte-for-byte stroke equality check; installed geometry, tools, finished products, forces and thresholds must match exactly.')
 write('phase_summary.json',summary)
 best=dict(config=s.model.CONFIG,stage=STAGE,phase_source_stages=source_stages,phases_passed=summary['logical_passed'],phases_total=27,strokes_passed=summary['strokes_passed'],strokes_total=summary['strokes_total'],overall_pass=False,motion_status='pending',witnesses=witnesses,recipe_sha256=summary['process_sha256'],acceptance=s.P['acceptance'],cost_cny=json.loads((O/'cost_summary.json').read_text())['total_cny'],prep_min_planning=json.loads((O/'timeline.json').read_text())['prep_min'],prep_min_verified=None,model_sources=dict(UR5e='https://github.com/google-deepmind/mujoco_menagerie/tree/main/universal_robots_ur5e',xArm6='https://github.com/xArm-Developer/xarm_ros/tree/master/xarm_description'),manufacturing_and_food_quality_qualified=False)
 write('best.json',best)
 print('FINAL',summary['logical_passed'],'/27',summary['strokes_passed'],'/',summary['strokes_total'],flush=True)
if __name__=='__main__':main()
