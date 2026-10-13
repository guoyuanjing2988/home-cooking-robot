"""R19 #36: the PGC-140-50 cable outlet (strain-relief boot) and the first part of its cable, as conservative convex
enclosing shapes on the gripper body (R_tool). New file. Used by arms.py for the arm options *_pgcc* (ARMS[..]['cable'] =
a ROUTINGS key). Sources and labels: R19_CABLE.md section 1 (S = sourced with URL, E = estimate / measured off a drawing).

What the PGC-140-50 has (DH's current drawings, PGC parameter sheet CN.2405 p.6 and Electric Gripper Brochure 2024 p.17):
no socket on the body. A fixed pigtail leaves the round base RADIALLY, horizontally, IN THE JAW PLANE (along the stroke
axis, under one jaw) through a strain-relief boot that sticks out 12 mm [S] (about Ø16 at the body [E]); cable Ø6.4 [S],
allowable bending radius R50 [S], 200 mm long to an M12 8-pin plug (M12x1, max Ø15) [S]; "Secure at least 100mm" beside
the body [S]. The exit height (cable axis above the gripper's bottom face, the 98 mm datum) is not dimensioned: 21.1 mm
measured on two DH drawings, 22-24 mm on a photo [E]; taken here as the band 19-25 mm (every shape is the hull over the
band). Only a side outlet is offered (no right-angle or through-flange version) [S].

Frame: the frame of scene.oem_pgc_drawing (the PGC drawing housing) before the finger-design shift that fingers.apply puts
on every geom of R_tool: tool x = gripper axis (fingertips at +x), y = jaw stroke, z = across the jaw plane; the gripper's
bottom (flange) face at X0 = -0.1735 m, the round Ø75 body from X0 to X0 + 52 mm. add() gives the cable geoms the pos
of R_gripper_oem_envelope (the shift actually applied), so they sit on the housing in every finger design.

Shapes per side (MuJoCo mesh geoms = convex hulls of the listed vertices; circles are polygons CIRCUMSCRIBED about the
true circle, so every hull encloses the solid it stands for):
 boot   the strain-relief boot: Ø16 cylinder on the exit axis, from 3 mm inside the body surface to 12 mm outside it;
 bendK  the cable (Ø6.4) turning from the exit direction to the dressing direction with a centreline radius of
        R50 + 3.2 = 53.2 mm (DH's R50 read as the INSIDE radius: the reading that reaches further out), in 3 arcs of 30 deg,
        each the hull of cross-sections every 5 deg, inflated by the sagitta between sections;
 run    the straight cable after the bend, RUN = 20 mm [E]: the length a tie on the adapter takes; beyond it the dress
        is a choice (to the UR tool connector, or along the arm) and is not modelled;
 k100   (keep-out routings only, instead of boot/bend/run) DH's "Secure at least 100mm" zone on that side: a slab from
        3 mm inside the body surface to 100 mm outside it, +-8 mm across the jaw plane (the boot radius), from above the
        boot top down to where a cable bent at the largest radius that fits in 100 mm (and its run) ends.
Dressing directions after the bend: 'dn' = -x, down along the body toward the gripper's flange face (DH's drawing);
'fl' = +z, toward the side of the robot flange / adapter (the UR flange centre is on the +z side of the gripper axis);
'a<deg>' = cos(deg) * (-x) + sin(deg) * (+z), e.g. a-45 = down and away from the robot-flange side. Suffix _r0: the first tie
right at the end of the bend (no straight run). Routing names: <side>_<dress>[_r0], side yp / ym = outlet under the +y / -y
jaw. Recommended after R19 #36: yp_a-45 (R19_CABLE.md).
Names start with R_pgc_cable (not R_gripper_ / R_finger_) so that no grasp / food contact window of the existing tools
(chain.py, r19prepchain.py, r19prep_verify.py: R_finger_* / R_gripper_* vs the food) ever applies to them. Contact
settings as the drawing housing (contype 2, conaffinity 3, negligible mass: R_tool has an explicit inertial). The checker
treats every geom on R_tool as gripper: 5 mm to the environment, 0 mm self; R_tool vs the wrist-3 link and vs the held
object are unchecked pairs (adjacent / same body), so those are checked statically (r19cable_static.py)."""
import numpy as np
import xml.etree.ElementTree as E
X0=-.1735;R0=.0375
NSEG=24   # polygon sides of the circumscribed circles
DIMS=dict(h_lo=.019,h_hi=.025,boot_r=.008,boot_l=.012,embed=.003,cable_r=.0032,bend_R=.050+.0032,run=.020,keepout=.100)
DIMS_SRC=dict(
 h_lo='E: exit height band low end (cable axis above the bottom face); 21.1 mm measured on DH drawings, 22-24 mm on a photo',
 h_hi='E: band high end',
 boot_r='E: boot about Ø11.7-15.8 measured on the DH drawing, rounded up to Ø16',
 boot_l='S: "12" (boot protrusion) dimensioned on the PGC-140-50 drawing, DH PGC parameter sheet CN.2405 p.6 / Electric Gripper Brochure 2024 p.17',
 embed='E: modelling only (the boot shape starts inside the housing shape)',
 cable_r='S: cable Ø6.4, same drawings',
 bend_R='S: "Cable allowable bending radius R50mm", same drawings; read as the inside radius -> centreline 53.2 mm (E, the reading that reaches further out)',
 run='E: 20 mm of straight cable after the bend for the first tie',
 keepout='S: "Secure at least 100mm", same drawings')
