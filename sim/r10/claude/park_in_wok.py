"""Park in place (Mac, 2026-10-13; new file, edits nothing): the spatula never leaves the wok. It is released at
the R15 stroke-0 start state (results/r19/stir/stirwalk2_h_scrape_dice_r17.json, first 'work0' state, jaw sign -1)
and modelled as world geoms at exactly the held pose (the R_gripper_spatula* geoms of the stir model at that q).
 (a) open the jaws (.015 -> .025) at the stroke start, retreat 6 cm along the grasp approach axis (-R_prep x, the
     r17chain approach method: 1 cm IK steps, cart follows the x component), every segment through check_path.
 (b) empty move retreated state -> CUP (results/mac/hub_cup/hubs.json CUP, relabelled by 2pi per joint within the
     cup action's allowed shifts, nearest the retreat): straight, then the tuck at mid/either cart, then the r19hub
     joint-ordered vias (no planner: cart differs). Union scene of r19hub_cup + the spatula in the wok.
 (c) cup chain play states (results/mac/chain_cup_final.json) re-checked as r19cup_recheck.py + the spatula in the wok.
 (d) = reverse of (b) and (a): the same checked states in reverse order (the checker is state-wise), ending at the
     stroke-start q exactly.
python park_in_wok.py [PIECES=abc]  -> results/mac/park_in_wok_<piece>.json"""
import sys,os,json,math,time
sys.argv=[sys.argv[0],'none']+sys.argv[1:]
import numpy as np,mujoco,xml.etree.ElementTree as E
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
import r19hub_cup as H
import chain
from scene import build,save,fmt
from checker import Checker
import kitchen16 as K16,kitchen17 as K17
KV=H.KV;PIECES=KV.get('PIECES','abc');OUTD='results/mac';SUF='' if KV.get('KEY','work0')=='work0' else '_'+KV['KEY']
ST=json.load(open('results/r19/stir/stirwalk2_h_scrape_dice_r17.json'));SIGN=-1
Q0=np.array(ST['states']['q'][ST['states']['kinds'].index(KV.get('KEY','work0'))],float)
print('stroke start q',np.round(Q0,4).tolist(),flush=True)
# ---- the spatula at the held pose: geoms of the stir model at Q0 ----
def spatula_geoms():
 sv=dict(K16.TOOL_XY);K16.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);K16.TOOL_XY['spider']=(1.52,.36)
 SCN=dict(r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None,'spatula':None})
 cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,r15_spatula=.45,r15_spatula_jaw=SIGN,**SCN);tree,meta=build(cfg,None)
 m=mujoco.MjModel.from_xml_string(E.tostring(tree.getroot(),encoding='unicode'));d=mujoco.MjData(m);d.qpos[:]=Q0;mujoco.mj_kinematics(m,d)
 K16.TOOL_XY.clear();K16.TOOL_XY.update(sv)
 tn={mujoco.mjtGeom.mjGEOM_BOX:('box',3),mujoco.mjtGeom.mjGEOM_CYLINDER:('cylinder',2),mujoco.mjtGeom.mjGEOM_CAPSULE:('capsule',2),mujoco.mjtGeom.mjGEOM_SPHERE:('sphere',1),mujoco.mjtGeom.mjGEOM_ELLIPSOID:('ellipsoid',3)}
 out=[]
 for g in range(m.ngeom):
  n=m.geom(g).name
  if not n.startswith('R_gripper_spatula'):continue
  t,ns=tn[m.geom_type[g]];qq=np.zeros(4);mujoco.mju_mat2Quat(qq,d.geom_xmat[g])
  out.append(dict(name='park_'+n[2:],type=t,size=m.geom_size[g][:ns].tolist(),pos=d.geom_xpos[g].tolist(),quat=qq.tolist()))
 return out
SG=spatula_geoms();print('spatula geoms',len(SG),[g['name'] for g in SG],flush=True)
def add_spat(world):
 for g in SG:E.SubElement(world,'geom',name=g['name'],type=g['type'],size=fmt(g['size']),pos=fmt(g['pos']),quat=fmt(g['quat']),rgba='.8 .8 .82 1',contype='1',conaffinity='2',mass='.000001')
