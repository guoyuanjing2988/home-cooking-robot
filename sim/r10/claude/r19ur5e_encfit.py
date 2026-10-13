"""R19 #12: UR5e collision geometry that ENCLOSES the MuJoCo Menagerie visual meshes (arm option ur5e_enc).

The sim's UR5e (models/base.xml, bodies R_arm_*) carries Menagerie's collision geoms R_geom_5 .. R_geom_28.
r19ur5e_enclose.py measured that the Menagerie visual meshes stick out of them by up to 26.5 mm (upper
arm). This script fits, from those same geoms (same bodies, same axes), primitives that contain every
point of the visual meshes, and writes r19/arm_ur5e_enc.json; arms.py (ARM=ur5e_enc) puts them on the
UR5e in place of the Menagerie geoms. Kinematics, masses, limits, speeds and the torque envelope are the
UR5e's, untouched.

Primitives (as r19arm_fit.py): the joint housings (Menagerie capsules R_geom_5/10/16/21/25/26, cylinder
R_geom_28) become CYLINDERS on the same axis (a capsule cap ending at a flat housing face either misses
the face's rim or, extended, sticks out up to its radius beyond it; R19_ARM_SWAP.md 7); the two tubes
(R_geom_11 upper arm, R_geom_17 forearm) stay CAPSULES on the same segment. Menagerie covers part of a link
with the housing geom of the NEIGHBOUR link on the shared joint axis (e.g. the upper arm's elbow housing by
the forearm's R_geom_16); such a coaxial primitive covers the same region at every joint angle, so a link's
points may be charged to it too (axis collinear with the joint axis to 1e-9, checked).

Start sizes (START) are read off the mesh profiles, as r19arm_fit.py does; four cylinders are added (EXTRA:
the three necks where a tube flares into its housing, and the shoulder's own part of the J2 housing, see NOCOVER).
Fit: (1) every point outside is charged to the candidate it is nearest to (RULE=distance, r19arm_fit.py's rule),
which grows to contain its points (cylinder: radius and either end; capsule: radius); repeat until none is
outside; (2) shrink: each primitive in turn shrinks to the points no other candidate holds; (3) rebalance: a
local search on the total volume (move one size inward by 8 .. 0.5 mm, give the freed points to the one other
primitive that grows least; keep the move if the volume drops), on a 20 % subset of the points; (4) certify
(below) and give the uncertified points back to step (1) until all is certified. Fit points: every mesh vertex
plus a grid of <= STEP (2 mm) on every triangle.
Proof of enclosure (not sampling): every triangle is certified when one convex primitive contains its
three corners (then it contains the triangle), or when every corner is inside the union by at least the
triangle's longest edge / sqrt(3) (every triangle point lies that close to a corner; the distance to the
union is 1-Lipschitz). Otherwise it is split in 4 and the parts are tested again, down to 1/2^DEPTH of the
edge; corners of parts still uncertified go back into the fit with that margin, until all are certified.
Radii and cylinder ends are finally moved out by 0.05 mm (rounding), as in r19arm_fit.py.

python r19ur5e_encfit.py [MEN=<menagerie universal_robots_ur5e dir>] [STEP=.002] [DEPTH=10]  -> r19/arm_ur5e_enc.json
Labels: M = Menagerie model files (ur5e.xml, assets/*.obj), E = derived here."""
import sys,json,math
from pathlib import Path
import numpy as np,mujoco
from scipy.spatial.transform import Rotation
H=Path(__file__).resolve().parent
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
MEN=Path(KV.get('MEN',H.parents[1]/'r01/concept/sources/menagerie/universal_robots_ur5e'))
STEP=float(KV.get('STEP',.002));DEPTH=int(KV.get('DEPTH',10));DELTA=float(KV.get('DELTA',1.));RULE=KV.get('RULE','distance')   # DELTA: max growth per round (1 m = none); RULE: charge an outside point to the primitive it is nearest to (distance, as r19arm_fit.py) or that grows least in volume (volume)
# Menagerie body -> sim body, and the Menagerie primitive order per body -> sim geom names (models/base.xml)
BODY={'shoulder_link':'R_arm_shoulder_link','upper_arm_link':'R_arm_upper_arm_link','forearm_link':'R_arm_forearm_link',
 'wrist_1_link':'R_arm_wrist_1_link','wrist_2_link':'R_arm_wrist_2_link','wrist_3_link':'R_arm_wrist_3_link'}
