"""Dimensioned plan from the same JSON; raster artifact at1500x840 pixels."""
from pathlib import Path
import json, math
from PIL import Image, ImageDraw, ImageFont
R=Path(__file__).resolve().parents[1]
p=json.loads((R/'results/process_v2.json').read_text(encoding='utf-8'))
im=Image.new('RGB',(1500,840),'#f7f9fb');d=ImageDraw.Draw(im)
fontpath='C:/Windows/Fonts/arial.ttf'
def f(n):return ImageFont.truetype(fontpath,n)
def text(x,y,s,n=20,color='#223044'):d.text((x,y),s,font=f(n),fill=color)
scale=400
def xy(x,y):return (70+(x+1.85)*scale,500-y*scale)
def rect(bounds,fill,outline='#566579',width=2):
    a,b=xy(bounds[0][0],bounds[1][1]),xy(bounds[0][1],bounds[1][0]);d.rectangle([a,b],fill,outline,width=width)
text(65,40,'R02 | One guarded cutting cell + passive food fixtures',34)
text(65,92,'Counter frame: metres; world Z = counter Z +0.850.  Front edge Y=0.  Cabinet underside Z=0.500.',20)
text(65,127,'Fixed appliance: 150 W supply; all other prep implements passive. Arm/rail drives are outside this BOM.',20)
text(65,165,'Solid footprints include bowl bails and opened door sweep. No rail geometry or arm path clearance is implied.',18,'#657487')
for name,b,col in [('left',[[-1.8,-.7],[0,.6]],'#e3dfd3'),('sink',[[-.7,-.11],[0,.6]],'#d8e9ef'),('right',[[-.11,.69],[0,.6]],'#e3dfd3'),('stove',[[.69,1.47],[0,.6]],'#e7d1d0')]:
    rect(b,col); x,y=xy((b[0][0]+b[0][1])/2,.62);text(x-35,y-10,name.upper(),16)
for x in [-1.8,-.7,-.11,.69,1.47]:
    a=xy(x,0);d.line([a,(a[0],a[1]+10)],'#566579',2);text(a[0]-22,a[1]+16,f'{x:.2f}',16)
for y in [0,.3,.6]:
    a=xy(-1.85,y);text(8,a[1]-8,f'{y:.2f}',16)
colors={'guarded_cutter':'#9bd4d3','peel_fixture':'#eab37a','tool_dock':'#b9cbbb','sink_insert':'#a4bfd6'}
names={'raw_tray':'RAW','drain_colander':'DRAIN','peel_fixture':'PEEL + BIN','tool_dock':'TOOL\nDOCK','guarded_cutter':'CUTTING\nCELL','sink_insert':'WASH'}
for a in p['counter_layout']:
    b=a['bounds_counter_m'];rect(b,colors.get(a['id'],'#c3d8e8'))
    x,y=xy(*a['center_xy_m']);name=names.get(a['id'],a['id'].replace('output_','').replace('leafy_greens','GREENS').upper())
    lines=name.split('\n')
    for i,s in enumerate(lines):
        n=13 if a['id'].startswith('output_') else 15
        length=d.textlength(s,font=f(n));text(x-length/2,y-9+19*i,s,n)
for door in p['moving_geometry_states']['front_doors']:
    b=door['sweep_bounds_m'];rect(b,None,'#bd544f',2)
    x,y=xy(*door['hinge_counter_m'][:2]);d.ellipse((x-3,y-3,x+3,y+3),fill='#bd544f')
for x in [-.9,.15]:
    a,b=xy(x-.05,.60),xy(x+.05,.52);d.rectangle([a,b],outline='#774d96',width=3)
x,y=xy(-.4,.56);d.ellipse((x-10,y-10,x+10,y+10),fill='#45758b')
text(x-25,y+14,'faucet',14,'#34556a')
text(65,556,'Layout checks',25)
text(65,597,'25 mm minimum gap between reserved station footprints.  Cutting cell X=0.15...0.65, Y=0.01...0.56.',20)
text(65,634,'Actual fixed cell top Z=0.375: 125 mm below cabinets/door sweeps.  Stove keep-out starts X=0.69.',20)
text(65,671,'Purple: representative outlet access.  Red: front cutting-cell door sweeps.  Sink insert stays at existing sink.',20)
text(65,714,'Food path: dirty raw tray -> supported wash/peel -> covered cartridge -> same next-step bowl -> rear parking.',20)
text(65,757,'Concept CAD; matched vendor datums, supported loading handoff, hygiene and paired-arm IK remain qualification gates.',18,'#9b4c35')
im.save(R/'renders/layout_plan.png')
print('PLAN_DONE1500x840')
