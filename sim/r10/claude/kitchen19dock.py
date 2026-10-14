"""R19 cart docking (GitHub #39, R19_DOCK.md): a floor DATUM RAIL along the base-cabinet plinth that carries the cart's
front on two V-groove wheels, a magnetic x scale on the rail, and an index pin + V-block stop at each cart station.
NEW layer; no existing file is changed. Nothing in a scene changes unless cfg['r19dock'] is set (add() returns the
tree untouched without it), so every earlier scene and stored result is byte-identical.

Labels: [S] bought part, size from the vendor catalogue (R19_DOCK.md section 8); [D] design value chosen here;
[E] estimate. All positions are world metres (x along the counter, y = 0 the base-cabinet front plane, +y toward the
wall, z up from the floor) for the rail, and cart-frame metres (origin under the cart reference point, docked at
world y = DOCK_Y = -0.21) for the cart parts.

FIXED (floor / plinth), geoms 'dock_*' (environment):
 - dock_rail: aluminium extrusion 40 (y) x 30 (z) mm, 6063-T5, slot 8 [D], on a 0-3 mm shim / adhesive bed (modelled
   as part of the box), x RAIL_X0..RAIL_X1 (the cabinet run + the parking alcove, as the R10 toe channel it replaces;
   the tether runs in the extrusion's inner channel). Fixed by MS-polymer / VHB to the floor tiles and by small
   angles into the plinth (dock_bracket_*, 2 screws each, one per 0.6 m of cabinet run; none in the alcove).
 - dock_vtrack: DualVee single-edge V track size 3 [S] (22.23 wide, 8.71 high, AISI 420 hardened), on the cabinet
   half of the extrusion top; its 90 deg V-edge is the y AND z datum of the cart front.
 - dock_scale: magnetic scale tape (RLS LM10 class, 2 mm poles, self-adhesive, stainless cover) [S] on the aisle face of
   the extrusion: the absolute x reference of the cart, in motion and docked.
 - dock_vblock_<station>: hardened steel insert with a 90 deg V-groove ACROSS the rail (groove along y), flush with
   the extrusion top on its aisle half, clamped by two T-nuts (re-locatable along the slot) at each station x.
 - dock_stop_l / dock_stop_r: rubber end buffers at the rail ends (the cart trucks hit them 25 mm past the soft limits).
CART (geoms 'R_cart_dock_*', cart parts):
 - two V-wheel TRUCKS at cart x = +-TRUCK_X: a DualVee W3 wheel [S] (OD 45.80, width 15.88, working radial load
   5900 N, axial 1701 N) on an eccentric bushing (sets the front height and the cart level), axis along y, rolling on
   the V track; a 6 mm steel plate from the chassis front cross-member down to the wheel stud on its aisle side.
   The cart's FRONT rests on these two wheels (the front castors of #14 are set 5 mm above the floor: off-rail and
   fault supports only).
 - the INDEX PIN unit at cart x = 0: a 24 V self-locking linear actuator (20 mm stroke) driving a hardened
   12 mm ball-nosed pin through a disc spring; 'up' = travel (nose 13 mm above the rail top, 4.3 mm above the V track), 'down' = seated in a
   station V-block (force-limited to PIN_PRELOAD_N, then held by the self-locking lead screw).
 - the scale READ HEAD (ride height 0.7 mm, LM10 allows up to 1.0 mm [S]) next to the pin unit, over the tape on the
   upper land of the extrusion's aisle face.
 - two ANTI-LIFT KEEPERS at cart x = +-KEEPER_X: a 4 mm steel arm down the aisle face to a UHMW-PE T-head that runs
   INSIDE the extrusion's aisle-face slot with 1 mm clearance all round. It never touches in normal running; it holds
   the cart front down / in if a V wheel is lifted (protective stops, a person pushing the cart, the pin's preload
   beyond the front load). Pin preload is limited to PIN_PRELOAD_N so the V wheels stay seated when docked.
cfg['r19dock'] = dict(pin='up'|'down', parts='all'|'world'|'cart', stations=None (dict name -> cart x; default STATIONS))
Geometry is conservative (enclosing boxes; the V track and V-blocks are boxes enclosing the V)."""
import numpy as np,xml.etree.ElementTree as E
from scipy.spatial.transform import Rotation
DOCK_Y=-.21                      # world y of the cart origin when docked (mobile.DOCK_Y, all stored paths)
RAIL_X0,RAIL_X1=-1.82,2.80       # [D] rail ends: the cart's x travel (-1.48..2.46) +- the truck offset +- 25 mm over-travel
EXT=dict(y0=-.045,y1=-.005,z0=0.,z1=.033)   # [D] extrusion 40 x 30 + 3 mm bed; 5 mm off the plinth / door plane for the angles
TRACK=dict(w=.02223,h=.00871,yc=-.016,apex_over_top=.0015)   # [S] DualVee T3 width / height; [D] centre y; [E] virtual apex above the real top
WHEEL=dict(od=.0458,w=.01588,vri=.01905)    # [S] DualVee W3 OD, width, inside vee radius (to the virtual apex)
TRUCK_X=.27                      # [D] trucks at cart x +-0.27 (0.54 m apart): inside the chassis outline, clear of the castors (|x| 0.137..0.304)
PLATE=dict(t=.006,gap=.0036,hx=.035,z0=.050)   # [D] truck plate: thickness, gap to the wheel face, half length, bottom z
PIN=dict(r=.006,y=-.037,up_bottom=.046,stroke=.020)   # [D] 12 mm ball-nosed pin over the aisle half of the rail; retracted nose 4.3 mm above the V-track top (>= 5 mm running clearance)
VBLOCK=dict(hx=.015,y0=-.045,y1=-.029,top=.033,depth=.005,v_width=.010)   # [D] V-block insert, 90 deg V across the rail (along y), 10 mm mouth, 5 mm deep
HOUSING=dict(hx=.020,y0=-.052,y1=-.022,z0=.052,z1=.090)   # [D] actuator housing under the chassis front (bottom 0.09)
HEAD=dict(x0=.040,x1=.080,y0=-.060,ride=.0007,z0=.018,z1=.036)   # [D] read head; ride height 0.7 mm: 0.4-1.0 mm over the +-0.3 mm y budget (LM10: <= 1.0 mm [S])
SCALE=dict(t=.0015,z0=.022,z1=.032)   # [S] LM10 tape ~1.3 mm + cover, 10 mm wide; [D] on the upper land of the aisle face (above the slot)
BRACKETS=[-1.65,-1.05,-.45,.15,.75,1.35]   # [D] plinth angles under the cabinet run (x -1.80..1.80); alcove: adhesive only
STOP=dict(l=.010,top=.075)       # [D] end buffers
SLOT=dict(z0=.0125,z1=.0205,depth=.008)   # aisle-face slot of the extrusion (8 mm opening, centred on the 30 mm face) [S, 8-slot profile]
KEEPER_X=.11;KEEPER=dict(hx=.015,arm_y0=-.056,arm_y1=-.052,arm_z0=.010,clear=.001)   # [D] keepers between the pin unit and the castors
PIN_PRELOAD_N=50.   # [D] <= half the smallest front (two-truck) load found by r19dock_budget.py PART=lean
# the cart stations (cart x, R_carriage_x) of the adopted paths (R19_DOCK.md section 2): hub nodes, anchors where the
# cart dwells for a seat / closed chain / forceful work, the parked stir, stgwok, and parking
STATIONS={'SPAT':-1.48,'PRESS':-1.274,'LEVER':-.7398,'SINK':-.68,'WOK':.172,'STIR':.55,'LID_POT':.8863,'POT':1.093,
 'STGWOK':1.21,'LID_RACK':1.3256,'PARK':2.40}
