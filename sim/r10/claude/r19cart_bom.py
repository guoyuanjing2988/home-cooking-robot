"""R19 cart (issue #14): component list (BOM) with sourced / derived / estimated masses, mass, CoG and
inertia of the R10 docked cart, the comparison with the sim's boxes (scene.build dock + deep_cart +
cantilever + verified_wheels, preset SD), and the model patch used by r19cart_dyn.py.

Labels: S = sourced (URL in SRC), D = derived from sourced numbers or from the sim geometry by stated
arithmetic (steel 7850 / aluminium 2700 kg/m3), E = engineering estimate (no source), M = read from the
compiled sim model.
Cart frame = the sim's `rail_structure` body: origin on the floor under the cart reference point, x along
the counter, y towards the cabinets (docked at world y = -0.21, bumper face at local y = +0.21), z up.
python r19cart_bom.py [MAST=steel|al]  -> results/r19/cart/bom.json (+ printed table)
Nothing here changes any existing file: patch() edits an in-memory MjModel copy."""
import sys,os,json,copy;sys.path.insert(0,'.')
import numpy as np
OUT='results/r19/cart'
SRC=dict(
 UR_DATASHEET='https://www.universal-robots.com/manuals/latest/en/datasheets/ur5e/ (weight 20.6 kg, payload 5 kg, reach 850 mm)',
 UR_DH='https://www.universal-robots.com/articles/ur/application-installation/dh-parameters-for-calculations-of-kinematics-and-dynamics/ (UR5e link masses and CoMs)',
 UR_MANUAL='https://www.universal-robots.com/manuals/EN/PDF/SW5_19/user-manual-UR5e-PDF_online/710-965-00_UR5e_User_Manual_en_Global.pdf (2.3 stopping data p.19-24; 6.2 stand loads p.41-42; 10.2.2 stop categories)',
 WHEEL='https://www.zlingkj.com/Data/zlingkj/upload/file/20240102/ZLLG65ASM500%20V2.0%E5%8D%95%E5%87%BA%E8%BD%B4.pdf (ZLLG65ASM500 V2.0: 165 mm, 48 V, 10 N.m rated / 30 N.m peak, 4.85 kg, 200 kg per 2 sets, PU 70 Shore A)',
 GRIP='https://www.dh-robotics.com/wp-content/uploads/2022/03/DH-Robotics-Servo-Electric-Grippers-Product-Gallery-202203D.pdf (PGC-140-50 ~1 kg, as recorded in hardware.py)')
