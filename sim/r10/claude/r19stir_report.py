"""R19 #3: independent re-evaluation of the stored stir library entries (results/r19/stir/lib_stir_cycle_<arm>.json)
and the summary tables of R19_STIR.md.

For each arm the stored geometry (B-spline knots / coefficients, with the limit + h^2 coordinates) and the stored
time law (t, s on a 2 ms grid) are rebuilt from the JSON alone (nothing from r19stir_cycle.py's memory) and checked:
 - joint speed / acceleration / jerk along the stored law (chain rule with s' and s'' from the stored s(t));
 - continuity at every hand-off: |q'(s+) - q'(s-)|, |q''(s+) - q''(s-)| of the geometry (C2 in s) and the jump of
   joint velocity / acceleration in time across each hand-off;
 - periodicity: q, q', q'' at s = 0 and s = L, and s' at both ends of the stored period;
 - the stored certified states lie on the stored geometry (nearest-parameter distance);
 - grip-point (TCP, site R_prep) speed and acceleration by forward kinematics (FR5 TCP limit 1 m/s, R19_ARM_SWAP.md);
 - the working parts' time against the bench (s' = 1 is bench speed).
python r19stir_report.py [ARMS=ur5e_enc2_pgc,fr5_j6_pgc_sp20] -> results/r19/stir/summary.json"""
import sys,os,json
sys.path.insert(0,'.')
import numpy as np
from scipy.interpolate import BSpline
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
ARMS_=KV.get('ARMS','ur5e_enc2_pgc,fr5_j6_pgc_sp20').split(',')
class Seg:
 def __init__(self,g):
  self.b=BSpline(np.array(g['knots']),np.array(g['coef']),g['k']);self.sq={int(j):tuple(v) for j,v in g.get('sq',{}).items()};self.a,self.e=g['local']
 def __call__(self,x,nu=0):
  H=[self.b(x,n) for n in range(nu+1)];y=np.array(H[nu],float)
  for j,(lim,sg) in self.sq.items():
   h=[v[...,j] for v in H]
   y[...,j]=lim+sg*h[0]**2 if nu==0 else sg*(2*h[0]*h[1] if nu==1 else 2*(h[1]**2+h[0]*h[2]) if nu==2 else 2*(3*h[1]*h[2]+h[0]*self.b(x,3)[...,j]))
  return y
