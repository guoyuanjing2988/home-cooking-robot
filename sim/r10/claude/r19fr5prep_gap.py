"""R19 #2 (FR5) prep sets: how far a blocked anchor is from passing. A diagnostic, not a check. New file.
r19prepchain.py, with r19fr5prep_chain.py's SEEDUR opt-in, is executed from its source up to its planning loop,
unchanged. For one anchor (ANCHOR=<label substring>), the start candidates CANDS=i0-i1 of r19prepchain's sorted list
(the mapped UR5e states first when SEEDUR is given, then the solver's) are each followed to the anchor's meets exactly
as r19prepchain.follow() does (same keyframe steps, same IK, same cart rule, the same checker: full bound every 5th
step and at every step with a hit), but WITHOUT stopping at a hit. A side stops only where r19prepchain would also
stop for a non-collision reason: TCP error > 5 mm / 3 deg or a joint step > 10 deg.
Per candidate and side: whether the IK reaches the meet, the states with hits, and the worst shortfall against the
gate. The shortfall uses the exact clearance of each failing pair (distance.py lower bound) against its required gap
(10 mm robot-environment, 5 mm gripper/held-environment, 0 self). literal_only = the exact bound clears the gate and
only MuJoCo's literal contact flags the pair (the seam / edge misread of R19_PREP_STEP3.md 4.1; such a state still
fails the unchanged checker). Per side also: pair_min (each failing pair's smallest clearance), env_short_mm (largest
environment shortfall, literal-only pairs excluded) and self_contact (a self pair touching: exact distance 0).
python r19fr5prep_gap.py ACT=<set> ARM=fr5_j6_pgc_sp20 "ANCHOR=under the tap" [SEEDUR=..] [SEEDS=3] [CANDS=0-11] [set options]
 -> results/r19/fr5/prep/gap_<ACT>_<anchor>_c<i0>-<i1>_<arm>.json"""
import sys,os,json,time
sys.path.insert(0,'.')
import numpy as np,mujoco
from scipy.spatial.transform import Rotation,Slerp
import r19fr5prep_chain as PC
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
src=PC.patched_source();cut=src.index('t0=time.monotonic();pieces={}')
g={'__name__':'r19prepchain_gap','__file__':os.path.abspath('r19prepchain.py')}
exec(compile(src[:cut],'r19prepchain.py','exec'),g)
KF,A,ch,K,OBJ,SIGN=g['KF'],g['A'],g['ch'],g['K'],g['OBJ'],g['SIGN']
a=[i for i in A if KV['ANCHOR'] in KF[i]['label']][0];i0,i1=map(int,KV.get('CANDS','0-11').split('-'))
t0=time.monotonic();cs,stat=g['candidates'](a);print(KF[a]['label'],'candidates',len(cs),stat,flush=True)
def shortfalls(c,q,hits):
 c.d.qpos[:]=q;mujoco.mj_kinematics(c.m,c.d);out=[];seen=set()
 for h in hits:
  p=h.get('pair') or []
  if len(p)!=2 or frozenset(p) in seen:continue
  seen.add(frozenset(p))
  if p[0] not in c.gnames or p[1] not in c.gnames:out.append(dict(pair=p));continue
  ia,ib=c.gnames.index(p[0]),c.gnames.index(p[1]);req=c.required(c,ia,ib);bd=c.bounds.pair(ia,ib);gate=req[0] if req else 0.
  out.append(dict(pair=p,clearance_mm=round(bd['lower_m']*1e3,2),gate_mm=round(gate*1e3,1),short_mm=round((gate-bd['lower_m'])*1e3,2),contact=bool(bd['upper_m']<=1e-6),
   literal_only=bool(bd['lower_m']>1e-6 and bd['lower_m']>=gate-1e-6)))
 return out
def follow_all(a,b,q):
 """r19prepchain.follow(a, b, q) without the stop at a hit (same steps, IK and cart rule)."""
 q=np.array(q,float);cA=q[0];rows=[];st=1 if b>a else -1
 for i in range(a,b,st):
  A_,B_=KF[i],KF[i+st];ca,cb=g['cart_of'](i,cA),g['cart_of'](i+st,cA)
  ang=np.degrees(np.linalg.norm(Rotation.from_matrix(B_['R']@A_['R'].T).as_rotvec()));dist=np.linalg.norm(B_['p']-A_['p'])
  n=max(1,int(np.ceil(max(dist/.01,ang/2,abs(cb-ca)/.01))));sl=Slerp([0,1],Rotation.from_matrix([A_['R'],B_['R']]))
  for k in range(1,n+1):
   pt_,Rt_=K.tcp_pose(OBJ,sl(k/n).as_matrix(),A_['p']+(B_['p']-A_['p'])*k/n,SIGN)
   if B_['c']=='F':q,pe,re,dq,dc=g['solve_free'](ch,q,pt_,Rt_)
   else:q[0]=ca+(cb-ca)*k/n;q,pe,re,dq=g['solve_to'](ch,q,pt_,Rt_)
   hits,rmin=g['state'](ch,q,False)
   full=bool(hits) or k%5==0 or k==n
   if full:r=ch.check(q,full=True,mass=0.);hits=r['hits'];rmin=min((v['reserve_mm'] for cat,v in r['clearance'].items() if cat!='self'),default=None)
   rows.append(dict(seg=f"{A_['label']}->{B_['label']}",step=f'{k}/{n}',cart=round(float(q[0]),3),step_deg=round(dq,2),pose_mm=round(pe*1000,2),
    reserve_mm=None if rmin is None else round(rmin,2),tcp=np.round(pt_,3).tolist(),short=shortfalls(ch,q,hits) if hits else []))
   if pe>.005 or re>np.radians(3) or dq>10:return rows,dict(at=rows[-1]['seg'],step=rows[-1]['step'],pose_mm=rows[-1]['pose_mm'],step_deg=rows[-1]['step_deg'])
 return rows,None
