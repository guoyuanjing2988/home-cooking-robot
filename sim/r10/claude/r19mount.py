"""R19 #42: buildable gripper mounts for the PGC-140-50 (design study). New file. Used by arms.py for the arm options
*_m<k> (ARMS[..]['mount'] = a MOUNTS key): apply() re-poses R_tool on the flange and adds the modelled bracket.

The problem (R19_CABLE2.md 1, DECISIONS 2026-10-14): the R10 tool pose puts the gripper axis 26.6 deg off J6 with the
gripper's mounting face 45 mm BEHIND the flange plane and 78 mm off axis, so the housing lies 16.9 mm inside wrist 3 (UR5e)
and no adapter could hold it there.

Frames. F = the flange frame (R_attachment_site, DH frame 6; z out of the flange) of the UR5e model, in which the R10 pose is
defined; u = +x_F is the side the gripper base sits on. arms.swap() carries R_tool with everything on it to another arm at
the same flange-relative pose (turned by that arm's clock_deg; the FR5 options here use fr5_j6_pgc: clock 90 deg, NO spacer,
the bracket replaces the sp20 plate). The housing frame is scene.oem_pgc_drawing's: housing axis = tool x, the mounting
face (the robot face of DH's standard flange, which the model's 98 / 138.5 mm heights include, R19_CABLE2.md 1) at
x = X0 = -0.1735 m plus the finger-design shift (pos of R_gripper_oem_envelope).

A mount = a rigid motion of the whole gripper in F: turn by rot_deg about y_F through the mounting-face centre, then put
the face centre at c (absolute, m, in (u, z)) or move it by dc. Everything on R_tool (housing, jaws, fingers, held parts,
TCP R_prep) moves with it: the TCP moves by exactly the same rigid motion.

The bracket (6061-T6 aluminium, 2.70 g/cm3 [S: ASM handbook value]) is two convex pieces on R_tool, named like the housing
(R_gripper_oem_*) so every tool treats them as the gripper body (5 mm to the environment, 0 mm self; NOT held):
 R_gripper_oem_mount_base  the mating boss: Ø63 x T1 on the flange face (ISO 9409-1-50-4-M6 robot side [S]: Ø63 flange,
                           4 x M6 on PCD 50, Ø6 pin, Ø31.5 H7 centring recess; the boss carries a Ø31.5 g6 x 2.5 spigot
                           into that recess). Its bottom face is the bolted mating face: it touches the flange by design
                           (like the named mating faces of the rail wall brackets, DECISIONS 2026-10-08), so it is the
                           only part exempt from the 5 mm wrist-3 gate; it stays inside the flange's Ø63 footprint.
 the rest, by bracket type (spec['bracket']); its gripper side presents the ISO 9409-1-50-4-M6 tool face that DH's
 standard flange bolts to (4 x M6 tapped on PCD 50, Ø31.5 H7 x 3 recess, Ø6 pin), exactly as on a robot; DH's flange
 (Ø75 x 5, in the housing model from X0) is kept:
  'hull'   R_gripper_oem_mount_body = hull of the boss top (Ø63 at z = T1) and the gripper support (the Ø75 face disc, or
           that disc extruded TF behind the face): one convex block (the wedge, tf = 0, and the single-block offset bracket);
           clip=True: that hull cut by the gripper's face plane (the wedge's top IS the face plane; nothing on the gripper side);
  'L'      an offset L bracket: R_gripper_oem_mount_arm = a plate on the boss, z = T1 .. T1 + T_ARM, |y| <= R_FL, from
           u = -R_FL out to u_arm - W_END (radially over wrist 3); R_gripper_oem_mount_drop = hull of the arm's end
           (u_arm - W_END .. u_arm) and the gripper support plate (Ø75 x TF behind the face): the leg that comes down
           beside wrist 3 to the gripper;
  'spacer' R_gripper_oem_mount_body = the Ø63 plate z = T1 .. c_z (inline mount).
Circles are polygons circumscribed about the true circle (NSEG sides), so the hulls enclose the solids.
Mass: from the geometry (tetrahedral decomposition of the convex pieces), minus the holes / plus the spigot (listed in
HOLES), plus DH's standard flange (22.6 cm3 of aluminium, CAD [S, R19_CABLE2.md 1] = 61 g, at 2.5 mm above the face).
Pocketed bodies (POCKET=True): the body hull minus its inward offset by WALL (8 mm walls all round) [E: a closed shell; an
open pocket from one side is a little lighter].
The bracket mass, the DH flange and the existing EOAT (R_tool 1.0 kg + jaws 0.2 kg) are folded into R_tool's inertial."""
import numpy as np
import xml.etree.ElementTree as E
from scipy.spatial import ConvexHull,HalfspaceIntersection
from scipy.spatial.transform import Rotation
RHO=2700.          # kg/m3, 6061 aluminium [S: handbook 2.70 g/cm3]
X0=-.1735          # mounting face in the housing frame (scene.oem_pgc_drawing, r19cable.X0)
R_FL=.0315         # ISO 9409-1-50 flange Ø63 [S: Fairino manual 3.4.2 Fig. 3.4-13; UR5e tool flange ISO 9409-1-50-4-M6]
R_GR=.0375         # PGC-140 body / DH standard flange Ø75 [S: DH drawing]
T1=.005            # mating boss height (E: design); a mount may set its own (spec['t1'])
TF=.010            # gripper support plate behind the face, offset brackets (E: design, >= WALL)
WALL=.008          # minimum wall (task rule, E)
T_ARM=.010         # L bracket arm plate (E: design, >= WALL)
W_END=.010         # L bracket: length of the arm end merged into the drop leg (E)
NSEG=32
DH_FLANGE=dict(kg=22.6e-6*RHO,dz=.0025,src='S: DH standard flange STEP, one solid 22.6 cm3 (R19_CABLE2.md 1) x 2.70 g/cm3; centroid taken 2.5 mm above its robot face [E]')
TILT0=float(np.degrees(np.arctan2(.448,.894)))   # the R10 tilt, 26.6 deg (measured: tool x in F = (-0.448, 0, 0.894))
# Mount candidates (u = +x_F, z = flange axis; m). Chosen by r19mount_design.py (R19_MOUNT.md 2). Recommended: m2.
MOUNTS={
 'm1':dict(label='C1 same tilt and offset, moved 77.5 mm out along the flange axis; offset L bracket',bracket='L',rot_deg=0.,dc=(0.,.0775),u_arm=.054,tf=TF,pocket=True),
 'm2':dict(label='C2 wedge: same 26.6 deg tilt, the gripper on the inclined top face of a wedge bolted to the flange',bracket='hull',rot_deg=0.,c=(.035,.03875),tf=0.,pocket=False,t1=.008,clip=True),   # t1 8 mm: the wedge's thinnest section is the boss rim on its low side (wall rule); clip: its top is the face plane
 'm3':dict(label='C3 inline: gripper axis on J6, DH standard flange on an 8 mm ISO 50 spacer',bracket='spacer',rot_deg=TILT0,c=(0.,.008),tf=0.,face_r=R_FL,pocket=False),
}
# Holes / features of every bracket (volume m3, + adds material), [E: design]
HOLES=[('robot side 4 x M6 clearance Ø6.6 through the boss', -4*np.pi*.0033**2*T1),
 ('robot side spigot Ø31.5 x 2.5 (into the flange recess)', np.pi*.01575**2*.0025),
 ('gripper side Ø31.5 x 3 centring recess', -np.pi*.01575**2*.003),
 ('gripper side 4 x M6 tapped, Ø5 x 12 deep', -4*np.pi*.0025**2*.012)]
