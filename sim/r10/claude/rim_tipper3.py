"""rim_tipper3.py (Mac 2026-10-13, new file): rim_tipper2.py with (a) the servo box hung UNDER the seat (so neither the
held cup nor the fingers meet it, whatever the approach) and the post under it to the cooker top, and (b) the load test
searching the approach yaw: the cup (symmetric) is turned ALPHA deg about its axis in the holder, so the cup chain's
grasp (TCP at the cup centre, jaws across, sense 1, approach = Rz(ALPHA) (0,1,0)) comes from another side. The screens
(ii) stir, (iii) cup / bowl pour paths and the static fit do not depend on ALPHA (the holder is the same).
Holder (box bracket): seat plate 72 x 72 x 12 mm under the cup; servo box 60 (radial) x 40 x 60 mm under the seat;
20 x 20 mm post under the servo to z .921. Tipped: the cup turned TIPDEG about the rim tangent through its inner bottom edge.
python rim_tipper3.py [AZ=..] [DZ=.03] [GAP=.015,.035] [ALPHAS=-90,..,90] [LOADN=..] [TAG=..] -> results/mac/rim_tipper3_<TAG>.json"""
import sys,os,json,math,time
import numpy as np,mujoco,xml.etree.ElementTree as E
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
import cupobj,bowlobj   # noqa: F401
import chain
from scene import build,save,fmt
from checker import Checker
import kitchen14 as K14,kitchen15 as K15,kitchen16 as K,kitchen17 as K17
KV=dict(a.split('=',1) for a in sys.argv[1:]);T0=time.monotonic()
AZS=[float(a) for a in KV.get('AZ',','.join(str(a) for a in range(0,360,15))).split(',')];DZS=[float(z) for z in KV.get('DZ','.03').split(',')]
GAPS=[float(g) for g in KV.get('GAP','.015,.035').split(',')];ALPHAS=[float(a) for a in KV.get('ALPHAS','-90,-60,-45,-30,-15,0,15,30,45,60,90').split(',')]
CR,CH=K14.CUP_R,K14.CUP_H;TIPDEG=float(KV.get('TIPDEG',120));W0=K15.WOK0;RIMZ=K15.RIM_Z
def rz(a):c,s=math.cos(a),math.sin(a);return np.array([[c,-s,0],[s,c,0],[0,0,1.]])
def q4(R):return Rotation.from_matrix(R).as_quat()[[3,0,1,2]]
CANDS=[]
import itertools
for dz,GAP,az in itertools.product(DZS,GAPS,AZS):
  RC=K15.A_RIM+GAP+CR
  a=math.radians(az);u=np.array([math.cos(a),math.sin(a),0.]);t=np.array([-math.sin(a),math.cos(a),0.]);c=np.r_[W0[:2],0]+RC*u;zb=RIMZ+dz
  Rz=rz(a);piv=c-CR*u+[0,0,zb]
  Rt=Rotation.from_rotvec(t*math.radians(TIPDEG)).as_matrix()
  if (Rt@[0,0,1.])@u>0:Rt=Rotation.from_rotvec(-t*math.radians(TIPDEG)).as_matrix()   # mouth inward
  cupc=c+[0,0,zb+CH/2];tc=piv+Rt@(cupc-piv)
  zs=zb-.012-.06;ph=(zs-.921)/2   # servo under the seat (60 mm tall); the post stops 1 mm above the cooker top (mounting not modelled)
  parts=[('cup','cylinder',cupc,[CR,CH/2],np.eye(3)),('seat','box',c+[0,0,zb-.006],[CR+.006,CR+.006,.006],Rz),
   ('servo','box',c+[0,0,zs+.03],[.03,.02,.03],Rz),('post','box',c+[0,0,.921+ph],[.01,.01,ph],Rz),('cupT','cylinder',tc,[CR,CH/2],Rt)]
  CANDS.append(dict(i=len(CANDS),az=az,dz=dz,gap=GAP,cup_bottom=(c+[0,0,zb]).tolist(),parts=parts))
