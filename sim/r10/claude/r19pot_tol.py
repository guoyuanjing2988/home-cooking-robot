"""R19 pot zone (GitHub #37, #8): the #13 tolerance study (r19tol_replay.py, unchanged) on the pot-zone paths. New file.

r19tol_replay.py / r19tol_core.py are imported and run as they are; this wrapper only
 - installs the kitchen19pot layer in every process (RACK=keyed; SPX / SPY = the spider rest of the layout under test,
   used for every scene; a chain's own tool_xy otherwise);
 - registers the new paths as actions of r19tol_core.CHAINS: SPIDER=<chain json> -> 'spider19', LID=<chain json>
   -> 'lid19' (default the adopted lid chain), with r17chain's approach worlds;
 - adds the keyed rack's geoms to the 'lid_rack' fixture group;
 - for the lid play with RACK=keyed applies the declared insertion window (kitchen19pot.window(); with POTWIN=1 also
   the optional lift-off window at the pot, kitchen19pot.window_pot()): in a state whose
   NOMINAL TCP is on the window segment, the pairs held-lid-part x keyed-rack-part are the intended contact and are
   not evaluated (their distance bound is set to 1 m, for gate and contact alike); every other pair, in every state,
   is evaluated as in #13. The lead-in's capture margin is reported by r19pot_tol.py capture (below).
 - writes to results/r19/pot/tol/<TOLTAG>/.
python r19pot_tol.py SCENES=play:spider19,app:spider19:0 PARTS=grid-tilt_x+y,cart-tilt_x,scen-dock_stops SPIDER=<json>
       [LID=<json>] [RACK=keyed] [POTWIN=1] [SPX= SPY=] TOLTAG=<name> ARM=ur5e_enc2_pgc PY=.15 [WORKERS=..] [DEADLINE=..]
python r19pot_tol.py capture [RACK=keyed] ... : the worst displacement of the lid rim at the window entry under each
       cart budget box (all 2^6 corners, R19_TOLERANCE section 1) plus the arm accuracy, vs the rack's capture range."""
import sys,os,json,math
sys.path.insert(0,'.')
import numpy as np
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
import kitchen19pot as P
if KV.get('RACK')=='keyed':P.install(rack='keyed')
import r19tol_core as C
C.OUT='results/r19/pot/tol/'+KV.get('TOLTAG','run')
if 'SPIDER' in KV:C.CHAINS['spider19']=dict(file=KV['SPIDER'],label='spider19',worlds={0:{},18:{}})
C.CHAINS['lid19']=dict(file=KV.get('LID','results/r17/chain_lid_s-1_final_ur5e_enc2_pgc.json'),label='lid19',worlds={0:{'r16_lid':'on'},8:{'r16_lid':'rack'}})
_gl=C.GROUPS['lid_rack'];C.GROUPS['lid_rack']=lambda n,p:_gl(n,p) or n.startswith('r19pot_rack_')
_kit=C._kitchen
def _kitchen(r):
 _kit(r)
 if 'SPX' in KV:
  import kitchen16 as K;K.TOOL_XY['spider']=(float(KV['SPX']),float(KV['SPY']))
C._kitchen=_kitchen
_bs=C.build_scene
def build_scene(key):
 ch,Q,info=_bs(key)
 if info.get('kind')=='play' and info.get('obj')=='lid':
  r=C.J(info['file']);ch._r19pot_wins=P.windows(r['grasp_sense'],rack=KV.get('RACK')=='keyed',pot=KV.get('POTWIN')=='1')
 return ch,Q,info
