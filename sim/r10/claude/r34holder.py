"""Issue #34 single-cup rim tipper (Mac 2026-10-13, new file): the holder of rim_tipper3.py as world geometry.
Wraps kitchen17.add (after cupobj / bowlobj). cfg keys: r34_holder = [az_deg, gap_m, dz_m] (holder at azimuth az about
the wok axis, cup wall gap outside the rim, cup bottom dz above the rim), r34_cup = True (the cup seated upright in it),
r34_tipped = True (the cup tipped TIPDEG into the wok, render only).
Holder (box bracket, ASSUMPTION): seat plate 72 x 72 x 12 mm under the cup, servo box 60 (radial) x 40 x 60 mm under
the seat, 20 x 20 mm post under it to z .921 (cooker-top mounting not modelled). Same numbers as rim_tipper3.py."""
import math,numpy as np
from scipy.spatial.transform import Rotation
import kitchen14 as K14,kitchen15 as K15,kitchen16 as K,kitchen17 as K17
import cupobj,bowlobj   # noqa: F401  (wrapper order: kitchen17.add -> cupobj -> bowlobj -> r34holder)
CR,CH=K14.CUP_R,K14.CUP_H;TIPDEG=120.
def rz(a):c,s=math.cos(a),math.sin(a);return np.array([[c,-s,0],[s,c,0],[0,0,1.]])
def geom(az,gap,dz):
 a=math.radians(az);u=np.array([math.cos(a),math.sin(a),0.]);t=np.array([-math.sin(a),math.cos(a),0.]);RC=K15.A_RIM+gap+CR
 c=np.r_[K15.WOK0[:2],0]+RC*u;zb=K15.RIM_Z+dz;Rz=rz(a);zs=zb-.012-.06;ph=(zs-.921)/2
 parts=[('r34_seat','box',c+[0,0,zb-.006],[CR+.006,CR+.006,.006],Rz),('r34_servo','box',c+[0,0,zs+.03],[.03,.02,.03],Rz),
  ('r34_post','box',c+[0,0,.921+ph],[.01,.01,ph],Rz)]
 piv=c-CR*u+[0,0,zb];Rt=Rotation.from_rotvec(t*math.radians(TIPDEG)).as_matrix()
 if (Rt@[0,0,1.])@u>0:Rt=Rotation.from_rotvec(-t*math.radians(TIPDEG)).as_matrix()
 tc=piv+Rt@(c+[0,0,zb+CH/2]-piv)
 return dict(cup_bottom=c+[0,0,zb],parts=parts,tipped=('r34_cup_tipped','cylinder',tc,[CR,CH/2],Rt))
_add0=K17.add
def add(tree,world,cfg):
 _add0(tree,world,cfg)
 if cfg.get('r34_holder') is None:return
 g=geom(*cfg['r34_holder']);K._add(world,'',g['parts'],rgba='.3 .32 .35 1')
 if cfg.get('r34_cup'):K._add(world,'',[('r34_cup_body','cylinder',[0,0,CH/2],[CR,CH/2],np.eye(3))],np.eye(3),g['cup_bottom'],rgba='.95 .95 .95 1')
 if cfg.get('r34_tipped'):K._add(world,'',[g['tipped']],rgba='.95 .95 .95 1')
K17.add=add
