"""R19 seasoning cups (GitHub #5): a NEW layer on top of today's kitchen (kitchen14..17, R18b layout).
No shared file is changed. All sizes are estimates (research/r19_seasoning_cups.md section 5).

CUPS (object frame: origin at the bottom centre, z up; the lug points to object -y; the pour lip is at
object +-x, 90 deg from the lug):
 cupS  ~100 ml brimful, outer radius 32.5 mm, 45 mm tall, deep-drawn 304 stainless (est. 0.08 kg)
 cupL  ~300 ml brimful, outer radius 42.5 mm, 70 mm tall (est. 0.15 kg)
 The body is modelled as a SOLID cylinder (cup + contents envelope, conservative). A short horizontal lug
 (16 x 8 mm bar) carries the keyed 30 mm grip block (30 across the jaws, 24 along the lug, 24 high; the
 same class of block as the lid tab / spider / lever, R16-R17). Block centre LUG_GAP = 25 mm outside the cup
 wall, block top BLOCK_DZ = 6 mm above the rim. Grasp: approach along the lug toward the cup (object +y),
 jaws HORIZONTAL across the block (object x). With the jaws vertical the lower finger (53 mm below the TCP
 when open) would reach below the cup bottom, into the caddy floor.
 The finger extents behind these numbers (TCP frame, jaws open 25 mm): fingertips 30 mm past the TCP,
 finger plates 40-53 mm off the TCP across the jaws, 54 mm wide. So the open fingers straddle the cup at
 >= 40 mm from its axis (S radius 32.5: 7.5 mm clear; L: the fingertips stop 23 mm short of the wall).
 Pour: a roll about the lug axis (= the gripper's approach axis, a wrist-3 roll).

CADDY (six cups, 2 x 3, STEPPED). The plan's flat 2 x 3 caddy cannot be picked with a lug facing the robot:
the back row's lug would face the front row's cups. Here the back row stands on a tier STEP = 75 mm higher,
so the gripper's lowest point (open finger bottom, 24 mm under the TCP) passes over the front row's tallest
part (an L cup's block top, 80 mm) with >= 5 mm when picking a back cup (calc: back S block centre at
75+4+45+6-12 = 118 mm; 118-24 = 94 >= 80+5). Column pitch PX = 100 mm: the open fingers (53 mm off the
target axis) stay 5 mm from an L neighbour (100-53-42.5 = 4.5 mm; the fingers are 54 mm tall, so the
neighbour's lower body is beside them; the screen checks it). Row pitch PY = 95 mm. Footprint ~0.30 x
0.19 m, lugs 25 mm forward of it. Carry handle: a post at the caddy's left end (-x) with the keyed block on
top (the plan's centre bail would arch over the middle column's grasp path; not modelled, and the caddy
carry itself is NOT checked here). The wire rack is modelled as solid plates (floor, tier, end post).
Every box I add is an 8-vertex box MESH (the R11 rule: MuJoCo 3.2.5 reports box-box gaps inside the margin
at about half the true gap; box-mesh is exact).

STAGING CANDIDATES (cfg['r19seas'] = dict(site=..., cups=..., taken=...)):
 T1   caddy on the counter strip behind the plating spots: centre (0.315, 0.3875), lugs toward the robot;
      front-row lug block front face at y 0.26 (plating spots end at y 0.25)
 T2R  / T2L  caddy on a bracket on the cart, right (+x) / left (-x) of the arm base (cart frame x +-0.32,
      0.05 m in front of the base axis), support at 0.86 m, lugs toward the aisle (-y); a 30 x 30 mm bar
      from the mast carries it. These geoms belong to the cart body (robot): the checker then requires
      10 mm between them and the arm OR the gripper (arm_arm_or_frame), stricter than the world's 5 mm.
 T2RC / T2LC  the same, lugs toward the counter (+y)
 T3   narrow rack between plating spot 1 and the cooker: S cups only (an L cup, 85 mm, does not fit the
      80 mm gap between x 0.55 and the cooker at 0.63), single file along y at x 0.59; lugs toward -x
      (toward plating spot 1): from the front the wok's handle block (0.595, 0.17, 1.025) is in the way.
      The open fingers need 53 mm + 32.5 mm + 5 mm to a neighbour, so the pitch is 95 mm and only TWO cups
      fit in y 0.27-0.47 (the R14 cup rail starts at y 0.505). The plan's 4-6 cups do not fit.
cups: 'L' / 'S' for every slot, or {slot: 'S'|'L'|None}; taken: the slot whose cup is in the hand (left out);
z: riser height (m) under the T1 caddy / T3 rack (a solid block on the counter; 0 = on the counter, the plan).
set_approach(pitch): grasp approach pitched down from horizontal (design sweep, default 0).

Slot names: T1/T2: f0 f1 f2 (front row, left to right in the caddy frame), b0 b1 b2 (back row, raised);
T3: s0 (front) s1.
helpers: setup_kitchen() (the R18b state), cfg_extra(), checker(extra) (build + this layer + the R11 held-box
mesh rule + Checker), plume_model(tree) (the R15 plume post-check)."""
import numpy as np,xml.etree.ElementTree as E
from scipy.spatial.transform import Rotation
from scene import fmt
import kitchen15 as K15,kitchen16 as K,kitchen17 as K17
COUNTER=.85
CUP=dict(S=dict(r=.0325,h=.045,ml=100,mass=.08,content_kg=.05),L=dict(r=.0425,h=.070,ml=300,mass=.15,content_kg=.16))   # content: <= 50 ml (S), <= 160 ml liquid (L), r19_seasoning_cups.md 2
BLOCK=np.array([.015,.012,.012]);LUG_GAP=.025;BLOCK_DZ=.006;LUG_KG=.02
PX,PY,STEP,FLOOR_T=.10,.095,.075,.004
HANDLE_H=.10
I3=np.eye(3)
def Rz(a):return K.Rz(a)
def grip_of(size):
 c=CUP[size];return np.array([0.,-(c['r']+LUG_GAP),c['h']+BLOCK_DZ-BLOCK[2]])
