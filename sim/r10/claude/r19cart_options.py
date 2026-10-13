"""R19 cart (issue #14): design options, cart-jerk sweep and the friction mechanism, with r19cart_dyn's model.

Options (each evaluated on the same time laws; BOM mass model, base assumptions of r19cart_dyn.BASE):
 rigid (fixed) castors; low steel ballast 10 / 20 kg; track +50 mm per side; rigid castors + 10 kg; aluminium
 mast. Reported: rigid-body minimum tip margin, max per-wheel friction demand, elastic-rocking (5 Hz, E) margin.
Jerk sweep: wok, 'fast' caps, cart a = 0.3 / 0.5 m/s^2 with ramp times a/j = 0.4 / 0.2 / 0.1 s; the rigid
 model does not depend on jerk, the elastic rocking estimate does (f_n 3 / 5 / 8 Hz, zeta 0.05, E).
Friction mechanism: decomposition of the worst per-wheel demand of wok/fastcart.
python r19cart_options.py PART=opt CASES=wok:fastcart,wok:fast   -> results/r19/cart/options_opt_<tag>.json
python r19cart_options.py PART=jerk                              -> results/r19/cart/options_jerk.json (+ friction)
(each part < 5 min)"""
import sys,os,json,time,math;sys.path.insert(0,'.')
import numpy as np
import r19smooth as S
import r19cart_dyn as D
OPTS=[('baseline: BOM, swivel casters',{},{},None),('rigid castors',{},dict(casters='rigid'),None),('ballast 10 kg (chassis floor)',dict(ballast_kg=10.),{},None),
 ('ballast 20 kg (chassis floor)',dict(ballast_kg=20.),{},None),('track +50 mm per side',{},{},.27),('rigid castors + ballast 10 kg',dict(ballast_kg=10.),dict(casters='rigid'),None),
 ('aluminium mast',dict(mast='al'),{},None)]
CASES=[('wok','fastcart'),('wok','fast'),('spider','fastcart'),('stir','k1')]
KV=dict(a.split('=',1) for a in sys.argv[1:]) if __name__=='__main__' else {}
def main():
 t00=time.monotonic();out=dict(options=[],jerk=[],friction={});ctxs={};part=KV.get('PART','opt')
 cases=[tuple(c.split(':')) for c in KV['CASES'].split(',')] if 'CASES' in KV else CASES
 for act,pro in (cases if part=='opt' else []):
  ctx=ctxs.setdefault(act,S.setup('spatula' if act=='stir' else act));law=D.get_law(ctx,act,pro)
  for name,mk,oo,xw in OPTS:
   D.XW=xw or .22
   try:
    md=D.make_model(ctx,'bom',**mk);o={**D.BASE,**oo};r=D.analyse(md,law,o,[('slope0.5deg',dict(slope_deg=.5))],(5.,))
   finally:D.XW=.22
   row=dict(act=act,profile=pro,option=name,min_margin_mm=r['min_margin_mm'],edge=r['edge'],max_mu=r['max_mu'],sdof5_mm=r['sdof_5Hz_min_margin_mm'],
    slope05_mm=r['sens_slope0.5deg']['min_margin_mm'],weight_N=r['weight_N'],cart_kg=round(md['info'].get('cart_kg',0),2))
   out['options'].append(row);print(json.dumps(row),flush=True)
 if part=='opt':
  tag='_'.join(f'{a}{p}' for a,p in cases);fn=f'{D.OUT}/options_opt_{tag}.json';json.dump(out,open(fn,'w'),indent=1,default=float);print('saved',fn,round(time.monotonic()-t00),'s');return
 ctx=ctxs.setdefault('wok',S.setup('wok'))
 for a in (.3,.5):
  for tr in (.4,.2,.1):
   law=D.get_law(ctx,'wok','fast',dict(a_cart=a,j_cart=a/tr));md=D.make_model(ctx,'bom');r=D.analyse(md,law,dict(D.BASE),(),(3.,5.,8.))
   ok=np.r_[True,np.diff(law['t'])>1e-9];jk=np.abs(np.diff(law['qa'][ok,0])/np.diff(law['t'][ok]))   # piece joins share a time stamp
   row=dict(a_cart=a,j_cart=round(a/tr,2),ramp_s=tr,motion_s=round(law['motion_s'],2),rigid_mm=r['min_margin_mm'],max_mu=r['max_mu'],
    sdof3_mm=r['sdof_3Hz_min_margin_mm'],sdof5_mm=r['sdof_5Hz_min_margin_mm'],sdof8_mm=r['sdof_8Hz_min_margin_mm'],peak_cart_jerk_fd=round(float(np.percentile(jk,99.9)),2))
   out['jerk'].append(row);print(json.dumps(row),flush=True)
 # friction mechanism at the worst per-wheel demand (wok, fastcart)
 law=D.get_law(ctx,'wok','fastcart');md=D.make_model(ctx,'bom');F,M,zc,zt=D.wrench_law(md,law,law['q'],law['qd'],law['qa'])
 sp=D.support(F,M,law['sg'],zc,zt,dict(D.BASE));mu=np.where(np.isfinite(sp['mu']),sp['mu'],99.);i=int(mu.argmax())
 N=F[i,2];xp=sp['xp'][i];yp=sp['yp'][i];Nd=sp['Nd'][i];Nd1=Nd*(D.XW-xp)/(2*D.XW);Nd2=Nd*(D.XW+xp)/(2*D.XW);Dy=(M[i,2]+D.YD*F[i,0])/D.XW
 sp0=D.support(F[i:i+1],M[i:i+1],law['sg'][i:i+1],zc[i:i+1],zt[i:i+1],{**D.BASE,'tether_N':0.})
 Qa=law['qa'][i:i+1].copy();Qa[:,0]=0;set_=D.set_payload(md,law['food'][i]);F0,M0,_,_=D.wrench(md,law['q'][i:i+1],law['qd'][i:i+1],Qa);s00=D.support(F0,M0,law['sg'][i:i+1],zc[i:i+1],zt[i:i+1],{**D.BASE,'tether_N':0.})
 out['friction']=dict(t=round(float(law['t'][i]),2),cart_a=round(float(law['qa'][i,0]),3),cart_v=round(float(law['qd'][i,0]),3),food=float(law['food'][i]),
  F_N=F[i].round(1).tolist(),M_floor_Nm=M[i].round(1).tolist(),N_N=round(float(N),1),cop_mm=[round(float(xp*1e3)),round(float(yp*1e3))],drive_load_N=round(float(Nd),1),
  wheel_loads_N=[round(float(Nd1),1),round(float(Nd2),1)],yaw_side_force_diff_N=round(float(Dy),1),mu=round(float(mu[i]),3),mu_no_tether=round(float(sp0['mu'][0]),3),
  mu_no_tether_no_cart_accel=round(float(s00['mu'][0]),3))
 print(json.dumps(out['friction']))
 os.makedirs(D.OUT,exist_ok=True);out['elapsed_s']=round(time.monotonic()-t00);json.dump(out,open(f'{D.OUT}/options_jerk.json','w'),indent=1,default=float);print('saved',out['elapsed_s'],'s')
if __name__=='__main__':main()
