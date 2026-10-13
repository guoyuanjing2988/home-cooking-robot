"""R19 cart (issue #14): dynamic tip-over, sliding and protective stops along the real smoothed time laws.

1. Time laws: each R19 smoothed whole-action movement (results/r19/smooth/<act>_spline_move.json, the checked
   geometry) is re-timed exactly as r19smooth.py does (Seg + time_segment, limits r19smooth.LIMITS[profile];
   reproduces R19_SMOOTH.md's times) -> q, q', q'' on the 2 ms grid. The R15 stir cycle comes from its stored
   states (results/r19/stir/: working parts at the bench timing, returns as rest-to-rest trapezoids at
   180 deg/s / 360 deg/s^2 as r15stirwalk2, plus a STOP at both ends of every working part, because the stored
   law has velocity jumps there; the ramps use 360 deg/s^2 on the leading joint, E).
2. Inverse dynamics: MuJoCo mj_inverse + mj_rnePostConstraint on the cart+arm tree, contacts off; cfrc_int of
   the cart root = the wrench the floor (and bumper) must supply incl. gravity, the cart's own acceleration and
   the held payload (r19smooth.load_parts: wok 1.8 kg + food 1.15 / water 0.5, spatula 0.3, lid 0.8, spider
   0.45, put on R_tool). Checked against a finite-difference Newton-Euler (agrees to 1e-6 N, N.m).
   Variants: 'sim' (the sim's boxes, menagerie UR5e) and 'bom' (r19cart_bom: BOM cart, UR DH link table).
3. Support: drive wheels (+-.22, -.22), casters (+-.22 + trail, .11); bumper face y .21, z .30.
   casters='swivel' (R10 "two casters"): horizontal floor force only at the two drive wheels (x by the motors,
   y by tyre side friction); the casters swivel, trail 35 mm behind the last motion (E; unknown when the cart
   has not moved yet -> the worse side). The bumper cannot help: its -y reaction would have to be carried by
   the drive wheels, which unload as the CoP moves to the caster line (mu x z_b / wheelbase = 0.45 < 1).
   casters='rigid' (fixed castors): y friction on all four wheels; the bumper bears on the cabinet up to
   min(Fb_max, mu N - |F_y|) (mobile.dock_stability's model), front margin as there.
   Margin = signed distance of the floor centre of pressure (CoP = ZMP) to the support-polygon edges, minus the
   worst-direction extras: floor slope (E), tether 20 N at 0.10 m (mobile.py design cap), process force at the
   TCP height. Friction: per drive wheel mu_req = |f| / N_wheel; x split by wheel load, y split incl. the yaw
   moment (the two drive wheels are in tandem along x, so yaw is resisted by differential side force).
4. Stops from every 10 ms of every law (cart E-stops every 50 ms): arm cat0 (each joint at its own maximum
   deceleration) / cat12 (path-synchronous, same limit; UR manual 6.2: "the load during stopping motion is
   independent of the stop category type") / none, combined with: cart continues on its law / cart E-stop at
   0.5 m/s^2 / traction-limited cart E-stop (mu x drive load, <= 2 x 30 N.m peak / r). UR5e stopping data:
   UR5e manual 2.3 graphs at 100 % speed and extension, constant-deceleration fit -> ALPHA.
   Reported per case: minimum instantaneous ZMP margin (rigid body), rocking energy ratio (angular impulse of
   the moment beyond an edge -> rotation energy, divided by the energy to lift the CoG over that edge; >= 1 is a
   tip-over), wheel lift, slip distance.
python r19cart_dyn.py ACT=wok|spatula|lid|spider|lever|stir [PRO=same,fast,fastcart|none] [VAR=bom,sim]
  [STOPS=1] [ALPHA66=1] [ASWEEP=.15,.3,.5,.8,1.2] [TAG=]  -> results/r19/cart/dyn_<act><TAG>.json"""
