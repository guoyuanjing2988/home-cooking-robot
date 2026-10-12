from v6_common import *
import persistent_v6_r07 as p
import xml.etree.ElementTree as E
checks={};probes=[]
def fingerprint(w):
 return json.dumps(w.snapshot(),sort_keys=True)+repr([(n,E.tostring(o['body'])) for n,o in w.objects.items()])+repr(w.transforms)
def reject(label,w,fn):
 before=fingerprint(w);err=None
 try:fn()
 except ValueError as e:err=str(e)
 checks[label]=bool(err) and before==fingerprint(w);probes.append(dict(test=label,rejected=bool(err),rollback=before==fingerprint(w),reason=err))
def place(w,prod,station):
 o=w.objects['food:'+prod];o['support']=station;o['pose']=p.T(w.station_regions(station)['input']['center'],np.eye(3));return o
def independent_containment(body,pose,reg):
 # Closed-form support extrema of every original primitive after composing its full transform.
 lo=np.full(3,np.inf);hi=-lo
 for g in p.local_geoms(body).values():
  t=pose@g['transform'];Q=reg['rotation'].T@t[:3,:3];c=reg['rotation'].T@(t[:3,3]-reg['center']);s0=g['size'];typ=g['type']
  if typ==6:r=abs(Q)@s0
  elif typ==2:r=np.full(3,s0[0])
  elif typ==3:r=s0[0]+s0[1]*abs(Q[:,2])
  elif typ==5:r=s0[0]*np.sqrt(Q[:,0]**2+Q[:,1]**2)+s0[1]*abs(Q[:,2])
  elif typ==4:r=np.sqrt((Q**2)@(s0**2))
  else:raise ValueError('Unsupported primitive '+str(typ))
  lo=np.minimum(lo,c-r);hi=np.maximum(hi,c+r)
 margin=float(min(np.min(lo+reg['half']),np.min(reg['half']-hi)))
 return dict(pass_=margin>=-1e-9,margin_m=margin,minimum=lo.tolist(),maximum=hi.tolist())
