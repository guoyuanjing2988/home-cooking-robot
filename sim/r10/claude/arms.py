"""R19 arm option: which arm the scene is built with (default UR5e, unchanged).

Choose it with cfg['arm'], or ARM=<id> on the command line (the KEY=VALUE style of every script
here), or the environment variable ARM. Ids: ur5e (default), fr5 (Fairino FR5, stock J6 +-175 deg),
fr5_j6 (FR5 with the optional J6 +-360 deg), fr5_pgc / fr5_j6_pgc / cs66_pgc (the same arms with the PGC-140 housing
from DH's drawing, as ur5e_enc2_pgc), ur5e_enc (R19 #12: the UR5e, with collision geoms that enclose the Menagerie
visual meshes, r19/arm_ur5e_enc.json from r19ur5e_encfit.py; everything else is the UR5e's), ur5e_enc2 (the same, tighter:
convex pieces, r19/arm_ur5e_enc2.json from r19ur5e_enc2fit.py). For ur5e nothing in the model is touched.

For another arm, scene.build calls swap(): the UR5e bodies under R_mount are replaced by the arm
built from r19/arm_<model>.json (r19arm_fit.py: vendor URDF frames, DH masses/CoMs, capsules
enclosing the vendor STL meshes), with the SAME body / joint / site names, so the checker, the
solver and every script work unchanged. The gripper (R_tool, with everything the scene put on it)
is moved over unchanged, at the same pose relative to the flange (DH frame 6) as on the UR5e
(whose R_attachment_site is its DH frame 6), turned by CLOCK_DEG about the flange axis.

Mount yaw and gripper clocking (design choices, E): FR5 J1 and J6 stop at +-175 deg. The 10 deg dead
zone of each is put where the checked UR5e chains (results/r17/chain_*_final, spatula, plate 2) never
are: J1 in the largest unused UR J1 sector (209..305 deg, centre 257 deg) -> base turned 77 deg in
the mount; J6 in the only unused UR J6 sector (260..280 deg, centre 270 deg) -> gripper turned 90 deg
on the flange. Chosen once from the UR5e data, before any FR5 run (R19_ARM_SWAP.md)."""
import os,sys,json,copy,xml.etree.ElementTree as E
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
H=Path(__file__).resolve().parent
UR_ENV_SOURCE='https://www.universal-robots.com/media/1807465/ur5e_e-series_datasheets_web.pdf'
ARMS={
 'ur5e':dict(name='Universal Robots UR5e (baseline)',speeds_degps=[180.]*6,payload_kg=5.,com_radius_m=.35,
  speeds_source='M: UR5e datasheet, 180 deg/s all joints',payload_source=UR_ENV_SOURCE),
 'fr5':dict(name='Fairino FR5 (stock J6 +-175 deg)',model='fr5',j6_deg=175.,speeds_degps=[180.]*6,payload_kg=5.,com_radius_m=.30,
  speeds_source='M: fairino.us FR5 page, 180 deg/s all joints (URDF/joint_limits.yaml: 3.15 rad/s J1-J3, 3.2 rad/s J4-J6 = 180.5/183.3 deg/s; the lower datasheet value is used)',
  payload_source='M: Fairino Cobots manual 3.4.5.2.5, Figure 3.4-19 FR5 load curve: 5 kg rated at <= 300 mm CoG offset from the flange centre (full performance); https://fairino-doc-en.readthedocs.io/latest/CobotsManual/installation.html',
  mount_yaw_deg=77.,clock_deg=90.),
 'fr5_j6':dict(name='Fairino FR5 with the optional J6 +-360 deg',model='fr5',j6_deg=360.,speeds_degps=[180.]*6,payload_kg=5.,com_radius_m=.30,
  speeds_source='as fr5',payload_source='as fr5',j6_source='M: fairino.us FR5 page "Wrist3 +-175 deg (Optional +-360 deg)"',mount_yaw_deg=77.,clock_deg=90.),
 'cs66':dict(name='Elite Robots CS66',model='cs66',j6_deg=360.,speeds_degps=[150.,150.,180.,180.,180.,180.],payload_kg=6.,com_radius_m=.15,
  speeds_source='M, conflicting: datasheet J1-J2 150, J3 180, J4-J6 230 deg/s; URDF joint_limits.yaml 180 all; the lower of the two per joint is used',
  payload_source='E: 6 kg rated (M, CS66 datasheet); the allowed CoG offset is ND (no CS66 payload diagram found); 0.15 m assumed, below the FR5 published 0.30 m and the UR5e file 0.35 m, so the wrist envelopes are on the strict side',
  mount_yaw_deg=0.,clock_deg=0.),
 'ur5e_enc':dict(name='Universal Robots UR5e, collision geoms enclosing the Menagerie visual meshes (R19 #12)',speeds_degps=[180.]*6,payload_kg=5.,com_radius_m=.35,
  speeds_source='as ur5e',payload_source=UR_ENV_SOURCE,enclose='r19/arm_ur5e_enc.json'),
 'ur5e_enc2':dict(name='Universal Robots UR5e, convex collision pieces enclosing the Menagerie visual meshes (R19 #12, tighter)',speeds_degps=[180.]*6,payload_kg=5.,com_radius_m=.35,
  speeds_source='as ur5e',payload_source=UR_ENV_SOURCE,enclose='r19/arm_ur5e_enc2.json'),
 'ur5e_enc2_pgc':dict(name='ur5e_enc2 with the PGC-140-50 housing as drawn by DH (round body, R19 #12) instead of the 75 mm box',speeds_degps=[180.]*6,payload_kg=5.,com_radius_m=.35,
  speeds_source='as ur5e',payload_source=UR_ENV_SOURCE,enclose='r19/arm_ur5e_enc2.json',oem='pgc_drawing',
  oem_source='M: DH PGC-140 Short Manual v2.1, Fig. 1.3(a) (Dimension drawing): Ø75 body, 98 mm body height, 53 mm across the jaw plane over the top 46 mm, 73 mm finger span, 36.4 mm, 138.5 mm overall; https://uploads.unchainedrobotics.de/media/file_upload/PGC-140-Short-Manual_v2.1_e46a3c6b.pdf')}
