"""R14 kitchen additions: cooking is now in scope, so the stove keep-out box goes and
the real range hood, a wok, the seasoning outlet under an upper cabinet, a cup rail on
the backsplash, a rice/flour outlet and (optionally) the fridge are added (all positions
are design proposals; see README R14).
add(tree, cfg) edits a scene.build() tree in place. cfg keys (all optional):
 r14_cup (attach a 60 x 70 mm cup at the TCP, gripper class), r14_drum (pour drum at the TCP),
 r14_drawer / r14_drawer_open (rejected under-counter drawer fridge, kept for its reach evidence),
 r14_fridge (single-door fridge left of the counter run) with r14_fridge_door_deg, r14_held_handle,
 r14_rbin_z (robot door-bin floor height), r14_box_taken, r14_held_box; r15 (+ r15_* keys: kitchen15.py)."""
import numpy as np,xml.etree.ElementTree as E
from scene import box,fmt
from scipy.spatial.transform import Rotation
# --- design positions (world, m); the north counter front edge is y = 0, counter top z = 0.85
HOOD=dict(x=(.69,1.46),y=(.15,.60),z=(1.25,1.35))           # slim hood under the cabinet line
WOK=dict(c=(.83,.17),r=.16,z=(.93,1.02))                      # front-left burner
SEASON_PORT=dict(x=(.50,.60),y=(.30,.46),z=(1.31,1.35))       # outlet manifold under upper_cabinet_1
CUP_RAIL=dict(x=(.47,.69),y=(.545,.60),z=(.925,.945))         # backsplash rail, cups hang in front
CUPS_X=[.50,.57,.64];CUP_Y=.505;CUP_R,CUP_H=.03,.07
STAPLE_PORT=dict(x=(-1.05,-.95),y=(.30,.46),z=(1.31,1.35))    # rice / flour outlet under upper_cabinet_0
DRAWER=dict(x=(-1.80,-1.20),z=(.45,.71),depth=.55,open=.45)   # 60 cm refrigerated drawer unit (top drawer)
# the user's single-door fridge (estimated, user: "单开门的…你估算下"): 0.55 W x 0.60 D x 1.45 H,
# standing left of the counter run, door hinged on the left (away from the counter), vertical
# bar handle near the right edge at 0.95-1.25 m. Shelves and freezer box are set back 0.12 m
# for the door bins (as in real fridges). The robot's cold box (冷藏料盒) sits in a door bin at
# 0.85 m (0.92 m: the lift fails at door 30-35°; 1.00 m: the grasp fails). The docked arm
# can only swing the door to ~55° and cannot reach past the cabinet's own front frame onto
# the shelves (r14reach rounds 1-2), but the door's inner face faces the arm.
# Door-frame coordinates: u from the hinge along the door, v from the door's inner face.
FRIDGE=dict(x=(-2.44,-1.89),y_face=-.05,depth=.60,h=1.45,door_t=.05,bar_x=-1.93,bar_y=-.09,bar_z=(.95,1.25),bar_r=.0125,
 shelves=(.45,.70,.95),freezer=(1.16,1.40),setback=.12,bins_z=(.25,.78),
 rbin=dict(u=(.10,.50),v=(0,.10),z=.85,lip=.06),rbox=dict(u=(.14,.44),v=(.01,.09),h=.10,bar_z=.11,bar_r=.006))