NAMES={'shoulder_link':['R_geom_5'],'upper_arm_link':['R_geom_10','R_geom_11'],'forearm_link':['R_geom_16','R_geom_17'],
 'wrist_1_link':['R_geom_21'],'wrist_2_link':['R_geom_25','R_geom_26'],'wrist_3_link':['R_geom_28']}
TUBES={'R_geom_11','R_geom_17'}   # stay capsules; the others are joint housings -> cylinders
# Start sizes (E, read off the mesh: per joint housing the axial span of the points of BOTH links on that
# axis and the radius on its far side; r19arm_fit.py reads its nominal sizes off the STL profiles the same
# way). The fit then grows them. Extent [s0, s1] along the Menagerie geom axis from the Menagerie centre.
START={'R_geom_5':(-.024,.1116,.0601),'R_geom_10':(-.1101,.0236,.0606),'R_geom_16':(-.1204,.1258,.0612),'R_geom_21':(-.04,.106,.040),
 'R_geom_25':(-.096,.025,.040),'R_geom_26':(-.033,.077,.040),'R_geom_28':(-.019,.027,.040)}
# Added (E): the necks where a tube flares into its joint housing (tube r 46 / 38 mm, neck r 58 / 54 mm),
# cylinders on the link axis (z). Without them the tube or the housing radius has to cover the flare.
# The shoulder's own part of the J2 housing (y 0 .. .074) gets its own cylinder on the shoulder body, and the
# upper arm's R_geom_10 may not cover the shoulder (NOCOVER): the shoulder sits on the base (mesh 1 mm apart), so a
# geom of the upper arm there would be checked against the base (upper arm and base are not adjacent), a contact
# the real arm cannot make (the first fit gave MuJoCo contacts R_geom_10 / base at -0.4 mm in 73 wok states).
EXTRA={'upper_arm_link':[('R_geom_enc_ua_neck_s',.03,.085,.0584),('R_geom_enc_ua_neck_e',.325,.39,.0585)],
 'forearm_link':[('R_geom_enc_fa_neck_e',.03,.095,.0536)],
 'shoulder_link':[('R_geom_enc_sh_j2',0.,.0745,.0606,'y')]}
NOCOVER={('shoulder_link','R_geom_10')}
def Rq(q):return Rotation.from_quat(np.r_[q[1:],q[0]]).as_matrix()
def TT(p,R):X=np.eye(4);X[:3,:3]=R;X[:3,3]=p;return X
def grid(T,step):
 """Vertices + lattice points (<= step along edges 0->1 and 0->2) + points along edge 1->2."""
 e1=T[:,1]-T[:,0];e2=T[:,2]-T[:,0];e3=T[:,2]-T[:,1];out=[T.reshape(-1,3)]
 n1=np.maximum(1,np.ceil(np.linalg.norm(e1,axis=1)/step)).astype(int);n2=np.maximum(1,np.ceil(np.linalg.norm(e2,axis=1)/step)).astype(int)
 n3=np.maximum(1,np.ceil(np.linalg.norm(e3,axis=1)/step)).astype(int)
 for a,b in set(zip(n1.tolist(),n2.tolist())):
  if a==1 and b==1:continue
  sel=np.nonzero((n1==a)&(n2==b))[0];W=np.array([(i/a,j/b) for i in range(a+1) for j in range(b+1) if i*b+j*a<=a*b])
  out.append((T[sel,0][:,None,:]+W[:,0][None,:,None]*e1[sel][:,None,:]+W[:,1][None,:,None]*e2[sel][:,None,:]).reshape(-1,3))
 for c in set(n3.tolist()):
  if c==1:continue
  sel=np.nonzero(n3==c)[0];w=np.arange(1,c)/c;out.append((T[sel,1][:,None,:]+w[None,:,None]*e3[sel][:,None,:]).reshape(-1,3))
 return np.unique(np.round(np.concatenate(out),9),axis=0)
