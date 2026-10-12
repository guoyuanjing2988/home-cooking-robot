"""R08 scene: unchanged L101 kitchen/rail plus explicitly designed low fixtures.

Distances in metres. Y increases towards the wall. No processor is installed.
Custom station geometry is a design, not a qualified purchased appliance.
"""
from pathlib import Path
import copy,json,xml.etree.ElementTree as E
import numpy as np
from scipy.spatial.transform import Rotation
H=Path(__file__).resolve().parent
ROOT=H.parents[2]
def load(name):return json.loads((H/name).read_text(encoding='utf-8-sig'))
def save(name,value):
 p=H/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2,allow_nan=False,default=lambda x:x.tolist() if isinstance(x,np.ndarray) else x.item()),encoding='utf-8')
def fmt(v):return ' '.join(f'{float(x):.12g}' for x in v)
def box(parent,name,p,size,color=(.55,.62,.66,1)):
 held=name.startswith('R_held_')
 return E.SubElement(parent,'geom',name=name,type='box',pos=fmt(p),size=fmt(np.array(size)/2),rgba=fmt(color),contype='2' if held else '1',conaffinity='3' if held else '2',mass='.000001')
def body(parent,name,p,R=np.eye(3)):
 return E.SubElement(parent,'body',name=name,pos=fmt(p),quat=fmt(Rotation.from_matrix(R).as_quat()[[3,0,1,2]]))
def tray_parts(parent,prefix):
 # One full custom tray definition for both stored and held states. Tool +X
 # faces into the drawer; tool -Y is up. No smaller airborne substitute.
 box(parent,prefix+'tray_handle',[0,0,0],[.060,.030,.024])
 box(parent,prefix+'tray_stem',[.045,.02,0],[.090,.020,.020])
 box(parent,prefix+'tray_floor',[.110,.040,0],[.160,.008,.320])
 for s in [-1,1]:
  box(parent,prefix+'tray_side'+str(s),[.110,.018,s*.157],[.148,.044,.006])
  box(parent,prefix+'tray_end'+str(s),[.110+s*.077,.018,0],[.006,.044,.320])
 for s in [-1,1]:box(parent,prefix+'key_shoulder'+str(s),[s*.036,0,0],[.008,.046,.030])
def vessel(parent,name,p,r=.12,height=.14,tilt=0):
 # Original 240 mm colander dimensions, 2 mm shell. Tilt moves the entire shell.
 R=Rotation.from_euler('x',tilt,degrees=True).as_matrix();b=body(parent,name,p,R)
 E.SubElement(b,'geom',name=name+'_bottom',type='cylinder',pos='0 0 .001',size=fmt([r-.002,.001]),rgba='.42 .6 .7 1',contype='1',conaffinity='2')
 for k in range(32):
  a=k*2*np.pi/32;g=box(b,name+f'_wall{k}',[(r-.001)*np.cos(a),(r-.001)*np.sin(a),height/2],[.002,2*r*np.tan(np.pi/32),height]);g.set('quat',fmt(Rotation.from_euler('z',a).as_quat()[[3,0,1,2]]))
 return b
