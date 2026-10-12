"""Choose the strongest completed final screen and record its practical limits."""
import os
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[n]='1'
import json,math
from pathlib import Path
import numpy as np,mujoco
import checker as ck
from run import identifier,delta
from summarize import phases
HERE=Path(__file__).resolve().parent

def analyze(c):
    directory=HERE/'results/final'/identifier(c);rs=[json.loads((directory/f'{p}.json').read_text()) for p in ck.PHASES]
    assert len(rs)==16 and all(r['seeds']>=96 for r in rs)
    ck.configure(c);joint_margin=math.inf;reach_margin=math.inf;eff_counts={};witnesses={}
    for r in rs:
        pools=[]
        for si,seg in enumerate(r['definition']['segments']):
            parts=[row['segments'][si] for row in r['rows']]
            pools.append(sum(bool(p.get('ok')) and p['nominal']['torque']['ratio']<=.85 for p in parts))
        eff_counts[r['id']]=min(pools)
        if not r['feasible_seeds']:continue
        pool=r['composite_rows'] or [row for row in r['rows'] if row['ok']]
        best=min(pool,key=lambda row:row['nominal']['torque']['ratio']);witnesses[r['id']]=dict(seed=best['k'],source_seed_ids=best.get('source_seed_ids',[best['k']]),ratio=best['nominal']['torque']['ratio'])
        for si,part in enumerate(best['segments']):
            ch=ck.Checker(r['definition'],r['definition']['segments'][si],delta(r['id']))
            for po in part['poses']:
                q=np.asarray(po['q']);ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d)
                for n in ck.ARMS['R']:
                    lo,hi=ch.m.jnt_range[ch.jid[n]];joint_margin=min(joint_margin,float(min(q[ch.qa[n]]-lo,hi-q[ch.qa[n]])))
                dist=float(np.linalg.norm(ch.d.site('R_attachment_site').xpos-ch.d.body('R_mount').xpos))
                reach_margin=min(reach_margin,{'xArm6':.7,'UR5e':.85,'xArm7':.7,'FR3':.855,'AUBO_i5':.886}[c['arm']]-dist)
    passed=[r for r in rs if r['feasible_seeds']]
    return dict(id=identifier(c),config=c,phases_passed=len(passed),phases=phases(identifier(c)),
      worst_best_admitted_torque_ratio=max((r['best_nominal']['torque']['ratio'] for r in passed),default=None),
      active_arm_min_joint_limit_margin_deg=float(np.degrees(joint_margin)) if math.isfinite(joint_margin) else None,
      active_arm_min_nominal_reach_margin_m=reach_margin if math.isfinite(reach_margin) else None,
      rated_reference_efficiency_0_85_feasible_seeds=eff_counts,phases_at_efficiency_0_85=sum(n>0 for n in eff_counts.values()),
      witnesses=witnesses,verified_continuous_output_torque=False,fully_verified_rated_phase_count=0)

def main():
    configs=json.loads((HERE/'results/chosen_configs.json').read_text());designs=[analyze(c) for c in configs]
    ranked=sorted(designs,key=lambda r:(-r['phases_passed'],r['worst_best_admitted_torque_ratio'] or 99,-(r['active_arm_min_nominal_reach_margin_m'] or 0),r['config']['count']))
    winner=ranked[0]
    out=dict(winner,designs=designs,status='PARTIAL_CONDITIONAL_MODEL_SCREEN',source_commits=json.loads((HERE/'sources/sources.json').read_text()),
      arm_nominal_payload_kg=5.,tool_holder_mass_kg=1.2,required_nominal_flange_payload_kg=4.2,
      ratings=ck.META['ratings'],scene=dict(counter_z_m=.85,counter_depth_m=.60,upper_cabinet_bottom_m=1.35,upper_cabinet_top_m=1.95,upper_cabinet_depth_m=.37,
        rail_length_m=4.6,rail_y_m=.575,rail_travel_m=[-2.12,2.12],wall_bracket_x_m=[-1.5,-.75,0,.55],carriage_mass_kg=8.),
      rating_interpretation='Phase counts are unchanged-checker model admissions against manufacturer-rated motor torque times 100:1 gearing, without overload. Continuous joint-output rating and gearbox efficiency remain unverified; no fully verified continuous-rating pass is claimed.',
      open_requirements=['Continuous joint-output torque/thermal and gearbox efficiency evidence for the modeled hardware generation.',
        'Explicit spring-applied brake mechanism on every gravity-loaded joint. Power-loss-holding joint brakes are documented, spring mechanism is not.',
        'Safety-rated Category 1 stop chain and person detection, measured stopping time, door/restart interlocks.',
        'Structural beam/support/anchor design including overhang and dynamic/stopping cases.',
        'Custom gripper hardware/normal-force/key-bearing validation and room clearance for parked arms.',
        'Continuous stroke, transitions, tool pickup paths, wet-use protection, sanitation and food-quality trials.'])
    ck.json_write(HERE/'results/best.json',out)
    print('BEST',winner['id'],winner['phases_passed'],winner['worst_best_admitted_torque_ratio'])
if __name__=='__main__':main()
