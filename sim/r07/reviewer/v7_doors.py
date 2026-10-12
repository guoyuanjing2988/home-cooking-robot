from v7_common import *
import hashlib,xml.etree.ElementTree as E
idle=read('idle.json');rows=[];files=set()
for group in ('task_fold','meal_end_return_diagnostic','explicit_unfold'):
 for r in idle[group]['attempts']:files.add(r['motion_model_xml'])
for group in ('front_fold','front_unfold','front_return','high_front_fold','high_front_unfold','high_front_return'):
 files.add(idle[group]['model_xml'])
for file in (I/'results/connections_v7'/v.ID).glob('*.json'):
 for l in json.loads(file.read_text())['legs']:files.add(l['model_xml'])
for file in sorted(files):
 root=E.fromstring((I/file).read_text());gs={g.get('name'):g for g in root.findall('.//geom') if g.get('name')};leaves=[(n,g) for n,g in gs.items() if n.startswith('r07_closed_door_')];cabs=[n for n in gs if n.startswith('upper_cabinet')];bad=[]
 expected=[]
 for ci,(lo,hi) in enumerate([(-1.8,-.7),(-.1,.69),(1.47,1.8)]):
  count=2 if hi-lo>.6 else 1;width=(hi-lo)/count
  for j in range(count):
   name=f'r07_closed_door_{ci}_{j}';g=gs[name];sign=1 if j==0 else -1;hinge=lo if j==0 else hi
   if not np.allclose(np.fromstring(g.get('size'),sep=' '),[width/2,.009,.3],rtol=0,atol=1e-10) or not np.allclose(np.fromstring(g.get('pos'),sep=' '),[hinge+sign*width/2,.221,1.65],rtol=0,atol=1e-10):bad.append(name)
 rows.append(dict(file=file,closed_leaves=len(leaves),cabinet_geoms=len(cabs),dimension_or_position_errors=bad,open_sweep_masks=[n for n in gs if n.startswith(('cabinet_door_sweep_','idle_full_sweep_cover_'))],sensor_covers=sum(n.startswith('door_pause_sensor_') for n in gs),helper_geoms=[n for n in gs if n.startswith('L_geom')]))
ch=v.scene(0);closed=ch.gnames.index('r07_closed_door_0_0');cab=next(i for i,n in enumerate(ch.gnames) if n.startswith('upper_cabinet'));finger=ch.gnames.index('R_finger_plus');arm=ch.gnames.index('R_geom_25')
gates=[dict(pair=[ch.gnames[a],ch.gnames[b]],required=f.required(ch,a,b)) for a in (closed,cab) for b in (finger,arm)]
# Force an overlap in a disposable compiled scene and run the complete contacts policy.
q=ch.m.qpos0.copy();ch.set_contacts({});ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d);ch.m.geom_pos[closed]=ch.d.geom_xpos[arm].copy();mujoco.mj_forward(ch.m,ch.d);hits=f.contacts(ch,q)[0];injected=[x for x in hits if set(x['pair'])=={ch.gnames[closed],ch.gnames[arm]}]
# Independently check the parked support boxes and all-robot sweep thresholds without rewriting the submitted policy.
ch=v.scene(0);ch.xml=(I/idle['model_xml']).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));sweeps=[i for i,n in enumerate(ch.gnames) if n.startswith('idle_full_sweep_cover_')];badgates=[]
for a in sweeps:
 for b in np.flatnonzero(ch.robot):
  if f.required(ch,a,b)[0]<.010:badgates.append([ch.gnames[a],ch.gnames[b]])
dump('door_scope.json',dict(saved_motion_models=len(rows),models=rows,all_corrected_scope=all(x['closed_leaves']==5 and x['cabinet_geoms']>=3 and not x['dimension_or_position_errors'] and not x['open_sweep_masks'] and x['sensor_covers']==5 and not x['helper_geoms'] for x in rows),ordinary_closed_door_cabinet_gates=gates,closed_door_collision_probe_rejected=bool(injected),collision_probe=injected,idle_sweep_count=len(sweeps),idle_bad_robot_gates=badgates,doors_against_corridor=False))
print('DOOR_SCOPE',len(rows),'probe',bool(injected),'badgates',len(badgates))

