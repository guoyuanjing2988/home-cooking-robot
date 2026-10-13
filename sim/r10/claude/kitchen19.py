"""R19 prep layout (issue #4, steps 1-2): a layer on top of kitchen17 (new file; no shared file changed).
See R19_PREP_LAYOUT.md for the chosen spots (LAYOUT below) and the evidence.

The prep stations of R11/R12 are placed again in today's (R18b) kitchen. Their geometry is EXACTLY the
R11 station geometry of scene.py: a donor scene is built once with the stations at the origin (presets
WD/SD: lever base AY-403 class 30 mm lower with the plate 35 mm toward the aisle, 卓晋 3-in-1 slicer,
R11 open-cradle peeler), and their bodies are copied to the new pose (x, y, yaw about z). The R14 robot
cold box (冷藏料盒, kitchen14.FRIDGE['rbox']) gets a counter set-down pose.

cfg['r19'] (dict), read by add(tree, cfg) after scene.build():
 stations   {'slicer'|'lever'|'peeler'|'cold_box': (x, y, yaw_deg)}  stations on the counter
 pusher     'rest' (default) | None (held: left out) | float (pressed this far, m)
 objs       [(name, R 3x3 list, p list)]  R19 objects lying in the world (carrot, tomato, pusher, ...)
 tray       True (default): the R19 raw-tray contents: carrot on its ribs (scene.py), tomato on a
            45 mm pad at the tray front (R11 WD), potato moved to the tray's back right; the scene's own
            raw carrot / potato / tomato must be absent (raw_absent, set by base_cfg()).
 no_staple  True (default): the obsolete rice/flour outlet (r14_staple_port) is removed (rice is the
            user's, DECISIONS 2026-10-13); removing an obstacle can only make paths easier.
Objects for r17chain-style whole actions (registered in kitchen16.OBJ, as kitchen17 does):
 carrot  Ø35 x 160 mm cylinder (the dyn.py carrot), frame at its centre, axis along object x;
         grasp at the centre from object +y (front grasp off the rib tray), jaws along object z
 tomato  Ø70 x 60 mm cylinder (R11), frame at its centre; grasped at the equator from object +y,
         jaws along object x (WD)
 pusher  the lever cutter's guided pusher (disc, stem, knob), frame at the knob centre; knob gripped
         from the front (+y), jaws along x (R11 AU/AW 'press_front')
All sizes are the R11/R12/R14 estimates; nothing here is a measured product."""
import copy,numpy as np,xml.etree.ElementTree as E
from scipy.spatial.transform import Rotation
from scene import box,fmt
import kitchen15 as K15,kitchen16 as K,kitchen17 as K17
COUNTER_TOP=.85
def Rz(a):return K.Rz(a)
# ---------------- R11 station geometry (donor) ----------------
_DON=None
def donor():
 """Station bodies built by scene.build at the origin (R11 geometry, presets WD + SD peeler)."""
 global _DON
 if _DON is None:
  import chain
  from scene import build
  c=chain.chain_cfg('WD',present=['slicer','lever','peeler'],slicer=[0.,0.],lever_base=[0.,0.],peel=[0.,0.],raw_absent=['potato','carrot','greens','tomato'],r11_tomato=False)
  tree,meta=build(c,None);w=tree.find('worldbody')
  _DON=dict(slicer=w.find("body[@name='slicer_station']"),bowl=w.find("body[@name='slicer_out_bowl']"),lever=w.find("body[@name='lever_station']"),
   peeler=w.find("body[@name='peeler_station']"),cfg=c,chute_top=np.array(meta['chute_top']),lever_dz=c.get('lever_dz',0.))
 return _DON
LEVER_KNOB_Z=.302;LEVER_PLATE_TOP=.094;LEVER_PRESS=.102   # above the counter: knob centre (scene.lever_knob + lever_dz), blade plate top (scene.plate_top), press stroke
TOMATO_R,TOMATO_H=.035,.03                                    # R11 tomato cylinder (radius, half height)
CARROT_R,CARROT_HL=.0175,.08                                  # carrot radius, half length
SLICER_CHUTE=np.array([-.08,0.,.28])                          # chute top centre, slicer frame (above the counter)
SLICER_BOWL=np.array([.275,0.,.001]);SLICER_BOWL_R=.085
RBOX=dict(L=.30,W=.08,H=.10,bar_z=.11,bar_r=.006,post=.038)   # kitchen14.FRIDGE['rbox']: tub, bridge-bar height above the rim, post offset
def place(name,x,y,yaw):
 """World pose (R, p) of a station frame."""
 return Rz(yaw),np.array([x,y,COUNTER_TOP])
