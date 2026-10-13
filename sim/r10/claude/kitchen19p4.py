"""R19 prep audit step 4 (GitHub #38, follow-up of R19_PREP_STEP3.md): slicer output and the cooking-time
staging spot. NEW layer; no shared file is changed. Nothing in a scene changes unless cfg['r19p4'] is set (add()
returns the tree untouched without it), so every earlier scene and stored result is byte-identical.
All sizes and masses are ESTIMATES (design proposals for printed / bought parts), nothing is a measured product.

1. Slicer out-bowl drawer (option (a) of R19_PREP_STEP3.md 5), cfg['r19p4']['drawer'] = dict(xo=<bowl x out>, y=.495):
   - the R11 plain out bowl (r19_slicer_out_bowl) is replaced by DBOWL: the same R11 vessel radius (85 mm) but
     75 mm tall (R11: 90 mm) and the step-3 strut + keyed knob, knob toward +x (the only side free of the slicer
     body). Why 75 mm: the bowl stands on a 5 mm guide plate and is lifted 8 mm at the grasp; its rim must stay
     >= 5 mm (held gate) under the slicer spout (bottom 0.95 m): 0.85 + 0.005 + 0.008 + H <= 0.945 -> H <= 82 mm;
   - a printed guide (p4_drawer_*): base plate 5 mm on the counter from under the spout to the out position,
     two low side rails (15 mm over the plate, 6 mm thick, 8 mm radial play to the bowl's wall corners) and
     end stops. The bowl itself is the drawer: the arm pulls it out by its knob along +x (the slide is held
     8 mm above the plate in the sim, a conservative stand-in for sliding on it, as the step-3 catch tray);
   - the drawer axis is y 0.495 (step 3: 0.50) so the back rail clears the wall (north_wall y 0.60);
   - out position xo: the R07 potato staging bowl (x -1.504..-1.296, y 0.356..0.564) stands where the bowl must
     go, so drop_potato=True removes it (as kitchen19.LAYOUT already removes the R07 tomato bowl).
2. Option (b), a chute on the spout to a bowl in the open strip: geometry only (r19prep4_probe.py MODE=chute);
   no part is added here (see R19_PREP_STEP4.md: there is no drop height and no free open-strip spot).
3. Cooking-time staging container on the cart, site T2L of the R19 cups study (kitchen19seas.py), cfg['r19p4']
   ['t2l'] = dict(cx, cy, zb, yaw, present): a STG pan (cup-style: solid envelope cylinder r STG_R x STG_H, a lug
   and the keyed 30 mm block of the R19 cups, approach along the lug, jaws horizontal across the block, pour = a
   roll about the lug axis) standing on a cradle plate carried by a 30 x 30 mm bar from the cart mast (as the
   cups' T2 bracket). The cradle and the parked pan are CART geoms (R_cart_p4_*, body rail_structure, the cart's
   own contact classes): the unchanged checker then wants 10 mm between them and the arm, gripper or held object
   (not 5), so the pan is picked 12 mm above its cradle (cups: same). Pins under the pan locate it (not modelled:
   below the plate top). Cart frame: x along the rail from the arm base axis, y (base_y -0.21 m): arm base axis at
   y 0.08, mast y -0.22..-0.12; world = cart frame + (cart x, -0.21, 0).
Every box / cylinder added here, held or in the world or on the cart, is a convex MESH (mesh(): boxes 8-vertex,
cylinders 16-gon prisms circumscribed), the R11 rule as kitchen19p3.mesh_held."""
import numpy as np,xml.etree.ElementTree as E
from scipy.spatial.transform import Rotation
from scene import fmt
import kitchen16 as K,kitchen19 as K19,kitchen19p3 as P3
I3=np.eye(3)
# ---------------- drawer bowl ----------------
DBOWL=dict(R=.085,H=.075,t=.003);DRAWER=dict(plate_t=.005,rail_h=.015,rail_t=.006,play=.008,stop_t=.006,y=.495)   # width 2*(88+8+6) = 204 mm between the slicer base (y 0.39) and the wall (0.60): 3 mm each side
SPOUT_BOTTOM=K19.COUNTER_TOP+.10   # scene.py slicer_spout: centre z .12, height .04 above the counter
MASS_EST=dict(dbowl=.22,stg=.22)   # [est] printed / thin stainless bowl; stainless pan (r 70 x 85 mm, ~0.8 mm wall)
def _reg_container(name,R,H,t):
 parts,grip=P3.container(name,R,H,t)
 parts=[(n.replace('p3_','p4_',1),*r) for n,*r in parts]
 K.OBJ[name]=dict(parts=parts,grip=grip,a=np.array([-1.,0,0]),j=np.array([0,1.,0]),hax=np.array([-1.,0,0]),grip_part=[n for n,*_ in parts if n.endswith('_knob')][0])
 K19.JAW[name]=0.;K19.MASS[name]=MASS_EST[name]