def cup_parts(size,prefix):
 c=CUP[size];r,h=c['r'],c['h'];g=grip_of(size);d=-g[1];y0,y1=-(r-.002),-(d-BLOCK[1])
 return [(f'{prefix}_body','cylinder',[0,0,h/2],[r,h/2],I3),
  (f'{prefix}_lug','box',[0,(y0+y1)/2,g[2]],[.008,(y0-y1)/2,.004],I3),
  (f'{prefix}_block','box',g,BLOCK,I3)]
APITCH=0.
def _objs():
 for s in ('S','L'):
  n='cup'+s;K.OBJ[n]=dict(parts=cup_parts(s,'r19c'+s),grip=grip_of(s),a=np.array([0,1.,0]),j=np.array([1.,0,0]),grip_part=f'r19c{s}_block')
_objs()
def set_approach(pitch_deg):
 """Grasp approach pitched pitch_deg below horizontal (from above-front, toward the cup); the jaws stay across
 the block (object x). 0 = horizontal along the lug. Same idea as kitchen16.set_design lid_a / car_a."""
 global APITCH
 APITCH=float(pitch_deg);b=np.radians(APITCH)
 for s in ('S','L'):K.OBJ['cup'+s]['a']=np.array([0,np.cos(b),-np.sin(b)])
def cup_mass(size):
 """(mass kg, CoM in the object frame) of the empty cup incl. lug + block (est.)"""
 c=CUP[size];g=grip_of(size);m=c['mass']+LUG_KG;return m,(c['mass']*np.array([0,0,c['h']/2])+LUG_KG*g)/m
# ---------------- staging candidates ----------------
def caddy_slots(origin,R,cups):
 """Stepped 2 x 3 caddy, origin = footprint centre on the support, R = caddy frame (lugs toward its -y)."""
 out={}
 for row,(y,z) in (('f',(-PY/2,FLOOR_T)),('b',(PY/2,STEP+FLOOR_T))):
  for k,x in enumerate((-PX,0.,PX)):out[f'{row}{k}']=(R.copy(),origin+R@np.array([x,y,z]))
 return out
def site_def(site,z=0.):
 """(frame 'world'|'cart', origin, R caddy frame, kind); z = riser height under the caddy / rack (T1, T3)"""
 if site=='T1':return 'world',np.array([.315,.3875,COUNTER+z]),I3,'caddy'
 if site in ('T2R','T2L','T2RC','T2LC'):
  sx=.32 if site.startswith('T2R') else -.32;R=I3 if not site.endswith('C') else Rz(180.)
  return 'cart',np.array([sx,.08-.05,.86]),R,'caddy'   # cart frame: the arm base axis is at local (0, .08); the caddy centre 5 cm toward the aisle of it
 if site=='T3':return 'world',np.array([.59,0.,COUNTER+z]),Rz(-90.),'rack'   # rack frame -y = world -x (lugs toward plating spot 1)
 raise KeyError(site)
