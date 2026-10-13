"""Park in wok: the whole sequence assembled and re-checked state by state (Mac, 2026-10-13; new file, edits nothing).
 a   stroke-<k> start (jaws closed) -> jaws open -> 6 cm retreat      (park_in_wok.py method, recomputed here)
 b   retreat -> CUP endpoint                                            (results/mac/park_in_wok_b2_<KEY><TAG>.json)
 cup reversed grasp approach (CUP -> grasp), held play, release retreat (results/mac/chain_cup_final.json, relabelled by
     the same 2pi multiples as the CUP state used by b; all its states stay in range)
 d   b reversed, then a reversed (back to the identical stroke-start q, jaws closed)
Every distinct state gets the full unchanged checker: empty-gripper states in the r19hub_cup union scene + the spatula in
the wok; the held play in the cup chain's scene + the spatula (as park_in_wok.py piece c). d is a's and b's states in
reverse order (the check is state-wise), so it is not checked a second time.
python park_in_wok_seq.py [KEY=work1] [TAG=_r1]  -> results/mac/park_in_wok_seq_<KEY>.json"""
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
KV=H.KV;KEY=KV.get('KEY','work1');TAG=KV.get('TAG','_r1');OUTD='results/mac'
ST=json.load(open('results/r19/stir/stirwalk2_h_scrape_dice_r17.json'));SIGN=-1
Q0=np.array(ST['states']['q'][ST['states']['kinds'].index(KEY)],float)
A=json.load(open(f'{OUTD}/park_in_wok_a_{KEY}.json'));B=json.load(open(f'{OUTD}/park_in_wok_b2_{KEY}{TAG}.json'));assert B['ok']
def spatula_geoms():   # as park_in_wok.py
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
SG=spatula_geoms()
def add_spat(world):
 for g in SG:E.SubElement(world,'geom',name=g['name'],type=g['type'],size=fmt(g['size']),pos=fmt(g['pos']),quat=fmt(g['quat']),rgba='.8 .8 .82 1',contype='1',conaffinity='2',mass='.000001')
_ut=H.union_tree
def union_tree_park():
 tree,meta=_ut();add_spat(tree.find('worldbody'));return tree,meta
H.union_tree=union_tree_park
ch=H.union_checker();m,d=ch.m,ch.d;sid=m.site('R_prep').id;ids=ch.arm_ids;lo=m.jnt_range[ids,0]+1e-9;hi=m.jnt_range[ids,1]-1e-9
T0=time.monotonic()
def fk(q):d.qpos[:]=q;mujoco.mj_kinematics(m,d);return d.site_xpos[sid].copy(),d.site_xmat[sid].reshape(3,3).copy()
def solve_to(q,pt,Rt):   # as park_in_wok.py
 q=np.array(q,float)
 def res(x):
  q[ids]=x;d.qpos[:]=q;mujoco.mj_kinematics(m,d)
  return np.r_[(d.site_xpos[sid]-pt)*10,Rotation.from_matrix(Rt@d.site_xmat[sid].reshape(3,3).T).as_rotvec()]
 x0=np.clip(q[ids],lo,hi);sol=least_squares(res,x0,bounds=(lo,hi),max_nfev=200,xtol=1e-10,ftol=1e-10);q[ids]=sol.x
 pe,re=ch.pose_error(q,pt,Rt);return q,pe,re
def recheck(c,qs,lab):
 worst={};nh=0;hl=[]
 for i,q in enumerate(qs):
  r=c.check(np.asarray(q,float),full=True,mass=0.)
  if not r['ok']:nh+=1;hl.append(dict(i=i,hits=[h['pair'] for h in r['hits']][:3],ranges=r['ranges'],mobile=r['mobile']['ok'],stab=r['stability']['ok']))
  for cat,v in r['clearance'].items():
   if cat not in worst or v['reserve_mm']<worst[cat][0]:worst[cat]=(v['reserve_mm'],i)
 out=dict(label=lab,states=len(qs),states_failed=nh,fails=hl[:10],min_reserve_by_cat={k:dict(mm=round(v[0],1),i=v[1]) for k,v in worst.items()},
  min_env_mm=round(min([v[0] for k,v in worst.items() if k!='self'] or [1e9]),1),min_self_mm=round(worst['self'][0],1) if 'self' in worst else None)
 print('recheck',lab,{k:v for k,v in out.items() if k!='min_reserve_by_cat'},round(time.monotonic()-T0),flush=True);return out
# ---- a (recomputed exactly as park_in_wok.py) ----
p0,R0=fk(Q0);qo=Q0.copy();qo[-2:]=H.JAW;pa=[Q0.copy(),qo.copy()];q=qo.copy();c0=q[0]
for s in range(1,7):
 dp=-R0[:,0]*.06*s/6;q[0]=c0+dp[0];q,pe,re=solve_to(q,p0+dp,R0);pa.append(q.copy())