def fmt(v):return ' '.join(f'{float(x):.12g}' for x in v)
def T(p,R):X=np.eye(4);X[:3,:3]=R;X[:3,3]=p;return X
def _pose(el):
 p=np.fromstring(el.get('pos','0 0 0'),sep=' ');q=np.fromstring(el.get('quat','1 0 0 0'),sep=' ')
 return T(p,Rotation.from_quat(q[[1,2,3,0]]/np.linalg.norm(q)).as_matrix())
def quat(R):return Rotation.from_matrix(R).as_quat()[[3,0,1,2]]
def ring(r,n=NSEG):
 t=2*np.pi*(np.arange(n)+.5)/n;return (r/np.cos(np.pi/n))*np.c_[np.cos(t),np.sin(t)]
def disc(c,nrm,r,n=NSEG):
 """vertices of a circumscribed polygon of radius r, centre c, normal nrm (in F)"""
 nrm=np.asarray(nrm,float)/np.linalg.norm(nrm);e2=np.array([0,1.,0]) if abs(nrm[1])<.9 else np.array([1.,0,0])
 e1=np.cross(e2,nrm);e1/=np.linalg.norm(e1);e2=np.cross(nrm,e1)
 return np.array([np.asarray(c,float)+a*e1+b*e2 for a,b in ring(r,n)])
# ---------------- the current pose and the mount motion ----------------
def current(tree):
 """flange -> tool transform (4x4, F frame), mounting-face centre c0 and gripper axis a0 in F, from the tree (UR5e bodies)."""
 w3=tree.find(".//body[@name='R_arm_wrist_3_link']");site=w3.find("site[@name='R_attachment_site']");tool=w3.find("body[@name='R_tool']")
 X=np.linalg.inv(_pose(site))@_pose(tool)
 env=tool.find("geom[@name='R_gripper_oem_envelope']");sh=np.fromstring(env.get('pos','0 0 0'),sep=' ') if env is not None else np.zeros(3)
 face_t=np.array([X0,0,0])+sh
 return X,X[:3,:3]@face_t+X[:3,3],X[:3,0].copy(),face_t
