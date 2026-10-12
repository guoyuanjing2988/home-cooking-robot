import sys,runpy,os,json,time
from pathlib import Path
H=Path(__file__).resolve().parent;ID=sys.argv[1];os.environ['R07_LAYOUT']=ID;os.environ['R07_PARK_SECONDS']='480'
sys.argv=['park_single_v4_r07.py',ID];runpy.run_path(str(H/'park_single_v4_r07.py'),run_name='__main__')
sys.argv=['run_v4_r07.py','idle_v2_r07.py',ID,'--snapshot-only'];runpy.run_path(str(H/'run_v4_r07.py'),run_name='__main__')