def variants():
 # Structural changes are cumulative alternatives, not tiny tolerance nudges.
 return [
 dict(id='I01',mand=[.40,.25],yaw=0,peel=[-1.30,.25],wash_tilt=0,wash_z=.72,bowls='rear',approach='top',change='Replace processor with horizontal mandoline; original upright basket centred at the jet.'),
 dict(id='I02',mand=[.40,.16],yaw=0,peel=[-1.30,.25],wash_tilt=0,wash_z=.86,bowls='rear',approach='top',change='Front mandoline corridor and basket above sink rim; test jet-height conflict.'),
 dict(id='I03',mand=[.40,.16],yaw=0,peel=[-1.30,.25],wash_tilt=-45,wash_z=.75,bowls='rear',approach='top',change='Tilt full wash shell 45 degrees into sink; preserve radius and height.'),
 dict(id='I04',mand=[.36,.16],yaw=90,peel=[-1.30,.25],wash_tilt=-45,wash_z=.75,bowls='rear',approach='top',change='Rotate complete mandoline and its 200 mm stroke 90 degrees to use front approach.'),
 dict(id='I05',mand=[.36,.16],yaw=90,peel=[-1.30,.32],wash_tilt=-45,wash_z=.75,bowls='front',approach='front',change='Move complete bowl assemblies to front docks and use side-loading peeler drawer.'),
 dict(id='I06',mand=[-1.32,.17],yaw=0,peel=[.32,.31],wash_tilt=-45,wash_z=.75,bowls='front',approach='front',change='Swap root-processing bays: mandoline on broad left counter; peeler on right.'),
 dict(id='I07',mand=[-1.27,.16],yaw=0,peel=[.38,.38],wash_tilt=-55,wash_z=.745,bowls='spread',approach='front',change='Packing evidence moves all bowls to left rear, peeler right rear, greens left front and wedger right front; correct full raw tray arrangement.'),
 dict(id='I08',mand=[-1.27,.16],yaw=0,peel=[.38,.38],wash_tilt=-55,wash_z=.745,bowls='spread',approach='front',side_wash=True,change='Keep distributed stations; replace vertical wash loading with front-facing approach below spout and shorten peeler entry to its open mouth.'),
 dict(id='I09',mand=[.435,.135],yaw=0,peel=[-1.21,.135],wash_tilt=-55,wash_z=.760,bowls='spread',approach='front',side_wash=True,seated_peel=True,change='Restore legal right-rear park volume. Move full mandoline right-front, P16 left-front, rotate greens fixture 90deg, raise full tilted basket15mm; use horizontal-food side grasp and actual peeler cradle seat.'),
 ]