I3=np.eye(3);RY=Rotation.from_euler('x',90,degrees=True).as_matrix()   # cylinder axis z -> y
def apex_z():return EXT['z1']+TRACK['h']+TRACK['apex_over_top']
def wheel_cz():return apex_z()+WHEEL['vri']
def pin_down_bottom():
 """lowest point of the seated ball nose: the nose (radius r) touches the two 45 deg flanks; its centre sits r/sin45
 above the V apex; the apex is VBLOCK depth below the rail top."""
 apex=VBLOCK['top']-VBLOCK['depth'];return apex+PIN['r']/np.sin(np.pi/4)-PIN['r']
def capture_mm():
 """x capture of the V-block: a nose landing anywhere inside the V mouth slides to the groove line."""
 return round(VBLOCK['v_width']/2*1e3,1)
def world_parts(stations=None):
 """fixed parts: (name, type, centre, half sizes, R) in the world."""
 st=STATIONS if stations is None else stations;e=EXT;t=TRACK;out=[]
 xc=(RAIL_X0+RAIL_X1)/2;hx=(RAIL_X1-RAIL_X0)/2
 out.append(('dock_rail','box',[xc,(e['y0']+e['y1'])/2,(e['z0']+e['z1'])/2],[hx,(e['y1']-e['y0'])/2,(e['z1']-e['z0'])/2],I3))
 out.append(('dock_vtrack','box',[xc,t['yc'],e['z1']+t['h']/2],[hx,t['w']/2,t['h']/2],I3))
 out.append(('dock_scale','box',[xc,e['y0']-SCALE['t']/2,(SCALE['z0']+SCALE['z1'])/2],[hx,SCALE['t']/2,(SCALE['z1']-SCALE['z0'])/2],I3))
 v=VBLOCK
 for n,x in st.items():out.append((f'dock_vblock_{n}','box',[x,(v['y0']+v['y1'])/2,v['top']-.004],[v['hx'],(v['y1']-v['y0'])/2,.004],I3))
 for k,x in enumerate(BRACKETS):out.append((f'dock_bracket_{k}','box',[x,(e['y1']+0.)/2,.0165],[.015,-e['y1']/2,.0135],I3))
 for n,x0 in (('l',RAIL_X0),('r',RAIL_X1-STOP['l'])):
  out.append((f'dock_stop_{n}','box',[x0+STOP['l']/2,(e['y0']+e['y1'])/2,(e['z1']+STOP['top'])/2],[STOP['l']/2,(e['y1']-e['y0'])/2,(STOP['top']-e['z1'])/2],I3))
 return out
