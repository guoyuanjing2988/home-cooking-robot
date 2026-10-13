"""Issue #34 (Mac 2026-10-13, new file): independent full re-check of a cup -> rim-tipper-holder chain's playback states.
Registers the holder (r34holder.py), then runs r19cup_recheck.py unchanged. python rim_tipper_load_recheck.py results/mac/rim_tipper_load_<tag>.json"""
import sys,runpy
import r34holder   # noqa: F401
sys.argv=['r19cup_recheck.py']+sys.argv[1:]
runpy.run_path('r19cup_recheck.py',run_name='__main__')
