"""R12 3D-printed fingers for the DH PGC-140-50 (design study, 2026-10-11).

Tool frame (R_tool): x = approach (fingertips at +x), y = jaw axis (plus finger
at +y), z = pad height. For every design the TCP (R_prep, tool origin) is the held
item's centre; the housing, jaws and fingers are placed relative to it.
Inherited stock model (no design): housing face 35 mm behind the TCP, fingers
protrude 37.5 mm past it, so the item sits at the fingertip.

Design parameters:
 P   finger protrusion past the housing face (m)
 D   grasp depth: housing face to item centre (m)
 c   crank: the pads sit c below the jaw axis in tool z (the housing rides higher)
 H   pad height (tool z); T structural thickness; tp TPU thickness at the datum
 fo  closed half gap: the pad datum (deepest pad point) is at |y| = fo + q
 profile 'flat' | 'channel' (horizontal V groove along x: face angle phi, half
         width w) | 'pocket' (inverted pyramid centred on the TCP) | 'finray'
Planning model (checker): each finger is one convex box hull named R_finger_*,
so held-item contact stays the registered grasp. Dynamics model: dyn_parts()."""
import numpy as np,xml.etree.ElementTree as E
from scipy.spatial.transform import Rotation
FACE0=.035          # stock housing face behind the TCP
JAW_X,JAW_Y=-.02,.004  # stock jaw body position in the tool frame
MOUNT=.0375         # finger length inside the housing face (stock box starts at -.0725)
DESIGNS={
 'L':dict(label='加长平直 TPU 垫',P=.075,D=.045,c=.02,H=.04,T=.008,tp=.004,fo=.015,profile='flat'),
 'V':dict(label='横向 V 槽托指',P=.075,D=.045,c=.02,H=.046,T=.008,tp=.004,fo=.0225,profile='channel',phi=30.,w=.02),
 'K':dict(label='金字塔窝指',P=.075,D=.045,c=.02,H=.046,T=.008,tp=.004,fo=.0225,profile='pocket',phi=30.,w=.02),
 # Dual zone: rigid PETG rims (flush with the datum) at |z|>=w carry hard items in force
 # mode; a sprung soft centre (silicone, ks N/m, travel) protrudes e and alone touches
 # round items, so a position-mode close sets a gentle force ks*squeeze.
 'D':dict(label='双区指（软中带+硬边）',P=.075,D=.045,c=.02,H=.048,T=.008,tp=.004,fo=.016,profile='dual',w=.019,e=.001,ks=1500.,travel=.006,squeeze=.004),
 'R':dict(label='鳍条软指 (Fin Ray)',P=.085,D=.045,c=.02,H=.04,T=.022,tp=.0015,fo=.015,profile='finray',n=6,K=.15,kroot=10.,krib=.01,rib_tilt=-25.),
}
# Item cross-sections for the jaw standoff: kind, half grasp width (m), half height (tool z, m)
ITEM={'carrot':('cyl_z',.0175,None),'tomato':('sphere',.035,.03),'potato':('sphere',.0325,.045),'pusher':('box',.015,None),
 'greens':('box',.05,None),'holder':('box',.015,None),'catch_tray':('box',.015,None)}
def get(cfg):
 d=cfg.get('finger');return None if d is None else dict(DESIGNS[d],key=d) if isinstance(d,str) else d
def rim(d):
 """Inward protrusion of the pad rims above the datum (groove depth)."""
 if d['profile']=='dual':return d['e']
 return d['w']*np.tan(np.radians(d['phi'])) if d['profile'] in ('channel','pocket') else 0.
def profile_z(d,t):
 """Pad surface height u (inward, from the datum) at tool-z offset t from the pad centre."""
 if d['profile'] in ('channel','pocket'):return np.minimum(abs(t),d['w'])*np.tan(np.radians(d['phi']))
 if d['profile']=='dual':return np.where(abs(t)<d['w'],d['e'],0.)
 return np.zeros_like(t)
