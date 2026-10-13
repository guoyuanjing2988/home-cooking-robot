"""R19 prep audit step 3 (GitHub #38): objects for the basket, soak-tub and output-transfer sets (new file;
kitchen19.py is not changed). Registered in kitchen16.OBJ / kitchen19.JAW / kitchen19.MASS on import, so
r19prepchain.py, r19prep_verify.py and kitchen19.add() can hold them or lay them in the world (cfg['r19']
objs). All sizes and masses are ESTIMATES (design proposals), nothing is a measured product.

Grasp (all containers here): an R13-class keyed 30 mm knob on a side strut, taken END-ON along the handle
(approach toward the container axis, jaws horizontal across the strut). The pour is then a roll about the
approach axis (a wrist-3 roll), as the checked spider (R16/R17, tip 110 deg about its handle) and the R19
cups (roll about the lug). Differences to the R13 CAD basket (cad_r13.basket, softfoods 'bulk'):
 - the R13 knob was gripped top-down with the jaws along the handle; here the jaws close across the handle
   (keyed V grooves on the two side faces instead), the pour axis (the handle axis) is the same;
 - the strut is longer: knob centre KNOB_OUT = 60 mm outside the wall (R13: 35 mm), because the PGC's
   fingertips reach 30 mm past the TCP and the R12 D fingers are 13 mm thick: with the R13 knob the open
   finger would stand 5 mm from (or in) the basket wall.

Objects (frame = bottom centre of the floor, container axis = z, handle along +x):
 basket       R13 side-handle wash basket: Ø220 x 100 mm, drain holes (not modelled), keyed knob. Held as an
              envelope of basket + contents: walls, floor and a content cylinder up to the rim (the contents
              never stick out of the model; a closed top is conservative for everything outside).
 basket_open  the same basket without the content cylinder (lying in the world, food is dropped into it).
 tub          soak tub: round stainless basin, inner Ø250 x 75 mm (the Ø220 basket fits with 15 mm radial
              play; with the basket seated the basket strut passes 15 mm over the tub rim), same knob.
              The R19 prep audit proposed a GN 1/3 pan (325 x 176 mm): the Ø220 basket does not fit in 176 mm.
 bowl         prep / staging bowl Ø200 x 90 mm with the same strut + knob (target of the pours).
 ctray        lever-base catch tray: 110 x 120 x 50 mm open tray that sits under the AY-403 blade plate (the
              wedges fall into it), keyed knob on a front lug; pulled out toward the robot.
Masses [est]: basket 0.35 kg, tub 0.50 kg, bowl 0.30 kg, catch tray 0.15 kg (stainless / PP sheet estimates).
Water: density 998 kg/m3 at 20 C (see R19_PREP_STEP3.md for the source)."""
import numpy as np
import kitchen16 as K,kitchen19 as K19
I3=np.eye(3)
KNOB_OUT=.06                              # knob centre outside the outer wall (m)
KNOB=dict(h=(.02,.015,.015))              # knob half sizes: along the handle (x), across (y = jaw axis), height
STRUT=dict(hy=.012,hz=.006)               # strut half width (y), half thickness (z); its top is at the rim
RHO_W=998.                                # kg/m3 water at 20 C
BASKET=dict(R=.11,H=.10,t=.003)
TUB=dict(R=.127,H=.075,t=.002,water_h=.055,zs=.075-.05)   # tub knob on a LOW side bracket (strut top 50 mm under the rim, knob top 20 mm under it): a seated basket's strut and fingers pass over it
BOWL=dict(R=.10,H=.09,t=.003)
SBOWL=dict(R=.085,H=.09,t=.003)          # the slicer out bowl (R11 vessel r .085 x .09) with the same strut + knob
CTRAY=dict(X=.055,Y=.06,H=.05,t=.003,lug=.045)
MASS_EST=dict(basket=.35,tub=.50,bowl=.30,sbowl=.25,ctray=.15)
def _ring(pre,R,H,t,n=12,z0=0.):
 """n wall boxes on a circle (outer radius R, thickness t) from z0 to z0+H."""
 out=[];hl=R*np.tan(np.pi/n)
 for k in range(n):
  a=2*np.pi*(k+.5)/n;c,s=np.cos(a),np.sin(a)
  Rz=np.array([[c,-s,0],[s,c,0],[0,0,1.]]);out.append((f'{pre}_w{k}','box',[(R-t/2)*c,(R-t/2)*s,z0+H/2],[t/2,hl,H/2],Rz))
 return out
def _handle(pre,R,H,zs=None):
 """strut from the wall to the knob (strut top at zs, default the rim) + the keyed knob on it (the grip part)."""
 zs=H if zs is None else zs;kx=R+KNOB_OUT;sx0=R-.004;sx1=kx+KNOB['h'][0]
 return [(f'{pre}_strut','box',[(sx0+sx1)/2,0,zs-STRUT['hz']],[(sx1-sx0)/2,STRUT['hy'],STRUT['hz']],I3),
  (f'{pre}_knob','box',[kx,0,zs+KNOB['h'][2]],list(KNOB['h']),I3)],np.array([kx,0,zs+KNOB['h'][2]])
