"""R19 #36 part 2 (new file): the rest of the PGC-140-50 pigtail, its M12 plug junction and the short adapter cable to the
arm's tool connector, as conservative convex enclosing shapes on R_tool, for the routings '<routing>_tc' of r19cable.py
(ROUTINGS[..]['tc']). Report: R19_CABLE2.md. Labels: S = sourced (file / URL), M = measured (sim / CAD), E = estimate.

The whole run from the gripper body to the tool connector is rigid with wrist 3 (the gripper is bolted to the flange and
the connector sits on the wrist-3 housing), so it is a fixed shape on R_tool, like the first cable section of r19cable.py.
It is built in the housing frame H of r19cable.py (the R_tool frame before the finger-design shift; the geoms get the
same pos as R_gripper_oem_envelope, so they stay put relative to the wrist in every finger design):
 1. start: the end of the routing's first section (r19cable.py: boot, R50 bend, 20 mm run to the first tie), on the
    measured exit height (21.0 mm, MEAS) -- the first section itself stays the hull over the 19-25 mm band;
 2. the centreline is a polyline of corner points (ROUTES), every corner filleted with the centreline radius
    R50 + 3.2 = 53.2 mm (DH: "Cable allowable bending radius R50mm", read as the inside radius, as r19cable.py) --
    the same bend rule is used for the adapter cable [E: the adapter cable is assumed no stiffer than DH's];
 3. along it: the pigtail rest (153.0 mm of free cable from the boot tip [S] minus what the first section uses), the
    M12 junction (DH's plug 47.0 mm x dia 16.2 [S] + the adapter cable's straight M12 socket, 43 mm [S, Lumberg
    RKT 8-282] -> taken as one rigid dia 16.2 x 90 mm body, no overlap credited [E]) which must lie on a straight
    part, then the adapter cable (dia 6.4 taken [E]) to the tool-connector plug;
 4. the tool-connector plug (PORTS / PLUGS) as a rigid body on the connector axis.
With junction=False in a route spec (routing 'yp_a-45_tcf') there is no M12 junction: one flexible dia 6.4 cable from the
boot to the plug (a DH pigtail made to length with the arm-side plug [E: DH offers an M8 outlet on request; not published]).
Routes were found by a search (scratch opt_tc.py; R19_CABLE2.md 3) against the static limits and the free-space maps of
r19cable2_free.py, then screened / certified with r19cable2_screen.py / r19cable_check.py.
Every circle is a polygon circumscribed about the true circle (r19cable.circle), every bend a set of hulls of
cross-sections every 5 deg inflated by the outer-fibre sagitta (as r19cable.bend). Names R_pgc_cable_tc_<piece>
(prefix R_pgc_cable: the checker gives them the 5 mm gripper gate; no grasp / food window exempts them; r19tol_core
excludes them from the held part)."""
import numpy as np
STEP_FILE='inputs/dh_cad/step/PGC-140-50-W-S_simple_v4.0_20240814.step'
FLANGE_FILE='inputs/dh_cad/zip_x/PGC-140-50_2D&3D Model/PGC-140-50_标准法兰_v1.0.STEP'
# measured on DH's CAD (R19_CABLE2.md section 1; gmsh 4.15.2 / OpenCASCADE, scratch venv; mm)
MEAS=dict(exit_h=21.00,exit_lateral=0.00,boot_dia=15.50,boot_out=10.50,boot_pocket_r=30.0,cable_dia=6.40,cable_free=153.0,plug_len=47.0,
 plug_dia=16.2,pigtail_total=200.0,body_r=37.50,flange_plate=5.0,flange_dia=75.0,flange_spigot=(31.5,2.5),flange_ears_h=14.9)
