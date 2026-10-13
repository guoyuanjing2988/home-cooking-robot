"""R19 holding-bowl video: registers the bowl (bowlobj, which also registers the cup and the port pad), then runs
r17video.py unchanged. python r19bowl_video.py results/mac/chain_bowl_<tag>.json renders/mac/bowl_pour.mp4 [CAM=az,el,dist] [LOOK=x,y,z] [TITLE=..]"""
import sys,runpy
import bowlobj   # noqa: F401  (OBJ['bowl'], OBJ['cup'], kitchen17.add wrappers)
import dress   # render-only: the held bowl steel (R_gripper_* is drawn dark grey), the cup white, the pad and post steel
dress.RULES.insert(0,(('R_gripper_r19_bowl','r19_bowl'),'steel'));dress.RULES.insert(0,(('r19_cup',),'ceramic'));dress.RULES.insert(0,(('r19_scale',),'steel'))
sys.argv=['r17video.py']+sys.argv[1:]
runpy.run_path('r17video.py',run_name='__main__')
