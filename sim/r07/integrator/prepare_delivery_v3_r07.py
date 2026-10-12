"""Fresh rebuild before rendering; separate foreground stage from long IK jobs."""
import sys,json,time,subprocess,ast,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';ID=sys.argv[1];begin=time.monotonic();rows=[]
for p in H.glob('*v3*r07.py'):ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p))
# Correct one documentary coordinate which the runtime already overrides.
# No actual compiled collision geometry or task pose changes here.
file=O/f'layouts/{ID}_process.json';P=json.loads(file.read_text());cfg=json.loads((O/f'layouts/{ID}.json').read_text());g=next(x for x in P['installed_geometry'] if x['name']=='secondary_drive_guard');expected=[cfg['station_frames']['secondary']['new_center'][0],.47,.70]
if g['pos']!=expected:
 old=file.read_bytes();archive=H/'audit'/f'{ID}_process_before_metadata_reconciliation.json';archive.write_bytes(old);before=g['pos'];g['pos']=expected;file.write_text(json.dumps(P,indent=2));(H/'audit'/f'{ID}_metadata_reconciliation.json').write_text(json.dumps(dict(field='installed_geometry.secondary_drive_guard.pos',before=before,after=expected,old_sha256=hashlib.sha256(old).hexdigest(),new_sha256=hashlib.sha256(file.read_bytes()).hexdigest(),physical_change=False,reason='Runtime always uses station_frames.secondary.new_centerX,.47,.70. Correct the exported documentary coordinate; fresh model hashes must still match all saved searches.'),indent=2))
stages=[('persistent_v2_r07.py',[ID]),('fresh_admission_v2_r07.py',[ID]),('rules_v3_r07.py',[ID]),('deliver_v3_r07.py',[ID]),('failure_evidence_v3_r07.py',[ID]),('counter_and_arm_r07.py',[ID]),('map_figure_v3_r07.py',[ID])]
if len(sys.argv)>2:stages=stages[[x[0] for x in stages].index(sys.argv[2]):]
prior=H/'audit'/f'{ID}_delivery_prepare.json'
if prior.exists():(H/'audit'/f'{ID}_delivery_prepare_previous_{time.time_ns()}.json').write_bytes(prior.read_bytes())
for script,args in stages:
 remaining=1050-(time.monotonic()-begin)
 if remaining<30:raise RuntimeError('Prepare stage budget exhausted; resume remaining scripts separately.')
 start=time.monotonic();r=subprocess.run([sys.executable,'-B',script,*args],timeout=remaining);rows.append(dict(script=script,elapsed_s=time.monotonic()-start,exit_code=r.returncode));(H/'audit'/f'{ID}_delivery_prepare.json').write_text(json.dumps(rows,indent=2));print('PREPARE',rows[-1],flush=True)
 if r.returncode:raise RuntimeError(script)
model=json.loads((O/'persistent_model.json').read_text());model['fixed_faucet_operating_state']=cfg['replacement_faucet'];model['water_valve_execution_verified']=False;(O/'persistent_model.json').write_text(json.dumps(model,indent=2))
motion=json.loads((O/'motion.json').read_text());motion['persistent_model']=model;(O/'motion.json').write_text(json.dumps(motion,indent=2))
measured=O/'measured_paths_v3.json'
if measured.exists():
 data=json.loads(measured.read_text());assert data['layout']==ID
 for path,digest in data['path_hashes'].items():assert hashlib.sha256((H/path).read_bytes()).hexdigest()==digest,'Measured path changed: '+path
 schedule=json.loads((O/'schedule.json').read_text());schedule.update(data['schedule_fields']);(O/'schedule.json').write_text(json.dumps(schedule,indent=2))
arms=json.loads((O/'arm_reconsideration_v3.json').read_text());arms['selected_layout']=ID;arms['compared'][0]['evidence']=f'results/layouts/{ID}_envelope.json';(O/'arm_reconsideration_v3.json').write_text(json.dumps(arms,indent=2))
print('PREPARE COMPLETE',ID,flush=True)
