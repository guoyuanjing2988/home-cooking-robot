"""R19 #12, second fit: ur5e_enc2, collision geoms that ENCLOSE the Menagerie visual meshes and follow them closely.

Why: ur5e_enc (r19ur5e_encfit.py) covers each joint housing with a cylinder on the joint axis, also over the
neighbour link (coaxial cover, rotation-invariant). The real housings are not bodies of revolution: the forearm's
elbow cap is a lopsided dome (r 68 mm toward +-x, 21-48 mm toward the upper arm side), the shoulder top has a
bump, the tubes flare into the housings on one side only. Any primitive on the joint axis must be revolved over
all of that, so ur5e_enc is up to 50 mm outside the real surface (bloat(), per link: shoulder 20, upper arm 20,
forearm 51, wrists 9-11 mm). Profile bands along the axis (tried first) did not help: the excess is around the
axis, not along it.

ur5e_enc2: every link is covered by convex polytopes on its OWN body only (no coaxial cover, so nothing is revolved):
 1. every point of the link's mesh (vertices + a <= 2 mm grid on every triangle) is given to the ur5e_enc primitive
    whose surface it lies nearest to among those that hold it (its own or the coaxial neighbour's): that splits
    the link into its housing / neck / tube / cap pieces, each inside one convex ur5e_enc primitive;
 2. a piece longer than SEG (60 mm) along its main axis is cut into <= SEG long parts (a whole tube's hull
    would bridge its flared ends: 15 mm bloat), neighbouring parts overlapping by 2 x OVL (4 mm); each part becomes a k-DOP: the intersection of NDIR (162) half-spaces n.x <= max over its points of n.x
    + MARGIN (0.3 mm), n on a Fibonacci sphere: a convex polytope at most a fraction of a mm outside the hull of
    the piece (and never outside the ur5e_enc primitive by more than MARGIN);
 3. proof of enclosure as in r19ur5e_encfit.certify (every triangle held by one polytope at its 3 corners, or its
    corners inside the union by its longest edge / sqrt(3), else split, to 1/2^10); points of parts that fail are
    added to the polytope of the nearest piece point (its half-spaces move out) until all triangles are certified;
 4. MuJoCo mesh geoms (convex) from the polytope vertices, names R_geom_enc2_<link>_<k>; the Menagerie geoms
    R_geom_5..28 are removed (arms.enclose, 'remove').
Polytopes give exact signed distances inside (max over the planes) and MuJoCo / distance.Bounds collide them as
convex meshes (mesh-box distances are exact in MuJoCo 3.2.5, R11; cylinders are not, R19_ARM_SWAP.md 7).

python r19ur5e_enc2fit.py [FROM=r19/arm_ur5e_enc.json] [NDIR=162] [MARGIN=.0003] -> r19/arm_ur5e_enc2.json (+ bloat of both)
Labels: M = Menagerie meshes, E = fitted here."""
import sys,json,math
import numpy as np,mujoco
from scipy.spatial import ConvexHull,HalfspaceIntersection,cKDTree
import r19ur5e_encfit as F
H=F.H;KV=F.KV
SRC=KV.get('FROM','r19/arm_ur5e_enc.json');DST=KV.get('OUT','r19/arm_ur5e_enc2.json')
SEG=float(KV.get('SEG',.06));OVL=float(KV.get('OVL',.004));NDIR=int(KV.get('NDIR',162));MARGIN=float(KV.get('MARGIN',.0003));STEP=float(KV.get('STEP',.002));DEPTH=int(KV.get('DEPTH',10))
SHORT={'shoulder_link':'sh','upper_arm_link':'ua','forearm_link':'fa','wrist_1_link':'w1','wrist_2_link':'w2','wrist_3_link':'w3'}
def fib(n):
 k=np.arange(n)+.5;phi=np.arccos(1-2*k/n);t=math.pi*(1+5**.5)*k
 return np.c_[np.cos(t)*np.sin(phi),np.sin(t)*np.sin(phi),np.cos(phi)]