def add_cands(world,which=None,skip=()):
 for C in CANDS:
  if which is not None and C['i'] not in which:continue
  for n,ty,p,s,R in C['parts']:
   if n in skip:continue
   E.SubElement(world,'geom',name=f"tip{C['i']}_{n}",type=ty,pos=fmt(p),size=fmt(s),quat=fmt(q4(R)),rgba='.3 .6 .3 1',contype='1',conaffinity='2',mass='.000001')
def cand_ids(m):
 out={}
 for g in range(m.ngeom):
  n=m.geom(g).name
  if n.startswith('tip') and '_' in n:i,part=n[3:].split('_',1);out[g]=(int(i),part)
 return out
RES={C['i']:dict(az=C['az'],dz=C['dz'],gap=C['gap'],cup_bottom=[round(x,3) for x in C['cup_bottom']],scenes={}) for C in CANDS}
def screen(label,tree,meta,Q,parts_up=('cup','seat','servo','post'),margin=.05):
 ch=Checker(tree,meta);m,d=ch.m,ch.d;ci=cand_ids(m)
 for g in ci:m.geom_margin[g]=margin
 best={}   # (i, 'up'|'tip') -> (slack, state, pair)
 for k,q in enumerate(Q):
  d.qpos[:]=q;mujoco.mj_kinematics(m,d);mujoco.mj_comPos(m,d);mujoco.mj_collision(m,d)
  for c in d.contact[:d.ncon]:
   x,y=int(c.geom[0]),int(c.geom[1])
   if (x in ci)==(y in ci):continue
   cg,og=(x,y) if x in ci else (y,x)
   if not ch.robot[og]:continue
   req=ch.required(ch,cg,og)
   if req is None:continue
   i,part=ci[cg];key=(i,'up' if part in parts_up else 'tip');s=float(c.dist)-req[0]
   if key not in best or s<best[key][0]:best[key]=(s,k,[ch.gnames[og],part],req[1])
 for C in CANDS:
  for pose in ('up','tip'):
   b=best.get((C['i'],pose));RES[C['i']]['scenes'].setdefault(label,{})[pose]=dict(ok=True,min_slack_mm='>%d'%(margin*1000-10)) if b is None else dict(ok=b[0]>=0,min_slack_mm=round(b[0]*1000,1),state=b[1],pair=b[2],rule=b[3])
 print('screen',label,len(Q),'states', sum(RES[i]['scenes'][label]['up']['ok'] for i in RES),'up ok,',sum(RES[i]['scenes'][label]['tip']['ok'] for i in RES),'tipped ok',round(time.monotonic()-T0),flush=True)
 return ch
def chain_tree(r,held=True,extra=None):
 K.set_design(**r['design'])
 for k_,v in r.get('tool_xy',{}).items():K.TOOL_XY[k_]=tuple(v)
 if r.get('wok_tilt'):K17.set_wok_tilt(r['wok_tilt'])
 cfg=chain.chain_cfg('SD',**{**dict(r19_station=True,r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools=dict(K17.R17_TOOLS_OFF)),**r['scene'],**(K17.held_cfg(r['obj'],r['grasp_sense']) if held else {}),**(extra or {})})
 return build(cfg,None)
