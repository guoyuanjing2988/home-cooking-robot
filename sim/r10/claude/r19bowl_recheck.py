"""R19 holding bowl: independent full re-check of a chain's playback states (registers the bowl, then runs
r19cup_recheck.py unchanged). python r19bowl_recheck.py results/mac/chain_bowl_<tag>.json"""
import sys,runpy
import bowlobj   # noqa: F401
sys.argv=['r19cup_recheck.py']+sys.argv[1:]
runpy.run_path('r19cup_recheck.py',run_name='__main__')