assert np.max(abs(pa[-1]-np.array(A['retreated_q'])))<1e-6,('retreat differs',np.max(abs(pa[-1]-np.array(A['retreated_q']))))
pc=H.check_path(ch,pa[1:]);assert pc['ok'],pc.get('fail')
QA=[Q0]+[np.asarray(x) for x in pc['qs']]   # closed -> open (jaws only) -> the <=4 mm retreat states
QB=[np.asarray(x,float) for x in B['qs']];assert np.max(abs(QB[0]-QA[-1]))<1e-9
# ---- cup action, relabelled to the CUP state used by b ----
U,apps,_=H.unwrapped('results/mac/chain_cup_final.json');qc=np.array(B['cup_q'],float)
ks=np.round((qc-apps[0][-1])/H.TWO_PI);assert np.allclose(qc,apps[0][-1]+ks*H.TWO_PI,atol=1e-9) and np.all(ks[:3]==0) and np.all(ks[9:]==0)
sh=lambda X:[np.asarray(x,float)+ks*H.TWO_PI for x in X]
CAPP=sh(apps[0][::-1]);CPLAY=sh(U);CREL=sh(apps[1])
for X in (CAPP,CPLAY,CREL):
 Xa=np.array(X)
 assert np.all(Xa[:,ids]>=m.jnt_range[ids,0]-1e-9) and np.all(Xa[:,ids]<=m.jnt_range[ids,1]+1e-9)
assert np.allclose(CREL[-1],qc) and np.allclose(CAPP[0],qc)
# held scene: the cup chain's scene + spatula (as park_in_wok.py piece c)
r=json.load(open('results/mac/chain_cup_final.json'));K16.set_design(**r['design'])
for k_,v in r.get('tool_xy',{}).items():K16.TOOL_XY[k_]=tuple(v)
cfg=chain.chain_cfg('SD',**{**dict(r19_station=True,r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools=dict(K17.R17_TOOLS_OFF)),**r['scene'],**K17.held_cfg(r['obj'],r['grasp_sense'])})
tree,meta=build(cfg,None);add_spat(tree.find('worldbody'));cc=Checker(tree,meta)
RC=dict(a=recheck(ch,QA,'a: stroke start, jaws open, retreat (union+spatula)'),b=recheck(ch,QB,'b: retreat -> CUP (union+spatula)'),
 cup_approach=recheck(ch,CAPP,'cup grasp approach, empty, cup on the pad (union+spatula)'),
 cup_play=recheck(cc,CPLAY,'cup held play (cup scene+spatula)'),cup_release=recheck(ch,CREL,'cup release retreat (union+spatula)'))
ok=all(v['states_failed']==0 for v in RC.values())
seg=[dict(label='a: release the spatula, retreat 6 cm',scene='empty',qs=QA),dict(label='b: tuck, cart, unfold to the cup port',scene='empty',qs=QB[1:]),
 dict(label='cup: approach the cup',scene='empty',qs=CAPP[1:]),dict(label='cup: carry, pour, return',scene='held',qs=CPLAY),dict(label='cup: release',scene='empty',qs=CREL),
 dict(label='d: back to the wok',scene='empty',qs=QB[::-1][1:]),dict(label='d: re-grasp the spatula',scene='empty',qs=QA[::-1][1:])]
for s in seg:s['qs']=[list(map(float,x)) for x in s['qs']]
ta=A['jaw_time_s']+A['retreat_time_s'];tb=B['time_b_s'];tc=r['time_s']
OUT=dict(key=KEY,ok=ok,stroke_start_q=Q0.tolist(),cup_relabel_2pi={str(j):int(k) for j,k in enumerate(ks) if k},rechecks=RC,
 times=dict(a_s=ta,b_s=tb,cup_chain_s=tc,d_s=round(ta+tb,2),total_s=round(2*(ta+tb)+tc,2),baseline_s=75.4,saving_s=round(75.4-(2*(ta+tb)+tc),2)),
 end_equals_start=bool(np.max(abs(np.array(seg[-1]['qs'][-1])-Q0))<1e-12),spatula_geoms=SG,segments=seg,
 notes=['d = the a and b states in reverse order; the checker is state-wise, so they are not checked twice',
  'the cup grasp approach states are the r17chain 1 cm IK steps (r17chain spacing), re-checked here state-wise with the spatula',
  'cup chain time 20.6 s includes its approach/retreat, grasp/release and the 2 s dwell (r17chain timing model)'])
save(f'{OUTD}/park_in_wok_seq_{KEY}.json',OUT);print('SEQ',ok,OUT['times'],'end==start',OUT['end_equals_start'],round(time.monotonic()-T0),flush=True)
