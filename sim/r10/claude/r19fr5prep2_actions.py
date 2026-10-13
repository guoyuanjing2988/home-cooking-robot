"""R19 #2 / #38 (FR5 tomato vs the folded T2L cradle, R19_FR5_PREP3.md): pick-side motion options on top of
r19fr5prep_actions.py (R19_FR5_PREP2.md). New file; nothing shared is edited (r19fr5prep_actions.py, r19prepchain.py,
r19prep3_actions.py are imported / read and patched in memory only, as r19fr5prep_actions.py does).

The keyframes are built exactly as before (r19prepchain.action() -> r19fr5prep_actions.override()) and then the PICK
SIDE only (the keyframes before the first lane meet: 'pick', 'lifted', 'out and up') can be changed here:
 XPY=<deg>        the grasp turned <deg> about the vertical at those keyframes (the tomato is the R11 cylinder, axis
                  vertical, so the item on its pad is the same; only the direction the gripper comes from changes; the
                  first lane keeps its own orientation, so the carry turns it back on the way)
 XPU=x,y,z        the 'out and up' position (default as before: pick + (0, -0.04, 0.15))
 (the pick cart itself: r19fr5prep_actions's XCART=pick:<cart x>)
Everything else (lanes, the tap, the rinse, the lever base, gates, objects, the arm) is r19fr5prep_actions / r19prepchain.
With no XPY / XPU the keyframes are exactly r19fr5prep_actions's.

Run (r19prepchain.py executed from its source with r19fr5prep_chain's SEEDUR opt-in and this override):
 python r19fr5prep2_actions.py ACT=tomato ARM=fr5_j6_pgc_sp20 TAG=fr5y.. [XPY=..] [XPU=..] [r19fr5prep_actions / r19prepchain options]
 -> results/r19/prep/chain_tomato_<TAG>_<arm>.json (re-check with r19prep_verify.py, r19cable_check.py, r19prep5_screen.py)"""
import numpy as np
import kitchen16 as K
import r19fr5prep_actions as XA
PICK_SIDE=('pick','lifted','out and up')
def override(res,KV):
 OBJ,SCENE,KF,GR=XA.override(res,KV)
 if OBJ=='tomato' and KV.get('ACT')=='tomato':
  m1=[i for i,k in enumerate(KF) if k['meet']][0]
  idx=[i for i in range(m1) if KF[i]['label'] in PICK_SIDE];assert [KF[i]['label'] for i in idx]==list(PICK_SIDE),[k['label'] for k in KF[:m1]]
  if 'XPY' in KV:
   Rz=K.Rz(float(KV['XPY']))
   for i in idx:KF[i]=dict(KF[i],R=Rz@KF[i]['R'])
  if 'XPU' in KV:
   i=idx[2];KF[i]=dict(KF[i],p=np.array([float(v) for v in KV['XPU'].split(',')]))
 return OBJ,SCENE,KF,GR
OLD="OBJ,SCENE,KF,GR=__import__('r19fr5prep_actions').override(action(),KV);"
NEW="OBJ,SCENE,KF,GR=__import__('r19fr5prep2_actions').override(action(),KV);"
def source():
 """r19fr5prep_actions.source() with this module's override (in memory only)."""
 s=XA.source();assert s.count(OLD)==1,'r19fr5prep_actions.source() changed: the override call is not unique'
 s=s.replace(OLD,NEW);r="res=dict(keyframe_source='r19prepchain/r19prep3_actions keyframes overridden by r19fr5prep_actions.override (argv X..)'"
 assert s.count(r)==1;return s.replace(r,"res=dict(keyframe_source='r19prepchain/r19prep3_actions keyframes overridden by r19fr5prep_actions.override + r19fr5prep2_actions.override (argv X..)'")
if __name__=='__main__':
 import os;exec(compile(source(),os.path.abspath('r19prepchain.py'),'exec'),{'__name__':'__main__','__file__':os.path.abspath('r19prepchain.py')})
