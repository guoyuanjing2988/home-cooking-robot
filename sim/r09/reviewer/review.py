"""Read-only independent R09 review; all artifacts stay under reviewer/.
Synthetic negative probes are never credited as physical execution.
Run each mode through bounded.py (CPU, 1900 MiB, foreground timeout).
"""
import os,sys,json,copy,hashlib,difflib,ast,math,time,csv
from pathlib import Path
import xml.etree.ElementTree as E
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[k]='1'
HERE=Path(__file__).resolve().parent;IN=HERE.parent/'integrator';ROOT=HERE.parents[2]
sys.path.insert(0,str(IN))
import numpy as np,mujoco
from scipy.spatial.transform import Rotation
import scene,checker,verify,state,execute,planner,parking
from checker import Checker,reference
CFG=scene.load('results/selected.json')['config']
def save(name,obj):
 p=HERE/'results'/name;p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(obj,indent=2,allow_nan=False,default=lambda x:x.tolist() if isinstance(x,np.ndarray) else x.item()),encoding='utf-8')
def make(held=None):
 tr,meta=scene.build(CFG,held);return Checker(tr,meta),meta
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rot(t,b):
 if 'rotation' in b:return np.array(b['rotation'])
 jaws=[(0,0,1),(0,0,-1),(1,0,0),(-1,0,0)] if abs(t['approach'][1])>.9 else [(0,1,0),(0,-1,0),(1,0,0),(-1,0,0)]
 return reference.rotation(t['approach'],jaws[b['start']%4])
def rules():
 verify.save=lambda _,v:save('submitted_regression.json',v);verify.main()
 src=ROOT/'sim/r05/integrator/reference.py';imp=Path(reference.__file__)
 for name,a,b in [('reference_import',src.read_text(),imp.read_text()),('r08_to_r09_adapter',(ROOT/'sim/r08/integrator/checker.py').read_text(),(IN/'checker.py').read_text()),('reference_vs_adapter',src.read_text(),(IN/'checker.py').read_text())]:
  (HERE/'diffs'/f'{name}.diff').write_text(''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True))),encoding='utf-8')
 # Original reference on the unchanged R07 regression witnesses. No R09
 # floor or mast gate is imposed on these different historical machines.
 admission=json.loads((ROOT/'sim/r07/integrator/results/fresh_admission.json').read_text());reg=[]
 for i in [0,9,54,58]:
  tr=E.parse(ROOT/f'sim/r07/integrator/models/L101_stroke_{i}.xml')
  for mesh in tr.findall('.//mesh'):mesh.set('file',str(IN/'assets'/Path(mesh.get('file')).name))
  c=Checker.__new__(Checker);c.desc={'intended':[]};c.meta={};c.bind_model(mujoco.MjModel.from_xml_string(E.tostring(tr.getroot(),encoding='unicode')));c.intended=set()
  for k,p in enumerate(admission['rows'][i]['reference']['poses']):
   literal=c.forbidden(np.array(p['q']));hits=[h for h in literal if c.required(c,*[c.gnames.index(n) for n in h['pair']]) is not None]
   from distance import Bounds
   more,mins,proof=Bounds(c,c.required).check(frozenset());hits+=more
   ranges=all(c.m.jnt_range[j,0]-1e-8<=p['q'][a]<=c.m.jnt_range[j,1]+1e-8 for j,a in enumerate(c.m.jnt_qposadr))
   expected=not p['forbidden'] and p['public_ranges_ok'];actual=not hits and ranges
   reg.append(dict(stroke=i,endpoint=k,expected_geometry=expected,actual_geometry=actual,expected_hits=p['forbidden'],actual_hits=hits,match=expected==actual,wall_mating_filter='R09 exact named mating face predicate'))
 # Complete arm subtree retained, except rigid mount placement and added full gripper housing.
 old=E.parse(ROOT/'sim/r08/integrator/models/base.xml');new=E.parse(IN/'models/base.xml')
 def arm(tr):
  b=copy.deepcopy(tr.find(".//body[@name='R_mount']"));b.attrib.pop('pos',None);b.attrib.pop('quat',None)
  return [(e.tag,dict(e.attrib)) for e in b.iter()]
 save('rules.json',dict(reference_sha256=sha(src),empty_source_diff=src.read_bytes()==imp.read_bytes(),historical_regression=reg,arm_subtree_equal=arm(old)==arm(new),process_contract_equal=(IN/'assets/process_contract.json').read_bytes()==(ROOT/'sim/r08/integrator/assets/process_contract.json').read_bytes(),constants={k:getattr(reference,k) for k in ('PAD','MU','SF','NORMAL_SUM_N','KEY_FORCE_N','KEY_MOMENT_NM')},distance_equal=(IN/'distance.py').read_bytes()==(ROOT/'sim/r08/integrator/distance.py').read_bytes(),point_bound_equal=(IN/'point_bound.py').read_bytes()==(ROOT/'sim/r08/integrator/point_bound.py').read_bytes()))
 print('rules complete',flush=True)