def standoff(d,item,r=None,rz=None):
 """Distance from the item centre to the pad datum along the jaw axis when the pads touch."""
 kind,r0,rz0=ITEM[item];r=r0 if r is None else r;rz=(rz0 if rz0 else r) if rz is None else rz
 t=np.linspace(-d['H']/2,d['H']/2,2001);u=profile_z(d,t)
 if kind=='sphere':
  inside=abs(t)<rz;e=np.where(inside,r*np.sqrt(np.clip(1-(t/rz)**2,0,1)),-1)
  return float(np.max(np.where(inside,u+e,-1)))
 return float(np.max(u)+r)  # cylinder along z or flat-sided box: rests on the highest pad points
def jaw_q(cfg,held,r=None):
 d=get(cfg)
 if held is None:return .025
 if d['profile']=='dual':
  # hard items press the soft centre fully back onto the rims (force mode);
  # round items are held by the soft centre only, squeezed by d['squeeze']
  kind=ITEM[held][0];r_=ITEM[held][1] if r is None else r
  so=standoff(d,held,r)-d['squeeze'] if kind=='sphere' else r_
  return float(np.clip(so-d['fo'],0,.025))
 return float(np.clip(standoff(d,held,r)-d['fo'],0,.025))
def fmt(v):return ' '.join(f'{float(x):.12g}' for x in v)
def local(d,s,x_tool,u,z_tool):
 """Jaw-body-local coordinates of a tool-frame point given by (x, inward u from the datum, z)."""
 return np.array([x_tool-(.015-d['D']),s*(d['fo']-JAW_Y-u),z_tool-d['c']])
def apply(tree,cfg):
 """Planning model: move the TCP to the item centre for this design and replace
 the stock fingers by each finger's convex box hull (mount + beam + pad)."""
 d=get(cfg);tool=tree.find(".//body[@name='R_tool']")
 q=np.fromstring(tool.get('quat'),sep=' ');R=Rotation.from_quat(q[[1,2,3,0]]).as_matrix()
 dx=d['D']-FACE0;sh=np.array([-dx,0,d['c']])
 tool.set('pos',fmt(np.fromstring(tool.get('pos'),sep=' ')-R@sh))
 for ch in tool:
  if ch.tag in ('geom','body','inertial') and ch.get('name')!='R_prep':
   ch.set('pos',fmt(np.fromstring(ch.get('pos','0 0 0'),sep=' ')+sh))
 g_=rim(d)
 for jn,s in (('R_jaw_minus',-1),('R_jaw_plus',1)):
  jb=tool.find(f"body[@name='{jn}']");g=jb.find('geom')
  a=local(d,s,-d['D']-MOUNT,g_,min(-d['H']/2,d['c']-.01));b=local(d,s,-d['D']+d['P'],-d['tp']-d['T'],max(d['H']/2,d['c']+.01))
  g.set('pos',fmt((a+b)/2));g.set('size',fmt(abs(b-a)/2))
 return tree
# ---------------- dynamics parts (floating gripper copy in dyn.py) ----------------
def _box(parent,name,c,half,R,fr,rgba='.92 .9 .85 1',contact=True):
 g=E.SubElement(parent,'geom',name=name,type='box',pos=fmt(c),size=fmt(half),quat=fmt(Rotation.from_matrix(R).as_quat()[[3,0,1,2]]),rgba=rgba,friction=fr,margin='0')
 g.set('contype','4' if contact else '0');g.set('conaffinity','0');return g
def _prism(root,parent,name,P3,out,fr,rgba='.92 .9 .85 1'):
 """Convex triangular prism (surface triangle P3, extruded 3 mm along out)."""
 V=np.r_[P3,P3+.003*out];asset=root.find('asset')
 E.SubElement(asset,'mesh',name='m_'+name,vertex=' '.join(fmt(v) for v in V))
 return E.SubElement(parent,'geom',name=name,type='mesh',mesh='m_'+name,rgba=rgba,friction=fr,margin='0',contype='4',conaffinity='0')