def motion(spec,c0):
 """(R_m, c_new): turn by rot_deg about y_F through the face centre, then move the face centre to c / by dc."""
 Rm=Rotation.from_euler('y',spec.get('rot_deg',0.),degrees=True).as_matrix()
 if 'c' in spec:cn=np.array([spec['c'][0],0.,spec['c'][1]])
 else:cn=c0+np.array([spec['dc'][0],0.,spec['dc'][1]])
 return Rm,cn
def new_tool(X0_,c0,spec):
 Rm,cn=motion(spec,c0);R=Rm@X0_[:3,:3];p=Rm@(X0_[:3,3]-c0)+cn;return T(p,R),cn,Rm@X0_[:3,0]
def bracket_F(spec,cn,n):
 """convex pieces of the bracket in F: {name: vertices}. spec['t1']: this mount's boss height (default T1)."""
 t1=spec.get('t1',T1);base=np.vstack([np.c_[ring(R_FL),np.full(NSEG,z)] for z in (0.,t1)])
 top=np.c_[ring(R_FL),np.full(NSEG,t1)]
 fr=spec.get('face_r',R_GR);face=disc(cn,n,fr);plate=np.vstack([face,face-spec.get('tf',0.)*np.asarray(n)]) if spec.get('tf',0.)>0 else face
 kind=spec.get('bracket','hull')
 if kind=='spacer':return {'R_gripper_oem_mount_base':base,'R_gripper_oem_mount_body':np.vstack([top,np.c_[ring(R_FL),np.full(NSEG,cn[2])]])}
 if kind=='L':
  ua=spec['u_arm'];box=lambda u0,u1:np.array([[u,y,z] for u in (u0,u1) for y in (-R_FL,R_FL) for z in (t1,t1+T_ARM)])
  return {'R_gripper_oem_mount_base':base,'R_gripper_oem_mount_arm':box(-R_FL,ua-W_END),'R_gripper_oem_mount_drop':np.vstack([box(ua-W_END,ua),plate])}
 body=np.vstack([top,plate])
 if spec.get('clip'):   # the part is bounded by the gripper face plane: the hull clipped to the side behind it (convex)
  h=ConvexHull(body);eq=np.vstack([h.equations,np.r_[n,-float(np.dot(n,cn))]]);ip=np.array([0.,0.,t1+.001])
  assert np.all(eq[:,:3]@ip+eq[:,3]<0),'clip: no interior point'
  body=HalfspaceIntersection(eq,ip).intersections
 return {'R_gripper_oem_mount_base':base,'R_gripper_oem_mount_body':body}
# ---------------- mass properties of convex polytopes ----------------
def poly_props(V):
 """volume (m3), centroid, inertia about the centroid per unit density (3x3) of the convex hull of V."""
 V=np.asarray(V,float);h=ConvexHull(V);o=V[h.vertices].mean(0);vol=0.;c=np.zeros(3);C=np.zeros((3,3))
 for s in h.simplices:
  a,b,d=V[s]-o;v=abs(np.linalg.det(np.c_[a,b,d]))/6.
  if v<=0:continue
  P=np.array([np.zeros(3),a,b,d]);S=P.sum(0)
  vol+=v;c+=v*S/4;C+=v/20.*(P.T@P+np.outer(S,S))
 c/=vol;Cc=C-vol*np.outer(c,c);I=np.trace(Cc)*np.eye(3)-Cc
 return vol,c+o,I
def inner(V,off):
 """the convex hull of V offset inward by off (halfspace intersection); None if empty."""
 h=ConvexHull(V);eq=h.equations.copy();eq[:,3]+=off
 ctr=V[h.vertices].mean(0)
 if np.any(eq[:,:3]@ctr+eq[:,3]>=0):return None
 try:return HalfspaceIntersection(eq,ctr).intersections
 except Exception:return None