MEAS_SRC={k:'S: DH PGC-140-50-W-S simplified STEP v4.0 (2024-08-14), '+STEP_FILE for k in MEAS if not k.startswith('flange')}
MEAS_SRC.update({k:'S: DH PGC-140-50 standard flange STEP v1.0, '+FLANGE_FILE+' (the same flange is inside the gripper STEP: its robot face is the gripper datum X0)' for k in MEAS if k.startswith('flange')})
RB=.050+.0032          # centreline bend radius (m), as r19cable.DIMS['bend_R']
R_CAB=.0032            # cable radius (m): DH pigtail dia 6.4 [S]; adapter cable taken the same [E]
JUNCTION=dict(len=.047+.043,r=.0081,src='S: DH plug 47.0 x dia 16.2 (STEP v4.0) + Lumberg RKT 8-282 straight M12 socket 43 mm (R19_CABLE.md 1); no mating overlap credited [E]')
def unit(v):v=np.asarray(v,float);return v/np.linalg.norm(v)
def arc(P,t,n,Rb,phi,r,max_deg=30.,step_deg=5.):
 """tube of radius r: centreline leaves P along t (unit), turns toward n (unit, perpendicular to t) by phi (rad) at radius
 Rb. Pieces of <= max_deg, each the hull of cross-sections every <= step_deg inflated by the outer-fibre sagitta."""
 C=P+Rb*n;b=np.cross(t,n);k=max(1,int(np.ceil(np.degrees(phi)/max_deg-1e-9)));out=[]
 for j in range(k):
  a0,a1=phi*j/k,phi*(j+1)/k;m=max(1,int(np.ceil(np.degrees(a1-a0)/step_deg-1e-9)));sag=(Rb+r)*(1-np.cos((a1-a0)/m/2));V=[]
  for p in np.linspace(a0,a1,m+1):
   c=C-Rb*np.cos(p)*n+Rb*np.sin(p)*t;V.append(CAB.circle(c,unit(c-C),b,r+sag))
  out.append(np.vstack(V))
 return out
def fillet(Q,Rb=RB):
 """centreline from the corner polyline Q[0] .. Q[-1] with every interior corner filleted at radius Rb. Elements
 ('S', a, b) straight and ('A', P, t, n, phi) arc, in order; asserts every straight is long enough for its fillets."""
 Q=[np.asarray(p,float) for p in Q];n=len(Q)-1;d=[unit(Q[i+1]-Q[i]) for i in range(n)];L=[np.linalg.norm(Q[i+1]-Q[i]) for i in range(n)]
 th=[0.]*(n+1);tl=[0.]*(n+1)
 for i in range(1,n):th[i]=float(np.arccos(np.clip(d[i-1]@d[i],-1,1)));tl[i]=Rb*np.tan(th[i]/2)
 for i in range(n):assert tl[i]+tl[i+1]<=L[i]+1e-6,f'segment {i}: {L[i]*1e3:.1f} mm < fillets {tl[i]*1e3:.1f} + {tl[i+1]*1e3:.1f} mm'
 el=[]
 for i in range(n):
  a=Q[i]+d[i]*tl[i];b=Q[i+1]-d[i]*tl[i+1]
  if (b-a)@d[i]>1e-9:el.append(('S',a,b))
  if i+1<n and th[i+1]>1e-9:el.append(('A',b,d[i],unit(d[i+1]-(d[i+1]@d[i])*d[i]),th[i+1]))
 return el
def length(e):return float(np.linalg.norm(e[2]-e[1])) if e[0]=='S' else RB*e[4]
def at(el,s):
 """point and tangent at arc length s along the elements, and the index of the element."""
 for k,e in enumerate(el):
  l=length(e)
  if s<=l+1e-12:
   if e[0]=='S':t=unit(e[2]-e[1]);return e[1]+t*s,t,k
   _,P,t,n,phi=e;p=s/RB;C=P+RB*n;return C-RB*np.cos(p)*n+RB*np.sin(p)*t,np.cos(p)*t+np.sin(p)*n,k
  s-=l
 raise ValueError('beyond the end')
