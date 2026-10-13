"""R19 #41: the stir cycle with a SHORTER PUSH on the two centre strokes (patterns 0 and 1), built, re-checked at
<= 4 mm and stored as a NEW library entry next to the #3 / #40 ones (which are not touched). New file.

Why (R19_SPILL.md): the spill is a start-up transient: the first two strokes, both through the centre, bulldoze
the freshly dropped heap into the far wall and its front goes over the rim. In the bench sandbox (r19spill_drive.py
MODE=bkeys) ending the push of patterns 0 and 1 at u = 0.06 m instead of 0.10 m (everything else unchanged: start
pose, handle elevation 62 -> 38 deg over the push, timing, lift 5 + 1.5 cm, 4 cm back) removed the spill with the
mixing unchanged; ending it at 0.08 m did not.
Geometry (only what the change touches is new; the rest is the stored #3 cycle, bit for bit):
 work0, work1       NEW: the R15 continuation (r19stir_cycle.follow: 10 ms IK steps, pose <= 5 mm / 3 deg, fast check
                    every step, full check every 25th, plume every step) along the modified bench path (keyframes
                    = stirbench's own keyframes() with U1 = U1S for patterns 0 and 1, results/r19/stir/spill/
                    keys_<tag>.json), started from the stored cycle's own start states (same IK branch and 2pi
                    labels); stored as r19stir_cycle.work_spline (interpolating quintic, or the range-safe smoothing
                    spline if the IK sits on a limit)
 return4->0, return0->1, return1->2
                    NEW: velocity-continuous (C2) quintic returns (r19stir_cycle.ret_A) between the stored / new
                    working parts; options T = 0.2 .. 1.2 s without a via, then the 16 via sets of r19stir_cycle
                    (mid / ends, up / back, 3 .. 15 cm), screened (r19stir_cycle.screen: fast check + ranges + plume at
                    <= 8 mm) cheapest proxy first; the first that certifies is taken
 work2..4, return2->3, return3->4   the stored #3 segments (B-splines from the library entry, unchanged)
Certificate: every segment of the new cycle (new and reused) cut at <= 4 mm (r19stir_cycle.certify: point_bound,
 sub-steps <= 0.5 mm) and checked with Checker.check(full=True) + r19enc_check.one (10 / 5 / 0 mm, joint ranges,
 R11 held-box mesh rule) + the plume rule (arm >= 0.20 m from the wok axis) in the stir scene (r19stir_cycle.model),
 and every certified state again in the CURRENT layout (r19stir2_join scene 'std': PY=.15, keyed rack, spider rest
 (1.56, .20), held spatula_b; plume rule), relabelled exactly as r19stir2_join.cycle relabels the stored cycle.
Time law: the #40 jerk-limited law (r19stir2_law.timelaw, as r19stir2_retime.law): periodic (3 cycles unrolled from
 rest, middle kept), joint speed = datasheet, s' <= 1 on the working parts (never faster than the bench path),
 |d3q/dt3| <= 0.95 x 8000 deg/s^3 (JM=; the independent check of r19stir2_retime.py stays <= J even at the one-sided ends of the stored period), A = min(800, J W / 2) for W in (0.1, 0.2, 0.4) s; the fastest converged law.
python r19spill_cycle.py keys                                   -> results/r19/stir/spill/keys_<tag>.json
python r19spill_cycle.py works   ARM=<arm>                      -> results/r19/stir/spill/cycle_<arm>_<tag>/works.json
python r19spill_cycle.py returns ARM=<arm> [WORKERS=16]         -> .../returns.json
python r19spill_cycle.py cert    ARM=<arm> PART=new|old [WORKERS=16]   -> .../cert_<part>.pkl (stir scene)
python r19spill_cycle.py std     ARM=<arm> [WORKERS=16]         -> .../std_recheck.json (current layout)
python r19spill_cycle.py law     ARM=<arm> W=<s>                -> .../law_j8000_w<W>.npz / .json
python r19spill_cycle.py lib     ARM=<arm>                      -> results/r19/stir/lib_stir_cycle_<arm>_<tag>_j8000.json,
                                                                   .../fromrest_j8000.npz, .../cycle.json
python r19spill_cycle.py report  ARM=<arm>                      -> .../report.json (continuity, ranges, independent re-evaluation)
(<tag> = short01_u06 for U1S = .06)"""
import sys,os,json,time,math,hashlib,pickle
sys.path.insert(0,'.')
import numpy as np
KV=dict(a.split('=',1) for a in sys.argv[2:] if '=' in a)
ARM=KV.get('ARM','ur5e_enc2_pgc');os.environ['ARM']=ARM
U1S=float(KV.get('U1S',.06));PMOD=(0,1);TAG=f'short01_u{int(round(U1S*100)):02d}'
SD='results/r19/stir/spill';OUT=f'{SD}/cycle_{ARM}_{TAG}';KEYSF=f'{SD}/keys_{TAG}.json'
BASE=f'results/r19/stir/lib_stir_cycle_{ARM}.json';LIBN=f'results/r19/stir/lib_stir_cycle_{ARM}_{TAG}_j8000.json'
SIGN=-1;WK=int(KV.get('WORKERS',16));J=8000.;JM=float(KV.get('JM',.95));A_UR=800.;NS=5;DT=.01
SETTLE=1.5;P=2.4
# ---------------------------------------------------------------- keyframes (stirbench.keyframes, METHOD=scrape, patterns 0 and 1 with U1 = U1S)
def keyframes(U1m=U1S,T_=12.):
 import spatula15 as SP
 PAT=[(0.,0.),(30.,0.),(0.,.05),(30.,-.06),(0.,-.05)];U0,U1,E0,E1=-.08,.10,62.,38.;CL=.0015
 mod=lambda k:k%5 in PMOD
 K=[];t=SETTLE;k=0
 while t<SETTLE+T_+P:
  u1=U1m if mod(k) else U1
  def P_(u,e,psi,f):p,R,_=SP.pose(u,e,psi,E0+(E1-E0)*f,clear=CL);return p,R
  ps,e=PAT[k%5];psi=np.radians(ps);ps2,e2=PAT[(k+1)%5]
  for f in np.linspace(0,1,12):K.append((t+.45*f*P,*P_(U0+(u1-U0)*f,e,psi,f)))
  p,R=P_(u1-.04,e,psi,1.);p=p+np.array([0,0,.05]);K.append((t+.56*P,p,R))
  K.append((t+.76*P,p+np.array([0,0,.015]),R))
  p0,R0=P_(U0,e2,np.radians(ps2),0.)
  K.append((t+.88*P,(p+p0)/2+np.array([0,0,.05]),R0));K.append((t+.97*P,p0+np.array([0,0,.015]),R0));t+=P;k+=1
 return K
