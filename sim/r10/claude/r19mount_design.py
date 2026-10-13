"""R19 #42: design search for a buildable gripper mount (new file; reads only, writes results/r19/mount/design*.json).

For each arm (ur5e_enc2_pgc: the k-DOP wrist-3 hulls; fr5_j6_pgc: the FR5 wrist-3 cylinder) the wrist-3 collision geoms
are taken from the built scene into the UR flange convention (r19mount.py: F, u = +x_F, the side the gripper base sits on;
the FR5 geoms are turned back by its clock_deg). A candidate mount (r19mount.MOUNTS format) moves the housing pieces
(R_gripper_oem_*, R_gripper_palm, as built) rigidly and adds the bracket pieces. Gate: every housing piece and the bracket
body >= 5 mm from every wrist-3 geom (the gripper / held gate); the mating boss is reported, exempt (bolted mating face).
Distances: mj_geomDistance (signed) in a small model holding only these geoms, with distmax 10 mm (with 0.2 m it is badly
wrong for these meshes: -38 mm reported for a pair 5.8 mm apart; with 10 mm it equals the exact GJK value, "10" = 10 or
more), and distance.Bounds.pair (the checker's GJK lower bound, >= 0, exact for separated convex pairs) as the gate value.
Gate also: no bracket piece (except the boss) may enter the housing (mj_geomDistance >= -0.1 mm: touching at the face only).
Searches (TCP change = the rigid motion applied to the current TCP; rotation = rot_deg), each over candidates in order of
|TCP change| until the first valid one, mj_geomDistance only, then the found one re-evaluated with the GJK bound:
 C1 L      same tilt and offset, move along the flange axis only, offset L bracket (arm plate over wrist 3 + a leg to the
           gripper support), u_arm 50-65 mm (PART=L; PART=Lfine: 1 mm steps);
 C4 L      the same with a radial move too (du 0-60 mm, dz -20-120 mm, 2.5 mm grid) (PART=L);
 C1/C4 single block: the bracket as one convex block (hull of the boss top and the support plate) (PART=hull);
 C2 wedge  same tilt, face centre (cu, h) on a wedge over the flange; buildability: face low edge >= WALL above the
           flange face, robot-side M6 counterbores (PCD 50 at +-45 deg) under >= SCREW_H of material (PART=wedge);
 C3 inline gripper axis on J6 (turned 26.6 deg), DH flange on an ISO 50 spacer (PART=inline);
 the r19mount.MOUNTS entries as they stand (PART=mounts).
python r19mount_design.py [STEP=.0025] [PART=all|L|Lfine|hull|wedge|inline|mounts] [FRESH=1] -> results/r19/mount/design[_<PART>].json
(the wrist-3 / housing geometry is cached in results/r19/mount/geo_cache.pkl; FRESH=1 rebuilds it)"""
import sys,os,json,time
sys.path.insert(0,'.')
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
import numpy as np,mujoco,xml.etree.ElementTree as E
from scipy.spatial.transform import Rotation
import r19mount as MT
from distance import Bounds
GATE=.005;SCREW_H=.012;STEP=float(KV.get('STEP',.0025))
def fmt(v):return ' '.join(f'{float(x):.12g}' for x in v)
def scene(arm):
 os.environ['ARM']=arm
 import chain,kitchen16 as K,arms
 from scene import build
 K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.)
 cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None},arm=arm)
 tree,meta=build(cfg,None);m=mujoco.MjModel.from_xml_string(E.tostring(tree.getroot(),encoding='unicode'));d=mujoco.MjData(m);mujoco.mj_kinematics(m,d)
 return tree,m,d,arms.ARMS[arm]