_reg_container('dbowl',DBOWL['R'],DBOWL['H'],DBOWL['t'])
def dbh(dxk=.15,yk=.20,zk=.20,pd=0.):
 """'dbh_<dxk>_<yk>_<zk>_p<pd>': the drawer bowl with a CRANKED printed handle instead of the step-3 strut: a rim strut
 along +x to a post at x = dxk (beside the slicer's right face when the bowl is under the spout), the post up to zk
 (above the bowl bottom), a bar forward (-y) to a keyed 30 mm knob at y = -yk, facing the robot. Grasp: approach +y
 (toward the bowl), jaws horizontal across the knob (object x), pitched pd below horizontal; pour = roll about the
 approach axis through the knob. Probe round 1 (dbowl, knob +x at y 0.495): 0/96 everywhere (upper arm / forearm vs
 the upper cabinet), so the knob must come out from under the cabinet."""
 n=f'dbh_{dxk:g}_{yk:g}_{zk:g}_p{pd:g}'
 if n in K.OBJ:return n
 R,H,t=DBOWL['R'],DBOWL['H'],DBOWL['t'];pre='p4_dbh'
 parts=[(f'{pre}_floor','cylinder',[0,0,t/2],[R,t/2],I3)]+[(n_.replace('p3_dbh','p4_dbh'),*r) for n_,*r in P3._ring('p3_dbh',R,H,t)]
 sh,st=.012,.006   # strut / bar half width, half thickness
 parts+=[(f'{pre}_strut','box',[(R-.004+dxk+sh)/2,0,H-st],[(dxk+sh-(R-.004))/2,sh,st],I3),
  (f'{pre}_post','box',[dxk,0,(H-2*st+zk+st)/2],[sh/2+.003,sh,(zk+st-(H-2*st))/2],I3),
  (f'{pre}_bar','box',[dxk,-(yk-.02)/2,zk],[sh/2+.003,(yk-.02)/2+sh,st],I3)]
 th=np.radians(pd);Rk=np.array([[1,0,0],[0,np.cos(th),np.sin(th)],[0,-np.sin(th),np.cos(th)]])   # knob turned about the jaw axis (x) so the approach comes from above-front
 g=np.array([dxk,-yk,zk]);parts.append((f'{pre}_knob','box',g.tolist(),[.015,.02,.015],Rk))
 K.OBJ[n]=dict(parts=parts,grip=g,a=np.array([0,np.cos(th),-np.sin(th)]),j=np.array([1.,0,0]),hax=np.array([0,np.cos(th),-np.sin(th)]),grip_part=f'{pre}_knob')
 K19.JAW[n]=0.;K19.MASS[n]=MASS_EST['dbowl']+.06
 return n
def drawer_seat(x=None):
 """object pose (R, p) of the drawer bowl standing on the guide plate at x (default: under the spout)."""
 sx,sy,_=K19.LAYOUT['slicer'];cen=np.array(K19.place('slicer',*K19.LAYOUT['slicer'])[1])+K19.Rz(K19.LAYOUT['slicer'][2])@K19.SLICER_BOWL
 return I3.copy(),np.array([cen[0] if x is None else x,DRAWER['y'],K19.COUNTER_TOP+DRAWER['plate_t']])