# R19 #2 (like-for-like with ur5e_enc2_pgc): the vendor-mesh arms with the PGC-140 housing from DH's drawing instead of the box;
# the arm, its limits, speeds and torque envelope (env) are those of the base option
for _b in ('fr5','fr5_j6','cs66'):
 ARMS[_b+'_pgc']=dict(ARMS[_b],name=ARMS[_b]['name']+' + PGC-140 housing from the DH drawing',env=_b,oem='pgc_drawing',oem_source=ARMS['ur5e_enc2_pgc']['oem_source'])
for _b in ('fr5','fr5_j6'):   # R19 #2 design proposal (E): the same gripper on a flange adapter 20 mm longer along the flange axis (the wrist-1 housing / PGC pair)
 ARMS[_b+'_pgc_sp20']=dict(ARMS[_b+'_pgc'],name=ARMS[_b+'_pgc']['name']+' on a 20 mm longer adapter',tool_spacer_m=.02)
# R19 #36: + the PGC-140 cable outlet (boot) and the first part of its cable (r19cable.py, R19_CABLE.md); everything else as the base
# option. <base>c = the conservative default routing both_dn (boot on both jaw sides: the side is a mounting choice); <base>c_<routing>
# = one routing (r19cable.ROUTINGS); <base>c_ALL / <base>c_SEL = several routings at once, screening models only (never a certificate)
import r19cable as _cab
for _b in ('ur5e_enc2_pgc','fr5_j6_pgc_sp20'):
 ARMS[_b+'c']=dict(ARMS[_b],name=ARMS[_b]['name']+' + cable outlet and first cable section (both jaw sides, R50 bend down)',cable='both_dn',cable_source='R19_CABLE.md section 1')
 for _r in list(_cab.ROUTINGS)+list(_cab.SCREENS):ARMS[_b+'c_'+_r]=dict(ARMS[_b],name=ARMS[_b]['name']+' + cable, routing '+_r,cable=_r,cable_source='R19_CABLE.md section 1')