def keys():
 K=keyframes();K0=keyframes(.10);ref=json.load(open('results/r15/stir_h_scrape_dice_keys.json'))
 assert len(K0)==len(ref['keys']) and all(abs(a[0]-b['t'])==0 and np.array_equal(np.asarray(a[1]),np.array(b['p'])) and np.array_equal(np.asarray(a[2]),np.array(b['R'])) for a,b in zip(K0,ref['keys'])),'keyframes() with U1 = .10 must be the R15 export'
 os.makedirs(SD,exist_ok=True)
 json.dump(dict(note=ref['note']+f'; R19 #41: patterns {list(PMOD)} push to U1 = {U1S} m instead of 0.10 m (lift point U1 - 0.04), everything else as R15 h_scrape_dice',
  grip_local=ref['grip_local'],clear_m=ref['clear_m'],u1_short_m=U1S,patterns_short=list(PMOD),source='r19spill_cycle.keyframes (stirbench.keyframes, METHOD=scrape, PERIOD 2.4, T 12)',
  keys=[dict(t=k[0],p=np.asarray(k[1]).tolist(),R=np.asarray(k[2]).tolist()) for k in K]),open(KEYSF,'w'),indent=1)
 print('saved',KEYSF,len(K),'keys; with U1 = .10 identical to the R15 export')
# ---------------------------------------------------------------- shared
def _init():
 os.environ['ARM']=ARM
 import r19stir_cycle as C
 C.KEYS=KEYSF;C._B.clear();C.OUT=OUT   # the modified bench path; work_spline's smoothing cache goes to this run's folder
def base():
 import r19stir_report as RP
 L_=json.load(open(BASE));G=L_['geometry'];segs={g['name']:RP.Seg(g) for g in G['segments']};return L_,G,segs,np.array(G['state_const'])