import sys,os,json,copy,time,math;sys.path.insert(0,'.')
import numpy as np,mujoco
from scipy.interpolate import BSpline,CubicSpline
import r19smooth as S
import r19cart_bom as B
OUT='results/r19/cart';G=9.81;H=S.H
XW,YD,YC,ZB=.22,-.22,.11,.30   # contact lines and bumper height (scene.py dock+deep_cart; mobile.dock_stability)
BASE=dict(mu=.5,Fb_max=250.,trail=.035,casters='swivel',slope_deg=0.,tether_N=20.,tether_z=.10,proc_N=0.)
# UR5e stop deceleration, rad/s^2 = pi / t_stop at 100 % speed (180 deg/s) and 100 % extension (UR manual 2.3):
# max payload (5 kg): J0 .164 s, J1 .288 s, J2 .162 s; 66 % of 5 kg: J0 .140, J1 .210, J2 .102 (manual p.19-23).
# Wrists: no data, as J2 (E). The graphs are linear in speed through ~0, i.e. constant deceleration (J0: 19 m/s^2
# at the TCP from both the 33 % and the 100 % speed points; v0 = 2 d / t is the same at all payloads).
ALPHA={'max':np.pi/np.array([.164,.288,.162,.162,.162,.162]),'66':np.pi/np.array([.140,.210,.102,.102,.102,.102])}
PEAK_T,R_WHEEL=30.,.0825   # ZLLG65ASM500 V2.0 peak torque 30 N.m, 165 mm wheel (WHEEL datasheet)
EDGES=['back','right(+x)','front','left(-x)']
KV=dict(a.split('=',1) for a in sys.argv[1:]) if __name__=='__main__' else {}
# ------------------------------------------------------------------ model and wrench
def make_model(ctx,variant,**kw):
 m=copy.deepcopy(ctx['m']);d=mujoco.MjData(m)
 m.opt.disableflags|=int(mujoco.mjtDisableBit.mjDSBL_CONTACT)|int(mujoco.mjtDisableBit.mjDSBL_LIMIT)|int(mujoco.mjtDisableBit.mjDSBL_EQUALITY)
 info=B.patch(m,d,variant,**kw)
 return dict(m=m,d=d,info=info,tool=B.body_I(m,m.body('R_tool').id),rid=m.body('rail_structure').id,sid=m.site('R_prep').id,ctx=ctx)
def set_payload(md,food,parts=None):
 """Held parts (+ food / water at [0,0,.02], disc r .12) on R_tool. parts=None: the chain's object (frame ctx T)."""
 ctx=md['ctx'];ps=list(ctx['parts'] if parts is None else parts)+([(food,np.array([0,0,.02]),.12)] if food else [])
 if not ps:B.tool_payload(md['m'],md['d'],md['tool'],np.eye(4),0.,None,None);return 0.
 M=sum(p[0] for p in ps);c=sum(p[0]*p[1] for p in ps)/M;I=np.zeros((3,3))
 for mm,cc,rr in ps:
  Id=np.diag([mm*rr*rr/4,mm*rr*rr/4,mm*rr*rr/2]);dd=cc-c;I+=Id+mm*(dd@dd*np.eye(3)-np.outer(dd,dd))
 B.tool_payload(md['m'],md['d'],md['tool'],ctx['T'] if parts is None else np.eye(4),M,c,I);return M
def wrench(md,Q,QD,QA):
 """Required external wrench on the cart+arm tree: F (n,3) and moment M (n,3) about the floor point under the
 cart origin; system CoM height; TCP height."""
 m,d,rid,sid=md['m'],md['d'],md['rid'],md['sid'];n=len(Q);F=np.zeros((n,3));M=np.zeros((n,3));zc=np.zeros(n);zt=np.zeros(n)
 for i in range(n):
  d.qpos[:]=Q[i];d.qvel[:]=QD[i];d.qacc[:]=QA[i];mujoco.mj_inverse(m,d);mujoco.mj_rnePostConstraint(m,d)
  c=d.subtree_com[rid];f=d.cfrc_int[rid];F[i]=f[3:];M[i]=f[:3]+np.cross(c-[Q[i,0],Q[i,1],0.],f[3:]);zc[i]=c[2];zt[i]=d.site_xpos[sid][2]
 return F,M,zc,zt
def wrench_law(md,law,Q,QD,QA):
 """wrench() with the payload of each sample's piece (food changes between pieces)."""
 out=[np.zeros((len(Q),3)),np.zeros((len(Q),3)),np.zeros(len(Q)),np.zeros(len(Q))]
 for fv in sorted(set(law['food'].tolist())):
  sel=law['food']==fv;set_payload(md,fv,law.get('parts'));r=wrench(md,Q[sel],QD[sel],QA[sel])
  for o_,r_ in zip(out,r):o_[sel]=r_
 return out
