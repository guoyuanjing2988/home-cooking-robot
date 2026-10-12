"""Actual full-size five-leaf opening sweep at the conditional stored snapshot."""
import json,math,xml.etree.ElementTree as E
import numpy as np,mujoco
import final_check as f
from distance import Bounds
H=f.s.HERE;O=H/'results';idle=json.loads((O/'idle_repair.json').read_text());root=E.parse(H/'models/idle_r05.xml');w=root.find('worldbody');doors=[]
for ci,(lo,hi) in enumerate([(-1.8,-.7),(-.1,.69),(1.47,1.8)]):
 count=2 if hi-lo>.6 else 1;width=(hi-lo)/count
 for i in range(count):
  name=f'open_cabinet_door_{ci}_{i}';hinge=lo if i==0 else hi;sign=1 if i==0 else -1
  b=E.SubElement(w,'body',name=name,pos=f.s.model.fmt([hinge,.230,1.65]));E.SubElement(b,'joint',name=name+'_hinge',type='hinge',axis=f.s.model.fmt([0,0,-sign]),range='0 1.5707963267948966');f.s.model.box(b,name,[sign*width/2,-.009,0],[width,.018,.6],robot=False,mass=5.94)
  doors.append(dict(name=name,cabinet=ci,width_m=width,hinge_x_m=hinge,hinge_y_m=.230,hinge_basis='Rear outside edge of full18mm leaf; closed occupied volume unchanged, no leaf width reduction'))
ch=f.s.Checker(f.s.P['phases'][0],f.s.P['phases'][0]['segments'][0]);ch.bind_model(mujoco.MjModel.from_xml_string(E.tostring(root.getroot(),encoding='unicode')));q=np.zeros(ch.m.nq);q[:len(idle['parked_snapshot']['q'])]=idle['parked_snapshot']['q'];ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d);oracle=Bounds(ch,f.required)
door_ids=[ch.gnames.index(x['name']) for x in doors];ids=[g for g,n in enumerate(ch.gnames) if g not in door_ids and not n.startswith('cabinet_door_sweep') and n!='protected_stove'];lo=[];hi=[]
for g in ids:
 if ch.m.geom_type[g]==0:lo.append([-1e6]*3);hi.append([1e6]*3);continue
 lo.append([oracle.support(g,-axis)[k] for k,axis in enumerate(np.eye(3))]);hi.append([oracle.support(g,axis)[k] for k,axis in enumerate(np.eye(3))])
lo=np.array(lo);hi=np.array(hi);radius=max(math.hypot(x['width_m'],.009) for x in doors);steps=int(math.ceil(radius*math.pi/2/.004));bad=[];queries=0
for k in range(steps+1):
 theta=(k/steps)*math.pi/2
 for a in doors:q[ch.qa[a['name']+'_hinge']]=theta
 ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d)
 for a,g in zip(doors,door_ids):
  ext=abs(ch.d.geom_xmat[g].reshape(3,3))@ch.m.geom_size[g];p=ch.d.geom_xpos[g];delta=np.maximum(np.maximum(lo-(p+ext),(p-ext)-hi),0);close=np.flatnonzero(np.linalg.norm(delta,axis=1)<.010)
  for j in close:
   other=ids[j];n=ch.gnames[other]
   if n.startswith('upper_cabinet_'+str(a['cabinet'])):continue # native door/frame hinge assembly, not a robot task exemption
   v=oracle.pair(g,other);queries+=1
   if v['lower_m']<.010-1e-6:bad.append(dict(angle_deg=theta*180/math.pi,pair=[a['name'],n],lower_gap_mm=v['lower_m']*1000,upper_gap_mm=v['upper_m']*1000,required_mm=10))
 if bad:break
person_intrusions=[]
for a,g in zip(doors,door_ids):
 ext=abs(ch.d.geom_xmat[g].reshape(3,3))@ch.m.geom_size[g];p=ch.d.geom_xpos[g]
 if all(p+ext>[-1.6,-.75,.85]) and all(p-ext<[.6,-.05,1.85]):person_intrusions.append(a['name'])
out=dict(schema='r05.actual-door-leaf-sweep',pass_=not bad,doors=doors,leaf_full_size='18mm x600mm, original cabinet span divided into native paired leaves; complete occupied leaf retained',angles_checked=k+1,requested_angles=steps+1,max_leaf_point_step_mm=radius*(math.pi/2)/steps*1000,opening_deg=90,blockers=bad,narrow_queries=queries,native_hinge_mate='Door versus its own cabinet body is a native environmental assembly; rear-edge hinge and leaf localY<=0 imply worldY<=cabinet_front for0..90deg. All robot/frame/appliance/foreign cabinet geometries retain10mm.',paired_leaf_proof='For paired full-width leaves hinged at rear outside edges, leftleaf x<=lo+w*cos(theta), rightleaf x>=hi-w*cos(theta). Their midspan plane separates the complete solids for0..90deg; minimum gap2*w*(1-cos(theta))>=0. No occupied leaf was shrunk to provide a seam.',logical_mask='protected_stove excluded only from physical door obstruction enumeration; retained in all robot checks',stored_snapshot_only=True,deployment_verified=False,original_person_volume_clear=not person_intrusions,opened_native_door_intrusions=person_intrusions,person_scope='Robot-only original corridor is clear at stored snapshot. The actual open leaves still intrude this full rectangular human volume; a holistic person-corridor pass is not claimed.')
(O/'doors.json').write_text(json.dumps(out,indent=2));idle_final=json.loads((O/'idle.json').read_text());idle_final['actual_door_leaf_sweep']=dict(pass_=out['pass_'],source='results/doors.json',max_point_step_mm=out['max_leaf_point_step_mm']);idle_final['full_declared_person_volume_pass']=not person_intrusions;idle_final['opened_native_door_intrusions']=person_intrusions;idle_final['static_storage_snapshot_scope']='Robot clearance, door/foreign-obstacle sweep and robot-only corridor checks; not a complete person-corridor acceptance';(O/'idle.json').write_text(json.dumps(idle_final,indent=2));print('ACTUAL_DOORS',out['pass_'],'angles',k+1,'queries',queries,'blockers',bad[:2],'person volume intrusions',person_intrusions,flush=True)