STEEL,AL=7850.,2700.
def rhs(b,h,t,rho):return (b*h-(b-2*t)*(h-2*t))*rho   # kg/m of a rectangular hollow section
MAST=os.environ.get('MAST','steel')
def items(mast=None,chassis_scale=1.):
 """(name, qty, unit kg, COM in the cart frame, box size for the inertia (None = point), label, note)."""
 mast=mast or MAST
 mm=rhs(.1,.1,.004,STEEL if mast=='steel' else AL)*.865
 L=[
  ('chassis frame RHS 40x40x2 steel, 3.2 m',1,rhs(.04,.04,.002,STEEL)*3.2*chassis_scale,(0,-.05,.11),(.60,.50,.04),'D','perimeter 0.60x0.50 + 2 cross members; 2.39 kg/m'),
  ('deck plate Al 5 mm 0.60x0.50',1,.6*.5*.005*AL*chassis_scale,(0,-.05,.1325),(.60,.50,.005),'D',''),
  ('wheel / caster brackets, mast foot gussets',1,2.0*chassis_scale,(0,-.12,.13),(.5,.3,.05),'E',''),
  (f'mast RHS 100x100x4 {mast}, 0.865 m (z .19-1.055)',1,mm,(0,-.17,.6225),(.10,.10,.865),'D','%.2f kg/m'%rhs(.1,.1,.004,STEEL if mast=='steel' else AL)),
  ('beam RHS 100x50x4 steel, 0.30 m (mast -> mount)',1,rhs(.1,.05,.004,STEEL)*.30,(0,-.045,1.08),(.09,.30,.05),'D','8.92 kg/m'),
  ('mast-beam joint plates + bolts',1,.8,(0,-.17,1.08),None,'E',''),
  ('UR adapter, 20 deg wedge, Al, pocketed',1,2.0,(0,.08,1.10),(.17,.17,.04),'E','solid wedge 170x170x(10..72) mm would be 3.2 kg'),
  ('drive hub motor ZLTECH ZLLG65ASM500 V2.0',2,4.85,[(-.22,-.22,.0825),(.22,-.22,.0825)],(.167,.089,.167),'S','WHEEL'),
  ('swivel caster 100 mm PU with total lock',2,.9,[(-.22,.11,.06),(.22,.11,.06)],None,'E','catalogue class 0.7-1.2 kg'),
  ('drive driver ZLAC8015D',1,.8,(0,-.10,.21),None,'E','datasheet mass not captured'),
  ('48 V DC supply 600 W (230 V tether in)',1,1.5,(.10,-.10,.22),None,'E',''),
  ('safety relay, contactor, terminals, enclosure, wiring',1,1.9,(-.05,-.10,.22),(.30,.12,.07),'E',''),
  ('dock bumper, rubber D-profile + Al backing 0.56 m',1,1.0,(0,.205,.30),(.56,.02,.10),'E',''),
  ('covers: chassis skirt',1,1.5,(0,-.05,.20),(.62,.52,.20),'E',''),
  ('covers: mast',1,1.0,(0,-.17,.62),(.12,.12,.86),'E',''),
  ('E-stop button + box on mast',1,.3,(0,-.23,1.0),None,'E',''),
  ('UR arm cable on the cart (1.5 m x 0.35 kg/m)',1,.5,(0,-.20,.60),None,'E',''),
  ('tether inlet, strain relief, connector',1,.4,(0,.15,.10),None,'E',''),
  ('fasteners, misc',1,1.0,(0,-.10,.30),None,'E',''),
  ('dock pads / fiducials',1,.3,(0,.20,.20),None,'E','')]
 return L
# UR5e (UR_DH, sourced): link masses and CoMs in the DH frames; base = datasheet total - links (D)
UR_A=[0,-.425,-.3922,0,0,0];UR_D=[.1625,0,0,.1333,.0997,.0996];UR_AL=[np.pi/2,0,0,np.pi/2,-np.pi/2,0]
UR_M=[3.761,8.058,2.846,1.37,1.3,.365];UR_C=[[0,-.02561,.00193],[.2125,0,.11336],[.15,0,.0265],[0,-.0018,.01634],[0,.0018,.01634],[0,0,-.001159]]
UR_TOTAL=20.6;UR_BASE=UR_TOTAL-sum(UR_M)
UR_BODIES=['R_arm_shoulder_link','R_arm_upper_arm_link','R_arm_forearm_link','R_arm_wrist_1_link','R_arm_wrist_2_link','R_arm_wrist_3_link']
TOOL=dict(gripper=(1.0,'S','GRIP'),fingers=(.2,'E',''),flange_adapter=(.15,'E',''))   # R_tool: the sim has 1.0 + 2 jaws x 0.1
def dh_frames(q):
 T=np.eye(4);out=[]
 for i in range(6):
  c,s=np.cos(q[i]),np.sin(q[i]);ca,sa=np.cos(UR_AL[i]),np.sin(UR_AL[i])
  T=T@np.array([[c,-s*ca,s*sa,UR_A[i]*c],[s,c*ca,-c*sa,UR_A[i]*s],[0,sa,ca,UR_D[i]],[0,0,0,1]]);out.append(T.copy())
 return out
