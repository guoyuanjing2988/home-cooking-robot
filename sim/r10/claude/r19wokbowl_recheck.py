"""WOK_TIP_HOLDING_BOWL (Mac 2026-10-13): independent full re-check of a wokbowl chain's playback states. Registers the
bowl, applies the chain's wok grasp tilt (as r17video.py does), then runs r19cup_recheck.py unchanged.
python r19wokbowl_recheck.py results/mac/wok_tip_holding_bowl_<tag>.json"""
import sys,json,runpy
import bowlobj   # noqa: F401
import kitchen17 as K17
r=json.load(open(sys.argv[1]))
if r.get('wok_tilt'):K17.set_wok_tilt(r['wok_tilt'])
if r.get('wok_grasp')=='end':K17.set_wok_end_grasp()
sys.argv=['r19cup_recheck.py']+sys.argv[1:]
runpy.run_path('r19cup_recheck.py',run_name='__main__')
