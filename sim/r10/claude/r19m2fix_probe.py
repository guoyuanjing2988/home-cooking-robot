"""R19 #42 m2 prep fixes (R19_M2FIX.md): fast per-anchor diagnostics of a prep set. New file; nothing shared is edited.
The planner's source (r19fr5prep_actions.source() = r19prepchain.py + SEEDUR + X.. overrides, or r19prep5_chain.py) is
executed only up to its anchors loop, so the keyframes, the checker, candidates() and follow() are the planner's own.
Then, for each anchor whose label contains ANCHOR: the 96-start IK status counts, the most frequent hit pairs of the
'collision' starts, and for the first TRIES candidates the follow to each side (ok, or the first failing state).
python r19m2fix_probe.py RUNNER=r19fr5prep_actions.py|r19prep5_chain.py|r19m2fix_ct2s.py ANCHOR=<label substring> [TRIES=4] <runner argv>"""
import sys,os,collections
sys.path.insert(0,'.')
KV0=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
RUNNER=KV0['RUNNER'];ANCHOR=KV0['ANCHOR'];NT=int(KV0.get('TRIES',4))
sys.argv=[RUNNER]+[a for a in sys.argv[1:] if not a.startswith(('RUNNER=','ANCHOR=','GEOM='))]
if '\ndef source(' in open(RUNNER,encoding='utf-8').read():src=__import__(RUNNER[:-3]).source()   # wrappers (r19fr5prep_actions, r19m2fix_ct2s)
else:src=open(RUNNER,encoding='utf-8').read()
MARK="t0=time.monotonic();pieces={};anchors={};log=[];good={}"
assert src.count(MARK)==1,'anchors loop marker not unique'
ns={'__name__':'__probe__','__file__':os.path.abspath(RUNNER)}
exec(compile(src[:src.index(MARK)],os.path.abspath(RUNNER),'exec'),ns)
_solve=ns['solve'];HITS=collections.Counter()
def solve(*a,**k):
 r=_solve(*a,**k)
 for row in r['rows']:
  if row['status']=='collision':
   for h in row['check']['hits'][:2]:HITS[tuple(sorted(h['pair']))]+=1
 return r
ns['solve']=solve
KF=ns['KF']
for a in [i for i,k in enumerate(KF) if k['anchor'] and ANCHOR in k['label']]:
 HITS.clear();cs,stat=ns['candidates'](a);import numpy as np
 cs=[c for i,c in enumerate(cs) if not any(np.max(abs(np.array(c['q'])-np.array(o['q'])))<1e-3 for o in cs[:i])]   # distinct IK states only
 print(f"{KF[a]['label']}#{a} c={KF[a]['c']} candidates {len(cs)} {stat}",flush=True)
 for p,n in HITS.most_common(6):print('   collision',n,p)
 if KV0.get('GEOM') and cs:   # where the arm base, the flange and the TCP are at the best candidate (world, m)
  import mujoco;ch=ns['ch'];ch.d.qpos[:]=cs[0]['q'];mujoco.mj_kinematics(ch.m,ch.d)
  for nm in [ch.m.body(b).name for b in range(ch.m.nbody) if any(s in ch.m.body(b).name for s in ('base_link','shoulder','wrist_3','R_tool'))]:print('   body',nm,ch.d.xpos[ch.m.body(nm).id].round(3))
  print('   R_prep site',ch.d.site_xpos[ch.m.site('R_prep').id].round(3),'q',[round(v,2) for v in cs[0]['q'][3:9]])
 for i,c in enumerate(cs[:NT]):
  msg=[]
  for b in ns['sides'](a):
   out,f=ns['follow'](a,b,c['q'])
   msg.append(f"->{KF[b]['label']}#{b}: "+('ok' if f is None else str({k:f[k] for k in ('at','step_deg','pose_mm','reserve_mm','hits') if k in f})))
  print(f" cand {i} cart {c['q'][0]:.3f} reserve {c['reserve_mm']:.1f} | "+' | '.join(msg),flush=True)