def dyn_parts(root,jaw,s,d,fr):
 """Contact geometry of one finger inside its (floating copy) jaw body. jaw: the
 body element; s: -1 minus, +1 plus; fr: pad friction string."""
 nm=jaw.get('name');x0,x1=-d['D'],-d['D']+d['P'];H=d['H'];tp=d['tp']
 for g in jaw.findall('geom'):g.set('contype','0');g.set('conaffinity','0');g.set('rgba','0 0 0 0')
 out=np.array([0,s,0.])  # outward (away from the item) in the jaw frame
 # structural beam behind the pad (no food contact); for the Fin Ray only the mount block
 p=d['profile']
 a=local(d,s,x0-MOUNT,-tp,-H/2);b=local(d,s,x1 if p!='finray' else x0,-tp-d['T'],H/2)
 _box(jaw,nm+'_beam',(a+b)/2,abs(b-a)/2,np.eye(3),fr,'.55 .6 .65 1',False)
 if p=='flat':
  a=local(d,s,x0,0,-H/2);b=local(d,s,x1,-tp,H/2);_box(jaw,nm+'_pad',(a+b)/2,abs(b-a)/2,np.eye(3),fr)
 elif p in ('channel','pocket'):
  g_=rim(d);w=d['w'];th=.003
  if p=='channel':
   # faces of the horizontal V and the flat rims, each a thin box extruded along x
   pts=[(-H/2,g_),(-w,g_),(0,0),(w,g_),(H/2,g_)]
   for i,((z0,u0),(z1,u1)) in enumerate(zip(pts[:-1],pts[1:])):
    A=local(d,s,x0,u0,z0);B=local(d,s,x1,u1,z1);C=(A+B)/2
    tz=np.array([0,B[1]-A[1],B[2]-A[2]]);L=np.linalg.norm(tz);tz/=L;nrm=np.cross([1,0,0],tz)
    if nrm@out<0:nrm=-nrm
    Rm=np.c_[[1,0,0],tz,nrm]
    if np.linalg.det(Rm)<0:Rm[:,2]*=-1;nrm=Rm[:,2]
    _box(jaw,f'{nm}_ch{i}',C+nrm*th/2,[(x1-x0)/2,L/2,th/2],Rm,fr)
  else:
   wx=w;apex=local(d,s,0,0,0);c4=[local(d,s,sx*wx,g_,sz*w) for sx,sz in ((-1,-1),(1,-1),(1,1),(-1,1))]
   for i in range(4):_prism(root,jaw,f'{nm}_pk{i}',np.array([apex,c4[i],c4[(i+1)%4]]),out,fr)
   for i,(xa,xb,za,zb) in enumerate([(x0,-wx,-H/2,H/2),(wx,x1,-H/2,H/2),(-wx,wx,w,H/2),(-wx,wx,-H/2,-w)]):
    A=local(d,s,xa,g_,za);B=local(d,s,xb,g_-th,zb);_box(jaw,f'{nm}_rim{i}',(A+B)/2,abs(B-A)/2,np.eye(3),fr)
 elif p=='finray':finray(root,jaw,s,d,fr)
 elif p=='dual':
  w=d['w'];car=jaw
  if d.get('rock'):
   # R13 self-aligning pad: rims + soft centre on a carrier that rocks about the
   # approach axis (pin behind the pad), so both rims meet tapered or curved items.
   # Range in radians (R13 bench compiler); weak centring spring.
   car=E.SubElement(jaw,'body',name=nm+'_rock',pos='0 0 0')
   E.SubElement(car,'joint',name=nm+'_rock_j',type='hinge',pos=fmt(local(d,s,(x0+x1)/2,-tp-d['T']/2,0)),axis='1 0 0',
    stiffness=str(d.get('krock',.05)),damping='.002',range=f"{-np.radians(d['rock'])} {np.radians(d['rock'])}",limited='true',armature='1e-5')
   E.SubElement(car,'inertial',pos=fmt(local(d,s,(x0+x1)/2,-tp,0)),mass='.01',diaginertia='2e-6 2e-6 2e-6')
  # one pad, or R13 'tines': several narrow dual pads at z offsets (a fork whose
  # tines run in the slot-tray channels; supported grasps of long items)
  for ti,z0 in enumerate(d.get('tines',[0.])):
   sfx='' if ti==0 else f'_t{ti}'
   for i,(za,zb) in enumerate(((-H/2,-w),(w,H/2))):
    A=local(d,s,x0,0,z0+za);B=local(d,s,x1,-tp,z0+zb);_box(car,f'{nm}{sfx}_rim{i}',(A+B)/2,abs(B-A)/2,np.eye(3),fr,'.55 .6 .65 1')
   # sprung soft centre: slide joint along the outward direction, compressed q>=0
   A=local(d,s,x0,d['e'],z0-w+.0005);B=local(d,s,x1,d['e']-.004,z0+w-.0005)
   sb=E.SubElement(car,'body',name=nm+sfx+'_soft',pos=fmt((A+B)/2))
   E.SubElement(sb,'joint',name=nm+sfx+'_soft_j',type='slide',axis=fmt(out),stiffness=str(d['ks']),damping=str(d['ks']/200),range=f"0 {d['travel']}",limited='true',armature='1e-4')
   E.SubElement(sb,'inertial',pos='0 0 0',mass='.005',diaginertia='1e-6 1e-6 1e-6')
   _box(sb,nm+sfx+'_softpad',[0,0,0],abs(B-A)/2,np.eye(3),fr)
  if len(d.get('tines',[0.]))>1:  # bridge joining the tines behind the pads (no food contact)
   zs=d['tines'];A=local(d,s,x0-.004,-tp,min(zs)-H/2);B=local(d,s,x0+.004,-tp-d['T'],max(zs)+H/2)
   _box(car,nm+'_bridge',(A+B)/2,abs(B-A)/2,np.eye(3),fr,'.55 .6 .65 1',False)
  if d.get('lip'):
   # R13 catch lip: a thin plate at the fingertip pointing inward (under the item),
   # inner edge raised by lip_ang; touches down beside the item and closes under it.
   Ls,lt,be=d['lip'],d.get('lip_t',.0015),np.radians(d.get('lip_ang',15.))
   v=np.array([-np.sin(be),-s*np.cos(be),0.]);z=np.array([0,0,1.]);xb=np.cross(v,z);xb/=np.linalg.norm(xb)
   if xb[0]>0:xb=-xb
   Rm=np.c_[xb,v,z]
   if np.linalg.det(Rm)<0:Rm[:,0]*=-1
   P0=local(d,s,x1,0,0)-np.array([lt/2,0,0])
   _box(car,nm+'_lip',P0+v*Ls/2,[lt/2,Ls/2,H/2],Rm,fr,'.55 .6 .65 1')
