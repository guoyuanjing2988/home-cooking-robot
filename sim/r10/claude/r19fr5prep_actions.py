"""R19 #2 (FR5) prep sets, round 2 (R19_FR5_PREP2.md): motion variants for the three sets that failed on
fr5_j6_pgc_sp20 (R19_FR5_PREP.md 3): tomato and carrot (the route between the tap and the carry lane) and basket (the
drain pose). New file; nothing shared is edited.

The keyframes are first built exactly as before, by r19prepchain.action() (tomato, carrot) and r19prep3_actions.action()
(basket), and then overridden here by override(). The set's purpose stays: same object and grasp, same pick, same pose
under the tap with the same rinse, same destination. Only the lane poses and the route between the tap and the lanes,
fixed carts at anchors / meets, and (basket) the drain / in-front-of-the-stream pose change. Gates, fixtures, the tap,
object sizes, the arm and the adapter are not touched.

Adopted settings (smoke runs, each re-checked at <= 4 mm with r19prep_verify.py; R19_FR5_PREP2.md):
 basket  BYAW=-20 BPITCH=30 XD=0,-.06,.02 XTAPC=-0.25 "XCART=pick:-0.55;over the tub:-0.55"   (SEEDS=1 TRIES=8 KEEP=8)
 carrot  XL1R=y30p-30 XL2R=y30p-30 CHAPP=0 CHUP=0,-.10,.18 SEEDUR=<carrot r2 UR5e chain>      (SEEDS=2 TRIES=10 KEEP=2)
 tomato  XL1=-0.65,.06,1.10 XL1R=level LVC=-0.25 L2C=-0.25 SEEDUR=<tomato r2 UR5e chain>     (SEEDS=2 TRIES=10 KEEP=3)
 (CHAPP, CHUP, LVC, L2C, SEEDUR are existing r19prepchain / r19fr5prep_chain options.)

Overrides (KEY=VALUE, all optional; with none of them the keyframes are exactly r19prepchain's):
 tomato, carrot
  XL1=x,y,z        position of the first lane meet (tomato: L1, the pick side; carrot: the lane on the pick side)
  XL1R=<rot>       object orientation there (default: as before = the tap orientation)
  XV1=x,y,z[;..]   vias between the first lane and the tap, listed from the lane toward the tap (the anchor at the tap
                   follows them backwards: its exit route); XV1R=<rot>[;..] their orientation(s) (default: the tap's)
  XL2=, XL2R=, XV2=, XV2R=   the same for the second lane (carrot: the chute-side lane, which before was the same pose as
                   the first; tomato: L2, after the tap, vias listed from the tap toward the lane)
  <rot> = tap (the tap orientation) | level (the pick orientation, grasp level) | p<deg> (grasp pitched <deg> about the
         world x axis, with the tap's roll for the tomato, e.g. p-15) | y<deg>p<deg> (also turned <deg> about z)
 basket
  XD=dx,dy,dz      the drain pose and its shakes, relative to the under-the-tap pose (before: 0,-.06,.04)
  XIN=dx,dy,dz     the in-front-of-the-stream pose on the way in (default: = XD)
  XDYAW=<deg>      the basket turned about the vertical through its floor centre at the drain, its shakes and the
                   in-front pose (the knob and the gripper swing with it)
  XDV=dx,dy,dz[;..] vias between the rinse centre and the drain (relative to the under-the-tap pose)
 all three
  XTAPC=<cart x>   the anchor under the tap gets this fixed cart (as r19prepchain's TAPC for the tomato)
  XCART=<label start>:<cart x>[;..]   the keyframes whose label starts so get this fixed cart (e.g. the other anchors, so
                   that both sides of a meet stay on the same side of the FR5's J1 dead zone)
  XDEDUP=0         keep exact duplicate start candidates (default: dropped; a fixed-cart anchor returns the same IK state from
                   many solver starts, and identical states give identical follows and joins, so only the run time changes)

Run (= r19prepchain.py executed from its source, with r19fr5prep_chain.py's SEEDUR opt-in, and with one line changed:
the keyframes come from override(action()) instead of action(); every other option, the checker and the output format
are r19prepchain's):
 python r19fr5prep_actions.py ACT=tomato|carrot|basket ARM=fr5_j6_pgc_sp20 TAG=fr5x.. [X..] [r19prepchain options]
 -> results/r19/prep/chain_<ACT>_<TAG>_<arm>.json (re-check it with r19prep_verify.py as any prep set)"""
import numpy as np
from scipy.spatial.transform import Rotation
import kitchen16 as K
def _vec(s):return np.array([float(v) for v in s.split(',')])
def _vecs(s):return [_vec(t) for t in s.split(';') if t]
def _rot(spec,Rtap,obj,troll):
 """object orientation from a <rot> spec (see the docstring)."""
 if spec in (None,'','tap'):return Rtap
 if spec=='level':return np.eye(3)
 yaw=0.
 if spec.startswith('y'):yaw,spec=float(spec[1:spec.index('p')]),spec[spec.index('p'):]
 assert spec.startswith('p'),spec
 R=K.Rx(float(spec[1:]))
 if obj=='tomato':a=R@K.OBJ['tomato']['a'];R=Rotation.from_rotvec(a*np.radians(troll)).as_matrix()@R   # the tap's roll about the approach axis (r19prepchain.action roll())
 return K.Rz(yaw)@R
def _kf(base,R,p,label):
 k={a:b for a,b in base.items() if a!='_o'};k.update(R=np.asarray(R,float),p=np.asarray(p,float),label=label,anchor=False,meet=False,dw=0.,seat=0.,c='F');return k
