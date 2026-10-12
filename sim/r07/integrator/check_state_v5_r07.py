"""Focused negative checks for food-only abstraction and attachment continuity."""
import os,sys,json,copy,hashlib
os.environ['R07_LAYOUT']=sys.argv[1]
import numpy as np
import persistent_v5_r07 as p
w=p.World();initial=w.snapshot();checks={}
try:w.transform('carrot','slices','BFP610_processing_bowl',10,'test')
except ValueError:checks['cannot_transform_food_on_raw_land']=w.snapshot()==initial
w.objects['food:carrot']['support']='linear_peeler_holder';w.attached='food:carrot';before=w.snapshot()
try:w.transform('carrot','peeled','linear_peeler_holder',2823.529,'test')
except ValueError:checks['cannot_transform_held_food']=w.snapshot()==before
w.attached=None
a=w.transform('carrot','peeled','linear_peeler_holder',6*2*.160/.0034/.20,'P16 data-derived cycle')
w.objects['food:carrot']['support']='BFP610_processing_bowl';b=w.transform('carrot','slices','BFP610_processing_bowl',None,'Exact batch duration unknown')
checks['food_plus_scrap_conserved']=abs(w.snapshot()['total_food_kg']-.57)<1e-12 and a['conserved'] and b['conserved']
checks['bulk_volume_equals_mass_over_density_packing']=abs(np.prod(b['bed_size_m'])-b['edible_after_kg']/(b['bulk_density_kg_m3']*b['packing_fraction']))<1e-12
checks['unknown_duration_not_zero']=b['duration_s'] is None and not b['duration_qualified']
checks['full_touch_body_retained']=w.objects['food:carrot'].get('full_touch_body') is not None
before=w.snapshot();bad=w.objects['food:carrot']['pose'].copy();bad[0,3]+=.001
try:w.rebind('food:carrot','R',bad)
except ValueError:checks['one_mm_teleport_rejected']=before==w.snapshot()
try:w.rebind('food:carrot','R',w.objects['food:carrot']['pose'].copy())
except ValueError:checks['bulk_direct_attachment_rejected']=w.attached is None
event=w.rebind('food:potato','R',w.objects['food:potato']['pose'].copy());checks['same_pose_bind_accepted']=event['pass_']
try:w.rebind('food:tomato','R',w.objects['food:tomato']['pose'].copy())
except ValueError:checks['second_simultaneous_object_rejected']=w.attached=='food:potato'
rigid=p.World();obj=rigid.objects['food:carrot'];oldpose=obj['pose'].copy();oldparts=p.local_geoms(obj['body']);h=copy.deepcopy(obj['h']);h['object_rotation_deg']=[13,27,41];event=rigid.reframe('food:carrot',h,commit=True);newparts=p.local_geoms(obj['body'])
checks['rigid_regrasp_keeps_every_world_part']=all(np.max(abs(oldpose@part['transform']-obj['pose']@newparts[name]['transform']))<1e-7 for name,part in oldparts.items())
h['food_state']='half'
try:rigid.reframe('food:carrot',h,commit=True)
except ValueError:checks['regrasp_cannot_shrink_food']=True
checks={k:bool(v) for k,v in checks.items()};out=dict(layout=p.v.ID,pass_=all(checks.values()),checks=checks,initial=initial,transformations=[a,b],scope='Unit checks of state invariants, not robot path or completed product evidence.')
(p.v.O/'state_model_regression_v5.json').write_text(json.dumps(out,indent=2));print('STATE_CHECKS',out['pass_'],checks)
assert out['pass_']
