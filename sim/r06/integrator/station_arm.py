"""OEM xArm6 model, public payload-chart union and rated-envelope comparison."""
from station_cell import *
from scipy.optimize import differential_evolution
vendor=V3/'vendor';src=E.parse(vendor/'xarm6_oem.urdf').getroot()
for mesh in src.findall('.//mesh'):mesh.set('filename',str((vendor/'xarm_assets'/Path(mesh.get('filename')).name).resolve()))
aux=E.SubElement(src,'mujoco');E.SubElement(aux,'compiler',discardvisual='true',fusestatic='false',balanceinertia='true',meshdir=str((vendor/'xarm_assets').resolve()))
model=mujoco.MjModel.from_xml_string(E.tostring(src,encoding='unicode'));mujoco.mj_saveLastXML(str(V3/'models/xarm6_converted.xml'),model)
root=E.parse(V3/'models/xarm6_converted.xml').getroot();world=root.find('worldbody');children=list(world);mount=body(world,'candidate_mount',[0,.70,1.30]);mount.set('quat',quat(Rotation.from_euler('x',90,degrees=True)))
for child in children:world.remove(child);mount.append(child)
link=root.find(".//body[@name='link6']");E.SubElement(link,'site',name='candidate_flange',pos='0 0 0',size='.005')
text=E.tostring(root,encoding='unicode');(V3/'models/xarm6_side_mount.xml').write_text(text);m=mujoco.MjModel.from_xml_string(text);d=mujoco.MjData(m)
names=['joint'+str(i) for i in range(1,7)];ids=[m.joint(n).id for n in names];qa=[int(m.jnt_qposadr[j]) for j in ids];da=[int(m.jnt_dofadr[j]) for j in ids];limits=[m.jnt_range[j].tolist() for j in ids];sid=m.site('candidate_flange').id;jp=np.zeros((3,m.nv));jr=np.zeros_like(jp)
# Exact documented rectangular radial/axial bounds, no interpolation invented.
chart=[(5,.030,.015),(3,.100,.090),(2,.200,.180)]
def evaluate(x):
 d.qpos[qa]=x;mujoco.mj_forward(m,d);mujoco.mj_jacSite(m,d,jp,jr,sid);rot=d.site_xmat[sid].reshape(3,3);vals=[]
 for mass,r,z in chart:
  f=mass*9.81;tau=d.qfrc_bias[da]+f*jp[2,da];coef=np.array([f*np.cross(jr[:,da].T,rot[:,i])[...,2] for i in range(3)]).T
  vals.append(np.maximum(abs(tau),abs(tau+z*coef[:,2]))+r*np.linalg.norm(coef[:,:2],axis=1))
 return np.max(vals,axis=0)
caps={};witness={};beg=time.monotonic()
for i,n in enumerate(names):
 candidates=[differential_evolution(lambda x:-evaluate(x)[i],limits,popsize=8,maxiter=55,tol=1e-7,seed=1800+k,polish=True,workers=1) for k in range(3)]
 best=min(candidates,key=lambda r:r.fun);caps[n]=float(-best.fun);witness[n]=dict(q=best.x.tolist(),capacity_Nm=float(-best.fun),restarts=3,evaluations=sum(r.nfev for r in candidates));print(n,caps[n],flush=True)
