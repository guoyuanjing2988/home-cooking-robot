"""R19 prep step 5 (#38): the gripper-cable re-check (r19cable_check.py prep, imported UNCHANGED) for sets whose scenes need the
step-4 / step-5 layers. r19cable_check.py's prep mode takes its scenes from r19prep_verify.py, which does not build the
kitchen19p4 (T2L cradle) or kitchen19p5 (fold-away cradle) parts; here r19prep5_verify.py (a copy of r19prep4_verify.py
+ the p5 layer) is handed to it in place of r19prep_verify (sys.modules), at the top level so the pool workers do the same.
Everything else (states, densifying, checks, groups, verdicts) is r19cable_check.py's own. Output under
results/r19/prep5/cable/prep/ instead of results/r19/cable/ (other agents' folder).
python r19prep5_cable.py prep FILE=<chain json> ARM=ur5e_enc2_pgcc_yp_a-45 [RACK=keyed SPX=1.56 SPY=.20] [WORKERS=16]"""
import sys,os
sys.path.insert(0,'.')
import r19prep5_verify
sys.modules['r19prep_verify']=r19prep5_verify
import r19cable_check as RC
RC.OUT='results/r19/prep5/cable'
if __name__=='__main__':
 assert RC.MODE=='prep',RC.MODE
 RC.main()
