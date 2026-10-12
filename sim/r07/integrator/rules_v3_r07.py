import os,sys,json,copy,xml.etree.ElementTree as E,runpy,hashlib
os.environ['R07_LAYOUT']=sys.argv[1]
import runtime_v2_r07 as v
import numpy as np,mujoco
from distance import Bounds
rows=[]
for gap in (.005,.0075,.009,.0099,.010,.0101):
 ch=v.scene(104);root=E.fromstring(ch.xml);w=root.find('worldbody')
 rb=E.SubElement(w.find(".//body[@name='rail_structure']"),'body',name='R_door_probe_finger_body',pos='3 0 1')
 v.s.model.box(rb,'R_door_probe_finger',[0,0,0],[.04,.04,.04],robot=True)
 v.s.model.box(w,'idle_full_sweep_cover_probe',[3+.04+gap,0,1],[.04,.04,.04],robot=False)
 ch.xml=E.tostring(root,encoding='unicode');ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));q=ch.m.qpos0.copy();ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False
 ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d);a=ch.gnames.index('R_door_probe_finger');b=ch.gnames.index('idle_full_sweep_cover_probe');required=v.f.required(ch,a,b);actual=mujoco.mj_geomDistance(ch.m,ch.d,a,b,.1,None)
 bounds=Bounds(ch,v.f.required);pairs=[p for p in bounds.pairs if {p[0],p[1]}=={a,b}];assert len(pairs)==1 and pairs[0][2]==.01
 hits,_,_=bounds.check();rejected=any(set(h['pair'])=={'R_door_probe_finger','idle_full_sweep_cover_probe'} for h in hits)
 row=dict(gap_mm=actual*1000,gate_mm=required[0]*1000,category=required[1],gripper_classified=bool(ch.gripper(a)),rejected=rejected,expected_reject=gap<.01,pass_=rejected==(gap<.01));assert row['gripper_classified'];rows.append(row)
assert all(r['pass_'] for r in rows)
(v.O/'door_gate_regression_v3.json').write_text(json.dumps(dict(layout=v.ID,pass_=True,rows=rows,scope='Native distance and actual Bounds.check rejection probes, including robot finger geometry at5-10mm. Entire idle sweep takes10mm; ordinary held/environment remains5mm.'),indent=2))
runpy.run_path(str(v.H/'rules_r07.py'))
contacts=[]
for i,(ph,sg,key) in enumerate(v.items):
 for pi,hands in enumerate(sg['poses']):
  for side,h in hands.items():
   for c in h.get('contacts',[]):contacts.append(dict(stroke_index=i,stroke=key,pose=pi,side=side,**c))
out=dict(schema='r07.v3.exact-active-contact-ledger',layout=v.ID,source_process=f'results/layouts/{v.ID}_process.json',process_sha256=hashlib.sha256(json.dumps(v.P,sort_keys=True).encode()).hexdigest(),contacts=contacts)
assert not any(c['face']=='slicer_bowl_land' for c in contacts)
(v.O/'intended_contacts.json').write_text(json.dumps(out,indent=2));print('10mm door gate and active contact ledger PASS',len(contacts))
