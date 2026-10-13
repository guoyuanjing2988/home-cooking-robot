"""R19 #36 part 2: static checks of the tool-connector runs (r19cable2_tc.py) that the path checker cannot see (new file).
r19cable_static.one(arm) unchanged (every R_pgc_cable* geom: vs wrist 3, fingers, held objects of the 5 adopted chains,
wrist 2 over the whole J6 turn, wrist 1 over J5 x J6, radial reach), plus, because the run passes the gripper body:
 - the run (R_pgc_cable_tc_*) vs the housing R_gripper_oem_* (same body R_tool: never checked by the checker);
 - wrist 3 split into the plug (it sits on the tool connector, which is part of the wrist-3 shapes) and the rest;
 - the route data (r19cable2_tc.build: length, pigtail rest, adapter-cable length, plug exit).
Distances: the checker's own lower bound (distance.Bounds.pair, GJK) in mm.
python r19cable2_static.py ARMS=<arm>[,<arm>..] -> results/r19/cable/static2.json (merged per arm)"""
import sys,os,json
sys.path.insert(0,'.')
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
def extra(arm):
 os.environ['ARM']=arm
 import numpy as np,chain,arms,r19cable as CAB,r19cable2_tc as TC
 from scene import build
 from checker import Checker
 import kitchen16 as K
 from r19enc_check import meshheld
 import xml.etree.ElementTree as E
 K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);K.TOOL_XY['spatula']=(-1.15,.30);K.SPAT_ELEV=8.;K.SPAT_YAW=0.;K.SPAT_ROLL=180.
 info={}
 orig=arms.swap
 def swap(tree,a):   # route data from the same tree add() sees
  info.update(TC.build(CAB.ROUTINGS[arms.ARMS[a]['cable']]['tc'],a,tree)[1]);return orig(tree,a)
 arms.swap=swap
 try:cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None});tree,meta=build(cfg,None)
 finally:arms.swap=orig
 meshheld(tree);ch=Checker(tree,meta);m,d=ch.m,ch.d
 import mujoco;mujoco.mj_kinematics(m,d)
 nm=ch.gnames;tc=[g for g,n in enumerate(nm) if n.startswith('R_pgc_cable_tc_')];hous=[g for g,n in enumerate(nm) if n.startswith('R_gripper_oem')]
 w3=[g for g in range(m.ngeom) if ch.robot[g] and m.geom_bodyid[g]==m.body('R_arm_wrist_3_link').id and m.geom_type[g]!=0]
 def mind(A,B):
  best=(1e9,None)
  for a in A:
   for b in B:
    v=ch.bounds.pair(a,b)['lower_m']
    if v<best[0]:best=(v,(nm[a],nm[b]))
  return dict(min=round(best[0]*1e3,2),pair=best[1])
 plug=[g for g in tc if nm[g]=='R_pgc_cable_tc_plug']
 return dict(route=info,tc_vs_housing_mm=mind(tc,hous),tc_vs_wrist3_mm=dict(plug=mind(plug,w3),rest=mind([g for g in tc if g not in plug],w3),
  note='adjacent pair, fixed pose; the plug sits on the tool connector, which the wrist-3 shapes enclose'),tc_pieces=len(tc))
if __name__=='__main__':
 import subprocess
 fn='results/r19/cable/static2.json';allo=json.load(open(fn)) if os.path.exists(fn) else {}
 code="import sys,json;sys.argv=['x','ARM={a}'];sys.path.insert(0,'.');import r19cable_static as S,r19cable2_static as S2;o=S.one('{a}');o.update(S2.extra('{a}'));print('RESULT '+json.dumps(o,default=str))"
 P={a:subprocess.Popen([sys.executable,'-c',code.format(a=a)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) for a in KV['ARMS'].split(',')}
 for a,p in P.items():
  so,se=p.communicate();line=[l for l in so.splitlines() if l.startswith('RESULT ')]
  allo[a]=json.loads(line[-1][7:]) if line else dict(error=se[-1500:])
  print(a,json.dumps(allo[a],default=str)[:2500],flush=True)
 os.makedirs('results/r19/cable',exist_ok=True);json.dump(allo,open(fn,'w'),indent=1,default=str);print(fn)
