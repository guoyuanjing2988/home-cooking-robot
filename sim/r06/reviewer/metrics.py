"""Finalize numerical/ledger/cost review metrics; no writes outside reviewer."""
import os
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[n]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import sys,json,math,csv,hashlib,time
from pathlib import Path
import numpy as np,mujoco
H=Path(__file__).resolve().parent;ROOT=H.parents[2];UP=ROOT/'sim/r06/integrator'
sys.path.insert(0,str(UP));import jobs as j;import cell as c
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,v):(H/n).write_text(json.dumps(v,indent=2,allow_nan=False,default=lambda x:x.tolist() if isinstance(x,np.ndarray) else x.item() if isinstance(x,np.generic) else str(x)),encoding='utf-8')
static=read(H/'results/static_replay.json');passing=[x for x in static['rows'] if x['pass_']];poses=[p for r in passing for p in r['poses']]
strokes={}
for file in (H/'results').glob('stroke_replay*.json'):
    for r in read(file)['rows']:strokes[r['id']]=r
phase=read(UP/'results/phase_summary.json');motion=read(UP/'results/motion.json');pref=read(H/'results/prefix_replay.json');clear=read(UP/'results/clearance.json');cons=read(H/'results/conservation.json')
ds=read(H/'results/connection_rejections_0_17.json')['rows'];extras=read(H/'results/additional_connections_0_3.json')['rows'];rows=[]
for r in passing:
    job=j.JOBS[r['index']];ch=j.load_cell(job)
    for k,qrow in enumerate([x for x in phase['selected_witnesses'] if x['stroke']==r['id']]):
        q=np.array(qrow['q']);hs=c.hand(ch,job['targets'][0],job['load']);hs['R']['held_kg']=3.;rat,gr,cases=j.check_load(ch,q,hs);rows.append(dict(id=r['id'],pose_index=k,total_flange_kg=4.2,external_payload_kg=3.,torque_ratio=rat,grip_margin=gr,pass_=rat<=1 and gr>=1))
# Independently recompute rated-payload witness torques and offset maximization,
# retaining source inertias and removing only EOAT mass from the rated bare-arm test.
ch=c.Cell(j.V);m,d=ch.m,ch.d
for n in ('R_tool','R_jaw_minus','R_jaw_plus'):
    bid=m.body(n).id;m.body_mass[bid]=1e-9;m.body_inertia[bid]=1e-12
mujoco.mj_setConst(m,d);ix=[ch.qa[n] for n in c.ARM];dofs=[ch.da[n] for n in c.ARM];env=read(UP/'results/torque_envelope.json');caps=[]
for index,name in enumerate(c.ARM):
    witness=env['witnesses'][name];q=ch.q0.copy();q[ix]=witness['joints_rad'];d.qpos[:]=q;d.qvel[:]=0;mujoco.mj_forward(m,d)
    flange=m.site('R_attachment_site').id;R=d.site_xmat[flange].reshape(3,3);point=d.site_xpos[flange]+R@np.array(witness['CoM_flange_m']);jp=np.zeros((3,m.nv));jr=np.zeros_like(jp)
    mujoco.mj_jac(m,d,jp,jr,point,int(m.site_bodyid[flange]));tau=d.qfrc_bias-jp.T@np.array([0,0,-49.05]);actual=abs(float(tau[dofs[index]]));caps.append(dict(joint=name,stored_Nm=env['envelope_Nm'][name],recomputed_witness_Nm=actual,error_Nm=abs(actual-env['envelope_Nm'][name]),mount_variant=7,offset_radius_m=float(np.linalg.norm(witness['CoM_flange_m']))))
