"""R19 #40 gap 3: the stored stir cycle (#3) retimed under a JOINT JERK limit, as new library entries next to the old
ones (the old ones are not touched). New file.

Geometry, certified states and certificate are the stored entry's, unchanged (a time law needs no new collision
check, R19_SMOOTH.md); only the time law is new. Method = r19stir_cycle.py's (TOPP by reachability analysis, ds/dt <= 1
on the working parts = never faster than the bench, joint speed = datasheet, periodic: 3 cycles unrolled from rest
and the middle one kept, erosion + moving-average filter W, local slow-downs on the 2 ms grid) with one more limit:
|d3q/dt3| <= J for every joint (r19stir2_law.timelaw). The filter alone gives a time-law jerk up to about 2 A / W, so
for each J the law is computed for W in (0.1, 0.2, 0.4, 0.8, 1.6) s with A = min(A_UR, J W / 2) and the FASTEST
converged law is kept (each candidate holds every limit on the 2 ms grid; none is loosened).
Jerk limits (deg/s^3) and where they come from (no OEM hard limit exists for either arm: R19_STIR2.md 3):
  57296  1000 rad/s^3, MoveIt 2 Ruckig smoothing default DEFAULT_MAX_JERK (planner default) [S]
   8000  A / 0.1 s at A = 800 deg/s^2: the R19_SMOOTH rule 'full acceleration in >= 0.1 s' (ASSUMPTION) [E]
   1000  Fairino SDK PtpFIRPlanningStart(maxAcc, maxJek = 1000): 'unified joint jerk limit (deg/s3), default 1000'
         (SDK planner default, the only OEM-published joint jerk number for either arm) [S]
python r19stir2_retime.py law ARM=<arm> J=<deg/s^3> W=<s>       -> results/r19/stir/retime/law_<arm>_j<J>_w<W>.npz (+ .json)
python r19stir2_retime.py pick ARM=<arm> J=<deg/s^3>            -> results/r19/stir/lib_stir_cycle_<arm>_j<J>.json (fastest
                                                                   converged W), retime/fromrest_<arm>_j<J>.npz
python r19stir2_retime.py ladder [ARMS=..] [JS=57296,8000,1000] [WORKERS=24]  (all laws in parallel, then every pick)"""
import sys,os,json,time,math,hashlib
sys.path.insert(0,'.')
import numpy as np
KV=dict(a.split('=',1) for a in sys.argv[2:] if '=' in a)
ARM=KV.get('ARM','ur5e_enc2_pgc');os.environ['ARM']=ARM
OUT='results/r19/stir/retime';A_UR=800.;WS=(.1,.2,.4,.8,1.6)
SRC={57296:'1000 rad/s^3: MoveIt 2 Ruckig trajectory smoothing DEFAULT_MAX_JERK (planner default), https://github.com/moveit/moveit2/blob/main/moveit_core/trajectory_processing/src/ruckig_traj_smoothing.cpp [S]',
 8000:'A / 0.1 s with A = 800 deg/s^2: the R19_SMOOTH rule "full acceleration in >= 0.1 s" (ASSUMPTION, no OEM value) [E]',
 1000:'Fairino SDK PtpFIRPlanningStart(double maxAcc, double maxJek = 1000): "Unified joint jerk limit (deg/s3), default 1000" (SDK planner default; example call PtpFIRPlanningStart(1000, 1000)), https://fairino-doc-en.readthedocs.io/latest/SDKManual/CPPRobotMovement.html [S]'}
def load(arm):
 import r19stir_report as RP,r19stir2_law as TL
 L_=json.load(open(f'results/r19/stir/lib_stir_cycle_{arm}.json'));G=L_['geometry'];segs=[RP.Seg(g) for g in G['segments']];names=[g['name'] for g in G['segments']]
 path=TL.PathN([(sg,sg.a,sg.e) for sg in segs],6,per=True);isw=np.array([n.startswith('work') for n in names])
 def capf(s):
  r=np.mod(np.asarray(s,float),path.L);k=np.clip(np.searchsorted(path.B,r,side='right')-1,0,len(path.segs)-1);return np.where(isw[k],1.,1e12)
 return L_,path,capf,names
