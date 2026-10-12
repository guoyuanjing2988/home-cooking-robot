import os,sys,json
os.environ['R07_LAYOUT']=sys.argv[1]
import runtime_v6_r07 as v
import mujoco
from pathlib import Path
ID=v.ID;checks={};ch=v.scene(0);leaf=ch.gnames.index('r07_closed_door_0_0');finger=ch.gnames.index('R_finger_plus');arm=ch.gnames.index('R_geom_25');checks['normal_closed_leaf_finger5mm']=v.f.required(ch,leaf,finger)[0]==.005;checks['normal_closed_leaf_arm10mm']=v.f.required(ch,leaf,arm)[0]==.010
idle=json.loads((v.O/'layouts'/f'{ID}_idle.json').read_text());ch.xml=(v.H/idle['model_xml']).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));sweep=next(i for i,n in enumerate(ch.gnames) if n.startswith('idle_full_sweep_cover_'));finger=ch.gnames.index('R_finger_plus');checks['idle_sweep_finger10mm']=v.f.required(ch,sweep,finger)[0]==.010
checks['all_idle_robot_sweep_pairs10mm']=all(v.f.required(ch,a,b)[0]>=.010 for a,n in enumerate(ch.gnames) if n.startswith('idle_full_sweep_cover_') for b in range(len(ch.gnames)) if ch.robot[b])
ch.xml=(v.H/'models'/f'{ID}_fold_closed_doors.xml').read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));checks['motion_has_no_sweep_covers']=not any(n.startswith('idle_full_sweep_cover_') for n in ch.gnames);checks['motion_has_five_full_closed_leaves']=sum(n.startswith('r07_closed_door_') for n in ch.gnames)==5;checks['five_sensor_covers']=sum(n.startswith('door_pause_sensor_') for n in ch.gnames)==5
checks['motion_has_no_legacy_open_sweep_masks']=not any(n.startswith('cabinet_door_sweep_') for n in ch.gnames)
working=v.scene(0);checks['working_has_no_swept_volumes']=not any(n.startswith(('cabinet_door_sweep_','idle_full_sweep_cover_')) for n in working.gnames)
out=dict(layout=ID,pass_=all(checks.values()),checks=checks,source='DECISIONS.md 2026-10-09 Door-sweep scope');(v.O/'door_scope_regression_v6.json').write_text(json.dumps(out,indent=2));print(out);assert out['pass_']