def chute_top(x,y,yaw):R,p=place('slicer',x,y,yaw);return p+R@SLICER_CHUTE
def lever_seat(x,y,yaw,lift=0.):
 """Tomato centre on the blade plate (+lift above its seat)."""
 return np.array([x,y,COUNTER_TOP+LEVER_PLATE_TOP+TOMATO_H+lift])
def knob(x,y,yaw):return np.array([x,y,COUNTER_TOP+LEVER_KNOB_Z])
def box_bar(x,y,yaw):return np.array([x,y,COUNTER_TOP+RBOX['H']+RBOX['bar_z']])
def _copy_station(world,src,name,x,y,yaw,drop=()):
 b=copy.deepcopy(src);b.set('name',f'r19_{name}_station');R,p=place(name,x,y,yaw)
 b.set('pos',fmt(p));b.set('quat',fmt(Rotation.from_matrix(R).as_quat()[[3,0,1,2]]))
 for g in list(b.iter('geom')):
  if g.get('name') in drop:
   for par in b.iter():
    if g in list(par):par.remove(g);break
 world.append(b);return b
def _cold_box(world,x,y,yaw,prefix='r19_cbox_',bar=True):
 R=Rz(yaw);p=np.array([x,y,COUNTER_TOP]);q=fmt(Rotation.from_matrix(R).as_quat()[[3,0,1,2]])
 for n,c,s in cold_box_parts(bar):
  g=box(world,prefix+n,p+R@np.asarray(c),np.asarray(s)*2,(.3,.55,.75,1));g.set('quat',q)
def cold_box_parts(bar=True):
 """Tub (long axis along local y), two posts, bridge bar across (local x), frame at the tub's bottom centre."""
 L,W,H,bz,br,po=RBOX['L'],RBOX['W'],RBOX['H'],RBOX['bar_z'],RBOX['bar_r'],RBOX['post']
 P=[('tub',[0,0,H/2],[W/2,L/2,H/2])]
 for s in (-1,1):P.append((f'post{s:+d}',[s*po,0,H+bz/2],[.006,.006,bz/2]))
 if bar:P.append(('bar',[0,0,H+bz],[.044,br,br]))
 return P
def base_cfg(extra=None):
 """chain_cfg extras for today's kitchen with the R19 raw tray (the scene's own raw carrot, potato and
 tomato left out; kitchen19 places them)."""
 return dict(raw_absent=['carrot','potato','tomato'],r11_tomato=False,**(extra or {}))
TRAY_CARROT=np.array([-1.42,.12,.868+.045+CARROT_R])          # scene.py rib tray: carrot centre on the ribs (raw_shift .27)
TRAY_PAD=np.array([-1.245,.12]);TRAY_PAD_H=.045               # R11 WD tomato pad (50 x 50 x 45 mm) at the tray front
TRAY_TOMATO=np.array([-1.245,.12,.868+TRAY_PAD_H+TOMATO_H])
TRAY_POTATO=np.array([-1.245,.27,.903])
TRAY_GEOMS=('raw_tray','raw_rib-1','raw_rib1','raw_greens')      # scene.py geoms that move with the tray
def tray(name,dxy=(0.,0.)):
 """World position of a raw-tray item with the tray moved by dxy (x, y)."""
 return {'carrot':TRAY_CARROT,'tomato':TRAY_TOMATO,'potato':TRAY_POTATO}[name]+np.array([dxy[0],dxy[1],0.])