T3_Y=(.315,.41)   # cup centres along y (pitch 95 mm; S radius 32.5)
def slots(site,z=0.):
 """{slot: (R object, p object bottom centre)} in the site's frame (world, or the cart body frame)."""
 fr,o,R,kind=site_def(site,z)
 if kind=='caddy':return caddy_slots(o,R,None)
 return {f's{k}':(R.copy(),np.array([o[0],y,o[2]+.004])) for k,y in enumerate(T3_Y)}
def cart_to_world(q,R,p):
 """Cart-frame pose -> world pose for state q (cart x = q[0], base_y = q[1], yaw q[2] = 0 in every chain)."""
 assert abs(q[2])<1e-9;return R,np.array(p)+[q[0],q[1],0.]
def slot_size(site,cups,slot):
 if site=='T3':return 'S' if (cups if isinstance(cups,str) else (cups or {}).get(slot,'S')) else None
 if isinstance(cups,str):return cups
 return (cups or {}).get(slot,'L')
# ---------------- geometry ----------------
_n=[0]
def _geom(parent,asset,name,typ,pos,size,R=I3,cls=('1','2'),rgba='.75 .76 .78 1',extra=None):
 a=dict(name=name,pos=fmt(pos),quat=fmt(Rotation.from_matrix(R).as_quat()[[3,0,1,2]]),rgba=rgba,contype=cls[0],conaffinity=cls[1],mass='.000001')
 if extra:a.update(extra)
 if typ=='box':
  mn='r19s_mb_'+name;h=np.asarray(size,float)
  E.SubElement(asset,'mesh',name=mn,vertex=' '.join(fmt([sx*h[0],sy*h[1],sz*h[2]]) for sx in(-1,1) for sy in(-1,1) for sz in(-1,1)))
  a.update(type='mesh',mesh=mn)
 else:a.update(type=typ,size=fmt(size))
 return E.SubElement(parent,'geom',**a)
def _bx(parent,asset,name,lo,hi,R,o,**kw):
 lo,hi=np.asarray(lo,float),np.asarray(hi,float);return _geom(parent,asset,name,'box',o+R@((lo+hi)/2),(hi-lo)/2,R,**kw)
def caddy_parts(parent,asset,o,R,pre,kw):
 rL=CUP['L']['r'];xw=PX+rL+.005
 _bx(parent,asset,pre+'floor_f',[-xw,-PY/2-rL,0],[xw,-PY/2+rL+.002,FLOOR_T],R,o,**kw)
 _bx(parent,asset,pre+'tier',[-xw,-PY/2+rL+.004,0],[xw,PY/2+rL,STEP+FLOOR_T],R,o,**kw)
 _bx(parent,asset,pre+'post',[-xw-.012,-.015,0],[-xw,.015,HANDLE_H],R,o,**kw)
 _bx(parent,asset,pre+'handle_block',[-xw-.012-.024,-.015,HANDLE_H-.012],[-xw-.012,.015,HANDLE_H+.012],R,o,**kw)
def add(tree,cfg):
 """Add the staged cups (and their caddy / rack / bracket) for cfg['r19seas'] (no-op without it)."""
 sc=cfg.get('r19seas')
 if not sc:return tree
 site=sc['site'];zr=float(sc.get('z',0.));fr,o,R,kind=site_def(site,zr);asset=tree.getroot().find('asset')
 if asset is None:asset=E.SubElement(tree.getroot(),'asset')
 if fr=='world':parent=tree.find('worldbody');kw=dict(cls=('1','2'))
 else:   # the cart body (robot side): same contact classes as the cart's own geoms
  parent=tree.find(".//body[@name='rail_structure']");kw=dict(cls=('2','3'),extra=dict(margin='.01'))
 pre=('R_cart_r19s_' if fr=='cart' else 'r19s_')
 if zr>0:   # riser (a solid block from the counter to the caddy / rack support, its footprint)
  hx,hy=((PX+CUP['L']['r']+.005,PY/2+CUP['L']['r']) if kind=='caddy' else (CUP['S']['r']+.002,(T3_Y[-1]-T3_Y[0])/2+CUP['S']['r']+.005))
  cy=0. if kind=='caddy' else (T3_Y[0]+T3_Y[-1])/2
  _bx(parent,asset,pre+'riser',[-hx,cy-hy,-zr] if kind=='caddy' else [o[0]-hx,cy-hy,COUNTER],[hx,cy+hy,-.0005] if kind=='caddy' else [o[0]+hx,cy+hy,COUNTER+zr-.0005],R if kind=='caddy' else I3,o if kind=='caddy' else np.zeros(3),**kw)
 if kind=='caddy':
  caddy_parts(parent,asset,o,R,pre+'caddy_',kw)
  if fr=='cart':   # bracket: a 30 x 30 mm bar from the mast (cart frame y -0.17) to under the caddy, then the caddy rests on it
   ym=-.17;yc=o[1];_bx(parent,asset,pre+'bracket_x',[min(0,o[0]),ym-.015,o[2]-.03],[max(0,o[0]),ym+.015,o[2]],I3,np.zeros(3),**kw)
   _bx(parent,asset,pre+'bracket_y',[o[0]-.015,ym-.015,o[2]-.03],[o[0]+.015,yc,o[2]],I3,np.zeros(3),**kw)
 else:   # T3 rack: a 4 mm plate under the file of cups
  r=CUP['S']['r'];_bx(parent,asset,pre+'rack',[o[0]-r-.002,T3_Y[0]-r-.005,0],[o[0]+r+.002,T3_Y[-1]+r+.005,.004],I3,np.array([0,0,o[2]]),**kw)
 for sl,(Rs,ps) in slots(site,zr).items():
  if sl==sc.get('taken'):continue
  size=slot_size(site,sc.get('cups','L'),sl)
  if size is None:continue
  for n,t,q,s,Rp in cup_parts(size,f'{pre}cup_{sl}'):
   _geom(parent,asset,n,t,ps+Rs@np.asarray(q),s,Rs@Rp,**kw)
 return tree
