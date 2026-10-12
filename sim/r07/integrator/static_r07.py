import json,time,sys,copy
import numpy as np
import r07_runtime as rt
if '--mobile-helper' in sys.argv:
 import r07_ik
 r07_ik.install()
s=rt.s;H=rt.H;O=rt.O
lo=int(sys.argv[1]);hi=int(sys.argv[2]);seeds=int(sys.argv[3]) if len(sys.argv)>3 else 12
items=[(ph,sg,ph['id']+'__'+sg['label'].replace(' ','_')) for ph in s.P['phases'] for sg in ph['segments']]
(O/'static').mkdir(exist_ok=True)
old=json.loads((O/'inherited_best.json').read_text())['witnesses'];began=time.monotonic()
for index in range(lo,min(hi,len(items))):
 ph,sg,key=items[index];ch=s.Checker(ph,sg);rng=np.random.default_rng(70700+index);rows=[];good=[]
 for k in range(seeds):
  # Fresh solves in R07; the archived q is a warm start, never an admission.
  if k==0 and key in old:
   qs=np.array(old[key]['poses'][0]['q']);base=ch.initial
   def warm(rng,k):
    q,park=base(rng,k)
    for side in ch.hands:
     for n in s.ck.ARMS[side]:q[ch.qa[n]]=np.clip(qs[ch.qa[n]],*ch.m.jnt_range[ch.jid[n]])
    return q,park
   ch.initial=warm
  start=time.monotonic();raw=ch.run_seed(k,rng)
  if k==0 and key in old:ch.initial=base
  # Every solver proposal gets the unchanged reference pose/load/grip replay
  # plus R05 all-pair convex checker on the new geometry.
  verified=rt.f.replay(ch,raw) if len(raw['poses'])==len(sg['poses']) else None
  row=dict(seed=k,solver_ok=raw['ok'],elapsed_s=time.monotonic()-start,raw=raw,replay=verified)
  rows.append(row)
  if verified and verified['ok']:good.append(verified);break
 witness=min(good,key=lambda r:r['max_envelope_ratios']['check']) if good else None
 out=dict(index=index,stroke=key,logical=ph['id'].split('.')[0],phase=ph['id'],label=sg['label'],ok=bool(witness),starts=len(rows),solver_solutions_found=sum(r['solver_ok'] for r in rows),witness=witness,rows=rows,config=s.model.CONFIG)
 rt.write('static/'+str(index)+'.json',out)
 if witness:(H/'models'/('stroke_'+str(index)+'.xml')).write_text(ch.xml)
 print(index,key,'PASS' if witness else 'FAIL','seeds',len(rows),'elapsed',round(time.monotonic()-began,1),flush=True)