def add(tree,cfg):
 r=cfg.get('r19');world=tree.find('worldbody')
 if r is None:return tree
 if r.get('no_staple',True):
  for g in list(world.iter('geom')):
   if g.get('name')=='r14_staple_port':world.remove(g)
 for bname in r.get('drop_bowls',[]):   # R07 staging bowls taken off the counter (bodies stored_bowl_<name>...)
  for b in list(world.findall('body')):
   if any((g.get('name') or '').startswith('stored_bowl_'+bname) for g in b.iter('geom')):world.remove(b)
 dxy=np.array(r.get('tray_dxy',(0.,0.)),float)
 if np.any(dxy):
  for g in world.iter('geom'):
   if g.get('name') in TRAY_GEOMS:p_=np.fromstring(g.get('pos'),sep=' ');p_[:2]+=dxy;g.set('pos',fmt(p_))
 if r.get('tray',True):
  box(world,'r19_raw_pad_tomato',[*(TRAY_PAD+dxy),.868+TRAY_PAD_H/2],[.05,.05,TRAY_PAD_H],(.4,.5,.35,1))
  if r.get('potato',True):box(world,'r19_raw_potato',tray('potato',dxy),[.09,.065,.07],(.85,.5,.15,1))
 D=donor()
 for name,(x,y,yaw) in (r.get('stations') or {}).items():
  if name=='slicer':
   _copy_station(world,D['slicer'],'slicer',x,y,yaw)
   R,p=place('slicer',x,y,yaw);b=copy.deepcopy(D['bowl']);b.set('name','r19_slicer_out_bowl');b.set('pos',fmt(p+R@SLICER_BOWL));world.append(b)
   for g in b.iter('geom'):g.set('name','r19_'+g.get('name'))
  elif name=='lever':
   pu=r.get('pusher','rest');drop=('lever_pusher','lever_pusher_stem','lever_pusher_knob') if pu!='rest' else ()
   _copy_station(world,D['lever'],'lever',x,y,yaw,drop)
   if isinstance(pu,float):   # pressed by pu: the pusher lower on its rails
    Rp,pp=pusher_pose(x,y,yaw,pu);K._add(world,'',OBJ_PARTS['pusher'],Rp,pp,rgba='.6 .6 .65 1')
  elif name=='peeler':_copy_station(world,D['peeler'],'peeler',x,y,yaw)
  elif name=='cold_box':_cold_box(world,x,y,yaw)
 for name,R,p in r.get('objs',[]):
  K._add(world,'',[q for q in K.OBJ[name]['parts']],np.asarray(R,float),np.asarray(p,float),rgba='.9 .4 .15 1')
 return tree
# ---------------- objects for whole-action chains ----------------
def _carrot_parts():
 return [('r19_carrot','cylinder',[0,0,0],[CARROT_R,CARROT_HL],K.Ry(90))]   # cylinder axis (local z) along object x
def _tomato_parts():
 return [('r19_tomato','cylinder',[0,0,0],[TOMATO_R,TOMATO_H],np.eye(3))]
def _pusher_parts():
 # scene.LEVER_PUSHER relative to the knob centre (disc 110 x 25 mm, stem 20 x 20 x 60, knob 30 x 50 x 30)
 return [('r19_pusher_disc','cylinder',[0,0,.2445-.332],[.055,.0125],np.eye(3)),('r19_pusher_stem','box',[0,0,.287-.332],[.01,.01,.03],np.eye(3)),
  ('r19_pusher_knob','box',[0,0,0],[.015,.025,.015],np.eye(3))]
