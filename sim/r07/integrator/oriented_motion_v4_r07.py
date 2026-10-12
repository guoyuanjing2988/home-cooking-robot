"""Generalise support normal to the full rotated dock's actual local+Z face."""
import inspect,numpy as np
def install(mo):
 if getattr(mo,'oriented_docks_v4',False):return
 original=mo.windows
 def windows(ch,q,hands):
  ws=original(ch,q,hands)
  if ch.config.get('horizontal_tool_docks'):
   for w in ws:
    if w['face'] in ('dock_wash_pad_face','dock_eye_core_spoon_face'):
     g=ch.gnames.index(w['face']);w['normal']=ch.d.geom_xmat[g].reshape(3,3)[:,2].tolist();w['insertion_axis_reason']='Actual local+Z mating-face normal of full90deg rotated dock; own object/support only, <=50mm and until5mm gap.'
  return ws
 mo.windows=windows
 source=inspect.getsource(mo.lift)
 old='p+np.array([0,0,mm/1000])'
 assert source.count(old)==1
 source=source.replace(old,"p+np.array(next(w['normal'] for w in ws if w['side']==side))*mm/1000")
 exec(compile(source,'oriented_support_lift_v4','exec'),mo.__dict__)
 mo.oriented_docks_v4=True