def load():
 m=mujoco.MjModel.from_xml_path(str(MEN/'ur5e.xml'))
 bn=lambda b:mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_BODY,b)
 prims=[];tris={}
 for g in range(m.ngeom):
  b=bn(m.geom_bodyid[g]);GT=TT(m.geom_pos[g],Rq(m.geom_quat[g]))
  if m.geom_type[g]==mujoco.mjtGeom.mjGEOM_MESH:
   mid=m.geom_dataid[g];a,n=m.mesh_vertadr[mid],m.mesh_vertnum[mid];V=m.mesh_vert[a:a+n].astype(float)@GT[:3,:3].T+GT[:3,3]
   fa,fn=m.mesh_faceadr[mid],m.mesh_facenum[mid];tris.setdefault(b,[]).append(V[m.mesh_face[fa:fa+fn]])
  elif b in NAMES:
   k=sum(1 for p in prims if p['body']==b);nm=NAMES[b][k];h=float(m.geom_size[g][1])
   mt={mujoco.mjtGeom.mjGEOM_CAPSULE:'capsule',mujoco.mjtGeom.mjGEOM_CYLINDER:'cylinder'}[m.geom_type[g]]
   s0,s1,r=START.get(nm,(-h,h,float(m.geom_size[g][0])))
   prims.append(dict(name=nm,body=b,type='capsule' if nm in TUBES else 'cylinder',c=GT[:3,3].copy(),u=GT[:3,2].copy(),quat=[float(x) for x in m.geom_quat[g]],
    s0=s0,s1=s1,r=r,start=dict(extent_m=[s0,s1],radius_m=r),menagerie=dict(type=mt,pos=m.geom_pos[g].tolist(),size=[float(m.geom_size[g][0]),h],quat=m.geom_quat[g].tolist())))
 for b,lst in EXTRA.items():
  for nm,s0,s1,r,*ax in lst:
   u,q=(np.array([0.,1,0]),[math.sqrt(.5),-math.sqrt(.5),0.,0.]) if ax==['y'] else (np.array([0.,0,1]),[1.,0,0,0])
   prims.append(dict(name=nm,body=b,type='cylinder',c=np.zeros(3),u=u,quat=q,s0=s0,s1=s1,r=r,menagerie=None,start=dict(extent_m=[s0,s1],radius_m=r,axis=ax[0] if ax else 'z')))
 bodyT={bn(b):TT(m.body_pos[b],Rq(m.body_quat[b])) for b in range(1,m.nbody)}
 parent={bn(b):bn(m.body_parentid[b]) for b in range(1,m.nbody)}
 jaxis={bn(b):m.jnt_axis[m.body_jntadr[b]].copy() for b in range(1,m.nbody) if m.body_jntnum[b]}
 assert all(np.allclose(m.jnt_pos[j],0) for j in range(m.njnt))   # every joint axis passes through its body origin
 return m,prims,{b:np.vstack(t) for b,t in tris.items()},bodyT,parent,jaxis
def candidates(L,prims,bodyT,parent,jaxis,nocover=True):
 """(prim index, X: link-L frame -> prim body frame): L's own primitives, and the neighbours' primitives that
 lie on the joint axis shared with L (rotation-invariant about it, so valid at every joint angle)."""
 out=[(i,np.eye(4)) for i,p in enumerate(prims) if p['body']==L]
 for i,p in enumerate(prims):
  B=p['body']
  if parent.get(L)==B:X=bodyT[L];axB=X[:3,:3]@jaxis[L];ptB=X[:3,3]           # p on L's parent; L's joint axis in B's frame
  elif parent.get(B)==L:X=np.linalg.inv(bodyT[B]);axB=jaxis[B];ptB=np.zeros(3)  # p on L's child; the child's joint axis
  else:continue
  if abs(abs(p['u']@axB)-1)<1e-9 and np.linalg.norm(np.cross(p['c']-ptB,axB))<1e-9 and not(nocover and (L,p['name']) in NOCOVER):out.append((i,X))
 return out
