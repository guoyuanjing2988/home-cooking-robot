"""Prospective completed-food scene, including every stored transfer vessel."""
import xml.etree.ElementTree as E,copy
import numpy as np
from scipy.spatial.transform import Rotation
import persistent_v6_r07 as p
v=p.v
def completed_scene():
 w=p.World()
 for prod,mass in w.mass.items():
  edible=mass*(.96 if prod in ('carrot','potato') else 1)*.975;scrap=mass-edible;w.mass[prod]=edible;w.scrap[prod]=scrap
  density=1000 if prod in ('leafy_greens','tomato') else 1030;packing=.20 if prod=='leafy_greens' else .60 if prod=='tomato' else .55;thick=edible/(density*packing*.11*.15);b=E.Element('body');v.s.model.box(b,'food_bulk',[.179-thick/2,0,0],[thick,.11,.15],robot=False)
  bowl=w.objects['bowl_'+prod];foodpose=bowl['pose'].copy();foodpose[:3,:3]=foodpose[:3,:3]@Rotation.from_euler('xyz',bowl['h'].get('object_rotation_deg') or [0,0,0],degrees=True).as_matrix()
  if v.cfg.get('bowl_bail_swing_deg'):
   swing=Rotation.from_euler('z',-v.cfg['bowl_bail_swing_deg'],degrees=True);pivot=np.array([.093,0,0]);key=pivot-swing.apply(pivot);foodpose[:3,:3]=foodpose[:3,:3]@swing.inv().as_matrix();foodpose[:3,3]-=foodpose[:3,:3]@key
  o=w.objects['food:'+prod];o.update(body=b,pose=foodpose,support='bowl_'+prod,mass=edible);w.conditions[prod]='declared_finished_product'
  # Full scrap bed in the custom station tray. Multiple food masses remain
  # distinct adjacent cells rather than coincident duplicated solids.
  i=list(w.mass).index(prod);x,y,_=v.cfg['station_frames']['peel']['new_center'];height=scrap/(1030*.35*.075*.07);sb=E.Element('body');v.s.model.box(sb,'scrap_bulk',[0,0,0],[.075,.07,height],robot=False);sp=p.T([x-.12+i*.08,y,.875+height/2],np.eye(3));w.objects['scrap:'+prod]=dict(body=sb,pose=sp,home=sp.copy(),h=copy.deepcopy(o['h']),support='linear_peeler_scrap_floor',mass=scrap)
 ch,_=w.build(58,None,v.items[58][1]['poses'][0]['R']);ch.hands={};ch.allowed=[];ch.working_stroke=False;ch.contact_windows=[]
 return ch,w.snapshot()