def fullq(q0,x):q=np.array(q0,float);q[3:9]=x;return q
# ---------------------------------------------------------------- stage 1: the two new working parts
def _follow(k):
 _init();import r19stir_cycle as C
 L_,G,segs,q0=base();sg=segs[f'work{k}'];q=fullq(q0,sg(sg.a)[0] if np.ndim(sg(sg.a))>1 else sg(sg.a))
 r=C.follow((k,-1,dict(q=q.tolist(),jaw_sign=SIGN)))
 if r['ok']:
  Q=np.array(r['states']);sp,info=C.work_spline(Q,k,SIGN);M=C.model(SIGN);pe,re=C.pose_track(M,sp,k,SIGN,q0)
  r['spline']=dict(info,pose_mm=pe,rot_deg=re);r['start_dev_deg']=float(np.degrees(np.abs(Q[0,3:9]-q[3:9]).max()))
 return r
def works():
 import multiprocessing as mp
 os.makedirs(OUT,exist_ok=True);t0=time.monotonic()
 with mp.Pool(2) as pool:R=pool.map(_follow,[0,1])
 for r in R:print('work',r['stroke'],'ok',r['ok'],{k:r.get(k) for k in ('max_pose_mm','max_rot_deg','pinned_steps','min_reserve_mm','min_plume_mm','min_plume_geom','stop_t','phase','hits','spline','start_dev_deg')},flush=True)
 json.dump(dict(arm=ARM,keys=KEYSF,u1_short_m=U1S,works=R,elapsed_s=round(time.monotonic()-t0)),open(f'{OUT}/works.json','w'))
 print('saved',f'{OUT}/works.json','%.0f s'%(time.monotonic()-t0))
def new_works():
 """the two new working parts as splines (from works.json; work_spline is deterministic and its smoothing choice cached in OUT)"""
 _init();import r19stir_cycle as C
 W=json.load(open(f'{OUT}/works.json'))['works'];out={}
 for r in W:
  assert r['ok'],f"work {r['stroke']} did not pass"
  Q=np.array(r['states']);sp,info=C.work_spline(Q,r['stroke'],SIGN);out[r['stroke']]=(sp,0.,(len(Q)-1)*DT,info,Q)
 return out
def handoffs():
 """(qe, ve, ae, qs, vs, as_) of the three new returns, from the stored / new working parts"""
 L_,G,segs,q0=base();NW=new_works()
 def end(sp,b):return fullq(q0,np.ravel(sp(b))),np.ravel(sp(b,1)),np.ravel(sp(b,2))
 def beg(sp,a):return fullq(q0,np.ravel(sp(a))),np.ravel(sp(a,1)),np.ravel(sp(a,2))
 w4=segs['work4'];w2=segs['work2'];s0,a0,b0=NW[0][:3];s1,a1,b1=NW[1][:3]
 return {'return4->0':(*end(w4,w4.e),*beg(s0,a0)),'return0->1':(*end(s0,b0),*beg(s1,a1)),'return1->2':(*end(s1,b1),*beg(w2,w2.a))},q0
# ---------------------------------------------------------------- stage 2: the three new returns
TGRID=np.round(np.arange(.20,1.201,.10),3);LIFTS=(.03,.06,.10,.15)
def _plan(args):
 """options of one return (as r19stir_cycle.plan_options, variant A): no via, then the 16 via sets; proxy time"""
 name,H=args;_init();import r19stir_cycle as C,arms
 M=C.model(SIGN);V=np.radians(arms.speeds(ARM));A=math.radians(A_UR);qe,ve,ae,qs,vs,as_=H
 VS={('none',0.):([],[])}
 for h in LIFTS:
  for mode,tg in (('up',''),('back','_back')):
   q1,_=C.ik_via(M,qe,qs,h,.5,mode);VS[('mid'+tg,h)]=([q1.tolist()],[.5])
   q1,_=C.ik_via(M,qe,qs,h,0.,mode);q2,_=C.ik_via(M,qe,qs,h,1.,mode);VS[('ends'+tg,h)]=([q1.tolist(),q2.tolist()],[1/3,2/3])
 opts=[]
 for (kind,h),(vq,vf) in VS.items():
  for T in TGRID:
   sp=C.ret_A(qe,ve,ae,qs,vs,as_,float(T),[np.array(v) for v in vq],vf)
   if not C.in_range(M,sp,0,float(T)):continue
   u=np.linspace(0,T,400);pv=np.abs(sp(u,1)).max(0);pa=np.abs(sp(u,2)).max(0)
   opts.append(dict(name=name,T=float(T),via_kind=kind,lift=h,via=vq,f=vf,proxy_s=round(float(T*max(1.,float(np.max(pv/V)),math.sqrt(float(np.max(pa/A))))),4)))
 return sorted(opts,key=lambda o:(o['via_kind']!='none',o['proxy_s']))