def route(Q,rigid=(),r=R_CAB):
 """shapes of a cable along the filleted corner polyline Q (H frame, m): {piece: vertices}, the elements and the length.
 rigid: (s0, s1, radius, name) bodies on the centreline between arc lengths s0 and s1 from Q[0]; each must lie on one
 straight element (a plug cannot bend)."""
 el=fillet(Q);S={}
 for i,e in enumerate(el):
  if e[0]=='S':S[f'c{i:02d}']=CAB.prism(e[1],e[2],r)
  else:
   for j,V in enumerate(arc(e[1],e[2],e[3],RB,e[4],r)):S[f'c{i:02d}{"abcdefgh"[j]}']=V
 for s0,s1,rr,nm in rigid:
  p0,_,k0=at(el,s0);p1,_,k1=at(el,s1)
  assert k0==k1 and el[k0][0]=='S',f'{nm}: {s0*1e3:.1f}..{s1*1e3:.1f} mm is not on one straight element'
  S[nm]=CAB.prism(p0,p1,rr)
 return S,el,sum(length(e) for e in el)
# ---------------------------------------------------------------- the arm's tool connector and the plug on it
# The connector pose is given in the arm's own wrist-3 frame and moved into H with the tool pose the scene uses (for the
# FR5: arms.swap's flange -> tool transform with its spacer and clocking), so the run always ends on the connector.
PORTS={
 'ur5e':dict(frame='w3',p=[0.,.06737,.0435],axis=[0.,0.,1.],plug='m8ra',
  what='UR e-Series tool connector, M8 8-pin (Lumberg RKMW 8-354; male before 1 Sep 2024, female after; RS485 + 24 V)',
  src='M: Menagerie UR5e wrist3.obj (UR mesh): bump of dia ~9.8 at y_w3 67.37 mm (31.57 mm behind the mesh flange face 98.94), '
      'radial (+z_w3), top at r 43.5; S: UR5e tool drawing, connector axis 31.55 mm from the flange face, radial, on the dowel-hole '
      'line, https://www.universal-robots.com/media/1833559/ur5e-tool-drawing.jpg'),
 'fr5':dict(frame='fr5_w3',p=[0.,-.0400,.0790],axis=[0.,-1.,0.],plug='m12ra',
  what='Fairino FR5 end RS485 connector, 5-pin (485-A, 485-B, 24 V, GND); the 8-pin M12 end I/O connector has no RS485',
  src='M: Fairino FR5 wrist3_link.STL (frcobot_ros2 fairino5_v6): dia ~14.6 socket face with 5 contacts at -90 deg (DH frame 6 '
      'x = 0 deg), centre z 79.0 mm (21 mm behind the flange at 100), flush with the dia 80 housing; the 8-contact face at 180 deg is '
      'the M12 I/O; S: pinouts, Fairino Cobots manual 3.5.4, https://fairino-doc-en.readthedocs.io/latest/CobotsManual/installation.html')}
PLUGS={   # right-angle cable plugs as boxes: along the connector axis from the mating face (-2 mm embedded .. top), along the cable
          # exit direction (-back .. run, from the connector axis), +-half across; +1 mm on every side [E]; cable leaves at (exit_h, run)
 'm8ra':dict(top=.018,back=.0045,run=.024,half=.0054,exit_h=.0126,
  src='S: Binder 77 3408 0000 50008 M8 8-pin right-angle (about 18 mm mating face to top, head 10.8 thick, 24 mm axis to strain '
      'relief end, 4.5 mm behind the axis), https://www.binder-connector.com/prod_media/masszeichnung_produktzeichnung/77-3408-0000-WD08.jpg; '
      'the male version for post-2024 UR robots is taken the same [E]'),
 'm12ra':dict(top=.0266,back=.00725,run=.031,half=.00725,exit_h=.0266-.00725,
  src='S: Lumberg RKWT 8-282 M12 right-angle (26.6 mm to the mating face, 31 mm axis to overmould end, dia 14.5; R19_CABLE.md 1); '
      'taken for the FR5 5-pin RS485 plug [E: the FR5 connector type is not published]')}
def _pose(el):
 from scipy.spatial.transform import Rotation
 p=np.fromstring(el.get('pos','0 0 0'),sep=' ');q=np.fromstring(el.get('quat','1 0 0 0'),sep=' ');X=np.eye(4)
 X[:3,:3]=Rotation.from_quat(q[[1,2,3,0]]/np.linalg.norm(q)).as_matrix();X[:3,3]=p;return X
