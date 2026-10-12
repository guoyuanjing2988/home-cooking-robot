"""R13 printable parts: robot-swappable finger sets for the PGC-140-50, the supported-
grasp fork, the finger rack, the V-rib slot tray and the handled food basket.
Run with the robocasa conda env (build123d):  python cad_r13.py <outdir>
Units mm. Finger part frame (MINUS finger) as in cad_fingers.py: x along the finger
(0 = jaw top face, + toward the tip), y = closing direction (0 = pad datum at the closed
jaw, + toward the item), z = pad height (0 at the pad centre; the jaw is at z = +C).

Quick change (my design from research/finger_change_and_food_eoat.md; load paths by
form fit, latch only against pull-off):
 jaw_adapter  bolted to each jaw (2x M4 + dowel Ø3, pattern ASSUMED, check DH STEP):
              a 60° dovetail tongue along x (14 wide, 7 high, 26 long) with a Ø4.1
              cross hole along z for the lock pin.
 finger root  dovetail socket that slides up onto the tongue (+x -> -x) to a shoulder;
              a Ø4 x 30 stainless lock pin along z, spring-loaded inward, with its head
              outside the finger's +z face. Grip force (y) and pad-plane loads (z) bear
              on the dovetail; only pull-off along x is held by the pin (shear, steel).
 finger_rack  one nest per finger: lead-in V (2 mm), bottom stop, and a ramp that lifts
              the pin head: park = lower the fingers into the nests (ramp retracts the
              pins), lift the jaws out; pick = lower the jaws into the parked fingers,
              then move sideways (+z) off the ramp so the pins snap into the tongues.
Bought parts per finger: 1 lock pin Ø4x30 (A2), 1 spring Ø5x15 (~2 N/mm), 2 pad springs,
2 M3 shoulder screws; per jaw adapter: 2x M4x16, 1 dowel Ø3x8."""
import sys,os
from build123d import *
OUT=sys.argv[1] if len(sys.argv)>1 else 'cad/r13';os.makedirs(OUT,exist_ok=True)
cyl=lambda r,h:Cylinder(r,h,align=(Align.CENTER,Align.CENTER,Align.MIN))
def box(x0,x1,y0,y1,z0,z1):return Pos((x0+x1)/2,(y0+y1)/2,(z0+z1)/2)*Box(x1-x0,y1-y0,z1-z0)
C=20.0;JAW_BOLT_Y=7.0;PITCH=5.0
TONGUE_W,TONGUE_H,TONGUE_L,DT_ANG=14.0,7.0,26.0,60.0
def dovetail(w,h,l,clear=0.):
 """Dovetail prism along x: narrow side at y=0 (adapter face), wide side at y=-h?"""
 import math
 d=h/math.tan(math.radians(DT_ANG))
 pts=[(-(w/2-d)-clear,0),((w/2-d)+clear,0),(w/2+clear,-h-clear),(-w/2-clear,-h-clear)]  # (z,y)
 sk=Polyline([(0,y,z) for z,y in pts]+[(0,pts[0][1],pts[0][0])]);f=make_face(sk) if False else None
 prof=Plane.YZ*Polygon(*[(y,z) for z,y in pts],align=None)
 return extrude(prof,amount=l)
def jaw_adapter():
 base=box(0,9,-6-TONGUE_H,JAW_BOLT_Y+6,C-11,C+11)
 for z_ in (C-PITCH,C+PITCH):
  base-=Pos(-1,JAW_BOLT_Y,z_)*Rot(0,90,0)*cyl(2.25,12);base-=Pos(5,JAW_BOLT_Y,z_)*Rot(0,90,0)*cyl(4.0,5)
 base-=Pos(-.01,JAW_BOLT_Y,C)*Rot(0,90,0)*cyl(1.55,4)
 tongue=Pos(8.9,-6,C)*dovetail(TONGUE_W,TONGUE_H,TONGUE_L+.1)
 a=base+tongue
 a-=Pos(9+TONGUE_L-8,-6-TONGUE_H/2,C-TONGUE_W/2-1)*cyl(2.05,TONGUE_W+2)  # lock-pin cross hole (along z)
 return a