def ret_sp(o,H):
 import r19stir_cycle as C
 qe,ve,ae,qs,vs,as_=H;return C.ret_A(qe,ve,ae,qs,vs,as_,o['T'],[np.array(v) for v in o['via']],o['f'])
def _screen(args):
 o,H,q0=args;_init();import r19stir_cycle as C
 M=C.model(SIGN);ok,info=C.screen(M,q0,ret_sp(o,H),0.,o['T']);return dict(o,ok=ok,screen=info)
def returns():
 import multiprocessing as mp
 t0=time.monotonic();HO,q0=handoffs()
 with mp.Pool(min(WK,3),initializer=_init) as pool:OP=dict(zip(HO,pool.map(_plan,list(HO.items()))))
 res={}
 with mp.Pool(WK,initializer=_init) as pool:
  for name,opts in OP.items():
   # no-via options first (cheapest proxy first), then the via sets: screened in batches of WK, stop once 3 pass
   passed=[];fails=[]
   for i in range(0,len(opts),WK):
    out=pool.map(_screen,[(o,HO[name],q0) for o in opts[i:i+WK]],chunksize=1)
    passed+=[x for x in out if x['ok']];fails+=[x for x in out if not x['ok']]
    if len(passed)>=3:break
   passed.sort(key=lambda x:(x['via_kind']!='none',x['proxy_s']))
   res[name]=dict(options=len(opts),passed=passed,fails=[dict(T=x['T'],via_kind=x['via_kind'],lift=x['lift'],**x['screen']) for x in fails][:12])
   print(name,'options',len(opts),'passed',[(x['T'],x['via_kind'],x['lift'],x['proxy_s']) for x in passed[:4]],'fails',[(x['T'],x['via_kind'],x['screen'].get('at'),x['screen'].get('hits'),x['screen'].get('plume_mm')) for x in fails[:4]],'%.0f s'%(time.monotonic()-t0),flush=True)
 json.dump(dict(arm=ARM,returns=res,elapsed_s=round(time.monotonic()-t0)),open(f'{OUT}/returns.json','w'),default=float)
 print('saved',f'{OUT}/returns.json')
# ---------------------------------------------------------------- the new cycle's segments, in cycle order
NAMES=['work0','return0->1','work1','return1->2','work2','return2->3','work3','return3->4','work4','return4->0']
NEW={'work0','return0->1','work1','return1->2','return4->0'}
def segments(pick=None):
 """[(name, spline, a, b)] of the new cycle; pick = {return name: option index in returns.json passed list}"""
 L_,G,segs,q0=base();NW=new_works();HO,_=handoffs();RJ=json.load(open(f'{OUT}/returns.json'))['returns'];pick=pick or {}
 out=[]
 for n in NAMES:
  if n in ('work0','work1'):sp,a,b,_,_=NW[int(n[-1])];out.append((n,sp,a,b))
  elif n in NEW:
   o=RJ[n]['passed'][pick.get(n,0)];out.append((n,ret_sp(o,HO[n]),0.,o['T']))
  else:s=segs[n];out.append((n,s,s.a,s.e))
 return out,q0