def box_inertia(m,s):
 if s is None:return np.zeros((3,3))
 a,b,c=s;return m/12*np.diag([b*b+c*c,a*a+c*c,a*a+b*b])
def summarize(L):
 rows=[];M=0.;S1=np.zeros(3)
 for n,k,u,p,s,lab,note in L:
  ps=p if isinstance(p,list) else [p]*k
  for pp in ps:M+=u;S1+=u*np.array(pp,float)
  rows.append(dict(item=n,qty=k,unit_kg=round(u,3),total_kg=round(u*k,3),com_m=p,label=lab,note=note))
 c=S1/M;I=np.zeros((3,3))
 for n,k,u,p,s,lab,note in L:
  for pp in (p if isinstance(p,list) else [p]*k):
   r=np.array(pp,float)-c;I+=box_inertia(u,s)+u*(r@r*np.eye(3)-np.outer(r,r))
 return rows,M,c,I
def sim_parts():
 """The sim's cart boxes (scene.build with the SD preset: dock, deep_cart, cantilever, verified_wheels)."""
 return [('R_cart_chassis',14.,(0,-.05,.14)),('R_cart_electrics',3.,(0,-.10,.225)),('R_cart_mast',4.,(0,-.17,.6225)),('R_cart_beam',2.5,(0,-.045,1.08)),
  ('R_dock_bumper',.5,(0,.205,.30)),('R_cart_wheel_drive x2 (4.85 each)',9.7,(0,-.22,.0825)),('R_cart_wheel_caster x2 (verified_wheels sets 4.85 each, dock code says 1.5)',9.7,(0,.11,.05)),
  ('R_mount (base plate + cover)',1.13,(0,.08,1.108))]
# ------------------------------------------------------------------ model patch
def _set_inertial(m,b,mass,com,I):
 import mujoco
 w,V=np.linalg.eigh(I)
 if np.linalg.det(V)<0:V[:,0]*=-1
 qt=np.zeros(4);mujoco.mju_mat2Quat(qt,V.flatten());m.body_mass[b]=mass;m.body_ipos[b]=com;m.body_iquat[b]=qt;m.body_inertia[b]=np.maximum(w,1e-7)
def body_I(m,b):
 import mujoco
 R=np.zeros(9);mujoco.mju_quat2Mat(R,m.body_iquat[b]);R=R.reshape(3,3);return m.body_mass[b],m.body_ipos[b].copy(),R@np.diag(m.body_inertia[b])@R.T
def combine(parts):
 M=sum(p[0] for p in parts);c=sum(p[0]*np.asarray(p[1]) for p in parts)/M;I=np.zeros((3,3))
 for mm,cc,II in parts:r=np.asarray(cc)-c;I+=II+mm*(r@r*np.eye(3)-np.outer(r,r))
 return M,c,I
def ur_map(m,d):
 """Constant transform DH frame i -> MuJoCo body i (the menagerie base frame is the DH base frame turned 180 deg
 about z; checked: flange positions agree within ~1 mm, the menagerie's UR5 link offsets)."""
 import mujoco
 bid=m.body('R_arm_base').id;q=m.qpos0.copy();q[:3]=[0,-.21,0];out=[];rng=np.random.default_rng(3);err=0.
 Rz=np.diag([-1.,-1,1])
 for trial in range(3):
  q[3:9]=rng.uniform(-2.5,2.5,6) if trial else 0.;d.qpos[:]=q;mujoco.mj_kinematics(m,d)
  Tb=np.eye(4);Tb[:3,:3]=d.xmat[bid].reshape(3,3);Tb[:3,3]=d.xpos[bid];Tb[:3,:3]=Tb[:3,:3]@Rz
  F=dh_frames(q[3:9]);rel=[]
  for i,n in enumerate(UR_BODIES):
   b=m.body(n).id;Tw=np.eye(4);Tw[:3,:3]=d.xmat[b].reshape(3,3);Tw[:3,3]=d.xpos[b];rel.append(np.linalg.inv(Tw)@Tb@F[i])
  if trial==0:out=rel
  else:err=max(err,max(float(np.linalg.norm((r1@np.r_[UR_C[i],1])[:3]-(r0@np.r_[UR_C[i],1])[:3])) for i,(r0,r1) in enumerate(zip(out,rel))))
 return out,err