DIRS=np.r_[np.eye(3),-np.eye(3),fib(NDIR)]
def sd(P,p):return (P@p['n'].T-p['d']).max(1)   # exact signed distance inside, a lower bound outside
def certify(T,polys,depth=DEPTH):
 """r19ur5e_encfit.certify for polytopes on the link's own frame."""
 st=dict(triangles=len(T),split_parts=0,levels=0,corner_outside=0);bad=[np.zeros((0,3))];badh=[np.zeros(0)]
 for lev in range(depth+1):
  if not len(T):break
  S=np.stack([sd(T.reshape(-1,3),p) for p in polys],1).reshape(len(T),3,-1);U=S.min(2)
  out=(U>0).any(1)
  if out.any():bad.append(T[out][U[out]>0]);badh.append(np.zeros(int((U[out]>0).sum())));st['corner_outside']+=int(out.sum())
  one=(S.max(1)<=0).any(1);a=np.max(np.linalg.norm(T-np.roll(T,1,axis=1),axis=2),axis=1);lip=U.max(1)+a/math.sqrt(3)<=0
  T=T[~(one|lip|out)];st['levels']=lev
  if lev==depth or not len(T):break
  M=(T+np.roll(T,-1,axis=1))/2
  T=np.concatenate([np.stack([T[:,0],M[:,0],M[:,2]],1),np.stack([M[:,0],T[:,1],M[:,1]],1),np.stack([M[:,2],M[:,1],T[:,2]],1),np.stack([M[:,0],M[:,1],M[:,2]],1)]);st['split_parts']+=len(T)
 if len(T):a=np.max(np.linalg.norm(T-np.roll(T,1,axis=1),axis=2),axis=1);bad.append(T.reshape(-1,3));badh.append(np.repeat(a/math.sqrt(3)+1e-7,3))
 st['uncertified']=int(len(T))+st['corner_outside'];return st,np.concatenate(bad),np.concatenate(badh)
def vertices(p):
 c=p['inside'];hs=HalfspaceIntersection(np.c_[p['n'],-(p['d']+1e-6)],c);V=hs.intersections;return V[ConvexHull(V).vertices]
def fit():
 m,_,tris,bodyT,parent,jaxis=F.load();old=F.from_json(SRC);out=[];report={}
 for L in F.NAMES:
  cand=F.candidates(L,old,bodyT,parent,jaxis);P=F.grid(tris[L],STEP)
  loc=F.to_frames(P,cand,old);S=np.stack([F.sdist(s_,r_,old[i]) for (s_,r_),(i,X) in zip(loc,cand)],1)
  assert S.min(1).max()<=1e-9,'the source fit does not hold every point'
  k=np.where(S<=1e-9,S,-np.inf).argmax(1);polys=[]
  used=np.zeros(len(P),bool)
  for kk,(i,X) in enumerate(cand):
   idx=np.nonzero(k==kk)[0]
   if len(idx)<20:continue   # a few stray points: taken by the growth below
   Q=P[idx];ax=np.linalg.eigh(np.cov((Q-Q.mean(0)).T))[1][:,-1];t=(Q-Q.mean(0))@ax;nseg=max(1,int(math.ceil((t.max()-t.min())/SEG)))
   edges=np.linspace(t.min(),t.max(),nseg+1)
   for sg in range(nseg):   # a long piece is cut along its main axis into <= SEG long parts (the hull of a whole tube bridges its flared ends)
    sel=(t>=edges[sg]-OVL)&(t<=edges[sg+1]+OVL)   # neighbouring parts overlap by 2*OVL, so a seam triangle sits inside one of them
    if sel.sum()<20:continue
    Qs=Q[sel];used[idx[sel]]=True
    polys.append(dict(body=L,src=old[i]['name'],n=DIRS,d=(Qs@DIRS.T).max(0)+MARGIN,inside=Qs.mean(0),points=int(len(Qs)),Q=Qs))
  rest=np.nonzero(~used)[0]
  pts,hh=P[rest],np.zeros(len(rest));rounds=[]
  lab=np.concatenate([np.full(len(p['Q']),j) for j,p in enumerate(polys)]);kd=cKDTree(np.concatenate([p['Q'] for p in polys]))
  for rnd in range(40):
   if len(pts):   # points outside: the polytope of the nearest piece point moves out to hold them (by their margin)
    Sx=np.stack([sd(pts,p) for p in polys],1);o=np.nonzero(Sx.min(1)+hh>1e-12)[0]
    if len(o):
     own_=lab[kd.query(pts[o])[1]]
     for j in np.unique(own_):
      sel=o[own_==j];polys[j]['d']=np.maximum(polys[j]['d'],(pts[sel]@DIRS.T+hh[sel,None]).max(0))
   st,bad,badh=certify(tris[L],polys);rounds.append(st['uncertified'])
   if not st['uncertified']:break
   pts,hh=np.r_[pts,bad],np.r_[hh,badh]
  else:raise RuntimeError(L+' not certified')
  for j,p in enumerate(polys):
   V=vertices(p);p.update(name=f"R_geom_enc2_{SHORT[L]}_{j}",V=V)
  out+=polys;report[L]=dict(pieces=len(polys),rounds=rounds,certificate=st,max_protrusion_mm=round(float(np.stack([sd(np.unique(tris[L].reshape(-1,3),axis=0),p) for p in polys],1).min(1).max())*1e3,3))
  print(L,report[L],[(p['name'],p['src'],p['points'],len(p['V'])) for p in polys],flush=True)
 return m,tris,out,report