def cert():
 """stir-scene certificate (r19stir_cycle.certify) of the new segments (PART=new; a return that fails moves to its
 next screened option) or of the reused ones (PART=old); SEGS=<names> certifies only those (each command < 5 min);
 results are cached per segment in cert_<part>.pkl"""
 import multiprocessing as mp,r19stir_cycle as C
 _init();t0=time.monotonic();part=KV.get('PART','new');fn=f'{OUT}/cert_{part}.pkl';cache=pickle.load(open(fn,'rb')) if os.path.exists(fn) else {}
 RJ=json.load(open(f'{OUT}/returns.json'))['returns'];pick=cache.get('pick',{n:0 for n in NEW if n.startswith('return')})
 only=KV['SEGS'].split(',') if 'SEGS' in KV else None
 mine=lambda n:((n in NEW)==(part=='new')) and (only is None or n in only)
 with mp.Pool(WK,initializer=_init) as pool:
  while True:
   S,q0=segments(pick);todo=[(n,sp,a,b) for n,sp,a,b in S if mine(n) and (n,pick.get(n)) not in cache]
   if todo:
    for (n,sp,a,b),c in zip(todo,C.certify(pool,SIGN,todo,q0)):cache[(n,pick.get(n))]=c;print(n,'option',pick.get(n),'states',len(c['Q']),'ok',c['summary']['ok'],list(c['summary']['hit_pairs'])[:2],'%.0f s'%(time.monotonic()-t0),flush=True)
    cache['pick']=pick;pickle.dump(cache,open(fn,'wb'))
   bad=[n for n,sp,a,b in S if mine(n) and not cache[(n,pick.get(n))]['summary']['ok']]
   if not bad:break
   for n in bad:
    assert n.startswith('return'),f'{n} fails its certificate: {list(cache[(n,None)]["summary"]["hit_pairs"])[:3]}'
    pick[n]+=1
    if pick[n]>=len(RJ[n]['passed']):raise SystemExit(f'{n}: no screened option certifies')
  cache['pick']=pick;pickle.dump(cache,open(fn,'wb'))
 for n,sp,a,b in S:
  if mine(n):print(json.dumps(C.seg_summary(dict(cache[(n,pick.get(n))],name=n)),default=float))
 print('saved',fn,'%.0f s'%(time.monotonic()-t0))
def certified():
 """the stir-scene certificate of every segment of the new cycle, in cycle order -> [(name, cert)], pick"""
 cn=pickle.load(open(f'{OUT}/cert_new.pkl','rb'));co=pickle.load(open(f'{OUT}/cert_old.pkl','rb'));pick=cn['pick']
 missing=[n for n in NAMES if (n,pick.get(n)) not in (cn if n in NEW else co)];assert not missing,f'not certified yet: {missing}'
 return [(n,(cn if n in NEW else co)[(n,pick.get(n))]) for n in NAMES],pick
def std():
 """every certified state of the new cycle re-checked in the current layout (r19stir2_join scene 'std'), relabelled
 as r19stir2_join.cycle relabels the stored cycle (nearest to the spatula hand-off, every state in range)"""
 sv=sys.argv;sys.argv=['r19stir2_join.py','cycle',f'ARM={ARM}',f'WORKERS={WK}']
 import r19stir2_join as JN
 sys.argv=sv;t0=time.monotonic()
 CS,pick=certified();Q=np.concatenate([c['Q'] for n,c in CS]);kinds=[n for n,c in CS for _ in c['Q']]
 M=JN.scene('stir');r,U,lab=JN.spat_end();k=JN.cycle_relabel(dict(states=dict(q=Q.tolist()),hub=dict(state=Q[0].tolist())),U[-1],M['lo'],M['hi'])
 Qr=Q.copy();Qr[:,3:9]+=2*np.pi*k;rs,cs=JN.certify('std',Qr);per={}
 for kd,x in zip(kinds,rs):
  e=min(v[0] for kk,v in x['cl'].items() if kk!='self');p=per.setdefault(kd,dict(states=0,hits=0,min_env_mm=1e9,min_plume_mm=1e9));p['states']+=1;p['hits']+=bool(x['hits'] or not x['ranges']);p['min_env_mm']=min(p['min_env_mm'],e);p['min_plume_mm']=min(p['min_plume_mm'],x['plume'][0])
 out=dict(arm=ARM,relabel_2pi=k.astype(int).tolist(),scene='std: R18b chain scene, plating spot y .15, kitchen19pot keyed rack + spider rest (1.56, .20), held spatula_b, plume rule (r19stir2_join.scene)',layer=JN.scene('std')['layer'],certificate=cs,per_segment=per,elapsed_s=round(time.monotonic()-t0))
 json.dump(out,open(f'{OUT}/std_recheck.json','w'),indent=1,default=float);print(json.dumps(cs,default=float),'%.0f s'%(time.monotonic()-t0))