w=p.World();station='BFP610_processing_bowl'
reject('wrong_support',w,lambda:w.transform('carrot','slices',station,None,'review probe'))
o=place(w,'carrot',station);o['pose'][:3,3]=[9,9,9]
reject('9m_remote_geometry',w,lambda:w.transform('carrot','slices',station,None,'review probe'))
o=place(w,'carrot',station);o['pose'][2,3]=1.375
reject('old_above_appliance_geometry',w,lambda:w.transform('carrot','slices',station,None,'review probe'))
o=place(w,'carrot',station);o['pose'][0,3]+=w.station_regions(station)['input']['half'][0]-.001
reject('center_inside_full_input_protrudes',w,lambda:w.transform('carrot','slices',station,None,'review probe'))
o=place(w,'carrot',station);w.attached='food:carrot'
reject('held_food',w,lambda:w.transform('carrot','slices',station,None,'review probe'));w.attached=None
reject('overcapacity',w,lambda:w.transform('carrot','slices',station,None,'review probe',packing=.001))
reject('unknown_operation',w,lambda:w.transform('carrot','invented',station,None,'review probe'))
reject('negative_duration',w,lambda:w.transform('carrot','slices',station,-1,'review probe'))
touch=E.tostring(o['full_touch_body']);evt=w.transform('carrot','slices',station,None,'unqualified exact batch time');o=w.objects['food:carrot'];reg=w.station_regions(station);out=independent_containment(o['body'],o['pose'],reg['output']);scr=w.objects['scrap:carrot:'+station];scrcheck=independent_containment(scr['body'],scr['pose'],reg['scrap'])
checks.update(output_inside_own_region=out['pass_'],scrap_inside_own_region=scrcheck['pass_'],full_touch_unchanged=touch==E.tostring(o['full_touch_body']),mass_conserved=abs(w.snapshot()['total_food_kg']-.57)<1e-12,volume_correct=abs(np.prod(evt['bed_size_m'])-evt['edible_after_kg']/evt['bulk_density_kg_m3']/evt['packing_fraction'])<1e-12,unknown_duration_not_zero=evt['duration_s'] is None and not evt['duration_qualified'])
reject('bulk_direct_attachment',w,lambda:w.rebind('food:carrot','R',o['pose']));reject('bulk_direct_reframe',w,lambda:w.reframe('food:carrot',o['h']))
place(w,'potato',station);reject('occupied_container',w,lambda:w.transform('potato','slices',station,None,'review probe'))
fresh=p.World();o=fresh.objects['food:carrot'];far=o['pose'].copy();far[0,3]+=.001
reject('1mm_binding_teleport',fresh,lambda:fresh.rebind('food:carrot','R',far));fresh.rebind('food:carrot','R',o['pose']);reject('second_attachment',fresh,lambda:fresh.rebind('food:potato','R',fresh.objects['food:potato']['pose']))
h=copy.deepcopy(o['h']);h['food_state']='half';reject('resized_regrasp',fresh,lambda:fresh.reframe('food:carrot',h))
fresh=p.World();place(fresh,'carrot','linear_peeler_holder');fresh.transform('carrot','peeled','linear_peeler_holder',2823.529,'P16 engineering allowance');old=copy.deepcopy(fresh.objects['scrap:carrot:linear_peeler_holder']);place(fresh,'carrot',station);fresh.transform('carrot','slices',station,None,'review probe');new=fresh.objects['scrap:carrot:linear_peeler_holder'];checks['old_scrap_stays_at_peeler']=old['mass']==new['mass'] and np.array_equal(old['pose'],new['pose']);checks['station_scrap_sums']=abs(sum(x['mass'] for k,x in fresh.objects.items() if k.startswith('scrap:'))-sum(fresh.scrap.values()))<1e-12
states=[];fkchecks=[];events=[];failures=[];scene_rows=[]
for file in sorted((I/'results/connections_v6'/v.ID).glob('*.json'),key=lambda f:int(f.stem)):
 r=json.loads(file.read_text());snapshots=[r['state_before'],r['conditional_state_after_attempt']]+[st for leg in r['legs'] for st in (leg['state'],leg['state_after_checked_leg'])]
 for st in snapshots:
  mass=sum(st['food_mass_kg'].values())+sum(st['scrap_mass_kg'].values());owner=[n for n,o in st['objects'].items() if o['owner']=='R'];scrapmass=sum(o['mass_kg'] for n,o in st['objects'].items() if n.startswith('scrap:'))
  states.append(dict(connection=r['connection'],mass_ok=abs(mass-.57)<1e-12,ownership_ok=owner==([st['attached']] if st['attached'] else []),scrap_mass_matches=abs(scrapmass-sum(st['scrap_mass_kg'].values()))<1e-12))
 for leg in r['legs']:
  update=leg['carried_pose_update'];attached=leg['state']['attached']
  if update:
   xml=(I/leg['model_xml']).read_text();ch=v.scene(r['from_stroke']['index']);ch.xml=xml;ch.bind_model(mujoco.MjModel.from_xml_string(xml));actual=p.fk(ch,np.array(leg['planner']['path'][-1]));stored=np.array(leg['state_after_checked_leg']['objects'][attached]['pose']);fkchecks.append(dict(connection=r['connection'],leg=leg['name'],max_error=float(np.max(abs(stored-actual))),passed_leg=leg['pass_']))
  elif attached:fkchecks.append(dict(connection=r['connection'],leg=leg['name'],unchanged=leg['state']['objects'][attached]['pose']==leg['state_after_checked_leg']['objects'][attached]['pose'],passed_leg=leg['pass_']))
 for e in r['conditional_state_construction']:
  if e['operation']=='conditional_food_transformation':events.append(dict(connection=r['connection'],event=e['event']))
  if 'reject' in e['operation'] or 'unqualified' in e['operation']:failures.append(dict(connection=r['connection'],trace=e))
seq=read('state_sequence.json');ch=v.scene(0)
R05=I.parents[1]/'r05/integrator';old=mujoco.MjModel.from_xml_path(str(R05/'models/witnesses/Q01__water_on.xml'));names={old.geom(i).name:i for i in range(old.ngeom)};fixed=[]
for j,n in enumerate(ch.gnames):
 if n in names and n.startswith(('north_wall','upper_cabinet','counter','sink','stove','floor','south_wall')):
  i=names[n];fixed.append(dict(name=n,unchanged=all(np.array_equal(getattr(old,k)[i],getattr(ch.m,k)[j]) for k in ('geom_type','geom_size','geom_pos','geom_quat'))))
dump('meal.json',dict(checks=checks,all_probes_pass=all(checks.values()),negative_probes=probes,independent_bulk_containment=out,independent_scrap_containment=scrcheck,state_snapshots=len(states),snapshot_invariants=states,all_snapshot_invariants=all(all(r[k] for k in ('mass_ok','ownership_ok','scrap_mass_matches')) for r in states),carried_FK=fkchecks,all_carried_FK_match=all(r.get('max_error',0)<1e-10 and r.get('unchanged',True) for r in fkchecks),unique_transformations=list({json.dumps(e['event'],sort_keys=True):e['event'] for e in events}.values()),conditional_rejections=failures,executed_state_is_initial=seq['initial_state']==seq['executed_state'],executed_prefix=seq['executed_prefix_connections'],fixed_kitchen=fixed,helper_bodies=[ch.m.body(i).name for i in range(ch.m.nbody) if ch.m.body(i).name.startswith('L_')],full_bfp610_reservation_m=(2*ch.m.geom_size[ch.m.geom('bfp610_complete_envelope').id]).tolist()))
print('MEAL',all(checks.values()),'states',len(states),'FK',len(fkchecks),flush=True)