out=[]
for ci in range(i0,min(i1,len(cs)-1)+1):
 c_=cs[ci];sides={}
 for b in g['sides'](a):
  rows,stop=follow_all(a,b,c_['q'])
  hs=[r_ for r_ in rows if r_['short']];real=[(s_['short_mm'],s_,r_) for r_ in hs for s_ in r_['short'] if s_.get('short_mm') is not None and not s_['literal_only']]
  w=max(real,key=lambda x:x[0]) if real else None
  pm={}   # per failing pair over the side: smallest exact clearance, its gate, ever touching, only literal flags
  for r_ in hs:
   for s_ in r_['short']:
    if s_.get('clearance_mm') is None:continue
    k_=' / '.join(sorted(s_['pair']));o=pm.setdefault(k_,dict(min_clearance_mm=1e9,gate_mm=s_['gate_mm'],contact=False,literal_only=True,states=0))
    o['min_clearance_mm']=min(o['min_clearance_mm'],s_['clearance_mm']);o['contact']|=s_['contact'];o['literal_only']&=s_['literal_only'];o['states']+=1
  env=[v for v in pm.values() if v['gate_mm']>0 and not v['literal_only']];slf=[v for v in pm.values() if v['gate_mm']==0 and not v['literal_only']]
  sides[KF[b]['label']+f'#{b}']=dict(reached=stop is None,stop=stop,states=len(rows),hit_states=len(hs),pair_min=pm,
   env_short_mm=max([v['gate_mm']-v['min_clearance_mm'] for v in env],default=0.),self_contact=any(v['contact'] for v in slf),self_flag_only=any(v['literal_only'] for v in pm.values() if v['gate_mm']==0),literal_only_states=sum(1 for r_ in hs if all(s_.get('literal_only') for s_ in r_['short'])),
   pairs=sorted({' / '.join(sorted(s_['pair'])) for r_ in hs for s_ in r_['short']}),first_hit=None if not hs else dict(seg=hs[0]['seg'],step=hs[0]['step'],tcp=hs[0]['tcp'],short=hs[0]['short']),
   worst=None if w is None else dict(short_mm=w[0],pair=w[1]['pair'],clearance_mm=w[1]['clearance_mm'],gate_mm=w[1]['gate_mm'],contact=w[1]['contact'],seg=w[2]['seg'],step=w[2]['step'],tcp=w[2]['tcp'],cart=w[2]['cart']),
   min_reserve_mm=min((r_['reserve_mm'] for r_ in rows if r_['reserve_mm'] is not None),default=None),max_step_deg=max((r_['step_deg'] for r_ in rows),default=None))
 worst=max([s['worst']['short_mm'] for s in sides.values() if s['worst']]+[0.])
 out.append(dict(cand=ci,start_reserve_mm=round(c_['reserve_mm'],1),cart=round(c_['q'][0],3),ur_seed=ci<stat.get('ur_seeds_ok',0),all_reached=all(s['reached'] for s in sides.values()),
  worst_short_mm=worst,clean=all(s['reached'] and s['hit_states']==s['literal_only_states'] for s in sides.values()),sides=sides))
 print('cand',ci,'cart',out[-1]['cart'],'reached',out[-1]['all_reached'],'worst short %.2f mm'%worst,{k:(v['reached'],v['hit_states'],'env short %.2f'%v['env_short_mm'],'self contact' if v['self_contact'] else '',v['worst'] and (v['worst']['pair'],v['worst']['short_mm'],v['worst']['seg'])) for k,v in sides.items()},flush=True)
res=dict(act=g['ACT'],arm=g['ARM'],anchor=KF[a]['label'],argv=sys.argv[1:],method=__doc__,n_candidates=len(cs),start_status=stat,cands=[i0,i1],results=out,elapsed_s=round(time.monotonic()-t0))
os.makedirs('results/r19/fr5/prep',exist_ok=True)
import arms;fn=f"results/r19/fr5/prep/gap_{g['ACT']}_{KV['ANCHOR'].replace(' ','_')}_c{i0}-{i1}{arms.tag(g['ARM'])}.json";json.dump(res,open(fn,'w'),default=float);print(fn,'elapsed',res['elapsed_s'])