def _rng(a,b):return [(a[0]+a[1])/2,(b[0]+b[1])/2],[a[1]-a[0],b[1]-b[0]]
def add(tree,cfg):
 world=tree.find('worldbody')
 for g in list(world.iter('geom')):
  if g.get('name')=='protected_stove':
   for par in world.iter():
    if g in list(par):par.remove(g);break
 b=lambda n,x,y,z,c=(.8,.8,.8,1):box(world,n,[(x[0]+x[1])/2,(y[0]+y[1])/2,(z[0]+z[1])/2],[x[1]-x[0],y[1]-y[0],z[1]-z[0]],c)
 b('r14_hood',HOOD['x'],HOOD['y'],HOOD['z'],(.93,.92,.86,1))
 b('r14_upper_over_hood',HOOD['x'],(.23,.60),(1.35,1.95),(.6,.42,.25,1))
 # wok as its collision envelope (cylinder) on the burner
 c=WOK['c'];E.SubElement(world,'geom',name='r14_wok',type='cylinder',pos=fmt([c[0],c[1],sum(WOK['z'])/2]),size=fmt([WOK['r'],(WOK['z'][1]-WOK['z'][0])/2]),rgba='.15 .15 .15 1',contype='1',conaffinity='2',mass='.000001')
 b('r14_season_port',SEASON_PORT['x'],SEASON_PORT['y'],SEASON_PORT['z'],(.85,.85,.9,1))
 b('r14_staple_port',STAPLE_PORT['x'],STAPLE_PORT['y'],STAPLE_PORT['z'],(.85,.85,.9,1))
 b('r14_cup_rail',CUP_RAIL['x'],CUP_RAIL['y'],CUP_RAIL['z'],(.7,.7,.72,1))
 for i,x in enumerate(CUPS_X):
  if cfg.get('r14_cup_taken')==i:continue
  E.SubElement(world,'geom',name=f'r14_cup_{i}',type='cylinder',pos=fmt([x,CUP_Y,CUP_RAIL['z'][0]+.005]),size=fmt([CUP_R,CUP_H/2]),rgba='.95 .95 .95 1',contype='1',conaffinity='2',mass='.000001')
 if cfg.get('r14_drawer'):  # rejected R14 option: under-counter drawer fridge (kept for the reach evidence)
  # refrigerated drawer unit replaces the left base cabinets (closed: flush with y = 0)
  for g in list(world.iter('geom')):
   n=g.get('name','')
   if n.startswith('north_cabinet_left'):
    p=np.fromstring(g.get('pos'),sep=' ')
    if p[0]<DRAWER['x'][1]:
     for par in world.iter():
      if g in list(par):par.remove(g);break
  x0,x1=DRAWER['x'];y_open=-DRAWER['open'] if cfg.get('r14_drawer_open') else 0.
  b('r14_fridge_body',(x0,x1),(0.,.60),(0.,DRAWER['z'][0]),(.9,.92,.94,1))
  b('r14_fridge_body_top',(x0,x1),(0.,.60),(DRAWER['z'][1],.82),(.9,.92,.94,1))
  # drawer: front panel + bin (open: pulled toward the aisle)
  b('r14_drawer_front',(x0,x1),(y_open-.02,y_open),DRAWER['z'],(.85,.88,.9,1))
  b('r14_drawer_handle',(x0+.15,x1-.15),(y_open-.05,y_open-.02),(DRAWER['z'][1]-.04,DRAWER['z'][1]-.02),(.6,.6,.6,1))
  if cfg.get('r14_drawer_open'):
   for s in (0,1):b(f'r14_drawer_side{s}',(x0+.01,x0+.02) if s==0 else (x1-.02,x1-.01),(y_open,y_open+DRAWER['depth']),(DRAWER['z'][0],DRAWER['z'][1]-.03),(.85,.88,.9,1))
   b('r14_drawer_floor',(x0+.01,x1-.01),(y_open,y_open+DRAWER['depth']),(DRAWER['z'][0],DRAWER['z'][0]+.01),(.85,.88,.9,1))
   # an R13 slot tray (one item) sitting in the drawer, handle knob facing up
   b('r14_tray',(x0+.08,x1-.08),(y_open+.05,y_open+.35),(DRAWER['z'][0]+.01,DRAWER['z'][0]+.05),(.62,.5,.38,1))
  else:b('r14_drawer_closed',(x0,x1),(0.,.58),DRAWER['z'],(.85,.88,.9,1))
 if cfg.get('r14_fridge'):fridge(tree,world,cfg)
 if cfg.get('r15'):import kitchen15;kitchen15.add(tree,world,cfg)  # R15 cooking station (replaces the r14 wok envelope)
 if cfg.get('r16'):import kitchen16;kitchen16.add(tree,world,cfg)  # R16 second heat zone, lid, carrier, utensils
 if cfg.get('r17'):import kitchen17;kitchen17.add(tree,world,cfg)  # R17 sink rinse: the user's single-lever faucet
 if cfg.get('r14_drum'):
  # 分格转筒 held by its end knob: Ø80 x 140 mm drum along the tool approach axis (wrist roll axis)
  tool=tree.find(".//body[@name='R_tool']");site=tool.find("site[@name='R_prep']")
  p=np.fromstring(site.get('pos','0 0 0'),sep=' ') if site is not None else np.zeros(3)
  E.SubElement(tool,'geom',name='R_gripper_drum',type='cylinder',pos=fmt(p+[.10,0,0]),size='.042 .07',quat='.707106781187 0 .707106781187 0',rgba='.88 .9 .93 1',contype='2',conaffinity='3',mass='.3')
 if cfg.get('r14_cup'):
  tool=tree.find(".//body[@name='R_tool']");site=tool.find("site[@name='R_prep']")
  p=np.fromstring(site.get('pos','0 0 0'),sep=' ') if site is not None else np.zeros(3)
  E.SubElement(tool,'geom',name='R_gripper_cup',type='cylinder',pos=fmt(p),size=fmt([CUP_R,CUP_H/2]),rgba='.95 .95 .95 1',contype='2',conaffinity='3',mass='.05')
 return tree