# ------------------------------------------------------------------ time laws
def laws(ctx,act,pro,lim=None):
 """Re-time the stored spline movement exactly as r19smooth.py; dwells as one static sample each."""
 mv=json.load(open(f'results/r19/smooth/{act}_spline_move.json'));w=np.array(mv['scale_w']);q0=np.array(mv['q0'])
 L=dict(S.LIMITS[pro]);L.update(lim or {});T=[];Q=[];QD=[];QA=[];FOOD=[];PIECE=[];DW=[];t0=0.;tot=0.
 for k,pc in enumerate(mv['pieces']):
  p=S.Path(BSpline(np.array(pc['knots']),np.array(pc['coef']),pc['k']),w,q0,pc['kind'],sq={int(a):(v[0],v[1]) for a,v in pc.get('sq',{}).items()})
  seg=S.Seg(ctx,p,pc['food_kg'],L,pc['fixed']);rt=S.time_segment(ctx,seg);t,s,sd=rt['t'],np.clip(rt['s'],0,p.L),rt['sd'];tot+=rt['time_s']
  sdd=np.gradient(sd,t);q=p.q(s);qp=p.q(s,1);qpp=p.q(s,2);qd=np.zeros_like(q);qa=np.zeros_like(q)
  qd[:,S.DOF]=qp*sd[:,None];qa[:,S.DOF]=qpp*(sd*sd)[:,None]+qp*sdd[:,None]
  T.append(t0+t);Q.append(q);QD.append(qd);QA.append(qa);n=len(t);FOOD+=[pc['food_kg']]*n;PIECE+=[k]*n;DW+=[0]*n;t0+=t[-1]
  if pc['dwell_after_s']>0:
   T.append(np.array([t0+pc['dwell_after_s']/2]));Q.append(q[-1:]);QD.append(0*qd[-1:]);QA.append(0*qa[-1:]);FOOD+=[pc['food_kg']];PIECE+=[k];DW+=[1];t0+=pc['dwell_after_s']
 return dict(t=np.concatenate(T),q=np.vstack(Q),qd=np.vstack(QD),qa=np.vstack(QA),food=np.array(FOOD),piece=np.array(PIECE),dwell=np.array(DW,bool),motion_s=tot,limits=L)
def stir_law(k=1.):
 """R15 stir cycle as executable. Working parts: the stored 10 ms IK states (x working_slowdown) as a cubic
 spline in bench time u, run at path speed du/dt = 1/k (k = 1: the bench timing), started from and stopped to
 rest ON the path by a linear speed ramp whose leading-joint acceleration is 360 deg/s^2 (E, r15stirwalk2's AMAX);
 returns: rest-to-rest straight joint moves (trapezoid 180 deg/s, 360 deg/s^2, as r15stirwalk2)."""
 st=json.load(open('results/r19/stir/stirwalk2_h_scrape_dice_r17.json'));Qs=np.array(st['states']['q']);kinds=st['states']['kinds']
 dt=.01*st['working_slowdown'];AM=np.radians(360.);VM=np.radians(180.)
 runs=[];i=0
 while i<len(kinds):
  j=i
  while j<len(kinds) and kinds[j]==kinds[i]:j+=1
  runs.append((kinds[i],i,j));i=j
 T=[];Q=[];QD=[];QA=[];KIND=[];t0=[0.]
 def add(t,q,qd,qa,kind):T.append(t0[0]+t);Q.append(q);QD.append(qd);QA.append(qa);KIND.extend([kind]*len(t));t0[0]+=t[-1]+H
 for kind,a,b in runs:
  X=Qs[a:b]
  if kind=='return':
   dq=X[-1,3:9]-X[0,3:9];lead=np.abs(dq).max()
   if lead<1e-9:continue
   tt=2*math.sqrt(lead/AM) if lead<VM*VM/AM else lead/VM+VM/AM;ta=min(tt/2,VM/AM);vm=AM*ta
   t=np.arange(0,tt+H/2,H);sd=np.minimum.reduce([t*AM,np.full_like(t,vm),(tt-t)*AM]).clip(0);sdd=np.where(t<ta,AM,np.where(t>tt-ta,-AM,0.))
   s_=np.r_[0,np.cumsum((sd[1:]+sd[:-1])/2*H)];k_=lead/s_[-1];s_*=k_;sd=sd*k_;sdd=sdd*k_
   u=dq/lead;q=np.tile(X[0],(len(t),1));q[:,3:9]+=s_[:,None]*u;qd=np.zeros_like(q);qa=np.zeros_like(q);qd[:,3:9]=sd[:,None]*u;qa[:,3:9]=sdd[:,None]*u
   add(t,q,qd,qa,'return')
  else:
   tk=np.arange(len(X))*dt;cs=CubicSpline(tk,X[:,3:9]);Tw=tk[-1];sm=1./k
   tri=np.abs(cs(0.,1)).max()*sm/AM;tro=np.abs(cs(Tw,1)).max()*sm/AM;Tt=Tw/sm+(tri+tro)/2
   t=np.arange(0,Tt+H/2,H);sig=np.minimum.reduce([sm*t/max(tri,1e-9),np.full_like(t,sm),sm*(Tt-t)/max(tro,1e-9)]).clip(0)
   dsig=np.where(t<tri,sm/max(tri,1e-9),np.where(t>Tt-tro,-sm/max(tro,1e-9),0.))
   u=np.r_[0,np.cumsum((sig[1:]+sig[:-1])/2*H)];u*=Tw/u[-1]
   q=np.tile(X[0],(len(t),1));q[:,3:9]=cs(u);v1=cs(u,1);qd=np.zeros_like(q);qa=np.zeros_like(q);qd[:,3:9]=v1*sig[:,None];qa[:,3:9]=cs(u,2)*(sig*sig)[:,None]+v1*dsig[:,None]
   add(t,q,qd,qa,kind)
 n=sum(len(t) for t in T)
 return dict(t=np.concatenate(T),q=np.vstack(Q),qd=np.vstack(QD),qa=np.vstack(QA),food=np.zeros(n),piece=np.zeros(n,int),dwell=np.zeros(n,bool),kind=np.array(KIND),motion_s=t0[0],
  parts=[(.3,np.zeros(3),0.)],meta=dict(period_bench_s=st['period_bench_s'],working_slowdown=st['working_slowdown'],feasible_period_s=st['feasible_period_s'],work_time_scale=k,
  cycle_s=round(t0[0],2),note='spatula 0.3 kg at the TCP (E); working parts start/stop on the path at 360 deg/s^2 (E)'))
