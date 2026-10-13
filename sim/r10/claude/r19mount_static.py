"""R19 #42: static checks of the gripper housing + bracket against the arm's own links (new file; reads only).
Per arm option (the mount options and, for reference, the current ur5e_enc2_pgc / fr5_j6_pgc_sp20):
 - wrist 3 (R_tool's parent: the checker never tests this pair): every R_tool geom vs every wrist-3 collision geom at the
   fixed pose, mj_geomDistance (distmax 10 mm: exact there, R19_MOUNT.md 2; "10" = 10 mm or more) and the checker's own
   GJK lower bound distance.Bounds.pair; gate >= 5 mm for the housing and the bracket body (the gripper / held gate); the
   bracket's mating boss (R_gripper_oem_mount_base) is reported but exempt: its bottom face is bolted to the flange;
 - wrist 2 over the whole J6 turn (the tool vs wrist 2 depends on J6 only): J6 every 1 deg;
 - wrist 1 over J5 x J6 (the tool vs wrist 1 depends on J5, J6): J5 every 2.5 deg over its range, J6 every 5 deg;
 - forearm over J4 x J5 x J6: J4 every 15 deg, J5 every 5 deg, J6 every 15 deg.
 These three pairs are non-adjacent, so the checker covers them in every path (self gate 0 mm); this is the static sweep.
 Per pair group: the minimum distance (mm; mj_geomDistance distmax 10 mm, negative = penetration depth) and where, the
 share of the grid in contact (< 0) and within 5 mm. Tool geoms: housing (R_gripper_oem_envelope / upper / jaws,
 R_gripper_palm), bracket (R_gripper_oem_mount_*), fingers (R_finger_*, jaws closed).
python r19mount_static.py [ARMS=a,b,..] -> results/r19/mount/static.json (merged per arm)"""
import sys,os,json,time
sys.path.insert(0,'.')
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
import numpy as np,mujoco
DM=.01
def one(arm):
 os.environ['ARM']=arm
 import chain,kitchen16 as K,arms
 from scene import build
 from checker import Checker
 K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.)
 cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None},arm=arm)
 tree,meta=build(cfg,None);ch=Checker(tree,meta);m,d=ch.m,ch.d;nm=ch.gnames
 b=lambda n:m.body(n).id;tb=b('R_tool');jaw=(b('R_jaw_minus'),b('R_jaw_plus'))
 tool=[g for g in range(m.ngeom) if m.geom_bodyid[g] in (tb,)+jaw and m.geom_type[g]!=0 and not nm[g].startswith(('R_held_','R_pgc_cable'))]
 grp=lambda g:'bracket_mating_boss' if nm[g].endswith('mount_base') else 'bracket' if 'mount' in nm[g] else 'fingers' if nm[g].startswith('R_finger') else 'housing'
 link=lambda body:[g for g in range(m.ngeom) if m.geom_bodyid[g]==b(body) and (m.geom_contype[g] or m.geom_conaffinity[g])]
 W3,W2,W1,FA=link('R_arm_wrist_3_link'),link('R_arm_wrist_2_link'),link('R_arm_wrist_1_link'),link('R_arm_forearm_link')
 qa={n:m.jnt_qposadr[m.joint(n).id] for n in ('R_wrist_1_joint','R_wrist_2_joint','R_wrist_3_joint')}
 rng={n:m.jnt_range[m.joint(n).id] for n in qa}
 q0=np.zeros(m.nq);d.qpos[:]=q0;mujoco.mj_kinematics(m,d)
 # wrist 3, fixed pose
 w3={}
 for g in tool:
  best=None
  for w in W3:
   s=mujoco.mj_geomDistance(m,d,g,w,DM,None);lb=ch.bounds.pair(g,w)['lower_m'];v=lb if s>0 else s
   if best is None or v<best[0]:best=(v,s,lb,nm[w])
  w3[nm[g]]=dict(group=grp(g),mm=round(best[0]*1e3,2),mj_mm=round(best[1]*1e3,2),gjk_lower_mm=round(best[2]*1e3,2),vs=best[3])
 gate=min(v['mm'] for v in w3.values() if v['group'] in ('housing','bracket'))
 def sweep(links,grid):
  """min distance per tool group over the grid of (joint name -> value) dicts; contact / near shares"""
  out={};n=0;cnt={};near={}
  for qs in grid:
   q=q0.copy()
   for k,v in qs.items():q[qa[k]]=v
   d.qpos[:]=q;mujoco.mj_kinematics(m,d);n+=1;seen=set();seen5=set()
   for g in tool:
    G=grp(g);mn=min(mujoco.mj_geomDistance(m,d,g,w,DM,None) for w in links)
    if G not in out or mn<out[G][0]:out[G]=(mn,{k:round(float(np.degrees(v)),1) for k,v in qs.items()})
    if mn<0:seen.add(G)
    if mn<.005:seen5.add(G)
   for G in seen:cnt[G]=cnt.get(G,0)+1
   for G in seen5:near[G]=near.get(G,0)+1
  return {G:dict(min_mm=round(v[0]*1e3,2),at_deg=v[1],contact_share=round(cnt.get(G,0)/n,4),within5mm_share=round(near.get(G,0)/n,4)) for G,v in out.items()},n
 r6=lambda step:np.radians(np.arange(-180,180,step))
 j5=lambda step:np.radians(np.arange(max(-180.,np.degrees(rng['R_wrist_2_joint'][0])),min(180.,np.degrees(rng['R_wrist_2_joint'][1]))+1e-9,step))   # one turn at most (periodic)
 sw2,n2=sweep(W2,[{'R_wrist_3_joint':a} for a in r6(1.)])
 sw1,n1=sweep(W1,[{'R_wrist_2_joint':a,'R_wrist_3_joint':c} for a in j5(2.5) for c in r6(5.)])
 swf,nf=sweep(FA,[{'R_wrist_1_joint':a,'R_wrist_2_joint':b_,'R_wrist_3_joint':c} for a in r6(15.) for b_ in j5(5.) for c in r6(15.)])
 # the J5 band that is contact-free with wrist 1 for EVERY J6 (housing + bracket)
 free=[]
 for a in j5(2.5):
  ok=True
  for c in r6(5.):
   q=q0.copy();q[qa['R_wrist_2_joint']]=a;q[qa['R_wrist_3_joint']]=c;d.qpos[:]=q;mujoco.mj_kinematics(m,d)
   if min(mujoco.mj_geomDistance(m,d,g,w,DM,None) for g in tool if grp(g) in ('housing','bracket') for w in W1)<0:ok=False;break
  free.append((round(float(np.degrees(a)),1),ok))
 return dict(arm=arm,mount=arms.ARMS[arm].get('mount'),wrist3=w3,wrist3_gate_mm=gate,wrist3_gate_ok=bool(gate>=5.-1e-6),
  wrist2_J6_turn=dict(grid=n2,groups=sw2),wrist1_J5xJ6=dict(grid=n1,groups=sw1,J5_free_for_all_J6_deg=[a for a,ok in free if ok]),
  forearm_J4xJ5xJ6=dict(grid=nf,groups=swf),J5_range_deg=np.degrees(rng['R_wrist_2_joint']).round(1).tolist())
if __name__=='__main__':
 import subprocess
 A=KV.get('ARMS','ur5e_enc2_pgc,ur5e_enc2_pgc_m1,ur5e_enc2_pgc_m2,ur5e_enc2_pgc_m3,fr5_j6_pgc_sp20,fr5_j6_pgc_m1,fr5_j6_pgc_m2,fr5_j6_pgc_m3').split(',')
 fn='results/r19/mount/static.json';allo=json.load(open(fn)) if os.path.exists(fn) else {}
 code="import sys,json;sys.path.insert(0,'.');import r19mount_static as S;print('RESULT '+json.dumps(S.one('{a}'),default=float))"
 P={a:subprocess.Popen([sys.executable,'-c',code.format(a=a)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) for a in A}
 for a,p in P.items():
  so,se=p.communicate();line=[l for l in so.splitlines() if l.startswith('RESULT ')]
  allo[a]=json.loads(line[-1][7:]) if line else dict(error=se[-1500:])
  print(a,json.dumps(allo[a],default=str)[:1500],flush=True)
 os.makedirs('results/r19/mount',exist_ok=True);json.dump(allo,open(fn,'w'),indent=1,default=str);print(fn)