def geoms_F(m,d,body,C):
 """collision geoms of a body in the UR flange convention: list of dict(name,type,size,pos,R,verts)"""
 fl=m.site('R_attachment_site').id;Rf=d.site_xmat[fl].reshape(3,3);pf=d.site_xpos[fl];b=m.body(body).id;out=[]
 for g in range(m.ngeom):
  if m.geom_bodyid[g]!=b or (m.geom_contype[g]==0 and m.geom_conaffinity[g]==0):continue
  R=C.T@Rf.T@d.geom_xmat[g].reshape(3,3);p=C.T@Rf.T@(d.geom_xpos[g]-pf);row=dict(name=m.geom(g).name,type=int(m.geom_type[g]),size=m.geom_size[g].copy(),pos=p,R=R)
  if m.geom_type[g]==mujoco.mjtGeom.mjGEOM_MESH:
   mid=m.geom_dataid[g];a=m.mesh_vertadr[mid];row['verts']=p+m.mesh_vert[a:a+m.mesh_vertnum[mid]].astype(float)@R.T
  out.append(row)
 return out
def housing_tool(m,d):
 """housing pieces (vertices in the tool frame) of the built model"""
 tb=m.body('R_tool').id;Rt=d.xmat[tb].reshape(3,3);pt=d.xpos[tb];out={}
 for g in range(m.ngeom):
  n=m.geom(g).name
  if m.geom_bodyid[g]!=tb or not (n.startswith('R_gripper_oem') or n=='R_gripper_palm') or m.geom_type[g]!=mujoco.mjtGeom.mjGEOM_MESH:continue
  mid=m.geom_dataid[g];a=m.mesh_vertadr[mid];W=d.geom_xpos[g]+m.mesh_vert[a:a+m.mesh_vertnum[mid]].astype(float)@d.geom_xmat[g].reshape(3,3).T
  out[n]=(W-pt)@Rt
 return out
def mini(fixed,pieces):
 """small model: fixed geoms (from geoms_F) + convex pieces {name: verts F}; returns (m, d, ids_fixed, ids_pieces)"""
 asset=[];body=[]
 for f in fixed:
  q=fmt(Rotation.from_matrix(f['R']).as_quat()[[3,0,1,2]])
  if f['type']==mujoco.mjtGeom.mjGEOM_MESH:
   asset.append(f'<mesh name="m_{f["name"]}" vertex="{fmt(f["verts"].ravel())}"/>');body.append(f'<geom name="{f["name"]}" type="mesh" mesh="m_{f["name"]}" contype="0" conaffinity="0"/>')
  else:
   tn={mujoco.mjtGeom.mjGEOM_CYLINDER:'cylinder',mujoco.mjtGeom.mjGEOM_CAPSULE:'capsule',mujoco.mjtGeom.mjGEOM_BOX:'box',mujoco.mjtGeom.mjGEOM_SPHERE:'sphere'}[f['type']]
   sz=f['size'][:{'cylinder':2,'capsule':2,'box':3,'sphere':1}[tn]]
   body.append(f'<geom name="{f["name"]}" type="{tn}" size="{fmt(sz)}" pos="{fmt(f["pos"])}" quat="{q}" contype="0" conaffinity="0"/>')
 for n,V in pieces.items():
  asset.append(f'<mesh name="m_{n}" vertex="{fmt(np.asarray(V).ravel())}"/>');body.append(f'<geom name="{n}" type="mesh" mesh="m_{n}" contype="0" conaffinity="0"/>')
 xml='<mujoco><asset>'+''.join(asset)+'</asset><worldbody>'+''.join(body)+'</worldbody></mujoco>'
 m=mujoco.MjModel.from_xml_string(xml);d=mujoco.MjData(m);mujoco.mj_forward(m,d)
 return m,d,[m.geom(f['name']).id for f in fixed],{n:m.geom(n).id for n in pieces}
def bounds(m,d):
 """a distance.Bounds for pair() only (its support functions; no pair list)"""
 from scipy.spatial import ConvexHull
 B=Bounds.__new__(Bounds);B.m=m;B.d=d;B.local={}
 for g in range(m.ngeom):
  if m.geom_type[g]==mujoco.mjtGeom.mjGEOM_MESH:
   mid=m.geom_dataid[g];a=m.mesh_vertadr[mid];v=m.mesh_vert[a:a+m.mesh_vertnum[mid]].astype(float);B.local[g]=v[ConvexHull(v).vertices]
 return B
