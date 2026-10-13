"""R19 prep step 5 (GitHub #38, R19_PREP_T2L.md): a FOLD-AWAY T2L cradle (Route B). NEW layer; kitchen19p4.py is
imported and not changed. Nothing in a scene changes unless cfg['r19p5'] is set (add() returns the tree untouched
without it), so every earlier scene and stored result is byte-identical. All sizes, masses and torques are ESTIMATES
(design proposals for printed / bought parts); nothing is a measured product.

Design (cart frame as kitchen19p4: x along the rail from the arm base axis, +y toward the counter, z world):
 - the step-4 cradle (plate 160 x 160 x 4 mm under the pan, pan bottom-centre (-0.32, 0.05, 0.93)) and its arm
   (bracket_y, 30 x 30 mm, from the mast bar to the plate) become ONE rigid LEAF that turns about a HINGE at the end
   of the mast bar, at H = (-0.32, -0.17, 0.911) (the arm's root, on the bar's centre line);
 - kind 'swing' (default; "swings toward the wall"): a VERTICAL hinge pin. Deployed = the step-4 pose (leaf along
   +y); folded = turned FOLD_DEG (+90) about z, so the leaf lies along the cart's left side (-x, toward the left wall
   at the rail end) and the plate centre is at (-0.54, -0.17). The pan stays level, so it MAY stay aboard
   (cfg pan=True); the hinge carries no gravity moment about its axis. The fixed mast bar is lowered 40 mm
   (z 0.854..0.884) so the leaf turns over it with a 12 mm gap (the checker's 10 mm cart-part rule for a held
   leaf); the pin, its two bushes and the end-stop / detent pair (0 and FOLD_DEG) sit in that gap: NOT modelled.
 - kind 'flip' ("flips down"): a hinge pin along x. Deployed = the step-4 pose; folded = turned FOLD_DEG (-90) about
   x, the leaf hangs down along the mast bar (plate bottom near z 0.61). The pan must be OFF the cradle to fold.
   The mast bar keeps its step-4 height but ends 15 mm short of the leaf (x -0.29): pin + knuckles in that gap,
   NOT modelled. The deployed leaf needs a lock against the droop moment (leaf ~0.8 N.m + filled pan ~1.4 N.m [E]).
 - KNOB: a keyed 30 mm block (the R16/R17 grip block) on a short stub of the leaf, gripped by the PGC; the arm turns
   the leaf by it (contact only on the straight <= 50 mm grasp approach / release retreat, as every set).
   swing: knob on TOP of the leaf arm at KNOB_R from the pin, gripped from above (approach -z, jaws across the arm),
          so the fold is a wrist roll about the approach axis plus a KNOB_R arc;
   flip:  knob on the arm's -x face at KNOB_R from the pin, approach +x (along the pin axis, as the R17 faucet lever).
 - the leaf's own frame (the 'fold' object of r19prep5_actions): origin at the hinge point H, axes = the cart axes
   in the deployed state; a fold is a pure rotation of that frame about the pin (p fixed, R = Rz / Rx(angle)).
cfg['r19p5'] = dict(state='deployed'|'folded'|'held', kind='swing'|'flip', pan=False, fold_deg=None, knob_r=None,
                    angle=None)   # 'held': the leaf is in the gripper (only the fixed parts are added); angle: any
                                   # intermediate angle as a cart part (screens)
Geom names: fixed parts 'R_cart_p5_fix_*', leaf parts 'R_cart_p5_leaf_*', parked pan 'R_cart_p5_stg_*' (cart geoms,
contact classes of the cart, as kitchen19p4), held leaf 'R_gripper_p5_*' via kitchen16.OBJ['fold_<kind>']."""
import numpy as np,xml.etree.ElementTree as E
from scipy.spatial.transform import Rotation
import kitchen16 as K,kitchen19p4 as P4
I3=np.eye(3)
DEFAULT=dict(kind='swing',fold_deg=None,knob_r=None,knob='top',pan=False,state='deployed',angle=None)
FOLD_DEG=dict(swing=90.,flip=-90.)
KNOB_R=dict(swing=.03,flip=.06)   # [design] knob distance from the pin along the leaf arm (m)
KNOB_DX=.07                        # [design] 'top' knob: lateral offset (-x) from the leaf arm's centre line
PT=.004;ARM_H=.015;ARM_W=.015      # plate thickness; leaf arm half height / half width (30 x 30 mm, as kitchen19p4)
MASS_EST=dict(leaf=.45)            # [est] Al 30 x 30 x 2 mm tube 0.22 m + 4 mm Al plate 160 x 160 + knob, ~0.45 kg
def hinge_local():
 """hinge point H in the cart frame (the leaf arm's root, on its centre line)."""
 t=P4.T2L;return np.array([t['cx'],-.17,t['zb']-PT-ARM_H])
