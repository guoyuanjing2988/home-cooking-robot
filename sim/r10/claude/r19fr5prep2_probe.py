"""R19 #2 / #38 (R19_FR5_PREP3.md): screen PICK-side variants of the FR5 tomato set against the folded T2L cradle with the
pan aboard (kitchen19p5 swing, as r19prep5_screen.py MODE=fold P5_kind=swing PAN=1). New file; a SCREEN, not a check.
Per variant (r19fr5prep2_actions.py options on top of the adopted tomato options), in its own process:
 1. the pick anchor's start candidates (r19prepchain.candidates: the same 96-start solver, seeds and UR5e seeds);
 2. for each of the first NC distinct ones: r19prepchain.follow() pick -> first lane meet (same steps / IK / checker),
    the grasp approach r19prepchain.approach() (50 mm, empty gripper, the tomato on its pad), and the meet join
    r19prepchain.meet_join() to the TAP-side lane state of the adopted chain (REF play state JOINQ; a stand-in for the
    tap side, which this pick change does not touch);
 3. the folded-cradle gates of the pick anchor + follow states (play scene) and of the approach states (approach scene),
    with r19prep5_screen.Meas (the checker's required gap: 10 mm arm / held vs a cart part) in r19prep5_screen.prep_scene
    of REF (the tomato is a vertical cylinder, so its scene does not depend on the grasp's turn about the vertical).
    States as stored (<= 1 cm TCP steps), not cut to 4 mm: a screen.
python r19fr5prep2_probe.py VARS=<file> [NC=6] [NPROC=12] [TLIM=270] TAG=.. [base options]
 VARS: one variant per line '<name> KEY=VALUE ..'
 -> results/r19/fr5y/probe_<TAG>.json"""
import sys,os,json,time,shlex
sys.path.insert(0,'.')
import numpy as np
KV0=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
REF=KV0.get('REF','results/r19/prep/chain_tomato_fr5xfull_fr5_j6_pgc_sp20.json');JOINQ=int(KV0.get("JOINQ",79))
BASE=dict(ACT='tomato',ARM='fr5_j6_pgc_sp20',SEEDS='2',SEEDUR='results/r19/prep/chain_tomato_r2_ur5e_enc2_pgc.json',XL1='-0.65,.06,1.10',XL1R='level',LVC='-0.25',L2C='-0.25')
def load_ns(kv):
 import r19fr5prep2_actions as XB
 s=XB.source();cut=s.index('t0=time.monotonic();pieces={}')
 a0=list(sys.argv);sys.argv=[sys.argv[0]]+[f'{k}={v}' for k,v in kv.items()]
 try:g={'__name__':'r19fr5prep2_probe_ns','__file__':os.path.abspath('r19prepchain.py')};exec(compile(s[:cut],'r19prepchain.py','exec'),g)
 finally:sys.argv=a0
 return g
def fold_meas():
 a0=list(sys.argv);sys.argv=[sys.argv[0],'MODE=fold','P5_kind=swing','PAN=1','ARM=fr5_j6_pgc_sp20','PY=.15']
 try:
  import r19prep5_screen as S5
 finally:sys.argv=a0
 S5.S4.potzone();R=json.load(open(REF))
 chP,preP=S5.prep_scene(R,'play');chA,preA=S5.prep_scene(R,0)
 return S5.Meas(chP,preP),S5.Meas(chA,preA)
def gates(me,Q):
 out=[];
 for q in Q:b,v=me(np.asarray(q,float),want_depth=False);out.append((b[0],b[1],len(v)>0))
 g=min(out,key=lambda t:t[0]) if out else (None,None,False)
 return dict(min_gate_mm=None if g[0] is None else round(g[0]*1e3,1),pair=g[1],hit_states=sum(t[2] for t in out),states=len(out))