# ---- (ii) stir cycle (scene as r19stir_save.py SCENE=r17 + the R15 spatula held) ----
ST=json.load(open('results/r19/stir/stirwalk2_h_scrape_dice_r17.json'));QS=np.array(ST['states']['q'],float)
sv=dict(K.TOOL_XY);K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);K.TOOL_XY['spider']=(1.52,.36)
cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,r15_spatula=.45,r15_spatula_jaw=-1,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None,'spatula':None})
tree,meta=build(cfg,None);add_cands(tree.find('worldbody'));chs=screen('stir',tree,meta,QS)
# fit against the static kitchen (stir scene: drum cradle, wok, hood, camera ...)
m,d=chs.m,chs.d;ci=cand_ids(m);d.qpos[:]=QS[0];mujoco.mj_forward(m,d);ft=np.zeros(6)
world=[g for g in range(m.ngeom) if not chs.robot[g] and g not in ci and m.geom_bodyid[g]==0]
for C in CANDS:
 fit={}
 for g,(i,part) in ci.items():
  if i!=C['i']:continue
  best=(1e9,None)
  for w in world:
   n=m.geom(w).name
   if part in ('post','seat','servo') and any(s in n for s in ('cooker','counter')):continue
   dd=mujoco.mj_geomDistance(m,d,g,w,.05,ft)
   if dd<best[0]:best=(dd,n)
  fit[part]=dict(min_mm=round(best[0]*1000,1),nearest=best[1])
 RES[C['i']]['fit']=fit;RES[C['i']]['fit_ok']=all(v['min_mm']>0 for v in fit.values())
print('fit ok',sum(RES[i]['fit_ok'] for i in RES),round(time.monotonic()-T0),flush=True)
K.TOOL_XY.clear();K.TOOL_XY.update(sv)
# ---- (iii) cup and bowl pour paths, and the wok paths (extra) ----
for lab,f in (('cup_pour','results/mac/chain_cup_final.json'),('bowl_pour','results/mac/chain_bowl_final.json'),('wok_spot1','results/r17/chain_wok_s-1_final.json'),('wok_spot2','results/r17/chain_wok_s-1_r18plate2b.json')):
 r=json.load(open(f));tree,meta=chain_tree(r);add_cands(tree.find('worldbody'));screen(lab,tree,meta,np.array(r['play'],float))
 if r.get('wok_tilt'):K17.set_wok_tilt(0.)
for i,R in RES.items():
 sc=R['scenes'];R['stir_up_ok']=sc['stir']['up']['ok'];R['stir_tip_ok']=sc['stir']['tip']['ok'];R['pour_paths_ok']=sc['cup_pour']['up']['ok'] and sc['bowl_pour']['up']['ok']
 R['wok_paths_ok']=sc['wok_spot1']['up']['ok'] and sc['wok_spot2']['up']['ok']