def probes():
 rows=[]
 def rec(label,accepted,expected=False,detail=None):rows.append(dict(name=label,accepted=bool(accepted),expected_accept=expected,pass_=bool(accepted)==expected,detail=detail))
 ch,meta=make('holder');t=scene.targets(CFG,meta)[6];r=scene.load('results/strokes/6.json');q=np.array(r['internal']['path'][0]);bank=scene.load('results/statics/6_0.json');cand=min(bank['candidates'],key=lambda x:np.linalg.norm(np.array(x['q'])-q));R=np.array(cand['rotation'])
 ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d);ch.configure_target(t,R);base=copy.deepcopy(ch.windows)
 rec('genuine_working_live_FK',bool(ch.permissions('working')),True)
 rec('working_on_transfer',bool(ch.permissions('transfer')))
 for label,key,value in [('wrong_object','object','carrot'),('wrong_support','support','wash_basket'),('wrong_part','parts',['R_held_tray_floor']),('missing_kind','kind',None),('forged_origin','origin',[9,9,9]),('overlong','length_m',.0501),('forged_rotation','rotation',np.eye(3).tolist())]:
  ch.windows=copy.deepcopy(base)
  for w in ch.windows:w[key]=value
  rec(label,bool(ch.permissions('working')))
 ch.windows=copy.deepcopy(base);g=ch.gnames.index('mandoline_deck');ch.m.geom_quat[g]=[2**-.5,0,0,2**-.5]
 mujoco.mj_setConst(ch.m,ch.d);mujoco.mj_forward(ch.m,ch.d)
 rec('support_rotated_after_registration',frozenset(['R_held_holder','mandoline_deck']) in ch.permissions('working'),detail={'world_rotation':ch.d.geom_xmat[g].tolist(),'local_quat':ch.m.geom_quat[g].tolist()})
 for item,part in [('carrot','R_held_carrot'),('catch_tray','R_held_tray_floor')]:
  for mutation,value in [('quat','.707106781187 0 .707106781187 0'),('size','.3 .3 .3')]:
   tr,mm=scene.build(CFG,item);tr.find(f".//geom[@name='{part}']").set(mutation,value)
   try:cc=Checker(tr,mm);accepted=True
   except ValueError:accepted=False
   rec(item+'_constructor_'+mutation,accepted)
 cc,_=make('carrot');g=cc.gnames.index('R_held_carrot');f=cc.gnames.index('R_finger_minus');cc.m.geom_quat[g]=[2**-.5,0,2**-.5,0]
 rec('live_rotated_carrot_grasp',cc.grasp_allowed(g,f));res=cc.check(cc.m.qpos0.copy());rec('live_rotated_full_state',res['ok'],detail={'identity_ok':res['identity_ok']})
 # Support shape is not canonicalized: forge the real named deck before minting.
 tr,mm=scene.build(CFG,'holder');tr.find(".//geom[@name='mandoline_deck']").set('size','.165 .06 .06');cc=Checker(tr,mm);cc.d.qpos[:]=q;mujoco.mj_forward(cc.m,cc.d);cc.configure_target(t,R);res=cc.check(q,kind='working',mass=.55,force=t['force'])
 rec('forged_double_thickness_support_permission',bool(cc.permissions('working')),detail={'full_state_ok':res['ok'],'hits':res['hits'],'identity_ok':res['identity_ok']})
 # Expiry checked through solved FK, never overwrite data.site_xpos.
 from scipy.optimize import least_squares
 cc,mm=make('holder');tt=scene.targets(CFG,mm)[7];rr=scene.load('results/strokes/7.json');qq=np.array(rr['internal']['path'][0]);bb=scene.load('results/statics/7_0.json');Rr=np.array(min(bb['candidates'],key=lambda v:np.linalg.norm(np.array(v['q'])-qq))['rotation']);cc.configure_target(tt,Rr)
 for dist in [.049,.051,.070]:
  pp=np.array(tt['points'][0])+[0,0,dist]
  def fun(x):
   cc.d.qpos[:]=qq;cc.d.qpos[cc.arm_ids]=x;mujoco.mj_kinematics(cc.m,cc.d);sid=cc.m.site('R_prep').id
   return np.r_[10*(cc.d.site_xpos[sid]-pp),Rotation.from_matrix(Rr@cc.d.site_xmat[sid].reshape(3,3).T).as_rotvec()]
  sol=least_squares(fun,qq[cc.arm_ids],max_nfev=100,gtol=1e-12,ftol=1e-12,xtol=1e-12);qq[cc.arm_ids]=sol.x;cc.d.qpos[:]=qq;mujoco.mj_forward(cc.m,cc.d)
  rec('retreat_'+str(dist),bool(cc.permissions('transfer')),dist<.05,{'residual':float(np.linalg.norm(fun(sol.x)))})
 # Independently established synthetic attached safe pose.
 accepted=[r for r in scene.load('results/statics/0_1.json')['rows'] if r['status']=='ok'];qc=np.array(accepted[0]['q']);cc,_=make('carrot')
 def world_at(q0):
  w=state.World();cc.d.qpos[:]=q0;mujoco.mj_forward(cc.m,cc.d);w.objects['carrot'].update(pos=cc.d.site_xpos[cc.m.site('R_prep').id].tolist(),attached=True,support='robot');return w
 for label,path,extra in [('fake_cartesian',[[0]],{'positions':[[9,9,9]]}),('bad_dimensions',[[0],[0]],{}),('nonfinite',[[float('nan')]*cc.m.nq]*2,{}),('oversize_jump',[qc.tolist(),(qc+np.eye(cc.m.nq)[0]*.1).tolist()],{})]:
  w=world_at(qc);before=w.snapshot()
  try:w.commit_path('carrot',dict(ok=True,path=path),checker=cc,start_q=qc,**extra);acc=True;err=None
  except (ValueError,TypeError) as e:acc=False;err=str(e)
  rec(label,acc,detail={'error':err,'transactional':before==w.snapshot()})
 # Nonholonomic rule must also hold at the commit boundary, not only planner.edge.
 park=np.array(scene.load('assets/park_mobile.json')['q']);park[-2:]=.015
 w=world_at(park);p2=park.copy();p2[1]+=.001
 pre=cc.check(park,mass=.12);post=cc.check(p2,mass=.12)
 try:w.commit_path('carrot',dict(ok=True,path=[park.tolist(),p2.tolist()]),checker=cc,start_q=park);acc=True;err=None
 except ValueError as e:acc=False;err=str(e)
 edge=planner.edge(cc,park,p2,time.monotonic()+10,mass=.12)
 rec('lateral_skid_commit',acc,detail={'error':err,'endpoint_checks':[pre['ok'],post['ok']],'planner_edge_reason':edge.get('reason'),'executed_counter':w.executed_connections})
 # A canonical stroke supplied as a held-carrot hold: verify endpoint coverage.
 tt=scene.targets(CFG,cc.meta)[0];RR=rot(tt,accepted[0]);w=world_at(qc)
 try:w.commit_path('carrot',dict(ok=True,path=[qc.tolist(),qc.tolist()]),checker=cc,start_q=qc,target=tt,rotation=RR);acc=True;err=None
 except ValueError as e:acc=False;err=str(e)
 rec('zero_progress_named_raw_pick',acc,detail={'error':err,'executed_counter':w.executed_connections,'start_target_error_m':float(np.linalg.norm(np.array(w.objects['carrot']['pos'])-tt['points'][0]))})
 save('negative_probes.json',dict(rows=rows,failures=[r for r in rows if not r['pass_']],scope='Synthetic only; no delivery state modified'))
 print('probes',len(rows),'failures',[r['name'] for r in rows if not r['pass_']],flush=True)
