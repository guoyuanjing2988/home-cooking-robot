"""R19 #36 / #42 (m2 cable): the static checks of a run (pairs the path checker cannot see) for m2 cable options (new file),
one subprocess per option:
 - r19cable_static.one, unchanged: cable vs wrist 3, fingers, the held objects of the 5 chains, wrist 2 over the whole J6
   turn, wrist 1 over J5 x J6, radial reach;
 - extra(): r19cable2_static.extra's checks (the run vs the housing, which on m2 includes the wedge R_gripper_oem_mount_*;
   wrist 3 split into the plug and the rest; the route data), with one change: the route data are taken where arms.swap
   calls r19cable.add, i.e. AFTER r19mount.apply re-posed the gripper (r19cable2_static hooks arms.swap itself, before the
   mount, which gives the old-pose tool connector for an m2 option).
CANDS=<json>: candidate runs (r19cable2_tc ROUTES-style specs) registered as single-run options '<m2 base>c_<key>' first.
The held objects' poses relative to the gripper are the grasps of the old-mount chains in r19cable_static.CHAINS: the m2
mount moves the whole gripper with its TCP, so the held object sits the same way on R_tool.
python r19m2cable_static.py ARMS=<arm>[,<arm>..] [CANDS=<json>] [OUT=<json>] -> results/r19/cable/m2/static.json (merged per arm)"""
import sys,os,json,subprocess
sys.path.insert(0,'.')
def register(cands):
 import r19cable2_tc as TC,r19cable as CAB,arms
 C=json.load(open(cands))
 for k,s in C.items():
  TC.ROUTES[k]=s;CAB.ROUTINGS[k]=dict(CAB.ROUTINGS[s['_base']],tc=k)
  for b in ('ur5e_enc2_pgc_m2','fr5_j6_pgc_m2'):arms.ARMS[b+'c_'+k]=dict(arms.ARMS[b],name=arms.ARMS[b]['name']+' + cable, m2 run candidate '+k,cable=k,cable_source='R19_M2CABLE.md')
def extra(arm):
 os.environ['ARM']=arm
 import numpy as np,chain,arms,r19cable as CAB,r19cable2_tc as TC
 from scene import build
 from checker import Checker
 import kitchen16 as K
 from r19enc_check import meshheld
 K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);K.TOOL_XY['spatula']=(-1.15,.30);K.SPAT_ELEV=8.;K.SPAT_YAW=0.;K.SPAT_ROLL=180.
 info={};orig=CAB.add
 def add(tree,routing,a=None):   # after the mount re-pose (arms.swap order: r19mount.apply, then r19cable.add)
  info.update(TC.build(CAB.ROUTINGS[routing]['tc'],a,tree)[1]);return orig(tree,routing,a)
 arms._cab.add=add
 try:cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None});tree,meta=build(cfg,None)
 finally:arms._cab.add=orig
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
 return dict(route=info,tc_vs_housing_mm=mind(tc,hous),tc_vs_wedge_mm=mind(tc,[g for g in hous if nm[g].startswith('R_gripper_oem_mount')]),
  tc_vs_wrist3_mm=dict(plug=mind(plug,w3),rest=mind([g for g in tc if g not in plug],w3),note='adjacent pair, fixed pose; the plug sits on the tool connector, which the wrist-3 shapes enclose'),tc_pieces=len(tc))
def child(arm,cands):
 if cands:register(cands)
 sys.argv=['x','ARM='+arm]
 import r19cable_static as S
 o=S.one(arm);o.update(extra(arm));print('RESULT '+json.dumps(o,default=str))
if __name__=='__main__':
 KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
 fn=KV.get('OUT','results/r19/cable/m2/static.json');allo=json.load(open(fn)) if os.path.exists(fn) else {}
 code="import sys;sys.path.insert(0,'.');import r19m2cable_static as M;M.child({a!r},{c!r})"
 P={a:subprocess.Popen([sys.executable,'-c',code.format(a=a,c=KV.get('CANDS'))],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) for a in KV['ARMS'].split(',')}
 for a,p in P.items():
  so,se=p.communicate();line=[l for l in so.splitlines() if l.startswith('RESULT ')]
  allo[a]=json.loads(line[-1][7:]) if line else dict(error=se[-1500:])
  print(a,json.dumps(allo[a],default=str)[:2000],flush=True)
 os.makedirs(os.path.dirname(fn),exist_ok=True);json.dump(allo,open(fn,'w'),indent=1,default=str);print(fn)