def finger(P,D,H,fo,Wz,name,tines=None,TP=4.,T=8.,pocket=True):
 """Dual-zone finger with the quick-change socket. P protrusion past the housing face
 (finger length from the jaw top = P + housing offset 0 here), D housing face to item
 centre, H pad height, fo closed half gap (pad datum offset from the jaw centre line)."""
 GAP=1.5;X0,X1=GAP+3.0,P-3.0;TOT=16.0  # 12 mm pad pocket + 4 mm back wall (as R12)
 zs=tines or [0.]
 body=None
 for z0 in zs:  # pad beam(s) at the datum, offset fo from the closed jaw line
  b=box(GAP,P,-TOT,0,z0-H/2,z0+H/2);body=b if body is None else body+b
  if pocket:body-=box(X0,X1,-12,0.01,z0-Wz,z0+Wz)
 if len(zs)>1:body+=box(GAP,GAP+10,-TOT,0,min(zs)-H/2,max(zs)+H/2)
 # root block carrying the socket: from the datum back to the jaw line (fo) + 14 mm
 yb=-(fo+6+TONGUE_H+5);root=box(0,TONGUE_L+12,yb,-TOT+0.01,C-12,C+12)
 body=body+root
 sock=Pos(-0.01,-(fo+6),C)*dovetail(TONGUE_W,TONGUE_H,TONGUE_L+0.02,clear=.25)
 body-=sock
 body-=Pos(TONGUE_L-8,-(fo+6)-TONGUE_H/2,C-14)*cyl(2.1,30)        # lock-pin bore along z
 body-=Pos(TONGUE_L-8,-(fo+6)-TONGUE_H/2,C+12-6)*cyl(3.0,6.2)     # spring / head counterbore on +z
 return body
def rack(n=2,pitch=70.):
 """Nests for n finger pairs (one pair per row), with pin-head ramps on +z."""
 L=n*pitch;b=box(0,60,-L/2,L/2,0,12)
 for i in range(n):
  y=-L/2+pitch*(i+.5)
  for s in (-1,1):
   b-=box(8,52,y+s*14-6,y+s*14+6,4,12.01)              # finger nests
   b+=Pos(30,y+s*21,11.9)*box(-4,4,-1,1,0,6.1)    # ramp post beside the nest (lifts the pin head)
 return b
def slot_tray(W=150.,L=240.,HR=35.,pitch=34.):
 base=box(0,W,0,L,0,5)
 import math
 for k in range(int(L//pitch)+1):
  y=pitch*(k+.5)
  if y>L-3:break
  base+=box(5,W-30,y-3,y+3,5,5+HR-6)
  base+=Pos((5+W-30)/2,y,5+HR-6)*Box(W-35,6,6)
 return base
def basket(R=100.,H=70.):
 b=cyl(R,H)-Pos(0,0,2)*cyl(R-2,H)
 for i in range(-4,5):
  for j in range(-4,5):
   if (i*18)**2+(j*18)**2<(R-10)**2:b-=Pos(i*18,j*18,-1)*cyl(3,4)   # drain holes Ø6
 for s in (-1,1):b+=box(s*(R-3)-4,s*(R-3)+4,-4,4,H-20,H+50)
 b+=box(-R+4,R-4,-6,6,H+44,H+56)
 knob=box(-15,15,-20,20,H+55.9,H+86)
 import math
 for s in (-1,1):knob-=Pos(s*15,0,H+71)*Rot(90,0,0)*Pos(0,0,-21)*Cylinder(4.5,42,align=(Align.CENTER,Align.CENTER,Align.MIN))  # keyed V-ish grooves for the pads
 return b+knob
if __name__=='__main__':
 sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
 import foods
 parts={'jaw_adapter':jaw_adapter()}
 for k,v in foods.SETS.items():
  if v.get('gripper')!='PGC':continue
  parts[f'finger_{k}']=finger(1000*v['P']+1000*(v['D']-.035)*0,1000*v['D'],1000*v['H'],1000*v['fo'],1000*v['w'],k)
 parts['fork_P2']=finger(53,41,16,13.5,6.5,'fork',tines=[-34.,34.],pocket=True)
 parts['finger_rack_2pairs']=rack(2);parts['slot_tray_section']=slot_tray();parts['food_basket']=basket()
 for n,p in parts.items():
  export_step(p,f'{OUT}/{n}.step');export_stl(p,f'{OUT}/{n}.stl')
  bb=p.bounding_box();print(n,'bbox mm',round(bb.size.X,1),round(bb.size.Y,1),round(bb.size.Z,1),'volume cm3',round(p.volume/1000,1),'solids',len(p.solids()))
