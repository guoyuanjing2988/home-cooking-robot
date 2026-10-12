"""Conservative level-floor footprint, tether and support-polygon statics.

Static floor contact polygon uses inset wheel/caster contact centres, not body
outline. A passive equalising rear bogie and locked drive are design requirements.
No ramps/thresholds admitted. Process loads are forces ON the arm, both signs
are additionally tested for tip-over so a sign convention cannot hide failure.
"""
import numpy as np,mujoco
def footprint(q):
 x,y,a=q[:3];c,s=np.cos(a),np.sin(a);R=np.array([[c,-s],[s,c]])
 return np.array([[u,v] for u in [-.33,.33] for v in [-.25,.25]])@R.T+[x,y]
def floor_check(ch,q):
 p=footprint(q);ok=bool(np.all(p[:,0]>=-1.80+.01) and np.all(p[:,0]<=2.80-.01) and np.all(p[:,1]>=-.90+.01) and np.all(p[:,1]<=-.025-.01))
 # 6mm cable inside 30mm guarded toe channel, 20mm sag/lateral envelope.
 # Short branch exits in front of the cart, away from wheels. Yaw is limited
 # by this unsteered inlet. Large in-place turns are rejected, never teleported.
 x,y,a=q[:3];end=np.array([x-np.sin(a)*.26,y+np.cos(a)*.26,.10]);start=np.array([end[0],-.025,.015])
 wheel_min=1e6
 for xx in [-.24,.24]:
  for yy in [-.20,.20]:
   centre=np.array([x+np.cos(a)*xx-np.sin(a)*yy,y+np.sin(a)*xx+np.cos(a)*yy])
   v=end[:2]-start[:2];t=np.clip((centre-start[:2])@v/max(v@v,1e-12),0,1)
   wheel_min=min(wheel_min,float(np.linalg.norm(centre-start[:2]-v*t)-.0825-.020))
 cable_ok=bool(abs(a)<=.18 and wheel_min>=.010 and -1.8<=end[0]<=2.8 and end[1]<-.035)
 # Protected branch:3mm cable radius,20mm lateral/aisleward sag; fixed
 # fairlead prevents wallward sag at the guide. Conservative AABB separation
 # checks ALL arm/held parts and environment. Only real floor/guide support
 # and the named chassis inlet are mating contacts, not general exclusions.
 low=np.minimum(start,end)-[.020,.020,.003];high=np.maximum(start,end)+[.020,.003,.003]
 cable_hits=[]
 for g,n in enumerate(ch.gnames):
  if n in ('floor','floor_cable_guide','R_cart_chassis'):continue
  if n.startswith('R_cart_wheel_'):continue # complete circular sweep above
  # Fast safe enclosing AABB for primitives; meshes use precomputed support.
  typ=ch.m.geom_type[g]
  if typ==0:continue
  center=ch.d.geom_xpos[g];rot=abs(ch.d.geom_xmat[g].reshape(3,3));size=ch.m.geom_size[g]
  if typ==6:ext=rot@size
  elif typ in (3,5):ext=rot@np.array([size[0],size[0],size[1]+(size[0] if typ==3 else 0)])
  elif typ==2:ext=np.ones(3)*size[0]
  else:ext=np.ones(3)*ch.m.geom_rbound[g]
  gap=np.linalg.norm(np.maximum(np.maximum((center-ext)-high,low-(center+ext)),0))
  need=.005 if ch.held[g] or ch.gripper(g) else .010
  if gap<need-1e-9:cable_hits.append(dict(part=n,conservative_AABB_gap_m=float(gap),required_m=need))
 cable_ok=cable_ok and not cable_hits
 return dict(ok=ok and cable_ok,footprint_ok=ok,cable_ok=cable_ok,cable_hits=cable_hits,footprint_xy_m=p.tolist(),cable_branch_m=[start.tolist(),end.tolist()],cable_envelope_aabb_m=[low.tolist(),high.tolist()],wheel_cable_clearance_m=wheel_min,cable_envelope_radius_m=.020,guide_bounds_m=[[-1.8,-.04,0],[2.8,-.01,.03]],floor_assumption='0.9m clear level aisle + right end alcove x=1.8..2.8; not measured')