def mass_props(spec,parts):
 """bracket mass (kg), CoG (F, m), inertia about the CoG (F), with per-piece rows; + DH flange separately."""
 rows=[];M=0.;S=np.zeros(3);Ilist=[]
 for nm,V in parts.items():
  vol,c,I=poly_props(V);row=dict(piece=nm,solid_cm3=round(vol*1e6,1))
  if (nm.endswith('body') or nm.endswith('drop')) and spec.get('pocket'):
   Vi=inner(V,WALL)
   if Vi is not None:
    vi,ci,Ii=poly_props(Vi);vs=vol-vi;cs=(vol*c-vi*ci)/vs
    d0=c-cs;d1=ci-cs;I=(I+vol*(np.dot(d0,d0)*np.eye(3)-np.outer(d0,d0)))-(Ii+vi*(np.dot(d1,d1)*np.eye(3)-np.outer(d1,d1)));vol,c=vs,cs
    row.update(pocket_cm3=round(vi*1e6,1))
  row.update(cm3=round(vol*1e6,1),kg=round(vol*RHO,4),cog_mm=np.round(c*1e3,1).tolist());rows.append(row)
  Ilist.append((vol*RHO,c,I*RHO));M+=vol*RHO;S+=vol*RHO*c
 hv=sum(v for _,v in HOLES);hz=spec.get('t1',T1)/2   # holes / spigot, taken at the boss (centre of the flange, z = t1/2) [E]
 Ilist.append((hv*RHO,np.array([0,0,hz]),np.zeros((3,3))));M+=hv*RHO;S+=hv*RHO*np.array([0,0,hz])
 com=S/M;Itot=np.zeros((3,3))
 for m_,c,I in Ilist:d=c-com;Itot+=I+m_*(np.dot(d,d)*np.eye(3)-np.outer(d,d))
 return dict(kg=float(M),cog_F=com,I_F=Itot,rows=rows,holes_cm3=round(hv*1e6,1))
def describe(spec,X0_,c0):
 """everything about a mount in F (no tree): new tool transform, face, bracket pieces and mass."""
 Xn,cn,n=new_tool(X0_,c0,spec);parts=bracket_F(spec,cn,n);mp=mass_props(spec,parts)
 dh=dict(kg=DH_FLANGE['kg'],cog_F=cn+DH_FLANGE['dz']*n)
 return dict(X=Xn,c=cn,n=n,parts=parts,mass=mp,dh_flange=dh)
# ---------------- the arms.py hook ----------------
def apply(tree,key):
 """arms.swap() hook (UR5e bodies, before any arm swap): re-pose R_tool for MOUNTS[key], add the bracket pieces on
 R_tool, fold the bracket + DH flange into R_tool's inertial."""
 spec=MOUNTS[key];w3=tree.find(".//body[@name='R_arm_wrist_3_link']");site=w3.find("site[@name='R_attachment_site']");tool=w3.find("body[@name='R_tool']")
 X0_,c0,a0,_=current(tree);D=describe(spec,X0_,c0);Xn=D['X']
 Wt=_pose(site)@Xn;tool.set('pos',fmt(Wt[:3,3]));tool.set('quat',fmt(quat(Wt[:3,:3])))
 Ri=Xn[:3,:3].T;pi=Xn[:3,3];asset=tree.getroot().find('asset')
 for nm,V in D['parts'].items():
  Vt=(V-pi)@Ri.T   # F -> tool frame
  E.SubElement(asset,'mesh',name='M_'+nm,vertex=' '.join(fmt(v) for v in Vt))
  E.SubElement(tool,'geom',name=nm,type='mesh',mesh='M_'+nm,rgba='.75 .77 .8 1',contype='2',conaffinity='3',mass='.000001')
 # inertial: existing R_tool inertial + bracket + DH flange (tool frame)
 ine=tool.find('inertial');m0=float(ine.get('mass'));p0=np.fromstring(ine.get('pos','0 0 0'),sep=' ')
 if ine.get('fullinertia'):f=np.fromstring(ine.get('fullinertia'),sep=' ');I0=np.array([[f[0],f[3],f[4]],[f[3],f[1],f[5]],[f[4],f[5],f[2]]])
 else:I0=np.diag(np.fromstring(ine.get('diaginertia'),sep=' '))
 if ine.get('quat'):Rq=Rotation.from_quat(np.fromstring(ine.get('quat'),sep=' ')[[1,2,3,0]]).as_matrix();I0=Rq@I0@Rq.T
 mp=D['mass'];items=[(m0,p0,I0),(mp['kg'],Ri@(mp['cog_F']-pi),Ri@mp['I_F']@Ri.T),(D['dh_flange']['kg'],Ri@(D['dh_flange']['cog_F']-pi),np.zeros((3,3)))]
 M=sum(m for m,_,_ in items);com=sum(m*c for m,c,_ in items)/M;I=np.zeros((3,3))
 for m,c,Ii in items:d=c-com;I+=Ii+m*(np.dot(d,d)*np.eye(3)-np.outer(d,d))
 for k in ('diaginertia','quat','fullinertia'):ine.attrib.pop(k,None)
 ine.set('mass',f'{M:.12g}');ine.set('pos',fmt(com));ine.set('fullinertia',fmt([I[0,0],I[1,1],I[2,2],I[0,1],I[0,2],I[1,2]]))
 return tree