def fridge(tree,world,cfg):
 """Single-door fridge with the door at cfg['r14_fridge_door_deg'] (0 = closed). The door
 rotates about the hinge (left front corner) and opens toward the aisle (-y). The handle
 bar is left out when cfg['r14_held_handle'] (the gripper holds it: its contact is the grasp)."""
 F=FRIDGE;x0,x1=F['x'];yf=F['y_face'];t=F['door_t'];th=np.radians(cfg.get('r14_fridge_door_deg',0.))
 b=lambda n,x,y,z,c=(.93,.94,.95,1):box(world,n,[(x[0]+x[1])/2,(y[0]+y[1])/2,(z[0]+z[1])/2],[x[1]-x[0],y[1]-y[0],z[1]-z[0]],c)
 # cabinet: back, sides, top, bottom (open front, behind the door plane y = yf + t)
 y0,y1=yf+t,yf+t+F['depth']-t;w=.03
 b('r14_fr_back',(x0,x1),(y1-w,y1),(0,F['h']));b('r14_fr_top',(x0,x1),(y0,y1),(F['h']-w,F['h']));b('r14_fr_bottom',(x0,x1),(y0,y1),(0,.05))
 b('r14_fr_left',(x0,x0+w),(y0,y1),(0,F['h']));b('r14_fr_right',(x1-w,x1),(y0,y1),(0,F['h']))
 sb=F['setback']
 for k,z in enumerate(F['shelves']):b(f'r14_fr_shelf{k}',(x0+w,x1-w),(y0+sb,y1-w),(z-.006,z),(.85,.9,.95,1))
 b('r14_fr_freezer',(x0+w,x1-w),(y0+sb,y1-w),F['freezer'],(.8,.85,.9,1))
 # door (rotated about the hinge at (x0, yf), axis -z so that opening swings it toward -y)
 hinge=np.array([x0,yf+t]);R=np.array([[np.cos(-th),-np.sin(-th)],[np.sin(-th),np.cos(-th)]])
 def door_box(n,cx,cy,cz,hx,hy,hz,c=(.93,.94,.95,1)):
  p=hinge+R@(np.array([cx,cy])-hinge);g=box(world,n,[p[0],p[1],cz],[2*hx,2*hy,2*hz],c)
  g.set('quat',fmt(Rotation.from_euler('z',-th).as_quat()[[3,0,1,2]]));return g
 door_box('r14_fr_door',(x0+x1)/2,yf+t/2,F['h']/2,(x1-x0)/2,t/2,F['h']/2)
 door_box('r14_fr_door_bins',(x0+x1)/2,yf+t+.05,sum(F['bins_z'])/2,(x1-x0)/2-.04,.05,(F['bins_z'][1]-F['bins_z'][0])/2,(.85,.9,.95,1))
 # robot door bin (floor + 60 mm front lip) with the robot's cold box: 0.30 x 0.08 x 0.10 tub with a
 # short bridge bar across its middle, 110 mm above the rim (top-down pinch, no carrying moment;
 # a 30 mm bridge failed: the arm then has to dip past the cabinet's right front edge).
 # The box is left out when cfg['r14_box_taken']; only the bar when cfg['r14_held_box'].
 RB,BX=F['rbin'],F['rbox'];U=lambda u:x0+u;V=lambda v:yf+t+v;zb=cfg.get('r14_rbin_z',RB['z'])
 door_box('r14_fr_rbin_floor',U(sum(RB['u'])/2),V(sum(RB['v'])/2),zb-.003,(RB['u'][1]-RB['u'][0])/2,(RB['v'][1]-RB['v'][0])/2,.003,(.85,.9,.95,1))
 door_box('r14_fr_rbin_lip',U(sum(RB['u'])/2),V(RB['v'][1]-.003),zb+RB['lip']/2,(RB['u'][1]-RB['u'][0])/2,.003,RB['lip']/2,(.85,.9,.95,1))
 if not cfg.get('r14_box_taken'):
  uc,vc=sum(BX['u'])/2,sum(BX['v'])/2
  door_box('r14_fr_rbox',U(uc),V(vc),zb+BX['h']/2,(BX['u'][1]-BX['u'][0])/2,(BX['v'][1]-BX['v'][0])/2,BX['h']/2,(.3,.55,.75,1))
  for sgn in (-1,1):door_box(f'r14_fr_rbox_post{sgn:+d}',U(uc),V(vc+sgn*.038),zb+BX['h']+BX['bar_z']/2,.006,.006,BX['bar_z']/2,(.3,.55,.75,1))
  if not cfg.get('r14_held_box'):door_box('r14_fr_rbox_bar',U(uc),V(vc),zb+BX['h']+BX['bar_z'],BX['bar_r'],.044,BX['bar_r'],(.95,.6,.1,1))
 if not cfg.get('r14_held_handle'):
  door_box('r14_fr_bar',F['bar_x'],F['bar_y'],sum(F['bar_z'])/2,F['bar_r'],F['bar_r'],(F['bar_z'][1]-F['bar_z'][0])/2,(.6,.6,.62,1))
 for z in F['bar_z']:door_box(f'r14_fr_bar_post{z}',F['bar_x'],(F['bar_y']+yf)/2,z,.006,(yf-F['bar_y'])/2,.006,(.6,.6,.62,1))
 # the cart can drive past the counter end: extend the carriage range
 j=tree.find(".//joint[@name='R_carriage_x']")
 if j is not None:j.set('range','-2.6 2.46')
