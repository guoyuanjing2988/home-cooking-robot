"""R19 cup video: registers the cup and the port pad (cupobj), then runs r17video.py unchanged.
python r19cup_video.py results/mac/chain_cup_<tag>.json renders/mac/cup_pour.mp4 [CAM=az,el,dist] [LOOK=x,y,z] [TITLE=..]"""
import sys,runpy
import cupobj   # noqa: F401  (OBJ['cup'], kitchen17.add wrapper)
import dress   # render-only: the held cup white (R_gripper_* is drawn dark grey), the pad and post steel
dress.RULES.insert(0,(('R_gripper_r19_cup','r19_cup'),'ceramic'));dress.RULES.insert(0,(('r19_scale',),'steel'))
sys.argv=['r17video.py']+sys.argv[1:]
runpy.run_path('r17video.py',run_name='__main__')
