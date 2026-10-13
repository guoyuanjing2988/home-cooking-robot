"""R19 arm swap: build the data of a non-UR arm model for the sim (no sim run here).

Reads the vendor description files saved (as data, nothing executed) in sim/vendor_r19/<vendor>/,
checks the URDF joint origins against the vendor's published DH table, moves the vendor's link
masses / CoMs (published in DH frames) into the URDF link frames, and fits collision capsules
that ENCLOSE every vertex of the vendor's per-link STL meshes (checked on points sampled over every
mesh triangle). Writes r19/arm_<id>.json, which arms.py turns into the MJCF arm at scene build.

python r19arm_fit.py fr5|cs66   -> r19/arm_<id>.json
Labels in the output: M = manufacturer file / page, E = derived here, ND = not published."""
import sys,json,struct,math,xml.etree.ElementTree as E
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
H=Path(__file__).resolve().parent;VENDOR=H.parents[1]/'vendor_r19'
def stl(fn):
 b=open(fn,'rb').read();n=struct.unpack('<I',b[80:84])[0];assert 84+50*n==len(b),fn
 a=np.frombuffer(b[84:84+50*n],dtype=np.dtype([('n','<3f4'),('v','<9f4'),('a','<u2')]))
 return a['v'].reshape(-1,3,3).astype(float)
def seg_dist(P,a,b):
 a,b=np.asarray(a,float),np.asarray(b,float);d=b-a;L=d@d
 t=np.clip(((P-a)@d)/L,0,1) if L>0 else np.zeros(len(P));return np.linalg.norm(P-(a+t[:,None]*d),axis=1)
def cyl_dist(P,a,b,r):
 """Distance of points outside a solid cylinder (axis a->b, radius r); <= 0 inside."""
 a,b=np.asarray(a,float),np.asarray(b,float);u=b-a;L=np.linalg.norm(u);u=u/L;t=(P-a)@u;rho=np.linalg.norm(P-a-t[:,None]*u,axis=1)
 ax=np.maximum(np.maximum(-t,t-L),0.);rad=np.maximum(rho-r,0.)
 return np.where((ax>0)|(rad>0),np.hypot(ax,rad),np.maximum(rho-r,np.maximum(-t,t-L)))
def fit(tris,caps,rng):
 """caps: list of (name, a, b, nominal r[, 'cylinder']) read off the STL profiles. Points: every vertex,
 every edge midpoint and 4 random interior points of every triangle. Starting from the nominal sizes,
 each point outside all primitives is charged to the one that needs the least growth to contain it;
 a capsule grows its radius, a cylinder its radius and its axial extent, to its worst charged point
 (repeated until no point is outside)."""
 w=rng.dirichlet([1,1,1],size=4)
 S=np.concatenate([tris.reshape(-1,3),(tris[:,[0,1,2]]+tris[:,[1,2,0]]).reshape(-1,3)/2]+[np.einsum('k,nkj->nj',x,tris) for x in w])
 P=[dict(name=c[0],a=np.array(c[1],float),b=np.array(c[2],float),r=float(c[3]),type=c[4] if len(c)>4 else 'capsule') for c in caps]
 def out(p):return cyl_dist(S,p['a'],p['b'],p['r']) if p['type']=='cylinder' else seg_dist(S,p['a'],p['b'])-p['r']
 for it in range(60):
  M=np.stack([out(p) for p in P],1);best=M.min(1)
  if best.max()<=0:break
  o=best>0;k=np.argmin(M[o],1);Q=S[o]
  for kk in np.unique(k):
   p=P[kk];X=Q[k==kk]
   if p['type']=='capsule':p['r']=max(p['r'],seg_dist(X,p['a'],p['b']).max())
   else:
    u=p['b']-p['a'];L=np.linalg.norm(u);u=u/L;t=(X-p['a'])@u;rho=np.linalg.norm(X-p['a']-t[:,None]*u,axis=1)
    p['r']=max(p['r'],rho.max());lo,hi=min(0.,t.min()),max(L,t.max());p['a'],p['b']=p['a']+lo*u,p['a']+hi*u
 M=np.stack([out(p) for p in P],1)
 return P,float(M.min(1).max()),len(S)
