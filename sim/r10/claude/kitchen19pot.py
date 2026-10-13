"""R19 pot zone (GitHub #37 spider rest, #8 lid rack): a layer on top of kitchen16 / kitchen17. New file.
NOTHING changes unless install() is called (the r19pot_*.py scripts call it from their options); every
other script and every stored result keeps the R17/R18b layout.

1. Spider rest (#37). Its position is kitchen16.TOOL_XY['spider'] (r17chain.py SPX / SPY, default R17 spot
   (1.52, 0.36)); install(spider=(x, y)) sets it for every scene built in this process. The rest is the
   kitchen16 cradle pad (80 x 80 x 20 mm, `r16_rest_spider`) with the spider lying on it in its use frame
   (bowl level, handle rising toward the robot at 45 deg, keyed grip block `r16_spider_block` at the end).
2. Keyed lid rack (#8), install(rack='keyed'): the R16 rack (a flat base and two low fins 19 mm off the lid,
   `r16_rack_*`) is replaced by a V-SADDLE with lead-in V-grooves, `r19pot_rack_*`:
   - two pads under the upright lid's rim, at y = cy -/+ PAD_S (90 mm) from the lid centre. Each pad holds the
     rim edge in a V-groove (90 deg included, flanks FLANK_H = 20 mm long along the flank, 6 mm thick) whose
     groove line is the rim's tangent at that point;
   - the two pads together form a saddle (contact normals 35.5 deg off vertical, toward the lid centre):
     gravity centres the lid along y (along the rack) and in height; the grooves centre the rim plane in x
     and square it (rotation about z and y); the lid is lowered straight down into it;
   - lead-in (capture): a rim edge that lands anywhere on a flank slides to the groove line. Mouth half-width
     at the flank top = APEX_A + FLANK_H sin 45 = 19.6 mm from the groove centre, i.e. the 10 mm rim is
     captured for an x error up to +-14.6 mm; along y the saddle captures up to about +-PAD_S. Both exceed
     the 3-5 mm asked in #8; the design value claimed is +-5 mm (half the geometric capture, for friction and
     the curved rim edge: with the rim's 155 mm radius the edge drops 5.2 mm over +-40 mm along the groove).
   - seated pose = kitchen16.pose('lid', 'rack') UNCHANGED (rim plane x 1.725-1.735, centre y 0.25, z 1.017):
     the rim corners sit SEAT_CLEAR (0.5 mm) off both flanks there, so every stored lid state outside the
     last 50 mm is geometrically the same scene except the rack parts themselves;
   - the rack stays inside the R16 rack footprint (x 1.70-1.80, y 0.08-0.42 on the counter end).
   - in-plane rotation of the lid (about x) is held by friction in the grooves (est.: 0.8 kg lid, mu 0.3,
     friction torque ~0.4 N.m vs ~0.06 N.m from the tab); it is not a positive key (see R19_POTZONE.md).
3. Lid insertion contact window (DECISIONS 2026-10-08, "Lift/approach window"): window() returns the
   declared window of the lid set: the last <= 50 mm of the straight move down the rack's insertion axis
   (world -z), TCP from the release pose (kf 'in the rack', 4 mm above the seat) up to 50 mm above it, rotation
   fixed; the intended contacts are ONLY the held lid's parts vs the keyed rack's parts (the support). Nothing
   else gets a window. r19pot_chain.py / r19pot_check.py / r19pot_tol.py apply it."""
import numpy as np,xml.etree.ElementTree as E
import kitchen16 as K
from scene import fmt
PAD_S=.09          # m: pad contact offset along y from the lid centre
HALF=np.radians(45.)   # flank half-angle from the contact normal (90 deg V)
FLANK_H=.020;FLANK_T=.006;PAD_L=.040;SUPPORT_D=.040;SUPPORT_W=.020   # flank length along the flank, thickness; pad length along the groove; support block
RIM_HALF=.005;SEAT_CLEAR=.0005   # lid rim half-thickness (kitchen16 r16_lid_rim); rim corner to flank at the seated pose
APEX_A=RIM_HALF/np.tan(HALF)+SEAT_CLEAR/np.sin(HALF)   # apex depth below the rim edge along the contact normal
PLATE=dict(t=.005)   # connecting plate under the lid, between the pads
WINDOW_L=.050      # m: the declared window length (DECISIONS: <= 50 mm)
ACTIVE=dict(rack=None,spider=None)
_ORIG_ADD=None
def _lid_rack_frame():
 """World centre of the rim ring (mid-plane), lid centre (y, z) and radius at the seated pose."""
 R,p=K.pose('lid','rack');rim=next(q for q in K.OBJ['lid']['parts'] if q[0]=='r16_lid_rim')
 c=R@np.asarray(rim[2],float)+p;return R,p,c,rim[3][0]