SIDES={'yp':0.,'ym':180.}   # exit toward +y (under the jaw on the +y side) / -y; the gripper can be mounted either way (180 deg about its axis: symmetric jaws)
ROUTINGS={'both_dn':dict(sides=('yp','ym'),dress='dn',note='default, conservative: the side is a mounting choice, so both; DH drawing bend (down)'),
 'yp_dn':dict(sides=('yp',),dress='dn'),'ym_dn':dict(sides=('ym',),dress='dn'),
 'yp_fl':dict(sides=('yp',),dress='fl'),'ym_fl':dict(sides=('ym',),dress='fl'),
 'yp_k100':dict(sides=('yp',),dress='k100'),'ym_k100':dict(sides=('ym',),dress='k100')}
# routing study (R19_CABLE.md 4): dressing direction a<deg> = cos(a) * (-x, down) + sin(a) * (+z, toward the flange side), and the straight
# run after the bend (_r0: the first tie right at the end of the bend; default 20 mm)
for _s in ('yp','ym'):
 for _a in (-45,30,45,60):ROUTINGS[f'{_s}_a{_a}']=dict(sides=(_s,),dress=f'a{_a}')
 for _a in ('dn','fl','a30','a45','a60','a-45'):ROUTINGS[f'{_s}_{_a}_r0']=dict(sides=(_s,),dress=_a,run=0.)
# screening models (several routings at once, each its own group of geoms; never a certificate): ALL = every single-side routing,
# SEL = the short list after the lid / wok screens (R19_CABLE.md 4)
SCREENS={'ALL':[r for r in ROUTINGS if len(ROUTINGS[r]['sides'])==1],'SEL':['yp_dn','ym_dn','yp_fl','yp_fl_r0','yp_a-45','yp_a-45_r0','ym_fl_r0','ym_a-45_r0']}
def fmt(v):return ' '.join(f'{float(x):.9g}' for x in v)
def circle(c,n1,n2,r,n=NSEG):
 """polygon circumscribed about the circle of radius r, centre c, in the plane spanned by unit n1, n2."""
 rr=r/np.cos(np.pi/n);t=2*np.pi*(np.arange(n)+.5)/n;return c+rr*(np.cos(t)[:,None]*n1+np.sin(t)[:,None]*n2)
def prism(p0,p1,r):
 """vertices whose hull encloses the cylinder of radius r on the segment p0 -> p1."""
 p0=np.asarray(p0,float);p1=np.asarray(p1,float);a=p1-p0;a/=np.linalg.norm(a)
 n1=np.cross(a,[1.,0,0]) if abs(a[0])<.9 else np.cross(a,[0,1.,0]);n1/=np.linalg.norm(n1);n2=np.cross(a,n1)
 return np.r_[circle(p0,n1,n2,r),circle(p1,n1,n2,r)]
def bend(P1,u,v,Rb,r,arcs=3,step_deg=5.):
 """the tube of radius r whose centreline leaves P1 along u and turns (centreline radius Rb) to the direction v (v perp. u):
 `arcs` pieces, each the hull of cross-sections every <= step_deg, inflated by the outer-fibre sagitta between sections."""
 C=P1+Rb*v;out=[]
 for k in range(arcs):
  a0,a1=np.radians(90.*k/arcs),np.radians(90.*(k+1)/arcs);m=int(np.ceil(np.degrees(a1-a0)/step_deg));ph=np.linspace(a0,a1,m+1)
  sag=(Rb+r)*(1-np.cos((a1-a0)/m/2));V=[]
  for p in ph:
   c=C-Rb*np.cos(p)*v+Rb*np.sin(p)*u;tng=np.cos(p)*u+np.sin(p)*v;n2=np.cross(tng,np.cross(u,v));n2/=np.linalg.norm(n2);n1=np.cross(n2,tng)
   V.append(circle(c,n1,n2,r+sag))
  out.append(np.vstack(V))
 return out,P1+Rb*u+Rb*v   # (pieces, centreline end point)
