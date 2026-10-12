"""Independent convex hull distance: original mesh vertices, no geometry edits."""
from reverify import *
from scipy.spatial import ConvexHull
from scipy.optimize import minimize,LinearConstraint
def vertices(ch,g):
 m,d=ch.m,ch.d;rt=d.geom_xmat[g].reshape(3,3);pos=d.geom_xpos[g]
 if m.geom_type[g]==mujoco.mjtGeom.mjGEOM_BOX:
  pts=np.array(list(itertools.product((-1,1),repeat=3)))*m.geom_size[g]
 elif m.geom_type[g]==mujoco.mjtGeom.mjGEOM_MESH:
  mid=m.geom_dataid[g];adr=m.mesh_vertadr[mid];num=m.mesh_vertnum[mid];pts=m.mesh_vert[adr:adr+num].astype(float)
 else:raise ValueError(ch.gnames[g])
 pts=pts@rt.T+pos;hull=ConvexHull(pts);return pts[hull.vertices],hull.equations
def distance(ch,a,b):
 va,pa=vertices(ch,a);vb,pb=vertices(ch,b)
 aa=np.zeros((len(pa)+len(pb),6));aa[:len(pa),:3]=pa[:,:3];aa[len(pa):,3:]=pb[:,:3];bb=-np.r_[pa[:,3],pb[:,3]]
 start=np.r_[va.mean(axis=0),vb.mean(axis=0)]
 def fun(x):delta=x[:3]-x[3:];return float(delta@delta)
 def jac(x):delta=x[:3]-x[3:];return np.r_[2*delta,-2*delta]
 res=minimize(fun,start,jac=jac,constraints=[LinearConstraint(aa,-np.inf,bb)],method='SLSQP',options=dict(ftol=1e-14,maxiter=250))
 violation=float(np.max(aa@res.x-bb))
 direction=res.x[:3]-res.x[3:];length=np.linalg.norm(direction)
 projection_gap=float(np.min(va@(direction/length))-np.max(vb@(direction/length))) if length>1e-8 else 0.
 # Finite-dimensional convex QP. A feasible pair is an independent upper
 # witness for true separation, useful even without optimizer convergence.
 return dict(pair=[ch.gnames[a],ch.gnames[b]],convex_separation_mm=float(np.sqrt(max(0,res.fun))*1000),separating_projection_lower_bound_mm=projection_gap*1000,clearance_10mm_certified=bool(projection_gap>=.010-1e-6),constraint_violation_m=violation,optimizer_success=bool(res.success),point_a_world_m=res.x[:3].tolist(),point_b_world_m=res.x[3:].tolist(),original_vertex_counts=[len(va),len(vb)],independent_below_10mm=bool(violation<=1e-7 and res.fun<(.010-1e-6)**2))
def main():
 rows=[];raw=json.loads((I/'results/final6/Q05.potato.json').read_text());ph=next(x for x in s.P['phases'] if x['id']=='Q05.potato')
 for label,k in [('helper_index_6',5),('helper_index_7',79)]:
  sg=next(x for x in ph['segments'] if x['label']==label);pt=next(x for x in raw['parts'] if x['label']==label);row=next(x for x in pt['rows'] if x['k']==k);ch=s.Checker(ph,sg)
  contacts(ch,np.array(row['poses'][1]['q']),sg['poses'][1]);a=ch.gnames.index('L_link2_collision');b=ch.gnames.index('cable_chain_swept_cover_0_piece4')
  r=distance(ch,a,b);r.update(stroke='Q05.potato__'+label,k=k,pose=1,libccd_20mm_query_mm=float(mujoco.mj_geomDistance(ch.m,ch.d,a,b,.020,None)*1000),libccd_100mm_query_mm=float(mujoco.mj_geomDistance(ch.m,ch.d,a,b,.100,None)*1000));rows.append(r);print(json.dumps(r),flush=True)
 ph=s.P['phases'][0];ch=s.Checker(ph,ph['segments'][0]);ch.bind_model(mujoco.MjModel.from_xml_path(str(I/'models/passing.xml')))
 q=np.array(json.loads((I/'results/motion.json').read_text())['parking']['q']);contacts(ch,q,ph['segments'][0]['poses'][0]);layout=json.loads((O/'motion_layout_independent.json').read_text());door=[]
 for x in layout['parked_door_sweep_infringements']:
  a,b=[ch.gnames.index(n) for n in x['pair']]
  r=distance(ch,a,b);r['libccd_500mm_query_mm']=x['gap_mm'];door.append(r)
 dump('convex_geometry_crosscheck.json',dict(clearance_discrepancies=rows,parked_door_sweeps=door,method='Original compiled mesh vertex convex hulls and oriented boxes;6variable convex quadratic distance using hull halfspaces. Geometries were read unchanged; no scale, padding, threshold or collision-model mutation.',limits='Convex hull separation is nonnegative, so zero proves intersection/touching but does not assign an exact penetration depth. Feasible below10mm point witnesses establish failure of10mm clearance without relying on libccd positive-distmax estimates.'))
 print('confirmed alternative-seed conflicts',sum(x['independent_below_10mm'] for x in rows),'confirmed doors',sum(x['independent_below_10mm'] for x in door),flush=True)
if __name__=='__main__':main()
