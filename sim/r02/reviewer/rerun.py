"""Fresh IK runs, with original adapter, read-only source and reviewer-only output."""
import sys, os, json, time, argparse, hashlib
from pathlib import Path
sys.dont_write_bytecode=True
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[key]='1'
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'sim/r02/concept2'))
import adapter
def worker(pid):
    best=json.loads((ROOT/'sim/r02/concept2/results/best.json').read_text())
    ph=next(p for p in adapter.process_instances() if p['id']==pid)
    result=adapter.run_instance(ph,best['config'],96)
    result['review_note']='fresh 96-seed solve; original adapter and rule; unqualified rated-output limits'
    out=HERE/'reruns';out.mkdir(exist_ok=True)
    (out/(pid+'.json')).write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    prior_path=ROOT/'sim/r02/concept2/results/final_v4'/best['id']/(pid+'.json')
    prior=json.loads(prior_path.read_text())
    def summary(r):return dict(ok=r['ok'],feasible_seeds=r['feasible_seeds'],parts=[{k:p[k] for k in ('label','seeds','feasible_seeds','ik_seeds','collision_free_seeds','blocker_counts')} for p in r['parts']])
    comparison=dict(id=pid,original=summary(prior),rerun=summary(result),counts_equal=summary(prior)==summary(result),prior_sha256=hashlib.sha256(prior_path.read_bytes()).hexdigest(),rerun_sha256=hashlib.sha256((out/(pid+'.json')).read_bytes()).hexdigest(),elapsed_s=result['elapsed_s'])
    (out/(pid+'.comparison.json')).write_text(json.dumps(comparison,indent=2),encoding='utf-8')
    print(json.dumps(comparison),flush=True)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('phase');args=parser.parse_args();worker(args.phase)