def mesh_samples(T,step=.002):
 """points on every triangle (vertices + lattice <= step) with the triangle's outward normal (the Menagerie meshes
 are closed and outward: signed volumes 0.26-4.8 L, all positive)."""
 e1=T[:,1]-T[:,0];e2=T[:,2]-T[:,0];N=np.cross(e1,e2);N/=np.maximum(np.linalg.norm(N,axis=1),1e-15)[:,None]
 n1=np.maximum(1,np.ceil(np.linalg.norm(e1,axis=1)/step)).astype(int);n2=np.maximum(1,np.ceil(np.linalg.norm(e2,axis=1)/step)).astype(int);P=[];Q=[]
 for a,b in set(zip(n1.tolist(),n2.tolist())):
  sel=np.nonzero((n1==a)&(n2==b))[0];W=np.array([(i/a,j/b) for i in range(a+1) for j in range(b+1) if i*b+j*a<=a*b])
  P.append((T[sel,0][:,None,:]+W[:,0][None,:,None]*e1[sel][:,None,:]+W[:,1][None,:,None]*e2[sel][:,None,:]).reshape(-1,3));Q.append(np.repeat(N[sel],len(W),axis=0))
 return np.concatenate(P),np.concatenate(Q)
def solids_enc(fn,step=.002):
 out=[]
 for p in F.from_json(fn):out.append(dict(name=p['name'],body=p['body'],surf=F.surface(p,step),sd=(lambda X,p=p:F.sdist(*F.local(X,p),p))))
 return out
def solids_poly(polys,step=.002):
 out=[]
 for p in polys:
  hull=ConvexHull(p['V']);eq=hull.equations
  out.append(dict(name=p['name'],body=p['body'],surf=F.grid(p['V'][hull.simplices],step),sd=(lambda X,eq=eq:(X@eq[:,:3].T+eq[:,3]).max(1))))
 return out
