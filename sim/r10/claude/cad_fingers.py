"""R12 printable parts for the dual-zone finger (fingers.DESIGNS['D']) on a DH PGC-140-50.
Run with the robocasa conda env (build123d):  python cad_fingers.py <outdir>
Units mm. Part frame (MINUS finger): x along the finger (0 = jaw top face, + toward
the tip), y = closing direction (0 = pad datum, + toward the item), z = pad height
(z = 0 at the pad centre; the jaw centre line is at z = +C: the crank).

Parts (the plus finger is the mirror image, exported as *_plus):
 finger_body  PETG (food-contact grade, e.g. Kimya PETG-S natural): jaw mount block,
              beam, rigid rims flush with the datum at |z| >= W, pocket for the
              floating pad, two guide/stop bores for M3 shoulder screws
 pad_carrier  PETG plate floating in the pocket on two stainless compression springs
              (rate ~0.75 N/mm each, OD <= 7 mm, to be chosen from a catalogue)
 pad_skin     TPU 92A (food-contact certified grade, e.g. Kimya TPU-92A) with a 3 mm grid
              of 1.0 x 0.8 mm grooves; or cast Smooth-Sil 940 (40A) in pad_mold
Jaw interface (PGC-140 Short Manual v2.1, Fig 1.3b, read from the drawing): per jaw
2x M4 (depth 8) + 1x dowel Ø3 in a line at 5 mm pitch. The line direction (here z) and
its distance from the closed pad face (JAW_BOLT_Y) are ASSUMPTIONS: check DH's STEP
file before printing."""
import sys,os
from build123d import *
OUT=sys.argv[1] if len(sys.argv)>1 else 'cad';os.makedirs(OUT,exist_ok=True)
# --- parameters (match fingers.DESIGNS['D']) ---
P=75.0; C=20.0; H=48.0; W=19.0       # protrusion, crank, pad height, soft-zone half height
TP=4.0; T=8.0                        # rim plate + structure behind the datum at the rims
E_=1.0; TRAVEL=6.0                   # skin protrudes E_ when unloaded; travel to the hard stop
SKIN=3.0; CARRIER=4.0; WALL=4.0
GAP=1.5                              # beam clears the housing top face (as DH's own fingers)
MOUNT_X=8.0; MOUNT_Z=18.0            # mount block on the jaw (thickness along x, width along z)
JAW_BOLT_Y=7.0                       # bolt line, toward the item from the datum (ASSUMED)
PITCH=5.0
POCKET=SKIN+CARRIER-E_+TRAVEL        # 12
TOT=max(TP+T,POCKET+WALL)            # 16 behind the datum
X0,X1=GAP+3.0,P-3.0
cyl=lambda r,h:Cylinder(r,h,align=(Align.CENTER,Align.CENTER,Align.MIN))
# --- body ---
beam=Pos(GAP+(P-GAP)/2,-TOT/2,0)*Box(P-GAP,TOT,H)
mount=Pos(MOUNT_X/2,(JAW_BOLT_Y+4-TOT)/2,C)*Box(MOUNT_X,JAW_BOLT_Y+4+TOT,MOUNT_Z)
body=beam+mount
body=body-Pos((X0+X1)/2,-POCKET/2,0)*Box(X1-X0,POCKET,2*W)
# jaw bolts along x: Ø4.5 clearance through the block, Ø8 x 4 counterbore from the +x side
for z_ in (C-PITCH,C+PITCH):
 body=body-Pos(-1,JAW_BOLT_Y,z_)*Rot(0,90,0)*cyl(2.25,MOUNT_X+2)
 body=body-Pos(MOUNT_X-4,JAW_BOLT_Y,z_)*Rot(0,90,0)*cyl(4.0,5)
body=body-Pos(-0.01,JAW_BOLT_Y,C)*Rot(0,90,0)*cyl(1.55,3.0)  # Ø3.1 dowel hole, 3 mm deep
# floating pad guides: Ø3.4 through the back wall, Ø6.5 x 3.5 counterbore outside, Ø7.2 x 2 spring seat inside
GX=((X0+X1)/2-20,(X0+X1)/2+20)
for gx in GX:
 body=body-Pos(gx,-TOT-0.5,0)*Rot(-90,0,0)*cyl(1.7,WALL+1)
 body=body-Pos(gx,-TOT-0.01,0)*Rot(-90,0,0)*cyl(3.25,3.5)
 body=body-Pos(gx,-POCKET-0.01,0)*Rot(-90,0,0)*cyl(3.6,2.0)
# --- floating pad at its unloaded (extended) position ---
CL,CH=X1-X0-0.6,2*W-0.6
carrier=Pos((X0+X1)/2,E_-SKIN-CARRIER/2,0)*Box(CL,CARRIER,CH)
for gx in GX:carrier=carrier-Pos(gx,E_-SKIN-CARRIER-0.01,0)*Rot(-90,0,0)*cyl(2.0,CARRIER-1)  # Ø4 x 3 for an M3 heat-set insert
skin=Pos((X0+X1)/2,E_-SKIN/2,0)*Box(CL,SKIN,CH)
for i in range(int(CL//3)):skin=skin-Pos(X0+0.3+1.5+3*i,E_-0.4,0)*Box(1.0,0.8,CH+1)
for k in range(int(CH//3)):skin=skin-Pos((X0+X1)/2,E_-0.4,-CH/2+1.5+3*k)*Box(CL+1,0.8,1.0)
mold=Pos((X0+X1)/2,E_-SKIN/2-1,0)*Box(CL+8,SKIN+2,CH+8)-Pos((X0+X1)/2,E_-SKIN/2,0)*Box(CL,SKIN+0.01,CH)
parts={'finger_body':body,'pad_carrier':carrier,'pad_skin':skin,'pad_mold':mold}
for n,p in parts.items():
 export_step(p,f'{OUT}/{n}_minus.step');export_stl(p,f'{OUT}/{n}_minus.stl')
 m=mirror(p,Plane.XZ);export_step(m,f'{OUT}/{n}_plus.step');export_stl(m,f'{OUT}/{n}_plus.stl')
 bb=p.bounding_box();print(n,'bbox mm',round(bb.size.X,1),round(bb.size.Y,1),round(bb.size.Z,1),'volume cm3',round(p.volume/1000,2),'solids',len(p.solids()))
export_step(Compound(children=[body,carrier,skin]),f'{OUT}/finger_D_minus_assembly.step')