def summary(path,tl,V,A,capf,J,names):
 """middle cycle: period, per-segment times, peaks, ratios (as r19stir_cycle.law_summary, + jerk)"""
 t,s,sd=tl['t'],tl['s'],tl['sd'];L=path.L;t1,t2=np.interp(L,s,t),np.interp(2*L,s,t);m=(t>=t1)&(t<=t2)
 H=t[1]-t[0];sdd=np.gradient(sd,H);sddd=np.gradient(sdd,H);q1,q2,q3=path(s,1),path(s,2),path(s,3)   # derivatives on the FULL law, then the middle cycle (no one-sided ends)
 v=q1*sd[:,None];a=q2*sd[:,None]**2+q1*sdd[:,None];j=q3*sd[:,None]**3+3*q2*(sd*sdd)[:,None]+q1*sddd[:,None]
 rat=dict(v=np.max(np.abs(v[m])/V,axis=1),a=np.max(np.abs(a[m])/A,axis=1),cap=sd[m]/np.sqrt(capf(s[m])),j=np.max(np.abs(j[m])/J,axis=1))
 pk=dict(v=np.abs(v[m]).max(0),a=np.abs(a[m]).max(0),j=np.abs(j[m]).max(0),j_geometric=np.abs((q3*sd[:,None]**3)[m]).max(0));B=path.B
 isw=np.array([n.startswith('work') for n in names]);r=np.mod(s[m],L);k=np.clip(np.searchsorted(B,r,side='right')-1,0,len(B)-2);wsd=sd[m][isw[k]]
 return dict(cycle_s=round(float(t2-t1),4),period_per_stroke_s=round(float(t2-t1)/5,4),segment_s=[round(float(np.interp(L+B[j+1],s,t)-np.interp(L+B[j],s,t)),3) for j in range(len(B)-1)],
  peak_v_degps=np.degrees(pk['v']).round(1).tolist(),peak_a_degps2=np.degrees(pk['a']).round(0).tolist(),peak_j_degps3=np.degrees(pk['j']).round(0).tolist(),peak_j_geometric_degps3=np.degrees(pk['j_geometric']).round(0).tolist(),
  worst_ratio={k_:round(float(v_.max()),4) for k_,v_ in rat.items()},converged=tl['converged'],iters=tl['iters'],kappa_min=round(tl['kappa_min'],5),
  sdot_at_cycle_ends=[round(float(np.interp(L,s,sd)),4),round(float(np.interp(2*L,s,sd)),4)],three_cycles_from_rest_s=round(float(t[-1]),3),
  works_median_sdot=round(float(np.median(wsd)),3),works_min_sdot=round(float(wsd.min()),3),works_share_sdot_ge_095=round(float(np.mean(wsd>=.95)),3))
def law():
 import arms,r19stir2_law as TL
 J=float(KV['J']);W=float(KV['W']);A=min(A_UR,J*W/2);t0=time.monotonic();JM=float(KV.get('JMARGIN',.99))   # the law is solved for 0.99 J: an independent
 L_,path,capf,names=load(ARM);V=np.radians(arms.speeds(ARM))                                                   # finite-difference check (check) then stays <= J
 tl=TL.timelaw(path,V,math.radians(A),capf,0.,0.,W,reps=3,iters=int(KV.get('ITERS',80)),J=math.radians(J)*JM)
 sm=summary(path,tl,V,math.radians(A),capf,math.radians(J),names);sm.update(J_degps3=J,jerk_margin=JM,W_s=W,A_degps2=A,elapsed_s=round(time.monotonic()-t0))
 os.makedirs(OUT,exist_ok=True);fn=f'{OUT}/law_{ARM}_j{int(J)}_w{W:g}'
 np.savez(fn+'.npz',t=tl['t'],s=tl['s'],sd=tl['sd']);json.dump(sm,open(fn+'.json','w'),indent=1)
 print(ARM,'J',J,'W',W,'A',A,json.dumps({k:sm[k] for k in ('period_per_stroke_s','converged','iters','worst_ratio','peak_j_degps3')}),'%.0f s'%sm['elapsed_s'],flush=True)