with (UP/'results/costs.csv').open(encoding='utf-8-sig',newline='') as f:cost=list(csv.DictReader(f))
subtotal=sum(float(x['line_cny']) for x in cost if x['id']!='RESERVE15');reserve=sum(float(x['line_cny']) for x in cost if x['id']=='RESERVE15');safety=[x for x in cost if 'safety' in x['item'].lower()]
# Engineering sensitivity case, explicitly NOT a released frame material/section.
F=(20.6+1.2+3)*9.81;L=1.31;E=69e9;I=(.04**4-.036**4)/12;delta=F*L**3/(48*E*I)
native_sources=[]
for item in read(H/'audit/provenance.json')['copies']:
    p=ROOT/item['source'];copy=UP/item['copy'];native_sources.append(dict(source=item['source'],source_and_copy_unchanged=hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'] and hashlib.sha256(copy.read_bytes()).hexdigest()==item['sha256']))
input_hashes=read(H/'audit/provenance.json')['binding_hashes'];unchanged_inputs=all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha for name,sha in input_hashes.items())
executed_min=[min(p['clearance'][cat]['reserve_mm'] for cat in p['clearance'] if cat!='self') for p in poses]
def quant(values):return {str(q):float(np.quantile(values,q/100)) for q in (0,5,25,50,75,95,100)}
summary=dict(static_strokes_passed=len(passing),full_geometry_handling_strokes=len(static['rows']),all_obligations=len(j.JOBS),conditional_held_poses=len(poses),static_numerator_disagreements=[r['id'] for r in static['rows'] if r['pass_']!=r['submitted_pass']],unique_full_strokes_replayed=len(strokes),full_strokes_passed=sum(x['pass_'] for x in strokes.values()),full_stroke_checked_states=sum(x['states_checked'] for x in strokes.values()),full_strokes=[{k:r[k] for k in ('id','pass_','states_checked','max_point_step_mm','min_reserve_mm')} for r in strokes.values()],maximum_stroke_point_step_mm=max(r['max_point_step_mm'] for r in strokes.values()),maximum_static_position_error_mm=max(p['position_mm'] for p in poses),maximum_static_orientation_error_deg=max(p['orientation_deg'] for p in poses),maximum_static_torque_ratio=max(p['torque_ratio'] for p in poses),minimum_static_grip_margin=min(p['grip_margin'] for p in poses),max_independent_torque_disagreement=max(p['torque_disagreement'] for r in static['rows'] for p in r['poses']),max_independent_grip_disagreement=max(p['grip_disagreement'] for r in static['rows'] for p in r['poses']),static_pose_minimum_reserve_mm=quant(executed_min),static_pose_fraction_ge_10=float(np.mean(np.array(executed_min)>=10)),static_category_reserves_mm=clear['static_distribution_mm'],prefix_full_replay=pref['rows'][0],unadmitted_partial_descent=pref['rows'][1],key_approach_failure=pref['rows'][2],submitted_loaded_connections_replayed=len(ds),loaded_rejection_witnesses_reproduced=sum(r['reproduced_rejection'] for r in ds),direct_candidate_paths=[dict(index=r['index'],from_=r['from_'],to=r['to'],bound_m=r['direct_endpoint_displacement_bound_m'],replay=r['independent_bounded_direct_replay']) for r in ds],longest_submitted_loaded_candidate=max(ds,key=lambda r:r['direct_endpoint_displacement_bound_m'])['index'],fresh_required_seams_searched=len(extras),fresh_search_seconds=[r['planner']['planner_time_s'] for r in extras],fresh_qualified_meal_paths=0,connection_review_count=len(ds)+len(extras)+1,meal_connections_passed=motion['connections_passed'],meal_connections_total=motion['connections_total'],meal=False,prep_min=None,cost_cny=subtotal+reserve,cost_subtotal_cny=subtotal,reserve_cny=reserve,safety_packages=len(safety),safety_cny=sum(float(x['line_cny']) for x in safety),cost_quote_status='engineering allowances only',payload_challenge_rows=rows,payload_challenge_all_pass=all(x['pass_'] for x in rows),rated_envelope_witnesses=caps,frame_sensitivity=dict(status='Reviewer sensitivity assumption; not claimed actual structure',span_m=L,section='40x40x2mm square aluminium tube, simply supported central load',E_Pa=E,load_N=F,deflection_mm=delta*1000,installed_composite_frame_unknown=True),conservation_all_actual_states_pass=all(abs(s['mass_kg']-.57)<1e-10 and s['every_joint_recorded'] and all(f['own_parent_present'] and f['body_instances']==1 for f in s['food']) and all(p['max_pose_error_m']<1e-10 and p['lid'] in (0,None) for p in s['containers']) for s in cons['physical_states']),proposed_ledger_all_80_states_mass_conserved=all(abs(s['mass_kg']-.57)<1e-10 for s in cons['proposed_states']),utility_current_A=1320/(230*.8),three6L_fills_s=3*6/6*60,conditional_root_cut_engagement_s=30*.035/.0005+18*.07/.0005,native_sources_unchanged=all(x['source_and_copy_unchanged'] for x in native_sources),binding_inputs_unchanged=unchanged_inputs)
save('results/metrics.json',summary);save('audit/source_immutability.json',dict(copies=native_sources,binding_inputs_unchanged=unchanged_inputs))
print('FINAL REVIEW METRICS',len(passing),'/',len(j.JOBS),'strokes; independent full strokes',len(strokes),'; connections reviewed',len(ds)+len(extras)+1,'; actual meal',motion['connections_passed'],'/',motion['connections_total'],'; cost',subtotal+reserve,flush=True)
