"""Three disjoint queues: redo prior positive strokes first, then remaining recipe."""
import json,sys,runpy,time
from pathlib import Path
H=Path(__file__).resolve().parent;ID=sys.argv[1];part=int(sys.argv[2]);start=time.monotonic();positive=[int(p.stem) for p in (H/'results/static_v4/L53').glob('*.json') if json.loads(p.read_text()).get('witness')]
priority=sorted(positive)+[i for i in (47,48,49,50,51,52,54,55,56,57,58,16,17,18,19,35,36,37,38,39,13,14,15,32,33,34,10,12,28,30,31,43,46,53) if i not in positive]
priority+= [i for i in range(59) if i not in priority];assert len(priority)==len(set(priority))==59
queue=priority[part::3]
(H/'audit'/f'{ID}_queue_{part}.json').write_text(json.dumps(dict(indices=queue,prior_positive_proposals=positive),indent=2))
for i in queue:
 remaining=1035-(time.monotonic()-start)
 if remaining<40:break
 sys.argv=['static_v7_r07.py',ID,str(i),str(i+1),str(remaining),'96','96'];runpy.run_path(str(H/'static_v7_r07.py'),run_name='__main__')
