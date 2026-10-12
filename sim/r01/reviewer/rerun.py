"""Independent foreground R01 review: read concept code, write only reviewer output."""
import os
for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import sys, json, time, argparse, subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'concept'))
import checker as ck

def worker(pid):
    best=json.loads((HERE.parent/'concept/results/best.json').read_text())
    ck.configure(best['config'])
    r=ck.normalize_result(ck.run_phase(pid,96,.05 if pid=='P01' else 0.))
    r['config']=best['config']
    r['review_status']='conditional diagnostic; output-rated torques unverified'
    out=HERE/'reruns';out.mkdir(exist_ok=True)
    ck.json_write(out/f'{pid}.json',r)
    prior=json.loads((HERE.parent/'concept/results/final'/best['id']/f'{pid}.json').read_text())
    keys=['verdict','feasible_seeds','ik_seeds','collision_free_seeds','blocker_counts','best_seed']
    comparison={k:dict(original=prior[k],review=r[k],equal=prior[k]==r[k]) for k in keys}
    comparison['nominal_ratio_abs_difference']=abs(prior['best_nominal']['torque']['ratio']-r['best_nominal']['torque']['ratio']) if prior['best_nominal'] and r['best_nominal'] else None
    ck.json_write(out/f'{pid}.comparison.json',comparison)
    print(pid,r['verdict'],r['feasible_seeds'],r['blocker_counts'],comparison,flush=True)

def bounded(command,name,seconds):
    if not 0<seconds<1200:raise ValueError('Must be below 20 minutes')
    (HERE/'audit').mkdir(exist_ok=True)
    began=time.monotonic();peak=0;reason=None
    with (HERE/'audit'/f'{name}.log').open('w',encoding='utf-8') as log:
        p=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
        try:
            while p.poll() is None:
                peak=max(peak,ck.tree_peak_memory(p.pid))
                if time.monotonic()-began>seconds:reason='timeout';raise TimeoutError(name)
                if peak>1900:reason='memory';raise MemoryError(name)
                time.sleep(.5)
        finally:
            if p.poll() is None:ck.kill_tree(p)
            ck.json_write(HERE/'audit'/f'{name}.resource.json',dict(command=command,elapsed_s=time.monotonic()-began,peak_MiB=peak,exit_code=p.returncode,timeout_s=seconds,limit_MiB=1900,workers=1,failure=reason))
    print((HERE/'audit'/f'{name}.log').read_text()[-3500:],flush=True)
    if p.returncode:raise RuntimeError(f'{name}: exit {p.returncode}')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--worker');ap.add_argument('--phases',nargs='+');ap.add_argument('--seconds',type=int,default=240);ap.add_argument('--script');args=ap.parse_args()
    if args.worker:worker(args.worker)
    elif args.phases:
        for phase in args.phases:bounded([sys.executable,'-B','-u',str(__file__),'--worker',phase],phase,args.seconds)
    elif args.script:bounded([sys.executable,'-B','-u',str(HERE/args.script)],Path(args.script).stem,args.seconds)
