"""R19 #36: static checks of the cable shapes (r19cable.py) that the path checker cannot see (new file).
 1. cable vs the wrist-3 link (R_tool's parent: an adjacent pair, never checked by the checker; the relative pose is fixed);
 2. cable vs each adopted chain's held object (same body R_tool: unchecked; fixed relative pose) and vs the fingers at
    jaw open / closed (jaw bodies are children of R_tool: unchecked);
 3. two self pairs the checker does see, swept over the joints that move them relative to the gripper (a map of the
    postures a routing forbids; the paths themselves are checked by r19cable_check.py): cable vs wrist 2 over the whole
    J6 turn (720 steps), cable (and, for reference, the housing) vs wrist 1 over J5 x J6 (every 3 deg x 6 deg): the minimum
    of MuJoCo's convex distance (mj_geomDistance; a map, not a certificate) and the share of the J5 x J6 grid in which
    the cable intersects wrist 1;
 4. radial reach about the J6 axis (the swept radius of the tool) of the cable vs the housing.
python r19cable_static.py ARMS=<arm>[,<arm>..] -> results/r19/cable/static.json (merged per arm)"""
import sys,os,json
sys.path.insert(0,'.')
import numpy as np
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
CHAINS={'wok':'results/r17/chain_wok_s-1_final_py.15_ur5e_enc2_pgc.json','lever':'results/r17/chain_lever_s+1_final_ur5e_enc2_pgc.json',
 'lid':'results/r17/chain_lid_s-1_final_ur5e_enc2_pgc.json','spatula':'results/r17/chain_spatula_s-1_r18roll-1.15_.30_ur5e_enc2_pgc.json',
 'spider':'results/r19/pot/chain_spider_s+1_pot_1.56_.20_ur5e_enc2_pgc.json'}
