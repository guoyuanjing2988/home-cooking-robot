"""Containment and transactional negative probes, not robot execution."""
import os,sys,json,copy,hashlib
os.environ['R07_LAYOUT']=sys.argv[1]
import numpy as np
import persistent_v6_r07 as p
w=p.World();checks={};events=[]
h=p.zero(dict(held='root_food',held_kg=3.,contacts=[dict(kind='working_stroke'),dict(kind='grasp_release_support')]))
checks['free_transfer_retains_payload_acceleration_SF']=len(h['check_forces_N'])==6 and all(abs(np.linalg.norm(f)-1.35)<1e-12 for f in h['check_forces_N'])
checks['free_transfer_has_no_working_permission']=all(c['kind']=='grasp_release_support' for c in h['contacts'])
def fingerprint(w):
 return json.dumps(w.snapshot(),sort_keys=True)+repr([(n,p.E.tostring(o['body'])) for n,o in w.objects.items()])+repr(w.transforms)
def reject(label,call):
 before=fingerprint(w)
 try:call();checks[label]=False
 except ValueError:checks[label]=fingerprint(w)==before
reject('wrong_support_rejected',lambda:w.transform('carrot','slices','BFP610_processing_bowl',None,'unqualified batch time'))
obj=w.objects['food:carrot'];obj['support']='BFP610_processing_bowl';obj['pose'][:3,3]=[9,9,9]
reject('reviewer_9m_pose_rejected_transactionally',lambda:w.transform('carrot','slices','BFP610_processing_bowl',None,'test'))
reg=w.station_regions('BFP610_processing_bowl');obj['pose'][:3,3]=reg['input']['center'];obj['pose'][2,3]=1.375
reject('reviewer_above_appliance_pose_rejected',lambda:w.transform('carrot','slices','BFP610_processing_bowl',None,'test'))
obj['pose'][:3,3]=reg['input']['center'];w.attached='food:carrot'
reject('held_food_rejected',lambda:w.transform('carrot','slices','BFP610_processing_bowl',None,'test'));w.attached=None
reject('output_capacity_rejected_before_mass_commit',lambda:w.transform('carrot','slices','BFP610_processing_bowl',None,'test',packing=.001))
e=w.transform('carrot','slices','BFP610_processing_bowl',None,'Exact batch duration unqualified');events.append(e)
checks['output_inside_declared_bowl']=e['output_containment']['pass_'];checks['scrap_inside_own_cutting_container']=e['scrap_containment']['pass_'] and w.objects['scrap:carrot:BFP610_processing_bowl']['support']=='BFP610_processing_bowl';checks['full_exterior_also_contains_output']=w.contains(w.objects['food:carrot']['body'],w.objects['food:carrot']['pose'],reg['input'])['pass_'];checks['mass_conserved']=e['conserved'] and abs(w.snapshot()['total_food_kg']-.57)<1e-12;checks['unknown_duration_not_zero']=e['duration_s'] is None
checks['volume_from_mass_density_packing']=abs(np.prod(e['bed_size_m'])-e['edible_after_kg']/(e['bulk_density_kg_m3']*e['packing_fraction']))<1e-12
reject('bulk_direct_attachment_rejected',lambda:w.rebind('food:carrot','R',w.objects['food:carrot']['pose'].copy()))
bad=w.objects['food:potato']['pose'].copy();bad[0,3]+=.001;reject('one_mm_binding_teleport_rejected',lambda:w.rebind('food:potato','R',bad))
w.rebind('food:potato','R',w.objects['food:potato']['pose'].copy());reject('second_attachment_rejected',lambda:w.rebind('food:tomato','R',w.objects['food:tomato']['pose'].copy()))
w.attached=None;w.objects['food:potato']['support']='BFP610_processing_bowl';w.objects['food:potato']['pose']=p.T(reg['input']['center'],np.eye(3));reject('occupied_bulk_container_rejected',lambda:w.transform('potato','slices','BFP610_processing_bowl',None,'test'))
reject('unknown_operation_rejected',lambda:w.transform('potato','imaginary_cut','BFP610_processing_bowl',None,'test'))
other=p.World();food=other.objects['food:carrot'];food['support']='linear_peeler_holder';food['pose']=p.T(other.station_regions('linear_peeler_holder')['input']['center'],np.eye(3));other.transform('carrot','peeled','linear_peeler_holder',2823.529,'P16 design allowance');old=copy.deepcopy(other.objects['scrap:carrot:linear_peeler_holder']);other.objects['food:carrot']['support']='BFP610_processing_bowl';other.objects['food:carrot']['pose']=p.T(reg['input']['center'],np.eye(3));other.transform('carrot','slices','BFP610_processing_bowl',None,'unqualified');after=other.objects['scrap:carrot:linear_peeler_holder'];checks['prior_peel_scrap_does_not_teleport']=np.array_equal(old['pose'],after['pose']) and old['mass']==after['mass'];checks['all_station_scrap_masses_match_ledger']=abs(sum(o['mass'] for n,o in other.objects.items() if n.startswith('scrap:'))-sum(other.scrap.values()))<1e-12
checks={k:bool(a) for k,a in checks.items()};out=dict(layout=p.v.ID,pass_=all(checks.values()),checks=checks,transformations=events,scope='Containment is necessary; declared OEM cavity shape and physical loading/controls remain unqualified. No executable meal credit.')
(p.v.O/'state_model_regression_v6.json').write_text(json.dumps(out,indent=2));print('CONTAINMENT',out['pass_'],checks,flush=True);assert out['pass_']
