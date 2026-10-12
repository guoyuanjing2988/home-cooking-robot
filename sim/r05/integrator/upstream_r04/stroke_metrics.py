"""Compact reviewer ledger derived from independently replayed stroke evidence."""
import json,csv
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results'
def main():
 summary=json.loads((O/'phase_summary.json').read_text());best=json.loads((O/'best.json').read_text());rows=[]
 cats=['robot_environment','arm_arm_or_frame','held_gripper_environment','self']
 for instance in summary['instances']:
  for part in instance['parts']:
   key=part['id'];row=dict(stroke=key,stage=part['source_stage'],starts=part['starts'],solver_solutions=part['solver_solutions_found'],independently_verified_witnesses=part['independent_verified_witnesses'],static_pass=part['ok'],position_error_mm_max=None,orientation_error_deg_max=None,envelope_ratio_nominal_max=None,envelope_ratio_check_max=None,grip_margin_check_min=None,published_rated_joint_output_ratio=None,xArm_motor_gear_ideal_ratio_check_max=None)
   for cat in cats:
    row[cat+'_clearance_mm_min']=None;row[cat+'_minimum_is_lower_bound']=None
   w=best['witnesses'].get(key)
   if w:
    poses=w['poses'];errors=[error for p in poses for error in p['errors']]
    row.update(position_error_mm_max=max(e['position_mm'] for e in errors),orientation_error_deg_max=max(e['orientation_deg'] for e in errors),envelope_ratio_nominal_max=w['max_envelope_ratios']['nominal'],envelope_ratio_check_max=w['max_envelope_ratios']['check'],grip_margin_check_min=min(g['margin'] for p in poses for g in p['grip']['check']),xArm_motor_gear_ideal_ratio_check_max=max(v for p in poses for v in p['xArm_motor_rated_times_gear_ideal_ratios'].values()))
    for cat in cats:
     record=min((p['min_clearance'][cat] for p in poses),key=lambda r:r['clearance_mm'])
     row[cat+'_clearance_mm_min']=record['clearance_mm'];row[cat+'_minimum_is_lower_bound']=record['lower_bound']
   rows.append(row)
 with (O/'stroke_metrics.csv').open('w',newline='',encoding='utf-8-sig') as file:
  writer=csv.DictWriter(file,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 print('metrics',len(rows),'static accepted',sum(r['static_pass'] for r in rows))
if __name__=='__main__':main()