def h_frame(tree):
 """H (housing frame) in R_tool's parent frame (the UR wrist 3 of base.xml; arms.swap moves R_tool later): R_tool's pose
 times the finger-design shift that its geoms carry (pos of R_gripper_oem_envelope)."""
 tool=tree.find(".//body[@name='R_tool']");env=tool.find("geom[@name='R_gripper_oem_envelope']")
 X=_pose(tool);X[:3,3]=X[:3,3]+X[:3,:3]@np.fromstring(env.get('pos','0 0 0'),sep=' ');return X
def port_H(arm,tree):
 """(mating-face centre, outward axis, port key) of the arm's tool connector in H."""
 import arms
 from scipy.spatial.transform import Rotation
 spec=arms.ARMS[arm];XH=h_frame(tree)
 if spec.get('model')=='fr5':
  k='fr5';Xs=_pose(tree.find(".//site[@name='R_attachment_site']"));Rz=np.eye(4);Rz[:3,:3]=Rotation.from_euler('z',spec['clock_deg'],degrees=True).as_matrix()
  Sp=np.eye(4);Sp[2,3]=spec.get('tool_spacer_m',0.);Xfl=Sp@Rz@np.linalg.inv(Xs)@XH   # H in the FR5 flange frame (arms.swap)
  M=np.linalg.inv(Xfl);p=np.array(PORTS[k]['p'])-[0,0,.1]   # FR5 flange frame = wrist-3 frame + (0, 0, 0.1) (r19/arm_fr5.json 'flange')
 elif spec.get('model') is None:k='ur5e';M=np.linalg.inv(XH);p=np.array(PORTS[k]['p'])
 else:raise KeyError(f'no tool-connector data for {arm}')
 return M[:3,:3]@p+M[:3,3],M[:3,:3]@np.array(PORTS[k]['axis']),k
def plug(P,a,e,key):
 """box hull of a right-angle plug on the port (P mating face, a outward axis), cable leaving along e (made perpendicular to
 a); returns vertices, the cable exit point and direction."""
 g=PLUGS[key];e=unit(e-(e@a)*a);w=np.cross(a,e);mg=.001
 V=np.array([P+a*x+e*y+w*z for x in (-.002,g['top']+mg) for y in (-g['back']-mg,g['run']+mg) for z in (-g['half']-mg,g['half']+mg)])
 return V,P+a*g['exit_h']+e*g['run'],e
# ---------------------------------------------------------------- the run
def start(base):
 """end of the first section of the single-side routing `base` (r19cable.ROUTINGS) on the measured exit height: the first-tie
 point T, the cable direction there, and the pigtail length the first section uses (from the boot tip)."""
 R=CAB.ROUTINGS[base];D=CAB.DIMS;run=R.get('run',D['run']);t=np.radians(CAB.SIDES[R['sides'][0]]);u=np.array([0.,np.cos(t),np.sin(t)]);x_=np.array([1.,0,0])
 dr=R['dress'];v={'dn':-x_,'fl':np.array([0.,0,1.])}.get(dr)
 if dr.startswith('a'):a_=np.radians(float(dr[1:]));v=np.cos(a_)*-x_+np.sin(a_)*np.array([0.,0,1.])
 P1=np.array([CAB.X0+MEAS['exit_h']/1e3,0,0])+(CAB.R0+D['boot_l'])*u;T=P1+D['bend_R']*(u+v)+run*v
 used=(D['boot_l']-MEAS['boot_out']/1e3)+np.pi/2*D['bend_R']+run
 return T,v,used
