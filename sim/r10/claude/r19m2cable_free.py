"""R19 #36 / #42 (m2 cable): r19cable2_free.py (the free-space map around the gripper) run unchanged, with one option (new
file): P5=1 hands r19prep5_verify.py to it in place of r19prep_verify.py (as r19prep5_cable.py does), so the prep sets that
need the step-4 / step-5 layers (fold, unfold, ct2s, stgwok: the T2L cradle) get their own scenes. At the top level, so the
pool workers (which re-run this file as __mp_main__) do the same. Maps are a search guide only, never a certificate.
python r19m2cable_free.py <mode> <r19cable2_free.py arguments> [P5=1] -> results/r19/cable/free/<mode>_<name>__<arm>.npz"""
import sys
sys.path.insert(0,'.')
if 'P5=1' in sys.argv[2:]:
 import r19prep5_verify
 sys.modules['r19prep_verify']=r19prep5_verify
import r19cable2_free as F
if __name__=='__main__':F.main()