def job(arg):
 name,kv=arg;t0=time.monotonic()
 try:
  os.environ['ARM']=kv['ARM'];g=load_ns(kv);KF=g['KF'];a=0;x=g['sides'](0)[0]
  cs,stat=g['candidates'](a);keep=[]
  for i,c_ in enumerate(cs):
   if len(keep)>=int(KV0.get('NC',6)):break
   if not any(np.max(abs(np.array(c_['q'])-np.array(cs[j]['q'])))<1e-3 for j in keep):keep.append(i)
  R=json.load(open(REF));qtap=np.array(R['play'][JOINQ],float);rows=[]
  for i in keep:
   q=np.array(cs[i]['q'],float);out,f=g['follow'](a,x,q);qd=np.degrees(q[3:9])
   row=dict(cand=i,cart=round(float(q[0]),3),q_deg=np.round(qd,1).tolist(),branch=f"J1 {qd[0]:.0f} E{'+' if qd[2]>0 else '-'} W{'+' if qd[4]>0 else '-'}",start_reserve_mm=round(float(cs[i]['reserve_mm']),1),
    follow_ok=f is None,follow_fail=None if f is None else {k:(float(v) if isinstance(v,(np.floating,np.integer)) else v) for k,v in f.items() if k in ('at','cart','step_deg','pose_mm','hits')},
    lane_cart=out[-1]['cart'] if out else None,follow_min_reserve_mm=min([o['reserve_mm'] for o in out if o['reserve_mm'] is not None],default=None),max_step_deg=max([o['step_deg'] for o in out],default=None),
    follow_s=round(sum(o['dt'] for o in out),1))
   ap=g['approach'](a,g['GR'][0][1],True,q);row.update(app_ok=ap['ok'],app_min_reserve_mm=ap.get('min_reserve_mm'),app_food_gap_mm=ap.get('min_food_gap_mm'),app_fail=None if ap['ok'] else dict(stop=ap.get('stop'),hits=ap.get('hits')))
   if f is None:
    j=g['meet_join'](np.array(out[-1]['q']),qtap,x);row.update(join_ok=j['ok'],join_deg=j.get('arm_deg'),join_cart_m=j.get('cart_m'),join_s=j.get('s'),join_why=None if j['ok'] else str(j.get('why') or j.get('hits') or j.get('reason'))[:300])
    row['_qs']=dict(play=[q.tolist()]+[o['q'] for o in out]+(j.get('qs') or []),app=ap.get('qs') or [])
   else:row['_qs']=dict(play=[q.tolist()]+[o['q'] for o in out],app=ap.get('qs') or [])
   rows.append(row)
  meP,meA=fold_meas()
  for row in rows:
   qs=row.pop('_qs');row['fold_play']=gates(meP,qs['play']);row['fold_app']=gates(meA,qs['app'])
   row['clean']=bool(row['follow_ok'] and row['app_ok'] and row.get('join_ok') and row['fold_play']['hit_states']==0 and row['fold_app']['hit_states']==0)
  return dict(name=name,kv=kv,n_cands=len(cs),stat=stat,tried=len(rows),clean=sum(r['clean'] for r in rows),rows=rows,keyframes=[dict(label=k['label'],p=np.round(k['p'],4).tolist(),c=k['c']) for k in KF[:x+1]],elapsed_s=round(time.monotonic()-t0))
 except Exception:
  import traceback;return dict(name=name,kv=kv,error=traceback.format_exc()[-1500:])
if __name__=='__main__':
 import multiprocessing as mp
 base={**BASE,**{k:v for k,v in KV0.items() if k not in ('VARS','NC','NPROC','TAG','TLIM','REF','JOINQ')}};V=[]
 for ln in open(KV0['VARS'],encoding='utf-8'):
  ln=ln.split('#')[0].strip()
  if ln:p=shlex.split(ln);V.append((p[0],{**base,**dict(x_.split('=',1) for x_ in p[1:])}))
 t0=time.monotonic();print('variants',len(V),flush=True)
 with mp.Pool(min(int(KV0.get('NPROC',12)),len(V)),maxtasksperchild=1) as pool:
  try:res=pool.map_async(job,V,chunksize=1).get(timeout=float(KV0.get('TLIM',270)))
  except mp.TimeoutError:pool.terminate();print('TIME LIMIT: no result written',flush=True);sys.exit(1)
 for r in res:
  if 'error' in r:print(r['name'],'ERROR',r['error'][-600:],flush=True);continue
  print(f"{r['name']:12s} clean {r['clean']}/{r['tried']} of {r['n_cands']} ({r['elapsed_s']} s)",flush=True)
  for w in r['rows']:
   print(f"   c{w['cand']:<2d} cart {w['cart']:+.3f} {w['branch']:14s} follow {'ok' if w['follow_ok'] else w['follow_fail']} lane {w['lane_cart']} app {'ok' if w['app_ok'] else w['app_fail']} "
         f"join {w.get('join_ok')} {w.get('join_deg')} | fold play {w['fold_play']['min_gate_mm']} ({w['fold_play']['hit_states']}) app {w['fold_app']['min_gate_mm']} ({w['fold_app']['hit_states']}) {w['fold_app']['pair']}",flush=True)
 os.makedirs('results/r19/fr5y',exist_ok=True);fo=f"results/r19/fr5y/probe_{KV0.get('TAG','x')}.json"
 json.dump(dict(base=base,ref=REF,joinq=JOINQ,method=__doc__,variants=res,elapsed_s=round(time.monotonic()-t0)),open(fo,'w'),default=float,indent=1);print(fo,round(time.monotonic()-t0),'s')
