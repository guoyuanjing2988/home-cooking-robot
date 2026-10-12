"""R15 spatula geometry and stroke poses, shared by stirbench.py (physics) and kitchen15.py /
r15reach.py (reach), so both use the same tool and the same keyframes.
Wok: spherical cap, sphere radius RS 0.20 m, rim radius 0.17 m; wok frame origin = inner
bottom point, +y = away from the robot (the arm works from -y).
Spatula (锅铲 class, GSW TN-S / Town 33976 sizes in r15_cooking_market.md 6): blade 100 mm
wide x 85 mm long, its edge an arc that fits the wok; the handle leaves the blade's top edge
bent BEND = 25° toward the face side, as on a real wok spatula, so the blade can lie at a
shallow angle on the steel while the handle rises toward the hand.
Blade frame: x = blade width (w), y = up the blade (hgt), z = face normal; origin = edge
midpoint. Stroke poses are set by the HANDLE elevation E above horizontal (pointing back
toward the robot), not by the blade angle: the blade then makes (E - BEND - local wall
slope) with the steel, which must stay >= MIN_BLADE_DEG."""
import numpy as np
from scipy.spatial.transform import Rotation
RS,A_RIM=.20,.17;DEPTH=RS-np.sqrt(RS**2-A_RIM**2);C=np.array([0,0,RS])
BW,BH,BT=.10,.085,.004;BEND=np.radians(25);MIN_BLADE_DEG=10.
HD=np.array([0,np.cos(BEND),np.sin(BEND)])   # handle direction in the blade frame
BASE=np.radians(90)                          # strokes push away from the robot (+y)
def edge_rc():return RS*np.sin(np.radians(30))   # edge arc that fits the steel at a 30° blade angle (shallower: corners touch first; steeper: they ride a few mm up)
def grip_point(grip):
 """Grip point in the blade frame, grip m from the edge along the blade then the handle."""
 return np.array([0,BH,0])+HD*(grip-BH)
def pose(u,e,psi,elev_deg,clear=.003):
 """Blade origin p and rotation R (wok frame) with the blade edge's lowest point clear m off the steel at
 horizontal stroke coordinates (u along, e across, stroke yaw psi) and the handle at
 elev_deg above horizontal, pointing back along the stroke. Returns p, R, blade angle to
 the steel (deg)."""
 d=np.array([np.cos(BASE+psi),np.sin(BASE+psi),0.]);l=np.array([-d[1],d[0],0.])
 h_=u*d+e*l;r=np.linalg.norm(h_);P=np.array([h_[0],h_[1],RS-np.sqrt(RS**2-r**2)])
 n=(C-P)/RS;p=P+clear*n
 t=d-(d@n)*n;t/=np.linalg.norm(t)
 w=np.cross(n,t);w/=np.linalg.norm(w)
 E=np.radians(elev_deg);h=-np.cos(E)*d+np.sin(E)*np.array([0,0,1.])
 h=h-(h@w)*w;h/=np.linalg.norm(h)                 # keep the handle in the stroke plane
 zh=np.cross(w,h);hgt=np.cos(BEND)*h-np.sin(BEND)*zh
 R=np.c_[w,hgt,np.cross(w,hgt)]
 # a 10 cm blade on the curved steel touches at its lowest edge point (often a corner at shallow
 # blade angles), not at the edge midpoint: shift along n so that point sits clear m off the steel
 edge=bottom_corners()
 for _ in range(3):
  gap=RS-np.linalg.norm(p+edge@R.T-C,axis=1);p=p+(clear-gap.min())*n
 return p,R,float(np.degrees(np.arcsin(np.clip(hgt@n,-1,1))))
def roll(p,R,grip,deg):
 """Roll the spatula by deg about its handle axis through the grip point (wrist 3)."""
 g=p+R@grip_point(grip);ax=R@HD;Rr=Rotation.from_rotvec(ax*np.radians(deg)).as_matrix()
 return g+Rr@(p-g),Rr@R
def bottom_corners():
 """Lower corners of the blade segment boxes (blade frame): the points that meet the steel."""
 return np.array([c+np.array([sx*h[0],-h[1],sz*h[2]]) for c,h in blade_parts() for sx in (-1,1) for sz in (-1,1)])
def blade_parts():
 """Blade segments (centre, half size) in the blade frame; the edge follows an arc of radius edge_rc()."""
 rc=edge_rc();out=[]
 for k in range(5):
  x=(k-2)*BW/5;rise=rc-np.sqrt(rc**2-x**2);out.append((np.array([x,rise+BH/2,0]),np.array([BW/10*1.02,BH/2,BT/2])))
 return out