def build(cfg,held=None,mode='empty'):
 tree=E.parse(H/'models/base.xml');world=tree.find('worldbody')
 # Door sensors move bodily 10 mm wallward for installation reserve; same sizes.
 for g in world.findall('geom'):
  if g.get('name','').startswith('door_pause_sensor'):
   p=np.fromstring(g.get('pos'),sep=' ');p[1]+=.01;g.set('pos',fmt(p))
 # 330 x 120 x 60 mm golden deck; full 65 mm RADIUS holder used in held model.
 mp=np.array([*cfg['mand'],.85]);R=Rotation.from_euler('z',cfg['yaw'],degrees=True).as_matrix()
 mb=body(world,'mandoline_station',mp,R)
 # Full deck is conservative; food/deck working contact is declared explicitly.
 box(mb,'mandoline_deck',[0,0,.08],[.330,.120,.060],(.25,.45,.62,1))
 for side in [-1,1]:
  box(mb,f'mandoline_guard{side}',[0,side*.095,.09],[.370,.010,.180])
  box(mb,f'mandoline_foot{side}',[side*.135,0,.025],[.035,.170,.050])
 box(mb,'mandoline_blade',[0,0,.112],[.001,.120,.004],(.8,.8,.8,1))
 # Pull-out catch tray: distinct actual hollow food region under deck, front outlet.
 if held!='catch_tray':
  tray=body(mb,'stored_catch_tray',[0,-.110,.044],np.array([[0,0,-1],[1,0,0],[0,-1,0]]))
  tray_parts(tray,'stored_')
 pp=np.array([*cfg['peel'],.85]);pb=body(world,'peeler_station',pp)
 # OEM P16 cover and separate guide retain full R07 dimensions.
 box(pb,'P16_drive',[0,.095,.10],[.480,.050,.050])
 box(pb,'P16_guide',[0,.040,.075],[.360,.035,.025])
 box(pb,'peel_drawer_floor',[0,-.045,.009],[.310,.180,.018])
 for side in [-1,1]:
  box(pb,f'peel_cradle{side}',[side*.07,-.045,.045],[.016,.055,.072])
  box(pb,f'peel_guard_side{side}',[side*.19,-.01,.09],[.006,.220,.180])
 box(pb,'peel_guard_back',[0,.125,.09],[.386,.006,.180])
 box(pb,'peel_guard_roof',[0,-.01,.183],[.386,.226,.006])
 # Open front door slides laterally within its own floor-level pocket, no raised lid.
 box(pb,'peel_door_pocket',[.24,-.12,.09],[.090,.008,.180])
 tool=copy.deepcopy(E.parse(H/'assets/components.xml').find("body[@name='linear_peeler_cutter']"))
 if tool is not None:tool.set('pos','0 -.045 .09');tool.attrib.pop('quat',None);pb.append(tool)
 # Remaining low fixtures, included while solving carrot (no later scene swaps).
 late=int(cfg['id'][1:])>=7
 gb=body(world,'greens_station',[-.835,.16,.85] if cfg['id']=='I09' else [-.935,.15,.85] if late else [-1.00,.38,.85],Rotation.from_euler('z',90,degrees=True).as_matrix() if cfg['id']=='I09' else np.eye(3))
 box(gb,'greens_base',[0,0,.01],[.260,.210,.020])
 box(gb,'greens_blade_guard',[0,.09,.095],[.260,.012,.190])
 box(gb,'greens_guillotine',[0,0,.13],[.002,.160,.090],(.5,.65,.5,1))
 box(gb,'greens_split_comb',[.09,0,.045],[.020,.160,.070])
 tb=body(world,'tomato_station',[.015,.14,.85] if late else [-.82,.14,.85])
 box(tb,'wedger_base',[0,0,.01],[.200,.200,.020])
 for s in [-1,1]:box(tb,f'wedger_guard{s}',[s*.093,0,.075],[.010,.200,.150])
 box(tb,'wedger_pusher',[0,0,.14],[.075,.075,.025])
 box(tb,'wedger_lever',[0,-.025,.18],[.025,.250,.025])
 # Eight radial cutting sectors: four complete diametral blades.
 for a in range(4):
  g=box(tb,f'wedger_blade{a}',[0,0,.065],[.10,.000952,.020],(.7,.7,.7,1));g.set('quat',fmt(Rotation.from_euler('z',a*45,degrees=True).as_quat()[[3,0,1,2]]))
 # Bowl shells/bails copied whole; offsets rigidly transform original global frames.
 centers={'rear':[[-1.65,.40],[-1.05,.43],[.06,.44],[.45,.44]],'front':[[-1.65,.14],[-1.04,.15],[.06,.15],[.45,.15]],'spread':[[-1.67,.46],[-1.40,.46],[-1.13,.46],[-.86,.46]]}[cfg['bowls']]
 old=E.parse(H/'assets/components.xml')
 for index,b in enumerate(old.findall('body')[:4]):
  b=copy.deepcopy(b);p=np.fromstring(b.get('pos'),sep=' ')
  # I01-I04 retain the provisional frame placement exposed by the packing
  # audit. I05 onward use measured shell-bottom centres from full source FK.
  source_x=[-1.69,-1.445,-1.18,.04] if int(cfg['id'][1:])>=5 else [-1.69,-1.16,.05,.47]
  b.set('pos',fmt(p+np.array([centers[index][0]-source_x[index],centers[index][1]-.452,0])))
  world.append(b)
 # Basket mouth lies exactly on jet XY even when tilted: its bottom follows R*z.
 tilt=cfg['wash_tilt'];wr=Rotation.from_euler('x',tilt,degrees=True).as_matrix()
 mouth=np.array([-.58,.43,cfg['wash_z']+.14*np.cos(np.deg2rad(tilt))]);bottom=mouth-wr@np.array([0,0,.14])
 vessel(world,'wash_basket',bottom,tilt=tilt)
 box(world,'raw_tray',[-1.625,.19,.859] if late else [-1.65,.17,.856],[.320,.300,.018] if late else [.260,.240,.012],(.5,.6,.4,1))
 raw=[('carrot',[-1.69,.12,.8855],[.16,.035,.035]),('potato',[-1.515,.12,.903],[.09,.065,.07]),('greens',[-1.68,.265,.903],[.17,.10,.07]),('tomato',[-1.515,.27,.898],[.07,.07,.06])] if late else [('carrot',[-1.65,.12,.90],[.16,.035,.035]),('potato',[-1.68,.22,.90],[.09,.065,.07]),('greens',[-1.57,.29,.92],[.17,.10,.07]),('tomato',[-1.56,.10,.90],[.07,.07,.06])]
 for index,(name,p,size) in enumerate(raw):
  if held!=name:box(world,'raw_'+name,p,size,(.85,.4+.1*index,.15,1))
 if held:
  rb=tree.find(".//body[@name='R_tool']")
  if held=='holder':
   E.SubElement(rb,'geom',name='R_held_holder',type='sphere',pos='.055 0 0',size='.065',rgba='.9 .5 .15 1',mass='0.000001',contype='2',conaffinity='3')
  elif held=='catch_tray':
   tray_parts(rb,'R_held_')
  else:box(rb,'R_held_'+held,[0,0,0],{'carrot':[.035,.035,.16],'potato':[.07,.065,.09],'greens':[.07,.10,.17],'tomato':[.06,.07,.07]}[held],(.9,.4,.1,1))
  if held=='holder':
   for s in [-1,1]:box(rb,'R_held_key_shoulder'+str(s),[s*.036,0,0],[.008,.046,.030])
 E.indent(tree)
 return tree,dict(mandoline_origin=mp.tolist(),mandoline_rotation=R.tolist(),peeler_origin=pp.tolist(),wash_bottom=bottom.tolist(),wash_mouth=mouth.tolist(),wash_normal=(wr@np.array([0,0,1])).tolist(),jet=[-.58,.43,.91],held=held,mode=mode,raw_objects={n:dict(position=p,size=s,support='raw_tray') for n,p,s in raw})