# Compute flange CoM of the ACTUAL pan + full1.2kg EOAT with existing load adapter.
rows=[]
for product in PRODUCTS:
 cell=StationCell(32,'output_'+product);q=cell.q0.copy();cell.pose(q);flange=cell.m.site('R_attachment_site').id;fp=cell.d.site_xpos[flange];fr=cell.d.site_xmat[flange].reshape(3,3);rootid=cell.m.body('R_tool').id;parts=[]
 for b in range(cell.m.nbody):
  parent=b
  while parent and parent!=rootid:parent=int(cell.m.body_parentid[parent])
  if parent==rootid:parts.append((float(cell.m.body_mass[b]),fr.T@(cell.d.xipos[b]-fp)))
 toolids=[cell.m.body(n).id for n in ('R_tool','R_jaw_minus','R_jaw_plus')];tm=sum(cell.m.body_mass[b] for b in toolids);tc=sum(cell.m.body_mass[b]*(fr.T@(cell.d.xipos[b]-fp)) for b in toolids)/tm
 heldmass=payload(cell,[0,0,0])['R']['held_kg'];hc=np.array([0,0,.09])+PREP_LOCAL.apply(cell.com);actual_mass=tm+heldmass;com=(heldmass*hc+tm*tc)/actual_mass;challenge=(tm*tc+3*hc)/(tm+3)
 def allowed(mass,xyz):return any(mass<=cap+1e-9 and np.linalg.norm(xyz[:2])<=r+1e-9 and 0<=xyz[2]<=z+1e-9 for cap,r,z in chart)
 rows.append(dict(product=product,actual_flange_mass_kg=actual_mass,actual_CoM_flange_m=com.tolist(),actual_payload_chart_pass=allowed(actual_mass,com),challenge_mass_kg=tm+3,challenge_CoM_flange_m=challenge.tolist(),challenge_payload_chart_pass=allowed(tm+3,challenge)))
write('v3/arm_evaluation.json',dict(arm='UFACTORY xArm6 OEM uf-gym model',mount={'position_m':[0,.70,1.30],'Rx_deg':90},public_chart_kg_Lxy_Lz_m=chart,rated_envelope_Nm=caps,witnesses=witness,loads=rows,accepted=False,reason='Existing long-offset pan key cannot satisfy public xArm6 payload chart, especially4.2kg external3kg challenge; no invented payload interpolation or substitution of UR5e limits',brakes='OEM manualp17 states pose holding on power outage;p94 documents wall mounting; home-tier evidence accepted, not a blocker',brake_url='https://www.ufactory.cc/wp-content/uploads/2023/05/xArm-User-Manual-V2.0.0.pdf',chart_page=237,model_url='https://github.com/xArm-Developer/uf-gym/blob/master/urdf/xarm/xarm6_robot_white.urdf',model_sha256=hashlib.sha256((vendor/'xarm6_oem.urdf').read_bytes()).hexdigest(),elapsed_s=time.monotonic()-beg,pricing='CNY45000 arm/controller allowance for comparison, not a supplier quote; not selected'))
data=json.loads((V3/'arm_evaluation.json').read_text());audit=[]
for link in src.findall('link'):
 inertial=link.find('inertial')
 if inertial is None:continue
 name=link.get('name');bid=model.body(name).id;mass=float(inertial.find('mass').get('value'));center=np.fromstring(inertial.find('origin').get('xyz','0 0 0'),sep=' ');ii=inertial.find('inertia');matrix=np.array([[float(ii.get('ixx')),float(ii.get('ixy')),float(ii.get('ixz'))],[float(ii.get('ixy')),float(ii.get('iyy')),float(ii.get('iyz'))],[float(ii.get('ixz')),float(ii.get('iyz')),float(ii.get('izz'))]]);eigen=np.linalg.eigvalsh(matrix)
 audit.append(dict(link=name,source_mass_kg=mass,compiled_mass_kg=float(model.body_mass[bid]),source_CoM_m=center.tolist(),compiled_CoM_m=model.body_ipos[bid].tolist(),mass_CoM_preserved=abs(mass-model.body_mass[bid])<1e-9 and np.linalg.norm(center-model.body_ipos[bid])<1e-9,source_inertia_eigenvalues=eigen.tolist(),triangle_inequality_violation=bool(eigen[-1]>sum(eigen[:-1])+1e-12)))
data.update(latest_chart_url='https://www.ufactory.cc/wp-content/uploads/2024/01/xArm-User-Manual-V2.3.0.pdf',latest_chart_pdf_page=193,latest_chart_same_bounds=True,conversion=dict(balanceinertia=True,reason='OEM link2 rotational inertia violates triangle inequality. Compilation balances only rotational inertia; mass/CoM and original URDF unchanged.',scope='Zero-velocity gravity envelope only, not a dynamically qualified xArm model',mass_CoM_audit=audit),selected_scene_variant=32,IK_or_paths_attempted=False)
write('v3/arm_evaluation.json',data)
