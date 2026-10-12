"""R14 concept CAD (build123d, conda env robocasa): the seasoning station in an upper
cabinet, the rice/flour module, the robot cup (料杯) and the rotary 4-compartment pour
drum (分格转筒料盒). Units mm. Concept geometry for layout and rendering; bought parts
(pumps, augers, load cell, bottles) are envelopes. python cad_r14.py <outdir>
Station frame: x along the counter, y from the cabinet front (0) to the wall (330),
z up from the cabinet floor (0); parts below the floor hang under the cabinet."""
import sys,os,math
from build123d import *
OUT=sys.argv[1] if len(sys.argv)>1 else 'cad/r14';os.makedirs(OUT,exist_ok=True)
def box(x0,x1,y0,y1,z0,z1):return Pos((x0+x1)/2,(y0+y1)/2,(z0+z1)/2)*Box(x1-x0,y1-y0,z1-z0)
cylz=lambda r,h:Cylinder(r,h,align=(Align.CENTER,Align.CENTER,Align.MIN))
# ---------------- pour drum: Ø80 x 140, 4 compartments, staggered slots ----------------
def drum(R=40,LC=35,NC=4,wall=2.,phi=(-75,-25,25,75),slot=(40,40,40,60)):
 L=LC*NC;tube=Rot(0,90,0)*Pos(0,0,-L/2)*(Cylinder(R,L,align=(Align.CENTER,Align.CENTER,Align.MIN))-Cylinder(R-wall,L,align=(Align.CENTER,Align.CENTER,Align.MIN)))
 d=tube
 for i in range(NC+1):d+=Pos(-L/2+LC*i,0,0)*Rot(0,90,0)*Cylinder(R,wall)
 for c in range(NC):  # slot = sector cut through the wall of compartment c
  xc=-L/2+LC*(c+.5);a=math.radians(phi[c]);w=math.radians(slot[c])
  pts=[(0,0)]+[(R+5)*math.sin(a+w*(k/8-.5)) for k in range(9)] and None
  sector=Pos(xc,0,0)*Rot(phi[c],0,0)*Pos(0,0,R-wall-1)*Box(LC-2*wall,2*(R)*math.sin(w/2),wall+4,align=(Align.CENTER,Align.CENTER,Align.MIN))
  d-=sector
 # end knob (30 mm, keyed V faces) on the -x cap
 knob=Pos(-L/2-16,0,0)*Box(30,30,30);knob-=Pos(-L/2-16,15,0)*Rot(0,0,45)*Box(8,8,32);knob-=Pos(-L/2-16,-15,0)*Rot(0,0,45)*Box(8,8,32)
 return d+knob
# ---------------- robot cup: Ø70 x 75, 1.5 mm wall, grip band ----------------
def cup():
 c=cylz(35,75)-Pos(0,0,1.5)*cylz(33.5,75);c+=Pos(0,0,30)*(cylz(36.5,18)-cylz(35,18));return c
# ---------------- seasoning station (concept envelopes) ----------------
def station():
 parts={}
 W,D,Hc=800,330,600;t=18
 shell=box(0,W,0,D,0,Hc)-box(t,W-t,-1,D-t,t,Hc-t)          # cabinet carcass (front open)
 parts['cabinet']=shell
 # shelf 1 (z 400): 12 x 500 ml bottles, 2 rows of 6 (Ø72 x 220)
 b=None
 for r in range(2):
  for k in range(6):
   bb=Pos(70+k*110,90+r*130,400)*cylz(36,220);b=bb if b is None else b+bb
 parts['bottles']=b+box(t,W-t,20,D-t,385,400)
 # shelf 2 (z 220): 12 stepper peristaltic pumps (70 x 45 x 50 envelopes) + paste syringes
 p=None
 for r in range(2):
  for k in range(6):
   pp=box(40+k*115,110+k*115,60+r*110,105+r*110,220,270);p=pp if p is None else p+pp
 parts['pumps']=p+box(t,W-t,20,D-t,205,220)
 parts['paste_syringes']=Pos(650,250,40)*cylz(28,150)+Pos(730,250,40)*cylz(28,150)
 # floor level: 4 sealed auger canisters (Ø90 x 160) + 花椒 vibratory feeder
 a=None
 for k in range(4):
  aa=Pos(80+k*120,240,t)*cylz(45,160);a=aa if a is None else a+aa
 parts['augers']=a+box(520,600,200,300,t,80)
 # under the cabinet: nozzle head (Ø70 x 40) and weighing + stirring platform with a cup
 parts['nozzle_head']=Pos(400,90,-40)*cylz(35,40)
 parts['scale_platform']=box(350,450,40,140,-190,-170)+box(390,410,120,190,-190,0)
 parts['cup_on_scale']=Pos(400,90,-170)*cup()
 # cup rack under the cabinet front (8 cups) and a 2-drum cradle
 r=box(470,780,40,140,-260,-250)+box(770,780,40,140,-260,0)
 for k in range(4):r+=Pos(505+k*75,90,-250)*cup()
 parts['cup_rack']=r
 return parts
def staples():
 parts={}
 W,D,Hc=600,330,600;t=18
 parts['cabinet']=box(0,W,0,D,0,Hc)-box(t,W-t,-1,D-t,t,Hc-t)
 # rice hopper 5 kg (V bottom) and flour/starch hopper 2 kg, each with a metering auger to an outlet
 rice=box(40,320,40,300,200,560)+Pos(180,170,100)*Cone(30,120,100,align=(Align.CENTER,Align.CENTER,Align.MIN))
 flour=box(360,560,40,300,260,560)+Pos(460,170,180)*Cone(25,90,80,align=(Align.CENTER,Align.CENTER,Align.MIN))
 parts['rice_hopper']=rice;parts['flour_hopper']=flour
 parts['augers']=box(150,330,150,190,40,100)+box(430,560,150,190,120,170)
 parts['outlets']=Pos(330,90,-30)*cylz(20,60)+Pos(560,90,-30)*cylz(15,40)
 parts['pot_platform']=box(230,430,0,180,-240,-220)+box(420,440,150,200,-240,0)
 return parts
if __name__=='__main__':
 out={'drum':drum(),'cup':cup()}
 for k,v in station().items():out['station_'+k]=v
 for k,v in staples().items():out['staples_'+k]=v
 for n,p in out.items():
  export_stl(p,f'{OUT}/{n}.stl')
  if n in ('drum','cup'):export_step(p,f'{OUT}/{n}.step')
  bb=p.bounding_box();print(n,'bbox',round(bb.size.X),round(bb.size.Y),round(bb.size.Z),'vol cm3',round(p.volume/1000,1),'solids',len(p.solids()))
