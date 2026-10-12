"""Retain invalid-scope studies; create six fully closed-door motion layouts."""
import json,copy,time
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results'
record=dict(kind='discovered_model_scope_error',time_unix=time.time(),affected_layouts=list(range(74,84)),reason='Legacy cabinet_door_sweep_* boxes remained in operation despite exclusion of idle_full_sweep_cover_*; earlier regression omitted legacy family.',disposition='L74-L83 retained as historical overconstrained studies, not current corrected-scope evidence. Stopped affected active connection and return workers; all slot/resource records retained.',current_layouts=list(range(84,90)),geometry_policy='Remove only named swept-volume masks during operation. Retain full closed door leaves, sensors, cabinet bodies, robot, held objects and appliance solids. Idle adds full-sweep covers and retains 10mm all-robot check.')
(H/'audit/v6_door_scope_correction.json').write_text(json.dumps(record,indent=2))
for n in range(84,90):
 old='L'+str(n-10);ID='L'+str(n)
 c=json.loads((O/'layouts'/f'{old}.json').read_text());c.update(id=ID,orientation='R07_v6_'+ID,remove_legacy_motion_sweeps=True,reason='Complete closed-door scope correction; '+c['reason'],scope_fix_source=old)
 for suffix in ('','_process','_process_v4','_process_v6','_envelope','_park_full'):
  d=c if not suffix else json.loads((O/'layouts'/f'{old}{suffix}.json').read_text())
  if suffix in ('_envelope','_park_full'):d['config']=c
  if suffix=='_park_full':d.update(pass_=False,warm_start_only=True)
  f=O/'layouts'/f'{ID}{suffix}.json';assert not f.exists();f.write_text(json.dumps(d,indent=2))
print('CREATED L84-L89; prior scope error explicitly retained')