def statics():
 _,meta=make();ts=scene.targets(CFG,meta);out=[]
 for i,t in enumerate(ts):
  cc,_=make(t['held']);r=scene.load(f'results/strokes/{i}.json');ep=[]
  for k,e in enumerate(r['endpoints']):
   b=e['best']
   if 'q' not in b:ep.append(dict(endpoint=k,available=False,ok=False,submitted_ok=e['ok']));continue
   R=rot(t,b);cc.configure_target(t,R);q=np.array(b['q']);check=cc.check(q,kind=t['kind'],mass=execute.mass(t),force=t['force']);pe,re=cc.pose_error(q,t['points'][k],R);ok=bool(check['ok'] and pe<=.005 and re<=math.radians(3))
   ep.append(dict(endpoint=k,available=True,ok=ok,match=ok==e['ok'],submitted_ok=e['ok'],q=q,rotation=R,position_mm=pe*1000,orientation_deg=np.degrees(re),check=check))
  out.append(dict(index=i,name=t['name'],static_ok=all(e['ok'] for e in ep),endpoints=ep));print(i,t['name'],[e['ok'] for e in ep],flush=True)
 save('statics.json',dict(rows=out,static_templates_pass=sum(r['static_ok'] for r in out),total=11))
def paths():
 _,meta=make();ts=scene.targets(CFG,meta);out=[];allrows=[]
 def replay(ch,path,mass,kind='transfer',force=None,t=None,R=None):
  expanded=[np.array(path[0])];maxb=0.
  for a,b in zip(path[:-1],path[1:]):
   a,b=np.array(a),np.array(b);bound=ch.point_bound.bound(b-a);n=max(1,math.ceil(bound/.004));maxb=max(maxb,bound/n)
   expanded.extend(a+(b-a)*j/n for j in range(1,n+1))
  rows=[]
  for j,q in enumerate(expanded):
   r=ch.check(q,kind=kind,force=force,mass=mass);pe=re=0.;baseok=True
   if t:
    a,b=np.array(t['points']);v=b-a;p=ch.d.site_xpos[ch.m.site('R_prep').id];s=np.clip((p-a)@v/max(v@v,1e-12),0,1);pe,re=ch.pose_error(q,a+s*v,R);baseok=bool(np.max(abs(q[:3]-expanded[0][:3]))<1e-10)
   elif j and np.max(abs(q[:3]-expanded[j-1][:3]))>1e-10:
    prev=expanded[j-1];delta=q[:2]-prev[:2];yaw=(q[2]+prev[2])/2;baseok=planner.carry_clear(ch,q) and np.max(abs(q[3:]-prev[3:]))<1e-10 and abs(delta@[-np.sin(yaw),np.cos(yaw)])<=1e-6+1e-3*np.linalg.norm(delta)
   rows.append(dict(q=q,ok=bool(r['ok'] and pe<=.005 and re<=math.radians(3) and baseok),clearance=r['clearance'],tip=r['stability'],load=r['load'],hits=r['hits'],base_ok=baseok,position_mm=pe*1000,orientation_deg=np.degrees(re)))
  return dict(states=len(rows),all_pass=all(r['ok'] for r in rows),maximum_global_bound_m=maxb,rows=rows)
 for i,t in enumerate(ts):
  rec=scene.load(f'results/strokes/{i}.json');ip=rec['internal'];ch,_=make(t['held'])
  if ip['ok']:
   bank=scene.load(f'results/statics/{i}_0.json');q=np.array(ip['path'][0]);R=np.array(min(bank['candidates'],key=lambda c:np.linalg.norm(np.array(c['q'])-q))['rotation']);ch.configure_target(t,R)
   rr=replay(ch,ip['path'],execute.mass(t),t['kind'],t['force'],t,R);save(f'path_{i}.json',rr);out.append(dict(index=i,name=t['name'],**{k:v for k,v in rr.items() if k!='rows'}));allrows+=rr['rows']
  else:out.append(dict(index=i,name=t['name'],all_pass=False,reason=ip.get('reason')))
  print('local',i,out[-1].get('states',0),flush=True)
 connections=[]
 for i in range(10):
  rec=scene.load(f'results/connections/{i}.json');ch,_=make(ts[i]['held']);stages=[]
  for k in ('fold','base_move','unfold'):
   p=rec['planner'][k];q=p.get('rejection',{}).get('q');r=ch.check(np.array(q),mass=execute.mass(ts[i])) if q is not None else None
   sr=dict(stage=k,ok=p['ok'],budget_s=p.get('budget_s'),elapsed_s=p.get('elapsed_s'),restarts=p.get('restarts'),nodes=p.get('nodes'),reason=p.get('rejection',{}).get('reason',p.get('reason')),rejected_state_reproduced=None if r is None else not r['ok'])
   if p.get('path'):sr['replay']=replay(ch,p['path'],execute.mass(ts[i]))
   stages.append(sr)
  connections.append(dict(index=i,executed=rec['executed'],binding_ready=rec['binding_ready'],stages=stages));print('connection',i,flush=True)
 idle=scene.load('results/idle.json');ch,_=make();idle_rows=[]
 # Reconstruct exact direct attempts including saved time-limited prefixes.
 from execute import diagnostic_q
 first=diagnostic_q(scene.load('results/strokes/0.json')['endpoints'][0]);last=diagnostic_q(scene.load('results/strokes/10.json')['endpoints'][-1]);park=np.array(idle['park_q']);fg=park.copy();fg[:3]=last[:3];sc=park.copy();sc[:3]=first[:3]
 for name,a,b in [('fold',last,fg),('unfold',sc,first)]:
  saved=idle[name]['rejection'];n=max(1,math.ceil(ch.point_bound.segment_bound(a,b)/.004));count=saved.get('checked',0)
  path=[a+(b-a)*j/n for j in range(count)]
  if path:
   rr=replay(ch,path,0);save('idle_'+name+'_prefix.json',rr);idle_rows.append(dict(name=name,**{k:v for k,v in rr.items() if k!='rows'}))
 save('paths.json',dict(locals=out,connections=connections,idle_prefixes=idle_rows,idle_drive_attempts={k:idle[k] for k in ('drive_to_park','drive_from_park')},complete_carrot_witness_present=False,other_completed_products=[],executed_connections=0,scope='Available local paths and attempted prefixes only; no end-to-end route exists'))
 print('paths complete',flush=True)