def axis(kind):return np.array([0,0,1.]) if kind=='swing' else np.array([1.,0,0])
def rot(kind,deg):return K.Rz(deg) if kind=='swing' else K.Rx(deg)
def parse_kv(kv):
 """kitchen19p5 design keys from a dict of strings (screens: P5_kind=flip P5_fold_deg=.. P5_knob_r=..)."""
 out={}
 for k,v in kv.items():
  out[k]=v if k in ('kind','state') else (v=='1') if k=='pan' else float(v)
 return out
KNOB=dict(   # knob styles: grip point (leaf frame, r = knob_r along the arm), approach a, jaw axis j, stub + block parts
 # top: a lateral stub out of the arm's -x face to a keyed 30 mm block KNOB_DX left of the arm (outside the stgwok gripper
 #      corridor, x -0.32 +- 0.04 over the pin), its top 20 mm over the arm top; gripped from above (approach -z), jaws along
 #      y (across the 30 mm block); the open fingers hang beside the arm, >= 40 mm from it.
 top=dict(g=lambda r:[-KNOB_DX,r,ARM_H+.005],a=[0,0,-1.],j=[0,1.,0],parts=lambda r:[('kstub','box',[-(ARM_W+KNOB_DX-.0125)/2,r,0],[(KNOB_DX-.0125-ARM_W)/2,.008,.008],I3),('knob','box',[-KNOB_DX,r,ARM_H+.005],[.0125,.015,.015],I3)]),
 # side: a 45 mm stub out of the arm's -x face and the block on it, gripped along +x (from the left), jaws vertical.
 side=dict(g=lambda r:[-ARM_W-.060,r,0],a=[1.,0,0],j=[0,0,1.],parts=lambda r:[('kstub','box',[-ARM_W-.0225,r,0],[.0225,.008,.008],I3),('knob','box',[-ARM_W-.060,r,0],[.015,.008,.015],I3)]))
def leaf_parts(kind='swing',knob_r=None,knob='top',pan=False):
 """leaf parts in the LEAF frame (origin H, cart axes when deployed): (name, type, centre, half sizes, R); pan=True adds the
 parked staging pan on the plate (as kitchen19p4 T2L: bottom centre on the plate top, lug toward -y)."""
 t=P4.T2L;ycen=t['cy']-(-.17)   # plate centre along the arm: 0.22 m
 kr=KNOB_R[kind] if knob_r is None else knob_r
 parts=[('arm','box',[0,ycen/2,0],[ARM_W,ycen/2,ARM_H],I3),
  ('plate','box',[0,ycen,ARM_H+PT/2],[P4.STG_R+.01,P4.STG_R+.01,PT/2],I3)]+KNOB[knob]['parts'](kr)
 if pan:
  Rl,pl=P4.t2l_local();o=pl-hinge_local()
  parts+=[(n.replace('p4_',''),typ,(Rl@np.asarray(q)+o).tolist(),s,Rl@Rp) for n,typ,q,s,Rp in K.OBJ['stg']['parts']]
 return parts
def knob_grip(kind='swing',knob_r=None,knob='top'):
 kr=KNOB_R[kind] if knob_r is None else knob_r
 return np.array(KNOB[knob]['g'](kr),float)
def fixed_parts(kind='swing'):
 """cart-frame fixed parts (name, centre, half sizes): the mast bar (kitchen19p4 bracket_x, changed as described)."""
 t=P4.T2L;zb=t['zb']-PT;ym=-.17
 if kind=='swing':   # lowered 42 mm: top 12 mm under the leaf arm (10 mm cart-part gap + 2 mm, as the pan's 12 mm pick); runs under the pin
  x0,x1,z0,z1=t['cx']-.025,.015,zb-.072,zb-.042
 else:               # step-4 height, ends 15 mm short of the leaf arm (x -0.29)
  x0,x1,z0,z1=t['cx']+ARM_W+.015,.015,zb-.03,zb
 return [('fix_bar',[(x0+x1)/2,ym,(z0+z1)/2],[(x1-x0)/2,.015,(z1-z0)/2])]
def obj_name(kind='swing',knob='top',knob_r=None,pan=False):
 return f'fold_{kind}_{knob}'+('' if knob_r is None else f'_r{knob_r:g}')+('_pan' if pan else '')