# ------------------------------------------------------------------ support
def polygon(tx):
 """CCW vertices (n,4,2): drive (-XW,YD),(XW,YD), casters (XW+tx,YC),(-XW+tx,YC)."""
 tx=np.atleast_1d(tx);P=np.zeros((len(tx),4,2));P[:,0]=[-XW,YD];P[:,1]=[XW,YD];P[:,2,0]=XW+tx;P[:,2,1]=YC;P[:,3,0]=-XW+tx;P[:,3,1]=YC;return P
def edge_dist(P,p):
 """Inward signed distance of points p (n,2) to the 4 edges (n,4): back, right, front, left."""
 out=np.zeros((len(p),4))
 for e in range(4):
  a=P[:,e];b=P[:,(e+1)%4];t=b-a;nrm=np.stack([-t[:,1],t[:,0]],1)/np.linalg.norm(t,axis=1)[:,None];out[:,e]=np.einsum('ij,ij->i',p-a,nrm)
 return out
def caster_sign(vx):
 """Sign of the last cart motion (0 before the first motion): swivel casters trail behind it."""
 s=np.zeros(len(vx));last=0.
 for i,v in enumerate(vx):
  if abs(v)>1e-6:last=np.sign(v)
  s[i]=last
 return s
def poly_E(p,sg,o):
 """Edge distances of CoP points p (n,2); swivel casters trail behind the last motion (sg), unknown -> worse side."""
 if o['casters']=='rigid':return edge_dist(polygon(np.zeros(len(p))),p)
 E=edge_dist(polygon(-o['trail']*sg),p);st=sg==0
 if st.any():E[st]=np.minimum(edge_dist(polygon(np.full(st.sum(),o['trail'])),p[st]),edge_dist(polygon(np.full(st.sum(),-o['trail'])),p[st]))
 return E
def support(F,M,sg,zc,zt,o):
 """Margins (m), CoP, bumper force, drive load and friction demand for required wrenches F, M (n,3)."""
 o={**BASE,**o};N=F[:,2];th=math.radians(o['slope_deg']);rigid=o['casters']=='rigid'
 extra_m=N*math.tan(th)*zc+o['tether_N']*o['tether_z']+o['proc_N']*zt;extra_f=N*math.tan(th)+o['tether_N']+o['proc_N']
 dx=extra_m/N;xp=-M[:,1]/N;yp0=M[:,0]/N
 if rigid:
  Fneed=np.maximum(0,(M[:,0]+extra_m-YC*N)/ZB);Fcap=np.minimum(o['Fb_max'],np.maximum(0,o['mu']*N-np.abs(F[:,1])-extra_f));Fb=np.minimum(Fneed,Fcap)
 else:Fneed=Fcap=Fb=np.zeros_like(N)
 yp=(M[:,0]-ZB*Fb)/N;p=np.stack([xp,yp],1)
 E=poly_E(p,sg,o)-dx[:,None]
 if rigid:E[:,2]=YC-yp0-dx+Fcap*ZB/N   # = (Fcap - Fneed) z_b / N beyond the caster line (mobile.dock_stability)
 Nc=N*(yp-YD)/(YC-YD);Nd=N-Nc;Nd1=Nd*(XW-xp)/(2*XW);Nd2=Nd*(XW+xp)/(2*XW);fx=F[:,0];fy=F[:,1]+Fb
 if rigid:
  mu=np.where(Nd>0,np.maximum(np.hypot(fx/np.maximum(Nd,1e-6),fy/N),(np.abs(fy)+extra_f)/N)+extra_f/np.maximum(Nd,1e-6),np.inf)
 else:
  D=(M[:,2]+YD*F[:,0])/XW;fy1=(fy-D)/2;fy2=(fy+D)/2;w1=np.maximum(Nd1,1e-6);w2=np.maximum(Nd2,1e-6);fx1=fx*w1/(w1+w2);fx2=fx-fx1
  mu=np.maximum((np.hypot(fx1,fy1)+extra_f*w1/(w1+w2))/w1,(np.hypot(fx2,fy2)+extra_f*w2/(w1+w2))/w2);mu=np.where((Nd1>0)&(Nd2>0),mu,np.inf)
 return dict(E=E,margin=E.min(1),edge=E.argmin(1),xp=xp,yp=yp,Fb=Fb,Fneed=Fneed,Nd=Nd,mu=mu,N=N,dx=dx)
