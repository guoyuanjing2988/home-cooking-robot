"""R09 scene: complete inherited kitchen/arm with mobile cart and low stations.

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
 return [dict(id='I09',trial=f'M{i+1:02d}',mount_height=h,mand=mp,yaw=yaw,peel=pp,wash_tilt=-55,wash_z=.760,bowls='spread',approach='front',side_wash=True,seated_peel=True,front_grasp=front,change=change) for i,(h,mp,yaw,pp,front,change) in enumerate([
 (.70,[.435,.135],0,[-1.21,.135],False,'Low fixed .70m mount; inherited full low stations.'),
 (.85,[.435,.135],0,[-1.21,.135],False,'Raise fixed mount to counter height .85m; remove wall-oriented approach constraint.'),
 (1.00,[.435,.135],0,[-1.21,.135],False,'Fixed 1.00m mount for sink/above-counter reach tradeoff.'),
 (1.15,[.435,.135],0,[-1.21,.135],False,'Fixed 1.15m mount tests elbow clearance versus shorter low cart.'),
 (.85,[.435,.135],0,[-1.21,.135],True,'Side grasp raw carrot and mandoline loading from front; full food unchanged.'),
 (.85,[.435,.135],90,[-1.21,.135],True,'Rotate full mandoline 90deg to align feed from aisle.'),
 (.95,[.435,.135],0,[-1.21,.185],True,'Raise mount .95m; shift full peeler 50mm rearward to open front approach.'),
 (.80,[.435,.135],0,[-1.21,.135],True,'Lower fixed mount .80m with front food approach; prioritize parking and sink access.')])]

# Lever cutter pusher at rest, station-local (name, centre, full size); knob centre
# is the grasp point. Pusher bottom at rest .232 (48 mm above a 60 mm tomato on
# the .124 plate top); pressed by .102 its bottom stops 6 mm above the plate.
LEVER_PUSHER=[('lever_pusher',[0,0,.2445],[.11,.11,.025]),('lever_pusher_stem',[0,0,.287],[.02,.02,.06]),('lever_pusher_knob',[0,0,.332],[.03,.05,.03])]
LEVER_KNOB=[0,0,.332];LEVER_PRESS=.102
def tomato_geom(parent,name,p):
 # R11 tomato: vertical cylinder, 70 mm diameter x 60 mm (round produce; avoids
 # MuJoCo's under-reported box-box distances inside the contact margin).
 held=name.startswith('R_held_')
 return E.SubElement(parent,'geom',name=name,type='cylinder',pos=fmt(p),size='.035 .03',rgba='.9 .3 .2 1',contype='2' if held else '1',conaffinity='3' if held else '2',mass='.000001')
def pusher_disc(parent,name,p,quat):
 # Round 110 mm pusher disc (as on real 8-wedge tomato cutters), 25 mm thick.
 held=name.startswith('R_held_');g=E.SubElement(parent,'geom',name=name,type='cylinder',pos=fmt(p),size='.055 .0125',rgba='.6 .6 .65 1',contype='2' if held else '1',conaffinity='3' if held else '2',mass='.000001')
 if quat:g.set('quat',quat)
 return g
TOMATO_DZ=.02  # tomato is gripped 20 mm above its centre (body clears the plate)
def tomato_dz(cfg):
 # R12 finger designs grip the tomato at its equator (the finger crank lifts the housing).
 return cfg.get('tomato_dz',TOMATO_DZ)
def lever_pusher(cfg):
 dz=cfg.get('lever_dz',0.);return [(n,[p[0],p[1],p[2]+dz],sz) for n,p,sz in LEVER_PUSHER]
def lever_knob(cfg):return [LEVER_KNOB[0],LEVER_KNOB[1],LEVER_KNOB[2]+cfg.get('lever_dz',0.)]
def plate_top(cfg):return .124+cfg.get('lever_dz',0.)
def build(cfg,held=None,mode='empty'):
 tree=E.parse(H/'models/base.xml');world=tree.find('worldbody')
 height=cfg.get('mount_height',.85)
 mount=tree.find(".//body[@name='R_mount']");mount.set('pos',fmt([0,0,height]))
 mount.set('quat',fmt(Rotation.from_euler('x',cfg.get('mount_tilt_deg',0),degrees=True).as_quat()[[3,0,1,2]]))
 mast=tree.find(".//geom[@name='R_cart_mast']");bottom=.553;top=height-.024
 mast.set('pos',fmt([0,0,(bottom+top)/2]));mast.set('size',fmt([.06,.06,(top-bottom)/2]))
 if cfg.get('dock'):
  # R10 docked cart (orchestrator design): no ballast, controller off-board
  # (wall-side, tethered), two ZLTECH drive wheels + two casters, mast at the
  # cart front, and a named dock bumper that bears on the base-cabinet fronts.
  cart=tree.find(".//body[@name='rail_structure']")
  for g in list(cart.findall('geom')):
   if g.get('name') in ('R_cart_ballast','R_cart_controller') or g.get('name','').startswith('R_cart_wheel_'):cart.remove(g)
  cart.find("joint[@name='base_y']").set('range','-.60 -.20')
  ch_=cart.find("geom[@name='R_cart_chassis']");ch_.set('pos','0 -.05 .14' if cfg.get('deep_cart') else '0 0 .14');ch_.set('size','.30 .25 .05' if cfg.get('deep_cart') else '.30 .20 .05');ch_.set('mass','14' if cfg.get('deep_cart') else '12')
  dwy=-.22 if cfg.get('deep_cart') else -.10
  el=cart.find("geom[@name='R_cart_electrics']");el.set('pos','0 -.10 .225');el.set('size','.15 .06 .035');el.set('mass','3')
  for x in (-.22,.22):
   E.SubElement(cart,'geom',name=f'R_cart_wheel_drive_{x:+.2f}',type='cylinder',pos=fmt([x,dwy,.0825]),size='.0835 .0445',quat='.707106781187 .707106781187 0 0',mass='4.85',rgba='.08 .08 .08 1',contype='2',conaffinity='3')
   E.SubElement(cart,'geom',name=f'R_cart_wheel_caster_{x:+.2f}',type='cylinder',pos=fmt([x,.11,.05]),size='.05 .02',quat='.707106781187 .707106781187 0 0',mass='1.5',rgba='.08 .08 .08 1',contype='2',conaffinity='3')
  E.SubElement(cart,'geom',name='R_dock_bumper',type='box',pos='0 .205 .30',size='.28 .005 .05',mass='.5',rgba='.9 .2 .2 1',contype='2',conaffinity='3')
  my=cfg.get('mount_y',.12);bottom=.19
  if cfg.get('cantilever'):
   # Mast stays at the cart centre; a forward beam carries the arm base so the
   # space below/in front of the arm is clear of structure.
   top=height-.065
   mb_=cfg.get('mast_y',-.05)
   mast.set('pos',fmt([0,mb_,(bottom+top)/2]));mast.set('size',fmt([.05,.05,(top-bottom)/2]));mast.set('mass','4')
   E.SubElement(cart,'geom',name='R_cart_beam',type='box',pos=fmt([0,(my+mb_)/2,top+.025]),size=fmt([.045,(my-mb_)/2,.025]),mass='2.5',rgba='.2 .3 .4 1',contype='2',conaffinity='3')
  else:
   mast.set('pos',fmt([0,my,(bottom+top)/2]));mast.set('size',fmt([.06,.06,(top-bottom)/2]));mast.set('mass','5')
  mount.set('pos',fmt([0,my,height]))
 fo=cfg.get('finger_offset',0.)
 if fo:
  # R11 3D-printed finger pads: each finger moved outward by fo, so the 50 mm
  # actuator stroke spans an opening of 2*fo .. 2*fo+50 mm (fo=15 mm: 30-80 mm).
  for n_,sg in (('R_finger_minus',-1),('R_finger_plus',1)):
   g_=tree.find(f".//geom[@name='{n_}']");p_=np.fromstring(g_.get('pos'),sep=' ');p_[1]+=sg*fo;g_.set('pos',fmt(p_))
 # Full buyable PGC-140-50 housing envelope, in addition to inherited fingers.
 # Custom flange adapter orientation remains a design assumption.
 box(tree.find(".//body[@name='R_tool']"),'R_gripper_oem_envelope',[-.10425,0,0],[.1385,.075,.075],(.15,.2,.25,1)).set('contype','2')
 tree.find(".//geom[@name='R_gripper_oem_envelope']").set('conaffinity','3')
 if cfg.get('finger'):
  import fingers;fingers.apply(tree,cfg)
 if cfg.get('verified_wheels'):
  # Four driven wheels. Full OEM motor housing and stationary inward spindle,
  # not a narrow tyre-only proxy. Outside +/-0.3235m fits 660mm bumper outline.
  cart=tree.find(".//body[@name='rail_structure']")
  for g in cart.findall('geom'):
   if g.get('name','').startswith('R_cart_wheel_'):
    g.set('size','.0835 .0445');g.set('mass','4.85')
    p=np.fromstring(g.get('pos'),sep=' ');s=np.sign(p[1]);p[1]=s*.13475
    E.SubElement(cart,'geom',name=g.get('name')+'_spindle',type='cylinder',pos=fmt(p),size='.012 .021',quat='.707106781187 .707106781187 0 0',mass='.000001',contype='2',conaffinity='3',rgba='.4 .4 .4 1')
 if cfg.get('long_spout'):
  for g in world.findall('geom'):
   n=g.get('name','')
   if n=='faucet_v3_fixed_spout_full_envelope':g.set('pos',fmt([-.58,.465,1.00]));g.set('size',fmt([.03,.135,.03]))
   if n=='faucet_v3_wall_bracket_mating':g.set('pos',fmt([-.58,.596,1.00]))
   if n=='faucet_v3_concealed_thread_and_connector':g.set('pos',fmt([-.58,.645,1.00]))
 # Reel outside the assumed counter end and guarded toe channel (no floor loop).
 box(world,'reel_case',[2.52,.15,.45],[.48,.14,.32],(.8,.7,.12,1))
 box(world,'floor_cable_guide',[.50,-.025,.015],[4.60,.030,.030],(.8,.7,.12,1))
 # Door sensors move bodily 10 mm wallward for installation reserve; same sizes.
 for g in world.findall('geom'):
  if g.get('name','').startswith('door_pause_sensor'):
   p=np.fromstring(g.get('pos'),sep=' ');p[1]+=.01;g.set('pos',fmt(p))
 # 330 x 120 x 60 mm golden deck; full 65 mm RADIUS holder used in held model.
 present=cfg.get('present')
 has=lambda n:present is None or n in present
 raise_=cfg.get('mand_raise',0.)
 mp=np.array([*cfg['mand'],.85+raise_]);R=Rotation.from_euler('z',cfg['yaw'],degrees=True).as_matrix()
 mb=body(world if has('mandoline') and not cfg.get('no_mand') else E.Element('body'),'mandoline_station',mp,R)
 if raise_:
  # Legs carry the golden deck so the carrot output bowl sits directly under the blade.
  legs=cfg.get('mand_legs') or [-cfg.get('mand_leg',.135),cfg.get('mand_leg',.135)]
  for k,lx in enumerate(legs):box(mb,f'mandoline_leg{2*k-1}',[lx,0,(.05-raise_)/2],[.035,.170,raise_+.05])
  bo=np.array([mp[0],mp[1],.851])+R@np.array([cfg.get('bowl_dx',0.),0,0])
  if not cfg.get('no_mand'):vessel(world,'carrot_out_bowl',bo,r=cfg.get('bowl_r',.095),height=.09)
 # Full deck is conservative; food/deck working contact is declared explicitly.
 box(mb,'mandoline_deck',[0,0,.08],[.330,.120,.060],(.25,.45,.62,1))
 for side in [-1,1]:
  box(mb,f'mandoline_guard{side}',[0,side*.095,.09],[.370,.010,.180])
  box(mb,f'mandoline_foot{side}',[side*.135,0,.025],[.035,.170,.050])
 box(mb,'mandoline_blade',[0,0,.112],[.001,.120,.004],(.8,.8,.8,1))
 # Pull-out catch tray: distinct actual hollow food region under deck, front outlet.
 if held!='catch_tray' and not raise_:
  tray=body(mb,'stored_catch_tray',[0,-.110,.044],np.array([[0,0,-1],[1,0,0],[0,-1,0]]))
  tray_parts(tray,'stored_')
 chute_top=None
 if cfg.get('slicer'):
  # R11 counter-resident electric slicer/dicer (卓晋 3-in-1 class, 21x33x28 cm,
  # 10x7 cm top chute, lid interlock). Body long axis along x; chute near the -x
  # end, discharge from the +x face into a bowl. Internals (disc, pusher) are an
  # appliance-contained transformation; the arm only drops produce into the chute.
  sp=np.array([*cfg['slicer'],.85]);sb=body(world if has('slicer') else E.Element('body'),'slicer_station',sp)
  box(sb,'slicer_base',[0,0,.10],[.33,.21,.20],(.85,.85,.82,1))
  cx=-.08
  for s_ in [-1,1]:
   box(sb,f'slicer_chute_wall_y{s_}',[cx,s_*(.035+.003),.24],[.112,.006,.08],(.7,.75,.8,1))
   box(sb,f'slicer_chute_wall_x{s_}',[cx+s_*(.05+.003),0,.24],[.006,.07,.08],(.7,.75,.8,1))
  box(sb,'slicer_spout',[.165+.03,0,.12],[.06,.10,.04],(.7,.75,.8,1))
  vessel(world,'slicer_out_bowl',sp+[.165+.11,0,.001],r=.085,height=.09)
  chute_top=(sp+[cx,0,.28]).tolist()
 lever_origin=None
 if cfg.get('lever_base'):
  # R11 fetched lever cutter base (AY-403 class, 8-wedge plate). Produce rests on
  # the blade plate; a guided pusher (spring-held at rest, no contact) is pushed
  # straight down by the arm through the plate; wedges fall into the bin below.
  lever_origin=np.array([*cfg['lever_base'],.85]);lb=body(world if has('lever') else E.Element('body'),'lever_station',lever_origin)
  box(lb,'lever_base_plate',[0,cfg.get('lever_plate_dy',.02),.006],[.22,.26,.012],(.75,.75,.78,1))
  dz=cfg.get('lever_dz',0.)
  box(lb,'lever_blade_plate',[0,0,.12+dz],[.13,.13,.008],(.8,.8,.85,1))
  for s_ in [-1,1]:
   box(lb,f'lever_plate_leg{s_}',[s_*.071,0,.064+dz/2],[.012,.13,.104+dz],(.75,.75,.78,1))
   box(lb,f'lever_rail{s_}',[s_*.075,.045,.274+dz/2],[.012,.012,.30+dz],(.6,.6,.65,1))
  box(lb,'lever_bin_back',[0,.07,.06+dz/2],[.13,.006,.096+dz],(.7,.7,.72,1))
  if held!='pusher':
   for n_,dp,sz in lever_pusher(cfg):
    if n_=='lever_pusher':pusher_disc(lb,n_,dp,None)
    else:box(lb,n_,dp,sz,(.6,.6,.65,1))
 pp=np.array([*cfg['peel'],.85]);pb=body(world if has('peeler') else E.Element('body'),'peeler_station',pp)
 # OEM P16 cover and separate guide retain full R07 dimensions.
 box(pb,'P16_drive',[0,.095,.10],[.480,.050,.050])
 box(pb,'P16_guide',[0,.040,.075],[.360,.035,.025])
 fwd=cfg.get('peel_fwd')
 box(pb,'peel_drawer_floor',[0,-.025,.009] if fwd else [0,-.045,.009],[.310,.140,.018] if fwd else [.310,.180,.018])
 for side in [-1,1]:
  box(pb,f'peel_cradle{side}',[side*.07,-.045,.045],[.016,cfg.get('cradle_d',.055),.072])
  box(pb,f'peel_guard_side{side}',[side*.19,0,.09] if fwd else [side*.19,-.01,.09],[.006,.200 if fwd else .220,.180])
 box(pb,'peel_guard_back',[0,.125,.09],[.386,.006,.180])
 if cfg.get('peel_top') or cfg.get('peel_open'):
  # Open-top cradle: the arm loads from above; the station lid is hinged open
  # (vertical, behind the back guard) and the cutter parks raised at the left end.
  box(pb,'peel_lid_open',[0,.134,.293],[.386,.006,.226])
 else:
  box(pb,'peel_guard_roof',[0,-.01,.183],[.386,.226,.006])
  # Open front door slides laterally within its own floor-level pocket, no raised lid.
  box(pb,'peel_door_pocket',[.24,-.12,.09],[.090,.008,.180])
 tool=copy.deepcopy(E.parse(H/'assets/components.xml').find("body[@name='linear_peeler_cutter']"))
 if tool is not None:tool.set('pos','-.155 -.045 .15' if (cfg.get('peel_top') or cfg.get('peel_open')) else '0 -.045 .09');tool.attrib.pop('quat',None);pb.append(tool)
 # Remaining low fixtures, included while solving carrot (no later scene swaps).
 late=int(cfg['id'][1:])>=7
 gb=body(world if has('greens') else E.Element('body'),'greens_station',[-.835,.16,.85] if cfg['id']=='I09' else [-.935,.15,.85] if late else [-1.00,.38,.85],Rotation.from_euler('z',90,degrees=True).as_matrix() if cfg['id']=='I09' else np.eye(3))
 box(gb,'greens_base',[0,0,.01],[.260,.210,.020])
 box(gb,'greens_blade_guard',[0,.09,.095],[.260,.012,.190])
 box(gb,'greens_guillotine',[0,0,.13],[.002,.160,.090],(.5,.65,.5,1))
 box(gb,'greens_split_comb',[.09,0,.045],[.020,.160,.070])
 tb=body(world if has('tomato') else E.Element('body'),'tomato_station',[*cfg['tomato'],.85] if cfg.get('tomato') else [.015,.14,.85] if late else [-.82,.14,.85])
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
  if index==0 and cfg.get('mand_raise'):continue
  b=copy.deepcopy(b);p=np.fromstring(b.get('pos'),sep=' ')
  # I01-I04 retain the provisional frame placement exposed by the packing
  # audit. I05 onward use measured shell-bottom centres from full source FK.
  source_x=[-1.69,-1.445,-1.18,.04] if int(cfg['id'][1:])>=5 else [-1.69,-1.16,.05,.47]
  b.set('pos',fmt(p+np.array([centers[index][0]-source_x[index],centers[index][1]-.452,0])))
  world.append(b)
 # Basket mouth lies exactly on jet XY even when tilted: its bottom follows R*z.
 tilt=cfg['wash_tilt'];wr=Rotation.from_euler('x',tilt,degrees=True).as_matrix()
 mouth=np.array([-.58,.43,cfg['wash_z']+.14*np.cos(np.deg2rad(tilt))]);bottom=mouth-wr@np.array([0,0,.14])
 if cfg.get('upright_basket'):
  tilt=0;wr=np.eye(3);bottom=np.array([-.55,.36,.670]);mouth=bottom+[0,0,.14]
 vb=vessel(world,'wash_basket',bottom,tilt=tilt)
 if cfg.get('upright_basket'):
  # Three physical pads join the actual sink floor to the basket bottom.
  for i,(x,y) in enumerate([[-.055,-.035],[.055,-.035],[0,.065]]):box(vb,f'wash_cradle_pad{i}',[x,y,-.010],[.025,.025,.020],(.3,.3,.3,1))
 rx=cfg.get('raw_shift',0.)
 rib=cfg.get('rib_tray')
 box(world,'raw_tray',[-1.625+rx,.19,.859] if late else [-1.65,.17,.856],[.320,.300,.018] if late else [.260,.240,.012],(.5,.6,.4,1))
 raw=[('carrot',[-1.69+rx,.12,.8855],[.16,.035,.035]),('potato',[-1.515+rx,.12,.903],[.09,.065,.07]),('greens',[-1.68+rx,.265,.903],[.17,.10,.07]),('tomato',[-1.515+rx,.27,.898],[.07,.07,.06])] if late else [('carrot',[-1.65,.12,.90],[.16,.035,.035]),('potato',[-1.68,.22,.90],[.09,.065,.07]),('greens',[-1.57,.29,.92],[.17,.10,.07]),('tomato',[-1.56,.10,.90],[.07,.07,.06])]
 if rib and late:
  cx,cy=-1.69+rx,.12
  for side in [-1,1]:box(world,f'raw_rib{side}',[cx+side*.07,cy,.868+.0225],[.016,.055,.045],(.4,.5,.35,1))
  raw[0]=('carrot',[cx,cy,.868+.045+.0175],[.16,.035,.035])
 if cfg.get('r11_tomato'):
  # R11: tomato on a 3D-printed 45 mm pad at the tray front (front grasp, jaws
  # horizontal, gripper envelope clear of the tray); the potato is not on the tray.
  tx,ty=cfg.get('tomato_raw',[-1.245,.12])
  box(world,'raw_pad_tomato',[tx,ty,.868+.0225],[.05,.05,.045],(.4,.5,.35,1))
  raw[3]=('tomato',[tx,ty,.868+.045+.03],[.07,.07,.06])
 for index,(name,p,size) in enumerate(raw):
  if name in cfg.get('raw_absent',[]):continue
  if name=='carrot' and cfg.get('carrot_at') is not None:p=list(cfg['carrot_at'])
  if name=='tomato' and cfg.get('tomato_at') is not None:p=list(cfg['tomato_at'])
  if name=='tomato' and cfg.get('tomato_gone'):continue
  if held!=name:
   if name=='tomato' and cfg.get('r11_tomato'):tomato_geom(world,'raw_tomato',p)
   else:box(world,'raw_'+name,p,size,(.85,.4+.1*index,.15,1))
 if held:
  rb=tree.find(".//body[@name='R_tool']")
  if held=='holder':
   E.SubElement(rb,'geom',name='R_held_holder',type='sphere',pos='.055 0 0',size='.065',rgba='.9 .5 .15 1',mass='0.000001',contype='2',conaffinity='3')
  elif held=='catch_tray':
   tray_parts(rb,'R_held_')
  elif held=='pusher':
   # Guided pusher of the lever cutter, grasped at its knob from above (approach
   # -z, jaws along x): tool axes x=-z, y=-x, z=+y world, so a world offset
   # (dx,dy,dz) is (-dz,-dx,dy) and a world box (sx,sy,sz) is (sz,sx,sy) in tool.
   front=cfg.get('press_front')
   for n_,dp,sz in lever_pusher(cfg):
    d_=np.array(dp)-np.array(lever_knob(cfg))
    if front:
     # Front grasp (approach +y, jaw +x): tool x=+y, y=-x, z=+z world, so a
     # world offset (dx,dy,dz) is (dy,-dx,dz) and a box (sx,sy,sz) is (sy,sx,sz).
     lp=[d_[1],-d_[0],d_[2]]
     if n_=='lever_pusher':pusher_disc(rb,'R_held_'+n_,lp,None)
     else:box(rb,'R_held_'+n_,lp,[sz[1],sz[0],sz[2]],(.6,.6,.65,1))
    else:
     lp=[-d_[2],-d_[0],d_[1]]
     # Disc axis = world z = tool -x: rotate the cylinder's local z onto tool x.
     if n_=='lever_pusher':pusher_disc(rb,'R_held_'+n_,lp,'.707106781187 0 .707106781187 0')
     else:box(rb,'R_held_'+n_,lp,[sz[2],sz[0],sz[1]],(.6,.6,.65,1))
  else:box(rb,'R_held_'+held,[0,0,0],{'carrot':[.035,.035,.16],'potato':[.07,.065,.09],'greens':[.07,.10,.17],'tomato':[.07,.07,.06] if cfg.get('r11_tomato') else [.06,.07,.07]}[held],(.9,.4,.1,1))
  if held=='tomato' and cfg.get('r11_tomato'):
   g_=tree.find(".//geom[@name='R_held_tomato']");rb.remove(g_);tomato_geom(rb,'R_held_tomato',[0,0,-tomato_dz(cfg)])
  if held=='holder':
   for s in [-1,1]:box(rb,'R_held_key_shoulder'+str(s),[s*.036,0,0],[.008,.046,.030])
 if cfg.get('mesh_tool'):
  # R11: MuJoCo 3.2.5 reports box-box distances inside the contact margin at
  # about half the true gap (measured 0.500x; box-shaped mesh vs box: 1.000x).
  # Tool-side boxes become identical 8-vertex box meshes; geometry unchanged.
  asset=tree.getroot().find('asset')
  if asset is None:asset=E.SubElement(tree.getroot(),'asset')
  tool=tree.find(".//body[@name='R_tool']")
  for g in tool.iter('geom'):
   if g.get('type')!='box':continue
   h=np.fromstring(g.get('size'),sep=' ');mn='mb_'+g.get('name')
   E.SubElement(asset,'mesh',name=mn,vertex=' '.join(fmt([sx*h[0],sy*h[1],sz*h[2]]) for sx in(-1,1) for sy in(-1,1) for sz in(-1,1)))
   g.set('type','mesh');g.set('mesh',mn);g.attrib.pop('size',None)
 E.indent(tree)
 if cfg.get('r14'):
  import kitchen14;kitchen14.add(tree,cfg)  # R14 storage / dispensing / cooking stations
 return tree,dict(config=cfg,mount_height=height,mandoline_origin=mp.tolist(),mandoline_rotation=R.tolist(),peeler_origin=pp.tolist(),wash_bottom=bottom.tolist(),wash_mouth=mouth.tolist(),wash_normal=(wr@np.array([0,0,1])).tolist(),jet=[-.58,.33,.97] if cfg.get('long_spout') else [-.58,.43,.91],chute_top=chute_top,lever_origin=None if lever_origin is None else lever_origin.tolist(),held=held,mode=mode,raw_objects={n:dict(position=p,size=s,support='raw_tray') for n,p,s in raw})
GRASP_W={'carrot':.035,'potato':.065,'tomato':.07,'greens':.10,'holder':.030,'catch_tray':.030,'pusher':.030}
def jaw_q(cfg,held):
 """Jaw slide value that closes the fingers onto the held object's grasp width
 (inherited .015 when no finger pads are configured)."""
 if cfg.get('finger'):
  import fingers;return fingers.jaw_q(cfg,held)
 fo=cfg.get('finger_offset',0.)
 if not fo or held is None:return .015
 return float(np.clip(GRASP_W[held]/2-fo,0,.025))
def targets(cfg,meta):
 mp=np.array(meta['mandoline_origin']);R=np.array(meta['mandoline_rotation']);pp=np.array(meta['peeler_origin'])
 # Tool approach +X, jaw local -Y: same reference rotation function in checker.
 out=[]
 def add(name,points,held=None,approach=(0,0,-1),force=None,kind='transfer'):
  out.append(dict(name=name,points=np.asarray(points).tolist(),held=held,approach=list(approach),force=force,kind=kind))
 rc=np.array(meta['raw_objects']['carrot']['position'])
 add('raw_pick',[rc,rc+[0,0,.04]],'carrot')
 if cfg.get('side_wash'):add('wash_load',[np.array(meta['wash_mouth'])+[0,-.14,-.005],np.array(meta['wash_mouth'])+[0,-.10,-.005]],'carrot',approach=(0,1,0))
 else:add('wash_load',[np.array(meta['wash_mouth'])+[0,-.04,.10],np.array(meta['wash_mouth'])+[0,-.04,.06]],'carrot')
 add('wash_work',[np.array(meta['wash_mouth'])+[0,-.04,.06],np.array(meta['wash_mouth'])+[.025,-.04,.06]],'carrot',force=[9.191,0,0],kind='working')
 if cfg['approach']=='top':points=[pp+[0,-.045,.17],pp+[0,-.045,.09]];approach=[0,0,-1]
 else:points=[pp+[0,-.22,.085],pp+[0,-.18,.085]];approach=[0,1,0]
 if cfg.get('seated_peel'):points=[pp+[0,-.045-cfg.get('peel_len',.04),.0895+cfg.get('peel_hover',0.)],pp+[0,-.045,.0895+cfg.get('peel_hover',0.)]]
 if cfg.get('peel_top'):points=[pp+[0,-.045,.1385],pp+[0,-.045,.0985]];approach=[0,0,-1]
 add('peel_load',points,'carrot',approach)
 add('peel_retrieve',points[::-1],'carrot',approach)
 add('holder_load',[mp+R@[-.10,0,.23],mp+R@[-.10,0,.19]],'carrot')
 add('mandoline_work',[mp+R@[-.10,0,.19],mp+R@[.10,0,.19]],'holder',force=(R@[-60,10,20]).tolist(),kind='working')
 add('holder_retreat',[mp+R@[.10,0,.19],mp+R@[.10,0,.26]],'holder')
 add('catch_tray_pick',[mp+R@[0,-.11,.044],mp+R@[0,-.15,.044]],'catch_tray',approach=(0,1,0))
 add('bowl_deliver',[[-1.67,.46,1.09],[-1.67,.46,1.05]] if cfg.get('fix_bowl_target') else [[-1.67,.12,1.09],[-1.67,.12,1.05]],'catch_tray')
 add('scrap_service',[pp+[0,-.18,.04],pp+[0,-.22,.04]],'catch_tray',approach=(0,1,0))
 if cfg.get('front_grasp'):
  for t in out:
   if t['name'] in ('raw_pick','holder_load'):t['approach']=[0,1,0]
 if cfg.get('long_spout'):
  for t in out:
   if t['name']=='wash_load':t.update(points=[[-.58,.25,.92],[-.58,.33,.92]],approach=[0,1,0])
   if t['name']=='wash_work':t.update(points=[[-.58,.33,.92],[-.565,.33,.92]],approach=[0,1,0])
 elif cfg.get('wash_front_high'):
  for t in out:
   if t['name']=='wash_load':t.update(points=[[-.58,.39,.875],[-.58,.43,.875]],approach=[0,1,0])
   if t['name']=='wash_work':t.update(points=[[-.58,.43,.875],[-.565,.43,.875]],approach=[0,1,0])
 if cfg.get('mand_raise'):out=[t for t in out if t['name'] not in ('catch_tray_pick','bowl_deliver','scrap_service')]
 for t in out:
  if cfg.get('cart_spots') and t['name'] in cfg['cart_spots']:t['cart_x']=cfg['cart_spots'][t['name']]
 if cfg.get('fixed_jaws'):
  for t in out:
   if (t['name']=='raw_pick' and not cfg.get('rib_tray')) or (t['name'] in ('peel_load','peel_retrieve') and cfg.get('peel_top')):t['jaws']=[[0,1,0],[0,-1,0]]
   if t['name']=='raw_pick' and cfg.get('rib_tray'):t['jaws']=[[0,0,1],[0,0,-1]];t['approach']=[0,1,0]
   if t['name'] in ('peel_load','peel_retrieve') and not cfg.get('peel_top'):t['jaws']=[[0,0,1],[0,0,-1]]
 if cfg.get('r11_tomato') and meta.get('lever_origin'):
  # One jaw sense only: the held tomato hangs 20 mm below the TCP in tool -z, so
  # the mirrored jaw (tool z = world -z) would misplace it.
  T=dict(held='tomato',approach=[0,1,0],jaws=[[1,0,0]],force=None,kind='transfer')
  tp=np.array(meta['raw_objects']['tomato']['position'])+[0,0,tomato_dz(cfg)]
  out.append(dict(T,name='raw_pick@tomato',points=[tp.tolist(),(tp+[0,0,.04]).tolist()]))
  out.append(dict(T,name='wash_load@tomato',points=[[-.58,.25,.92],[-.58,.33,.92]]))
  # Slide in 6 mm above the blade plate (pusher above), then set down 6 mm.
  lo_=np.array(meta['lever_origin']);pt=lo_+[0,0,plate_top(cfg)+.03+tomato_dz(cfg)]
  out.append(dict(T,name='wedge_slide@tomato',points=[(pt+[0,-.05,.006]).tolist(),(pt+[0,0,.006]).tolist()]))
  out.append(dict(T,name='wedge_load@tomato',points=[(pt+[0,0,.006]).tolist(),pt.tolist()]))
  kn=lo_+np.array(lever_knob(cfg))
  if cfg.get('press_front'):
   # Knob gripped from the front like the tomato placing (same arm posture).
   P=dict(approach=[0,1,0],jaws=[[1,0,0]],force=None);pre_=kn+[0,-.06,0]
  else:P=dict(approach=[0,0,-1],jaws=[[1,0,0],[-1,0,0]],force=None);pre_=kn+[0,0,.06]
  out.append(dict(P,name='pusher_grasp',held=None,kind='transfer',points=[pre_.tolist(),kn.tolist()]))
  out.append(dict(P,name='pusher_press',held='pusher',kind='working',points=[kn.tolist(),(kn-[0,0,LEVER_PRESS]).tolist()]))
  out.append(dict(P,name='pusher_return',held='pusher',kind='transfer',points=[(kn-[0,0,LEVER_PRESS]).tolist(),kn.tolist()]))
  for t in out[-7:]:
   if cfg.get('cart_spots') and t['name'] in cfg['cart_spots']:t['cart_x']=cfg['cart_spots'][t['name']]
 if meta.get('chute_top'):
  # Carrot vertical (jaws horizontal), TCP at its middle: lower 80 mm so the carrot
  # bottom ends 20 mm inside the chute; release then drops it inside the chute.
  c=np.array(meta['chute_top'])
  out.append(dict(name='chute_load',points=[(c+[0,0,.14]).tolist(),(c+[0,0,.06]).tolist()],held='carrot',approach=[0,1,0],force=None,kind='transfer',jaws=[[1,0,0],[-1,0,0]]))
  if cfg.get('cart_spots') and 'chute_load' in cfg['cart_spots']:out[-1]['cart_x']=cfg['cart_spots']['chute_load']
 if cfg.get('correct_peel_seat') and not cfg.get('peel_top'):
  for t in out:
   if t['name'] in ('peel_load','peel_retrieve'):
    t['points']=(np.array(t['points'])+[0,0,.009]).tolist()
 return out
