"""Auditable forces, home-safety cost reconciliation and finite meal timing."""
import json,csv,math
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2];OUT=H/'results';OUT.mkdir(exist_ok=True)
def write(n,x): (OUT/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
def main():
 p=json.loads((ROOT/'sim/r02/tools/results/process_v2.json').read_text());f=p['force_models'];rows=[]
 calculations={'carrot_cut':2*67.59/31*35,'potato_cut':2*61.49/47*70,'greens_cut':2*67.59/31*80,'tomato_wedge':2*15/(math.pi*2**2)*4*70*.952,'peel_drag':1.5*1.68*25,'eye_core':2*67.59/31*12,'peel_normal':1.5*1000*.005,'root_rub':1.5*1000*.006,'leaf_rub':1.5*400*.005,'tomato_rub':1.5*200*.005,'cleanup_wipe':1.5*500*.005,'water_jet':1.5*1000*(.006/60)**2/(math.pi*.01**2/4),'drawer_insert':1.5*(.5*1.1*9.81+1.1*.3+2),'machine_index':1.5*(.5*1.1*9.81+1.1*.3),'end_cup_preload':1.5*1000*.01,'handle_carry':1.5*1*.3,'leaf_separate':1.5*.1*.3}
 for name in f:rows.append(dict(name=name,reported_design_N=f[name]['design_N'],review_calculated_N=calculations[name],difference_N=f[name]['design_N']-calculations[name],source_ids=f[name]['source_ids'],margin=f[name]['margin_factor'],status=('unsupported proxy; structural placeholder only' if name in ('greens_cut','tomato_wedge','eye_core') else 'carrot evidence; potato transfer unqualified' if name=='peel_drag' else 'sourced slow-cut sizing approximation' if name in ('carrot_cut','potato_cut') else 'physics estimate with explicit designed inputs; calibration/quality not proved')))
 write('force_arithmetic.json',rows)
 original=list(csv.DictReader((ROOT/'sim/r02/concept2/results/costs.csv').open()));subtotal=sum(float(r['total_cny']) for r in original if r['item']!='15pctcontingency')
 safety=[dict(item='presence sensors (mmWave/ToF), mounting and coverage',cny=1500),dict(item='E-stop, monitored stop relay, OEM interfaces, no safety PLC',cny=3500),dict(item='rail/arm brake monitoring and controlled-stop integration',cny=3500),dict(item='30mA RCBO/RCD coordination, PE, isolation, glands',cny=2500),dict(item='blade interlocks, park catch, load cell (B09 counted here)',cny=1350),dict(item='additional pinch/drip guards and cleaning separation',cny=2000),dict(item='safety circuit assembly/coverage and stop test allowance',cny=3650)]
 assert sum(x['cny'] for x in safety)==18000
 removed=114000+18000+1350
 corrected=subtotal-removed+18000
 costs=dict(original_subtotal=subtotal,original_total=subtotal*1.15,original_safety_scanner_curtain_PLC=114000,transport_included_safety=18000,tools_B09_included_safety=1350,home_safety_total=18000,home_safety_items=safety,correction='Remove 100000 scanner/curtain+14000 PLC, remove18000 transport safety duplicate, relocate1350 tools B09, add one inclusive18000 home safety package.',corrected_subtotal=corrected,contingency_rate=.15,corrected_total=corrected*1.15,safety_budget_10k_to20k_total=[(corrected-18000+10000)*1.15,(corrected-18000+20000)*1.15],r01_original_total=488175,r01_matched_home_total=(424500-114000+18000)*1.15,r1_pro_user_benchmark=470000,cost_basis='Engineering allowances; no quote, hardware changes or general autonomy R&D included')
 costs['r02_minus_r01_home']=costs['corrected_total']-costs['r01_matched_home_total'];costs['r02_vs_R1Pro_percent']=100*(costs['corrected_total']/470000-1)
 write('cost_reconciliation.json',costs)
 with (OUT/'costs_home.csv').open('w',newline='',encoding='utf-8') as stream:
  w=csv.writer(stream);w.writerow(['item','cny','basis'])
  for r in original:
   if r['item']=='15pctcontingency' or float(r['total_cny']) in (100000,14000):continue
   val=float(r['total_cny']);item=r['item']
   if val==74000:val-=18000;item='Transport excluding duplicate safety'
   if abs(val-14149.96)<.001:val-=1350;item='Tools excluding relocated B09 safety'
   w.writerow([item,round(val,2),r['basis']])
  w.writerow(['One home safety package',18000,'Engineering estimate; inclusive blade B09'])
  w.writerow(['15 percent contingency',round(corrected*.15,2),'One reserve'])
 t=json.loads((ROOT/'sim/r02/concept2/results/timeline.json').read_text());oldserial=t['planning_serial_s'];oldmakespan=t['planning_makespan_s']
 cutter_ids={'Q10.carrot','Q10.potato','Q14','Q18','Q19','Q24'}
 events=t['events'];oldcut=sum(e['duration_s'] for e in events if e['id'] in cutter_ids)
 # Finite process count:32 carrot cuts,18 potato cuts,6 greens cuts,1 wedger.
 def press_seconds(v):
  return 32*(35/v+35/50+3)+18*(70/v+70/50+3)+(70/v+70/50+30)+(30/v+30/50+25)+4*(30/v+30/50+3)+30+(60/v+60/50+20)
 custom=[dict(blade_velocity_mm_s=v,cut_cell_s=press_seconds(v),serial_without_soak_min=(oldserial-oldcut+press_seconds(v))/60,serial_with_reference_10min_soak_min=(oldserial-oldcut+press_seconds(v)+600)/60,force_proven_at_this_speed=False,drive_required_rpm=v/5*60) for v in (5,10,20)]
 timing=dict(reference_meal=dict(carrot_kg=.12,potato_kg=.20,greens_kg=.10,tomato_kg=.15,total_kg=.57),submitted_serial_min=oldserial/60,submitted_resource_min=oldmakespan/60,submitted_cut_min=oldcut/60,omitted_soak_min=10,submitted_Q16_s=next(e['duration_s'] for e in events if e['id']=='Q16'),slow_corrected_serial_min=(oldserial+600)/60,slow_corrected_current_schedule_min=(oldmakespan+600)/60,strict_soak_is_quality_reference_not_universal_minimum=True,commercial_CL50=dict(rpm=375,power_W=550,catalogue_practical_kg_h=150,reference_roots_ideal_throughput_s=.32/150*3600,one_edge_cuts_s=375/60,ideal_axial_feed_mm_s=5*375/60,blade_speed_at_assumed_radius_0p1m_m_s=2*math.pi*.1*375/60),recommended_root_process=dict(guarded_buyable_rotary_disc_rpm=375,disc_mm=5,planning_derated_cuts_s=1,planning_axial_feed_mm_s=5,estimated_50cuts_s=50,speed_is_axial_feed_not_blade_plunge=True),custom_press_sensitivity=custom,fast_disc_meal_estimate=dict(serial_min_range=[39,43],with_staged_soak_overlap_min_range=[30,35],arithmetic_serial_min=(oldserial-oldcut+50+120+600)/60,cycle_time_verified=False,assumptions='Existing non-cut handling allowances retained (26.3min);rootcut50s plus other guarded cuts/setup~2min;10minsoak retained. Serial estimate adds soak. Redesigned staged schedule hides most/all soak behind root peeling/coring;6min inspection/cleanup retained. Small reference meal,not scalable kg/hrobot rate.'),motor_check=dict(original_5mmlead_10rpm_mm_s=5*10/60,at_20mm_s_rpm=240,mechanical_power_at_1000N_20mm_s_W=20,mechanical_screw_torque_at_1000N_eff0p85_Nm=1000*.005/(2*math.pi*.85)),limits='Commercial speed proves slow universal restriction unwarranted; does not validate same slow-cut force or tomato/greens quality at a new press speed. Use OEM speed for bought slicer;20mm/s custom blade is a test target,not qualified release speed.')
 write('throughput.json',timing)
 print(json.dumps(dict(cost_cny=costs['corrected_total'],r01_home_cny=costs['r01_matched_home_total'],slow_time_min=timing['slow_corrected_current_schedule_min'],custom=custom)))
if __name__=='__main__':main()
