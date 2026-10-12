from pathlib import Path
H=Path(__file__).resolve().parent
p=H/'fold_v7_r07.py';s=p.read_text();s=s.replace('import os,sys,json,time,math,hashlib','import os,sys,json,time,math,hashlib,xml.etree.ElementTree as E')
s=s.replace('ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.hands={}',"""root=E.fromstring(ch.xml);world=root.find('worldbody')
for g in list(world.findall('geom')):
 if g.get('name','').startswith('idle_full_sweep_cover_'):world.remove(g)
ch.xml=E.tostring(root,encoding='unicode');motion_model=f'models/{ID}_fold_closed_doors.xml';(H/motion_model).write_text(ch.xml);ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.hands={}""")
s=s.replace("model_xml=idle['model_xml']","model_xml=motion_model").replace('all_robot_door_gap_mm=10','idle_all_robot_sweep_gap_mm=10,motion_door_scope="closed leaves and cabinet bodies; no sweep covers"')
p.write_text(s)
p=H/'static_v7_r07.py';s=p.read_text();s=s.replace("([('L71',index)] if int(v.ID[1:])>=73 else [])","([('L73',index)] if int(v.ID[1:])>=74 else [])+([('L71',index)] if int(v.ID[1:])>=73 else [])").replace("'static_v7' if donor_id in ('L59','L71')","'static_v5' if donor_id in ('L59','L71','L73')")
p.write_text(s)