# R19 #42 (r19mount.py, R19_MOUNT.md): buildable gripper mounts. <base>_<k> = the base option with the gripper re-posed on the flange
# as r19mount.MOUNTS[k] and the modelled bracket on R_tool (its mass in R_tool's inertial); the FR5 ones start from fr5_j6_pgc
# (no spacer: the bracket replaces the sp20 plate). Everything else as the base option.
import r19mount as _mnt
for _k in _mnt.MOUNTS:
 for _b in ('ur5e_enc2_pgc','fr5_j6_pgc'):ARMS[_b+'_'+_k]=dict(ARMS[_b],name=ARMS[_b]['name']+', mount '+_k+': '+_mnt.MOUNTS[_k]['label'],mount=_k,mount_source='r19mount.py, R19_MOUNT.md')
def _cli():
 for a in sys.argv[1:]:
  if a.startswith('ARM='):return a[4:]
 return os.environ.get('ARM')
def current(cfg=None):
 """The arm id: cfg['arm'], else ARM=<id> on the command line, else $ARM, else ur5e."""
 a=(cfg or {}).get('arm') or _cli() or 'ur5e'
 if a not in ARMS:raise ValueError(f'unknown arm {a!r}; known: {sorted(ARMS)}')
 return a
def tag(arm=None):
 """'' for the UR5e, '_<id>' otherwise (appended to output names so no UR5e result is overwritten)."""
 arm=arm or current();return '' if arm=='ur5e' else '_'+arm
def speeds(arm=None):return list(ARMS[arm or current()]['speeds_degps'])
def envelope_file(tilt,arm=None):
 arm=arm or current();return f'assets/envelope_{int(tilt)}.json' if arm=='ur5e' or ARMS[arm].get('enclose') else f"assets/envelope_{ARMS[arm].get('env',arm)}_{int(tilt)}.json"   # ur5e_enc: the UR5e envelope (same arm)
def fmt(v):return ' '.join(f'{float(x):.12g}' for x in v)
def quat(R):return Rotation.from_matrix(R).as_quat()[[3,0,1,2]]
def T(p,R):X=np.eye(4);X[:3,:3]=R;X[:3,3]=p;return X
def _pose(el):
 p=np.fromstring(el.get('pos','0 0 0'),sep=' ');q=np.fromstring(el.get('quat','1 0 0 0'),sep=' ')
 return T(p,Rotation.from_quat(q[[1,2,3,0]]/np.linalg.norm(q)).as_matrix())
JOINTS=['R_shoulder_pan_joint','R_shoulder_lift_joint','R_elbow_joint','R_wrist_1_joint','R_wrist_2_joint','R_wrist_3_joint']
BODIES=['R_arm_shoulder_link','R_arm_upper_arm_link','R_arm_forearm_link','R_arm_wrist_1_link','R_arm_wrist_2_link','R_arm_wrist_3_link']
def enclose(tree,arm):
 """ur5e_enc: the UR5e bodies, joints, inertials and site stay; its collision geoms R_geom_5..28 get the fitted
 type / pos / quat / size, and the added ones (R_geom_enc_*) are put on their bodies with the same contact settings."""
 J=json.loads((H/ARMS[arm]['enclose']).read_text(encoding='utf-8'));G=J['geoms']
 for nm in J.get('remove',[]):   # ur5e_enc2: the Menagerie geoms go, the convex pieces replace them
  for b in tree.iter('body'):
   for g in list(b):
    if g.tag=='geom' and g.get('name')==nm:b.remove(g)
 for g in G:
  el=tree.find(f".//geom[@name='{g['name']}']")
  if el is None:el=E.SubElement(tree.find(f".//body[@name='{g['body']}']"),'geom',name=g['name'],contype='2',conaffinity='3',margin='.01',group='3')
  if g['type']=='mesh':   # a convex piece (MuJoCo collides meshes as their convex hull, which these are)
   E.SubElement(tree.getroot().find('asset'),'mesh',name='M_'+g['name'],vertex=' '.join(fmt(v) for v in g['vertices']));el.set('type','mesh');el.set('mesh','M_'+g['name']);continue
  el.set('type',g['type']);el.set('pos',fmt(g['pos']));el.set('quat',fmt(g['quat']));el.set('size',fmt(g['size']))
 return tree
