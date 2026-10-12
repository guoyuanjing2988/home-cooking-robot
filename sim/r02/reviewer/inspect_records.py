import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
if sys.argv[1]=='process':
 d=json.loads((ROOT/'sim/r02/tools/results/process_v2.json').read_text())
 for k in sys.argv[2:]: print(k,json.dumps(d[k],indent=2,ensure_ascii=True))
elif sys.argv[1]=='times':
 for f in (ROOT/'sim/r02/concept2/results/final_v4/c0684').glob('Q*.json'):
  r=json.loads(f.read_text());print(f.stem,len(r['parts']),round(r['elapsed_s']),[(p['label'],p['feasible_seeds'],p['ik_seeds'],p['collision_free_seeds']) for p in r['parts']])
elif sys.argv[1]=='json':
 for filename in sys.argv[2:]:
  d=json.loads((ROOT/filename).read_text(encoding='utf-8-sig'));print(filename,json.dumps(d,indent=2,ensure_ascii=True))
