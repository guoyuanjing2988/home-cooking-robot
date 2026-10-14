"""R19 #42 m2 (R19_M2FIX.md): the ct2s set with the catch tray turned about the vertical at the pour. New file; nothing
shared is edited. r19prep5_chain.py is executed from its source with one line changed (as r19fr5prep_actions.py runs
r19prepchain.py): its keyframes come from override(action()) instead of action(). Every other option, the checker, the
rules and the output format are r19prep5_chain.py's.
 CYAW=<deg>  the tray at 'over the pan on the folded cradle', 'rolled <CDEG> (pour)' and 'level again' turned CYAW about
             the vertical, with the pour mouth on the same point over the pan (r19prep4_actions.mouth_pose with Rz(CYAW)):
             the roll stays about the tray's handle axis (turned with it), CDEG and MOUTHZ as before. The pick, the lanes
             and the return are r19prep5_actions' own; the follows slerp the turn between the lane and the pour.
Without CYAW the keyframes are exactly r19prep5_actions'.
python r19m2fix_ct2s.py ACT=ct2s CYAW=<deg> <r19prep5_chain.py options>
 (through r19mount_run.py RUNNER=r19m2fix_ct2s.py ... the result goes to results/r19/mount/)"""
import numpy as np
def override(res,KV):
 OBJ,SCENE,KF,GR=res
 if 'CYAW' not in KV:return res
 import kitchen16 as K,kitchen19p4 as P4,r19prep4_actions as A4,r19prep5_actions as A5
 inf=A5.INFO['ct2s'];mouth=np.array(inf['pan_bottom_world'])+[0,0,P4.STG_H+inf['mouth_over_pan_rim_m']]
 (Rl,pl),(Rr,pr)=A4.mouth_pose('ctray',K.Rz(float(KV['CYAW'])),mouth,inf['pour_deg']);n=0
 for i,k in enumerate(KF):
  if k['label'] in ('over the pan on the folded cradle','level again'):KF[i]=dict(k,R=Rl,p=pl);n+=1
  elif k['label'].startswith('rolled'):KF[i]=dict(k,R=Rr,p=pr);n+=1
 assert n==3,('ct2s pour keyframes not found',n)
 inf['cyaw_deg']=float(KV['CYAW'])
 return OBJ,SCENE,KF,GR
OLD='OBJ,SCENE,KF,GR=action();'
NEW="OBJ,SCENE,KF,GR=__import__('r19m2fix_ct2s').override(action(),KV);"
def source():
 s=open('r19prep5_chain.py',encoding='utf-8').read();assert s.count(OLD)==1,'r19prep5_chain.py changed: the action() call is not unique'
 return s.replace(OLD,NEW)
if __name__=='__main__':
 import os;exec(compile(source(),os.path.abspath('r19prep5_chain.py'),'exec'),{'__name__':'__main__','__file__':os.path.abspath('r19prep5_chain.py')})