# ---------------- FR5 ----------------
FR5=dict(
 id='fr5',name='Fairino (FAIR INNOVATION) FR5',
 urdf='fairino/fairino5_v6.urdf',stl='fairino/meshes/{}.STL',
 links=['base_link','shoulder_link','upperarm_link','forearm_link','wrist1_link','wrist2_link','wrist3_link'],
 joints=['j1','j2','j3','j4','j5','j6'],
 # Fairino Cobots manual, "Robot brief introduction", Table 2.4-5 FR5 DH parameters (theta offsets 0):
 dh=dict(a=[0,-.425,-.395,0,0,0],d=[.152,0,0,.102,.102,.100],alpha=[math.pi/2,0,0,math.pi/2,-math.pi/2,0],
  mass=[4.64,10.08,2.71,1.56,1.56,.36],com_mm=[[-.19,-18.28,2.26],[212.47,0,121.2],[122.62,.17,12.59],[.05,-2.33,14.68],[-.05,2.33,14.68],[.93,.81,-20.05]],
  source='https://fairino-doc-en.readthedocs.io/latest/CobotsManual/robot_brief_introduction.html (Table 2.4-5); DH xlsx: https://fairino-doc-en.readthedocs.io/latest/_downloads/e40731353903151d7e48b23399b3ea18/FR%20Robots%20DH%20Transformation.xlsx'),
 # primitives (link frame of the URDF): joint housings = cylinders along their joint axis (flat faces:
 # a capsule's cap would add up to its radius, 4-6 cm, beyond every exposed housing face); tubes and
 # webs = capsules along the link (their caps end inside the housings). Ends / radii read off the
 # vendor STL profiles; fit() then grows them until every STL point is inside.
 caps={
  'shoulder_link':[('j1',[0,0,.074],[0,0,.2174],.058,'cylinder'),('j2stub',[0,0,.152],[0,-.0648,.152],.058,'cylinder')],
  'upperarm_link':[('h_shoulder',[0,0,.060],[0,0,.2034],.058,'cylinder'),('h_elbow',[-.425,0,.060],[-.425,0,.2034],.058,'cylinder'),
   ('web_e',[-.425,0,.138],[-.3489,0,.138],.058),('tube',[-.3352,0,.138],[-.0894,0,.138],.0476),('web_s',[0,0,.138],[-.0747,0,.138],.058)],
  'forearm_link':[('h_elbow',[0,0,-.040],[0,0,.0648],.058,'cylinder'),('web',[0,0,.012],[-.0772,0,.012],.045),('tube',[-.3489,0,0],[-.0772,0,0],.040),('h_wrist1',[-.395,0,-.0495],[-.395,0,.0582],.040,'cylinder')],
  'wrist1_link':[('h_j5',[0,-.058,.1021],[0,.0495,.1021],.040,'cylinder'),('neck',[0,0,.0533],[0,0,.1021],.040,'cylinder')],
  'wrist2_link':[('h_j6',[0,-.0495,.102],[0,.0582,.102],.040,'cylinder'),('neck',[0,0,.0532],[0,0,.102],.040,'cylinder')],
  'wrist3_link':[('flange',[0,0,.053],[0,0,.0990],.040,'cylinder')]},
 base_mesh='base_link',
 # datasheet (fairino.us FR5 page) and URDF/joint_limits.yaml values
 limits_deg_datasheet=[[-175,175],[-265,85],[-160,160],[-265,85],[-175,175],[-175,175]],
 speeds_degps_datasheet=[180]*6,
 sources=dict(datasheet='https://www.fairino.us/collaborative-robot/fairino/fr5',
  urdf='https://raw.githubusercontent.com/FAIR-INNOVATION/frcobot_ros2/main/fairino_description/urdf/fairino5_v6.urdf',
  meshes='https://github.com/FAIR-INNOVATION/frcobot_ros2/tree/main/fairino_description/meshes/fairino5_v6',
  joint_limits_yaml='https://raw.githubusercontent.com/FAIR-INNOVATION/frcobot_ros2/main/fairino5_v6_moveit2_config/config/joint_limits.yaml',
  load_curve='https://fairino-doc-en.readthedocs.io/latest/CobotsManual/installation.html (3.4.5.2.5, Figure 3.4-19)',
  installation='https://fairino-doc-en.readthedocs.io/latest/CobotsManual/installation.html (3.4.1.2)',
  safety='https://fairino-doc-en.readthedocs.io/latest/CobotsManual/safety.html'))