OBJ_PARTS=dict(carrot=_carrot_parts(),tomato=_tomato_parts(),pusher=_pusher_parts())
K.OBJ['carrot']=dict(parts=OBJ_PARTS['carrot'],grip=np.zeros(3),a=np.array([0,1.,0]),j=np.array([0,0,1.]),grip_part=None)
K.OBJ['tomato']=dict(parts=OBJ_PARTS['tomato'],grip=np.zeros(3),a=np.array([0,1.,0]),j=np.array([1.,0,0]),grip_part=None)
K.OBJ['pusher']=dict(parts=OBJ_PARTS['pusher'],grip=np.zeros(3),a=np.array([0,1.,0]),j=np.array([1.,0,0]),grip_part='r19_pusher_knob')
JAW=dict(carrot=.0015,tomato=.016,pusher=0.)   # fingers.jaw_q(D): carrot force mode, tomato position mode 4 mm squeeze, keyed knob
MASS=dict(carrot=.12,tomato=.15,pusher=.25)    # chain.MASS (R10/R11)
def pusher_pose(x,y,yaw,pressed=0.):return Rz(yaw),knob(x,y,yaw)-[0,0,pressed]
# ---------------- layout candidates (step 1) ----------------
# item: tool (fetched lever base = the fetched-tool work spot), slicer (resident), peeler (fetched), cold_box (set-down)
CANDIDATES={
 # fetched-tool work spot (lever base): R11 spot (reference), far-left front, back strip, by the sink
 'tool_R11':dict(item='tool',st=('lever',-1.00,.095,0.),desc='R11/R12 work spot (reference; cooking corridor)'),
 'tool_FL':dict(item='tool',st=('lever',-1.665,.095,0.),desc='far-left front: counter end to 1 cm left of the raw tray, blade plate at the R11 y'),
 'tool_FL_b':dict(item='tool',st=('lever',-1.665,.135,0.),desc='far-left front, 4 cm further back'),
 'tool_BK14':dict(item='tool',st=('lever',-1.40,.395,0.),desc='back strip instead of the potato staging bowl'),
 'tool_BK09':dict(item='tool',st=('lever',-0.88,.395,0.),desc='back strip by the sink instead of the tomato staging bowl'),
 # slicer (resident)
 'slicer_R11':dict(item='slicer',st=('slicer',.30,.13,0.),desc='R11 spot (reference; both plating spots)'),
 'slicer_BK10':dict(item='slicer',st=('slicer',-1.00,.475,0.),desc='left counter back (audit candidate), long axis along x, chute under the cabinet'),
 'slicer_FLT':dict(item='slicer',st=('slicer',-1.69,.225,90.),desc='far-left column, turned 90 deg: chute at the front (open strip), out bowl under the cabinet'),
 'slicer_BKT12':dict(item='slicer',st=('slicer',-1.36,.225,90.),desc='turned 90 deg over the raw tray position (raw tray moved), chute at the front'),
 # peeler (fetched; R11 open-cradle model, 0.48 x 0.24 m)
 'peeler_R11':dict(item='peeler',st=('peeler',-1.00,.20,0.),desc='R11/R12 spot (reference; overlaps the spatula)'),
 'peeler_FLT':dict(item='peeler',st=('peeler',-1.66,.25,90.),desc='far-left column turned 90 deg (cradles along y, back guard and lid toward the counter end, loaded from +x)'),
 'peeler_BK':dict(item='peeler',st=('peeler',-0.95,.462,0.),desc='left counter back by the sink, front-loaded under the cabinet (staging bowls moved)'),
 'tool_TR':dict(item='tool',st=('lever',-1.38,.095,0.),desc='raw-tray front (raw tray moved to the back)'),
 'slicer_TR40':dict(item='slicer',st=('slicer',-1.40,.225,90.),desc='turned 90 deg at the raw-tray front (raw tray moved), chute at the front'),
 'tool_TR47':dict(item='tool',st=('lever',-1.47,.095,0.),desc='raw-tray front, left half (raw tray moved to the back)'),
 'tool_TR50':dict(item='tool',st=('lever',-1.50,.095,0.),desc='raw-tray front, 3 cm further left'),
 'tool_BKL':dict(item='tool',st=('lever',-1.665,.43,0.),desc='far-left back, under the cabinet'),
 'tool_C90':dict(item='tool',st=('lever',-0.90,.095,0.),desc='left counter front by the sink (cooking corridor)'),
 'tool_PL':dict(item='tool',st=('lever',.30,.095,0.),desc='plating area (empty before cooking; prep-time only)'),
 'tool_PL90':dict(item='tool',st=('lever',.30,.13,90.),desc='plating area, turned 90 deg: front (slide-in side, knob grasp) toward +x'),
 'tool_CB':dict(item='tool',st=('lever',-0.90,.20,0.),desc='left counter by the sink, set back (blade plate y 0.20); the chosen spot is tool_CB_-0.86_0.21'),
 **{f'tool_CB_{x:.2f}_{y:.2f}':dict(item='tool',st=('lever',x,y,0.),desc='set-back work spot variants') for x,y in ((-0.87,.20),(-0.85,.20),(-0.90,.22),(-0.88,.22),(-0.86,.22),(-0.88,.21),(-0.86,.21),(-0.87,.215),(-0.90,.21))},
 **{f'cbox_CBX_{x:.2f}_{y:.2f}':dict(item='cold_box',st=('cold_box',x,y,90.),desc='cold box along x at the set-back work spot') for x,y in ((-0.86,.17),(-0.86,.19),(-0.86,.21),(-0.86,.15))},
 'cbox_CB':dict(item='cold_box',st=('cold_box',-0.90,.12,90.),desc='CHOSEN: cold box along x at the work spot (instead of the lever base)'),
 **{f'tool_CB_{x:.2f}_{y:.2f}':dict(item='tool',st=('lever',x,y,0.),desc='left counter by the sink, set back (carry lane and shoulder pass in front of it)') for x in (-.90,-.95) for y in (.20,.24)},
 **{f'tool_PLB_{x:.2f}_{y:.2f}':dict(item='tool',st=('lever',x,y,0.),desc='plating area, set back (knob further from the passing shoulder)') for x in (.10,.20,.30) for y in (.16,.20,.24)},
 **{f'tool_PL90_{x:.2f}_{y:.2f}':dict(item='tool',st=('lever',x,y,90.),desc='plating area, turned 90 deg (grid)') for x in (.10,.20,.30,.40) for y in (.10,.16,.20)},
 # raw tray (0.32 x 0.30, R10 rib tray + R11 tomato pad); dxy moves the whole tray
 'tray_now':dict(item='tray',st=('tray',0.,0.,0.),desc='today (R18b): x -1.515..-1.195, y .04-.34'),
 'tray_BKL':dict(item='tray',st=('tray',-.2825,.24,0.),desc='back-left corner under the cabinet: x -1.7975..-1.4775, y .28-.58'),
 'tray_BKM':dict(item='tray',st=('tray',0.,.24,0.),desc='back-middle under the cabinet (instead of the potato staging bowl): x -1.515..-1.195, y .28-.58'),
 # cold box set-down (box along y unless yaw 90)
 'cbox_T1':dict(item='cold_box',st=('cold_box',-1.69,.15,0.),desc='inside the far-left tool-spot footprint (shared with the tool spot)'),
 'cbox_T2':dict(item='cold_box',st=('cold_box',-1.665,.15,0.),desc='tool-spot footprint, centred'),
 'cbox_T3':dict(item='cold_box',st=('cold_box',-1.64,.15,0.),desc='tool-spot footprint, right'),
 'cbox_T4':dict(item='cold_box',st=('cold_box',-1.665,.17,0.),desc='tool-spot footprint, centred, 2 cm back'),
 'cbox_R14':dict(item='cold_box',st=('cold_box',-1.70,.18,0.),desc='R14 set-down (the only counter spot that passed in R14)'),
 'cbox_FL':dict(item='cold_box',st=('cold_box',-1.755,.18,0.),desc='against the counter end, 5.5 cm further left'),
 'cbox_FLX':dict(item='cold_box',st=('cold_box',-1.64,.05,90.),desc='along x at the counter front edge, far left'),
}
def boxes(C):
 """Envelope boxes (name, centre, size) of a candidate: each station geom's world AABB (exact for the
 R11 boxes at 0/90 deg; the out bowl as one cylinder envelope)."""
 import mujoco
 name,x,y,yaw=C['st'];D=donor();tree=E.Element('mujoco');w=E.SubElement(tree,'worldbody')
 if name=='tray':   # tray plate, ribs, items (as scene.py + the R19 pad / potato), moved by (x, y)
  d=np.array([x,y,0.]);c0=np.array([-1.355,.19,.859])
  out=[('tray',c0+d,[.32,.30,.018]),('ribs+carrot',np.array([-1.42,.12,.9305])+d,[.16,.055,.035+.045+.002]),('greens',np.array([-1.41,.265,.903])+d,[.17,.10,.07]),
   ('pad+tomato',np.array([-1.245,.12,.9055])+d,[.07,.07,.075]),('potato',TRAY_POTATO+d,[.09,.065,.07])]
  return [(n,np.asarray(c,float),list(sz)) for n,c,sz in out]
 if name=='cold_box':
  out=[];R=Rz(yaw);p=np.array([x,y,COUNTER_TOP])
  for n,c,s in cold_box_parts():
   ext=np.abs(R)@np.asarray(s);out.append((n,p+R@np.asarray(c),2*ext))
  return out
 src={'slicer':D['slicer'],'lever':D['lever'],'peeler':D['peeler']}[name];_copy_station(w,src,name,x,y,yaw)
 xml='<mujoco>'+E.tostring(w,encoding='unicode')+'</mujoco>'
 for k in ('<asset>',):pass
 import xml.etree.ElementTree as ET
 # meshes of the peeler cutter etc. are boxes/cylinders in components.xml; compile standalone
 m=mujoco.MjModel.from_xml_string(xml);d=mujoco.MjData(m);mujoco.mj_forward(m,d);out=[]
 for g in range(m.ngeom):
  ab=m.geom_aabb[g];Rg=d.geom_xmat[g].reshape(3,3);cen=d.geom_xpos[g]+Rg@ab[:3];ext=np.abs(Rg)@ab[3:]
  out.append((m.geom(g).name,cen,2*ext))
 if name=='slicer':
  R,p=place('slicer',x,y,yaw);c=p+R@SLICER_BOWL;out.append(('out_bowl',c+[0,0,.045],[2*SLICER_BOWL_R,2*SLICER_BOWL_R,.09]))
 return out
