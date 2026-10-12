"""Revision3: real moving station assemblies, with all original arm solids.

This adapter changes geometry, never the frozen R04/R05 acceptance functions.
Custom pans have engineered floor penetrations (lift glands and drain), not
globally reduced collision hulls. All replaced solids are listed in the design.
"""
import rescue_cell as rc
from rescue_cell import *
BASE_SCENE=rc.scene
V3=H/'v3'

def settings(v):
 p=V3/f'layouts/L{v}.json'
 if p.exists():return json.loads(p.read_text())
 return dict(id=v,name='Integrated pan bay with under-deck lift and indexed tools',width=1.50,depth=.90,pitch=.33,station_x=.45,
             lift_x=-.19,lift_y=.015,lift_bar_z=-.17,rod_y=-.042,rod_radius=.005,rod_x=.10,
             gland_half=.012,bridge_y=-.042,head_y=.19,head_z=.235,
             tool_park_x=.18,brush_y=.040,cradle_raise=.10,guard_y=.255,blade_y=0.,blade_z=.37,
             waste_x=.02,brush_z=.1735,tool_x=-.08,tool_z=.19)

def register(v):
 s=settings(v);cfg=dict(rc.CONFIGS[17],id=v,name=s['name'],width=s['width'],depth=s['depth'],pitch=s['pitch'],station_x=s['station_x'])
 rc.CONFIGS[v]=cfg
 return cfg,s

def moving(parent,name,pos,axis,rg,mass=.3,kind='slide'):
 b=body(parent,name,pos);E.SubElement(b,'joint',name=name+'_joint',type=kind,axis=fmt(axis),range=fmt(rg),damping='2')
 E.SubElement(b,'inertial',pos='0 0 0',mass=str(mass),diaginertia='.003 .003 .003')
 return b

def cylinder(parent,name,pos,radius,length,axis='z',**attrs):
 g=E.SubElement(parent,'geom',name=name,type='cylinder',pos=fmt(pos),size=fmt([radius,length/2]),rgba='.54 .60 .63 1',contype='1',conaffinity='2',**attrs)
 if axis!='z':g.set('quat',quat(Rotation.from_euler('y' if axis=='x' else 'x',90,degrees=True)))
 return g

def perforated(parent,name,bounds,z,thick,holes,**attrs):
 """Exact union of rectangles minus declared rectangular apertures."""
 xmin,xmax,ymin,ymax=bounds;xs=sorted(set([xmin,xmax]+[x for a,b,c,d in holes for x in (a,b) if xmin<x<xmax]));ys=sorted(set([ymin,ymax]+[y for a,b,c,d in holes for y in (c,d) if ymin<y<ymax]));names=[]
 for i,(a,b) in enumerate(zip(xs,xs[1:])):
  for j,(c,d) in enumerate(zip(ys,ys[1:])):
   x,y=(a+b)/2,(c+d)/2
   if any(aa<x<bb and cc<y<dd for aa,bb,cc,dd in holes):continue
   nm=f'{name}_{i}_{j}';box(parent,nm,[x,y,z],[b-a,d-c,thick],**attrs);names.append(nm)
 return names

def ring(parent,name,center,outer,inner,height,**attrs):
 x,y,z=center
 return perforated(parent,name,[x-outer,x+outer,y-outer,y+outer],z,height,[[x-inner,x+inner,y-inner,y+inner]],**attrs)