def sdof(x,t,fn,zeta=.05):
 """Unit-DC-gain SDOF (f_n, zeta) driven by x(t): elastic rocking on the tyres (E). Semi-implicit Euler <= 2 ms."""
 w=2*np.pi*fn;y=np.zeros_like(x);y[0]=x[0];yy=x[0];vv=0.
 for i in range(1,len(x)):
  h=t[i]-t[i-1];n_=max(1,int(math.ceil(h/.002)));dt=h/n_
  for _ in range(n_):vv+=(w*w*(x[i]-yy)-2*zeta*w*vv)*dt;yy+=vv*dt
  y[i]=yy
 return y
# ------------------------------------------------------------------ stops
def edge_rocking(md,q):
 """Rigid rocking about each support edge (trail 0): inertia about the edge (kg m^2), energy to bring the CoG
 over it (J), horizontal CoG-edge distance (m)."""
 m,d=md['m'],md['d'];d.qpos[:]=q;mujoco.mj_forward(m,d);rid=md['rid'];ids=[b for b in range(1,m.nbody) if m.body_rootid[b]==rid]
 Mt=float(m.body_mass[ids].sum());com=d.subtree_com[rid].copy();P=polygon(0.)[0];out=[]
 for e in range(4):
  a=np.r_[P[e]+q[:2],0];b=np.r_[P[(e+1)%4]+q[:2],0];u=(b-a)/np.linalg.norm(b-a);I=0.
  for bb in ids:
   r=d.xipos[bb]-a;r-=(r@u)*u;R=d.ximat[bb].reshape(3,3);I+=m.body_mass[bb]*(r@r)+u@R@np.diag(m.body_inertia[bb])@R.T@u
  r=com-a;r-=(r@u)*u;h=r[2];dh=float(np.hypot(r[0],r[1]));out.append((I,Mt*G*(math.hypot(dh,h)-h),dh))
 return out,Mt