# ---------------------------------------------------------------- stage 3: time law (jerk 8000), library entry
def path_of():
 import r19stir2_law as TL
 S,q0=segments(certified()[1]);path=TL.PathN([(sp,a,b) for n,sp,a,b in S],6,per=True);isw=np.array([n.startswith('work') for n,_,_,_ in S])
 def capf(s):
  r=np.mod(np.asarray(s,float),path.L);k=np.clip(np.searchsorted(path.B,r,side='right')-1,0,len(path.segs)-1);return np.where(isw[k],1.,1e12)
 return S,q0,path,capf
def law():
 import arms,r19stir2_law as TL,r19stir2_retime as RT
 W=float(KV['W']);A=min(A_UR,J*W/2);t0=time.monotonic();S,q0,path,capf=path_of();V=np.radians(arms.speeds(ARM))
 tl=TL.timelaw(path,V,math.radians(A),capf,0.,0.,W,reps=3,iters=int(KV.get('ITERS',80)),J=math.radians(J)*JM)
 sm=RT.summary(path,tl,V,math.radians(A),capf,math.radians(J),[n for n,_,_,_ in S]);sm.update(J_degps3=J,jerk_margin=JM,W_s=W,A_degps2=A,elapsed_s=round(time.monotonic()-t0))
 fn=f'{OUT}/law_j{int(J)}_w{W:g}';np.savez(fn+'.npz',t=tl['t'],s=tl['s'],sd=tl['sd']);json.dump(sm,open(fn+'.json','w'),indent=1)
 print(ARM,'W',W,'A',A,json.dumps({k:sm[k] for k in ('period_per_stroke_s','converged','iters','worst_ratio','segment_s')}),'%.0f s'%sm['elapsed_s'],flush=True)
def bspl(sp):
 if hasattr(sp,'b'):   # a stored segment (r19stir_report.Seg): its own JSON fields
  d=dict(type='bspline',k=int(sp.b.k),knots=sp.b.t.tolist(),coef=np.asarray(sp.b.c).tolist())
  if sp.sq:d['sq']={str(j):[float(l),float(g)] for j,(l,g) in sp.sq.items()};d['sq_note']='coordinate j stored as h: q_j = limit + sign*h^2'
  return d
 import r19stir_cycle as C
 return C.bspl(sp)