C.build_scene=build_scene
class EvW(C.Ev):
 """r19tol_core.Ev with the declared lid window: window pairs excluded in nominal-window states."""
 def __init__(s,ch):
  super().__init__(ch);s.Ws=getattr(ch,'_r19pot_wins',None) or [];s._act=None;nm=ch.gnames;G=ch.m.ngeom;s.WP=[]
  for W in s.Ws:
   M=np.zeros((G,G),bool);pi=[i for i,n in enumerate(nm) if n in set(W['parts'])]
   fi=[i for i,n in enumerate(nm) if n in set(W['faces']) or (W.get('face_prefix') and n.startswith(W['face_prefix']))]
   for a in pi:
    for b in fi:M[a,b]=M[b,a]=True
   s.WP.append(M)
 def pose(s,q,cart=None,grasp=None):
  super().pose(q,cart,grasp);s._act=None
  if s.Ws:
   act=[M for W,M in zip(s.Ws,s.WP) if P.in_window(W,s.d.site_xpos[s.sid],s.d.site_xmat[s.sid].reshape(3,3))]
   if act:s._act=np.logical_or.reduce(act)
 def bound(s,pa,pb,shift=None):
  r=super().bound(pa,pb,shift)
  if s._act is not None and len(pa):r=np.where(s._act[pa,pb],1.,r)
  return r
C.Ev=EvW
def capture():
 """Lead-in check of the keyed rack: at every lid-play state in the window, the displacement of the lowest rim point
 (the first point to meet the grooves) under the worst corner of each cart budget box, plus the arm accuracy
 (+-2 mm, R19_TOLERANCE section 1) and the rack placement tolerance PLACE (default 1 mm), against the capture range."""
 import itertools,mujoco
 sys.argv=[sys.argv[0]]+[a for a in sys.argv[1:] if a.startswith(('ARM=','PY='))]
 import r19tol_replay as R
 ch,Q0,info=build_scene('play:lid19');Q,src=C.densify(ch,Q0);m,d=ch.m,ch.d;W=P.window(C.J(info['file'])['grasp_sense']);sid=m.site('R_prep').id
 g=m.geom('R_gripper_r16_lid_rim').id;cap=P.capture();arm=.002;place=float(KV.get('PLACE',.001));out={}
 for name,half in R.SCENARIOS.items():
  worst=dict(x=0.,y=0.,z=0.);n=0
  corners=[np.array(sg)*np.array(half) for sg in itertools.product((1,-1),repeat=6)]
  for q in Q:
   d.qpos[:]=q;mujoco.mj_kinematics(m,d)
   if not P.in_window(W,d.site_xpos[sid],d.site_xmat[sid].reshape(3,3)):continue
   n+=1;R_=d.geom_xmat[g].reshape(3,3);c0=d.geom_xpos[g]+R_@np.array([0,0,0])
   low=c0-np.array([0,0,P.K.LID_R])   # lowest rim point (rim plane vertical): centre - R z
   pc=d.xpos[m.body('rail_structure').id].copy();pc[2]=0.;pm=d.xpos[m.body('R_mount').id].copy()
   for c in corners:
    x,y,z,yaw,tx,ty=c;p=low.copy();Rt=C.Rx(tx)@C.Ry(ty);p=Rt@(p-pc)+pc;pm2=Rt@(pm-pc)+pc;p=C.Rz(yaw)@(p-pm2)+pm2+np.array([x,y,z]);dv=p-low
    for k,ax in enumerate('xyz'):worst[ax]=max(worst[ax],abs(dv[k]))
  out[name]=dict(window_states=n,cart_disp_mm={k:round(v*1e3,3) for k,v in worst.items()},
   x_total_mm=round((worst['x']+arm+place)*1e3,2),y_total_mm=round((worst['y']+arm+place)*1e3,2),
   x_capture_mm=round(cap['x_capture_m']*1e3,2),y_capture_mm=round(cap['y_capture_m']*1e3,1),
   x_margin_mm=round((cap['x_capture_m']-worst['x']-arm-place)*1e3,2),y_margin_mm=round((cap['y_capture_m']-worst['y']-arm-place)*1e3,1),
   x_margin_vs_design_claim_mm=round((cap['design_claim_m']-worst['x']-arm-place)*1e3,2))
  print(name,json.dumps(out[name]),flush=True)
 os.makedirs(C.OUT,exist_ok=True);json.dump(dict(capture=cap,arm_accuracy_mm=arm*1e3,rack_placement_mm=place*1e3,scenarios=out,note=capture.__doc__),open(f'{C.OUT}/capture.json','w'),indent=1,default=float)
if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='capture':capture()
 else:
  import r19tol_replay as R
  R.main()
