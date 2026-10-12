import sys,runpy,json
from pathlib import Path
H=Path(__file__).resolve().parent
I=H.parent/'integrator'
mode=sys.argv[1]
if mode=='internal':
    ids=sorted(json.loads(p.read_text())['index'] for p in (I/'results/motion_v2/L34').glob('internal_*.json') if json.loads(p.read_text()).get('ok'))
    for i in ids:
        if (H/'results_v3'/f'internal_{i}.json').exists():continue
        sys.argv=[str(H/'v3_internal.py'),str(i)]
        runpy.run_path(sys.argv[0],run_name='__main__')
else:
    for name in sys.argv[1:]:
        sys.argv=[str(H/f'v3_{name}.py'),'L34']
        runpy.run_path(sys.argv[0],run_name='__main__')