def local(P,p):
 s=(P-p['c'])@p['u'];rho=np.linalg.norm(P-p['c']-np.outer(s,p['u']),axis=1);return s,rho
def sdist(s,rho,p):
 """signed distance to the primitive (exact for capsules; exact outside / max-norm inside for cylinders)"""
 if p['type']=='capsule':sc=np.clip(s,p['s0'],p['s1']);return np.hypot(s-sc,rho)-p['r']
 ax=np.maximum(p['s0']-s,s-p['s1']);rad=rho-p['r']
 return np.where((ax>0)&(rad>0),np.hypot(ax,rad),np.maximum(ax,rad))
def vol(p):return math.pi*p['r']**2*(p['s1']-p['s0'])+(4/3*math.pi*p['r']**3 if p['type']=='capsule' else 0.)
def grow_cost(s,rho,h,p):
 if p['type']=='capsule':
  sc=np.clip(s,p['s0'],p['s1']);r2=np.maximum(p['r'],np.hypot(s-sc,rho)+h);return math.pi*(r2**2-p['r']**2)*(p['s1']-p['s0'])+4/3*math.pi*(r2**3-p['r']**3)
 r2=np.maximum(p['r'],rho+h);a=np.minimum(p['s0'],s-h);b=np.maximum(p['s1'],s+h);return math.pi*r2**2*(b-a)-vol(p)
def to_frames(P,cand,prims):return [local(P@X[:3,:3].T+X[:3,3],prims[i]) for i,X in cand]
def fit(pts,prims,delta=DELTA):
 """pts: {L: (P, h, cand)}. Greedy least-added-volume growth until every point is inside by its margin h;
 each round a primitive grows by at most delta toward what its charged points need (so the charges can
 move to a neighbour that has grown meanwhile)."""
 for it in range(5000):
  charged={};nout=0
  for L,(P,hh,cand) in pts.items():
   loc=to_frames(P,cand,prims);O=np.stack([sdist(s,rho,prims[i])+hh for (s,rho),(i,X) in zip(loc,cand)],1);o=np.nonzero(O.min(1)>1e-12)[0];nout+=len(o)
   if not len(o):continue
   C=O[o] if RULE=='distance' else np.stack([grow_cost(s[o],rho[o],hh[o],prims[i]) for (s,rho),(i,X) in zip(loc,cand)],1);k=C.argmin(1)
   for kk in np.unique(k):
    s,rho=loc[kk];sel=o[k==kk];charged.setdefault(cand[kk][0],[]).append((s[sel],rho[sel],hh[sel]))
  if not nout:return it
  for i,lst in charged.items():
   p=prims[i];s,rho,hh=(np.concatenate([x[j] for x in lst]) for j in range(3))
   if p['type']=='capsule':sc=np.clip(s,p['s0'],p['s1']);p['r']=max(p['r'],min(p['r']+delta,float((np.hypot(s-sc,rho)+hh).max())))
   else:
    p['r']=max(p['r'],min(p['r']+delta,float((rho+hh).max())))
    p['s0']=min(p['s0'],max(p['s0']-delta,float((s-hh).min())));p['s1']=max(p['s1'],min(p['s1']+delta,float((s+hh).max())))
 raise RuntimeError('fit did not converge')