def bloat(m,tris,solids):
 """How far the model is OUTSIDE the real arm: for every exposed point of the model surface (no other solid of the
 arm holds it) that lies outside the real arm (on the outward side of the nearest mesh triangle), its distance to the
 nearest point of the real surface (Menagerie meshes, vertices + 2 mm grid: can exceed the true distance by
 <= 1.7 mm). Exposed points inside the real arm (internal faces between pieces) are not bloat and are skipped.
 Arm at q = 0 (stretched) and at the Menagerie home pose; the larger value counts."""
 d=mujoco.MjData(m);bn=lambda b:mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_BODY,b);bid={bn(b):b for b in range(1,m.nbody)}
 MS={L:mesh_samples(T) for L,T in tris.items()};res={}
 for q in (np.zeros(6),np.array([-1.5708,-1.5708,1.5708,-1.5708,-1.5708,0])):
  d.qpos[:]=q;mujoco.mj_kinematics(m,d);Rb=lambda L:d.xmat[bid[L]].reshape(3,3);W=lambda L,X:d.xpos[bid[L]]+X@Rb(L).T
  Pw=np.concatenate([W(L,P) for L,(P,N) in MS.items()]);Nw=np.concatenate([N@Rb(L).T for L,(P,N) in MS.items()]);tree=cKDTree(Pw)
  for i,so in enumerate(solids):
   X=W(so['body'],so['surf']);keep=np.ones(len(X),bool)
   for j,o in enumerate(solids):
    if j!=i:keep&=o['sd']((X-d.xpos[bid[o['body']]])@Rb(o['body']))>-1e-6
   X=X[keep]
   if not len(X):continue
   dist,k=tree.query(X);outside=np.einsum('ij,ij->i',X-Pw[k],Nw[k])>0;v=res.setdefault(so['name'],dict(body=F.BODY[so['body']],max_mm=0.,p99_mm=0.))
   if outside.any():v['max_mm']=max(v['max_mm'],round(float(dist[outside].max())*1e3,1));v['p99_mm']=max(v['p99_mm'],round(float(np.percentile(dist[outside],99))*1e3,1))
 links={}
 for nm,v in res.items():
  o=links.setdefault(v['body'],dict(max_mm=0.,worst=None))
  if v['max_mm']>o['max_mm']:o.update(max_mm=v['max_mm'],worst=nm)
 return dict(method=bloat.__doc__,per_link=links,per_primitive=res)
def main():
 m,tris,polys,report=fit()
 before=bloat(m,tris,solids_enc(SRC));after=bloat(m,tris,solids_poly(polys))
 out=dict(id='ur5e_enc2',name='UR5e, convex polytopes enclosing the Menagerie visual meshes, own body only',source=SRC,seg_m=SEG,ndir=len(DIRS),margin_m=MARGIN,step_m=STEP,depth=DEPTH,method=__doc__,
  labels=dict(M='Menagerie ur5e.xml, assets/*.obj',E='fitted here'),remove=[n for v in F.NAMES.values() for n in v],
  geoms=[dict(name=p['name'],body=F.BODY[p['body']],type='mesh',vertices=np.round(p['V'],7).tolist(),from_piece_of=p['src'],points=p['points'],label='E (convex k-DOP of a piece of the M mesh)') for p in polys],
  enclosure=report,bloat_before_ur5e_enc=before,bloat_after=after)
 (H/DST).write_text(json.dumps(out,indent=1),encoding='utf-8');print(H/DST,'geoms',len(polys))
 for L in before['per_link']:print(f"{L:22s} bloat ur5e_enc {before['per_link'][L]['max_mm']:5.1f} mm -> ur5e_enc2 {after['per_link'].get(L,{}).get('max_mm')} mm ({after['per_link'].get(L,{}).get('worst')})")
if __name__=='__main__':
 if 'bloat' in sys.argv[1:]:   # re-measure the bloat of a stored ur5e_enc2 json (and ur5e_enc) without refitting
  m,_,tris,_,_,_=F.load();J=json.loads((H/DST).read_text(encoding='utf-8'))
  polys=[dict(name=g['name'],body=F.INV_BODY[g['body']],V=np.array(g['vertices'])) for g in J['geoms']]
  J['bloat_before_ur5e_enc']=bloat(m,tris,solids_enc(SRC));J['bloat_after']=bloat(m,tris,solids_poly(polys));(H/DST).write_text(json.dumps(J,indent=1),encoding='utf-8')
  for L,v in J['bloat_before_ur5e_enc']['per_link'].items():print(f"{L:22s} bloat ur5e_enc {v['max_mm']:5.1f} mm ({v['worst']}) -> ur5e_enc2 {J['bloat_after']['per_link'].get(L,{}).get('max_mm')} mm ({J['bloat_after']['per_link'].get(L,{}).get('worst')})")
 else:main()