COUNTERS=[((-1.80,-0.70),(0.,.60)),((-0.08,.709),(0.,.60)),((1.46,1.80),(0.,.60))]   # counter tops free of the sink and the hob
def on_counter(lo,hi):
 return any(lo[0]>=a[0]-1e-6 and hi[0]<=a[1]+1e-6 and lo[1]>=b[0]-1e-6 and hi[1]<=b[1]+1e-6 for a,b in COUNTERS)
# ---------------- reach probes (step 1): working poses at each candidate ----------------
def _probes():
 P={}
 for nm,C in CANDIDATES.items():
  st,x,y,yaw=C['st'];sc={'stations':{st:(x,y,yaw)}}
  if st=='lever':
   Ra=Rz(yaw);a_=tuple((Ra@[0,1.,0]).round(6));j_=tuple((Ra@[1.,0,0]).round(6))   # the station's front grasp direction (R11 AU/AW), turned with it
   P[f'{nm}:place']=dict(desc='tomato held 8 mm over its seat on the blade plate',p=lever_seat(x,y,yaw,.008),a=a_,j=j_,held='tomato',scene=sc,jaw_q=JAW['tomato'])
   P[f'{nm}:knob']=dict(desc='pusher knob between the open jaws (grasp moment), tomato on the plate',p=knob(x,y,yaw),a=a_,j=j_,scene=dict(sc,objs=[('tomato',Ra.tolist(),lever_seat(x,y,yaw).tolist())]),jaw_q=.025)
   P[f'{nm}:pressed']=dict(desc='pusher held, pressed 102 mm (tomato cut, gone)',p=knob(x,y,yaw)-[0,0,LEVER_PRESS],a=a_,j=j_,held='pusher',scene=dict(sc,pusher=None),jaw_q=JAW['pusher'])
  if st=='slicer':
   c=chute_top(x,y,yaw)
   for tag,a,j in (('front',(0,1,0),(1,0,0)),('left',(-1,0,0),(0,1,0)),('right',(1,0,0),(0,1,0))):
    # carrot vertical: object x (its axis) along world z; grasp approach a, jaws j (horizontal)
    P[f'{nm}:drop_{tag}']=dict(desc=f'carrot vertical, bottom 20 mm inside the chute, gripper from the {tag}',p=c+[0,0,.06],a=a,j=j,held='carrot',scene=sc,jaw_q=JAW['carrot'])
  if st=='peeler':
   R,p=place('peeler',x,y,yaw);seat=p+R@np.array([0,-.045,.0995])   # SD peel_load end: station (0, -.045, .0995) incl. the 1 mm hover; carrot along the cradle (station x)
   a=R@np.array([0,1.,0]);j=np.array([0,0,1.])
   P[f'{nm}:seat']=dict(desc='carrot seated in the cradles, front load along the station y (SD peel_fwd)',p=seat,a=tuple(a.round(6)),j=j,held='carrot',scene=sc,jaw_q=JAW['carrot'],R_obj=R.tolist())
  if st=='cold_box':
   P[f'{nm}:set']=dict(desc='bridge bar pinched from above, box set down (bar 1.06 m)',p=box_bar(x,y,yaw),a=(0,0,-1),j=tuple((Rz(yaw)@[0,1.,0]).round(6)),scene=sc,jaw_q=0.)
 return P