def shrink(pts,prims):
 """Each primitive in turn shrinks to the points (with margins) that no other candidate holds; repeat until
 nothing changes. Keeps every point inside; removes the slack the greedy growth left."""
 for it in range(50):
  change=0.
  for i,p in enumerate(prims):
   S_=[];R_=[];H_=[]
   for L,(P,hh,cand) in pts.items():
    ks=[k for k,(j,X) in enumerate(cand) if j==i]
    if not ks:continue
    loc=to_frames(P,cand,prims);O=np.stack([sdist(s,rho,prims[j])+hh for (s,rho),(j,X) in zip(loc,cand)],1)
    others=np.delete(O,ks[0],axis=1).min(1) if O.shape[1]>1 else np.full(len(P),1.)
    e=others>1e-12;s,rho=loc[ks[0]];S_.append(s[e]);R_.append(rho[e]);H_.append(hh[e])
   s,rho,hh=np.concatenate(S_),np.concatenate(R_),np.concatenate(H_)
   if not len(s):continue
   old=(p['r'],p['s0'],p['s1'])
   if p['type']=='capsule':sc=np.clip(s,p['s0'],p['s1']);p['r']=float((np.hypot(s-sc,rho)+hh).max())
   else:p['r']=float((rho+hh).max());p['s0']=float((s-hh).min());p['s1']=float((s+hh).max())
   change=max(change,abs(p['r']-old[0]),abs(p['s0']-old[1]),abs(p['s1']-old[2]))
  if change<1e-7:return it
 return it
def grown(p,s,rho,hh):
 """p grown just enough to hold the points (s, rho in p's frame, margins hh)."""
 q=dict(p)
 if p['type']=='capsule':sc=np.clip(s,p['s0'],p['s1']);q['r']=max(p['r'],float((np.hypot(s-sc,rho)+hh).max()))
 else:q['r']=max(p['r'],float((rho+hh).max()));q['s0']=min(p['s0'],float((s-hh).min()));q['s1']=max(p['s1'],float((s+hh).max()))
 return q
def rebalance(pts,prims,steps=(.008,.004,.002,.001,.0005)):
 """Local search on the total volume: move one size of one primitive inward by a step (radius, either end);
 the points that are then outside everything go to the one other primitive whose growth to hold them all
 adds the least volume; keep the move if the total volume drops. Repeat until no move helps."""
 links={i:[L for L,(P,hh,cand) in pts.items() if any(j==i for j,X in cand)] for i in range(len(prims))}
 moves=0
 for it in range(200):
  best=None
  for i,p in enumerate(prims):
   for par in (('r',) if p['type']=='capsule' else ('r','s0','s1')):
    for d in steps:
     t=dict(p);t[par]+=-d if par in ('r','s1') else d
     if t['r']<.005 or t['s1']-t['s0']<.002:continue
     out={}
     for L in links[i]:
      P,hh,cand=pts[L];loc=to_frames(P,cand,prims)
      O=np.stack([sdist(s_,rho_,t if j==i else prims[j])+hh for (s_,rho_),(j,X) in zip(loc,cand)],1)
      o=O.min(1)>1e-12
      if o.any():out[L]=(o,loc,cand,hh)
     gain=vol(p)-vol(t)
     if not out:
      if gain>0 and (best is None or gain>best[0]):best=(gain,i,t,None,None)
      continue
     common=set.intersection(*[{j for j,X in cand if j!=i} for o,loc,cand,hh in out.values()])
     for j in common:
      S_=[];R_=[];H_=[]
      for L,(o,loc,cand,hh) in out.items():
       k=[n for n,(jj,X) in enumerate(cand) if jj==j][0];S_.append(loc[k][0][o]);R_.append(loc[k][1][o]);H_.append(hh[o])
      q=grown(prims[j],np.concatenate(S_),np.concatenate(R_),np.concatenate(H_));g=gain-(vol(q)-vol(prims[j]))
      if g>1e-12 and (best is None or g>best[0]):best=(g,i,t,j,q)
  if best is None:return moves
  g,i,t,j,q=best;prims[i].update(t);moves+=1
  if j is not None:prims[j].update(q)
 return moves