def pick(arm=None,J=None):
 import arms
 arm=arm or ARM;J=float(J if J is not None else KV['J']);os.environ['ARM']=arm
 C=[];L_,path,capf,names=load(arm);V=np.radians(arms.speeds(arm))
 for W in WS:
  fn=f'{OUT}/law_{arm}_j{int(J)}_w{W:g}'
  if os.path.exists(fn+'.json'):
   s0=json.load(open(fn+'.json'));z=np.load(fn+'.npz')   # summary re-evaluated from the stored law (middle cycle, derivatives on the full law)
   sm=summary(path,dict(t=z['t'],s=z['s'],sd=z['sd'],converged=s0['converged'],iters=s0['iters'],kappa_min=s0['kappa_min']),V,math.radians(s0['A_degps2']),capf,math.radians(J),names)
   sm.update(J_degps3=J,jerk_margin=s0.get('jerk_margin',1.),W_s=W,A_degps2=s0['A_degps2']);json.dump(sm,open(fn+'.json','w'),indent=1)
   if sm['converged'] and max(sm['worst_ratio'].values())<=1+1e-3:C.append((sm['cycle_s'],W,sm))
 if not C:print(arm,J,'no converged law');return None
 _,W,sm=min(C,key=lambda c:c[0]);z=np.load(f'{OUT}/law_{arm}_j{int(J)}_w{W:g}.npz');t,s=z['t'],z['s']
 L=path.L;t1,t2=np.interp(L,s,t),np.interp(2*L,s,t)
 from scipy.interpolate import CubicSpline
 H=t[1]-t[0];tg=np.arange(0,t2-t1-1e-9,H);sg=CubicSpline(t,s)(t1+tg)-L   # one period from s = 0 at t = 0, 2 ms grid (as r19stir_cycle.write_outputs)
 np.savez(f'{OUT}/fromrest_{arm}_j{int(J)}.npz',t=t,s=s,sd=z['sd'])
 lim=dict(L_['time_law']['limits']);lim.update(jerk_degps3=J,jerk_source=SRC.get(int(J),'given'),A_degps2_used=sm['A_degps2'],W_s=sm['W_s'],
  A_note='A = min(800, J W / 2): with the moving-average filter W the time law alone adds a jerk up to ~2 A / W')
 tlaw=dict(limits=lim,law=f'jerk-limited periodic law (middle of 3 unrolled cycles), one period from t = 0 (s = 0) on a 2 ms grid; repeat with t + period, s + length; q(t) = q(s(t)); |d3q/dt3| <= {J:g} deg/s^3 on the 2 ms grid',
  period_s=float(t2-t1),t=tg.round(6).tolist(),s=sg.round(9).tolist(),**{k:v for k,v in sm.items() if k not in ('elapsed_s',)})
 lib=dict(L_);lib['variant']=L_['variant']+f'; retimed under a joint jerk limit of {J:g} deg/s^3'
 lib['time_law']=tlaw;lib['time_law_stored_unlimited_jerk']={k:v for k,v in L_['time_law'].items() if k not in ('t','s')}
 lib['retimed_from']=dict(file=f'results/r19/stir/lib_stir_cycle_{arm}.json',md5=hashlib.md5(open(f'results/r19/stir/lib_stir_cycle_{arm}.json','rb').read()).hexdigest(),
  unchanged='geometry, states, verification.certificate (a time-law change does not invalidate the certificate; geometry_md5 identical)',script='r19stir2_retime.py',date=time.strftime('%Y-%m-%d'),
  candidates={f'W={c[1]:g}':dict(cycle_s=c[0],A_degps2=c[2]['A_degps2']) for c in C})
 assert hashlib.md5(json.dumps(L_['geometry']['segments']).encode()).hexdigest()==hashlib.md5(json.dumps(lib['geometry']['segments']).encode()).hexdigest()
 fn=f'results/r19/stir/lib_stir_cycle_{arm}_j{int(J)}.json'
 if os.path.exists(fn):
  n=1
  while os.path.exists(fn[:-5]+f'.replaced_{n}.json'):n+=1
  os.rename(fn,fn[:-5]+f'.replaced_{n}.json')
 json.dump(lib,open(fn,'w'));print('saved',fn,'period/stroke',sm['period_per_stroke_s'],'W',W,'A',sm['A_degps2'],flush=True);return sm
def _run(args):
 import subprocess
 arm,J,W=args;r=subprocess.run([sys.executable,__file__,'law',f'ARM={arm}',f'J={J}',f'W={W}'],capture_output=True,text=True)
 return (r.stdout.strip().splitlines() or [''])[-1]+(' ERR '+r.stderr[-300:] if r.returncode else '')