# ---------------- the chosen layout (see R19_PREP_LAYOUT.md) ----------------
# - slicer (卓晋, 6.8 kg, resident): far-left column, turned 90 deg, chute at the front (open strip), out bowl
#   under the cabinet; clear of every stored cooking path (replay) and reachable (drop probes);
# - raw tray: unchanged (R18b), picks reachable;
# - fetched-tool work spot (lever base AY-403 class; also the cold-box set-down and other fetched tools,
#   one at a time): left counter by the sink, SET BACK (origin (-0.86, 0.21)) so the carry lane and the
#   robot's own upper arm pass in front of it; the 6 stored cooking chains do not hit it (replay screen),
#   the hub edges are only partly replayed; the R07 tomato staging bowl is moved off this spot;
# - cold box: set down along x at the work spot (-0.86, 0.17), never at the same time as the lever base.
LAYOUT=dict(slicer=(-1.69,.225,90.),lever=(-0.86,.21,0.),cold_box=(-0.86,.17,90.),tray_dxy=(0.,0.),drop_bowls=['tomato'])   # the R07 tomato staging bowl (x -0.96..-0.76, y .36-.56) would overlap the lever base plate: moved off this spot
FAUCET_OUT=np.array([K17.FX,.37,1.10])   # the R17 faucet outlet (spout front end)
def layout_scene(*stations,**kw):
 """cfg['r19'] for the chosen layout with these stations out (the slicer is resident: always out)."""
 st={'slicer':LAYOUT['slicer']};st.update({s:LAYOUT[s] for s in stations})
 return dict(stations=st,tray_dxy=LAYOUT['tray_dxy'],drop_bowls=LAYOUT['drop_bowls'],**kw)
