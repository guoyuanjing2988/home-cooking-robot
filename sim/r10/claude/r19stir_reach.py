"""R19 #3: the R15 stroke-start reach probes (r15reach.py stir, unchanged) for an arm option, written to
results/r19/stir/reach/ instead of results/r15 (results/r15 is never written).
KEEP=<n> (default 8 = unchanged): solver.solve keeps the best <n> collision-free candidates per solve instead of 8
(it keeps them by clearance reserve, before r15reach's plume post-check, so with 8 a probe can lose every
plume-clear candidate). Search breadth only: every kept candidate passed the same checks; solver.py is not edited
(the patched copy of solve() lives only in this process).

The five probes (keyframes I = 0, 16, 32, 48, 64 = the starts of the 5 strokes) run in parallel, each in its own
process, with the options of the R18/R19 lanes: CARTX=.55 (the R15 parking spot), GRIP=.45, TAG=r19.
python r19stir_reach.py ARM=<arm> [I=0,16,32,48,64] [KEEP=8]
 -> results/r19/stir/reach/reach_stir_h_scrape_dice_i<III>_g0.45_cx.55_r19[_k<KEEP>]_<arm>.json"""
import sys,os,runpy,subprocess,time,json
KEYS='results/r15/stir_h_scrape_dice_keys.json';OUT='results/r19/stir/reach'
def one(args):
 """run r15reach.py with scene.save redirected from results/r15/ to OUT"""
 import scene,solver
 keep=[a for a in args if a.startswith('KEEP=')]
 if keep:
  n=int(keep[0][5:]);args=[a for a in args if not a.startswith('KEEP=')]
  if n!=8:
   src=open('solver.py',encoding='utf-8').read();assert src.count('candidates=order[:8]')==1
   exec(compile(src.replace('candidates=order[:8]','candidates=order[:%d]'%n),'solver.py','exec'),solver.__dict__)
 orig=scene.save
 def save(name,value):
  assert name.startswith('results/r15/reach_'),name
  return orig(OUT+'/'+name[len('results/r15/'):],value)
 scene.save=save;sys.argv=['r15reach.py']+args;runpy.run_path('r15reach.py',run_name='__main__')
if __name__=='__main__':
 if sys.argv[1:2]==['one']:one(sys.argv[2:]);sys.exit()
 KV=dict(a.split('=',1) for a in sys.argv[1:]);arm=KV['ARM'];os.makedirs(OUT,exist_ok=True);t0=time.monotonic()
 ps=[]
 for i in KV.get('I','0,16,32,48,64').split(','):
  kp=int(KV.get('KEEP',8))
  cmd=[sys.executable,'r19stir_reach.py','one','stir','KEYS='+KEYS,'I='+i,'CARTX=.55','GRIP=.45','TAG=r19'+('' if kp==8 else '_k%d'%kp),'ARM='+arm,'KEEP=%d'%kp]
  ps.append((i,subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)))
 for i,p in ps:
  o,_=p.communicate();print('I=%s rc=%d'%(i,p.returncode),o.strip().splitlines()[-1] if o.strip() else '',flush=True)
 print('elapsed %.0f s'%(time.monotonic()-t0))
