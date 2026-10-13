"""R19 seasoning cup as a held object (import before building a scene; edits no existing file).
Registers kitchen16.OBJ['cup'] and wraps kitchen17.add so a cfg can place the station pad and a cup.
Cup = the R14 robot cup (kitchen14 CUP_R x CUP_H, 60 x 70 mm), object frame at the bottom centre,
axis z up. Grasp as the R14 probes (r14reach.py cup_*, r14_cup): TCP at the cup's centre, approach
horizontal toward the wall (+y) with the cup upright, jaws across x (R12 dual-zone fingers, jaw .014).
Station (ASSUMPTION, R14 evidence 1: "cups at about 1.10-1.15 m, y 0.30, at the front of the cabinet
underside"): the cup stands on the weighing pad at PORT_CUP (bottom centre) under the kitchen14
seasoning port; the pad is a disc the cup's size on a slim post from the counter (the real hanger to
the cabinet is not modeled). cfg keys: r19_station (pad + post), r19_port (cup bottom centre on the pad, default PORT_CUP), r19_cup ('port' | None: a cup on the pad)."""
import numpy as np,xml.etree.ElementTree as E
from scene import fmt
import kitchen14 as K14,kitchen16 as K,kitchen17 as K17
PORT_CUP=np.array([.55,.30,1.085])   # cup bottom centre on the pad (cup centre z 1.12: R14 probe pt*_0.30_1.12 passed)
PAD_T,POST_R=.010,.012
CUP_MASS=.12   # stainless cup (assumed)
def cup_parts():
 return [('r19_cup_body','cylinder',[0,0,K14.CUP_H/2],[K14.CUP_R,K14.CUP_H/2],np.eye(3))]
K.OBJ['cup']=dict(parts=cup_parts(),grip=np.array([0,0,K14.CUP_H/2]),a=np.array([0,1.,0]),j=np.array([1.,0,0]),grip_part=None)
_add0=K17.add
def add(tree,world,cfg):
 _add0(tree,world,cfg)
 if cfg.get('r19_station') or 'r19_port' in cfg:   # a result json's scene carries r19_port (r17video)
  p=np.asarray(cfg.get('r19_port',PORT_CUP),float)
  E.SubElement(world,'geom',name='r19_scale_pad',type='cylinder',pos=fmt(p-[0,0,PAD_T/2]),size=fmt([K14.CUP_R,PAD_T/2]),rgba='.55 .57 .6 1',contype='1',conaffinity='2',mass='.000001')
  h=p[2]-PAD_T-.85;E.SubElement(world,'geom',name='r19_scale_post',type='cylinder',pos=fmt([p[0],p[1],.85+h/2]),size=fmt([POST_R,h/2]),rgba='.55 .57 .6 1',contype='1',conaffinity='2',mass='.000001')
 if cfg.get('r19_cup')=='port':K._add(world,'',K.OBJ['cup']['parts'],np.eye(3),np.asarray(cfg.get('r19_port',PORT_CUP),float),rgba='.95 .95 .95 1')
K17.add=add