def rack_parts():
 """Keyed rack geoms: list of (name, centre, half sizes, R) boxes in the world."""
 Rl,pl,c,Rr=_lid_rack_frame();out=[];ex=np.array([1.,0,0])
 for sg,tag in ((-1,'f'),(1,'b')):
  s=PAD_S;h=np.sqrt(Rr**2-s**2);C=np.array([c[0],c[1]+sg*s,c[2]-h])
  n=np.array([0,-sg*s,h])/Rr;t=np.array([0,h,sg*s])/Rr;A=C-n*APEX_A
  for fs,fn in ((1,'xp'),(-1,'xm')):
   u=np.cos(HALF)*n+fs*np.sin(HALF)*ex;m=-fs*np.cos(HALF)*ex+np.sin(HALF)*n   # flank direction (from the apex), normal into the groove
   M=np.c_[u,t,np.cross(u,t)]
   if np.dot(M[:,2],m)<0:M=np.c_[u,-t,np.cross(u,-t)]   # local z = +m (into the groove) keeps det +1
   ctr=A+u*FLANK_H/2-M[:,2]*FLANK_T/2
   out.append((f'r19pot_rack_{tag}_{fn}',ctr,np.array([FLANK_H/2,PAD_L/2,FLANK_T/2]),M))
  Ms=np.c_[ex,t,np.cross(ex,t)]
  out.append((f'r19pot_rack_{tag}_support',A-n*SUPPORT_D/2,np.array([SUPPORT_W,PAD_L/2,SUPPORT_D/2]),Ms))
 y0,y1=c[1]-PAD_S-.02,c[1]+PAD_S+.02
 out.append(('r19pot_rack_plate',np.array([c[0],(y0+y1)/2,.85+PLATE['t']/2]),np.array([SUPPORT_W+.005,(y1-y0)/2,PLATE['t']/2]),np.eye(3)))
 return out
def capture():
 """Geometric lead-in capture (m) of the keyed rack: x (across the rim plane), and y (along the rack)."""
 mouth=APEX_A+FLANK_H*np.sin(HALF);return dict(x_capture_m=round(mouth-RIM_HALF,4),y_capture_m=round(PAD_S,3),mouth_half_width_m=round(mouth,4),
  design_claim_m=.005,note='a rim edge landing on a flank slides to the groove line (45 deg flanks); along y the saddle (contacts 35.5 deg off vertical) centres the circle')
def _add_rack(world):
 for n,ctr,hs,M in rack_parts():
  q=K.quat(M);E.SubElement(world,'geom',name=n,type='box',pos=fmt(ctr),size=fmt(hs),quat=fmt(q),rgba='.35 .55 .75 1',contype='1',conaffinity='2',mass='.000001')
def _wrapped_add(tree,world,cfg):
 _ORIG_ADD(tree,world,cfg)
 if ACTIVE['rack']=='keyed' or cfg.get('r19pot_rack')=='keyed':
  for g in list(world.iter('geom')):
   if g.get('name','').startswith('r16_rack_'):
    for par in world.iter():
     if g in list(par):par.remove(g);break
  _add_rack(world)
def install(rack=None,spider=None):
 """Activate the layer in this process (every later scene.build): rack='keyed' and / or spider=(x, y)."""
 global _ORIG_ADD
 if rack is not None:
  ACTIVE['rack']=rack
  if _ORIG_ADD is None:_ORIG_ADD=K.add;K.add=_wrapped_add
 if spider is not None:
  import kitchen17   # noqa: F401  (sets the R17 spot first, then ours wins)
  ACTIVE['spider']=(float(spider[0]),float(spider[1]));K.TOOL_XY['spider']=ACTIVE['spider']