def one(arm):
 os.environ['ARM']=arm
 import importlib,mujoco,chain,arms
 from scene import build
 from checker import Checker
 import kitchen16 as K,kitchen17 as K17
 from r19enc_check import meshheld
 assert arms.current()==arm
 K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);K.TOOL_XY['spatula']=(-1.15,.30);K.SPAT_ELEV=8.;K.SPAT_YAW=0.;K.SPAT_ROLL=180.
 BASE=dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None})
 out=dict(arm=arm,routing=arms.ARMS[arm].get('cable'));import time;t0=time.monotonic();tm=lambda k:out.setdefault('timing_s',{}).__setitem__(k,round(time.monotonic()-t0,1))
 def mk(extra):
  cfg=chain.chain_cfg('SD',**{**BASE,**extra});tree,meta=build(cfg,None);meshheld(tree);return Checker(tree,meta)
 ch=mk({});m,d=ch.m,ch.d;B=ch.bounds
 cab=[g for g,n in enumerate(ch.gnames) if n.startswith('R_pgc_cable')];assert cab
 body=lambda nm:m.body(nm).id
 on=lambda b:[g for g in range(m.ngeom) if ch.robot[g] and m.geom_bodyid[g]==b and m.geom_type[g]!=0]
 W3,W2,W1=(on(body(n)) for n in ('R_arm_wrist_3_link','R_arm_wrist_2_link','R_arm_wrist_1_link'))
 J=[ch.qa[n] for n in arms.JOINTS];q0=m.qpos0.copy()
 def mind(q,A,Bs):
  d.qpos[:]=q;mujoco.mj_kinematics(m,d);best=(1e9,None)
  for a in A:
   for b in Bs:
    if np.linalg.norm(d.geom_xpos[a]-d.geom_xpos[b])-m.geom_rbound[a]-m.geom_rbound[b]>best[0]:continue   # bounding spheres: cannot beat the current minimum
    v=B.pair(a,b)['lower_m']
    if v<best[0]:best=(v,(ch.gnames[a],ch.gnames[b]))
  return best
 ft=np.zeros(6)
 def fast(q,A,Bs):   # sweeps: MuJoCo's own convex distance (mj_geomDistance, meshes as hulls; negative = penetration), a map, not a certificate
  d.qpos[:]=q;mujoco.mj_kinematics(m,d);best=(1e9,None)
  for a in A:
   for b in Bs:
    v=mujoco.mj_geomDistance(m,d,a,b,.3,ft)
    if v<best[0]:best=(v,(ch.gnames[a],ch.gnames[b]))
  return best
 v,p=mind(q0,cab,W3);out['cable_vs_wrist3_mm']=dict(min=round(v*1e3,2),pair=p,note='adjacent pair (not checked by the checker); fixed relative pose')
 # fingers at jaw open / closed
 fg=[g for g,n in enumerate(ch.gnames) if n.startswith('R_finger_')];res=[]
 for jq in (0.,.025):
  q=q0.copy();q[ch.qa['R_jaw_minus']]=q[ch.qa['R_jaw_plus']]=jq;res.append(mind(q,cab,fg)[0])
 out['cable_vs_fingers_mm']=round(min(res)*1e3,2);tm('fingers')
 # held objects of the adopted chains (fixed relative pose)
 hv={}
 for k,f in CHAINS.items():
  r=json.load(open(f));c2=mk(K17.held_cfg(r['obj'],r['grasp_sense']));held=[g for g,n in enumerate(c2.gnames) if c2.robot[g] and c2.m.geom_bodyid[g]==c2.m.body('R_tool').id and n.startswith('R_gripper_') and not n.startswith('R_gripper_oem') and n!='R_gripper_palm']
  cb=[g for g,n in enumerate(c2.gnames) if n.startswith('R_pgc_cable')];c2.d.qpos[:]=np.asarray(r['play'][0],float);mujoco.mj_kinematics(c2.m,c2.d)
  best=min(((c2.bounds.pair(a,b)['lower_m'],(c2.gnames[a],c2.gnames[b])) for a in cb for b in held),default=(None,None))
  hv[k]=dict(min_mm=None if best[0] is None else round(best[0]*1e3,2),pair=best[1],held_geoms=len(held))
 out['cable_vs_held_mm']=hv;tm('held')
 # swept self pairs
 j4,j5,j6=J[3],J[4],J[5]
 best=(1e9,None)
 for t in np.linspace(-np.pi,np.pi,720,endpoint=False):
  q=q0.copy();q[j6]=t;v,p=fast(q,cab,W2)
  if v<best[0]:best=(v,p,round(float(np.degrees(t)),1))
 out['cable_vs_wrist2_over_J6_mm']=dict(min=round(best[0]*1e3,2),pair=best[1],at_J6_deg=best[2]);tm('wrist2')
 best=(1e9,None);n=hit=0
 for a5 in np.radians(np.arange(-180,180,float(KV.get('G5',3)))):
  for a6 in np.radians(np.arange(-180,180,float(KV.get('G6',6)))):
   q=q0.copy();q[j5]=a5;q[j6]=a6;v,p=fast(q,cab,W1);n+=1;hit+=v<=0
   if v<best[0]:best=(v,p,(round(float(np.degrees(a5))),round(float(np.degrees(a6)))))
 tm('wrist1');out['cable_vs_wrist1_over_J5J6']=dict(min_mm=round(best[0]*1e3,2),pair=best[1],at_J5_J6_deg=best[2],grid=n,intersecting_share=round(hit/n,4))
 # same sweep for the housing (reference: how often the gripper body itself meets wrist 1)
 hous=[g for g,n_ in enumerate(ch.gnames) if n_.startswith('R_gripper_oem')];n=hit=0
 for a5 in np.radians(np.arange(-180,180,float(KV.get('G5',3)))):
  for a6 in np.radians(np.arange(-180,180,float(KV.get('G6',6)))):
   q=q0.copy();q[j5]=a5;q[j6]=a6;v,_=fast(q,hous,W1);n+=1;hit+=v<=0
 out['housing_vs_wrist1_intersecting_share']=round(hit/n,4)
 # radial reach about the J6 axis (wrist-3 frame: axis = y through the origin)
 d.qpos[:]=q0;mujoco.mj_kinematics(m,d);w3=body('R_arm_wrist_3_link');Rw=d.xmat[w3].reshape(3,3);pw=d.xpos[w3]
 def reach(gs):
  r=0.;ymin=1e9
  for g in gs:
   a,k=m.mesh_vertadr[m.geom_dataid[g]],m.mesh_vertnum[m.geom_dataid[g]];V=m.mesh_vert[a:a+k]@d.geom_xmat[g].reshape(3,3).T+d.geom_xpos[g];L=(V-pw)@Rw
   r=max(r,float(np.hypot(L[:,0],L[:,2]).max()));ymin=min(ymin,float(L[:,1].min()))
  return round(r*1e3,1),round(ymin*1e3,1)
 out['radial_reach_about_J6_mm']=dict(cable=reach(cab)[0],housing=reach(hous)[0],cable_lowest_y_w3_mm=reach(cab)[1],housing_lowest_y_w3_mm=reach(hous)[1],
  note='max distance from the J6 axis; y_w3 = position along the J6 axis in the wrist-3 frame (flange face at +100 mm)')
 print(json.dumps(out),flush=True);return out
if __name__=='__main__':
 fn='results/r19/cable/static.json';allo=json.load(open(fn)) if os.path.exists(fn) else {}
 import subprocess
 P={a:subprocess.Popen([sys.executable,'-c',f"import sys;sys.argv=['x','ARM={a}'];sys.path.insert(0,'.');import r19cable_static as S,json;print('RESULT '+json.dumps(S.one('{a}'),default=str))"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) for a in KV['ARMS'].split(',')}   # one process per arm, in parallel
 for a,p in P.items():
  so,se=p.communicate();line=[l for l in so.splitlines() if l.startswith('RESULT ')]
  allo[a]=json.loads(line[-1][7:]) if line else dict(error=se[-800:])
  print(a,json.dumps(allo[a],default=str)[:1500],flush=True)
 os.makedirs('results/r19/cable',exist_ok=True);json.dump(allo,open(fn,'w'),indent=1,default=str);print(fn)