def finray(root,jaw,s,d,fr):
 """Fin Ray finger as a pseudo-rigid-body linkage (planar, in the x-y plane of the
 jaw): a front strap (pad side) and a back strap, joined at the tip, with n-1 ribs
 pinned to both straps. Flexure hinges are revolute joints about z with torsional
 stiffness K (calibrated in finray_calibrate). Only the front strap touches food."""
 nm=jaw.get('name');n=d['n'];x0,x1=-d['D'],-d['D']+d['P'];W=d['T'];H=d['H'];K=d.get('K',.05)
 xs=np.linspace(x0,x1,n+1)
 # front strap nodes at u=0 (datum), back strap nodes on the line from (x0,u=-W) to the tip (x1,u=0)
 # ribs leave the front strap tilted towards the base by rib_tilt (classic Fin Ray layout)
 tl=np.tan(np.radians(d.get('rib_tilt',0.)));ub=lambda x:-W*(1-(x-x0)/(x1-x0))
 xb=[x0]+[x-(-ub(x))*tl for x in xs[1:-1]]+[x1]
 for _ in range(20):xb=[x0]+[x-(-ub(xb_))*tl for x,xb_ in zip(xs[1:-1],xb[1:-1])]+[x1]
 F=[local(d,s,x,0,0) for x in xs];B=[local(d,s,x,ub(x),0) for x in xb]
 def chain(prefix,P,thick,contact,rgba):
  par=jaw;bodies=[]
  for i in range(n):
   a,b=P[i],P[i+1];v=b-a;L=np.linalg.norm(v);ang=np.arctan2(v[1],v[0])
   pos=a if par is jaw else np.array([Lp,0,0])
   bd=E.SubElement(par,'body',name=f'{prefix}{i}',pos=fmt(pos),quat=fmt(Rotation.from_euler('z',ang-(angp if par is not jaw else 0)).as_quat()[[3,0,1,2]]))
   k_=K*(d.get('kroot',10.) if i==0 else 1.)  # clamped root is much stiffer than the strap flexures
   E.SubElement(bd,'joint',name=f'{prefix}{i}_j',type='hinge',axis='0 0 1',stiffness=str(k_),damping=str(k_/50),armature='1e-6')
   E.SubElement(bd,'inertial',pos=fmt([L/2,0,0]),mass='.002',diaginertia='1e-7 1e-7 1e-7')
   # strap slab: inner face on the node line (front strap: towards the item = -s*y)
   off=-s*thick/2 if contact else 0.
   E.SubElement(bd,'geom',name=f'{prefix}{i}_g',type='box',pos=fmt([L/2,-off,0]),size=fmt([L/2,thick/2,H/2]),rgba=rgba,friction=fr,margin='0',
    contype='4' if contact else '0',conaffinity='0')
   bodies.append((bd,L,ang));par=bd;Lp=L;angp=ang
  return bodies
 # The local frame of each strap segment: x along the segment. For the front strap the
 # item side is local -y*s... handled by placing the slab behind the node line.
 fb=chain(nm+'_f',F,d['tp']+.0015,True,'.92 .9 .85 1');bb=chain(nm+'_b',B,.0015,False,'.85 .83 .78 1')
 eq=root.find('equality')
 if eq is None:eq=E.SubElement(root,'equality')
 # tip: front and back strap ends coincide
 E.SubElement(eq,'connect',body1=fb[-1][0].get('name'),body2=bb[-1][0].get('name'),anchor=fmt([fb[-1][1],0,0]),solref='.002 1')
 # ribs: rigid links between front node i and back node i (i=1..n-1), pinned both ends
 for i in range(1,n):
  par,L,ang=fb[i-1];a,bk=F[i],B[i];v=bk-a;Lr=np.linalg.norm(v);rang=np.arctan2(v[1],v[0])-ang
  rb=E.SubElement(par,'body',name=f'{nm}_r{i}',pos=fmt([L,0,0]),quat=fmt(Rotation.from_euler('z',rang).as_quat()[[3,0,1,2]]))
  E.SubElement(rb,'joint',name=f'{nm}_r{i}_j',type='hinge',axis='0 0 1',stiffness=str(K*d.get('krib',.1)),damping=str(K/100),armature='1e-6')
  E.SubElement(rb,'inertial',pos=fmt([Lr/2,0,0]),mass='.001',diaginertia='1e-8 1e-8 1e-8')
  E.SubElement(rb,'geom',name=f'{nm}_r{i}_g',type='box',pos=fmt([Lr/2,0,0]),size=fmt([Lr/2,.00075,H/2*.9]),rgba='.85 .83 .78 1',contype='0',conaffinity='0')
  E.SubElement(eq,'connect',body1=rb.get('name'),body2=bb[i][0].get('name'),anchor=fmt([Lr,0,0]),solref='.002 1')