def stop_sim(md,law,i0,o,arm,cart,alpha,h=.002):
 """One stop starting at sample i0. Arm: cat0 (independent joints) / cat12 (path-synchronous) / none (law).
 Cart: law / es05 (0.5 m/s^2) / esmax (traction-limited). Returns the state samples with time weights."""
 q=law['q'][i0].copy();qd=law['qd'][i0].copy();vj=qd[3:9].copy();n=len(law['t'])
 if arm=='cat0':dec=-np.sign(vj)*alpha
 elif arm=='cat12':Tst=float(np.max(np.abs(vj)/alpha));dec=-vj/Tst if Tst>0 else 0*vj
 ac=0.
 if cart=='es05':ac=-np.sign(qd[0])*.5
 elif cart=='esmax':
  F,Mm,zc,zt=wrench(md,q[None],qd[None],law['qa'][i0][None]);sp=support(F,Mm,np.sign(qd[:1]),zc,zt,o)
  ac=-np.sign(qd[0])*max(1e-3,min(o['mu']*max(float(sp['Nd'][0]),0.)/(F[0,2]/G),2*PEAK_T/R_WHEEL/(F[0,2]/G)))
 Qs=[];QDs=[];QAs=[];W=[]
 for k in range(600):
  qa=np.zeros_like(qd);jj=min(i0+k,n-1)
  if arm=='none':q[3:9]=law['q'][jj,3:9];qd[3:9]=law['qd'][jj,3:9];qa[3:9]=law['qa'][jj,3:9]
  else:qa[3:9]=np.where(np.abs(qd[3:9])>1e-12,dec,0.)
  if cart=='law':q[0]=law['q'][jj,0];qd[0]=law['qd'][jj,0];qa[0]=law['qa'][jj,0]
  elif abs(qd[0])>1e-12:qa[0]=ac
  arm_done=arm=='none' or np.all(np.abs(qd[3:9])<=1e-12);cart_done=cart=='law' or abs(qd[0])<=1e-12
  if arm_done and cart!='law' and arm!='none' and not cart_done:   # arm at rest, constant cart deceleration: wrench constant from here
   Qs.append(q.copy());QDs.append(qd.copy());QAs.append(qa.copy());W.append(abs(qd[0]/ac));break
  Qs.append(q.copy());QDs.append(qd.copy());QAs.append(qa.copy());W.append(h)
  if (arm_done and cart_done) or (arm=='none' and cart=='law'):break
  if arm!='none':
   nv=qd[3:9]+qa[3:9]*h;nv=np.where(np.sign(nv)!=np.sign(qd[3:9]),0.,nv);q[3:9]+=(qd[3:9]+nv)/2*h;qd[3:9]=nv
  if cart!='law':
   nv=qd[0]+qa[0]*h;nv=0. if np.sign(nv)!=np.sign(qd[0]) else nv;q[0]+=(qd[0]+nv)/2*h;qd[0]=nv
 return np.array(Qs),np.array(QDs),np.array(QAs),np.array(W)
def stop_eval(md,law,i0,o,arm,cart,alpha,ER):
 Q,QD,QA,W=stop_sim(md,law,i0,o,arm,cart,alpha);F,Mm,zc,zt=wrench(md,Q,QD,QA);sg=np.full(len(Q),law['sg'][i0])
 sp=support(F,Mm,sg,zc,zt,o);(EI,Mt)=ER;N=sp['N']
 J=(np.clip(-sp['E'],0,None)*N[:,None]*W[:,None]).sum(0);KE=np.array([J[e]**2/(2*EI[e][0]) for e in range(4)]);U=np.array([EI[e][1] for e in range(4)])
 lift=max(KE[e]/(Mt*G*max(EI[e][2],1e-3))*(.44 if e in (1,3) else .33) for e in range(4))
 Nres=np.maximum(sp['Nd'],0) if o['casters']=='swivel' else N;fh=np.hypot(F[:,0],F[:,1]+sp['Fb'])
 vs=0.;slip=0.
 for k_ in range(len(W)):vs=max(0.,vs+(fh[k_]-o['mu']*Nres[k_])/Mt*W[k_]);slip+=vs*W[k_]   # slip velocity grows with the excess demand, friction arrests it
 mu=np.where(np.isfinite(sp['mu']),sp['mu'],99.)
 return dict(min_margin_mm=float(sp['margin'].min()*1e3),edge=int(sp['edge'][sp['margin'].argmin()]),energy_ratio=float((KE/np.maximum(U,1e-9)).max()),
  lift_mm=lift*1e3,slip_mm=slip*1e3,max_mu=float(mu.max()),duration_s=float(W.sum()),peak_F_h_N=float(np.hypot(F[:,0],F[:,1]).max()),
  peak_moment_excess_Nm=float((np.clip(-sp['E'],0,None)*N[:,None]).max()))
CASES=[('cat0','law'),('cat12','law'),('cat0','es05'),('cat12','es05'),('cat0','esmax'),('none','es05'),('none','esmax')]
def stops(md,law,o,alpha,step=.01,step_es=.05):
 out={f'{a}+{c}':dict(min_margin_mm=1e9,energy_ratio=0.,lift_mm=0.,slip_mm=0.,max_mu=0.,n=0) for a,c in CASES};k_es=max(1,int(round(step_es/step)))
 idx=[k for k in range(0,len(law['t']),max(1,int(round(step/H)))) if not law['dwell'][k]];last=None
 for j,k in enumerate(idx):
  fv=law['food'][k]
  if fv!=last:set_payload(md,fv,law.get('parts'));last=fv
  ma=np.abs(law['qd'][k,3:9]).max()>1e-6;mc=abs(law['qd'][k,0])>1e-6;ER=None
  for a,c in CASES:
   if c=='law' and not ma:continue
   if c!='law' and (j%k_es or not mc):continue
   ER=ER or edge_rocking(md,law['q'][k]);r=stop_eval(md,law,k,o,a,c,ALPHA[alpha],ER);ok=out[f'{a}+{c}'];ok['n']+=1
   if r['min_margin_mm']<ok['min_margin_mm']:
    ok.update(min_margin_mm=round(r['min_margin_mm'],1),edge=EDGES[r['edge']],at_t=round(float(law['t'][k]),2),cart_v=round(float(law['qd'][k,0]),3),food=float(fv),
     duration_s=round(r['duration_s'],3),peak_F_h_N=round(r['peak_F_h_N'],1),peak_moment_excess_Nm=round(r['peak_moment_excess_Nm'],1))
   for f_ in ('energy_ratio','lift_mm','slip_mm','max_mu'):
    if r[f_]>ok[f_]:ok[f_]=round(r[f_],4);ok[f_+'_at_t']=round(float(law['t'][k]),2)
 return out