def ladder():
 from concurrent.futures import ThreadPoolExecutor
 arms_=KV.get('ARMS','ur5e_enc2_pgc,fr5_j6_pgc_sp20').split(',');Js=[int(x) for x in KV.get('JS','57296,8000,1000').split(',')]
 jobs=[(a,J,W) for a in arms_ for J in Js for W in WS if not (J*W/2>=A_UR*2 and W>.1)]   # W > 0.1 only where it can matter (A capped at 800 already at a smaller W)
 if KV.get('FORCE')!='1':jobs=[j for j in jobs if not os.path.exists(f'{OUT}/law_{j[0]}_j{j[1]}_w{j[2]:g}.json')]
 print('laws to compute',len(jobs),flush=True)
 with ThreadPoolExecutor(int(KV.get('WORKERS',24))) as ex:
  for line in ex.map(_run,jobs):print(line,flush=True)
 out={}
 for a in arms_:
  for J in Js:out[f'{a}_j{J}']=pick(a,J)
 json.dump(out,open(f'{OUT}/ladder.json','w'),indent=1,default=float)
def check():
 """independent re-evaluation of library entries from the JSON alone, exactly as r19stir_report.py: joint speed /
 acceleration / jerk from the stored one-period law (s' s'' s''' by finite differences, edge_order 2) through q(s) of
 the stored B-splines; ratios to the entry's own limits (the 2 ms grid does not divide the period, so the law is not
 unrolled: the two ends use one-sided differences, as in the report).
 python r19stir2_retime.py check FILES=<lib json>[,<lib json>...]"""
 import r19stir_report as RP
 out={}
 for f in KV['FILES'].split(','):
  L_=json.load(open(f));G=L_['geometry'];segs=[RP.Seg(g) for g in G['segments']];B=np.array([g['s0'] for g in G['segments']]+[G['segments'][-1]['s1']]);Lc=B[-1]
  def q(s,nu=0):
   s=np.atleast_1d(np.asarray(s,float));s=np.mod(s,Lc);k=np.clip(np.searchsorted(B,s,side='right')-1,0,len(segs)-1);o=np.zeros((len(s),6))
   for j in np.unique(k):m=k==j;o[m]=segs[j](segs[j].a+s[m]-B[j],nu)
   return o
  TL_=L_['time_law'];t=np.array(TL_['t']);s=np.array(TL_['s']);P=TL_['period_s'];H=t[1]-t[0];m=np.ones(len(t),bool)
  sd=np.gradient(s,H,edge_order=2);sdd=np.gradient(sd,H,edge_order=2);sddd=np.gradient(sdd,H,edge_order=2)
  q1,q2,q3=q(s,1),q(s,2),q(s,3);v=q1*sd[:,None];a=q2*sd[:,None]**2+q1*sdd[:,None];j=q3*sd[:,None]**3+3*q2*(sd*sdd)[:,None]+q1*sddd[:,None]
  lim=TL_['limits'];V=np.array(lim['v_degps']);A=lim.get('A_degps2_used',lim['A_degps2']['A_UR'] if isinstance(lim['A_degps2'],dict) else lim['A_degps2']);J=lim.get('jerk_degps3')
  pv=np.degrees(np.abs(v[m])).max(0);pa=np.degrees(np.abs(a[m])).max(0);pj=np.degrees(np.abs(j[m])).max(0)
  out[f]=dict(period_per_stroke_s=round(P/5,4),peak_v_degps=pv.round(1).tolist(),peak_a_degps2=pa.round(0).tolist(),peak_j_degps3=pj.round(0).tolist(),
   ratio_v=round(float((pv/V).max()),4),ratio_a=round(float(pa.max()/A),4),ratio_j=None if J is None else round(float(pj.max()/J),4),limits=dict(A_degps2=A,J_degps3=J),
   sdot_ends=[round(float(sd[0]),4),round(float(np.polyval(np.polyder(np.polyfit(t[-8:],s[-8:],3)),P)),4)],geometry_md5=hashlib.md5(json.dumps(G['segments']).encode()).hexdigest(),cert_geometry_md5=L_['verification']['certificate']['geometry_md5'])
  print(f,json.dumps(out[f]),flush=True)
 json.dump(out,open(f'{OUT}/check.json','w'),indent=1)
if __name__=='__main__':
 {'law':law,'pick':pick,'ladder':ladder,'check':check}[sys.argv[1]]()
