"""R19 #2 (FR5) prep sets, round 2: screen keyframe variants (r19fr5prep_actions.py overrides) at one anchor. New file.
A screen, not a check: for each variant, the anchor's start candidates (r19prepchain.candidates, the same 96-start
solver and SEEDUR seeds) are followed to the anchor's meets with r19prepchain.follow() itself (same steps, IK, cart rule
and checker; it stops at the first hit, a TCP error > 5 mm / 3 deg or a joint step > 10 deg). Per variant: how many starts
reach every meet of the anchor, and where / on which pair the others stop. Whole sets are then planned and certified
with r19fr5prep_actions.py + r19prep_verify.py.
Phase 1 (parallel over variants): the start candidates, cached on disk by anchor pose and cart rule (variants with the
same anchor share them). Phase 2 (parallel over variants x CHUNK starts): the follows.
python r19fr5prep_explore.py ACT=<set> ARM=fr5_j6_pgc_sp20 "ANCHOR=under the tap" VARS=<file> [NC=24 distinct starts] [NPROC=8] [CHUNK=4] [SEEDS=2]
   [SEEDUR=..] [TAG=..] [base options]
 VARS file: one variant per line, '<name> KEY=VALUE ..' (the variant's options are added to the base options); '#' comments
 -> results/r19/fr5x/explore_<ACT>_<TAG>_<arm>.json"""
import sys,os,json,time,pickle,hashlib,shlex
sys.path.insert(0,'.')
import numpy as np
KV0=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
def load_ns(kv):
 """r19prepchain (with the SEEDUR opt-in and the keyframe override) executed up to its planning loop with options kv."""
 import r19fr5prep_actions as XA
 s=XA.source();cut=s.index('t0=time.monotonic();pieces={}')
 a0=list(sys.argv);sys.argv=[sys.argv[0]]+[f'{k}={v}' for k,v in kv.items()]   # r19prepchain reads its options from argv
 try:g={'__name__':'r19fr5prep_explore_ns','__file__':os.path.abspath('r19prepchain.py')};exec(compile(s[:cut],'r19prepchain.py','exec'),g)
 finally:sys.argv=a0   # (the arm, read again by later model builds, is the same in both)
 return g
def akey(g,a):
 k=g['KF'][a];return hashlib.md5(json.dumps([np.round(k['p'],5).tolist(),np.round(k['R'],5).tolist(),k['c'],g['ARM'],KV0.get('SEEDS'),KV0.get('SEEDUR')]).encode()).hexdigest()[:12]
def anchor_of(g):return [i for i in g['A'] if KV0['ANCHOR'] in g['KF'][i]['label']][0]
def ns_with_cands(kv):
 """the namespace for options kv, its anchor, and the anchor's start candidates (cached on disk by anchor pose and cart rule)."""
 g=load_ns(kv);a=anchor_of(g);KF=g['KF'];fn=f"results/r19/fr5x/cands_{akey(g,a)}.pkl"
 key=(tuple(np.round(KF[a]['p'],4)),tuple(np.round(KF[a]['R'].ravel(),4)))
 if os.path.exists(fn):g['_cands'][key]=pickle.load(open(fn,'rb'))
 cs,stat=g['candidates'](a)
 if not os.path.exists(fn):pickle.dump((cs,stat),open(fn,'wb'))
 return g,a,cs,stat
def prep(job):
 """phase 1: the variant's start candidates; the indices of the first NC distinct ones."""
 name,kv=job
 try:
  g,a,cs,stat=ns_with_cands(kv);keep=[]
  for i,c_ in enumerate(cs):
   if len(keep)>=int(KV0.get('NC',24)):break
   if not any(np.max(abs(np.array(c_['q'])-np.array(cs[j]['q'])))<1e-3 for j in keep):keep.append(i)
  return dict(name=name,n=len(cs),stat=stat,keep=keep)
 except Exception:
  import traceback;return dict(name=name,error=traceback.format_exc()[-1500:])