def drawer_parts(xo):
 """guide plate, rails and stops (name, centre, half sizes) from under the spout to the out position xo."""
 R,H=DBOWL['R'],DBOWL['H'];x0=drawer_seat()[1][0];y=DRAWER['y'];t=DRAWER['plate_t'];rh,rt,pl,st=DRAWER['rail_h'],DRAWER['rail_t'],DRAWER['play'],DRAWER['stop_t']
 rc=R/np.cos(np.pi/12)   # the 12 wall boxes' outer corners (kitchen19p3._ring)
 ri=rc+pl;xa=x0-ri-st;xb=xo+ri+st;z0=K19.COUNTER_TOP
 return [('p4_drawer_plate',[(xa+xb)/2,y,z0+t/2],[(xb-xa)/2,ri+rt,t/2]),
  ('p4_drawer_rail_f',[(xa+xb)/2,y-ri-rt/2,z0+t+rh/2],[(xb-xa)/2,rt/2,rh/2]),('p4_drawer_rail_b',[(xa+xb)/2,y+ri+rt/2,z0+t+rh/2],[(xb-xa)/2,rt/2,rh/2]),
  ('p4_drawer_stop_l',[xa+st/2,y,z0+t+rh/2],[st/2,ri,rh/2])]   # right end: no wall (the knob and strut pass over the plate end); a printed detent [design, not modelled] stops the bowl at xo
# ---------------- staging pan (cup-style, kitchen19seas cup design scaled) ----------------
STG_R,STG_H=.07,.085;BLOCK=np.array([.015,.012,.012]);LUG_GAP=.04;BLOCK_DZ=.006   # lug gap 40 mm (cups: 25): with 25 the open fingertips (30 mm past the TCP, 40-53 mm off it across the jaws) came 7.6 mm from the r 70 mm wall, under the 10 mm cart-geom gap (chain stgwok_m2 approaches)
def stg_grip():return np.array([0.,-(STG_R+LUG_GAP),STG_H+BLOCK_DZ-BLOCK[2]])
def _stg_parts(pre='p4_stg'):
 g=stg_grip();y0,y1=-(STG_R-.002),-(-g[1]-BLOCK[1])
 return [(f'{pre}_body','cylinder',[0,0,STG_H/2],[STG_R,STG_H/2],I3),(f'{pre}_lug','box',[0,(y0+y1)/2,g[2]],[.008,(y0-y1)/2,.004],I3),(f'{pre}_block','box',g.tolist(),BLOCK.tolist(),I3)]
K.OBJ['stg']=dict(parts=_stg_parts(),grip=stg_grip(),a=np.array([0,1.,0]),j=np.array([1.,0,0]),hax=np.array([0,1.,0]),grip_part='p4_stg_block')
K19.JAW['stg']=0.;K19.MASS['stg']=MASS_EST['stg']+.02
def stg_pitched(deg):
 """'stg_p<deg>': the same pan, gripped with the approach pitched deg below horizontal (as kitchen19seas.set_approach)."""
 n=f'stg_p{deg:g}'
 if n not in K.OBJ:
  b=np.radians(deg);K.OBJ[n]=dict(K.OBJ['stg'],a=np.array([0,np.cos(b),-np.sin(b)]));K19.JAW[n]=K19.JAW['stg'];K19.MASS[n]=K19.MASS['stg']
 return n
def ensure(names):
 for n in names:
  if isinstance(n,str) and n.startswith('stg_p'):stg_pitched(float(n[5:]))
  elif isinstance(n,str) and n.startswith('dbh_'):v=n[4:].split('_');dbh(float(v[0]),float(v[1]),float(v[2]),float(v[3][1:]))
  elif isinstance(n,str) and '_p' in n:P3.pitched(n)
T2L=dict(cx=-.32,cy=.05,zb=.93,yaw=0.)   # pan bottom-centre in the cart frame; yaw 0 = lug toward the aisle (-y)
def t2l_local(t2=None):
 t=dict(T2L,**(t2 or {}));return K.Rz(t['yaw']),np.array([t['cx'],t['cy'],t['zb']])
def t2l_world(cart_x,t2=None,base_y=-.21):
 R,p=t2l_local(t2);return R,p+np.array([cart_x,base_y,0.])
