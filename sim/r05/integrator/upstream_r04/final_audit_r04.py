"""Artifact/invariant checks, not tests which mirror an implementation."""
import json,hashlib,csv,collections,xml.etree.ElementTree as E
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2];O=H/'results';A=H/'audit'
def read(p):return json.loads(p.read_text())
P=read(O/'process_v3.json')
old=read(ROOT/'sim/r03/integrator/results/process_v3.json')
def force_parts(p):
 return {(ph['id'],sg['label']):[{side:{k:h[k] for k in ['held_kg','nominal_forces_N','check_forces_N','nominal_moments_Nm','check_moments_Nm','grip']} for side,h in po.items()} for po in sg['poses']] for ph in p['phases'] for sg in ph['segments']}
forces=dict(acceptance_unchanged=P['acceptance']==old['acceptance'],finished_products_unchanged=P['finished_products']==old['finished_products'],tools_full_geometry_unchanged=P['tools']==old['tools'],all_force_models_unchanged=P['force_models']==old['force_models'],all_stroke_mass_force_grip_cases_unchanged=force_parts(P)==force_parts(old),policy='R02/R03 sourced and physics-derived force bounds retained exactly, including proxies. No force was selected to improve acceptance or time.')
(O/'force_audit.json').write_text(json.dumps(forces,indent=2));assert all(v for k,v in forces.items() if isinstance(v,bool))
hashes=read(A/'input_hashes.json');changed=[]
for name,digest in hashes.items():
 p=ROOT/name
 if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:changed.append(name)
assert not changed,changed
static=read(O/'phase_summary.json');best=read(O/'best.json');motion=read(O/'motion.json');cost=read(O/'cost_summary.json');cheap=read(O/'cheapest.json');schedule=read(O/'schedule.json');seq=read(O/'state_sequence.json');pm=read(O/'persistent_model.json')
assert static['strokes_total']==105 and static['logical_total']==27
assert len(best['witnesses'])==static['verified_witnesses']==105
assert len(motion['connections'])==104 and len(motion['internal_paths'])==105 and motion['connections_passed']==0
assert best['motion_status']=='fail' and not best['overall_pass']
assert cheap['passing_configuration'] is None and cheap['cost_cny'] is None
assert best['cost_cny']==cost['totals']['best_candidate'] and best['prep_min_planning']==schedule['planned_prep_min']
assert pm['ownership_pass'] and not pm['executable']
assert len(seq['events'])==295 and seq['unverified_required_events']==293
assert read(O/'distance_validation.json')['all_regressions_pass']
assert read(O/'envelope_reachability_audit.json')['all_witnesses_reachable']
assert motion['passing']['pass_'] and motion['passing']['continuous_certificate']['ok']
resources=[dict(file=p.name,**read(p)) for p in A.glob('*.resource.json')]
assert all(r['timeout_s']<1200 and r['peak_MiB']<1900 for r in resources)
assert (H/'reference.py').read_bytes()==(ROOT/'sim/r02/concept2/reference.py').read_bytes()
bytes_total=sum(p.stat().st_size for p in H.rglob('*') if p.is_file());assert bytes_total<3*1024**3
required=['overview','parked','parked_doors_open','passing','conserved_initial','potato_wash','potato_peel','potato_cut','potato_delivery']+[f'Q{i:02}' for i in range(1,28)]
from PIL import Image
for n in required:
 if (H/'renders'/(n+'.png')).exists():
  with Image.open(H/'renders'/(n+'.png')) as im:im.verify()
with Image.open(H/'renders/full_meal_storyboard.gif') as im:assert im.n_frames==21
assert (ROOT/'posts/r04/integrator.md').read_text(encoding='utf-8').startswith('中文摘要：')
missing=[str(H/'renders'/(n+'.png')) for n in required if not(H/'renders'/(n+'.png')).exists()]
out=dict(status='PASS' if not missing else 'PENDING_RENDERS',checked_input_files=len(hashes),upstream_inputs_unchanged=not changed,unchanged_reference_sha256=hashlib.sha256((H/'reference.py').read_bytes()).hexdigest(),force_audit=forces,output_bytes=bytes_total,output_GiB=bytes_total/1024**3,resource_runs=len(resources),max_recorded_peak_MiB=max(r['peak_MiB'] for r in resources),max_timeout_s=max(r['timeout_s'] for r in resources),cpu_only=True,worker_concurrency_policy='At most4 simulation/render/download workers; serial foreground bounded chunks, no unattended service. Wrapper processes monitor workers, do not compute solver/render work.',missing_renders=missing,limitations='Artifact consistency PASS does not mean complete meal PASS; the documented geometric, path, idle, model/hardware and food-quality failures remain.')
(A/'final_audit.json').write_text(json.dumps(out,indent=2));print('audit',out['status'],'input files',len(hashes),'GiB',round(out['output_GiB'],3),'peak',out['max_recorded_peak_MiB'])