def stability(ch,q,force,mass,work=.08):
 m,d=ch.m,ch.d;d.qpos[:]=q;mujoco.mj_forward(m,d)
 root=m.body('rail_structure').id
 ids=[]
 for b in range(1,m.nbody):
  ancestor=b
  while ancestor and ancestor!=root:ancestor=m.body_parentid[ancestor]
  if ancestor==root:ids.append(b)
 masses=m.body_mass[ids];centres=d.xipos[ids]
 moving=np.array([m.body(b).name.startswith('R_arm_') or m.body(b).name in ('R_tool','R_jaw_minus','R_jaw_plus') for b in ids])
 sid=m.site('R_prep').id;R=d.site_xmat[sid].reshape(3,3);p=d.site_xpos[sid]
 item=ch.meta.get('held');off=np.array([.08,0,0]) if item=='holder' else np.zeros(3)
 com=p+R@off;application=p+R@(np.array([work,0,0]) if item=='holder' else np.array([.0175,0,0]) if item=='carrot' else np.zeros(3))
 W=float((masses.sum()+mass)*9.81);moment=np.sum(np.cross(centres,masses[:,None]*np.array([0,0,-9.81])),axis=0)+np.cross(com,[0,0,-mass*9.81])
 x,y,a=q[:3];c,s=np.cos(a),np.sin(a);rot=np.array([[c,-s],[s,c]])
 cases=[]
 # 20N tether fault cap at .10m; .15m/s2 base acceleration any horizontal direction.
 for factor in [1.,1.5]:
  for sign in [-1,1]:
   for axis in range(2):
    for direction in [-1,1]:
     effective=masses*np.where(moving,factor,1.)
     dynamic_mass=mass*factor;weight=float((effective.sum()+dynamic_mass)*9.81)
     gravity_moment=np.sum(np.cross(centres,effective[:,None]*np.array([0,0,-9.81])),axis=0)+np.cross(com,[0,0,-dynamic_mass*9.81])
     f=factor*sign*np.asarray(force,float);total=np.array([0.,0.,-weight])+f
     inertia=np.zeros(3);inertia[axis]=direction*(masses.sum()+mass)*.15*factor
     avg=(np.sum(masses[:,None]*centres,axis=0)+mass*com)/(masses.sum()+mass)
     torque=gravity_moment+np.cross(application,f)+np.cross(avg,inertia)
     reaction=-total[2]
     zmp=np.array([torque[1]/reaction,-torque[0]/reaction]);local=rot.T@(zmp-[x,y])
     margins=np.array([.215-abs(local[0]),.175-abs(local[1])])
     # Any horizontal cable direction at the low inlet: exact worst projection
     # onto any support edge is tension*height/reaction. Includes1.5 factor.
     cable_reserve=20*.10*factor/reaction
     margin=float(min(margins)-cable_reserve);cases.append(dict(factor=factor,force_sign=sign,inertial_axis=axis,inertial_sign=direction,margin_m=margin,restoring_margin_Nm=margin*reaction,zmp_world_m=zmp.tolist(),cable_any_direction_loss_m=cable_reserve))
 worst=min(cases,key=lambda x:x['margin_m'])
 return dict(ok=worst['margin_m']>0,min_margin_m=worst['margin_m'],min_restoring_Nm=worst['restoring_margin_Nm'],mass_kg=float(masses.sum()+mass),worst=worst,support_half_extents_m=[.215,.175],dynamic_factor=1.5,factor_scope='moving arm+held gravity, process wrench and acceleration; chassis gravity remains static; any horizontal20N cable tension at100mm inlet')