def side_shapes(side,dress,D=DIMS,run=None):
 """{piece: vertices} for one side, the hull over the exit-height band (vertices at both ends of the band)."""
 t=np.radians(SIDES[side]);u=np.array([0.,np.cos(t),np.sin(t)]);x_=np.array([1.,0,0])
 v={'dn':-x_,'fl':np.array([0.,0,1.])}.get(dress)
 if dress.startswith('a'):a_=np.radians(float(dress[1:]));v=np.cos(a_)*-x_+np.sin(a_)*np.array([0.,0,1.])   # between down (0) and the flange side (90)
 if run is not None:D=dict(D,run=run)
 S={}
 for h in (D['h_lo'],D['h_hi']):
  b=np.array([X0+h,0,0]);T={}
  if dress=='k100':
   Rk=D['keepout']-D['boot_l']-D['cable_r'];x_lo=X0+D['h_lo']-Rk-D['run'];w=np.array([0,-np.sin(t),np.cos(t)])*D['boot_r']   # largest centreline radius that keeps the outer surface within 100 mm
   ra,rb=R0-D['embed'],R0+D['keepout'];xs=(x_lo,X0+D['h_hi']+D['boot_r'])
   T['k100']=np.array([[x,0,0]+r*u+s*w for x in xs for r in (ra,rb) for s in (-1,1)])
  else:
   T['boot']=prism(b+(R0-D['embed'])*u,b+(R0+D['boot_l'])*u,D['boot_r'])
   P1=b+(R0+D['boot_l'])*u;pcs,P2=bend(P1,u,v,D['bend_R'],D['cable_r'])
   for k,P in enumerate(pcs):T[f'bend{k}']=P
   if D['run']>0:T['run']=prism(P2,P2+D['run']*v,D['cable_r'])
  for k,V in T.items():S[k]=V if k not in S else np.r_[S[k],V]
 return S
def shapes(routing):
 R=ROUTINGS[routing];S={}
 for s in R['sides']:
  for k,V in side_shapes(s,R['dress'],run=R.get('run')).items():S[f'{s}_{k}']=V
 return S
def add(tree,routing):
 """Put the shapes on R_tool (same pos as R_gripper_oem_envelope, i.e. the finger-design shift). routing: a ROUTINGS key,
 or 'ALL' (every single-side routing at once, named R_pgc_cable.<routing>.<piece>: a SCREENING model, never a certificate)."""
 tool=tree.find(".//body[@name='R_tool']");asset=tree.getroot().find('asset');env=tool.find("geom[@name='R_gripper_oem_envelope']")
 pos=env.get('pos','0 0 0') if env is not None else '0 0 0'
 for rt in (SCREENS[routing] if routing in SCREENS else [routing]):
  for pc,V in shapes(rt).items():
   nm=f'R_pgc_cable.{rt}.{pc}' if routing in SCREENS else f'R_pgc_cable_{pc}'
   E.SubElement(asset,'mesh',name='M_'+nm,vertex=' '.join(fmt(v) for v in V))
   E.SubElement(tool,'geom',name=nm,type='mesh',mesh='M_'+nm,pos=pos,rgba='.95 .55 .1 1',contype='2',conaffinity='3',mass='.000001')
 return tree
def summary():
 """extents of each routing (tool frame before the shift), for the report."""
 out={}
 for r in ROUTINGS:
  V=np.vstack(list(shapes(r).values()));rad=np.hypot(V[:,1],V[:,2])
  out[r]=dict(pieces=list(shapes(r)),max_radius_from_gripper_axis_mm=round(float(rad.max())*1e3,1),max_out_from_body_surface_mm=round(float(rad.max()-R0)*1e3,1),
   x_range_above_bottom_face_mm=[round(float(V[:,0].min()-X0)*1e3,1),round(float(V[:,0].max()-X0)*1e3,1)],z_range_mm=[round(float(V[:,2].min())*1e3,1),round(float(V[:,2].max())*1e3,1)])
 return out
if __name__=='__main__':
 import json;print(json.dumps(summary(),indent=1))
