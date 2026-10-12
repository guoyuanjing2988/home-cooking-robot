import sys,runpy,json
from pathlib import Path
H=Path(__file__).resolve().parent
for mode in sys.argv[1:]:
    if mode=='internal':
        p=H.parent/'integrator/results/motion_v4/L53'
        ids=sorted(json.loads(f.read_text())['index'] for f in p.glob('internal_*.json') if json.loads(f.read_text())['ok'])
        for i in ids:
            sys.argv=['v4_internal.py',str(i)]
            runpy.run_path(str(H/'v4_internal.py'),run_name='__main__')
    else:
        sys.argv=[f'v4_{mode}.py','L53']
        runpy.run_path(str(H/f'v4_{mode}.py'),run_name='__main__')