DISTMAX=.01   # mj_geomDistance is exact only inside a small distmax here (it inflates both shapes by distmax and takes an MPR
              # depth: with 0.2 m it reported -38 mm for a pair 5.8 mm apart); 10 mm = "10 or more"
def clearance(fixed,pieces,gjk=True):
 """per piece: min signed mj_geomDistance (distmax 10 mm) and min Bounds GJK lower bound (mm) to the fixed geoms; the gate
 value 'mm' = the GJK lower bound when the pair is separated (exact convex distance), else the mj_geomDistance depth"""
 m,d,fi,pi=mini(fixed,pieces);B=bounds(m,d);out={}
 for n,g in pi.items():
  best=None
  for f in fi:
   s=mujoco.mj_geomDistance(m,d,g,f,DISTMAX,None);lb=B.pair(g,f)['lower_m'] if gjk else s;v=lb if s>0 else s
   if best is None or v<best[0]:best=(v,s,lb,m.geom(f).name)
  out[n]=dict(mm=round(best[0]*1e3,2),mj_signed_mm=round(best[1]*1e3,2),gjk_lower_mm=round(best[2]*1e3,2),vs=best[3])
 return out
def penetration(pieces):
 """deepest mj_geomDistance between the bracket pieces (except the boss) and the housing pieces (mm; >= -0.1 = touching only)"""
 m,d,_,pi=mini([],pieces);H=[pi[n] for n in pi if 'mount' not in n];v=min(mujoco.mj_geomDistance(m,d,pi[b],h,DISTMAX,None) for b in pi if 'mount' in b and not b.endswith('base') for h in H)
 return round(v*1e3,2)
def evaluate(spec,base,arms_geo,gjk=True):
 """pieces of a candidate and its clearances on every arm; gate = min over housing pieces + bracket body."""
 X0_,c0,a0,tcp0=base['X'],base['c0'],base['a0'],base['tcp0']
 Dsc=MT.describe(spec,X0_,c0);Xn=Dsc['X'];pieces={n:V@Xn[:3,:3].T+Xn[:3,3] for n,V in base['housing'].items()}
 pieces.update(Dsc['parts']);res=dict(arms={})
 for arm,geo in arms_geo.items():
  cl=clearance(geo['w3'],pieces,gjk);gate=min(v['mm'] for n,v in cl.items() if not n.endswith('mount_base'))
  res['arms'][arm]=dict(gate_mm=gate,pieces=cl)
 res['body_vs_housing_mm']=penetration(pieces);res['gate_mm']=min(v['gate_mm'] for v in res['arms'].values())
 tcp=Xn[:3,3];res.update(tcp_change_mm=np.round((tcp-tcp0)*1e3,1).tolist(),tcp_change_norm_mm=round(float(np.linalg.norm(tcp-tcp0))*1e3,1),rot_deg=round(float(spec.get('rot_deg',0.)),2),
  face_centre_mm=np.round(Dsc['c']*1e3,1).tolist(),gripper_axis=np.round(Dsc['n'],4).tolist(),bracket_kg=round(Dsc['mass']['kg'],3),bracket_cog_F_mm=np.round(Dsc['mass']['cog_F']*1e3,1).tolist(),
  bracket_rows=Dsc['mass']['rows'])
 res['ok']=bool(res['gate_mm']>=GATE*1e3-1e-6 and res['body_vs_housing_mm']>=-.1)
 return res
def wedge_ok(c):
 """C2 buildability: face low edge >= WALL above the flange face; M6 counterbores at (+-17.7, +-17.7) under >= SCREW_H"""
 th=np.radians(MT.TILT0);cu,h=c;low=h-MT.R_GR*np.sin(th)
 zs=min(h+np.tan(th)*(u-cu) for u in (-.0177,.0177))
 return low>=MT.WALL-1e-9 and zs>=SCREW_H-1e-9,dict(face_low_edge_mm=round(low*1e3,1),screw_stack_mm=round(zs*1e3,1))
