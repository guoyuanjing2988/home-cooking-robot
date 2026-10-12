"""Breadth-first resumable96-start study, never overwriting an existing start.
Each script invocation is bounded externally and internally to<20minutes.
"""
import sys,json,time,runpy,gc
from pathlib import Path
layout=sys.argv[1];lo=int(sys.argv[2]);hi=int(sys.argv[3]);visit=int(sys.argv[4]) if len(sys.argv)>4 else 6;budget=float(sys.argv[5]) if len(sys.argv)>5 else 1020
H=Path(__file__).resolve().parent;began=time.monotonic();calls=[]
while time.monotonic()-began<budget-35:
 options=[]
 for i in range(lo,hi):
  f=H/'results/static_v2'/layout/f'{i}.json';r=json.loads(f.read_text()) if f.exists() else {'starts':0}
  if r['starts']<96:options.append((r['starts'],i))
 if not options:break
 starts,index=min(options);remaining=budget-(time.monotonic()-began)-5
 sys.argv=['static_v2_r07.py',layout,str(index),str(index+1),str(remaining),'96',str(visit)]
 t=time.monotonic();runpy.run_path(str(H/'static_v2_r07.py'),run_name='__main__');gc.collect()
 f=H/'results/static_v2'/layout/f'{index}.json';r=json.loads(f.read_text()) if f.exists() else {'starts':starts}
 calls.append(dict(index=index,before=starts,after=r['starts'],seconds=time.monotonic()-t,ok=bool(r.get('witness'))))
 (H/'audit'/f'{layout}_breadth_{lo}_{hi}_{int(began)}.json').write_text(json.dumps(dict(layout=layout,required_starts=96,visit_starts=visit,calls=calls,elapsed_s=time.monotonic()-began),indent=2))
 if r['starts']==starts:break
print('BREADTH_CHUNK',layout,lo,hi,'calls',len(calls),'elapsed',time.monotonic()-began,flush=True)