def independent_tip(ch,q,forces,mass,all_direction=False):
 m,d=ch.m,ch.d;d.qpos[:]=q;mujoco.mj_forward(m,d);root=m.body('rail_structure').id;ids=[]
 for b in range(1,m.nbody):
  chain=b
  while chain and chain!=root:chain=m.body_parentid[chain]
  if chain==root:ids.append(b)
 weights=m.body_mass[ids];centres=d.xipos[ids].copy();moving=np.array([m.body(b).name.startswith('R_arm_') or m.body(b).name in ('R_tool','R_jaw_minus','R_jaw_plus') for b in ids]);sid=m.site('R_prep').id;R=d.site_xmat[sid].reshape(3,3);p=d.site_xpos[sid].copy()
 off=np.array([.08,0,0]) if ch.meta.get('held')=='holder' else np.zeros(3);cm=p+R@off;wp=p+R@(off if ch.meta.get('held')=='holder' else np.array([.0175,0,0]) if ch.meta.get('held')=='carrot' else np.zeros(3))
 yaw=q[2];rot2=np.array([[np.cos(yaw),-np.sin(yaw)],[np.sin(yaw),np.cos(yaw)]]);O=np.array([q[0],q[1],0]);avg=(weights@centres+mass*cm)/(sum(weights)+mass);rows=[]
 for factor in [1.,1.5]:
  ww=weights*np.where(moving,factor,1);G=np.array([0.,0.,-9.81*(sum(ww)+factor*mass)]);Mg=np.sum(np.cross(centres-O,ww[:,None]*[0,0,-9.81]),axis=0)+np.cross(cm-O,[0,0,-9.81*factor*mass])
  for f in forces:
   for sign in [-1,1]:
    F=np.array(f)*sign*factor;reaction=-(G+F)[2];M=Mg+np.cross(wp-O,F)
    directions=[rot2[:,0],-rot2[:,0],rot2[:,1],-rot2[:,1]] if all_direction else [[1,0],[-1,0],[0,1],[0,-1]]
    for dr in directions:
     inert=np.r_[np.array(dr)*(sum(weights)+mass)*.15*factor,0];MM=M+np.cross(avg-O,inert);zmp=rot2.T@np.array([MM[1],-MM[0]])/reaction
     margin=min(.215-abs(zmp[0]),.175-abs(zmp[1]))-20*.10*factor/reaction
     rows.append(dict(margin_m=float(margin),moment_Nm=float(margin*reaction),factor=factor,force_N=F.tolist(),inertia_direction=list(dr)))
 return min(rows,key=lambda r:r['margin_m'])