def lib():
 import arms,r19stir2_retime as RT,r19stir_cycle as C,r19enc_check as RC
 from scipy.interpolate import CubicSpline
 _init();t00=time.monotonic();S,q0,path,capf=path_of();CS,pick=certified();L_=json.load(open(BASE));V=np.radians(arms.speeds(ARM))
 # the fastest converged jerk-limited law
 cand=[]
 for W in (.1,.2,.4):
  fn=f'{OUT}/law_j{int(J)}_w{W:g}'
  if os.path.exists(fn+'.json'):
   sm=json.load(open(fn+'.json'))
   if sm['converged'] and max(sm['worst_ratio'].values())<=1+1e-3:cand.append((sm['cycle_s'],W,sm))
 assert cand,'no converged law'
 _,W,sm=min(cand,key=lambda c:c[0]);z=np.load(f'{OUT}/law_j{int(J)}_w{W:g}.npz');t,s=z['t'],z['s'];L=path.L;t1,t2=np.interp(L,s,t),np.interp(2*L,s,t)
 H=t[1]-t[0];tg=np.arange(0,t2-t1-1e-9,H);sg=CubicSpline(t,s)(t1+tg)-L
 np.savez(f'{OUT}/fromrest_j{int(J)}.npz',t=t,s=s,sd=z['sd'])
 geo=[];B=path.B
 for j,(n,sp,a,b) in enumerate(S):geo.append(dict(name=n,s0=round(float(B[j]),9),s1=round(float(B[j+1]),9),local=[float(a),float(b)],**bspl(sp)))
 st=[q.tolist() for n,c in CS for q in c['Q']];kinds=[n for n,c in CS for _ in c['Q']]
 allrs=[r_ for n,c in CS for r_ in c['rs']];S_=RC.summarize(allrs,np.arange(len(allrs)));stdr=json.load(open(f'{OUT}/std_recheck.json'))
 gmd5=hashlib.md5(json.dumps(geo).encode()).hexdigest();smd5=hashlib.md5(json.dumps(st).encode()).hexdigest()
 cert=dict(L_['verification']['certificate']);cert.update(states=len(st),max_step_bound_mm=max(c['max_step_bound_mm'] for n,c in CS),hit_states=S_['hit_states'],out_of_range_states=S_['out_of_range_states'],
  min_env_reserve_mm=S_['min_env_reserve_mm'],min_env_pair=S_['min_env_pair'],min_self_reserve_mm=S_['min_self_reserve_mm'],min_self_pair=S_['min_self_pair'],min_reserve_by_category=S_['min_reserve_by_category'],
  min_plume_mm=S_['min_plume_mm'],min_plume_geom=S_['min_plume_geom'],plume_violations=S_['plume_violations'],ok=S_['ok'],segments=[C.seg_summary(dict(c,name=n)) for n,c in CS],
  geometry_md5=gmd5,states_md5=smd5,scene_model_md5=C.model(SIGN)['cfg_md5'],cache=f'{OUT}/cert_new.pkl, {OUT}/cert_old.pkl (per-state results)',reused_segments_from=BASE,
  current_layout_recheck=dict(file=f'{OUT}/std_recheck.json',**{k:stdr['certificate'][k] for k in ('ok','states','hit_states','out_of_range_states','min_env_reserve_mm','min_self_reserve_mm','min_plume_mm','plume_violations')},relabel_2pi=stdr['relabel_2pi']),
  date=time.strftime('%Y-%m-%d'),elapsed_s_this_run=None)
 assert cert['ok'] and cert['hit_states']==0 and cert['out_of_range_states']==0 and cert['plume_violations']==0 and cert['max_step_bound_mm']<=4.+1e-9,'not certified: no library entry'
 assert stdr['certificate']['ok'] and stdr['certificate']['hit_states']==0 and stdr['certificate']['plume_violations']==0,'current layout re-check failed: no library entry'
 lim=dict(L_['time_law']['limits']);lim.update(jerk_degps3=J,jerk_source=RT.SRC[int(J)],A_degps2_used=sm['A_degps2'],W_s=sm['W_s'],A_note='A = min(800, J W / 2): with the moving-average filter W the time law alone adds a jerk up to ~2 A / W')
 tlaw=dict(limits=lim,law=f'jerk-limited periodic law (middle of 3 unrolled cycles), one period from t = 0 (s = 0) on a 2 ms grid; repeat with t + period, s + length; q(t) = q(s(t)); |d3q/dt3| <= {J:g} deg/s^3 on the 2 ms grid',
  period_s=float(t2-t1),t=tg.round(6).tolist(),s=sg.round(9).tolist(),**{k:v for k,v in sm.items() if k not in ('elapsed_s',)})
 RJ=json.load(open(f'{OUT}/returns.json'))['returns'];W_=json.load(open(f'{OUT}/works.json'))
 lib=dict(id='STIR_CYCLE',arm=ARM,arm_name=L_['arm_name'],variant=f'A: velocity-continuous (C2) periodic cycle; R19 #41 spill fix: the centre strokes (patterns 0 and 1) push to u = {U1S} m instead of 0.10 m; retimed under a joint jerk limit of {J:g} deg/s^3',
  params=dict(L_['params'],stroke=f'h_scrape_dice with patterns {list(PMOD)} pushing to U1 = {U1S} m ({KEYSF})',u1_short_m=U1S,patterns_short=list(PMOD)),
  start_hub='H_stir0',end_hub='H_stir0',hub=dict(L_['hub'],q=[round(float(x),9) for x in path(0.)[0]],state=[float(x) for x in fullq(q0,path(0.)[0])],note='stroke 0 start (the same state as the #3 cycle); from rest the geometry is run with a ramp (three cycles from rest: %s s)'%sm['three_cycles_from_rest_s']),
  pre=L_['pre'],post=L_['post'],
  geometry=dict(L_['geometry'],param='s = bench time of the (modified) bench path on the working parts (ds/dt <= 1), nominal time on the returns; q(s) is C2 across every hand-off and around the cycle',length=L,segments=geo,
   new_segments=sorted(NEW),reused_segments=[n for n in NAMES if n not in NEW],works=dict(file=f'{OUT}/works.json',info=[{k:r.get(k) for k in ('stroke','max_pose_mm','max_rot_deg','pinned_steps','min_reserve_mm','min_plume_mm','spline')} for r in W_['works']]),
   returns=[dict(name=n,option=pick.get(n),**{k:RJ[n]['passed'][pick.get(n)][k] for k in ('T','via_kind','lift','proxy_s')}) for n in NAMES if n.startswith('return') and n in NEW]),
  time_law=tlaw,states=dict(layout=L_['states']['layout'],note='the certified states (stir scene), <= 4 mm apart, in cycle order',kinds=kinds,q=st),
  verification=dict(status='verified',certificate=cert),derived_from=dict(file=BASE,md5=hashlib.md5(open(BASE,'rb').read()).hexdigest(),script='r19spill_cycle.py',issue='GitHub #41',date=time.strftime('%Y-%m-%d')))
 if os.path.exists(LIBN):raise SystemExit(f'{LIBN} exists: not overwritten (rename it first)')
 json.dump(lib,open(LIBN,'w'),default=float)
 json.dump(dict(arm=ARM,lib=LIBN,law=dict(W=W,**{k:v for k,v in sm.items()}),certificate={k:v for k,v in cert.items() if k!='segments'},segments=cert['segments'],pick=pick),open(f'{OUT}/cycle.json','w'),indent=1,default=float)
 print('saved',LIBN,'period/stroke',sm['period_per_stroke_s'],'W',W,'A',sm['A_degps2'],'states',len(st),'%.0f s'%(time.monotonic()-t00))
