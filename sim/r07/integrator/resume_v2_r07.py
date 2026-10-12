"""Preserve v1 evidence before any new engineering iteration."""
import json,shutil,time
from pathlib import Path
H=Path(__file__).resolve().parent;root=H.parents[2];archive=H/'history/v1'
if not archive.exists():
 archive.mkdir(parents=True)
 for folder in ('results','renders','audit'):
  shutil.copytree(H/folder,archive/folder)
 for file in ('r07_model.py','r07_runtime.py','r07_ik.py','static_r07.py'):
  shutil.copy2(H/file,archive/file)
 for file in ('config.json','process_v3.json','torque_envelope.json','parking_probe.json'):
  shutil.copy2(H/'results'/file,H/'results'/('v1_'+file))
 old=root/'posts/r07/integrator.md';dest=root/'posts/r07/integrator_v1.md'
 if not dest.exists():shutil.copy2(old,dest)
out=H/'results/layouts';out.mkdir(exist_ok=True)
base=json.loads((H/'results/config.json').read_text())
choices=[
 dict(id='L01',height=1.193687,helper_height=1.212596,front_mount_y=.403386,helper_y=.427,mount_deg=149.236,helper_mount_deg=155.143,rail_centres_z=[1.15,1.235],lane_count=2,reason='Reproduce v1 geometry at full search budget; baseline map'),
 dict(id='L02',height=1.19,helper_height=1.19,front_mount_y=.335,helper_y=.335,mount_deg=155.,helper_mount_deg=155.,rail_centres_z=[1.305,1.305],lane_count=1,reason='Single high wall lane, bases forward of faucet, original chain band'),
 dict(id='L03',height=1.24,helper_height=1.22,front_mount_y=.345,helper_y=.345,mount_deg=180.,helper_mount_deg=180.,rail_centres_z=[1.305,1.22],lane_count=2,chain_centres_z=[1.2875,1.3225],reason='Inverted mounts, high principal rail, compact front stand-off'),
 dict(id='L04',height=1.27,helper_height=1.20,front_mount_y=.455,helper_y=.455,mount_deg=210.,helper_mount_deg=210.,rail_centres_z=[1.305,1.215],lane_count=2,chain_centres_z=[1.2875,1.3225],reason='Rear stand-off and opposite mount tilt, vary principal height'),
 dict(id='L05',height=1.19,helper_height=1.19,front_mount_y=.38,helper_y=.38,mount_deg=210.,helper_mount_deg=210.,rail_centres_z=[1.305,1.305],lane_count=1,reason='Single high lane with outward-opening tilted mounts'),
 dict(id='L06',height=1.13,helper_height=1.20,front_mount_y=.445,helper_y=.355,mount_deg=235.,helper_mount_deg=165.,rail_centres_z=[1.305,1.215],lane_count=2,reason='Low principal pivot and asymmetric helper tilt/stand-off'),
]
for choice in choices:
 path=out/(choice['id']+'.json')
 if path.exists():continue
 cfg=dict(base,**choice);cfg['orientation']='R07_v2_'+choice['id'];path.write_text(json.dumps(cfg,indent=2))
(H/'audit/resume_v2.json').write_text(json.dumps(dict(date='2026-10-08',reason='Orchestrator rejects v1 budget/iteration coverage; new reachability-first layout study and >=96 starts per stroke with >=20s available per unresolved start.',layouts=[c['id'] for c in choices],v1_post='posts/r07/integrator_v1.md'),indent=2))
print('v1 preserved; six parameterized layout candidates created')
