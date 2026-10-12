"""Full conservative GROHE 33281003 exterior, handle/spout sweeps and hoses.

Primary dimension drawing 3328130J identifies ECN 33281003 (20 Jan 2022).
225mm open handle,180mm shut handle,177mm spout top,146mm outlet,
227mm projection,51mm base,140deg spout and +/-55deg handle travel.
No collision mesh is made smaller than the drawing profile. The undimensioned
cast outline is covered by a broad polygon, 60mm full width (base is51mm).
Default covers all swivel positions. Explicit operating-state studies retain
the same complete profile at the recorded spout angle; they never earn an
all-swivel-position guarantee and require that state at operation start.
"""
import math
import numpy as np
import model as old
def replace(root,c):
 for p in root.iter():
  for g in list(p.findall('geom')):
   if g.get('name') in ('faucet_riser','sensor_faucet_stem','sensor_faucet_spout'):p.remove(g)
 fc=c['replacement_faucet']
 if fc.get('mount_type')=='wall':
  from faucet_wall_v3_r07 import install
  install(root,c);return
 w=root.find('worldbody');x,y=fc['deck_xy_m'];yaw=math.radians(fc['yaw_deg']);z=.85
 def box(name,lo,hi):
  lo=np.array(lo);hi=np.array(hi)
  old.box(w,'faucet_v3_'+name,(lo+hi)/2,hi-lo,robot=False,color=(.65,.69,.72,1))
 box('body',[x-.0255,y-.0255,z],[x+.0255,y+.0255,z+.180])
 # Full lever +/-55deg rotation and lift: a conservative120mm radial cover.
 box('handle_sweep',[x-.045,y-.120,z+.135],[x+.120,y+.120,z+.225]) if abs(yaw)<1e-8 else None
 if abs(yaw)>=1e-8:
  corners=np.array([[a,b] for a in (-.045,.120) for b in (-.120,.120)])
  r=np.array([[math.cos(yaw),-math.sin(yaw)],[math.sin(yaw),math.cos(yaw)]])
  pts=corners@r.T+[x,y];box('handle_sweep',[*pts.min(0),z+.135],[*pts.max(0),z+.225])
 # Conservative exterior profile, in radial/vertical coordinates. Each of
 # 28 angular cells encloses ALL angles analytically (not sparse samples).
 profile=[(.000,.030),(.025,.030),(.105,.100),(.220,.139),(.249,.139),(.249,.178),(.190,.180),(.090,.145),(.015,.083)]
 # Piecewise axial boxes include full casting between the published extents.
 sections=[(.0,.07,.03,.145),(.06,.15,.075,.176),(.14,.249,.13,.180)]
 cells=[(-70+k*5,-65+k*5) for k in range(28)]
 if fc.get('spout_state')=='nominal_fixed_during_operation':cells=[(0,0)]
 for k,(deg_a,deg_b) in enumerate(cells):
  a=yaw+math.radians(deg_a);b=a if deg_a==deg_b else a+math.radians(5)
  for j,(r0,r1,h0,h1) in enumerate(sections):
   # r*cos(theta)-t*sin(theta), r*sin(theta)+t*cos(theta), |t|<=.03.
   points=[]
   for rr in (r0,r1):
    for tt in (-.030,.030):
     angles=[a,b]
     for base in (math.atan2(-tt,rr),math.atan2(rr,tt)):
      angles += [base+n*math.pi for n in range(-4,5) if a<=base+n*math.pi<=b]
     points += [[x+rr*math.cos(t)-tt*math.sin(t),y+rr*math.sin(t)+tt*math.cos(t)] for t in angles]
   pts=np.array(points);box(f'spout_sweep_{k}_{j}',[*pts.min(0),z+h0],[*pts.max(0),z+h1])
 box('shank',[x-.0165,y-.0165,z-.060],[x+.0165,y+.0165,z])
 box('fixing_nut',[x-.033,y-.033,z-.103],[x+.033,y+.033,z-.055])
 # Both complete supply hoses (635mm max below deck drawing). Installation
 # routes them straight down the dry counter cabinet, inside this80mm duct.
 box('supply_hose_duct',[x-.040,y-.040,z-.635],[x+.040,y+.040,z-.100])
 # DFRobot FIT0498:70x57x45mm,12V/0.42A, normally closed (manufacturer).
 # Full150x120x110mm dry service enclosure includes valve, hose fittings and
 # wire clearance; hydraulic response and potable-material approval untested.
 box('water_valve_service',[x-.075,y-.060,.10],[x+.075,y+.060,.21])