def rpy(r):return Rotation.from_euler('xyz',r).as_matrix()
def run(spec):
 root=E.parse(VENDOR/spec['urdf']).getroot();J={j.get('name'):j for j in root.findall('joint')};L={l.get('name'):l for l in root.findall('link')}
 dh=spec['dh'];out=dict(id=spec['id'],name=spec['name'],sources=spec['sources'],labels=dict(M='manufacturer',E='derived here',ND='not published'),links=[])
 # 1. URDF joint origins vs DH: link i+1 frame in link i frame at q=0 must be Tz(d_i) Tx(a_i) Rx(alpha_i)
 check=[]
 for i,jn in enumerate(spec['joints']):
  o=J[jn].find('origin');xyz=np.fromstring(o.get('xyz'),sep=' ');R=rpy(np.fromstring(o.get('rpy'),sep=' '))
  if i==0:check.append(dict(joint=jn,urdf_xyz=xyz.tolist(),note='base_link -> j1 at the base origin (DH frame 0 = base_link)'));continue
  k=i-1;want_p=np.array([dh['a'][k],0,dh['d'][k]]);want_R=Rotation.from_euler('x',dh['alpha'][k]).as_matrix()
  check.append(dict(joint=jn,urdf_xyz=xyz.tolist(),dh_xyz=want_p.tolist(),dp_mm=round(float(np.linalg.norm(xyz-want_p))*1000,2),dR_deg=round(float(np.degrees(Rotation.from_matrix(R@want_R.T).magnitude())),3)))
 out['urdf_vs_dh']=check
 assert all(c.get('dp_mm',0)<=.2 and c.get('dR_deg',0)<=.01 for c in check),check
 rng=np.random.default_rng(0)
 for i,ln in enumerate(spec['links']):
  lk=L[ln];inert=lk.find('inertial');I=inert.find('inertia');urdf_mass=float(inert.find('mass').get('value'))
  Iu=np.array([[float(I.get('ixx')),float(I.get('ixy')),float(I.get('ixz'))],[float(I.get('ixy')),float(I.get('iyy')),float(I.get('iyz'))],[float(I.get('ixz')),float(I.get('iyz')),float(I.get('izz'))]])
  rec=dict(link=ln)
  if i==0:
   rec.update(mass=urdf_mass,com=np.fromstring(inert.find('origin').get('xyz'),sep=' ').tolist(),inertia_full=Iu[[0,1,2,0,0,1],[0,1,2,1,2,2]].tolist(),
    inertial_label='M (URDF base_link; base is fixed to the mount, so it only adds to the cart mass)')
  else:
   k=i-1;Rdh=Rotation.from_euler('x',dh['alpha'][k]).as_matrix();pdh=np.array([dh['a'][k],0,dh['d'][k]])
   c=pdh+Rdh@(np.array(dh['com_mm'][k])/1000)
   assert abs(urdf_mass-dh['mass'][k])<1e-6 and np.allclose(np.fromstring(inert.find('origin').get('xyz'),sep=' '),np.array(dh['com_mm'][k])/1000,atol=2e-5),ln
   Il=Rdh@Iu@Rdh.T
   rec.update(mass=dh['mass'][k],com=c.round(6).tolist(),inertia_full=Il[[0,1,2,0,0,1],[0,1,2,1,2,2]].tolist(),
    inertial_label='M mass and CoM (DH table, DH frame %d, moved into the URDF link frame here: the URDF carries the same numbers but in the DH frames, e.g. the upper-arm CoM x=+0.212 lies outside its own mesh); E inertia tensor (URDF values, assumed in the same DH frame, rotated with it)'%(k+1))
  if ln in spec['caps']:
   tris=stl(VENDOR/spec['stl'].format(ln));Pr,miss,n=fit(tris,spec['caps'][ln],rng)
   V=tris.reshape(-1,3)
   rec['capsules']=[dict(name=p['name'],type=p['type'],fromto=np.round(np.r_[p['a'],p['b']],5).tolist(),radius=round(float(p['r'])+5e-5,4),nominal_radius=c[3]) for p,c in zip(Pr,spec['caps'][ln])]
   rec['mesh_bbox']=[V.min(0).round(4).tolist(),V.max(0).round(4).tolist()];rec['enclosure_check']=dict(points=n,max_outside_m=miss)
   rec['capsule_label']='E: capsules / cylinders (the wrist housings, whose flat faces sit a few mm from the next-but-one link) enclosing every vertex and every sampled triangle point of the vendor STL (M); radius rounded up by 0.05 mm'
  out['links'].append(rec)
 for i,jn in enumerate(spec['joints']):
  j=J[jn];o=j.find('origin');lim=j.find('limit')
  out.setdefault('joints',[]).append(dict(name=jn,parent=j.find('parent').get('link'),child=j.find('child').get('link'),xyz=np.fromstring(o.get('xyz'),sep=' ').tolist(),rpy=np.fromstring(o.get('rpy'),sep=' ').tolist(),
   axis=np.fromstring(j.find('axis').get('xyz'),sep=' ').tolist(),urdf_limit_rad=[float(lim.get('lower')),float(lim.get('upper'))],urdf_velocity_rad_s=float(lim.get('velocity')),urdf_effort_Nm=float(lim.get('effort')),
   datasheet_limit_deg=spec['limits_deg_datasheet'][i],datasheet_speed_degps=spec['speeds_degps_datasheet'][i]))
 out['flange']=dict(xyz=[0,0,dh['d'][5]],label='M: DH d6 = 100 mm (Table 2.4-5); the URDF has no flange frame; the wrist3 STL ends at 99.0 mm',frame='DH frame 6 (theta6 offset 0)')
 out['base_mesh']=str((VENDOR/spec['stl'].format(spec['base_mesh'])).resolve()).replace('\\','/')
 out['dh']=dh
 return out