if __name__=='__main__':
 t0=time.monotonic();arms_geo={};PART=KV.get('PART','all');import pickle
 CACHE='results/r19/mount/geo_cache.pkl'
 if os.path.exists(CACHE) and KV.get('FRESH')!='1':arms_geo,base,sp20=pickle.load(open(CACHE,'rb'))
 for arm in (() if arms_geo else ('ur5e_enc2_pgc','fr5_j6_pgc','fr5_j6_pgc_sp20')):
  tree,m,d,spec=scene(arm);C=Rotation.from_euler('z',spec.get('clock_deg',0.),degrees=True).as_matrix()
  arms_geo[arm]=dict(w3=geoms_F(m,d,'R_arm_wrist_3_link',C))
  if arm=='ur5e_enc2_pgc':
   X0_,c0,a0,face_t=MT.current(tree);base=dict(X=X0_,c0=c0,a0=a0,tcp0=X0_[:3,3].copy(),housing=housing_tool(m,d))
  if arm=='fr5_j6_pgc_sp20':   # the current FR5 pose (for the record): housing as built vs its wrist 3
   fl=m.site('R_attachment_site').id;tb=m.body('R_tool').id;Rf=d.site_xmat[fl].reshape(3,3);pf=d.site_xpos[fl]
   Xs=np.eye(4);Xs[:3,:3]=C.T@Rf.T@d.xmat[tb].reshape(3,3);Xs[:3,3]=C.T@Rf.T@(d.xpos[tb]-pf);sp20=Xs
 os.makedirs('results/r19/mount',exist_ok=True);pickle.dump((arms_geo,base,sp20),open(CACHE,'wb'))
 fr=['ur5e_enc2_pgc','fr5_j6_pgc'];G={a:arms_geo[a] for a in fr}
 out=dict(method=__doc__,gate_mm=GATE*1e3,tilt0_deg=MT.TILT0,current=dict(tcp_F_mm=np.round(base['tcp0']*1e3,1).tolist(),face_centre_F_mm=np.round(base['c0']*1e3,1).tolist(),axis=np.round(base['a0'],4).tolist()))
 # the current pose on both arms (no bracket)
 cur=dict(arms={})
 for arm in fr:cur['arms'][arm]=clearance(G[arm]['w3'],{n:V@base['X'][:3,:3].T+base['X'][:3,3] for n,V in base['housing'].items()})
 cur['arms']['fr5_j6_pgc_sp20']=clearance(arms_geo['fr5_j6_pgc_sp20']['w3'],{n:V@sp20[:3,:3].T+sp20[:3,3] for n,V in base['housing'].items()})
 out['current']['clearance']=cur;print('current',json.dumps(cur)[:600],flush=True)
 def search(make,cands,label):
  """evaluate candidates in order of |TCP change| until the first valid one; returns (best spec, result, rows)"""
  rows=[]
  for key in sorted(cands,key=lambda k:k[0]):
   spec=make(*key[1:]);r=evaluate(spec,base,G,False)
   rows.append(dict(key=[round(float(x)*1e3,1) for x in key[1:]],tcp_change_norm_mm=r['tcp_change_norm_mm'],gate_mm=r['gate_mm'],ok=r['ok'],body_vs_housing_mm=r['body_vs_housing_mm']))
   if r['ok']:r=evaluate(spec,base,G);print(label,rows[-1],'GJK gate',r['gate_mm'],r['ok'],flush=True);return spec,r,rows
  print(label,'none',flush=True);return None,None,rows
 tcp_of=lambda spec:float(np.linalg.norm(MT.describe(spec,base['X'],base['c0'])['X'][:3,3]-base['tcp0']))
 S=STEP;U=np.arange(0,.0601,S);Z=np.arange(-.02,.1201,S);UA=(.050,.053,.056,.060,.065)
 Lmk=lambda du,dz,ua:dict(bracket='L',rot_deg=0.,dc=(du,dz),u_arm=ua,tf=MT.TF,pocket=True)
 Hmk=lambda du,dz:dict(bracket='hull',rot_deg=0.,dc=(du,dz),tf=MT.TF,pocket=True)
 out['C1_L']={};out['C4_L']={}
 for ua in (UA if PART in ('all','L') else ()):
  sp,r,rows=search(Lmk,[(abs(dz),0.,dz,ua) for dz in Z],f'C1 L u_arm {ua*1e3:.0f}');out['C1_L'][f'{ua*1e3:.0f}']=dict(spec=sp,result=r,rows=rows)
  sp,r,rows=search(Lmk,[(np.hypot(du,dz),du,dz,ua) for du in U for dz in Z],f'C4 L u_arm {ua*1e3:.0f}');out['C4_L'][f'{ua*1e3:.0f}']=dict(spec=sp,result=r,rows=rows)
 if PART=='Lfine':   # 1 mm refinement of C1 (L bracket, along the flange axis only)
  for ua in np.arange(.050,.0561,.001):
   sp,r,rows=search(Lmk,[(abs(dz),0.,dz,ua) for dz in np.arange(.065,.0851,.001)],f'C1 L fine u_arm {ua*1e3:.0f}');out['C1_L'][f'{ua*1e3:.0f}']=dict(spec=sp,result=r,rows=rows)
 if PART in ('all','hull'):
  sp,r,rows=search(Hmk,[(abs(dz),0.,dz) for dz in Z],'C1 single block');out['C1_hull']=dict(spec=sp,result=r,rows=rows)
  sp,r,rows=search(Hmk,[(np.hypot(du,dz),du,dz) for du in np.arange(-.08,.0601,S) for dz in Z],'C4 single block');out['C4_hull']=dict(spec=sp,result=r,rows=rows)
 # C2: wedge over the flange (single block, the face disc as its top)
 if PART in ('all','wedge'):
  W=[(tcp_of(dict(rot_deg=0.,c=(cu,h))),cu,h) for cu in np.arange(-.01,.0501,S) for h in np.arange(.015,.0701,S/2) if wedge_ok((cu,h))[0]]
  sp,r,rows=search(lambda cu,h:dict(bracket='hull',rot_deg=0.,c=(cu,h),tf=0.,pocket=False),W,'C2 wedge')
  out['C2']=dict(spec=sp,result=r,rows=rows,buildability=wedge_ok(sp['c'])[1] if sp else None)
 # C3: inline
 out['C3']={}
 for t in ((.0051,.008,.010) if PART in ('all','inline') else ()):
  r=evaluate(dict(bracket='spacer',rot_deg=MT.TILT0,c=(0.,t),tf=0.,face_r=MT.R_FL,pocket=False),base,G)
  out['C3'][f't{t*1e3:.0f}mm']=dict(gate_mm=r['gate_mm'],ok=r['ok'],tcp_change_mm=r['tcp_change_mm'],tcp_change_norm_mm=r['tcp_change_norm_mm'],arms={a:r['arms'][a]['gate_mm'] for a in fr},pieces={a:r['arms'][a]['pieces'] for a in fr})
 print('C3',{k:(v['gate_mm'],v['tcp_change_norm_mm']) for k,v in out['C3'].items()},flush=True)
 # the MOUNTS entries as they stand
 out['MOUNTS']={k:evaluate(s,base,G) for k,s in MT.MOUNTS.items()} if PART in ('all','mounts') else {}
 for k,v in out['MOUNTS'].items():print(k,'ok',v['ok'],'body/housing',v['body_vs_housing_mm'],'gate',v['gate_mm'],{a:v['arms'][a]['gate_mm'] for a in fr},'tcp',v['tcp_change_mm'],v['tcp_change_norm_mm'],'rot',v['rot_deg'],'kg',v['bracket_kg'],flush=True)
 os.makedirs('results/r19/mount',exist_ok=True);fn='results/r19/mount/design'+('' if PART=='all' else '_'+PART)+'.json'
 json.dump(out,open(fn,'w'),indent=1,default=lambda x:x.tolist() if isinstance(x,np.ndarray) else float(x));print(fn,'elapsed',round(time.monotonic()-t0),'s')