def cart_parts(pin='up'):
 """cart-mounted parts: (name, type, centre, half sizes, R) in the CART frame (y_local = y_world - DOCK_Y)."""
 L=lambda y:y-DOCK_Y;out=[];wz=wheel_cz();w=WHEEL;p=PLATE
 for s,tag in ((-1,'l'),(1,'r')):
  x=s*TRUCK_X
  out.append((f'R_cart_dock_wheel_{tag}','cylinder',[x,L(TRACK['yc']),wz],[w['od']/2,w['w']/2],RY))
  py1=TRACK['yc']-w['w']/2-p['gap'];py0=py1-p['t']
  out.append((f'R_cart_dock_plate_{tag}','box',[x,L((py0+py1)/2),(p['z0']+.09)/2],[p['hx'],p['t']/2,(.09-p['z0'])/2],I3))
 h=HOUSING;out.append(('R_cart_dock_pin_housing','box',[0.,L((h['y0']+h['y1'])/2),(h['z0']+h['z1'])/2],[h['hx'],(h['y1']-h['y0'])/2,(h['z1']-h['z0'])/2],I3))
 zb=PIN['up_bottom'] if pin=='up' else pin_down_bottom();zt=h['z0']+.004   # the pin shank runs up into the housing
 out.append(('R_cart_dock_pin','cylinder',[0.,L(PIN['y']),(zb+PIN['r']+zt)/2],[PIN['r'],(zt-zb-PIN['r'])/2],I3))
 out.append(('R_cart_dock_pin_nose','sphere',[0.,L(PIN['y']),zb+PIN['r']],[PIN['r']],I3))
 k=KEEPER
 for s,tag in ((-1,'l'),(1,'r')):
  x=s*KEEPER_X
  out.append((f'R_cart_dock_keeper_arm_{tag}','box',[x,L((k['arm_y0']+k['arm_y1'])/2),(k['arm_z0']+.09)/2],[k['hx'],(k['arm_y1']-k['arm_y0'])/2,(.09-k['arm_z0'])/2],I3))
  n0,n1=k['arm_y1'],EXT['y0']+SLOT['depth']-k['clear'];z0,z1=SLOT['z0']+k['clear'],SLOT['z1']-k['clear']   # the T-head inside the slot (the slot is not modelled: the rail is a solid box)
  out.append((f'R_cart_dock_keeper_{tag}','box',[x,L((n0+n1)/2),(z0+z1)/2],[k['hx'],(n1-n0)/2,(z1-z0)/2],I3))
 hd=HEAD;y1=EXT['y0']-SCALE['t']-hd['ride']
 out.append(('R_cart_dock_head','box',[(hd['x0']+hd['x1'])/2,L((hd['y0']+y1)/2),(hd['z0']+hd['z1'])/2],[(hd['x1']-hd['x0'])/2,(y1-hd['y0'])/2,(hd['z1']-hd['z0'])/2],I3))
 return out