def _reg(kind,knob,knob_r,pan):
 """kitchen16.OBJ entry of the held leaf (frame = hinge point H), e.g. 'fold_swing_top', 'fold_swing_top_r0.08_pan'."""
 n=obj_name(kind,knob,knob_r,pan)
 if n in K.OBJ:return n
 parts=[(f'p5_leaf_{a}' if not a.startswith('stg') else f'p5_{a}',typ,c,h,R) for a,typ,c,h,R in leaf_parts(kind,knob_r,knob,pan)]
 a=np.array(KNOB[knob]['a']);j=np.array(KNOB[knob]['j'])
 K.OBJ[n]=dict(parts=parts,grip=knob_grip(kind,knob_r,knob),a=a,j=j,hax=a,grip_part='p5_leaf_knob')
 import kitchen19 as K19
 K19.JAW[n]=0.;K19.MASS[n]=MASS_EST['leaf']+(P4.MASS_EST['stg']+.02 if pan else 0.)
 return n
for _k in ('swing','flip'):
 for _n in ('top','side'):
  for _p in (False,True):_reg(_k,_n,None,_p)
def ensure(names):
 for n in names:
  if isinstance(n,str) and n.startswith('fold_') and n not in K.OBJ:
   v=n[5:].split('_');pan=v[-1]=='pan';v=v[:-1] if pan else v
   _reg(v[0],v[1],float(v[2][1:]) if len(v)>2 else None,pan)
def leaf_pose_local(kind,deg):
 """(R, p) of the leaf frame in the cart frame at fold angle deg (0 = deployed)."""
 return rot(kind,deg),hinge_local()
def leaf_pose_world(kind,deg,cart_x,base_y=-.21):
 R,p=leaf_pose_local(kind,deg);return R,p+np.array([cart_x,base_y,0.])
def _geom(parent,name,typ,pos,size,R=I3):
 return E.SubElement(parent,'geom',name=name,type=typ,pos=' '.join(f'{v:.9g}' for v in pos),size=' '.join(f'{v:.9g}' for v in size),
  quat=' '.join(f'{v:.9g}' for v in Rotation.from_matrix(np.asarray(R,float)).as_quat()[[3,0,1,2]]),rgba='.45 .62 .80 1',contype='2',conaffinity='3',margin='.01',mass='.000001')
def add(tree,cfg):
 """Apply cfg['r19p5'] (no-op without it): fixed bar, leaf at its state (unless held), parked pan (swing only)."""
 c=cfg.get('r19p5')
 if not c:return tree
 c=dict(DEFAULT,**c);kind=c['kind'];fd=FOLD_DEG[kind] if c.get('fold_deg') is None else float(c['fold_deg'])
 cart=tree.find(".//body[@name='rail_structure']")
 for n,ctr,hs in fixed_parts(kind):_geom(cart,'R_cart_p5_'+n,'box',ctr,hs)
 if c['state']=='held':return tree
 deg=0. if c['state']=='deployed' else fd if c['state']=='folded' else float(c['state'])
 if c.get('angle') is not None:deg=float(c['angle'])
 R,p=leaf_pose_local(kind,deg)
 if c.get('pan') and kind!='swing' and abs(deg)>1e-9:raise ValueError('flip cradle: the pan cannot ride a folded leaf')
 for n,typ,q,s,Rp in leaf_parts(kind,c.get('knob_r'),c.get('knob','top'),bool(c.get('pan'))):
  _geom(cart,'R_cart_p5_'+('' if n.startswith('stg') else 'leaf_')+n,typ,R@np.asarray(q)+p,s,R@Rp)
 return tree
def mesh(tree):
 """R11 mesh rule for every step-5 part (boxes -> 8-vertex meshes, cylinders -> circumscribed 16-gon prisms)."""
 asset=tree.getroot().find('asset');n=16;t=2*np.pi*(np.arange(n)+.5)/n
 if asset is None:asset=E.SubElement(tree.getroot(),'asset')
 for g in tree.getroot().iter('geom'):
  nm=g.get('name') or ''
  if not nm.startswith(('R_gripper_p5_','p5_','R_cart_p5_')) or g.get('type') not in ('box','cylinder'):continue
  h=np.fromstring(g.get('size'),sep=' ');mn='mb5_'+nm
  if g.get('type')=='box':V=[[sx*h[0],sy*h[1],sz*h[2]] for sx in(-1,1) for sy in(-1,1) for sz in(-1,1)]
  else:rc=h[0]/np.cos(np.pi/n);V=[[rc*np.cos(a),rc*np.sin(a),sz*h[1]] for a in t for sz in (-1,1)]
  E.SubElement(asset,'mesh',name=mn,vertex=' '.join(' '.join(f'{x:.9g}' for x in v) for v in V))
  g.set('type','mesh');g.set('mesh',mn);g.attrib.pop('size',None)
 return tree