# ------------------------------------------------------------------ analysis
SENS=[('mu0.3',dict(mu=.3)),('mu0.2',dict(mu=.2)),('slope0.5deg',dict(slope_deg=.5)),('slope1deg',dict(slope_deg=1.)),('no_tether',dict(tether_N=0.)),
 ('trail0',dict(trail=0.)),('rigid_castors',dict(casters='rigid')),('rigid_castors_mu0.3',dict(casters='rigid',mu=.3)),('rigid_castors_Fb100',dict(casters='rigid',Fb_max=100.))]
def analyse(md,law,o,sens=SENS,sdof_fn=(3.,5.,8.)):
 Q,QD,QA=law['q'],law['qd'],law['qa'];F,M,zc,zt=wrench_law(md,law,Q,QD,QA);sg=law['sg']
 sp=support(F,M,sg,zc,zt,o);i=int(sp['margin'].argmin());mu=np.where(np.isfinite(sp['mu']),sp['mu'],99.);j=int(mu.argmax())
 moving=np.abs(QD[:,0])>1e-4;held=law['food']>0
 res=dict(samples=len(F),weight_N=round(float(np.median(F[:,2])),1),min_margin_mm=round(float(sp['margin'][i]*1e3),1),edge=EDGES[int(sp['edge'][i])],at_t=round(float(law['t'][i]),2),
  at_cart_v=round(float(QD[i,0]),3),at_cart_a=round(float(QA[i,0]),3),at_food=float(law['food'][i]),cop_mm=[round(float(sp['xp'][i]*1e3)),round(float(sp['yp'][i]*1e3))],
  per_edge_min_mm={EDGES[e]:round(float(sp['E'][:,e].min()*1e3),1) for e in range(4)},
  min_margin_cart_moving_mm=round(float(sp['margin'][moving].min()*1e3),1) if moving.any() else None,
  min_margin_food_held_mm=round(float(sp['margin'][held].min()*1e3),1) if held.any() else None,
  max_mu=round(float(mu[j]),3),mu_at_t=round(float(law['t'][j]),2),mu_at_cart_a=round(float(QA[j,0]),3),min_drive_load_N=round(float(sp['Nd'].min()),1),
  max_cart_a=round(float(np.abs(QA[:,0]).max()),3),max_cart_v=round(float(np.abs(QD[:,0]).max()),3),peak_F_h_N=round(float(np.hypot(F[:,0],F[:,1]).max()),1))
 if 'kind' in law:
  res['per_kind_min_margin_mm']={kk:round(float(sp['margin'][law['kind']==kk].min()*1e3),1) for kk in sorted(set(law['kind'].tolist()))}
  res['per_kind_max_mu']={kk:round(float(mu[law['kind']==kk].max()),3) for kk in sorted(set(law['kind'].tolist()))}
  res['per_kind_peak_qa_degps2']={kk:round(float(np.degrees(np.abs(QA[law['kind']==kk,3:9]).max()))) for kk in sorted(set(law['kind'].tolist()))}
 Fs,Ms,_,_=wrench_law(md,law,Q,0*QD,0*QA);ss=support(Fs,Ms,sg,zc,zt,o);res['static_min_margin_mm']=round(float(ss['margin'].min()*1e3),1)
 Qa=QA.copy();Qa[:,0]=0;F0,M0,_,_=wrench_law(md,law,Q,QD,Qa);s0=support(F0,M0,sg,zc,zt,o)
 lat=np.minimum(s0['E'][:,1],s0['E'][:,3]);res['no_cart_accel_min_margin_mm']=round(float(s0['margin'].min()*1e3),1)
 res['cart_a_headroom_min']=round(float(np.min(lat*G/zc)),3)   # |a_cart| that would use up the lateral margin at the worst instant
 for fn in sdof_fn:
  E=poly_E(np.stack([sdof(sp['xp'],law['t'],fn),sdof(sp['yp'],law['t'],fn)],1),sg,o)-sp['dx'][:,None]   # floor edges only (no bumper)
  res[f'sdof_{fn:g}Hz_min_margin_mm']=round(float(E.min()*1e3),1)
 for nm,oo in sens:
  s2=support(F,M,sg,zc,zt,{**o,**oo});m2=np.where(np.isfinite(s2['mu']),s2['mu'],99.)
  res['sens_'+nm]=dict(min_margin_mm=round(float(s2['margin'].min()*1e3),1),edge=EDGES[int(s2['edge'][s2['margin'].argmin()])],max_mu=round(float(m2.max()),3),max_bumper_N=round(float(s2['Fneed'].max()),1))
 return res