# ---------------------------------------------------------------- routes (corner points in H, mm, between the first tie and the plug)
# ROUTES[key] = {'_base': <first-section routing of r19cable.ROUTINGS>, '_screen': <in the screening set TC>, '_note': ..,
#  <port>: dict(lead=<mm along the first-section direction from the tie to the first corner>, mid=[corners, H mm],
#  exit=<plug cable-exit direction in H>, tail=<mm straight out of the plug's cable exit to the last corner>)}
ROUTES={}
# Found by a search over the run's free parameters (direction of the M12 junction on the cone the pigtail rest allows,
# corners, plug clocking, tail) that ranks valid runs by: reach about J6 + 2 x (45 mm - lowest point along J6)+ + 0.1 x length
# + 400 x the share of a J5 x J6 grid (9 x 12 deg) where the run meets wrist 1; hard limits: housing >= 2 mm, fingers >= 10,
# wrist 3 >= 2 (plug excluded: it sits on the port), wrist 2 over a whole J6 turn >= 3 (scratch opt_tc.py; R19_CABLE2.md 3).
ROUTES['yp_a-45_tc']={'_base':'yp_a-45','_screen':True,'_note':'the adopted first section (R19 #36 decision) continued to the tool connector',
 'ur5e':dict(lead=25.446,mid=[[-230.41,3.25,-226.61],[-149.63,-88.0,-125.48]],exit=[0.40002,0.0,-0.91651],tail=39.59),
 'fr5':dict(lead=25.446,mid=[[-257.44,-27.54,-202.65],[-128.15,-127.02,-42.11]],exit=[0.47125,-0.84979,-0.23619],tail=41.84)}
ROUTES['yp_a-45_tcf']={'_base':'yp_a-45','_screen':True,'_note':'the adopted first section continued as ONE flexible cable to the tool connector: '
 'no M12 junction on the wrist (a DH pigtail made to length with the arm-side plug; R19_CABLE2.md 3); found with the free-space maps (r19cable2_free.py)',
 'ur5e':dict(lead=25.446,mid=[[-224.28, 58.46, -145.96], [-114.8, -54.57, -57.84]],exit=[-0.02063, 0.0, -0.99979],tail=23.56,junction=False),
 'fr5':dict(lead=25.446,mid=[[-224.93, 182.76, -211.92], [-101.12, 122.77, -98.01]],exit=[0.86543, 0.25075, -0.43376],tail=57.19,junction=False)}
ROUTES['yp_a-45_r0_tc']={'_base':'yp_a-45_r0','_screen':True,'_note':'alternative: the same outlet and bend, first tie at the end of the bend (r0)',
 'ur5e':dict(lead=39.125,mid=[[-188.9,-89.15,-191.76]],exit=[0.45807,0.0,-0.88892],tail=38.81),
 'fr5':dict(lead=35.885,mid=[[-232.97,-95.16,-163.42]],exit=[0.59958,-0.74175,-0.30051],tail=61.13)}
def build(key,arm,tree,r=R_CAB):
 """{piece: vertices in H}, info. The route: T (start(base)) -> lead along the first-section direction -> mid corners ->
 tail straight into the plug's cable exit; every corner filleted at RB; the M12 junction placed where the pigtail ends."""
 P,a,pk=port_H(arm,tree)
 if pk not in ROUTES[key]:raise KeyError(f'route {key} has no run to the {pk} tool connector')
 spec=ROUTES[key][pk];T,v,used=start(ROUTES[key]['_base'])
 V,E,e=plug(P,a,np.asarray(spec['exit'],float),PORTS[pk]['plug'])
 Q=[T,T+v*spec['lead']/1e3]+[np.asarray(c,float)/1e3 for c in spec['mid']]+[E+e*spec['tail']/1e3,E]
 rest=MEAS['cable_free']/1e3-used
 J=JUNCTION if spec.get('junction',True) else dict(len=0.,r=r)   # junction=False: a flexible cable all the way (no M12 junction on the run)
 S,el,L=route(Q,rigid=[(rest,rest+J['len'],J['r'],'junction')] if J['len'] else [],r=r)
 S['plug']=V
 info=dict(port=pk,length_mm=round(L*1e3,1),pigtail_rest_mm=round(rest*1e3,2),adapter_cable_mm=round((L-rest-J['len'])*1e3,1) if J['len'] else None,pigtail_from_boot_tip_mm=None if J['len'] else round((L+used-(CAB.DIMS['boot_l']-MEAS['boot_out']/1e3))*1e3,1),
  T_mm=(T*1e3).round(2).tolist(),port_mm=(P*1e3).round(2).tolist(),plug_exit_mm=(E*1e3).round(2).tolist(),
  elements=[(e_[0],round(length(e_)*1e3,1)) for e_ in el])
 return S,info
import r19cable as CAB   # at the end: r19cable imports this module for ROUTES (either import order works)