# ---------------- Elite CS66 (ur_description-style package: frames = UR-convention DH) ----------------
CS66=dict(
 id='cs66',name='Elite Robots CS66',stl='elite/meshes/{}.stl',
 links=['base','shoulder','upperarm','forearm','wrist1','wrist2','wrist3'],
 # config/cs66/default_kinematics.yaml (joint origins, all axes z): (xyz, rpy) parent link -> joint frame
 kin=[((0,0,.1625),(0,0,0)),((0,0,0),(math.pi/2,0,0)),((-.4270,0,0),(0,0,0)),((-.3905,0,.1475),(0,0,0)),((0,-.0965,0),(math.pi/2,0,0)),((0,.0950,0),(-math.pi/2,0,0))],
 kin_file='elite/default_kinematics.yaml',
 # config/cs66/physical_parameters.yaml: masses, CoG (link frames), inertia
 mass=[.57127,4.521,7.533,3.009,1.559,1.447,.500],
 cog=[[-.00060346,1.4311e-05,.060221],[2.2e-05,-.016526,-.014442],[-.17828,4e-06,.12803],[-.20416,-7e-06,.03064],[1.3e-05,-.00479,-.02274],[-1.4e-05,.005107,-.012702],[-.000684,-.000175,-.04234]],
 inertia=[[.0010759,.0010109,.001408,7.8337e-08,-1.3213e-05,4.5992e-07],[.014192,.0091982,.012777,1.7839e-05,-1.027e-06,-4.6778e-05],[.13719,.6614,.53649,-7.5676e-05,-.17551,7.59e-06],
  [.0087604,.22281,.2176,1.7762e-05,-.010765,-4.13e-07],[.0045009,.0042164,.0014539,1.961e-06,-2.646e-06,-3.58e-07],[.0023787,.0020859,.0013191,1.953e-06,2.643e-06,5.584e-06],[.0014314,.0014299,.0003265,-2.32e-07,7.955e-06,1.266e-06]],
 dh=dict(d=[.1625,0,0,.1475,.0965,.0920],a=[0,-.4270,-.3905,0,0,0],note='physical_parameters.yaml dh_parameters; d6 = 0.0920 there but 0.0950 in default_kinematics.yaml (the URDF uses the latter)'),
 caps={
  'shoulder':[('j1',[0,0,-.0706],[0,0,.0772],.059,'cylinder'),('j2stub',[0,0,0],[0,-.0704,0],.059,'cylinder')],
  'upperarm':[('h_shoulder',[0,0,.0704],[0,0,.2188],.0608,'cylinder'),('h_elbow',[-.427,0,.0738],[-.427,0,.2188],.050,'cylinder'),
   ('web_e',[-.427,0,.1446],[-.355,0,.1446],.050),('tube',[-.343,0,.141],[-.119,0,.141],.050),('web_s',[0,0,.1446],[-.096,0,.1446],.060)],
  'forearm':[('h_elbow',[0,0,-.0354],[0,0,.0738],.0485,'cylinder'),('web',[0,0,.013],[-.111,0,.013],.045),('tube',[-.350,0,.013],[-.131,0,.013],.040),('h_wrist1',[-.3905,0,-.0544],[-.3905,0,.0620],.040,'cylinder')],
  'wrist1':[('h_j5',[0,-.049,0],[0,.0674,0],.0397,'cylinder'),('neck',[0,0,-.0855],[0,0,0],.0397,'cylinder')],
  'wrist2':[('h_j6',[0,-.0674,0],[0,.049,0],.0397,'cylinder'),('neck',[0,0,-.0475],[0,0,0],.0397,'cylinder')],
  'wrist3':[('flange',[0,0,-.043],[0,0,0],.0385,'cylinder')]},
 base_mesh='base',
 limits_deg_urdf=[[-360,360],[-360,360],[-180,180],[-360,360],[-360,360],[-360,360]],
 speeds_degps_datasheet=[150,150,180,230,230,230],speeds_degps_urdf=[180]*6,
 sources=dict(datasheet='https://www.neobotix-robots.com/fileadmin/images/downloads/Datenbl%C3%A4tter/CS66_Datasheet.pdf (joint speeds J1-J2 150, J3 180, J4-J6 230 deg/s; J1-J6 +-360 deg; mounting any angle; 20 kg; IP65)',
  description='https://github.com/EliteRobots/Elite_Robots_CS_ROS2_Description/tree/humble (config/cs66/*.yaml, meshes/cs66/collision/*.stl, urdf/cs_macro.xacro)'))