# declared contacts / running gaps (screens): the V wheels ride on the V track (by design); the seated pin bears on its
# station V-block; the read head runs at its ride height over the scale.
INTENDED=[('R_cart_dock_wheel_l','dock_vtrack'),('R_cart_dock_wheel_r','dock_vtrack')]
INTENDED_DOWN=[('R_cart_dock_pin_nose','dock_vblock_'),('R_cart_dock_pin','dock_vblock_'),('R_cart_dock_pin_nose','dock_rail')]   # the V-block is let into the rail's top slot
REPLACED=['floor_cable_guide']   # the R10 toe channel (y -0.04..-0.01, z 0..0.03) is replaced by the rail: the tether runs in the extrusion's bore
RUNNING=[('R_cart_dock_keeper_l','dock_rail',KEEPER['clear']),('R_cart_dock_keeper_r','dock_rail',KEEPER['clear']),('R_cart_dock_keeper_','dock_scale',KEEPER['clear']),('R_cart_dock_head','dock_scale',HEAD['ride']),('R_cart_dock_head','dock_rail',HEAD['ride']+SCALE['t']),('R_cart_dock_head','dock_vblock_',HEAD['ride']+SCALE['t'])]   # the head rides over the tape on the rail's aisle face
def _fmt(v):return ' '.join(f'{float(x):.9g}' for x in v)
def _geom(parent,name,typ,pos,size,R,rgba,cart):
 return E.SubElement(parent,'geom',name=name,type=typ,pos=_fmt(pos),size=_fmt(size),quat=_fmt(Rotation.from_matrix(np.asarray(R,float)).as_quat()[[3,0,1,2]]),
  rgba=rgba,contype='2' if cart else '1',conaffinity='3' if cart else '2',margin='.01' if cart else '0',mass='.000001')
def add(tree,cfg):
 """Apply cfg['r19dock'] (no-op without it): the fixed rail parts in the world and / or the cart parts."""
 c=cfg.get('r19dock')
 if not c:return tree
 c=dict(dict(pin='up',parts='all',stations=None),**c)
 if c['parts'] in ('all','world'):
  w=tree.find('worldbody')
  for n,typ,p,s,R in world_parts(c['stations']):_geom(w,n,typ,p,s,R,'.70 .72 .75 1' if 'rail' in n or 'bracket' in n else '.85 .55 .20 1',False)
 if c['parts'] in ('all','cart'):
  cart=tree.find(".//body[@name='rail_structure']")
  for n,typ,p,s,R in cart_parts(c['pin']):_geom(cart,n,typ,p,s,R,'.85 .30 .20 1',True)
 return tree
def mesh(tree):
 """R11 mesh rule for every dock part (boxes -> 8-vertex meshes, cylinders -> circumscribed 16-gon prisms; spheres stay)."""
 asset=tree.getroot().find('asset');n=16;t=2*np.pi*(np.arange(n)+.5)/n
 if asset is None:asset=E.SubElement(tree.getroot(),'asset')
 for g in tree.getroot().iter('geom'):
  nm=g.get('name') or ''
  if not nm.startswith(('dock_','R_cart_dock_')) or g.get('type') not in ('box','cylinder'):continue
  h=np.fromstring(g.get('size'),sep=' ');mn='mbd_'+nm
  if g.get('type')=='box':V=[[sx*h[0],sy*h[1],sz*h[2]] for sx in(-1,1) for sy in(-1,1) for sz in(-1,1)]
  else:rc=h[0]/np.cos(np.pi/n);V=[[rc*np.cos(a),rc*np.sin(a),sz*h[1]] for a in t for sz in (-1,1)]
  E.SubElement(asset,'mesh',name=mn,vertex=' '.join(_fmt(v) for v in V))
  g.set('type','mesh');g.set('mesh',mn);g.attrib.pop('size',None)
 return tree
def summary():
 """key design numbers (for the report)."""
 return dict(apex_z_m=round(apex_z(),4),wheel_centre_z_m=round(wheel_cz(),4),wheel_top_z_m=round(wheel_cz()+WHEEL['od']/2,4),
  wheel_flange_bottom_z_m=round(wheel_cz()-WHEEL['od']/2,4),pin_up_bottom_z_m=PIN['up_bottom'],pin_down_bottom_z_m=round(pin_down_bottom(),4),
  pin_travel_mm=round((PIN['up_bottom']-pin_down_bottom())*1e3,1),vblock_capture_mm=capture_mm(),truck_spacing_m=2*TRUCK_X,keeper_x_m=KEEPER_X,keeper_clearance_mm=KEEPER['clear']*1e3,pin_preload_N=PIN_PRELOAD_N,
  rail_x=[RAIL_X0,RAIL_X1],stations=STATIONS)
