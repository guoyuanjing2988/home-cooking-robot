"""R19 #36 part 2: free-space map around the gripper for routing the cable to the tool connector (new file).
For every state of a set (the same scenes and <= 4 mm states as r19cable_check.py, run through its own ctx / state code),
the distance from each voxel of a grid fixed in the housing frame H (r19cable.py; 6 mm voxels) to
 env   every environment geom the checker pairs with the cable (Bounds.pairs, categories robot_environment /
       held_gripper_environment), and (stir) the r 0.20 m plume cylinder;
 self  every robot geom the checker pairs with the cable in the 'self' category (wrist 1 / 2, forearm, ..., cart);
and, once, held = the robot geoms on R_tool that are not the housing / palm / cable (the held object; fixed in H).
The map keeps the minimum over the states (capped at 80 mm). Distances are lower bounds: exact for boxes, spheres,
capsules, cylinders and planes; for convex meshes the largest face-plane distance; ellipsoids as their bounding sphere.
A probe point p of radius r then clears every state by at least D(voxel of p) - r - VOX*sqrt(3)/2 (5.2 mm at 6 mm voxels); with
STRIDE=k only every k-th state is used (the states are <= 4 mm apart, so a further 2k mm should be allowed for).
python r19cable2_free.py <mode> <r19cable_check.py arguments> [STRIDE=1] -> results/r19/cable/free/<mode>_<name>.npz"""
import sys,os,json,time,math
sys.path.insert(0,'.')
import numpy as np
MODE=sys.argv[1];KV=dict(a.split('=',1) for a in sys.argv[2:] if '=' in a)
import r19cable_check as RC
VOX=float(KV.get('VOX',.006));LO=np.array([-.380,-.220,-.300]);HI=np.array([-.020,.220,.180]);CAP=.08   # VOX=.010 for a quick map
SHAPE=tuple(np.round((HI-LO)/VOX).astype(int)+1)
GRID=(np.stack(np.meshgrid(*[np.arange(n) for n in SHAPE],indexing='ij'),-1).reshape(-1,3)*VOX+LO)
_W={}
def _setup(key):
 key=tuple(key) if isinstance(key,list) else key
 if key in _W:return _W[key]
 import mujoco,re
 from scipy.spatial import ConvexHull
 c=RC.ctx(key);ch=c['ch'];m=ch.m
 cab={g for g in range(m.ngeom) if ch.gnames[g].startswith('R_pgc_cable')}
 env,slf={},{}
 for a,b,need,cat in ch.bounds.pairs:
  if (a in cab)==(b in cab):continue
  o=b if a in cab else a
  if cat=='self':slf[o]=min(slf.get(o,1e9),need)
  elif cat in ('robot_environment','held_gripper_environment'):env[o]=min(env.get(o,1e9),need)
 sh=np.array([float(x) for x in re.search(r'name="R_gripper_oem_envelope"[^>]*?pos="([^"]+)"',ch.xml).group(1).split()]) if re.search(r'name="R_gripper_oem_envelope"[^>]*?pos="',ch.xml) else np.zeros(3)
 planes={}
 for g in set(env)|set(slf):
  if m.geom_type[g]==7:
   a_,k=m.mesh_vertadr[m.geom_dataid[g]],m.mesh_vertnum[m.geom_dataid[g]];planes[g]=ConvexHull(m.mesh_vert[a_:a_+k]).equations
 tb=m.body('R_tool').id
 held=[g for g in range(m.ngeom) if ch.robot[g] and m.geom_bodyid[g]==tb and not ch.gnames[g].startswith(('R_gripper_oem','R_pgc_cable')) and ch.gnames[g]!='R_gripper_palm']
 for g in held:
  if m.geom_type[g]==7 and g not in planes:
   a_,k=m.mesh_vertadr[m.geom_dataid[g]],m.mesh_vertnum[m.geom_dataid[g]];planes[g]=ConvexHull(m.mesh_vert[a_:a_+k]).equations
 plume=None
 if MODE=='stir':
  import r19stir_cycle as SC,kitchen15 as K15
  plume=(np.array(K15.WOK0[:2],float),float(SC.PLUME),float(K15.RIM_Z),1.25)
 _W[key]=dict(c=c,env=sorted(env),slf=sorted(slf),planes=planes,sh=sh,tb=tb,held=held,plume=plume);return _W[key]