def certify(T,cand,prims,depth=DEPTH):
 """Exact enclosure test of triangles T (n,3,3) by the union of cand. Returns (stats, corners of the
 uncertified smallest parts with their margins)."""
 stats=dict(triangles=len(T),split_parts=0,levels=0,corner_outside=0);bad=[np.zeros((0,3))];badh=[np.zeros(0)]
 for lev in range(depth+1):
  if not len(T):break
  P=T.reshape(-1,3);S=np.stack([sdist(s,rho,prims[i]) for (s,rho),(i,X) in zip(to_frames(P,cand,prims),cand)],1).reshape(len(T),3,-1)
  U=S.min(2)                                                       # signed distance of each corner to the union
  out=(U>0).any(1)                                                 # a corner outside: fails, the corner goes back into the fit
  if out.any():bad.append(T[out][U[out]>0]);badh.append(np.zeros(int((U[out]>0).sum())));stats['corner_outside']+=int(out.sum())
  one=(S.max(1)<=0).any(1)                                         # one convex primitive holds all 3 corners
  a=np.max(np.linalg.norm(T-np.roll(T,1,axis=1),axis=2),axis=1)
  lip=U.max(1)+a/math.sqrt(3)<=0                                   # every corner inside the union by >= a/sqrt(3)
  T=T[~(one|lip|out)];stats['levels']=lev
  if lev==depth or not len(T):break
  M=(T+np.roll(T,-1,axis=1))/2                                     # midpoints of edges 01, 12, 20
  T=np.concatenate([np.stack([T[:,0],M[:,0],M[:,2]],1),np.stack([M[:,0],T[:,1],M[:,1]],1),np.stack([M[:,2],M[:,1],T[:,2]],1),np.stack([M[:,0],M[:,1],M[:,2]],1)])
  stats['split_parts']+=len(T)
 if len(T):
  a=np.max(np.linalg.norm(T-np.roll(T,1,axis=1),axis=2),axis=1);bad.append(T.reshape(-1,3));badh.append(np.repeat(a/math.sqrt(3)+1e-7,3))
 stats['uncertified']=int(len(T))+stats['corner_outside'];return stats,np.concatenate(bad),np.concatenate(badh)
def max_out(tris,cand_of,prims):
 """per link: the largest signed distance of a mesh VERTEX to the union of its candidates (> 0: sticks out)."""
 res={}
 for L,T in tris.items():
  if L not in cand_of:continue
  P=np.unique(T.reshape(-1,3),axis=0);O=np.stack([sdist(s,rho,prims[i]) for (s,rho),(i,X) in zip(to_frames(P,cand_of[L],prims),cand_of[L])],1).min(1)
  res[L]=dict(vertices=int(len(P)),max_protrusion_mm=round(float(O.max())*1e3,3),vertices_outside=int((O>0).sum()))
 return res
def geom_xml(p):
 """MJCF on the prim's own body: same axis (quat) as Menagerie, centre and half-length from [s0, s1]."""
 c=p['c']+p['u']*(p['s0']+p['s1'])/2;return dict(type=p['type'],pos=[round(float(x),7) for x in c],quat=p['quat'],size=[round(p['r'],7),round((p['s1']-p['s0'])/2,7)])
