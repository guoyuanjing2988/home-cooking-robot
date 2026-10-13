"""R19 #12: why does an r17chain anchor get so few IK starts? Re-runs r17chain's anchor solve (same scene, same
seeds, same solver.solve) for the named keyframes and counts, over the rejected starts, the pairs that hit
(status 'collision') next to the pose failures. Read-only: r17chain.py is executed only up to its main loop
(its definitions), nothing is written except results/r19/enc2/diag_<act><TAG>.json.

python r19enc_diag.py <the r17chain options> KFS=lifted,lowered   e.g.
python r19enc_diag.py ACT=wok SIGN=-1 GTILT=25 L2X=-.25 SINKC=-1.06 SPX=1.52 SPY=.36 PY=.14 ARM=ur5e_enc2 KFS=lifted"""
import sys,os,json,collections
sys.path.insert(0,'.')
if len(sys.argv)>1 and sys.argv[1]=='plateshift':
 # python r19enc_diag.py plateshift [SET=wok] [NEW=ur5e_enc2]: the stored path held fixed, the plate (and the
 # plate-2 dish) moved by (dx, dy); min clearance reserve of the arm pieces (10 mm) and the gripper / held parts
 # (5 mm) to the moved plate over every <= 4 mm state (MuJoCo mj_geomDistance; a screen, not the checker).
 import numpy as np,mujoco
 sys.argv=[sys.argv[0],'x']+sys.argv[2:];import r19enc_check as C
 KV=C.KV;key=KV.get('SET','wok');c=C.ctx(key,C.NEW);ch=c['ch'];m,d=ch.m,ch.d
 Q=list(C.states(key).values())[0];QS,src,sp=C.sample(ch,Q)
 plates=[m.geom(n).id for n in ('r15_plate','r17_plate2') if n in ch.gnames];p0={g:m.geom_pos[g].copy() for g in plates}
 arm=[g for g,n in enumerate(ch.gnames) if n.startswith('R_geom_') and not n.startswith('R_geom_base')];grip=[g for g,n in enumerate(ch.gnames) if ch.robot[g] and (n.startswith(('R_gripper','R_finger','R_held')))]
 rows=[];ft=np.zeros(6)
 for dx,dy in [(0,0),(0,.01),(0,.02),(0,.03),(0,.05),(0,.07),(0,.10),(-.02,0),(-.05,0),(-.08,0),(-.10,0),(-.05,.03),(-.08,.03)]:
  for g in plates:m.geom_pos[g]=p0[g]+[dx,dy,0]
  best=(1e9,None,None)
  for i,q in enumerate(QS):
   d.qpos[:]=q;mujoco.mj_kinematics(m,d)
   for pg in plates:
    for gs,need in ((arm,.010),(grip,.005)):
     for g in gs:
      v=mujoco.mj_geomDistance(m,d,g,pg,.03,ft)-need
      if v<best[0]:best=(v,ch.gnames[g]+' | '+ch.gnames[pg],round(float(src[i]),1))
  rows.append(dict(dx=dx,dy=dy,min_reserve_mm=round(best[0]*1e3,1),pair=best[1],stored_state=best[2]));print(json.dumps(rows[-1]),flush=True)
 for g in plates:m.geom_pos[g]=p0[g]
 fn=f'{C.OUT}/plateshift_{key}.json';json.dump(dict(note='stored path fixed, plate moved; mj_geomDistance screen (cylinder distances approximate), reserve = gap - required',rows=rows),open(fn,'w'),indent=1);print(fn);sys.exit()
src=open('r17chain.py',encoding='utf-8').read();cut=src.index('t0=time.monotonic();pieces={}')
g={'__name__':'r17chain_defs','__file__':os.path.abspath('r17chain.py')};exec(compile(src[:cut],'r17chain.py','exec'),g)
KV=g['KV'];KF=g['KF'];K=g['K'];np=g['np'];solve=g['solve'];ch=g['ch'];out={}
for name in KV['KFS'].split(','):
 k=[i for i,f in enumerate(KF) if f['label']==name][0];pt_,Rt_=K.tcp_pose(g['OBJ'],KF[k]['R'],KF[k]['p'],g['SIGN']);st=collections.Counter();pairs=collections.Counter();pose=[]
 for seed in g['SEEDS']:
  t=dict(name=f"{g['ACT']}_{k}",points=[list(pt_)]*2,held=None,kind='transfer',force=None,approach=list(Rt_[:,0]),jaws=[tuple(g['SIGN']*(KF[k]['R']@K.OBJ[g['OBJ']]['j']))],jaw_q=g['JAW_HELD'])
  if isinstance(KF[k]['c'],float):t['cart_x']=KF[k]['c']
  r=solve(ch,pt_,list(Rt_[:,0]),target=t,seed=seed)
  for row in r['rows']:
   st[row['status']]+=1
   if row['status']=='collision':
    for p in {' | '.join(sorted(h['pair'])) for h in row['check']['hits']}:pairs[p]+=1
   if row['status']=='pose':pose.append(row['position_mm'])
 out[name]=dict(keyframe=k,status=dict(st),collision_pairs=dict(pairs.most_common()),pose_failures=dict(n=len(pose),median_position_error_mm=round(float(np.median(pose)),1) if pose else None))
 print(name,json.dumps(out[name]),flush=True)
fn=f"results/r19/enc2/diag_{g['ACT']}{'_'+KV['TAG'] if 'TAG' in KV else ''}_{g['ARM']}.json";os.makedirs(os.path.dirname(fn),exist_ok=True);json.dump(dict(argv=sys.argv[1:],anchors=out),open(fn,'w'),indent=1);print(fn)
