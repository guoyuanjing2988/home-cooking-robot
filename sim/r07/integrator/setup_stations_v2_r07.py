"""Rigidly relocate full-size fixtures/targets, with explicit storage and lid dock."""
import json,copy,hashlib,sys
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
H=Path(__file__).resolve().parent;O=H/'results';base=json.loads((O/'v1_process_v3.json').read_text())
def group(name):
 if name.startswith('raw_') or name.startswith('staged_raw_'):return 'raw'
 if name.startswith('peel_') or name=='clamped_food':return 'peel'
 if name.startswith('secondary_'):return 'secondary'
 if name.startswith('slicer_') or name.startswith('bfp610_'):return 'slicer'
 if name.startswith('root_brush_'):return 'wash'
 if name.startswith('dock_'):
  return next(('dock_'+t for t in ('peeler','wash_pad','eye_core_spoon') if name.startswith('dock_'+t)),None)
 if name.startswith('output_'):return 'output_'+name.split('_')[1] if not name.startswith('output_leafy') else 'output_leafy_greens'
 return None
def transform(frame,pos):return (Rotation.from_euler('z',frame['yaw_deg'],degrees=True).apply(np.array(pos)-frame['old_center'])+frame['new_center']).tolist()
for file in sorted(p for p in (O/'layouts').glob('L*.json') if len(p.stem)==3 and (len(sys.argv)<2 or p.stem==sys.argv[1])):
 cfg=json.loads(file.read_text());p=copy.deepcopy(base);id=cfg['id']
 variant=int(id[1:]);peel_x=.05 if variant in (1,2,3,7,8,9) or variant>=10 else -.935;secondary_x=-1.14 if peel_x>.0 else -1.27
 if variant>=13:secondary_x=-1.17
 frames={
 'raw':dict(old_center=[-1.63,.17,0],new_center=[-1.63,.40,0],yaw_deg=0),
 'peel':dict(old_center=[-.935,.17,0],new_center=[peel_x,.13 if variant>=12 else .17 if peel_x>.0 else .38,0],yaw_deg=0),
 'secondary':dict(old_center=[-1.27,.17,0],new_center=[secondary_x,.14 if variant>=12 else .25 if variant>=10 else .40,0],yaw_deg=180 if variant==5 else 0),
 'slicer':dict(old_center=[.425,.16,0],new_center=[.425,.15 if variant>=12 else .325 if variant>=10 else .40,0],yaw_deg=0),
 }
 for typ,oldx,x,y in [('peeler',-.55,.04,.315),('wash_pad',-.18,.16,.315),('eye_core_spoon',-.325,.04,.48)]:frames['dock_'+typ]=dict(old_center=[oldx,.11,0],new_center=[x,y,0],yaw_deg=0)
 for prod,x,oldy in [('carrot',-1.665,.435),('potato',-1.415,.435),('leafy_greens',-1.165,.435),('tomato',-.915,.405)]:frames['output_'+prod]=dict(old_center=[x,oldy,0],new_center=[x,.115,0],yaw_deg=0)
 if variant>=13:
  for prod,x,y in [('carrot',-1.69,.115),('potato',-1.445,.115),('leafy_greens',-.895,.44),('tomato',-.895,.115)]:frames['output_'+prod]['new_center']=[x,y,0]
 for name,change in cfg.get('station_overrides',{}).items():frames[name].update(change)
 if cfg.get('replacement_faucet'):
  fc=cfg['replacement_faucet']
  if fc.get('mount_type')=='wall':reference=fc['wash_reference_pos_m']
  else:
   yaw=np.radians(fc['yaw_deg']);outlet=np.array(fc['deck_xy_m'])+.227*np.array([np.cos(yaw),np.sin(yaw)]);reference=[*outlet,.996]
  frames['wash']=dict(old_center=[-.4,.405,1.032],new_center=reference,yaw_deg=0)
 else:frames['wash']=dict(old_center=[-.4,.405,1.032],new_center=[-.4,.405,1.032],yaw_deg=0)
 cfg.update(station_frames=frames,lid_storage=dict(center_m=[.65,.17,1.005],rotation_deg=[0,90,0],full_size_m=[.30,.27,.006]),helper_stage_R=cfg.get('helper_stage_override',[-.65,.10,1.24] if peel_x>.0 else [.20,.075,1.24]),reason=cfg['reason']+'; full rigid stations relocated, stopped removable secondary lid in vertical dock')
 for geom in p['installed_geometry']:
  g=group(geom['name'])
  if g:
   geom['pos']=transform(frames[g],geom['pos']);geom['r07_frame']=g;geom['r07_yaw_deg']=frames[g]['yaw_deg']
  if geom['name']=='secondary_drive_guard':geom['pos']=[secondary_x,.47,.70]
  if geom['name']=='presence_sensor':geom['pos']=[-.80,.57,cfg.get('presence_z',.96 if variant>=10 else 1.30)]
 p['installed_geometry']=[g for g in p['installed_geometry'] if not g['name'].startswith('slicer_')]
 if cfg.get('peel_horizontal_supports'):
  rods=sorted((g for g in p['installed_geometry'] if g['name'].startswith('peel_riser_')),key=lambda g:g['name'])
  pc=frames['peel']['new_center']
  for i,g in enumerate(rods):g.update(pos=[pc[0]+(-.12,-.04,.04,.12)[i],pc[1],.859],r07_rotation_override_deg=[90,0,0],r07_support_note='Unchanged180x18x18mm solid laid horizontally; not a reduced collision envelope.')
 p['installed_geometry'] +=[dict(name='bfp_receiving_bowl_land',type='box',pos=[.10,.115,.856],size=[.21,.21,.012]),dict(name='secondary_lid_storage_slot',type='box',pos=[.65,.17,.86],size=[.025,.29,.020])]
 for ph in p['phases']:
  for sg in ph['segments']:
   for pose in sg['poses']:
    for side,h in pose.items():
     st=sg['station'];g=None
     if st=='peel':g='peel'
     elif st=='raw':g='raw'
     elif st=='secondary' or sg['label']=='Withdraw for guarded eight-wedge cycle':g='secondary'
     elif st=='output':g='output_'+h['product']
     elif st=='slicer':g='slicer'
     elif st=='sink' and h['held']=='root_food':g='wash'
     elif st=='dock' and h['held'] in ('peeler','wash_pad','eye_core_spoon'):g='dock_'+h['held']
     if g:
      if sg['label']=='Clean, drain, return tools, water off' and g.startswith('dock_'):
       # The inherited cleanup poses retained the pre-R05 dock Y=.46.
       # Correct the datum before the same rigid fixture relocation.
       h['pos'][1]-=.35
      h['pos']=transform(frames[g],h['pos']);rot=Rotation.from_euler('z',frames[g]['yaw_deg'],degrees=True)
      for key in ('approach','jaw_axis'):
       if h.get(key) is not None:h[key]=rot.apply(h[key]).tolist()
      for key in ('nominal_forces_N','check_forces_N','nominal_moments_Nm','check_moments_Nm'):h[key]=[rot.apply(v).tolist() for v in h[key]]
      if g=='wash' and cfg.get('replacement_faucet'):
       for contact in h.get('contacts',[]):contact['reason']='Root and complete brush assembly translated beneath replacement faucet outlet; same sourced rub/jet force and explicit own working face.'
     if sg.get('action')=='helper_index' and side=='R':h['pos']=cfg['helper_stage_R']
     if variant>=11 and h['held']=='empty' and sg['station']=='sink':
      h.update(approach=[0,1,0],jaw_axis=[1,0,0])
      if variant>=13 and sg['label'] in ('water_on','water_off_final'):h['pos'][2]=.96
     if cfg.get('electric_water_standby') and sg['label'] in ('water_on','water_off_final'):
      h['pos']=list(cfg['electric_water_standby']);h['r07_note']='Electric NC valve command at one fixed empty-hand standby pose; no knob manipulation. Hydraulic command success is separately unverified.'
     if cfg.get('colander_wash_shift_m') and sg['station']=='sink' and h['held']=='colander':
      h['pos']=(np.array(h['pos'])+cfg['colander_wash_shift_m']).tolist()
   if cfg.get('inspection_standbys') and sg['label']=='Inspect four outputs and present bowls':
    for pi,pose in enumerate(sg['poses']):
     pose['R']['pos']=list(cfg['inspection_standbys'][pi]);pose['R']['r07_note']='Empty-hand visual inspection from clear front vantages aligned with relocated output area. No output transfer or quality credit without the persistent sequence.'
   if sg['label']=='bowl_load':
    sg['r07_task']='Prepare receiving output bowl for stopped batch unloading; no continuous discharge'
    for pi,pose in enumerate(sg['poses']):
     h=pose['R'];bx=frames['output_'+h['product']]['new_center'][0] if variant>=12 else .10
     face='output_'+h['product']+'_land' if variant>=12 else 'bfp_receiving_bowl_land'
     by=frames['output_'+h['product']]['new_center'][1] if variant>=12 else .115
     h.update(pos=[bx,by,1.067 if pi==0 else 1.042],approach=[0,0,-1],jaw_axis=[0,1,0],object_rotation_deg=[0,0,0],contacts=[])
     if pi==len(sg['poses'])-1:h['contacts']=[dict(face=face,held_parts=['bowl_outer_bottom'],reason='Own bowl prepared on its output land for stopped batch transfer',kind='grasp_release_support',object_id='bowl_'+h['product'],support_id=face)]
 p['r07_layout']=cfg;p['r07_geometry_scope']='Runtime starts with complete v1 geometry then applies these rigid frames; all sizes and OEM geometry retained. Secondary removable lid uses declared complete sheet and a vertical stopped-lid storage slot.'
 p['r07_finished_products_sha256']=hashlib.sha256(json.dumps(base['finished_products'],sort_keys=True).encode()).hexdigest()
 file.write_text(json.dumps(cfg,indent=2),encoding='utf-8');(O/'layouts'/f'{id}_process.json').write_text(json.dumps(p,indent=2),encoding='utf-8')
print('station transforms created for',len(list((O/'layouts').glob('L*_process.json'))),'layouts')