_ut=H.union_tree
def union_tree_park():
 tree,meta=_ut();add_spat(tree.find('worldbody'));return tree,meta
H.union_tree=union_tree_park
ch=H.union_checker()
m,d=ch.m,ch.d;sid=m.site('R_prep').id;ids=ch.arm_ids;lo=m.jnt_range[ids,0]+1e-9;hi=m.jnt_range[ids,1]-1e-9
def fk(q):d.qpos[:]=q;mujoco.mj_kinematics(m,d);return d.site_xpos[sid].copy(),d.site_xmat[sid].reshape(3,3).copy()
def solve_to(q,pt,Rt):
 q=np.array(q,float)
 def res(x):
  q[ids]=x;d.qpos[:]=q;mujoco.mj_kinematics(m,d)
  return np.r_[(d.site_xpos[sid]-pt)*10,Rotation.from_matrix(Rt@d.site_xmat[sid].reshape(3,3).T).as_rotvec()]
 x0=np.clip(q[ids],lo,hi);sol=least_squares(res,x0,bounds=(lo,hi),max_nfev=200,xtol=1e-10,ftol=1e-10);q[ids]=sol.x
 pe,re=ch.pose_error(q,pt,Rt);return q,pe,re,float(np.degrees(np.max(abs(sol.x-x0))))
def st(q):
 r=ch.check(np.asarray(q,float),full=True,mass=0.);e,s=H.reserve(r);return dict(ok=r['ok'],reserve_mm=None if e is None else round(e,1),self_mm=None if s is None else round(s,1),hits=[h['pair'] for h in r['hits']][:4])
res_all={}
T0=time.monotonic()
# ---------------- (a) ----------------
p0,R0=fk(Q0);qo=Q0.copy();qo[-2:]=H.JAW
A=dict(stroke_start_q=Q0.tolist(),state_closed=st(Q0),state_open=st(qo))
print('a closed',A['state_closed'],'open',A['state_open'],flush=True)
path=[Q0.copy(),qo.copy()];q=qo.copy();c0=q[0];steps=[]
for s in range(1,7):
 dp=-R0[:,0]*.06*s/6;q[0]=c0+dp[0];q,pe,re,dq=solve_to(q,p0+dp,R0);steps.append(dict(step=s,pose_mm=round(pe*1000,2),step_deg=round(dq,2)));path.append(q.copy())
 if pe>.005 or re>np.radians(3):break
QR=path[-1].copy();A['retreat_steps']=steps;A['retreated_q']=QR.tolist();A['approach_axis']=(-R0[:,0]).tolist()
# jaws: fingers only move (TCP fixed): check the two end states fully, plus the retreat segments through check_path
pj=H.check_path(ch,path[1:]) if all(x['pose_mm']<=5 for x in steps) else dict(ok=False,fail='IK pose error')
A['retreat_check']={k:v for k,v in pj.items() if k!='qs'}
if pj['ok']:
 mt=H.metrics(ch,pj['qs']);A['retreat_time_s']=mt['time_s'];A['min_reserve_mm']=min(x['min_reserve_mm'] for x in pj['segments'])