def main():
 out={}
 for arm in ARMS_:
  os.environ['ARM']=arm
  L_=json.load(open(f'results/r19/stir/lib_stir_cycle_{arm}.json'));G=L_['geometry'];segs=[Seg(g) for g in G['segments']];B=np.array([g['s0'] for g in G['segments']]+[G['segments'][-1]['s1']]);Ltot=B[-1]
  names=[g['name'] for g in G['segments']]
  def q(s,nu=0):
   s=np.atleast_1d(np.asarray(s,float));k=np.clip(np.searchsorted(B,s,side='right')-1,0,len(segs)-1);o=np.zeros((len(s),6))
   for j in np.unique(k):m=k==j;o[m]=segs[j](segs[j].a+s[m]-B[j],nu)
   return o
  TL=L_['time_law'];t=np.array(TL['t']);s=np.array(TL['s']);H=t[1]-t[0]
  sd=np.gradient(s,H,edge_order=2);sdd=np.gradient(sd,H,edge_order=2);sddd=np.gradient(sdd,H,edge_order=2)
  q1,q2,q3=q(s,1),q(s,2),q(s,3);v=q1*sd[:,None];a=q2*sd[:,None]**2+q1*sdd[:,None];j=q3*sd[:,None]**3+3*q2*(sd*sdd)[:,None]+q1*sddd[:,None]
  lim=TL['limits'];V=np.array(lim['v_degps']);A=lim['A_degps2']['A_UR']
  # continuity of the geometry at the hand-offs (one-sided derivatives)
  jumps=[]
  for i in range(len(segs)):
   nx=(i+1)%len(segs);e=segs[i];n=segs[nx]
   d=[float(np.degrees(np.abs(e(e.e,nu)-n(n.a,nu)).max())) for nu in (0,1,2)];jumps.append(dict(at=f'{names[i]} -> {names[nx]}',dq_deg=round(d[0],6),dq1_degps=round(d[1],6),dq2_degps2=round(d[2],4)))
  # the certified states lie on the geometry
  Qs=np.array(L_['states']['q']);kinds=L_['states']['kinds'];dev=0.
  for nm in dict.fromkeys(kinds):
   i=names.index(nm);X=Qs[[x==nm for x in kinds]][:,3:9];u=np.linspace(segs[i].a,segs[i].e,20001);Y=segs[i](u)
   dev=max(dev,max(float(np.min(np.abs(Y-x).max(1))) for x in X[::7]))
  # grip point (TCP) by forward kinematics
  import mujoco,r19stir_cycle as C
  os.environ['ARM']=arm;C.ARM=arm;C.OUT=f'results/r19/stir/cycle_{arm}';C._M.clear();M=C.model(-1);m,d=M['ch'].m,M['ch'].d;sid=M['sid'];q0=np.array(G['state_const'])
  Q=np.tile(q0,(len(s),1));Q[:,3:9]=q(s);P=np.zeros((len(s),3))
  for i_,x in enumerate(Q):d.qpos[:]=x;mujoco.mj_kinematics(m,d);P[i_]=d.site_xpos[sid]
  vt=np.linalg.norm(np.gradient(P,H,axis=0),axis=1);at=np.linalg.norm(np.gradient(np.gradient(P,H,axis=0),H,axis=0),axis=1)
  # works vs the bench
  r=np.mod(s,Ltot);k=np.clip(np.searchsorted(B,r,side='right')-1,0,len(segs)-1);isw=np.array([n.startswith('work') for n in names])[k]
  wt=float(np.sum(isw)*H);bt=sum(g['s1']-g['s0'] for g in G['segments'] if g['name'].startswith('work'))
  per=dict(q=float(np.degrees(np.abs(q(0.)-q(Ltot)).max())),q1=float(np.degrees(np.abs(q(0.,1)-q(Ltot,1)).max())),q2=float(np.degrees(np.abs(q(0.,2)-q(Ltot,2)).max())),sdot=[round(float(sd[0]),5),round(float(np.polyval(np.polyder(np.polyfit(t[-8:],s[-8:],3)),TL['period_s'])),5)],s_end_vs_length=round(float(np.polyval(np.polyfit(t[-8:],s[-8:],3),TL['period_s'])-Ltot),7))
  out[arm]=dict(period_per_stroke_s=round(TL['period_s']/5,3),cycle_s=round(TL['period_s'],3),peak_v_degps=np.degrees(np.abs(v).max(0)).round(1).tolist(),v_limit_degps=V.tolist(),
   peak_a_degps2=np.degrees(np.abs(a).max(0)).round(0).tolist(),a_limit_degps2=A,peak_j_degps3=np.degrees(np.abs(j).max(0)).round(0).tolist(),
   max_ratio_v=round(float((np.degrees(np.abs(v))/V).max()),4),max_ratio_a=round(float(np.degrees(np.abs(a)).max()/A),4),
   handoff_geometry_jumps=jumps,max_handoff_jump=dict(dq_deg=max(x['dq_deg'] for x in jumps),dq1_degps=max(x['dq1_degps'] for x in jumps),dq2_degps2=max(x['dq2_degps2'] for x in jumps)),
   periodicity=dict(dq_deg=round(per['q'],6),dq1_degps=round(per['q1'],6),dq2_degps2=round(per['q2'],4),sdot_at_t0_and_period=per['sdot'],s_at_period_minus_length=per['s_end_vs_length']),
   stored_states_off_geometry_deg=round(dev,6),tcp_peak_speed_mps=round(float(vt.max()),3),tcp_peak_acc_mps2=round(float(at.max()),2),
   works_time_s=round(wt,3),works_bench_s=round(bt,3),works_slowdown=round(wt/bt,4),works_share_sdot_ge_095=round(float(np.mean(sd[isw]>=.95)),3),works_median_sdot=round(float(np.median(sd[isw])),3),works_min_sdot=round(float(sd[isw].min()),3),
   certificate={k_:L_['verification']['certificate'][k_] for k_ in ('ok','states','max_step_bound_mm','hit_states','out_of_range_states','min_env_reserve_mm','min_self_reserve_mm','min_plume_mm','plume_violations','min_reserve_by_category')},
   stop_variant=L_['stop_variant'],A_R15=dict(period_per_stroke_s=L_['time_law_A_R15']['period_per_stroke_s']))
  print(arm,json.dumps({k_:v_ for k_,v_ in out[arm].items() if k_ not in ('handoff_geometry_jumps','certificate')}),flush=True)
 json.dump(out,open('results/r19/stir/summary.json','w'),indent=1);print('saved results/r19/stir/summary.json')
if __name__=='__main__':main()