def targets(cfg,meta):
 mp=np.array(meta['mandoline_origin']);R=np.array(meta['mandoline_rotation']);pp=np.array(meta['peeler_origin'])
 # Tool approach +X, jaw local -Y: same reference rotation function in checker.
 out=[]
 def add(name,points,held=None,approach=(0,0,-1),force=None,kind='transfer'):
  out.append(dict(name=name,points=np.asarray(points).tolist(),held=held,approach=list(approach),force=force,kind=kind))
 add('raw_pick',[[-1.69,.12,.8855],[-1.69,.12,.9255]] if int(cfg['id'][1:])>=7 else [[-1.65,.12,.90],[-1.65,.12,.94]],'carrot')
 if cfg.get('side_wash'):add('wash_load',[np.array(meta['wash_mouth'])+[0,-.14,-.005],np.array(meta['wash_mouth'])+[0,-.10,-.005]],'carrot',approach=(0,1,0))
 else:add('wash_load',[np.array(meta['wash_mouth'])+[0,-.04,.10],np.array(meta['wash_mouth'])+[0,-.04,.06]],'carrot')
 add('wash_work',[np.array(meta['wash_mouth'])+[0,-.04,.06],np.array(meta['wash_mouth'])+[.025,-.04,.06]],'carrot',force=[9.191,0,0],kind='working')
 if cfg['approach']=='top':points=[pp+[0,-.045,.17],pp+[0,-.045,.09]];approach=[0,0,-1]
 else:points=[pp+[0,-.22,.085],pp+[0,-.18,.085]];approach=[0,1,0]
 if cfg.get('seated_peel'):points=[pp+[0,-.085,.0895],pp+[0,-.045,.0895]]
 add('peel_load',points,'carrot',approach)
 add('peel_retrieve',points[::-1],'carrot',approach)
 add('holder_load',[mp+R@[-.10,0,.23],mp+R@[-.10,0,.19]],'carrot')
 add('mandoline_work',[mp+R@[-.10,0,.19],mp+R@[.10,0,.19]],'holder',force=(R@[-60,10,20]).tolist(),kind='working')
 add('holder_retreat',[mp+R@[.10,0,.19],mp+R@[.10,0,.26]],'holder')
 add('catch_tray_pick',[mp+R@[0,-.11,.044],mp+R@[0,-.15,.044]],'catch_tray',approach=(0,1,0))
 add('bowl_deliver',[[-1.67,.12,1.09],[-1.67,.12,1.05]],'catch_tray')
 add('scrap_service',[pp+[0,-.18,.04],pp+[0,-.22,.04]],'catch_tray',approach=(0,1,0))
 return out