def _layout_probes():
 P={};L=LAYOUT;dxy=L['tray_dxy'];I=np.eye(3).tolist()
 tom=('tomato',I,tray('tomato',dxy).tolist());car=('carrot',I,tray('carrot',dxy).tolist())
 P['Q:pick_carrot']=dict(desc='carrot held 8 mm over its ribs (raw tray as today), tool spot empty',p=tray('carrot',dxy)+[0,0,.008],a=(0,1,0),j=(0,0,1),held='carrot',scene=layout_scene(objs=[tom]),jaw_q=JAW['carrot'])
 P['Q:pick_tomato']=dict(desc='tomato held 8 mm over its pad, tool spot empty',p=tray('tomato',dxy)+[0,0,.008],a=(0,1,0),j=(1,0,0),held='tomato',scene=layout_scene(objs=[car]),jaw_q=JAW['tomato'])
 P['Q:pick_tomato_lever']=dict(desc='tomato held 8 mm over its pad, lever base out',p=tray('tomato',dxy)+[0,0,.008],a=(0,1,0),j=(1,0,0),held='tomato',scene=layout_scene('lever',objs=[car]),jaw_q=JAW['tomato'])
 for z in (1.00,.97):
  P[f'Q:rinse_carrot_z{z:.2f}']=dict(desc=f'carrot (along x) under the faucet outlet, centre at z {z}, faucet open',p=np.array([FAUCET_OUT[0],FAUCET_OUT[1],z]),a=(0,1,0),j=(0,0,1),held='carrot',scene=layout_scene(objs=[tom]),lever=K17.LEVER_OPEN,jaw_q=JAW['carrot'])
  P[f'Q:rinse_tomato_z{z:.2f}']=dict(desc=f'tomato under the faucet outlet, centre at z {z}, faucet open, lever base out',p=np.array([FAUCET_OUT[0],FAUCET_OUT[1],z]),a=(0,1,0),j=(1,0,0),held='tomato',scene=layout_scene('lever',objs=[car]),lever=K17.LEVER_OPEN,jaw_q=JAW['tomato'])
 x,y,yaw=L['lever']
 P['Q:lever_place']=dict(desc='tomato 8 mm over its seat on the blade plate',p=lever_seat(x,y,yaw,.008),a=(0,1,0),j=(1,0,0),held='tomato',scene=layout_scene('lever',objs=[car]),jaw_q=JAW['tomato'])
 P['Q:lever_knob']=dict(desc='knob between the open jaws, tomato on the plate',p=knob(x,y,yaw),a=(0,1,0),j=(1,0,0),scene=layout_scene('lever',objs=[car,('tomato',I,lever_seat(x,y,yaw).tolist())]),jaw_q=.025)
 P['Q:lever_pressed']=dict(desc='pusher held, pressed 102 mm',p=knob(x,y,yaw)-[0,0,LEVER_PRESS],a=(0,1,0),j=(1,0,0),held='pusher',scene=layout_scene('lever',pusher=None,objs=[car]),jaw_q=JAW['pusher'])
 c=chute_top(*L['slicer'])
 for tag,a,j in (('front',(0,1,0),(1,0,0)),('left',(-1,0,0),(0,1,0))):
  P[f'Q:drop_{tag}']=dict(desc=f'carrot vertical, bottom 20 mm inside the chute, gripper from the {tag}',p=c+[0,0,.06],a=a,j=j,held='carrot',scene=layout_scene(objs=[tom]),jaw_q=JAW['carrot'])
  P[f'Q:over_{tag}']=dict(desc=f'carrot vertical 80 mm higher, over the chute, gripper from the {tag}',p=c+[0,0,.14],a=a,j=j,held='carrot',scene=layout_scene(objs=[tom]),jaw_q=JAW['carrot'])
 for bx,by in ((-0.90,.15),(-0.95,.15),(-0.90,.12),(-0.85,.13),(-1.00,.13)):
  sc=layout_scene(objs=[tom,car]);sc['stations']['cold_box']=(bx,by,0.)
  P[f'Q:cbox_{bx:.2f}_{by:.2f}']=dict(desc='bridge bar between the jaws (set-down / pick moment), box along y',p=box_bar(bx,by,0.),a=(0,0,-1),j=(0,1.,0),scene=sc,jaw_q=0.)
  sc=layout_scene(objs=[tom,car]);sc['stations']['cold_box']=(bx,by,90.)
  P[f'Q:cbox_{bx:.2f}_{by:.2f}_x']=dict(desc='as above, box along x',p=box_bar(bx,by,90.),a=(0,0,-1),j=(-1.,0,0),scene=sc,jaw_q=0.)
 return P
