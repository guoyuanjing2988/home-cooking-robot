"""Retain overwritten planner candidates, including their fresh rejection."""
import json,copy
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';m=json.loads((O/'motion.json').read_text());r=copy.deepcopy(next(x for x in m['internal'] if x['index']==20))
if r.get('solver_geometry_ok'):
 r['ok']=True;r['archive_scope']='First source20 candidate; fresh final reference rejected the22mm goal error. Raw planner success only.'
 (O/'history_internal_source20_preliminary.json').write_text(json.dumps(dict(records=[r],elapsed_s=sum(x.get('planner_time_s',0) for x in r['edges'])),indent=2))
current=O/'motion_internal_grasp_20_21.json';saved=O/'motion_internal_grasp_clearance_rejected_20_21.json';saved.write_bytes(current.read_bytes());print('Source20 history preserved')