def build_scene(v,held=None,locations=None):
 cfg,s=register(v);text,com=BASE_SCENE(v,held,locations);root=E.fromstring(text);w=root.find('worldbody')
 # Replace BOTH earlier custom proxies by one actual integrated mechanical bay.
 # A second open land remains for inspection/clean cassette staging.
 wash=w.find("body[@name='wash_basin']");process=w.find("body[@name='process_cell']")
 for b in (wash,process):
  for el in list(b):
   if el.get('name') not in ('wash_open_land','process_open_land'):b.remove(el)
 z=cfg['work_z'];sx=-cfg['station_x'];sy=cfg['rear_y']
 old=w.find("geom[@name='worktop_full']");w.remove(old)
 # Proper structural opening, framed by the retained worktop, for sealed rods
 # and screened water/scrap drainage. Exterior footprint remains unchanged.
 aperture=.25 if v>=32 else .24 if v>=30 else .18
 hole=[sx-aperture,sx+aperture,sy-.145,sy+.145]
 workholes=[hole]
 if v>=19:workholes.append([-.065,.065,.73,.86])
 perforated(w,'worktop_aperture',[-cfg['width']/2,cfg['width']/2,0,cfg['depth']],z-.022,.024,workholes)
 land=wash.find("geom[@name='wash_open_land']");wash.remove(land)
 for side in (-1,1):box(wash,'wash_open_land_'+str(side),[side*(.124 if v>=20 else .15),0,0],[.016 if v>=20 else .03,.245,.024])
 if v>=29:
  for side in (-1,1):
   clamp=moving(wash,'pan_retainer_'+str(side),[side*.177,0,.04],[-side,0,0],[0,.04],.20)
   box(clamp,'pan_retainer_shoe_'+str(side),[0,0,0],[.02,.14,.035])
   box(clamp,'pan_retainer_link_'+str(side),[side*.025,0,-.055],[.02,.016,.11])
   box(wash,'pan_clamp_L16_50_'+str(side),[side*.212,0,-.13],[.025,.025,.118])
   box(wash,'pan_clamp_cam_case_'+str(side),[side*.212,.025,-.06],[.030,.020,.065])
 # Full pan envelope retained, with three explicit floor penetrations. Insert
 # lifts through two sealed push rods; it remains in its own pan at all times.
 for product in PRODUCTS:
  pre='R_held_' if held=='output_'+product else '';pan=root.find(f".//body[@name='{pre}output_{product}']")
  floor=pan.find(f"geom[@name='{pre}pan_{product}_floor']");pan.remove(floor)
  gh=s['gland_half'];holes=[[sign*s['rod_x']-gh,sign*s['rod_x']+gh,s['rod_y']-gh,s['rod_y']+gh] for sign in (-1,1)]+[[-.010,.010,.043,.063]]
  attrs=dict(contype='2' if pre else '1',conaffinity='3' if pre else '2')
  perforated(pan,pre+'pan_'+product+'_floor',[-.1325,.1325,-.0815,.0815],.00035,.0007,holes,**attrs)
  for sign in (-1,1):
   ring(pan,pre+f'lift_gland_{product}_{sign}',[sign*s['rod_x'],s['rod_y'],.0045 if v>=25 else .005],gh+.003,gh,.009,**attrs)
  # Normally closed drain disk under the floor, opens downward in the bay.
  valve=moving(pan,pre+'pan_drain_'+product,[0,.053,.008 if v>=20 else .004 if v>=19 else -.003],[0,0,1 if v>=19 else -1],[0,.012],.03)
  box(valve,pre+'pan_drain_disk_'+product,[0,0,0],[.022,.022,.002],**attrs)
  # Recessed push sockets transmit lift load and prevent lateral basket escape.
  carrier=pan.find(f"body[@name='{pre}carrier_{product}']")
  if v>=25:carrier.find(f"geom[@name='{pre}carrier_latch_{product}']").set('pos','.12 .055 .069')
  for sign in (-1,1):
   ring(carrier,pre+f'lift_socket_{product}_{sign}',[sign*s['rod_x'],s['rod_y'],-.005],.010,.006,.010,**attrs)
  # Additional seals/sockets/valve mass, explicit weighted CoM.
  extra=.16;ine=pan.find('inertial');m=float(ine.get('mass'));c0=np.fromstring(ine.get('pos'),sep=' ');ine.set('mass',str(m+extra));ine.set('pos',fmt((m*c0+extra*np.array([0,-.02,.008]))/(m+extra)))
 # Lift stage: full LEFS16B-150 with normally applied lock envelope. A modeled
 # bridge and two push rods carry the insert; no unattached magic slide.
 lift=moving(wash,'basket_lift',[0,0,0],[0,0,1],[0,.155],1.1)
 box(wash,'LEFS16B150_full',[s['lift_x'],s['lift_y'],-.29 if v>=21 else -.215],[.065,.040,.389])
 box(lift,'lift_carriage',[s['lift_x']+(.053 if v>=19 else .033),s['lift_y'],s['lift_bar_z'] if v>=21 else -.24 if v>=19 else -.13],[.035,.060,.065])
 cross_start=s['lift_x']+(.065 if v>=19 else 0)
 box(lift,'lift_crossbar',[(cross_start+s['rod_x'])/2,s['bridge_y'],s['lift_bar_z']],[s['rod_x']-cross_start+.025,.025,.020])
 box(lift,'lift_bridge',[s['lift_x']+(.070 if v>=19 else .04),(s['bridge_y']+s['lift_y'])/2,s['lift_bar_z']],[.025 if v>=19 else .055,abs(s['bridge_y']-s['lift_y'])+.025,.020])
 rodtop=.011 # below pan floor at z=.012 while loading; lift .021 to socket top
 for sign in (-1,1):
  length=rodtop-s['lift_bar_z'];cylinder(lift,'basket_pushrod_'+str(sign),[sign*s['rod_x'],s['rod_y'],(rodtop+s['lift_bar_z'])/2],s['rod_radius'],length)
 # Station lift mechanical top catch, spring applied with electrical release.
 catch=moving(wash,'lift_safety_catch',[s['lift_x']+.045,s['lift_y']+.05,-.065],[0,-1,0],[0,.025],.1)
 box(catch,'lift_safety_pin',[0,0,0],[.018,.03,.010]);box(wash,'catch_solenoid_full',[s['lift_x']+.045,s['lift_y']+(.11 if v>=19 else .08),-.065],[.03,.05,.035])
 # Catch basin has true walls and apertures, plus a gravity-screened drain.
 holes=[[sign*s['rod_x']-.009,sign*s['rod_x']+.009,s['rod_y']-.009,s['rod_y']+.009] for sign in (-1,1)]+[[-.022,.022,.043,.087]]
 sump=.24 if v>=32 else .18
 perforated(wash,'wash_sump_floor',[-sump,sump,-.145,.145],-.105,.003,holes)
 for sign in (-1,1):
  box(wash,'wash_sump_side_'+str(sign),[sign*(sump-.0015),0,-.049],[.003,.29,.11])
  box(wash,'wash_sump_end_'+str(sign),[0,sign*.1435,-.049],[2*sump,.003,.11])
 for sign in (-1,1):ring(wash,'sump_rod_gland_'+str(sign),[sign*s['rod_x'],s['rod_y'],-.11],.014,.007,.01)
 # Full 1/2in NC water valve envelope, air break, separate dirty drain and
 # screen. Water particles are a volume ledger, not fictitious rigid food.
 box(wash,'water_NC_valve',[.13,.115,-.28],[.055,.040,.075]);cylinder(wash,'air_break_spout',[.11,.24 if v>=27 else .115,.20],.006,.045)
 spray_z=.20 if v>=26 else s['head_z']
 cylinder(wash,'spray_manifold',[0,.245 if v>=21 else s['head_y'],spray_z],.008,.25,'x')
 for ix in range(5):cylinder(wash,'spray_nozzle_'+str(ix),[-.10+.05*ix,(.245 if v>=21 else s['head_y'])-.010,spray_z-.01],.004,.025)
 ring(wash,'screen_drain_tube',[0,.065,-.17],.027,.022,.12)
 # Four wire screen bars retain >=3mm scrap; actual dirt/quality is an assumption.
 for i in range(9):box(wash,'drain_screen_'+str(i),[-.020+i*.005,.065,-.12],[.001,.044,.001])
 # Above-pan spindle module. It is parked behind the lid sweep, and advances
 # only after arm withdrawal and basket retention. Full commodity actuator
 # envelopes include motors, guide rails, travel and guarded tool holders.
 head_parent=wash
 if v>=24:
  head_parent=moving(wash,'service_lower',[0,0,0],[0,0,-1],[0,.365],3.)
  box(wash,'tool_Z_LEFS25C400_full' if v>=26 else 'tool_Z_LEFS16B400_full',[-.245,.19,.405],[.058,.102,.681] if v>=26 else [.040,.065,.639])
  box(head_parent,'tool_Z_bridge',[-.067 if v>=26 else -.08 if v>=25 else -.12,.19,s['head_z']+.145],[.29,.04,.025])
 head=moving(head_parent,'service_head',[s['tool_park_x'],s['head_y'],s['head_z']],[0,-1,0],[0,.19],1.8)
 box(head_parent,'head_LEFS16B200_full',[s['tool_park_x'],.015 if v>=20 else s['head_y']+.02,s['head_z']+(.16 if v>=20 else .06)],[.065,.439,.040])
 box(head,'head_plate',[0,0,0],[.060,.08,.035])
 feed=moving(head,'tool_feed',[-.11 if v>=23 else -.08,0,0],[1,0,0],[0,.16],.6)
 box(head,'feed_LEFS16B200_full',[0,0,.065],[.439,.040,.065])
 follower=moving(feed,'peel_follower',[.08 if v>=23 else 0,0,-.035],[0,0,-1],[0,.06],.25)
 box(follower,'peeler_OXO_full',[0,.04 if v>=20 else .078,0],[.1524,.0762,.0254] if v>=20 else [.0762,.1524,.0254],'.3 .65 .45 1')
 box(follower,'peeler_edge',[0,0,-.014],[.002,.065,.003] if v>=25 else [.065,.002,.003],'.75 .78 .8 1')
 box(feed,'follower_L16_full',[0,.11,.035] if v>=22 else [0,.09,.035] if v>=20 else [.028,0,.035],[.025,.025,.168])
 brush=moving(feed,'brush_approach',[.08 if v>=23 else 0,-.055,-.035],[0,0,-1],[0,.08],.20)
 cylinder(brush,'wash_brush_full',[0,0,0],.020,.060,'x')
 cylinder(brush,'wash_brush_motor',[.055,0,0],.016,.045,'x')
 # Cradle is a separate guided lift with two end retention cups. It is not
 # allowed to take ownership until both cups and support faces really meet.
 cradle_parent=wash
 if v>=27:
  cradle_parent=moving(wash,'cradle_park',[0,.23 if v>=30 else .18,0],[0,-1,0],[0,.23 if v>=30 else .18],1.2)
  box(wash,'cradle_park_LEFS16B200_full',[-.255 if v>=31 else -.205,.02,.86 if v>=32 else .79 if v>=31 else .47],[.065,.439,.040])
  box(cradle_parent,'cradle_park_bridge',[0,0,.60 if v>=30 else .50 if v>=29 else .40],[.41,.04,.018])
  if v>=31:
   box(cradle_parent,'cradle_park_carriage',[-.2125,0,.86 if v>=32 else .79],[.020,.04,.030])
   box(cradle_parent,'cradle_park_drop_link',[-.193,0,.73 if v>=32 else .695],[.019,.020,.26 if v>=32 else .19])
 cradle=moving(cradle_parent,'food_cradle',[0,0,.34 if v>=30 else .28 if v>=21 else .032],[0,0,-1 if v>=21 else 1],[0,.24],.8)
 box(wash,'cradle_LEFS16B250_full',[.20,.105 if v>=31 else -.02,-.15],[.065,.04,.489])
 box(cradle,'cradle_bridge',[0,-.063,-.010],[.23,.012,.010])
 for sign in (-1,1):
  box(cradle,'cradle_finger_'+str(sign),[sign*.060,-.025,0],[.016,.078,.003])
  cup=moving(cradle,'end_cup_'+str(sign),[sign*.115,0,.025],[-sign,0,0],[0,.04],.10)
  rot=moving(cup,'index_'+str(sign),[0,0,0],[1,0,0],[-math.pi,math.pi],.08,'hinge')
  cylinder(rot,'retention_cup_'+str(sign),[0,0,0],.017,.010,'x')
  if v>=25:
   cylinder(cup,'NEMA17_index_motor_'+str(sign),[0,0,.12],.030,.048)
   cylinder(cup,'index_vertical_shaft_'+str(sign),[0,0,.070],.004,.10)
   box(cup,'index_bevel_case_'+str(sign),[sign*.025,0,.025] if v>=26 else [0,0,.025],[.020,.026,.040])
  else:cylinder(cup,'NEMA17_index_motor_'+str(sign),[sign*.035,0,0],.030,.048,'x')
  box(cradle,'L16_end_feed_'+str(sign),[sign*.10,-.065,.14 if v>=26 else .030],[.168,.025,.025])
 # Eyer/core tool: complete145x20x13mm triangle tool on indexed Cartesian
 # carriage; same head feed, separate approach. Coverage not assumed executed.
 core=moving(head,'core_approach',[.075,-.06,.18 if v>=26 else .04],[0,0,-1],[0,.20 if v>=26 else .12],.15)
 box(core,'triangle_huller_full',[0,0,0],[.020,.013,.145],'.5 .65 .4 1')
 box(head,'core_LEFS16B200_full' if v>=26 else 'core_L16_full',[.12 if v>=20 else .075,-.06,.14 if v>=26 else .13],[.065,.040,.439] if v>=26 else [.025,.025,.168])
 # Cutting: retain full v2 blade140x110x3 and carriage; put the cut entirely
 # above pan rim. Feed cradle, pusher and catcher have actual solids.
 blade_x=s.get('blade_x',s['tool_park_x']);press=wash;pressbase=wash
 if s.get('press_vertical',v>=28):
  pressbase=moving(wash,'press_lower',[0,0,.45],[0,0,-1],[0,.45],1.)
  box(wash,'press_Z_LEFS25C450_full',[.32,.22,.45],[.058,.102,.731])
 if v>=22:
  press=moving(pressbase,'press_lateral',[0,0,0],[-1,0,0],[0,.13],4.)
  railz=.35 if s.get('press_vertical',v>=28) else .65 if v>=23 else .55
  box(pressbase,'press_park_rail',[.135,.225 if v>=23 else .185,railz],[.33,.045,.035]);box(pressbase,'press_park_motor',[.32,.225 if v>=23 else .185,railz],[.07,.06,.06])
 blade=moving(press,'slice_blade',[blade_x,s['blade_y'],s['blade_z']],[0,0,-1],[0,.20],2.)
 box(blade,'process_blade_full',[0,0,0],[.003,.14,.11],'.75 .77 .79 1');box(blade,'process_carriage_plate',[0,0,.065],[.04,.18,.03])
 box(press,'blade_screw_frame',[blade_x+(.075 if v>=20 else .04),s['blade_y']+(.14 if v>=20 else .12),s['blade_z']-.02],[.07,.08,.36])
 box(press,'blade_brake_stepper',[blade_x+(.075 if v>=20 else .04),s['blade_y']+(.14 if v>=20 else .12),s['blade_z']+.19],[.086,.086,.105])
 pusher=moving(wash,'slice_pusher',[-.24 if v>=24 else -.14,0,.28 if v>=24 else .24],[1,0,0],[0,.35 if v>=24 else .25],.35)
 box(pusher,'slice_pusher_face',[0,0,0],[.010,.05,.05]);box(wash,'pusher_L16_full',[-.16,-.11,.24],[.168,.025,.025])
 box(wash,'blade_guard_back',[.07,s['guard_y'],.25],[.36,.006,.40],'.4 .7 .8 .18')
 # Scrap falls through an open, four-wall rectangular chute, not a solid box.
 cx=s['waste_x'];cy=.065
 for sign in (-1,1):
  box(wash,'scrap_chute_x_'+str(sign),[cx+sign*.055,cy,-.24],[.002,.09,.28])
  box(wash,'scrap_chute_y_'+str(sign),[cx,cy+sign*.044,-.24],[.11,.002,.28])
 diverter=moving(wash,'scrap_diverter',[cx,cy,-.06],[1,0,0],[0,1.2],.1,'hinge');box(diverter,'scrap_gate',[0,0,0],[.105,.08,.003])
 # Relocate existing full waste bin under the integrated bay.
 w.find("body[@name='waste_bin']").set('pos',fmt([sx+cx,sy+cy,.30]))
 if held:
  mass=next(g['combined_mass_kg'] for g in SPEC['grasp_handles'] if g['object_id']==held)+.40
  grip=np.array([0,-.155,.15]);tr=Rotation.from_euler('z',180,degrees=True)*WORLD_TOOL*PREP_LOCAL
  com=(mass*np.array(com)+.16*tr.inv().apply(np.array([0,-.02,.008])-grip))/(mass+.16)
  root.find(".//site[@name='R_mass']").set('pos',fmt(np.array([0,0,.09])+PREP_LOCAL.apply(com)))
  # The unchanged reference applies held mass at its explicit CoM. Avoid
  # counting new pan hardware a second time in MuJoCo gravity bias.
  for b in root.find(f".//body[@name='R_held_{held}']").iter('body'):
   ine=b.find('inertial')
   if ine is not None:ine.set('mass','1e-9');ine.set('diaginertia','1e-12 1e-12 1e-12')
 return E.tostring(root,encoding='unicode'),com

class StationCell(rc.Workcell):
 def __init__(self,v,held=None,locations=None):
  register(v);old=rc.scene;rc.scene=build_scene
  try:super().__init__(v,held,locations)
  finally:rc.scene=old
  self.support_registry['wash_basin']['faces']=['wash_open_land_-1','wash_open_land_1']
 def window(self,obj,station,origin):
  out=super().window(obj,station,origin)
  parts=[n.removeprefix('R_held_') for n in self.gnames if n.removeprefix('R_held_').startswith('pan_'+obj.removeprefix('output_')+'_floor_')]+['pan_'+obj.removeprefix('output_')+'_'+a for a in ('left','right','front','rear')]
  if self.variant>=25:
   # Coplanar load-bearing gland feet at pan z=0 are deliberate dock supports.
   # They use only this object's registered land and the unchanged50mm normal
   # window. No permission is added for another fixture or transit path.
   parts += [n.removeprefix('R_held_') for n in self.gnames if n.removeprefix('R_held_').startswith('lift_gland_'+obj.removeprefix('output_')+'_')]
  for win in out:win['held_parts']=parts
  return out

def payload(ch,pos,load='carry'):
 h=rc.hand(ch,pos,load)
 if ch.held_id:h['R']['held_kg']+=.16
 return h