def _tray_probes():
 """Raw-tray picks for alternative tray places, with the slicer at the far left (turned) and the lever
 base at the raw-tray front (-1.47) either stored or out."""
 P={};I=np.eye(3).tolist()
 for tag,dxy in (('BKM',(0.,.24)),('BKM2',(-.045,.24)),('FLF',(-.2825,0.))):
  tom=('tomato',I,tray('tomato',dxy).tolist());car=('carrot',I,tray('carrot',dxy).tolist())
  for lev in (False,True):
   st={'slicer':CANDIDATES['slicer_FLT']['st'][1:]} if tag!='FLF' else {'slicer':CANDIDATES['slicer_BKT12']['st'][1:]}
   if lev:st['lever']=CANDIDATES['tool_TR47']['st'][1:] if tag!='FLF' else CANDIDATES['tool_FL']['st'][1:]
   if tag=='FLF' and lev:continue
   sc=lambda o:dict(stations=dict(st),tray_dxy=dxy,drop_bowls=['potato','leafy_greens'],objs=[o])
   lt='_lever' if lev else ''
   P[f'T{tag}:pick_carrot{lt}']=dict(desc=f'carrot held 8 mm over its ribs, tray moved {dxy}',p=tray('carrot',dxy)+[0,0,.008],a=(0,1,0),j=(0,0,1),held='carrot',scene=sc(tom),jaw_q=JAW['carrot'])
   P[f'T{tag}:pick_tomato{lt}']=dict(desc=f'tomato held 8 mm over its pad, tray moved {dxy}',p=tray('tomato',dxy)+[0,0,.008],a=(0,1,0),j=(1,0,0),held='tomato',scene=sc(car),jaw_q=JAW['tomato'])
 return P
REACH_PROBES=_probes();REACH_PROBES.update(_tray_probes());REACH_PROBES.update(_layout_probes())