def engineering():
 # Every submitted admitted sample, independently recompute moments about cart
 # origin rather than summing world moments in mobile.stability.
 samples=[];cache={}
 for i in range(11):
  t=scene.load(f'results/strokes/{i}.json')['target']
  for r in scene.load(f'results/replay/{i}.json')['rows']:samples.append((f'stroke{i}/{r["label"]}',t['held'],execute.mass(t),r))
 for r in scene.load('results/replay/maps.json')['rows']:
  held='carrot' if r['label'].startswith('M11/') and not r['label'].endswith('mandoline_work') else 'holder' if r['label'].endswith('mandoline_work') else None
  samples.append((r['label'],held,.12 if held=='carrot' else .55 if held=='holder' else 0,r))
 tips=[]
 for label,held,mass,r in samples:
  if held not in cache:cache[held]=make(held)[0]
  ch=cache[held];forces=r['load']['force_cases_N'];q=np.array(r['q']);tip=independent_tip(ch,q,forces,mass);anytip=independent_tip(ch,q,forces,mass,True)
  tips.append(dict(label=label,q=q,independent=tip,any_horizontal_acceleration=anytip,submitted_m=r['tip']['min_margin_m'],delta_m=tip['margin_m']-r['tip']['min_margin_m']))
 ch,_=make();q=np.array(scene.load('assets/park_mobile.json')['q']);r=ch.check(q);tip=independent_tip(ch,q,[[0,0,0]],0);tips.append(dict(label='park',q=q,independent=tip,any_horizontal_acceleration=independent_tip(ch,q,[[0,0,0]],0,True),submitted_m=r['stability']['min_margin_m'],delta_m=tip['margin_m']-r['stability']['min_margin_m']))
 # Independently derive parked X separation; same interval contains every
 # modeled upper/lower cabinet/oven sweep, conditional on the end alcove.
 ext=[]
 for g,n in enumerate(ch.gnames):
  if not ch.robot[g]:continue
  lo=np.array([ch.bounds.support(g,-a)[k] for k,a in enumerate(np.eye(3))]);hi=np.array([ch.bounds.support(g,a)[k] for k,a in enumerate(np.eye(3))]);ext.append(dict(name=n,lo=lo,hi=hi,x_separation_m=float(lo[0]-1.8)))
 # Actual water ray vs target carrot OBB and compiled basket opening.
 _,meta=make();bid=ch.m.body('wash_basket').id;mouth=ch.d.xpos[bid]+ch.d.xmat[bid].reshape(3,3)@[0,0,.14];jet=np.array(meta['jet']);t=scene.targets(CFG,meta)[2];wet=[]
 for k,p in enumerate(t['points']):
  for jaw in [(0,0,1),(0,0,-1),(1,0,0),(-1,0,0)]:
   R=reference.rotation(t['approach'],jaw);origin=R.T@(jet-p);v=R.T@[0,0,-1];low=0.;high=1e6
   for axis,h in enumerate([.0175,.0175,.08]):
    if abs(v[axis])<1e-10:
     if abs(origin[axis])>h:high=-1;break
    else:
     aa,bb=sorted([(-h-origin[axis])/v[axis],(h-origin[axis])/v[axis]]);low=max(low,aa);high=min(high,bb)
   wet.append(dict(endpoint=k,jaw=jaw,intersects=bool(high>=low)))
 costs=list(csv.DictReader((IN/'results/costs.csv').open()));base=sum(float(r['total_cny']) for r in costs if not r['item'].startswith(('ONE15','TOTAL')))
 reserve={}
 for cat in ['robot_environment','held_gripper_environment','arm_arm_or_frame','self']:
  vals=[r['clearance'][cat]['reserve_mm'] for _,_,_,r in samples if cat in r['clearance']];reserve[cat]=dict(count=len(vals),min_mm=min(vals),p05_mm=float(np.percentile(vals,5)),fraction_ge10=float(np.mean(np.array(vals)>=10)),under2=sum(v<2 for v in vals))
 save('engineering.json',dict(stability=dict(samples=len(tips),minimum_mm=min(r['independent']['margin_m'] for r in tips)*1000,minimum_any_horizontal_acceleration_mm=min(r['any_horizontal_acceleration']['margin_m'] for r in tips)*1000,maximum_discrepancy_m=max(abs(r['delta_m']) for r in tips),worst=min(tips,key=lambda r:r['independent']['margin_m']),rows=tips),park=dict(check=r if False else ch.last,minimum_sweep_separation_mm=min(e['x_separation_m'] for e in ext)*1000,bounds=ext,site_conditional=True),wash=dict(mouth=mouth,jet=jet,axis_offset_mm=float(np.linalg.norm(mouth[:2]-jet[:2]))*1000,target_ray_tests=wet),clearance=reserve,cost=dict(subtotal=base,reserve=base*.15,total=base*1.15),prep_time_s=None,peel_allowance_s_per_root=6*2*.16/.0034/.20))
 print('engineering',len(tips),'minimum',min(r['independent']['margin_m'] for r in tips)*1000,flush=True)