def t2l_parts(t2=None):
 """cart-frame cradle parts (name, centre, half sizes, R): plate under the pan, bar from the mast."""
 t=dict(T2L,**(t2 or {}));R,p=t2l_local(t);pt=.004;out=[('cradle',p+[0,0,-pt/2],[STG_R+.01,STG_R+.01,pt/2],R)]
 ym=-.17;zb=p[2]-pt   # bar: from the mast (cart y -0.17) along x under the plate, then along y to it (as kitchen19seas T2 bracket)
 out.append(('bracket_x',[p[0]/2,ym,zb-.015],[abs(p[0])/2+.015,.015,.015],I3))
 if p[1]-STG_R>ym+.015:out.append(('bracket_y',[p[0],(ym+p[1])/2,zb-.015],[.015,(p[1]-ym)/2,.015],I3))
 return out
# ---------------- tree layer ----------------
def _geom(parent,name,typ,pos,size,R=I3,cls=('1','2'),extra=None,rgba='.55 .75 .55 1'):
 a=dict(name=name,type=typ,pos=fmt(pos),size=fmt(size),quat=fmt(Rotation.from_matrix(np.asarray(R,float)).as_quat()[[3,0,1,2]]),rgba=rgba,contype=cls[0],conaffinity=cls[1],mass='.000001')
 if extra:a.update(extra)
 return E.SubElement(parent,'geom',**a)
def add(tree,cfg):
 """Apply cfg['r19p4'] (no-op without it): drawer, potato-bowl removal, T2L cradle (+ parked pan)."""
 c=cfg.get('r19p4')
 if not c:return tree
 w=tree.find('worldbody')
 if c.get('drop_potato'):
  for b in list(w.findall('body')):
   if any((g.get('name') or '').startswith('stored_bowl_potato') for g in b.iter('geom')):w.remove(b)
 if c.get('drawer'):
  P3.drop_out_bowl(tree)
  for n,ctr,hs in drawer_parts(float(c['drawer']['xo'])):_geom(w,n,'box',ctr,hs)
 if c.get('t2l'):
  t2=c['t2l'];cart=tree.find(".//body[@name='rail_structure']");kw=dict(cls=('2','3'),extra=dict(margin='.01'))
  for n,ctr,hs,R in t2l_parts(t2):_geom(cart,'R_cart_p4_'+n,'box',ctr,hs,R,**kw)
  if t2.get('present',True):
   R,p=t2l_local(t2)
   for n,typ,q,s,Rp in K.OBJ['stg']['parts']:_geom(cart,'R_cart_'+n,typ,R@np.asarray(q)+p,s,R@Rp,**kw)
 return tree
def mesh(tree):
 """R11 mesh rule for every step-4 part: boxes -> identical 8-vertex meshes, cylinders -> circumscribed 16-gon prisms."""
 asset=tree.getroot().find('asset');n=16;t=2*np.pi*(np.arange(n)+.5)/n
 if asset is None:asset=E.SubElement(tree.getroot(),'asset')
 for g in tree.getroot().iter('geom'):
  nm=g.get('name') or ''
  if not nm.startswith(('R_gripper_p4_','p4_','R_cart_p4_')) or g.get('type') not in ('box','cylinder'):continue
  h=np.fromstring(g.get('size'),sep=' ');mn='mb4_'+nm
  if g.get('type')=='box':V=[[sx*h[0],sy*h[1],sz*h[2]] for sx in(-1,1) for sy in(-1,1) for sz in(-1,1)]
  else:rc=h[0]/np.cos(np.pi/n);V=[[rc*np.cos(a),rc*np.sin(a),sz*h[1]] for a in t for sz in (-1,1)]
  E.SubElement(asset,'mesh',name=mn,vertex=' '.join(fmt(v) for v in V))
  g.set('type','mesh');g.set('mesh',mn);g.attrib.pop('size',None)
 return tree
def stg_mass(contents):
 """(kg, CoM in the object frame) of the pan + lug/block + contents (contents as a cylinder filling the pan's lower part)."""
 m0=MASS_EST['stg'];ml=.02;g=stg_grip();hc=min(STG_H,max(.01,contents/(600*np.pi*(STG_R-.002)**2)))   # loose cut pieces ~0.6 kg/L [est]
 com=(m0*np.array([0,0,STG_H/2])+ml*g+contents*np.array([0,0,hc/2]))/(m0+ml+contents);return m0+ml+contents,com