def report():
 """independent re-evaluation from the new library JSON alone (as r19stir_report.py): continuity at every hand-off
 (q, q', q'') and around the cycle, joint ranges on a dense grid, stored states on the geometry"""
 import r19stir_report as RP
 L_=json.load(open(LIBN));G=L_['geometry'];segs=[RP.Seg(g) for g in G['segments']];names=[g['name'] for g in G['segments']]
 jumps=[]
 for i in range(len(segs)):
  nx=(i+1)%len(segs);e=segs[i];n=segs[nx]
  d=[float(np.degrees(np.abs(np.ravel(e(e.e,nu))-np.ravel(n(n.a,nu))).max())) for nu in (0,1,2)];jumps.append(dict(at=f'{names[i]} -> {names[nx]}',dq_deg=round(d[0],6),dq1_degps=round(d[1],6),dq2_degps2=round(d[2],4)))
 _init();import r19stir_cycle as C
 M=C.model(SIGN);lo,hi=M['lo'],M['hi'];rng=[]
 for g,sg in zip(G['segments'],segs):
  X=sg(np.linspace(sg.a,sg.e,4001));rng.append(dict(name=g['name'],min_margin_deg=round(float(np.degrees(np.minimum(X-lo,hi-X).min())),4)))
 Qs=np.array(L_['states']['q']);kinds=L_['states']['kinds'];dev=0.
 for nm in dict.fromkeys(kinds):
  i=names.index(nm);X=Qs[[x==nm for x in kinds]][:,3:9];u=np.linspace(segs[i].a,segs[i].e,20001);Y=segs[i](u)
  dev=max(dev,max(float(np.min(np.abs(Y-x).max(1))) for x in X[::7]))
 out=dict(lib=LIBN,handoff_jumps=jumps,max_jump=dict(dq_deg=max(x['dq_deg'] for x in jumps),dq1_degps=max(x['dq1_degps'] for x in jumps),dq2_degps2=max(x['dq2_degps2'] for x in jumps)),
  joint_range_margin=rng,min_range_margin_deg=min(x['min_margin_deg'] for x in rng),stored_states_off_geometry_deg=round(np.degrees(dev),6))
 json.dump(out,open(f'{OUT}/report.json','w'),indent=1);print(json.dumps({k:v for k,v in out.items() if k not in ('handoff_jumps','joint_range_margin')}))
if __name__=='__main__':
 {'keys':keys,'works':works,'returns':returns,'cert':cert,'std':std,'law':law,'lib':lib,'report':report}[sys.argv[1]]()
