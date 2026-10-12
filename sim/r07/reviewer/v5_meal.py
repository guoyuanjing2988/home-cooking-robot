from v5_common import *
import persistent_v5_r07 as p
import hashlib,xml.etree.ElementTree as E
R05=I.parents[1]/'r05/integrator';old=mujoco.MjModel.from_xml_path(str(R05/'models/witnesses/Q01__water_on.xml'));ch=v.scene(0);new=ch.m
names={old.geom(i).name:i for i in range(old.ngeom)};fixed=[]
for j,n in enumerate(ch.gnames):
 if n in names and n.startswith(('north_wall','upper_cabinet','counter','sink','stove','floor','south_wall')):
  i=names[n];fixed.append(dict(name=n,unchanged=all(np.array_equal(getattr(old,k)[i],getattr(new,k)[j]) for k in ('geom_type','geom_size','geom_pos','geom_quat'))))
world=p.World();initial=world.snapshot();checks={};probes=[]
def refused(fn):
 try:fn();return False
 except ValueError:return True
checks['raw_support_transform_rejected']=refused(lambda:world.transform('carrot','slices','BFP610_processing_bowl',None,'unqualified'))
obj=world.objects['food:carrot'];obj['support']='BFP610_processing_bowl';world.attached='food:carrot'
checks['held_food_transform_rejected']=refused(lambda:world.transform('carrot','slices','BFP610_processing_bowl',None,'unqualified'))
world.attached=None;before=copy.deepcopy(obj['body']);before_touch=E.tostring(obj['full_touch_body']);before_pose=obj['pose'].copy();obj['pose'][:3,3]=[9,9,9]
event=world.transform('carrot','slices','BFP610_processing_bowl',None,'reviewer adversarial location probe')
probes.append(dict(test='food physically outside named station but support string matches',accepted=True,world_center_m=obj['pose'][:3,3].tolist(),event=event))
checks['mass_conserved']=abs(world.snapshot()['total_food_kg']-.57)<1e-12
checks['full_touch_body_unchanged']=before_touch==E.tostring(obj['full_touch_body'])
checks['bulk_direct_rebind_rejected']=refused(lambda:world.rebind('food:carrot','R',obj['pose']))
checks['bulk_direct_reframe_rejected']=refused(lambda:world.reframe('food:carrot',obj['h']))
checks['unknown_time_not_zero']=event['duration_s'] is None and not event['duration_qualified']
bed=event['bed_size_m'];checks['bulk_volume_mass_density_packing']=abs(np.prod(bed)-event['edible_after_kg']/event['bulk_density_kg_m3']/event['packing_fraction'])<1e-12
fresh=p.World();o=fresh.objects['food:carrot'];far=o['pose'].copy();far[0,3]+=.001
checks['one_mm_teleport_rejected']=refused(lambda:fresh.rebind('food:carrot','R',far));fresh.rebind('food:carrot','R',o['pose']);checks['second_attachment_rejected']=refused(lambda:fresh.rebind('food:potato','R',fresh.objects['food:potato']['pose']))
changed=copy.deepcopy(o['h']);changed['food_state']='half'
checks['resized_regrasp_rejected']=refused(lambda:fresh.reframe('food:carrot',changed))
rows=[];transform_events=[];container_pose_changes=[]
for file in sorted((I/'results/connections_v5'/v.ID).glob('*.json'),key=lambda x:int(x.stem)):
 r=json.loads(file.read_text());states=[r['state_before'],r['conditional_state_after_attempt']]+[l['state'] for l in r['legs']]
 for st in states:
  mass=sum(st['food_mass_kg'].values())+sum(st['scrap_mass_kg'].values());owners=[n for n,o in st['objects'].items() if o['owner']=='R']
  rows.append(dict(connection=r['connection'],mass_kg=mass,mass_ok=abs(mass-.57)<1e-12,ownership_ok=owners==([st['attached']] if st['attached'] else [])))
 for trace in r['conditional_state_construction']:
  if trace['operation']=='conditional_food_transformation':transform_events.append(dict(connection=r['connection'],event=trace['event'],executed=trace.get('prerequisites_executed')))
seq=read('state_sequence.json')
dump('meal.json',dict(checks=checks,adversarial_probes=probes,all_snapshot_mass_ok=all(r['mass_ok'] for r in rows),all_snapshot_ownership_ok=all(r['ownership_ok'] for r in rows),state_snapshots=len(rows),unique_transformations=list({json.dumps(x['event'],sort_keys=True):x['event'] for x in transform_events}.values()),executed_state_is_initial=seq['initial_state']==seq['executed_state'],executed_prefix=seq['executed_prefix_connections'],initial_objects=list(initial['objects']),fixed_kitchen=fixed,helper_bodies=[new.body(i).name for i in range(new.nbody) if new.body(i).name.startswith('L_')],full_bfp610_reservation_m=(2*new.geom_size[new.geom('bfp610_complete_envelope').id]).tolist(),scope='Independent state invariant and boundary probes. Remote-location acceptance is an enforcement defect, not a demonstrated executed food teleport. No accepted meal exists.'))
print('MEAL',checks,'snapshots',len(rows),'mass',all(r['mass_ok'] for r in rows),'owners',all(r['ownership_ok'] for r in rows),'transforms',len(transform_events),flush=True)
