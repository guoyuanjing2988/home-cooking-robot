"""R19 cart (issue #14): parametric concept CAD of the R10 docked cart (build123d, conda env robocasa). Units mm.
Frame RHS 40x40x2 steel (perimeter + 2 cross members), 5 mm Al deck, steel mast RHS 100x100x4 at y=-170,
steel beam RHS 100x50x4 to the UR mount at y=+80, 20 deg Al adapter wedge (pocketed), two hub-motor
envelopes (ZLLG65ASM500: D167 x 89) on brackets at (+-220,-220), two 100 mm caster envelopes at (+-220,110),
dock bumper (y face +210, z 250-350), electrics box. Cart frame as the sim: x along the counter, y to the
cabinets, z up from the floor. Prints CAD volumes x density for the metal parts (cross-check of r19cart_bom).
python r19cart_cad.py [outdir=cad/r19_cart] [XW=220] [MOUNT_Z=1120] [TILT=20]  (run in conda env robocasa)"""
import sys,os,math,json
from build123d import *
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a);OUT=next((a for a in sys.argv[1:] if '=' not in a),'cad/r19_cart');os.makedirs(OUT,exist_ok=True)
XW=float(KV.get('XW',220));YD,YC=-220.,110.;MZ=float(KV.get('MOUNT_Z',1120));TILT=float(KV.get('TILT',20));MY,MASTY=80.,-170.
STEEL,AL=7.85e-6,2.70e-6   # kg/mm^3
def box(x0,x1,y0,y1,z0,z1):return Pos((x0+x1)/2,(y0+y1)/2,(z0+z1)/2)*Box(x1-x0,y1-y0,z1-z0)
def rhs(b,h,t,L,axis):
 """Rectangular hollow section b x h x t, length L along axis ('x','y','z'), centred at the origin."""
 s=Box(b,h,L)-Box(b-2*t,h-2*t,L)
 return {'z':s,'x':Rot(0,90,0)*s,'y':Rot(90,0,0)*s}[axis]
parts={}
# chassis frame: perimeter 600 x 500 (x -300..300, y -300..200), tubes centred at z 110
f=Pos(0,-300+20,110)*rhs(40,40,2,600,'x')+Pos(0,200-20,110)*rhs(40,40,2,600,'x')
f+=Pos(-300+20,-50,110)*rhs(40,40,2,420,'y')+Pos(300-20,-50,110)*rhs(40,40,2,420,'y')
for x in (-90,90):f+=Pos(x,-50,110)*rhs(40,40,2,420,'y')
parts['frame']=(f,STEEL)
parts['deck']=(box(-300,300,-300,200,130,135),AL)
# mast foot plate + mast + beam + joint plate
# 20 deg adapter wedge 170 x 170, Al, pocketed under the UR flange; the arm leans to +y (counter), so the
# wedge is thick at -y (w1) and thin at +y (w0). The flange centre stays at MOUNT_Z, so the beam top is at
# MOUNT_Z - (w0+w1)/2 (the sim has its beam top at MOUNT_Z - 15 mm: a tilted plate there overlaps the beam)
w0=10.;w1=w0+170*math.tan(math.radians(TILT));BT=MZ-(w0+w1)/2
parts['mast']=(Pos(0,MASTY,190+(BT-50-190)/2)*rhs(100,100,4,BT-50-190,'z'),STEEL)
parts['beam']=(Pos(0,(MASTY+MY)/2,BT-25)*rhs(100,50,4,(MY-MASTY)+50,'y'),STEEL)   # 300 mm
wedge=extrude(Plane.YZ*Polygon((-85,0),(85,0),(85,w0),(-85,w1),align=None),amount=85,both=True)
parts['adapter']=(Pos(0,MY,BT)*wedge-Pos(0,MY,BT+w1)*Cylinder(45,2*(w1-w0)-10),AL)
# hub motors + brackets, casters, bumper, electrics
hub=None
for x in (-XW,XW):
 h=Pos(x,YD,82.5)*Rot(90,0,0)*Cylinder(83.5,89);hub=h if hub is None else hub+h
parts['hub_motors_envelope']=(hub,None)
cas=None
for x in (-XW,XW):
 c=Pos(x,YC,50)*Rot(90,0,0)*Cylinder(50,32)+Pos(x,YC,105)*Box(80,80,20);cas=c if cas is None else cas+c
parts['casters_envelope']=(cas,None)
parts['bumper']=(box(-280,280,200,210,250,350),None)
parts['electrics_box']=(box(-150,150,-160,-40,190,260),None)
asm=Compound(children=[p for p,_ in parts.values()])
export_step(asm,f'{OUT}/r19_cart.step');export_stl(asm,f'{OUT}/r19_cart.stl')
rep={}
for n,(p,rho) in parts.items():
 rep[n]=dict(volume_cm3=round(p.volume/1e3,1),mass_kg=round(p.volume*rho,2) if rho else None,bbox_mm=[[round(v,1) for v in p.bounding_box().min],[round(v,1) for v in p.bounding_box().max]])
 print(n,rep[n])
json.dump(dict(params=dict(XW=XW,YD=YD,YC=YC,MOUNT_Z=MZ,TILT=TILT,MOUNT_Y=MY,MAST_Y=MASTY,beam_top=BT,wedge_mm=[w0,round(w1,1)]),parts=rep,
 note='sim beam top = MOUNT_Z - 15 mm; a 20 deg adapter needs MOUNT_Z - %.0f mm'%((w0+w1)/2)),open(f'{OUT}/r19_cart_mass.json','w'),indent=1)
print('saved',OUT)
