"""Single conserved MJCF scene and ownership bindings; no snapshot duplication.

Free-body motion is kinematic mocap for geometric planning, never physics/yield
evidence. Missing transfer poses are explicit and stop certification.
"""
import json,copy,xml.etree.ElementTree as E
import numpy as np,mujoco
from scipy.spatial.transform import Rotation
import solver as s
H=s.HERE;P=s.P;tree,meta=s.model.build();root=tree.getroot();w=root.find('worldbody');bindings={}
def body(obj,pos,rotation=None):
 b=E.SubElement(w,'body',name='meal_'+obj,mocap='true',pos=s.model.fmt(pos),quat=s.model.quat(rotation or Rotation.identity()))
 bindings[obj]=dict(body=b.get('name'),initial_world_m=list(pos),geometry_complete=True);return b
def assembly(obj,typ,pos,prod='carrot'):
 h=dict(held=typ,held_kg=P['tools'][typ]['mass_kg'],product=prod,approach=[0,0,-1],jaw_axis=[0,1,0],object_rotation_deg=[0,0,0])
 b=body(obj,pos,Rotation.from_matrix(s.rot(h)));s.held(b,h,'meal_'+obj+'_');bindings[obj]['kind']=typ
 return b
for f in P['finished_products']:
 prod=f['product'];land=next(g for g in P['installed_geometry'] if g['name']=='raw_'+prod+'_land');pos=np.array(land['pos'])+[0,0,(land['size'][2]+f['input_size_m'][2])/2]
 b=body('food_'+prod,pos.tolist());s.model.box(b,'meal_food_'+prod+'_full',[0,0,0],f['input_size_m'],robot=False,mass=.000001)
 bindings['food_'+prod].update(kind='food',mass_kg=f['input_mass_kg'],initial_owner='raw_'+prod+'_land',cut_geometry_status='Uncut full envelope retained; split-piece topology and measured waste/yield are not certified')
 land=next(g for g in P['installed_geometry'] if g['name']=='output_'+prod+'_land');assembly('bowl_'+prod,'carried_bowl',[land['pos'][0],land['pos'][1],land['pos'][2]+land['size'][2]/2+.180],prod)
for typ,x,z in [('peeler',-.55,1.0715),('wash_pad',-.18,1.08),('eye_core_spoon',-.325,1.0865)]:assembly(typ,typ,[x,.46,z])
for obj,typ,pos in [('cup','food_cup',[0,.43,1.04]),('colander','colander',[-.46,.22,1.08]),('cassette','cut_cassette',[-1.27,.17,1.15])]:
 assembly(obj,typ,pos);bindings[obj]['storage_support_qualified']=False;bindings[obj]['placement_basis']='Explicit staging candidate; no inherited R03 storage witness or support/pickup path exists'
for prefix,obj in [('secondary_closed_lid','secondary_lid'),('root_brush_','root_brush')]:
 selected=[g for g in list(w) if g.tag=='geom' and g.get('name','').startswith(prefix)]
 b=body(obj,[0,0,0]);bindings[obj]['kind']=obj
 for g in selected:w.remove(g);b.append(g)
# Full pusher conservative proxy filling the unqualified aperture; not an OEM
# drawing and never accepted as a supplier-matched guarded feed mechanism.
b=body('slicer_pusher',[.4,.085,1.50]);s.model.box(b,'meal_slicer_pusher_shaft',[0,0,-.095],[.145,.060,.190],robot=False);s.model.box(b,'meal_slicer_pusher_head',[0,0,.0125],[.165,.080,.025],robot=False)
bindings['slicer_pusher'].update(kind='pusher',geometry_complete=False,geometry_basis='Conservative aperture-envelope proxy; matched OEM pusher dimensions/force and grasp interface missing')
b=body('slicer_lid',[.425,.0875,1.355]);s.model.box(b,'meal_slicer_lid_full',[0,0,0],[.385,.245,.010],robot=False);bindings['slicer_lid'].update(kind='lid',geometry_complete=False,geometry_basis='Full casing planform; feed opening/hinge and exact OEM lid not source qualified')
xml=E.tostring(root,encoding='unicode');m=mujoco.MjModel.from_xml_string(xml);d=mujoco.MjData(m);(H/'models/persistent_meal.xml').write_text(xml)
sequence=json.loads((H/'results/state_sequence.json').read_text());violations=[]
def validate(state):
 # Owner is single-valued, and an arm may carry only the one registered object.
 for side,a in state['arms'].items():
  obj=a['held']
  if obj:
   actual=state['food'][obj[5:]]['owner'] if obj.startswith('food:') else state['objects'][obj]['owner']
   assert actual==side,(side,obj,actual)
 for obj,record in state['objects'].items():
  if record['owner'] in ['R','L']:assert state['arms'][record['owner']]['held']==obj
 for prod,record in state['food'].items():
  if record['owner'] in ['R','L']:assert state['arms'][record['owner']]['held']=='food:'+prod
for e in sequence['events']:
 for tag in ['state_before','state_after']:
  if tag in e:
   try:validate(e[tag])
   except AssertionError as ex:violations.append(dict(event=e['id'],state=tag,error=str(ex)))
out=dict(schema='r04.single-conserved-scene.v1',model='models/persistent_meal.xml',compiled_ngeom=m.ngeom,compiled_nq=m.nq,mocap_bodies=m.nmocap,unique_food_bodies=4,bindings=bindings,ownership_invariant_errors=violations,ownership_pass=not violations,executable=False,missing=['Jaw approach/closure and release trajectories','Cup/colander/cassette storage supports and transfer witnesses','Conserved split food pieces, scraps and measured edible yield','Clamp latch travel and force proof','Brush hinge route, appliance lid and pusher source-matched geometry/routes','Both-arm routes on the conserved scene'],state_application='At a certified handoff, an object mocap pose is continuous; at each arm waypoint its pose is flange/tool transform times the registered grasp transform. An owner update without this trajectory is rejected. No missing event is executed by changing a body pose.',render_scope='Initial conserved raw-food scene only; static stroke renders separately show template witnesses')
(H/'results/persistent_model.json').write_text(json.dumps(out,indent=2));print('persistent bodies',m.nmocap,'ownership errors',len(violations))
