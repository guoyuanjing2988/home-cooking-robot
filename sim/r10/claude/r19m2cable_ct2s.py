"""R19 #36 / #42 (m2 cable, R19_M2CABLE.md): the UR5e ct2s set planned with the m2 cable run modelled, the cart at the tray
pick and at the tray return fixed. New file; nothing shared is edited. r19m2fix_ct2s.py (CYAW, the tray turned at the pour) is
used unchanged; on top, PICKC=<x> fixes the cart x of the two anchors 'pick (seated under the blade plate)' and 'in front of
the lever base' (r19prep5_actions leaves them free). Why: with the cable modelled the free choice moves the pick cart to
-1.18 (the cable meets the cart's staging block nearer), and the lane join to the pour cart (-0.52) is then blocked
(tray vs base plate during the 0.7 m shuffle); -0.62 is a cable-clear pick candidate 0.1 m from the pour.
python r19mount_run.py RUNNER=r19m2cable_ct2s.py ACT=ct2s CYAW=<deg> PICKC=<x> <r19prep5_chain.py options> ARM=<cable option>"""
import r19m2fix_ct2s as F
ANCH=('pick (seated under the blade plate)','in front of the lever base')
def override(res,KV):
 OBJ,SCENE,KF,GR=F.override(res,KV)
 if 'PICKC' in KV:
  n=0
  for i,k in enumerate(KF):
   if k['label'] in ANCH:KF[i]=dict(k,c=float(KV['PICKC']));n+=1
  assert n==2,('ct2s pick / return anchors not found',n)
 return OBJ,SCENE,KF,GR
if __name__=='__main__':
 import os
 s=F.source().replace("__import__('r19m2fix_ct2s')","__import__('r19m2cable_ct2s')")
 exec(compile(s,os.path.abspath('r19prep5_chain.py'),'exec'),{'__name__':'__main__','__file__':os.path.abspath('r19prep5_chain.py')})