def main():
 m,prims,tris,bodyT,parent,jaxis=load();cand_of={L:candidates(L,prims,bodyT,parent,jaxis) for L in NAMES}
 before=max_out(tris,{L:[(i,X) for i,X in candidates(L,prims,bodyT,parent,jaxis,False) if prims[i]['menagerie']] for L in NAMES},[dict(p,type=p['menagerie']['type'],s0=-p['menagerie']['size'][1],s1=p['menagerie']['size'][1],r=p['menagerie']['size'][0]) if p['menagerie'] else p for p in prims])   # the Menagerie geoms as they are
 pts={}
 for L in NAMES:
  P=grid(tris[L],STEP);pts[L]=(P,np.zeros(len(P)),cand_of[L])
  print(L,'triangles',len(tris[L]),'fit points',len(P),'candidates',[prims[i]['name']+('' if prims[i]['body']==L else '@'+BODY[prims[i]['body']]) for i,X in cand_of[L]],flush=True)
 rounds=[]
 rng=np.random.default_rng(0)
 vpts={}
 for L,(P,hh,c) in pts.items():k=rng.random(len(P))<.2;vpts[L]=(P[k],hh[k],c)   # the local search on a 20 % subset (speed); the grow / certify rounds use all
 for rnd in range(20):
  its=fit(pts,prims);sh=shrink(pts,prims) if rnd==0 else 0;rb=rebalance(vpts,prims) if rnd==0 else 0;cert={};nbad=0   # shrink + rebalance once; later rounds only grow (converges)
  for L in NAMES:
   st,bad,badh=certify(tris[L],cand_of[L],prims);cert[L]=st;nbad+=st['uncertified']
   if st['uncertified']:P,hh,c=pts[L];pts[L]=(np.r_[P,bad],np.r_[hh,badh],c)
  rounds.append(dict(fit_iterations=its,shrink_passes=sh,rebalance_moves=rb,uncertified=nbad,total_volume_l=round(sum(vol(p) for p in prims)*1e3,3)));print('round',rnd,rounds[-1],flush=True)
  if not nbad:break
 else:raise RuntimeError('enclosure not certified')
 for p in prims:
  p['r']+=5e-5
  if p['type']=='cylinder':p['s0']-=5e-5;p['s1']+=5e-5
 cert={L:certify(tris[L],cand_of[L],prims)[0] for L in NAMES};assert all(v['uncertified']==0 for v in cert.values())
 after=max_out(tris,cand_of,prims)
 out=dict(id='ur5e_enc',name='UR5e with collision geoms enclosing the MuJoCo Menagerie visual meshes',menagerie_dir=str(MEN.resolve()).replace('\\','/'),step_m=STEP,depth=DEPTH,rounds=rounds,
  method=__doc__,labels=dict(M='Menagerie ur5e.xml, assets/*.obj',E='fitted here'),
  geoms=[dict(name=p['name'],body=BODY[p['body']],**geom_xml(p),extent_m=[round(p['s0'],6),round(p['s1'],6)],
   **(dict(menagerie=p['menagerie'],start=p['start'],radius_growth_mm=round((p['r']-p['menagerie']['size'][0])*1e3,2),menagerie_extent_m=[-p['menagerie']['size'][1],p['menagerie']['size'][1]],label='E (axis and body = the Menagerie geom, M)')
      if p['menagerie'] else dict(added=True,start=p['start'],label='E: added cylinder (neck on the link axis, or the shoulder part of the J2 housing)'))) for p in prims],
  candidates={BODY[L]:[prims[i]['name'] for i,X in v] for L,v in cand_of.items()},
  enclosure_menagerie_geoms=before,enclosure_fitted_vertices=after,enclosure_certificate=cert)
 fn=H/'r19'/'arm_ur5e_enc.json';fn.write_text(json.dumps(out,indent=1),encoding='utf-8');print(fn)
 for g in out['geoms']:
  if g.get('menagerie'):print(f"{g['name']:22s} {g['body']:22s} {g['menagerie']['type']:8s}->{g['type']:8s} r Menagerie {g['menagerie']['size'][0]*1e3:5.1f} start {g['start']['radius_m']*1e3:5.1f} -> {g['size'][0]*1e3:6.2f} mm  extent {g['menagerie_extent_m']} start {g['start']['extent_m']} -> {g['extent_m']}")
  else:print(f"{g['name']:22s} {g['body']:22s} added   ->{g['type']:8s} r {g['start']['radius_m']*1e3:5.1f}->{g['size'][0]*1e3:6.2f} mm  extent {g['start']['extent_m']} -> {g['extent_m']}")
 for L in NAMES:print(f'{L:15s} Menagerie geoms: max protrusion {before[L]["max_protrusion_mm"]:6.2f} mm | fitted: {after[L]["max_protrusion_mm"]:6.2f} mm, certificate {cert[L]}')
if __name__=='__main__':main()