def admissions():
 out=[];cache={};ts=scene.targets(CFG,scene.build(CFG)[1]);inputs=[]
 for i,t in enumerate(ts):
  for r in scene.load(f'results/replay/{i}.json')['rows']:inputs.append((f'{i}/{r["label"]}',t,r))
 for r in scene.load('results/replay/maps.json')['rows']:
  name=r['label'].split('/')[-1]
  if r['label'].startswith('M11/'):t=next(t for t in ts if t['name']==name)
  else:
   pr=next(p for p in scene.load('results/reachability.json')['extra_design_probes'] if p['mount_height_m']==.85 and p['target']==name)
   t=dict(name=name,held=None,kind='transfer',force=None,points=[pr['point_m']]*2,approach=[0,0,-1] if name=='sink_low' else [0,1,0])
  inputs.append((r['label'],t,r))
 for label,t,r in inputs:
  held=t['held']
  if held not in cache:cache[held]=make(held)[0]
  ch=cache[held];q=np.array(r['q']);ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d);actual=ch.d.site_xmat[ch.m.site('R_prep').id].reshape(3,3)
  app=t['approach'];jaws=[(0,0,1),(0,0,-1),(1,0,0),(-1,0,0)] if abs(app[1])>.9 else [(0,1,0),(0,-1,0),(1,0,0),(-1,0,0)];R=min([reference.rotation(app,j) for j in jaws],key=lambda z:np.linalg.norm(z-actual));ch.configure_target(t,R)
  cr=ch.check(q,kind=t['kind'],force=t['force'],mass=execute.mass(t));out.append(dict(label=label,q=q,ok=cr['ok'],clearance=cr['clearance'],load=cr['load'],tip=cr['stability'],hits=cr['hits']))
  if len(out)%50==0:print('admissions',len(out),flush=True)
 dist={}
 for cat in ['robot_environment','held_gripper_environment','arm_arm_or_frame','self']:
  vals=[r['clearance'][cat]['reserve_mm'] for r in out if cat in r['clearance']];dist[cat]=dict(count=len(vals),minimum_mm=min(vals),p05_mm=float(np.percentile(vals,5)),fraction_ge10=float(np.mean(np.array(vals)>=10)),under2=sum(v<2 for v in vals))
 save('admissions.json',dict(rows=out,all_pass=all(r['ok'] for r in out),clearance_distribution=dist));print('admissions done',len(out),sum(not r['ok'] for r in out),flush=True)