A['jaw_time_s']=.5;A['ok']=bool(A['state_open']['ok'] and pj['ok'])
A['note']='the closed state is the stir model state; here the spatula is a world object, so fingers on the handle at .015 are a contact by design (the grip); the open state (.025) and the retreat are the check'
save(f'{OUTD}/park_in_wok_a{SUF}.json',A);print('A',json.dumps({k:v for k,v in A.items() if k not in('retreat_steps','stroke_start_q','retreated_q')},default=str),flush=True)
res_all['a']=A
# ---------------- (b) ----------------
if 'b' in PIECES:
 Hh=H.J('results/mac/hub_cup/hubs.json');qc=np.array(Hh['endpoints']['CUP']['q_shifted'],float);AS=H.allowed_shifts('cup',ch)
 base=np.array(Hh['endpoints']['CUP']['q_raw'] if 'q_raw' in Hh['endpoints']['CUP'] else qc,float);ks={}
 for j in ch.arm_ids:ks[j]=min(AS[j],key=lambda k:abs(base[j]+H.TWO_PI*k-QR[j]))
 qc=base.copy()
 for j,k in ks.items():qc[j]+=H.TWO_PI*k
 T=np.array(Hh['tuck']['q'],float);B=dict(cup_q=qc.tolist(),cup_shift_2pi={str(j):k for j,k in ks.items() if k},cup_state=st(qc),tries=[])
 print('b cup state',B['cup_state'],'shift',B['cup_shift_2pi'],flush=True)
 vias=[('straight',[])]
 for lab,x in (('tuck at the mid cart',(QR[0]+qc[0])/2),('tuck at the retreat cart',QR[0]),('tuck at the CUP cart',qc[0]),('tuck at H_WOK .172',.172)):vias.append((lab,[np.r_[x,-.21,0.,T,H.JAW,H.JAW]]))
 for lr,rq in H.retreats(ch,QR):
  vias.append((lr,[rq]));vias.append((lr+' + tuck at the mid cart',[rq,np.r_[(QR[0]+qc[0])/2,-.21,0.,T,H.JAW,H.JAW]]))
 for S in H.VIA_SETS:
  for cf in (False,True):
   v=QR.copy();v[S]=qc[S]
   if cf:v[0]=qc[0]
   vias.append((f'joints {S} first'+(', cart first' if cf else ''),[v]))
 for lab,wp in vias:
  if time.monotonic()-T0>float(KV.get('BUDGET_S',600)):B['tries'].append(dict(method='budget',ok=False));break
  p=H.check_path(ch,[QR,*wp,qc]);B['tries'].append(dict(method=lab,ok=p['ok'],fail=p.get('fail')));print('b',lab,p['ok'],(p.get('fail') or {}).get('fail',{}).get('hits'),flush=True)
  if p['ok']:
   mt=H.metrics(ch,p['qs']);B.update(ok=True,method=lab,**mt,min_reserve_mm=min(s['min_reserve_mm'] for s in p['segments']),states_checked=sum(s['n'] for s in p['segments']),qs=[list(map(float,x)) for x in p['qs']]);break
 B.setdefault('ok',False);save(f'{OUTD}/park_in_wok_b{SUF}.json',B);print('B',json.dumps({k:v for k,v in B.items() if k not in('qs','tries')},default=str),flush=True);res_all['b']=B
# ---------------- (c) ----------------
if 'c' in PIECES:
 r=json.load(open('results/mac/chain_cup_final.json'));K16.set_design(**r['design'])
 for k_,v in r.get('tool_xy',{}).items():K16.TOOL_XY[k_]=tuple(v)
 cfg=chain.chain_cfg('SD',**{**dict(r19_station=True,r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools=dict(K17.R17_TOOLS_OFF)),**r['scene'],**K17.held_cfg(r['obj'],r['grasp_sense'])})
 tree,meta=build(cfg,None);add_spat(tree.find('worldbody'));cc=Checker(tree,meta);worst={};nh=0;hl=[]
 for i,q in enumerate(r['play']):
  c=cc.check(np.array(q),full=True,mass=0.)
  if c['hits']:nh+=1;hl.append(dict(step=i,hits=[h['pair'] for h in c['hits']][:3]))
  for cat,v in c['clearance'].items():
   if cat not in worst or v['reserve_mm']<worst[cat][0]:worst[cat]=(v['reserve_mm'],i)
 spat_min=None
 C=dict(ok=nh==0,steps=len(r['play']),steps_with_hits=nh,hits=hl[:20],min_reserve_by_cat={k:dict(mm=round(v[0],1),step=v[1]) for k,v in worst.items()},
  min_reserve_mm=round(min(v[0] for k,v in worst.items() if k!='self'),1),time_s=r.get('time_s') or r.get('total_s'),note='play states only (as r19cup_recheck.py), spatula geoms added at the stroke-start held pose')
 save(f'{OUTD}/park_in_wok_c{SUF}.json',C);print('C',json.dumps({k:v for k,v in C.items() if k!='hits'},default=str),hl[:5],flush=True);res_all['c']=C
print('elapsed',round(time.monotonic()-T0),flush=True)