def follow_job(job):
 """phase 2: follow the start candidates idx of a variant to the anchor's meets with r19prepchain.follow()."""
 name,kv,idx=job
 try:
  g,a,cs,stat=ns_with_cands(kv);KF=g['KF'];rows=[]
  for i in idx:
   c_=cs[i];sides={}
   for b in g['sides'](a):
    out,f=g['follow'](a,b,c_['q'])
    sides[KF[b]['label']+f'#{b}']=dict(ok=f is None,steps=len(out),min_reserve_mm=min([o['reserve_mm'] for o in out if o['reserve_mm'] is not None],default=None),
     max_step_deg=max([o['step_deg'] for o in out],default=None),end_cart=out[-1]['cart'] if out else None,
     fail=None if f is None else {k:(v if not isinstance(v,(np.floating,np.integer)) else float(v)) for k,v in f.items() if k in ('at','cart','step_deg','pose_mm','reserve_mm','hits')},q_end=out[-1]['q'] if (out and f is None) else None)
   qd=np.degrees(np.array(c_['q'],float)[3:9])   # branch: elbow (J3) and wrist (J5) signs, J1
   rows.append(dict(cand=i,cart=round(float(c_['q'][0]),3),q_deg=np.round(qd,1).tolist(),branch=f"J1 {qd[0]:.0f} E{'+' if qd[2]>0 else '-'} W{'+' if qd[4]>0 else '-'}",start_reserve_mm=round(float(c_['reserve_mm']),1),ok=all(s['ok'] for s in sides.values()),sides=sides))
  return dict(name=name,rows=rows,keyframes=[dict(i=i,label=k['label'],p=np.round(k['p'],4).tolist(),c=k['c'],meet=k['meet'],anchor=k['anchor']) for i,k in enumerate(KF)],anchor=KF[a]['label'])
 except Exception:
  import traceback;return dict(name=name,error=traceback.format_exc()[-1500:])
def summary(name,kv,P,parts):
 rows=sorted([r for p in parts for r in p['rows']],key=lambda r:r['cand']);per={}
 for r in rows:
  for s,v in r['sides'].items():
   o=per.setdefault(s,dict(ok=0,fails={}))
   if v['ok']:o['ok']+=1
   else:k_=v['fail']['at']+' | '+(' / '.join(sorted(v['fail']['hits'][0])) if v['fail']['hits'] else ('step %.1f deg'%v['fail']['step_deg'] if v['fail']['step_deg']>10 else 'pose'));o['fails'][k_]=o['fails'].get(k_,0)+1
 return dict(name=name,kv=kv,anchor=parts[0]['anchor'] if parts else None,keyframes=parts[0]['keyframes'] if parts else None,n_cands=P['n'],start_status=P['stat'],tried=len(rows),clean=sum(r['ok'] for r in rows),per_side=per,rows=rows)
if __name__=='__main__':
 import multiprocessing as mp
 os.makedirs('results/r19/fr5x',exist_ok=True);t0=time.monotonic()
 base={k:v for k,v in KV0.items() if k not in ('VARS','NC','NPROC','ANCHOR','TAG','CHUNK')}
 V=[]
 for ln in open(KV0['VARS'],encoding='utf-8'):
  ln=ln.split('#')[0].strip()
  if ln:p=shlex.split(ln);V.append((p[0],{**base,**dict(x.split('=',1) for x in p[1:])}))
 g,a,cs,stat=ns_with_cands(base);print('base candidates',len(cs),stat,round(time.monotonic()-t0),'s',flush=True)   # once, shared by the variants with the same anchor
 CH=int(KV0.get('CHUNK',4))
 with mp.Pool(int(KV0.get('NPROC',8))) as pool:
  P=pool.map(prep,V,chunksize=1);print('candidates',[(p['name'],p.get('n'),len(p.get('keep',[]))) for p in P],round(time.monotonic()-t0),'s',flush=True)
  jobs=[(n,kv,p['keep'][i:i+CH]) for (n,kv),p in zip(V,P) if 'keep' in p for i in range(0,len(p['keep']),CH)]
  F=pool.map(follow_job,jobs,chunksize=1)
 res=[]
 for (n,kv),p in zip(V,P):
  if 'error' in p:res.append(dict(name=n,kv=kv,error=p['error']));continue
  parts=[f for f in F if f['name']==n]
  if any('error' in f for f in parts):res.append(dict(name=n,kv=kv,error=[f['error'] for f in parts if 'error' in f][0]));continue
  res.append(dict(summary(n,kv,p,parts),elapsed_s=round(time.monotonic()-t0)))
 for r in res:
  if 'error' in r:print(r['name'],'ERROR',r['error'][-400:],flush=True);continue
  print(f"{r['name']:14s} clean {r['clean']}/{r['tried']} of {r['n_cands']}",{s:(v['ok'],sorted(v['fails'].items(),key=lambda x:-x[1])[:2]) for s,v in r['per_side'].items()},f"{r['elapsed_s']} s",flush=True)
  print('   starts (cart, branch, clean, end carts):',sorted({(x['cart'],x['branch'],x['ok'],tuple(s['end_cart'] for s in x['sides'].values())) for x in r['rows']},key=lambda t:(not t[2],t[0])),flush=True)
 out=dict(act=KV0['ACT'],arm=g['ARM'],anchor=KV0['ANCHOR'],base=base,method=__doc__,variants=res,elapsed_s=round(time.monotonic()-t0))
 import arms;fo=f"results/r19/fr5x/explore_{KV0['ACT']}_{KV0.get('TAG','x')}{arms.tag(g['ARM'])}.json";json.dump(out,open(fo,'w'),default=float);print(fo,out['elapsed_s'],'s')