def _dist(m,d,g,P,planes):
 """lower bound of the distance from points P (world, n x 3) to geom g (signed: negative inside)."""
 t=m.geom_type[g];R=d.geom_xmat[g].reshape(3,3);L=(P-d.geom_xpos[g])@R;s=m.geom_size[g]
 if t==6:q=np.abs(L)-s;return np.linalg.norm(np.maximum(q,0),axis=1)+np.minimum(q.max(1),0)
 if t==2:return np.linalg.norm(L,axis=1)-s[0]
 if t==3:z=np.clip(L[:,2],-s[1],s[1]);return np.sqrt(L[:,0]**2+L[:,1]**2+(L[:,2]-z)**2)-s[0]
 if t==5:
  rr=np.hypot(L[:,0],L[:,1])-s[0];zz=np.abs(L[:,2])-s[1]
  return np.hypot(np.maximum(rr,0),np.maximum(zz,0))+np.minimum(np.maximum(rr,zz),0)
 if t==4:return np.linalg.norm(L,axis=1)-s.max()
 if t==0:return L[:,2]
 if t==7:E=planes[g];return (L@E[:,:3].T+E[:,3]).max(1)
 return np.full(len(P),-1.)   # unknown type: treated as occupied
def _block(m,d,g,orgH,RH):
 """voxel index ranges of the grid that lie within CAP of geom g's world AABB (planes: everything)."""
 if m.geom_type[g]==0:return [(0,n) for n in SHAPE]
 c=d.geom_xpos[g];R=d.geom_xmat[g].reshape(3,3);e=m.geom_aabb[g]
 C=np.array([[sx,sy,sz] for sx in (-1,1) for sy in (-1,1) for sz in (-1,1)])*e[3:]+e[:3];W=C@R.T+c;H=(W-orgH)@RH
 lo=np.floor((H.min(0)-CAP-LO)/VOX).astype(int);hi=np.ceil((H.max(0)+CAP-LO)/VOX).astype(int)+1
 return [(max(0,a),min(n,b)) for a,b,n in zip(lo,hi,SHAPE)]
def work(args):
 key,Q=args;W=_setup(key);ch=W['c']['ch'];m,d=ch.m,ch.d
 import mujoco
 De=np.full(SHAPE,CAP,np.float32);Ds=np.full(SHAPE,CAP,np.float32);Dh=None
 G3=GRID.reshape(SHAPE+(3,))
 for q in Q:
  d.qpos[:]=q;mujoco.mj_kinematics(m,d)
  RH=d.xmat[W['tb']].reshape(3,3);orgH=d.xpos[W['tb']]+RH@W['sh']
  for gs,D in ((W['env'],De),(W['slf'],Ds)):
   for g in gs:
    (a0,a1),(b0,b1),(c0,c1)=_block(m,d,g,orgH,RH)
    if a0>=a1 or b0>=b1 or c0>=c1:continue
    P=G3[a0:a1,b0:b1,c0:c1].reshape(-1,3)@RH.T+orgH;v=_dist(m,d,g,P,W['planes']).reshape(a1-a0,b1-b0,c1-c0)
    np.minimum(D[a0:a1,b0:b1,c0:c1],v,out=D[a0:a1,b0:b1,c0:c1])
  if W['plume'] is not None:
   xy,r,z0,z1=W['plume'];P=GRID@RH.T+orgH;rr=np.hypot(P[:,0]-xy[0],P[:,1]-xy[1])-r;zz=np.maximum(z0-P[:,2],P[:,2]-z1)
   v=(np.hypot(np.maximum(rr,0),np.maximum(zz,0))+np.minimum(np.maximum(rr,zz),0)).reshape(SHAPE);np.minimum(De,v,out=De)
  if Dh is None and W['held']:
   Dh=np.full(SHAPE,CAP,np.float32)
   for g in W['held']:
    (a0,a1),(b0,b1),(c0,c1)=_block(m,d,g,orgH,RH)
    if a0>=a1 or b0>=b1 or c0>=c1:continue
    P=G3[a0:a1,b0:b1,c0:c1].reshape(-1,3)@RH.T+orgH;v=_dist(m,d,g,P,W['planes']).reshape(a1-a0,b1-b0,c1-c0);np.minimum(Dh[a0:a1,b0:b1,c0:c1],v,out=Dh[a0:a1,b0:b1,c0:c1])
 return De,Ds,Dh