def supplemental():
 env=scene.load('assets/envelope_20.json');tr,_=scene.build(CFG);tool=tr.find(".//body[@name='R_tool']")
 for b in tr.iter('body'):
  if tool in list(b):b.remove(tool);break
 m=mujoco.MjModel.from_xml_string(E.tostring(tr.getroot(),encoding='unicode'));d=mujoco.MjData(m);sid=m.site('R_attachment_site').id;bid=m.site_bodyid[sid];rows=[]
 for w in env['witnesses']:
  d.qpos[:]=w['q'];mujoco.mj_forward(m,d);jp=np.zeros((3,m.nv));jr=jp.copy();mujoco.mj_jac(m,d,jp,jr,d.site_xpos[sid]+w['offset_world_m'],bid);j=m.joint(w['joint']).dofadr[0];tau=abs(d.qfrc_bias[j]+5*9.81*jp[2,j]);rows.append(dict(joint=w['joint'],independent_Nm=float(tau),submitted_Nm=w['torque_Nm'],difference_Nm=float(tau-w['torque_Nm'])))
 # Recompute admitted endpoint loads with finite-difference site Jacobians.
 torque=[]
 for sr in json.loads((HERE/'results/statics.json').read_text())['rows']:
  t=scene.load(f'results/strokes/{sr["index"]}.json')['target'];ch,_=make(t['held'])
  for ep in sr['endpoints']:
   if not ep['ok']:continue
   q=np.array(ep['q']);r=ep['check']['load'];mass=execute.mass(t);work=np.array(r['work_local_m']);com=np.array(r['held_com_local_m']);jacw=np.zeros((3,len(ch.arm_ids)));jacm=jacw.copy();sid=ch.m.site('R_prep').id
   for k,j in enumerate(ch.arm_ids):
    points=[]
    for sign in [-1,1]:
     qq=q.copy();qq[j]+=sign*1e-6;ch.d.qpos[:]=qq;mujoco.mj_forward(ch.m,ch.d);R=ch.d.site_xmat[sid].reshape(3,3);p=ch.d.site_xpos[sid];points.append((p+R@work,p+R@com))
    jacw[:,k]=(points[1][0]-points[0][0])/2e-6;jacm[:,k]=(points[1][1]-points[0][1])/2e-6
   ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d);rat=[]
   for f in r['force_cases_N']:
    tau=ch.d.qfrc_bias[ch.arm_ids]-jacw.T@f-jacm.T@[0,0,-mass*9.81];rat.append(max(abs(tau)/np.array(list(ch.env.values()))))
   torque.append(dict(stroke=sr['index'],endpoint=ep['endpoint'],finite_difference_max_ratio=max(rat),submitted_ratio=r['max_ratio'],difference=max(rat)-r['max_ratio']))
 save('supplemental.json',dict(envelope=rows,endpoint_torque=torque));print('supplemental complete',flush=True)
def attempts():
 out=[]
 for i in [2,5]:
  rec=scene.load(f'results/strokes/{i}.json');t=rec['target'];ch,_=make(t['held']);bank=scene.load(f'results/statics/{i}_0.json');candidate=bank['candidates'][-1] if i==5 else bank['candidates'][0];capture=[];original=execute.edge
  def logged(c,a,b,deadline,**kw):
   result=original(c,a,b,deadline,**kw);capture.append(dict(start=np.array(a).tolist(),end=np.array(b).tolist(),result=result));return result
  execute.edge=logged
  try:result=execute.continuation(ch,t,candidate['q'],np.array(candidate['rotation']),budget=65)
  finally:execute.edge=original
  out.append(dict(index=i,name=t['name'],result=result,segments=capture));print('continuation',i,result['ok'],result.get('reason'),flush=True)
 save('failed_continuations.json',dict(rows=out,scope='Independent fresh continuation from saved starts; no event commits'))
if __name__=='__main__':globals()[sys.argv[1]]()