# ---- (i) loading with the cup chain's grasp ----
rc=json.load(open('results/mac/chain_cup_final.json'));CP=np.array(rc['play'],float)
sel=[i for i,R in RES.items() if R['stir_up_ok'] and R['pour_paths_ok'] and R['fit_ok']]
sel=sorted(sel,key=lambda i:(not RES[i]['stir_tip_ok'],-(RES[i]['scenes']['stir']['up']['min_slack_mm'] if isinstance(RES[i]['scenes']['stir']['up']['min_slack_mm'],float) else 99)))[:int(KV.get('LOADN',8))]
print('load test for',[(RES[i]['az'],RES[i]['gap']) for i in sel],flush=True)
for i,ALPHA in itertools.product(sel,ALPHAS):
 C=CANDS[i];pb=np.array(C['cup_bottom']);L=dict();Ry=rz(math.radians(ALPHA))
 if 'loads' not in RES[i]:RES[i]['loads']={}
 tree,meta=chain_tree(rc,True);add_cands(tree.find('worldbody'),{i},skip=('cup','cupT'));ch=Checker(tree,meta)
 m,d=ch.m,ch.d;sid=m.site('R_prep').id;ids=[0]+list(ch.arm_ids);lo=m.jnt_range[ids,0]+1e-6;hi=m.jnt_range[ids,1]-1e-6
 pt,Rt=K.tcp_pose('cup',Ry,pb+[0,0,.008],rc['grasp_sense'])
 def ik(q0,pt,Rt,c=ch):
  q=np.array(q0,float);mm,dd=c.m,c.d;s_=mm.site('R_prep').id
  def res(x):
   q[ids]=x;dd.qpos[:]=q;mujoco.mj_kinematics(mm,dd)
   return np.r_[(dd.site_xpos[s_]-pt)*10,Rotation.from_matrix(Rt@dd.site_xmat[s_].reshape(3,3).T).as_rotvec()]
  sol=least_squares(res,np.clip(q[ids],lo,hi),bounds=(lo,hi),max_nfev=300,xtol=1e-10,ftol=1e-10);q[ids]=sol.x;pe,re=c.pose_error(q,pt,Rt);return q,pe,re
 sols=[]
 for q0 in CP[::int(KV.get('SEEDSTEP',8))]:
  q,pe,re=ik(q0,pt,Rt)
  if pe<.001 and re<np.radians(.5) and not any(np.max(abs(q-s))<1e-3 for s in sols):sols.append(q)
 tried=[]
 for q in sols:
  r1=ch.check(q,full=True,mass=0.)
  tried.append(dict(q=[round(x,4) for x in q.tolist()],held_ok=r1['ok'],hits=[h['pair'] for h in r1['hits']][:2]))
  if not r1['ok']:continue
  # release: empty gripper, jaws open, the cup seated in this holder; retreat 6 cm along -approach (-y)
  te,me=chain_tree(rc,False,dict(r19_cup=None));add_cands(te.find('worldbody'),{i},skip=('cupT',));ce=Checker(te,me)
  p0,R0=K.tcp_pose('cup',Ry,pb,rc['grasp_sense']);qq=q.copy();qq[-2:]=.025;qq,pe,re=ik(qq,p0,R0,ce);path=[qq.copy()]
  for s in range(1,7):
   qq,pe2,re2=ik(qq,p0-R0[:,0]*.01*s,R0,ce);path.append(qq.copy())
  rr=[ce.check(x,full=True,mass=0.) for x in path];okr=all(x['ok'] for x in rr) and pe<.001
  env=[min([v['reserve_mm'] for k,v in x['clearance'].items() if k!='self'] or [1e9]) for x in rr]
  tried[-1].update(release_ok=okr,release_hits=[[h['pair'] for h in x['hits']][:2] for x in rr if not x['ok']][:2],release_min_env_mm=round(min(env),1),
   held_min_env_mm=round(min([v['reserve_mm'] for k,v in r1['clearance'].items() if k!='self'] or [1e9]),1),cart=round(float(q[0]),3))
  if okr:L=dict(ok=True,**tried[-1]);break
 RES[i]['loads'][str(ALPHA)]=L or dict(ok=False,ik_solutions=len(sols),tried=tried[:4])
 print('load',C['az'],C['gap'],ALPHA,RES[i]['loads'][str(ALPHA)].get('ok'),'ik',len(sols),RES[i]['loads'][str(ALPHA)].get('cart'),[t['hits'][:1] for t in tried[:2]],round(time.monotonic()-T0),flush=True)
ok=[dict(az=R['az'],dz=R['dz'],gap=R['gap'],alpha=float(a),stir_up_slack=R['scenes']['stir']['up']['min_slack_mm'],stir_tip_ok=R['stir_tip_ok'],stir_tip_slack=R['scenes']['stir']['tip']['min_slack_mm'],
 cup_pour=R['scenes']['cup_pour']['up']['min_slack_mm'],bowl_pour=R['scenes']['bowl_pour']['up']['min_slack_mm'],held_min_env_mm=v.get('held_min_env_mm'),release_min_env_mm=v.get('release_min_env_mm'),cart=v.get('cart'),q=v.get('q'))
 for R in RES.values() for a,v in R.get('loads',{}).items() if v.get('ok')]
save('results/mac/rim_tipper3_'+KV.get('TAG','screen')+'.json',dict(geometry=dict(gaps_m=GAPS,alphas=ALPHAS,rim_z=RIMZ,tip_deg=TIPDEG,parts='cup 60x70, seat plate 72x72x12, servo box 60x40x60 under the seat, post 20x20 under it to z .921'),
 passing=ok,candidates={str(k):v for k,v in RES.items()},elapsed_s=round(time.monotonic()-T0)))
print('PASSING',ok,round(time.monotonic()-T0),flush=True)
