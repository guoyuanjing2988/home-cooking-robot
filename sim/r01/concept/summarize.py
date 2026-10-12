"""Compact phase tables and witness margins; no acceptance changes."""
import json,csv
from pathlib import Path
HERE=Path(__file__).resolve().parent

def measured(stage):
    rows=[]
    for d in (HERE/'results'/stage).iterdir():
        if not d.is_dir() or d.name.startswith('group'):continue
        rs=[json.loads(p.read_text()) for p in d.glob('P*.json')]
        if len(rs)!=16:continue
        passed=[r for r in rs if r['feasible_seeds']]
        rows.append(dict(id=d.name,config=rs[0]['config'],phases=len(passed),worst_ratio=max((r['best_nominal']['torque']['ratio'] for r in passed),default=99),
            ik_phases=sum(r['ik_seeds']>0 for r in rs),collision_free_phases=sum(r['collision_free_seeds']>0 for r in rs)))
    return sorted(rows,key=lambda r:(-r['phases'],r['worst_ratio'],r['config']['count']))

def phases(config_id):
    rows=[]
    for p in sorted((HERE/'results/final'/config_id).glob('P*.json')):
        r=json.loads(p.read_text());good=r['feasible_seeds']>0;row=dict(phase=r['id'],name=r['name'],seeds=r['seeds'],feasible_seeds=r['feasible_seeds'],ik_seeds=r['ik_seeds'],collision_free_seeds=r['collision_free_seeds'],
          nominal_ratio=r['best_nominal']['torque']['ratio'] if r['best_nominal'] else None,
          check_ratio=r['best_check']['torque']['ratio'] if r['best_check'] else None,ratio_pool=r['best_ratios_pool'],nominal_joint=r['best_nominal']['torque']['joint'] if r['best_nominal'] else None,
          blocker_counts=r['blocker_counts'],best_source_seed_ids=r['best_source_seed_ids'],stroke_counts=r['stroke_counts'])
        if good:row['ratio_if_gear_efficiency_0_85']=row['nominal_ratio']/.85
        rows.append(row)
    return rows

if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='phases':print(json.dumps(phases(sys.argv[2]),indent=2))
    else:
        stage=sys.argv[1] if len(sys.argv)>1 else 'coarse'
        r=measured(stage);print(json.dumps(r[:20],indent=2));print('complete designs',len(r))
