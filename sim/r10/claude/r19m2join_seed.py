"""R19 #42 (R19_M2JOIN.md): seeded stroke-start candidates for one stir stroke, added next to r19stir_reach.py's. New file.
r19stir_reach.py (r15reach.py + solver.solve: random collision-aware starts, best KEEP by reserve) found no stroke-start
of a wanted IK branch for some stroke. Here the stroke-start pose of stroke K (r19stir_cycle.tcp(t0_of(K), SIGN): the
same target r15reach / r19stir_cycle.follow use) is solved by least squares (as r19stir_cycle.follow: same residual,
bounds = joint ranges) from SEED states: the start / end states of the stored working parts of the other strokes
that are on the wanted branch (r19stir_cycle.groups of works.json). A solution is kept only if its pose error is
<= 0.1 mm / 0.05 deg, it is on the wanted branch (elbow, wrist = signs of sin q3, sin q5), Checker.check(full=True)
reports no hit and no range violation, and the plume rule holds (r19stir_cycle.model(SIGN)['plume'] >= 0): the same
gates as the reach candidates. Distinct solutions (1 deg) are written as an r15reach-style file:
results/r19/stir/reach/reach_stir_h_scrape_dice_i<III>_g0.45_cx.55_r19_k48_seeded_<arm>.json (cands: q, reserve_mm,
plume_mm, jaw_sign). Nothing else is written.
python r19m2join_seed.py ARM=<arm> STROKE=<k> SIGN=-1 BRANCH=-1,1"""
import sys,os,json,time
sys.path.insert(0,'.')
import numpy as np
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a);ARM=KV['ARM'];K=int(KV['STROKE']);SG=int(KV.get('SIGN',-1))
WANT=[int(x) for x in KV.get('BRANCH','-1,1').split(',')]
sys.argv=['r19stir_cycle.py','seed',f'ARM={ARM}']
import r19stir_cycle as SC
def br(q):q=np.asarray(q)[3:9];return [int(np.sign(np.sin(q[2]))),int(np.sign(np.sin(q[4])))]
if __name__=='__main__':
 import mujoco
 from scipy.optimize import least_squares
 from scipy.spatial.transform import Rotation
 t0=time.monotonic();M=SC.model(SG);ch=M['ch'];m,d=ch.m,ch.d;ids=M['ids'];sid=M['sid'];lo,hi=M['lo'],M['hi']
 p,Rt=SC.tcp(SC.t0_of(K),SG)
 W=json.load(open(f'{SC.OUT}/works.json'));seeds=[]
 for w in W['works']:
  if not w['ok'] or w['sign']!=SG or w['stroke']==K:continue
  for q in (w['states'][0],w['states'][-1]):
   if br(q)==WANT:seeds.append((f'stroke{w["stroke"]} cand{w["cand"]}',np.array(q,float)))
 print('seeds',len(seeds),flush=True);sols=[]
 for name,q0 in seeds:
  q=q0.copy()
  def res(x):
   q[ids]=x;d.qpos[:]=q;mujoco.mj_kinematics(m,d)
   return np.r_[(d.site_xpos[sid]-p)*10,Rotation.from_matrix(Rt@d.site_xmat[sid].reshape(3,3).T).as_rotvec()]
  sol=least_squares(res,np.clip(q[ids],lo+1e-8,hi-1e-8),bounds=(lo+1e-9,hi-1e-9),max_nfev=400,xtol=1e-12,ftol=1e-12);q[ids]=sol.x
  pe,re=ch.pose_error(q,p,Rt);b=br(q)
  if pe>1e-4 or np.degrees(re)>.05 or b!=WANT:continue
  if any(np.degrees(np.abs((q[ids]-s_[ids]+np.pi)%(2*np.pi)-np.pi)).max()<1. for s_,_ in sols):continue
  chk=ch.check(q,full=True,mass=0.);pl=M['plume'](q)
  res_=min((v['reserve_mm'] for cat,v in chk['clearance'].items() if cat!='self'),default=1e9)
  ok=not chk['hits'] and pl[0]>=0
  print(name,'pose %.2e m'%pe,'branch',b,'hits',[h['pair'] for h in chk['hits']][:2],'reserve %.1f'%res_,'plume %.1f'%pl[0],'deg',np.degrees(q[ids]).round(1).tolist(),flush=True)
  if ok:sols.append((q.copy(),dict(q=q.tolist(),reserve_mm=float(res_),plume_mm=float(pl[0]),jaw_sign=SG,seed=name)))
 out=f'results/r19/stir/reach/reach_stir_h_scrape_dice_i{K*16:03d}_g0.45_cx.55_r19_k48_seeded_{ARM}.json'
 json.dump(dict(probe='stir seeded (r19m2join_seed.py)',i=K*16,stroke=K,sign=SG,branch=WANT,tcp=list(map(float,p)),n_seeds=len(seeds),cands=[c for _,c in sols],elapsed_s=round(time.monotonic()-t0)),open(out,'w'),indent=1)
 print('kept',len(sols),'->',out,'%.0f s'%(time.monotonic()-t0))
