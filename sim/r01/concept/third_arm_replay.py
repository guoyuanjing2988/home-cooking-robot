"""Compare identical two-arm witnesses with an independently parked third arm."""
import os
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[n]='1'
import json,time
from pathlib import Path
import numpy as np
import checker as ck
from run import identifier,delta
HERE=Path(__file__).resolve().parent

def main():
    best=json.loads((HERE/'results/best.json').read_text());c2=dict(best['config'],count=2);c3=dict(c2,count=3);start=time.monotonic();phases=[]
    for pid in ck.PHASES:
        r=json.loads((HERE/'results/final'/identifier(c2)/f'{pid}.json').read_text());definition=r['definition']
        ck.configure(c2);old=[ck.Checker(definition,s,delta(pid)) for s in definition['segments']]
        ck.configure(c3);new=[ck.Checker(definition,s,delta(pid)) for s in definition['segments']]
        templates=[ch.initial(np.random.default_rng(0),0)[0] for ch in new];passed=[0]*len(new);lost=[]
        for row in r['rows']:
            for si,part in enumerate(row['segments']):
                if not part.get('ok'):continue
                a,b=old[si],new[si];ok=True;worst=0;hits=[]
                for pi,po in enumerate(part['poses']):
                    q=templates[si].copy()
                    for n in a.qa:q[b.qa[n]]=po['q'][a.qa[n]]
                    b.environment_pose(pi);h=b.forbidden(q);hits.extend(h);ok=ok and not h
                    hd=definition['segments'][si]['poses'][pi]['R']
                    for force in hd['nominal_forces_N']:
                        tq=b.torque(q,hd,force);gr=b.grip(q,hd,force);worst=max(worst,tq['ratio']);ok=ok and tq['ratio']<=1 and gr['margin']>=1
                if ok:passed[si]+=1
                else:lost.append(dict(seed=row['k'],segment=si,hits=hits[:4],torque_ratio=worst))
        phases.append(dict(phase=pid,two_arm_feasible_seeds=r['feasible_seeds'],three_arm_same_pose_stroke_counts=passed,
           three_arm_same_pose_feasible_seeds=min(passed),lost_witnesses=lost))
        if time.monotonic()-start>1100:raise TimeoutError('replay')
    ck.json_write(HERE/'results/third_arm_replay.json',dict(two_arm_config=c2,three_arm_config=c3,phases=phases,elapsed_s=time.monotonic()-start,
        interpretation='R/L poses and frozen carriages are identical, C is independently parked. No stabilising force or contact is invented: all T08 tasks assign R and fixed fixtures. Separate 96-seed sweeps differ in RNG consumption, so seed-count differences alone do not demonstrate benefit.'))
    print([(p['phase'],p['two_arm_feasible_seeds'],p['three_arm_same_pose_feasible_seeds']) for p in phases])
if __name__=='__main__':main()