def _vias(KV,key,base,Rtap,OBJ,troll,label):
 vs=_vecs(KV[key]);rs=KV.get(key+'R','tap').split(';');rs=(rs*len(vs))[:len(vs)]
 return [_kf(base,_rot(r,Rtap,OBJ,troll),v,f'{label} {i+1}') for i,(v,r) in enumerate(zip(vs,rs))]
def override(res,KV):
 """res = r19prepchain.action()'s (object, scene extras, keyframes, grasp list); returns the same with the keyframes overridden."""
 OBJ,SCENE,KF,GR=res;KF=[dict(k,_o=i) for i,k in enumerate(KF)]   # _o: the original index (grasp list)
 lab=lambda s:[i for i,k in enumerate(KF) if k['label']==s]
 if OBJ in ('tomato','carrot') and KV.get('ACT') in ('tomato','carrot'):
  troll=float(KV.get('TROLL',-90.)) if OBJ=='tomato' else 0.
  t=lab('under the tap')[0];Rtap=KF[t]['R'];M=[i for i,k in enumerate(KF) if k['meet']];m1,m2=M[0],M[1]
  # second lane first (indices after the tap shift when vias go in before it)
  if 'XL2' in KV or 'XL2R' in KV:KF[m2]=dict(KF[m2],p=_vec(KV['XL2']) if 'XL2' in KV else KF[m2]['p'],R=_rot(KV.get('XL2R'),Rtap,OBJ,troll) if 'XL2R' in KV else KF[m2]['R'])
  if 'XV2' in KV:KF[m2:m2]=_vias(KV,'XV2',KF[m2],Rtap,OBJ,troll,'via to the lane')
  if 'XL1' in KV or 'XL1R' in KV:KF[m1]=dict(KF[m1],p=_vec(KV['XL1']) if 'XL1' in KV else KF[m1]['p'],R=_rot(KV.get('XL1R'),Rtap,OBJ,troll) if 'XL1R' in KV else KF[m1]['R'])
  if 'XV1' in KV:KF[m1+1:m1+1]=_vias(KV,'XV1',KF[m1],Rtap,OBJ,troll,'via to the tap')
 elif KV.get('ACT')=='basket':
  t=lab('under the tap')[0];TAP=KF[t]['p'];Rn=KF[t]['R']
  dD=_vec(KV.get('XD','0,-.06,.04'));dI=_vec(KV.get('XIN',KV.get('XD','0,-.06,.04')));Ry=K.Rz(float(KV.get('XDYAW',0.)))@Rn
  for i,k in enumerate(KF):
   if k['label']=='in front of the stream':KF[i]=dict(k,p=TAP+dI,R=Ry)
   elif k['label']=='drain (out of the stream)':KF[i]=dict(k,p=TAP+dD,R=Ry)
   elif k['label'].startswith('shake') and k['label'].endswith('down'):KF[i]=dict(k,p=TAP+dD-[0,0,.015],R=Ry)
   elif k['label'].startswith('shake') and k['label'].endswith('up'):KF[i]=dict(k,p=TAP+dD,R=Ry)
  if 'XDV' in KV:
   d=lab('drain (out of the stream)')[0]
   KF[d:d]=[dict({a:b for a,b in KF[d].items() if a!='_o'},p=TAP+v,R=Ry,label=f'via {i+1} to the drain',dw=0.,anchor=False,meet=False) for i,v in enumerate(_vecs(KV['XDV']))]
 if 'XTAPC' in KV:
  t=lab('under the tap')[0];KF[t]=dict(KF[t],c=float(KV['XTAPC']))
 for it in [s for s in KV.get('XCART','').split(';') if s]:   # XCART=<label start>:<cart>;..  fixed cart of those (anchor) keyframes
  s,c=it.rsplit(':',1);hit=[i for i,k in enumerate(KF) if k['label'].startswith(s)];assert hit,('XCART: no keyframe',s)
  for i in hit:KF[i]=dict(KF[i],c=float(c))
 # grasp / release keyframe indices follow their keyframes
 GR=[(next(j for j,k in enumerate(KF) if k.get('_o')==i),w,inw) for i,w,inw in GR]
 for k in KF:k.pop('_o',None)
 return OBJ,SCENE,KF,GR
OLD='OBJ,SCENE,KF,GR=action();'
NEW="OBJ,SCENE,KF,GR=__import__('r19fr5prep_actions').override(action(),KV);"
def source():
 """r19prepchain.py's source with r19fr5prep_chain's SEEDUR opt-in and the keyframe override (in memory only)."""
 import r19fr5prep_chain as PC
 s=PC.patched_source();assert s.count(OLD)==1,'r19prepchain.py changed: the action() call is not unique'
 s=s.replace(OLD,NEW);r="res=dict(act=ACT,"
 assert s.count(r)==1;s=s.replace(r,"res=dict(keyframe_source='r19prepchain/r19prep3_actions keyframes overridden by r19fr5prep_actions.override (argv X..)',start_dedup=KV.get('XDEDUP','1')!='0',act=ACT,")
 d=" _cands[key]=(out,stat);return _cands[key]"   # XDEDUP (default on): exact duplicate start states (fixed-cart anchors return the same
 assert s.count(d)==1                            # IK solution from many solver starts) are dropped; identical states give identical follows and joins
 return s.replace(d," out=out if KV.get('XDEDUP','1')=='0' else [c_ for i_,c_ in enumerate(out) if not any(np.max(abs(np.array(c_['q'])-np.array(o_['q'])))<1e-3 for o_ in out[:i_])]\n"+d)
if __name__=='__main__':
 import os;exec(compile(source(),os.path.abspath('r19prepchain.py'),'exec'),{'__name__':'__main__','__file__':os.path.abspath('r19prepchain.py')})