def container(name,R,H,t,content=None,zs=None):
 parts=[(f'p3_{name}_floor','cylinder',[0,0,t/2],[R,t/2],I3)]+_ring(f'p3_{name}',R,H,t)
 if content:parts.append((f'p3_{name}_content','cylinder',[0,0,t+content/2],[R-t-.002,content/2],I3))
 hp,grip=_handle(f'p3_{name}',R,H,zs);return parts+hp,grip
def _ctray():
 X,Y,H,t,lug=CTRAY['X'],CTRAY['Y'],CTRAY['H'],CTRAY['t'],CTRAY['lug']
 P=[('p3_ctray_floor','box',[0,0,t/2],[X,Y,t/2],I3),('p3_ctray_wxm','box',[-X+t/2,0,H/2],[t/2,Y,H/2],I3),('p3_ctray_wxp','box',[X-t/2,0,H/2],[t/2,Y,H/2],I3),
  ('p3_ctray_wyb','box',[0,Y-t/2,H/2],[X,t/2,H/2],I3),('p3_ctray_wyf','box',[0,-Y+t/2,H/2],[X,t/2,H/2],I3),
  ('p3_ctray_lug','box',[0,-Y-lug/2,H-.006],[.012,lug/2+.002,.006],I3)]
 grip=np.array([0,-Y-lug,H+KNOB['h'][2]]);P.append(('p3_ctray_knob','box',grip.tolist(),[KNOB['h'][1],KNOB['h'][0],KNOB['h'][2]],I3))   # knob turned with the lug (jaws along x)
 return P,grip
def _register():
 for name,(R,H,t),cont,zs in (('basket',(BASKET['R'],BASKET['H'],BASKET['t']),BASKET['H']-BASKET['t'],None),('basket_open',(BASKET['R'],BASKET['H'],BASKET['t']),None,None),
   ('tub',(TUB['R'],TUB['H'],TUB['t']),None,TUB['zs']),('bowl',(BOWL['R'],BOWL['H'],BOWL['t']),None,None),('sbowl',(SBOWL['R'],SBOWL['H'],SBOWL['t']),None,None)):
  pre=name.replace('_open','')
  parts,grip=container(pre,R,H,t,cont,zs)
  if name=='basket_open':parts=[(n.replace('p3_basket','p3_basketo'),*r) for n,*r in parts]
  K.OBJ[name]=dict(parts=parts,grip=grip,a=np.array([-1.,0,0]),j=np.array([0,1.,0]),grip_part=[n for n,*_ in parts if n.endswith('_knob')][0])
  K19.JAW[name]=0.;K19.MASS[name]=MASS_EST[pre]
 P,g=_ctray();K.OBJ['ctray']=dict(parts=P,grip=g,a=np.array([0,1.,0]),j=np.array([1.,0,0]),grip_part='p3_ctray_knob');K19.JAW['ctray']=0.;K19.MASS['ctray']=MASS_EST['ctray']
_register()
def water_kg(R_in,h):return float(RHO_W*np.pi*R_in**2*h)
def knob_world(name,R,p):return np.asarray(p,float)+np.asarray(R,float)@K.OBJ[name]['grip']
def at_knob(name,Rw,knob):
 """Object pose (R, p) that puts its knob at the world point knob with rotation Rw."""
 return np.asarray(Rw,float),np.asarray(knob,float)-np.asarray(Rw,float)@K.OBJ[name]['grip']
def rolled_about_knob(name,R,p,deg):
 """The object rolled deg about its handle axis through the knob (the grasp approach axis): a wrist-3 roll."""
 from scipy.spatial.transform import Rotation
 g=knob_world(name,R,p);ax=np.asarray(R,float)@K.OBJ[name]['a'];Rr=Rotation.from_rotvec(ax*np.radians(deg)).as_matrix()
 return Rr@np.asarray(R,float),g+Rr@(np.asarray(p,float)-g)
# ---- layout proposals (step 3): where the containers stand (checked by the chains / screened in r19prep3_screen.py) ----
WORK=np.array([-0.86,.24,K19.COUNTER_TOP])     # the fetched-tool work spot (kitchen19.LAYOUT lever origin (-0.86, 0.21)); container centre 3 cm further back
def drop_out_bowl(tree):
 """Remove kitchen19's plain slicer out bowl (body r19_slicer_out_bowl) from a built tree: the step-3 'sbowl'
 (the same R11 vessel size with a strut + knob) takes its place."""
 w=tree.find('worldbody')
 for b in list(w.findall('body')):
  if b.get('name')=='r19_slicer_out_bowl':w.remove(b)
 return tree