def main():
 import multiprocessing as mp,r19smooth as S,glob
 W_=int(KV.get('WORKERS',20));ST=int(KV.get('STRIDE',1));t0=time.monotonic();parts={}
 if MODE=='chains':
  for f in KV['FILES'].split(','):
   r=json.load(open(f));parts[f'{os.path.basename(f)[:-5]}:play']=((f,'play'),None)
   for k,a in enumerate(r['approach_qs']):
    if a:parts[f'{os.path.basename(f)[:-5]}:app{k}']=((f,f'app{k}'),None)
  name='_'.join(os.path.basename(f)[:-5] for f in KV['FILES'].split(','))[:120]
 elif MODE=='hub':
  from r19smooth import unwrap
  D=KV['DIR'];E_=[e for e in KV.get('EDGES','').split(',') if e] or sorted(os.path.basename(f)[5:-5] for f in glob.glob(f'{D}/edge_*.json'))
  parts={e:('hub',unwrap(json.load(open(f'{D}/edge_{e}.json'))['qs'])) for e in E_};name=KV.get('TAG','hub')
 elif MODE=='prep':
  R=json.load(open(KV['FILE']));parts={'play':('play',R['play'])}
  for i,aq in enumerate(R.get('approach_qs') or []):
   if aq:parts[f'app{i}']=(['app',i],aq)
  name=os.path.basename(KV['FILE'])[:-5]
 elif MODE=='stir':
  L=json.load(open(KV['LIB']));Q=np.array(L['states']['q'],float);k=np.array(L['states']['kinds']);sel=[p for p in KV.get('PARTS','').split(',') if p]
  parts={n:('stir',Q[k==n]) for n in dict.fromkeys(k) if not sel or n.startswith(tuple(sel))};name=os.path.basename(KV['LIB'])[:-5]+('_'+'_'.join(sel) if sel else '')
 jobs=[];n_st=0
 for p,(key,Q) in parts.items():
  if MODE=='chains':
   import r19pot_check as RP
   QS,_=RP.states(*key)
  elif MODE=='prep':
   RV=RC.prepmod();c=RC.ctx(tuple(key) if isinstance(key,list) else key)['ch'];QS,_=RV.densify(c,RV.unwrap(c,Q)[0] if key=='play' else np.array(Q,float))
  else:QS,_,_=S.sample_poly(np.asarray(Q,float),S.FastBound(RC.ctx(key)['ch']))
  QS=np.asarray(QS)[::ST];n_st+=len(QS);nn=max(10,math.ceil(len(QS)/(W_*2)))
  jobs+=[(list(key) if isinstance(key,tuple) else key,QS[i:i+nn].tolist()) for i in range(0,len(QS),nn)]
 print(name,'states',n_st,'jobs',len(jobs),flush=True)
 De=np.full(SHAPE,CAP,np.float32);Ds=De.copy();Dh=De.copy()
 with mp.Pool(W_) as pool:
  for e,s,h in pool.imap_unordered(work,jobs):
   np.minimum(De,e,out=De);np.minimum(Ds,s,out=Ds)
   if h is not None:np.minimum(Dh,h,out=Dh)
 os.makedirs('results/r19/cable/free',exist_ok=True);fn=f'results/r19/cable/free/{MODE}_{name}__{RC.ARM}.npz'
 np.savez_compressed(fn,De=De,Ds=Ds,Dh=Dh,lo=LO,vox=VOX,cap=CAP,states=n_st,stride=ST,options=json.dumps(KV))
 print('saved',fn,'elapsed',round(time.monotonic()-t0),'s','free voxels (env>=20mm & self>=10mm):',int(((De>=.02)&(Ds>=.01)).sum()),'of',De.size,flush=True)
if __name__=='__main__':main()