def patch(m,d,variant='bom',mast=None,chassis_scale=1.):
 """In-memory: cart (rail_structure + R_mount) from the BOM, UR5e links from the UR DH table, tool from TOOL.
 variant 'sim' leaves the model as built. Returns a description."""
 import mujoco
 if variant=='sim':return dict(variant='sim')
 rid=m.body('rail_structure').id;mid=m.body('R_mount').id
 L=items(mast,chassis_scale);rows,M,c,I=summarize(L)
 _set_inertial(m,rid,M,c,I)   # the adapter is in the BOM, so R_mount carries nothing extra
 m.body_mass[mid]=1e-6;m.body_inertia[mid]=1e-9
 rel,err=ur_map(m,d)
 for i,n in enumerate(UR_BODIES):
  b=m.body(n).id;mm0,c0,I0=body_I(m,b);com=(rel[i]@np.r_[UR_C[i],1])[:3]
  _set_inertial(m,b,UR_M[i],com,I0*UR_M[i]/mm0)   # inertia about the CoM: menagerie values scaled by the mass ratio (E)
 b=m.body('R_arm_base').id;mm0,c0,I0=body_I(m,b);_set_inertial(m,b,UR_BASE,np.array([0,0,.04]),I0*UR_BASE/mm0)   # base CoM 40 mm above the flange (E)
 tid=m.body('R_tool').id;mt,ct,It=body_I(m,tid);mt_new=TOOL['gripper'][0]+TOOL['flange_adapter'][0];_set_inertial(m,tid,mt_new,ct,It*mt_new/mt)
 for jn in ('R_jaw_minus','R_jaw_plus'):m.body_mass[m.body(jn).id]=TOOL['fingers'][0]/2
 mujoco.mj_setConst(m,d)
 return dict(variant=variant,mast=mast or MAST,chassis_scale=chassis_scale,cart_kg=M,cart_com=c.tolist(),ur_map_err_m=err)
def tool_payload(m,d,base,T,M,c,I):
 """R_tool inertial = tool `base` (mass, com, I in the tool frame) + held payload (M, CoM c and inertia I in the
 object frame; object frame = tool frame x T)."""
 if M<=0:_set_inertial(m,m.body('R_tool').id,*base);return
 R=T[:3,:3];p=T[:3,3]+R@c;Mt,ct,It=combine([base,(M,p,R@I@R.T)]);_set_inertial(m,m.body('R_tool').id,Mt,ct,It)
