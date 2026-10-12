import sys,runpy
from pathlib import Path
H=Path(__file__).resolve().parent
for args in [('v4_envelopes.py',),('v4_internal.py','4','3'),('v4_internal.py','19','18')]:
    sys.argv=list(args);runpy.run_path(str(H/args[0]),run_name='__main__')
