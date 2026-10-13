"""R19 smooth: what a zero-velocity hub costs when whole actions are cut into stored movements.
For one free piece of a checked chain (spline geometry, same fit as r19smooth.py) the jerk-limited law is
computed (a) for the piece in one go and (b) for the piece cut at a hub state (a 'lane' meet keyframe,
where R17 joined its halves) into two movements that each start and end at rest. (b) - (a) is the time a
stop hub costs. Timing only: the two halves are the same kind of geometry as the checked one-piece
spline, but they are not re-checked here.
python r19smooth_hub.py  -> results/r19/smooth/hub.json"""
import sys,json;sys.path.insert(0,'.')
import numpy as np
import r19smooth as S
CASES=[('wok',12,'emptied -> lowered, hub at the lane meet on the way back',0.),('spider',14,'plate -> rest, hub at the lane-middle meet',0.),('wok',3,'lifted -> tipped, hub at the lane meet (food in the wok)',1.15)]
out=[]
for act,kfm,label,food in CASES:
 ctx=S.setup(act);ch=ctx['ch'];fb=S.FastBound(ch);Q=S.unwrap(ctx['r']['play']);w=np.r_[1.,ch.point_bound.weights.max(0)[3:9]];Y=Q[:,S.DOF]*w
 tl=S.r17_timing(ctx,Q);kf=tl['kf_idx'];tu=S.turns(Q[:,S.DOF]/np.r_[S.R17['CW'],np.full(6,np.radians(S.R17['QW']))])
 c=S.CHAINS[act];must=set([0,len(Q)-1]+[kf[k] for k in c['dwell']]+[kf[a] for a,b in c['fixed']]+[kf[b] for a,b in c['fixed']])
 rev=[int(i) for i in np.nonzero(tu>S.REV)[0] if min(abs(int(i)-j) for j in must)>2];stops=sorted(must|set(rev))
 m=kf[kfm];a=max(x for x in stops if x<m);b=min(x for x in stops if x>m)
 bc=json.load(open(f'{S.OUT}/{act}_baseline.json'));resv=np.full(len(Q),1e9)
 for rr,sv in zip(bc['rb'],bc['src']):
  for i in {int(np.floor(sv)),int(np.ceil(sv))}:
   if 0<=i<len(Q):resv[i]=min(resv[i],rr['res'],rr['self_mm'])
 tol=np.clip(.5*np.maximum(resv,0)/1e3,.0005,.008)
 def law(i0,i1,pro):
  Ys,ix=S.dedup(Y[i0:i1+1],list(range(i0,i1+1)));p,_=S.fit_spline(Ys,w,Q[0],tol[ix],fb);rt=S.time_segment(ctx,S.Seg(ctx,p,food,S.LIMITS[pro],False))
  return rt['time_s']
 for pro in ('same','fastcart'):
  t1=law(a,b,pro);t2a=law(a,m,pro);t2b=law(m,b,pro)
  out.append(dict(act=act,piece=[int(a),int(b)],hub_state=int(m),hub=label,profile=pro,one_piece_s=round(t1,2),two_movements_s=round(t2a+t2b,2),stop_hub_cost_s=round(t2a+t2b-t1,2),r17_piece_s=round(float(tl['dt'][a:b].sum()+S.R17['JOIN']*sum(1 for mi in tl['meet_idx'] if a<mi<b)),2)))
  print(json.dumps(out[-1]),flush=True)
json.dump(out,open(f'{S.OUT}/hub.json','w'),indent=1)
