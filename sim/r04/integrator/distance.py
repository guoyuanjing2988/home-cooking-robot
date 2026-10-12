"""Conservative convex distance certificates, independent of libccd distmax.

Broadphase uses enclosing AABBs. Narrowphase uses exact convex support functions
and GJK primal/dual bounds. A dual separating projection is always a lower bound;
the simplex point is an upper bound. Unknown never becomes a pass.
"""
import itertools
import numpy as np
import mujoco
from scipy.spatial import ConvexHull

def closest(points):
    pts=np.asarray(points);best=None
    for count in range(1,min(4,len(pts))+1):
        for ix in itertools.combinations(range(len(pts)),count):
            v=pts[list(ix)];gram=v@v.T
            mat=np.block([[gram,np.ones((count,1))],[np.ones((1,count)),np.zeros((1,1))]])
            rhs=np.r_[np.zeros(count),1.]
            weights=np.linalg.lstsq(mat,rhs,rcond=1e-13)[0][:count]
            if min(weights)<-1e-9:continue
            weights=np.maximum(weights,0);weights/=sum(weights);p=weights@v;value=float(p@p)
            if best is None or value<best[0]:best=(value,p,[pts[j] for j,w in zip(ix,weights) if w>1e-9])
    return best[1],best[2]

class Bounds:
    def __init__(self,ch,required):
        self.ch=ch;self.m=ch.m;self.d=ch.d;self.local={};self.pairs=[]
        m=ch.m
        for g in range(m.ngeom):
            if m.geom_type[g]==mujoco.mjtGeom.mjGEOM_MESH:
                mid=m.geom_dataid[g];adr=m.mesh_vertadr[mid];v=m.mesh_vert[adr:adr+m.mesh_vertnum[mid]].astype(float)
                self.local[g]=v[ConvexHull(v).vertices]
        frames=('rail_beam_','rail_guide_','cable_chain_','wall_crossbar_','lane_hanger_')
        for a in range(m.ngeom):
            for b in range(a+1,m.ngeom):
                # Sweep boxes are queried separately in the idle-kitchen audit.
                if any(ch.gnames[j].startswith('cabinet_door_sweep') for j in (a,b)):continue
                req=required(ch,a,b)
                if req is None:
                    ns=[ch.gnames[a],ch.gnames[b]]
                    if any(n.startswith(('R_geom_','L_link')) for n in ns) and any(n.startswith(frames) for n in ns):req=(.010,'arm_arm_or_frame')
                if req is not None:self.pairs.append((a,b,*req))
        self.aa=np.array([r[0] for r in self.pairs]);self.bb=np.array([r[1] for r in self.pairs])
        self.need=np.array([r[2] for r in self.pairs]);self.cats=np.array([r[3] for r in self.pairs]);self.catids={c:np.flatnonzero(self.cats==c) for c in set(self.cats)}
        influences=np.zeros((m.ngeom,m.nq),dtype=bool)
        for g in range(m.ngeom):
            body=int(m.geom_bodyid[g])
            while body:
                for j in range(int(m.body_jntadr[body]),int(m.body_jntadr[body]+m.body_jntnum[body])):
                    influences[g,int(m.jnt_qposadr[j])]=True
                body=int(m.body_parentid[body])
        # A shared ancestor rigid transform preserves pairwise distance exactly.
        self.relative_influence=np.logical_xor(influences[self.aa],influences[self.bb])
        self.motion_weights=np.ones(m.nq)
        for j in range(m.njnt):
            if m.jnt_type[j]==mujoco.mjtJoint.mjJNT_HINGE:self.motion_weights[int(m.jnt_qposadr[j])]=2.

    def support(self,g,direction):
        m,d=self.m,self.d;rt=d.geom_xmat[g].reshape(3,3);p=d.geom_xpos[g];v=rt.T@direction;sz=m.geom_size[g];typ=m.geom_type[g]
        if typ==mujoco.mjtGeom.mjGEOM_BOX:x=np.where(v>=0,sz,-sz)
        elif typ==mujoco.mjtGeom.mjGEOM_MESH:
            vs=self.local[g];x=vs[np.argmax(vs@v)]
        elif typ==mujoco.mjtGeom.mjGEOM_SPHERE:x=sz[0]*v/max(np.linalg.norm(v),1e-30)
        elif typ==mujoco.mjtGeom.mjGEOM_CAPSULE:
            x=sz[0]*v/max(np.linalg.norm(v),1e-30);x[2]+=sz[1] if v[2]>=0 else -sz[1]
        elif typ==mujoco.mjtGeom.mjGEOM_CYLINDER:
            x=np.r_[sz[0]*v[:2]/max(np.linalg.norm(v[:2]),1e-30),sz[1] if v[2]>=0 else -sz[1]]
        elif typ==mujoco.mjtGeom.mjGEOM_ELLIPSOID:x=sz*sz*v/max(np.linalg.norm(sz*v),1e-30)
        else:raise ValueError((g,typ))
        return p+rt@x

    def pair(self,a,b,tol=2e-7,translation=None):
        if self.m.geom_type[a]==0 or self.m.geom_type[b]==0:
            plane=a if self.m.geom_type[a]==0 else b;other=b if plane==a else a
            n=self.d.geom_xmat[plane].reshape(3,3)[:,2];gap=float(n@(self.support(other,-n)-self.d.geom_xpos[plane]))
            if translation is not None:gap+=min(0.,float(n@translation))
            return dict(lower_m=gap,upper_m=gap,iterations=1,method='analytic plane support')
        def sup(v):
            p=self.support(a,v)-self.support(b,-v)
            if translation is not None and v@translation>0:p=p+translation
            return p
        direction=self.d.geom_xpos[b]-self.d.geom_xpos[a]
        if np.linalg.norm(direction)<1e-10:direction=np.array([1.,0,0])
        points=[sup(direction)];v=points[0];lower=0.
        for it in range(80):
            upper=float(np.linalg.norm(v))
            if upper<1e-10:return dict(lower_m=0.,upper_m=upper,iterations=it+1,method='convex intersection/touch; no signed penetration claimed')
            w=sup(-v);lower=max(lower,float(v@w)/upper,0.)
            if upper-lower<=tol:return dict(lower_m=max(0.,lower-1e-8),upper_m=upper+1e-8,iterations=it+1,method='GJK separating-projection dual / simplex primal')
            if any(np.linalg.norm(w-x)<1e-12 for x in points):break
            v,points=closest(points+[w])
        return dict(lower_m=max(0.,lower-1e-8),upper_m=float(np.linalg.norm(v))+1e-8,iterations=it+1,method='bounded GJK; dual lower bound remains valid')

    def check(self,allowed=frozenset()):
        ch=self.ch;m=self.m;lo=np.zeros((m.ngeom,3));hi=lo.copy()
        for g in range(m.ngeom):
            if m.geom_type[g]==0:lo[g]=-1e6;hi[g]=1e6;continue
            for k in range(3):
                axis=np.eye(3)[k];lo[g,k]=self.support(g,-axis)[k];hi[g,k]=self.support(g,axis)[k]
        delta=np.maximum(np.maximum(lo[self.aa]-hi[self.bb],lo[self.bb]-hi[self.aa]),0)
        aabb=np.linalg.norm(delta,axis=1);mins={};hits=[];narrow=0
        excluded=np.array([i for i,(a,b,need,cat) in enumerate(self.pairs) if frozenset([ch.gnames[a],ch.gnames[b]]) in allowed],dtype=int) if allowed else np.array([],dtype=int)
        aabb[excluded]=1e6
        ids=set(np.flatnonzero(aabb<self.need+.002).tolist())
        for cat,ci in self.catids.items():ids.add(int(ci[np.argmin(aabb[ci])]))
        lower_all=aabb.copy();upper_all={};method_all={}
        for i in sorted(ids):
            a,b,need,cat=self.pairs[i]
            pair=frozenset([ch.gnames[a],ch.gnames[b]])
            if pair in allowed:continue
            lower=float(aabb[i]);upper=None;method='enclosing AABB separation lower bound'
            # Refine the closest pairs for each category and every doubtful gap.
            if lower<need+.002 or cat not in mins or lower<mins[cat]['clearance_mm']/1000:
                v=self.pair(a,b);lower=max(lower,v['lower_m']);upper=v['upper_m'];method=v['method'];narrow+=1
            lower_all[i]=lower;upper_all[i]=upper;method_all[i]=method
            val=dict(pair=[ch.gnames[a],ch.gnames[b]],clearance_mm=lower*1000,upper_bound_mm=None if upper is None else upper*1000,required_mm=need*1000,reserve_mm=(lower-need)*1000,lower_bound=True,method=method)
            if cat not in mins or lower<mins[cat]['clearance_mm']/1000:mins[cat]=val
            if lower<need-1e-6:
                hits.append(dict(pair=val['pair'],real_gap_mm=lower*1000,upper_bound_mm=val['upper_bound_mm'],required_gap_mm=need*1000,reason='independent convex upper witness violates gap' if upper is not None and upper<need-1e-6 else 'uncertified separation; no optimistic pass'))
        # Include every unrefined AABB bound in the minimum; no pair disappears.
        for cat,ci in self.catids.items():
            i=int(ci[np.argmin(lower_all[ci])]);a,b,need,_=self.pairs[i]
            mins[cat]=dict(pair=[ch.gnames[a],ch.gnames[b]],clearance_mm=float(lower_all[i]*1000),upper_bound_mm=None if upper_all.get(i) is None else upper_all[i]*1000,required_mm=need*1000,reserve_mm=float((lower_all[i]-need)*1000),lower_bound=True,method=method_all.get(i,'enclosing AABB separation lower bound'))
        self.last_lower=lower_all;self.last_allowed=excluded
        return hits,mins,dict(eligible_pairs=len(self.pairs),narrow_queries=narrow,absent_contact_assumption=False)

    def interval_certificate(self,dq,half_width):
        movement=self.relative_influence@(abs(np.asarray(dq))*self.motion_weights)*half_width
        reserve=self.last_lower-self.need
        # A moving intended contact also needs a continuous face/normal proof;
        # sampled normal checks alone are insufficient. Reject that interval.
        if len(self.last_allowed) and np.any(movement[self.last_allowed]>1e-12):return False
        return bool(np.all(reserve+1e-9>=movement))