def install_kv(KV):
 """Options as KEY=VALUE (the scripts' style): RACK=keyed, SPX=<x> SPY=<y>."""
 install(rack=KV.get('RACK'),spider=(KV['SPX'],KV['SPY']) if 'SPX' in KV else None)
 return dict(ACTIVE)
def window(sign=-1):
 """The declared lid insertion window (world): the TCP pose at the release keyframe ('in the rack', 4 mm above
 the seat), the retreat axis (+z: the window is the TCP on [origin, origin + WINDOW_L * axis]) and rotation, the
 parts (held lid geoms, 'R_gripper_' + lid part, without the grip part) and the faces (keyed rack geoms)."""
 R,p=K.pose('lid','rack');pt,Rt=K.tcp_pose('lid',R,p+[0,0,.004],sign)
 o=K.OBJ['lid'];parts=['R_gripper_'+q[0] for q in o['parts'] if q[0]!=o['grip_part']]
 return dict(kind='grasp_release_support',object='lid',support='r19pot_rack',origin=np.asarray(pt,float),axis=np.array([0,0,1.]),length_m=WINDOW_L,
  rotation=np.asarray(Rt,float),parts=parts,faces=[n for n,_,_,_ in rack_parts()],lateral_tol_m=5e-5,rot_tol=5e-4,
  rule='DECISIONS 2026-10-08 lift/approach window: straight move <= 50 mm along the declared insertion axis (the rack V-grooves, world z); only the lid parts vs the rack parts')
def window_pot(sign=-1):
 """OPTIONAL second window (reported separately): the lid's existing straight lift off the pot (r17chain ACT=lid:
 grasp at the seated lid, then straight up to kf 1, 20 mm above the seat, before the horizontal slide), i.e. a retreat
 of 20 mm (<= 50 mm) along the pot's face normal (+z); intended contact: the held lid parts vs the pot rim
 (r16_pot_wall*). The same DECISIONS rule; R17 treated its first 8 mm as an unchecked seat."""
 R,p=K.lid_on({});pt,Rt=K.tcp_pose('lid',R,p,sign)
 o=K.OBJ['lid'];parts=['R_gripper_'+q[0] for q in o['parts'] if q[0]!=o['grip_part']]
 return dict(kind='grasp_release_support',object='lid',support='r16_pot',origin=np.asarray(pt,float),axis=np.array([0,0,1.]),length_m=.020,
  rotation=np.asarray(Rt,float),parts=parts,faces=[],face_prefix='r16_pot_wall',lateral_tol_m=5e-5,rot_tol=5e-4,
  rule='DECISIONS 2026-10-08 lift/approach window: straight lift 20 mm along the pot face normal (world z); only the lid parts vs the pot rim')
def windows(sign=-1,rack=True,pot=False):
 """The declared windows of the lid set: the keyed-rack insertion (with the keyed rack) and, optionally, the lift off the pot."""
 return ([window(sign)] if rack else [])+([window_pot(sign)] if pot else [])
def allowed_pairs(Ws,names,tcp_p,tcp_R):
 """Pairs (frozensets of geom names) allowed by the windows the TCP pose is in; and how many windows are active."""
 out=set();n=0;ns=set(names)
 for W in Ws:
  if not in_window(W,tcp_p,tcp_R):continue
  n+=1;faces=[b for b in names if b in W['faces'] or (W.get('face_prefix') and b.startswith(W['face_prefix']))]
  out|={frozenset([a,b]) for a in W['parts'] if a in ns for b in faces}
 return out,n
def in_window(W,tcp_p,tcp_R):
 """True if a TCP pose lies on the declared window segment with the window rotation."""
 d=np.asarray(tcp_p)-W['origin'];ax=float(d@W['axis']);lat=float(np.linalg.norm(d-ax*W['axis']))
 return bool(lat<=W['lateral_tol_m'] and -W['lateral_tol_m']<=ax<=W['length_m']+W['lateral_tol_m'] and np.max(abs(np.asarray(tcp_R)-W['rotation']))<=W['rot_tol'])