def main():
 import mujoco,r19smooth as S
 os.makedirs(OUT,exist_ok=True)
 res={}
 for mast in ('steel','al'):
  rows,M,c,I=summarize(items(mast));res[mast]=dict(rows=rows,cart_kg=round(M,2),cart_com_m=c.round(4).tolist(),cart_I_about_com_kgm2=I.round(3).tolist())
 # whole machine (cart + UR5e + tool), sim vs BOM, in a typical carry pose (the wok chain's first state)
 ctx=S.setup('wok');m0=ctx['m'];q=np.array(ctx['r']['play'][0])
 out={}
 for var,mast in (('sim',None),('bom','steel'),('bom','al')):
  m=copy.deepcopy(m0);d=mujoco.MjData(m);info=patch(m,d,var,mast)
  d.qpos[:]=q;q[0]=0.;d.qpos[0]=0.;mujoco.mj_forward(m,d);rid=m.body('rail_structure').id
  ids=[b for b in range(1,m.nbody) if m.body_rootid[b]==rid]
  arm=[b for b in ids if m.body(b).name.startswith('R_arm_')];tool=[b for b in ids if m.body(b).name in ('R_tool','R_jaw_minus','R_jaw_plus')]
  sub=lambda B:(float(m.body_mass[B].sum()),(m.body_mass[B][:,None]*d.xipos[B]).sum(0)/m.body_mass[B].sum())
  tm,tc=sub(ids);cm,cc=sub([rid,m.body('R_mount').id]);am,ac=sub(arm);km,kc=sub(tool)
  out[var+('' if mast is None else '_'+mast)]=dict(total_kg=round(tm,2),com_m=(tc-[0,-.21,0]).round(4).tolist(),cart_kg=round(cm,2),cart_com_m=(cc-[0,-.21,0]).round(4).tolist(),
   arm_kg=round(am,3),arm_com_m=(ac-[0,-.21,0]).round(4).tolist(),tool_kg=round(km,3),info=info)
 ur=dict(links=[dict(body=n,mass_kg=UR_M[i],com_dh_m=UR_C[i],sim_mass_kg=float(m0.body_mass[m0.body(n).id])) for i,n in enumerate(UR_BODIES)],
  base_kg_derived=round(UR_BASE,3),sim_base_kg=float(m0.body_mass[m0.body('R_arm_base').id]),total_datasheet_kg=UR_TOTAL,
  sim_total_kg=float(sum(m0.body_mass[m0.body(n).id] for n in UR_BODIES+['R_arm_base'])))
 sp=sim_parts();sm=sum(p[1] for p in sp)
 J=dict(sources=SRC,labels='S sourced, D derived, E estimate, M sim',bom=res,machine=out,ur5e=ur,tool=TOOL,
  sim_cart_parts=[dict(part=n,kg=k,com_m=p) for n,k,p in sp],sim_cart_kg=sm,
  mismatches=['casters: verified_wheels (scene.py) re-sizes every R_cart_wheel_* geom to the 4.85 kg hub motor, so the two casters weigh 4.85 kg each (dock code: 1.5; real 100 mm caster ~0.9 kg): +7.9 kg low and forward',
   'mast 4 kg = aluminium 100x100x4; a steel mast (stiffness, OEM "rigid base" rule) is 10.4 kg',
   'R_mount 1.13 kg (flat plate) vs a 20 deg adapter wedge ~2 kg; beam 2.5 vs 2.7 kg',
   'electrics 3 kg vs 4.2 kg (on-board 48 V supply + driver + safety relay); no covers, E-stop, cable, fasteners in the sim (+5.0 kg)',
   'UR5e: menagerie link masses (UR5 values, 21.0 kg incl. a 4.0 kg base) vs UR DH table 17.7 kg links + 2.9 kg base = 20.6 kg datasheet',
   'mobile.dock_stability uses its own contact lines (+-0.22, -0.22/+0.11) independent of the geoms; the verified_wheels spindles sit at y=+-0.135 (massless)'])
 json.dump(J,open(f'{OUT}/bom.json','w'),indent=1,default=float)
 for mast in ('steel','al'):
  print(f'--- BOM, mast {mast}: cart {res[mast]["cart_kg"]} kg, CoM {res[mast]["cart_com_m"]}')
 for r in res['steel']['rows']:print(' %-55s %d x %6.3f = %6.2f kg  %s  %s'%(r['item'][:55],r['qty'],r['unit_kg'],r['total_kg'],r['label'],r['note'][:40]))
 print('sim cart parts',sm,'kg')
 for k,v in out.items():print(k,'total %.2f kg CoM %s | cart %.2f CoM %s | arm %.2f CoM %s | tool %.2f'%(v['total_kg'],v['com_m'],v['cart_kg'],v['cart_com_m'],v['arm_kg'],v['arm_com_m'],v['tool_kg']),v['info'].get('ur_map_err_m',''))
 print('saved',f'{OUT}/bom.json')
if __name__=='__main__':main()