def inertia_at_com(m,c,I6):
 """Elite yaml inertia: products of inertia ~ m*x*z of the CoG offset, i.e. about the link origin, not
 about the CoG. Moved to the CoG by the parallel-axis theorem (tensor elements). Dynamics only."""
 ixx,iyy,izz,ixy,ixz,iyz=I6;Io=np.array([[ixx,ixy,ixz],[ixy,iyy,iyz],[ixz,iyz,izz]]);c=np.asarray(c)
 for sgn in (1,-1):
  Ic=Io-m*(c@c*np.eye(3)-np.outer(c,c))*np.array([[1,sgn,sgn],[sgn,1,sgn],[sgn,sgn,1]])
  w=np.linalg.eigvalsh(Ic)
  if w.min()>0 and w[0]+w[1]>=w[2]-1e-12:return Ic,'E: inertia moved to the CoG by the parallel-axis theorem (sign %+d)'%sgn
 return np.diag(np.maximum(np.diag(Io),1e-6)),'E: diagonal of the vendor values (no valid CoG tensor found)'
def run_cs66(spec):
 import re
 txt=(VENDOR/spec['kin_file']).read_text()
 vals=[float(v) for v in re.findall(r'(?:x|y|z|roll|pitch|yaw):\s*([-\d.]+)',txt)]
 want=[v for p,r in spec['kin'] for v in (*p,*r)]
 assert np.allclose(vals,want,atol=1e-6),'kinematics yaml changed'
 out=dict(id=spec['id'],name=spec['name'],sources=spec['sources'],labels=dict(M='manufacturer',E='derived here',ND='not published'),links=[],
  frames_note='M: default_kinematics.yaml; the chain equals the UR-convention DH (d1 .1625, a2 -.427, a3 -.3905, d4 .1475, d5 .0965, d6 .095) exactly, base frame = base_link, wrist3 frame = flange = DH frame 6 (checked numerically)')
 rng=np.random.default_rng(0)
 for i,ln in enumerate(spec['links']):
  Ic,lab=inertia_at_com(spec['mass'][i],spec['cog'][i],spec['inertia'][i])
  rec=dict(link=ln,mass=spec['mass'][i],com=spec['cog'][i],inertia_full=Ic[[0,1,2,0,0,1],[0,1,2,1,2,2]].tolist(),inertial_label='M mass and CoG (physical_parameters.yaml, link frames; vendor note: base values might be incorrect); '+lab)
  if ln in spec['caps']:
   tris=stl(VENDOR/spec['stl'].format(ln));Pr,miss,n=fit(tris,spec['caps'][ln],rng);V=tris.reshape(-1,3)
   rec['capsules']=[dict(name=p['name'],type=p['type'],fromto=np.round(np.r_[p['a'],p['b']],5).tolist(),radius=round(float(p['r'])+5e-5,4),nominal_radius=c[3]) for p,c in zip(Pr,spec['caps'][ln])]
   rec['mesh_bbox']=[V.min(0).round(4).tolist(),V.max(0).round(4).tolist()];rec['enclosure_check']=dict(points=n,max_outside_m=miss)
   rec['capsule_label']='E: cylinders (joint housings) / capsules (tubes, webs) enclosing every vertex and every sampled triangle point of the vendor collision STL (M); radius rounded up by 0.05 mm'
  out['links'].append(rec)
 names=['shoulder_pan','shoulder_lift','elbow','wrist_1','wrist_2','wrist_3']
 for i,(p,r) in enumerate(spec['kin']):
  out.setdefault('joints',[]).append(dict(name=names[i]+'_joint',parent=spec['links'][i],child=spec['links'][i+1],xyz=list(p),rpy=list(r),axis=[0,0,1],
   datasheet_limit_deg=spec['limits_deg_urdf'][i],limit_label='M: URDF joint_limits.yaml (datasheet: J1-J6 +-360; the URDF elbow +-180 is the stricter and is used)',
   datasheet_speed_degps=spec['speeds_degps_datasheet'][i],urdf_speed_degps=spec['speeds_degps_urdf'][i]))
 out['flange']=dict(xyz=[0,0,0],label='M: the wrist3 link frame is the flange / tool0 (cs_macro.xacro), d6 = 0.095 (default_kinematics.yaml; physical_parameters.yaml says 0.092)',frame='DH frame 6')
 out['base_mesh']=str((VENDOR/spec['stl'].format(spec['base_mesh'])).resolve()).replace('\\','/')
 out['dh']=spec['dh'];return out
if __name__=='__main__':
 arm=sys.argv[1] if len(sys.argv)>1 else 'fr5';res=run(FR5) if arm=='fr5' else run_cs66(CS66)
 p=H/'r19'/f'arm_{arm}.json';p.write_text(json.dumps(res,indent=1),encoding='utf-8');print(p)
 for l in res['links']:
  print(l['link'],'mass',l['mass'],'com',l['com'],*(f"\n  {c['name']} r={c['radius']} (nominal {c['nominal_radius']})" for c in l.get('capsules',[])),'\n  outside',l.get('enclosure_check'))
 print(json.dumps(res.get('urdf_vs_dh',res.get('frames_note'))))
