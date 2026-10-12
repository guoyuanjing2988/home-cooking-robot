"""Conserved food partitions and guarded state transitions.

Geometric partitions are examples, not executed food transformations. A parent
is replaced at exactly the same occupied volume. No child is born in a bowl/bin.
Each subsequent delivery requires its own checked physical path.
"""
from station_cell import *

class Ledger:
 def __init__(self):
  self.nodes={p:dict(id=p,mass_kg=m,owner='output_'+p,state='whole_raw',parent=None) for p,m in [('carrot',.12),('potato',.20),('bok_choy',.10),('tomato',.15)]};self.history=[]
 def total(self):return sum(v['mass_kg'] for v in self.nodes.values())
 def transform(self,parent,children,checked_working_stroke,quality_assumption):
  if not checked_working_stroke or not checked_working_stroke.get('pass_'):raise ValueError('No admitted working stroke; transformation cannot commit')
  source=self.nodes[parent];before=self.total()
  if abs(sum(n['mass_kg'] for n in children)-source['mass_kg'])>1e-12:raise ValueError('Mass conservation failure')
  if any(n['owner']!=source['owner'] for n in children):raise ValueError('Split cannot teleport material to output or scrap bin')
  if len({n['id'] for n in children})!=len(children) or any(n['id'] in self.nodes for n in children):raise ValueError('Duplicate food identity')
  del self.nodes[parent]
  for child in children:self.nodes[child['id']]=dict(child,parent=parent,quality_assumption=quality_assumption)
  assert abs(self.total()-before)<1e-12
  self.history.append(dict(parent=parent,children=[n['id'] for n in children],mass_before_kg=before,mass_after_kg=self.total(),stroke=checked_working_stroke['id']))

def carrot_partition():
 outer=np.array([.160,.035,.035]);density=.12/np.prod(outer);peel=.0005;inner=np.array([.160,.034,.034]);segments=[]
 def part(n,size,center,kind):
  segments.append(dict(id=n,size_m=list(size),center_relative_original_m=list(center),mass_kg=float(density*np.prod(size)),owner='root_cradle',state=kind,parent='carrot'))
 # Non-overlapping four-side peel shell; end skins leave with explicit trim.
 for sign in (-1,1):
  part('carrot_peel_z_'+str(sign),[.160,.035,peel],[0,0,sign*(.0175-peel/2)],'peel_scrap')
  part('carrot_peel_y_'+str(sign),[.160,peel,.034],[0,sign*(.0175-peel/2),0],'peel_scrap')
  part('carrot_end_'+str(sign),[.004,.034,.034],[sign*.078,0,0],'end_trim_scrap')
 for k in range(30):part('carrot_slice_'+str(k+1),[.152/30,.034,.034],[-.076+(k+.5)*.152/30,0,0],'cut_edible')
 for a,b in itertools.combinations(segments,2):
  overlap=np.minimum(np.array(a['center_relative_original_m'])+np.array(a['size_m'])/2,np.array(b['center_relative_original_m'])+np.array(b['size_m'])/2)-np.maximum(np.array(a['center_relative_original_m'])-np.array(a['size_m'])/2,np.array(b['center_relative_original_m'])-np.array(b['size_m'])/2)
  assert not np.all(overlap>1e-10),(a['id'],b['id'])
 assert abs(sum(x['mass_kg'] for x in segments)-.12)<1e-12
 return segments

def save_contract():
 pieces=carrot_partition();checks=[];l=Ledger();extra_guards={}
 for bad in [None,dict(id='unplanned_cut',pass_=False)]:
  try:l.transform('carrot',pieces,bad,'Future quality test');checks.append(False)
  except ValueError:checks.append(True)
 for kind in ('mass_loss','teleport','duplicate'):
  test=copy.deepcopy(pieces)
  for child in test:child['owner']='output_carrot'
  if kind=='mass_loss':test[0]['mass_kg']*=.9
  if kind=='teleport':test[0]['owner']='waste_bin'
  if kind=='duplicate':test[1]['id']=test[0]['id']
  try:l.transform('carrot',test,dict(id='isolated_unit_test',pass_=True),'test only');extra_guards[kind]=False
  except ValueError:extra_guards[kind]=True
 write('v3/food_transformation_contract.json',dict(actual_initial_mass_kg=l.total(),executed_transformations=0,actual_food_states=l.nodes,
  quality_status='ASSUMPTION, never inferred from kinematic simulation. Visible dirt, peel depth, eyes/core, cut quality and food damage require later physical tests.',
  admission='Exact modeled ownership handoff, working stroke, child creation at parent volume, and every delivery path must pass before commit. Quality assumption is permitted after these geometric operations, not a reason to skip them.',
  carrot=dict(initial_size_m=[.160,.035,.035],raw_mass_kg=.12,nominal_peel_depth_mm=.5,end_trim_each_mm=4,slice_count=30,slice_thickness_mm=152/30,children=pieces,edible_mass_kg=sum(x['mass_kg'] for x in pieces if x['state']=='cut_edible'),scrap_mass_kg=sum(x['mass_kg'] for x in pieces if x['state']!='cut_edible'),partition_volume_and_mass_pass=True,children_created_in_original_volume=True,all_scrap_delivery_pending=True,executed=False),
  other_foods=dict(potato='Whole->washed->0.5mm nominal peel plus actual detected eye/core meshes->5mm slices->three fresh2L changes; eye count is detected, not fixed',bok_choy='Root disk->actual detected leaf bodies->600s cold soak->each crease2-5N->stalk splitting as needed->30-50mm sections',tomato='Detected hard-core mesh only->8 radial wedge children preserving pulp/seeds;0.65-1.35 mean mass and35-55deg declared physical assumptions'),
  guards_tested=dict(unchecked_transform_rejected=all(checks),additional_rejections=extra_guards,mass_remains_kg=l.total(),no_food_committed_as_finished=True)))
 # Compile a disconnected partition illustration at exactly the original raw
 # carrot coordinates. It is explicitly excluded from the persistent prefix.
 ch=StationCell(32,None,{'output_carrot':seats(register(32)[0])['wash_basin']});root=E.fromstring(ch.xml);food=root.find(".//body[@name='food_carrot']");carrier=root.find(".//body[@name='carrier_carrot']");carrier.remove(food)
 for item in pieces:
  center=np.array(item['center_relative_original_m'])+[0,0,.0215];b=body(carrier,item['id'],center);E.SubElement(b,'inertial',pos='0 0 0',mass=str(item['mass_kg']),diaginertia='0.000001 0.000001 0.000001');box(b,item['id']+'_solid',[0,0,0],item['size_m'],'.95 .43 .14 1' if item['state']=='cut_edible' else '.53 .29 .12 1')
 path=V3/'models/carrot_partition_NOT_EXECUTED.xml';path.write_text(E.tostring(root,encoding='unicode'));m=mujoco.MjModel.from_xml_path(str(path));assert len([i for i in range(m.nbody) if m.body(i).name.startswith(('carrot_slice_','carrot_peel_','carrot_end_'))])==36

if __name__=='__main__':save_contract()