def get_law(ctx,act,pro,lim=None):
 law=stir_law(float(pro[1:])) if act=='stir' else laws(ctx,act,pro,lim);law['sg']=caster_sign(law['qd'][:,0]);return law
V={'bom':('bom',{}),'sim':('sim',{}),'bom_al':('bom',dict(mast='al')),'bom_m30':('bom',dict(chassis_scale=.7)),'bom_p30':('bom',dict(chassis_scale=1.3))}
def main():
 act=KV.get('ACT','wok');pros=[p for p in KV.get('PRO','same,fast,fastcart').split(',') if p and p!='none'];var=KV.get('VAR','bom,sim').split(',')
 do_stops=KV.get('STOPS','1')=='1';t00=time.monotonic();ctx=S.setup('spatula' if act=='stir' else act)
 if act=='stir':pros=['k'+x for x in KV.get('STIRK','1').split(',')]   # work-part time scale: k1 = the bench timing
 o=dict(BASE);o.update({k:float(v) for k,v in KV.items() if k in ('mu','Fb_max','trail','slope_deg','tether_N','proc_N')})
 if 'casters' in KV:o['casters']=KV['casters']
 sens=SENS+([('proc6N',dict(proc_N=6.)),('proc25N',dict(proc_N=25.))] if act=='stir' else [])
 out=dict(act=act,base=o,alpha={k:v.round(2).tolist() for k,v in ALPHA.items()},profiles={})
 mds={v:make_model(ctx,*V[v][:1],**V[v][1]) for v in set(var+(['bom_al','bom_m30','bom_p30'] if 'bom' in var else []))}
 for pro in pros:
  law=get_law(ctx,act,pro);P=out['profiles'][pro]=dict(motion_s=round(law['motion_s'],2),limits=law.get('limits'),meta=law.get('meta'),rows={})
  for v in mds:
   r=analyse(mds[v],law,o,sens if v in ('bom','sim') else (),(3.,5.,8.) if v=='bom' else ());r['model']=mds[v]['info'];P['rows'][v]=r
   print(act,pro,v,json.dumps({k:x for k,x in r.items() if k not in ('model','per_edge_min_mm') and not k.startswith('sens_')}),flush=True)
  if do_stops:
   for al in (['max','66'] if KV.get('ALPHA66','1')=='1' else ['max']):
    st=stops(mds['bom'],law,o,al);P['rows']['bom']['stops_alpha_'+al]=st
    for k,x in st.items():print('  stop',pro,al,k,json.dumps(x),flush=True)
 if act!='stir' and KV.get('ASWEEP'):
  sw=[]
  for a in [float(x) for x in KV['ASWEEP'].split(',')]:
   law=get_law(ctx,act,'fast',dict(a_cart=a,j_cart=a/.1));r=analyse(mds['bom'],law,o,[('rigid_castors',dict(casters='rigid')),('slope0.5deg',dict(slope_deg=.5)),('mu0.3',dict(mu=.3))],(5.,))
   sw.append(dict(a_cart=a,j_cart=round(a/.1,2),motion_s=round(law['motion_s'],2),**{k:r[k] for k in ('min_margin_mm','edge','at_t','max_mu','mu_at_t','max_cart_a','min_margin_cart_moving_mm','sdof_5Hz_min_margin_mm','no_cart_accel_min_margin_mm')},
    rigid_castors=r['sens_rigid_castors'],slope05=r['sens_slope0.5deg'],mu03=r['sens_mu0.3']))
   print(act,'sweep',json.dumps(sw[-1]),flush=True)
  out['a_sweep']=sw
 os.makedirs(OUT,exist_ok=True);out['elapsed_s']=round(time.monotonic()-t00)
 fn=f'{OUT}/dyn_{act}'+KV.get('TAG','')+'.json';json.dump(out,open(fn,'w'),indent=1,default=float);print('saved',fn,out['elapsed_s'],'s')
if __name__=='__main__':main()