def swap(tree,arm):
 """Replace the UR5e under R_mount by `arm` (in place). R_tool keeps its pose relative to the flange."""
 if ARMS[arm].get('mount'):_mnt.apply(tree,ARMS[arm]['mount'])   # R19 #42: re-pose R_tool on the UR5e flange + the bracket, before the swap below carries it over
 if ARMS[arm].get('cable'):_cab.add(tree,ARMS[arm]['cable'],arm)   # R19 #36: cable shapes on R_tool (they move with it below); arm: the tool connector of the '_tc' routings
 if ARMS[arm].get('enclose'):return enclose(tree,arm)
 spec=ARMS[arm];M=json.loads((H/'r19'/f"arm_{spec['model']}.json").read_text(encoding='utf-8'))
 mount=tree.find(".//body[@name='R_mount']");old=mount.find("body[@name='R_arm_base']")
 w3=old.find(".//body[@name='R_arm_wrist_3_link']");site=w3.find("site[@name='R_attachment_site']");tool=w3.find("body[@name='R_tool']")
 site_tool=np.linalg.inv(_pose(site))@_pose(tool)   # UR5e: DH frame 6 (= R_attachment_site) -> gripper
 idx=list(mount).index(old);mount.remove(old)
 asset=tree.getroot().find('asset')
 if asset.find(f"mesh[@name='R_{arm}_base']") is None:E.SubElement(asset,'mesh',name=f'R_{arm}_base',file=M['base_mesh'])
 base=E.Element('body',name='R_arm_base',quat=fmt(quat(Rotation.from_euler('z',spec['mount_yaw_deg'],degrees=True).as_matrix())),childclass='R_ur5e')
 mount.insert(idx,base)
 links={l['link']:l for l in M['links']};J=M['joints']
 def inertial(b,l):
  E.SubElement(b,'inertial',pos=fmt(l['com']),mass=f"{l['mass']:.12g}",fullinertia=fmt(l['inertia_full']))
 def caps(b,l,lname):
  for c in l.get('capsules',[]):
   E.SubElement(b,'geom',name=f"R_geom_{arm}_{lname}_{c['name']}",type=c.get('type','capsule'),fromto=fmt(c['fromto']),size=f"{c['radius']:.6g}",group='3',contype='2',conaffinity='3',margin='.01',mass='0',rgba='.85 .87 .9 1')
 inertial(base,links[J[0]['parent']])
 E.SubElement(base,'geom',name=f'R_geom_{arm}_base',type='mesh',mesh=f'R_{arm}_base',contype='2',conaffinity='3',margin='.01',mass='0',rgba='.85 .87 .9 1')
 parent=base
 lim=[np.radians(j['datasheet_limit_deg']) for j in J]
 lim[5]=np.radians([-spec['j6_deg'],spec['j6_deg']])
 for k,j in enumerate(J):
  b=E.SubElement(parent,'body',name=BODIES[k],pos=fmt(j['xyz']),quat=fmt(quat(Rotation.from_euler('xyz',j['rpy']).as_matrix())))
  inertial(b,links[j['child']])
  E.SubElement(b,'joint',name=JOINTS[k],axis=fmt(j['axis']),range=fmt(lim[k]))
  caps(b,links[j['child']],j['child'].replace('_link',''))
  parent=b
 fl=np.array(M['flange']['xyz'],float)
 E.SubElement(parent,'site',name='R_attachment_site',pos=fmt(fl),quat='1 0 0 0')
 X=T(fl+[0,0,spec.get('tool_spacer_m',0.)],np.eye(3))@T(np.zeros(3),Rotation.from_euler('z',spec['clock_deg'],degrees=True).as_matrix())@site_tool   # R19 #2: optional adapter spacer along the flange axis
 tool.set('pos',fmt(X[:3,3]));tool.set('quat',fmt(quat(X[:3,:3])));parent.append(tool)
 return tree