# ---------------- the R18b kitchen + this layer as one checker ----------------
BASE=dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None})
def setup_kitchen():
 """Today's (R18b) layout: R17 design, spatula lying flipped at (-1.15, .30) on an 8 deg pad, spider at (1.52, .36)."""
 K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.)
 K.TOOL_XY['spatula']=(-1.15,.30);K.SPAT_ELEV=8.;K.SPAT_YAW=0.;K.SPAT_ROLL=180.;K.TOOL_XY['spider']=(1.52,.36)
def meshheld(tree):
 """R11 rule (as r19smooth.py MESHHELD): the held parts kitchen14+ attach to R_tool after scene.build's mesh pass
 become identical 8-vertex box meshes."""
 asset=tree.getroot().find('asset');tool=tree.find(".//body[@name='R_tool']")
 for g in tool.iter('geom'):
  if g.get('type')!='box':continue
  h=np.fromstring(g.get('size'),sep=' ');mn='mb19_'+g.get('name')
  E.SubElement(asset,'mesh',name=mn,vertex=' '.join(fmt([sx*h[0],sy*h[1],sz*h[2]]) for sx in(-1,1) for sy in(-1,1) for sz in(-1,1)))
  g.set('type','mesh');g.set('mesh',mn);g.attrib.pop('size',None)
 return tree
def build_tree(extra):
 import chain
 from scene import build
 cfg=chain.chain_cfg('SD',**{**BASE,**extra});tree,meta=build(cfg,None);add(tree,cfg);meshheld(tree);return tree,meta
def checker(extra):
 from checker import Checker
 tree,meta=build_tree(extra);return Checker(tree,meta),tree
PLUME_R=.20;HOOD_Z=1.25
PLUME_SKIP=('R_gripper_r19c','R_gripper_spatula','R_gripper_r15_wok','R_cart','R_dock')   # the held tool, the cart (as r15reach.py)
def plume_model(tree,radius=PLUME_R):
 """R15 plume rule (r15reach.py): every robot geom except the held tool and the cart stays >= radius from the
 wok axis between the rim and the hood bottom (1.25 m). Returns f(q) -> min distance in mm (< 0 = inside)."""
 import mujoco,copy
 t=copy.deepcopy(tree);E.SubElement(t.find('worldbody'),'geom',name='r15_plume',type='cylinder',pos=fmt([K15.WOK0[0],K15.WOK0[1],(K15.RIM_Z+HOOD_Z)/2]),size=fmt([radius,(HOOD_Z-K15.RIM_Z)/2]),contype='0',conaffinity='0')
 pm=mujoco.MjModel.from_xml_string(E.tostring(t.getroot(),encoding='unicode'));pd=mujoco.MjData(pm);pl=pm.geom('r15_plume').id
 rob=[g for g in range(pm.ngeom) if pm.geom(g).name.startswith('R_') and not pm.geom(g).name.startswith(PLUME_SKIP)]
 def f(q,which=False):
  pd.qpos[:]=q;mujoco.mj_kinematics(pm,pd);ft=np.zeros(6);v=min((mujoco.mj_geomDistance(pm,pd,g,pl,1.,ft),g) for g in rob)
  return (1000*v[0],pm.geom(v[1]).name) if which else 1000*v[0]
 return f
