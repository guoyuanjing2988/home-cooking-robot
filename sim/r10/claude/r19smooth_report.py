"""R19 smooth: summary tables from results/r19/smooth/<act>.json -> results/r19/smooth/summary.json + markdown tables on stdout.
python r19smooth_report.py"""
import json,os
OUT='results/r19/smooth';ACTS=['wok','spatula','lever','lid','spider']
rows=[];summ={}
for a in ACTS:
 f=f'{OUT}/{a}.json'
 if not os.path.exists(f):continue
 r=json.load(open(f));b=r['before'];bs=r['baseline_check'];st=b['stops']
 s=dict(act=a,r17_s=b['r17_time_s'],r17_motion_s=b['motion_s'],stored=b['stored_states'],label_jumps=b['label_jumps_2pi'],stopgo_s=b['stopgo_every_state_s'],
  stops_r17=dict(dwells=st['dwells'],joins=st['joins_stop_and_go'],reversals=st['reversals_gt150'],corners_90_150=st['corners_90_150'],corners_30_90=st['corners_30_90']),
  r17_peak_a=b['fd_peaks']['a'],r17_peak_j=b['fd_peaks']['j'],r17_step_bound_mm=b['step_bound_mm']['max'],
  baseline=dict(states=bs['states'],hits=bs['hit_states'],min_reserve_mm=bs['min_reserve_mm'],min_self_mm=bs['min_self_mm']),variants={})
 st0=json.load(open(f'{OUT}/{a}_baseline_stock.json'))['base'] if os.path.exists(f'{OUT}/{a}_baseline_stock.json') else None
 if st0:s['baseline_stock_model']=dict(states=st0['states'],hits=st0['hit_states'])
 for v,vv in r['variants'].items():
  c=vv['final_check'];t=vv['timing']
  s['variants'][v]=dict(check=dict(states=c['states'],hits=c['hit_states'],gjk_hits=c.get('gjk_hit_states'),out_of_range=c.get('out_of_range_states'),min_reserve_mm=c['min_reserve_mm'],min_self_mm=c['min_self_mm'],max_spacing_mm=c['max_spacing_mm'],rounds=len(vv['rounds'])),
   n_params=vv['stored']['n_params'],fixed_dev_mm=vv['fixed_piece_dev_mm'],fixed_tcp_off_line_mm=vv.get('fixed_tcp_off_line_mm'),
   timing={p:dict(total_s=x['total_s'],motion_s=x['motion_s'],zero_v=x['zero_velocity_points'],ramp_s=x['ramp_s'],ramp_fraction=min(1.,x['ramp_fraction']),peak_v=x['peak_v'],peak_a=x['peak_a'],peak_j=x['peak_j'],
    peak_v_tcp=x['peak_v_tcp'],peak_a_tcp=x['peak_a_tcp'],peak_j_tcp=x['peak_j_tcp'],peak_a_com=x['peak_a_com'],pgc=x['peak_pgc_Nm'],pgc_static=x['peak_pgc_static_Nm'],worst=x['worst_ratio'],stretched=x.get('stretched')) for p,x in t.items()})
 summ[a]=s
json.dump(summ,open(f'{OUT}/summary.json','w'),indent=1)
mx=lambda l:max(l[1:])
print('| Action | R17 time (motion) | stop-at-every-state | stops R17: dwell/join/reversal | baseline <=4 mm: states, hits, min reserve | variant | re-check: states, hits, min reserve | same | fast | fastcart | zero-v points | peak joint jerk R17 (FD) -> same (deg/s^3) |')
print('|'+'---|'*12)
for a,s in summ.items():
 for v,x in s['variants'].items():
  T=x['timing'];c=x['check'];st=s['stops_r17']
  print(f"| {a} | {s['r17_s']} ({s['r17_motion_s']:.1f}) | {s['stopgo_s']} | {st['dwells']}/{st['joins']}/{st['reversals']} | {s['baseline']['states']}, {s['baseline']['hits']}, {s['baseline']['min_reserve_mm']} | {v} | {c['states']}, {c['hits']}, {c['min_reserve_mm']} | {T['same']['total_s']} | {T['fast']['total_s']} | {T['fastcart']['total_s']} | {T['same']['zero_v']} | {mx(s['r17_peak_j']):.3g} -> {mx(T['same']['peak_j'])} |")
print()
for a,s in summ.items():
 x=s['variants'].get('spline')
 if not x:continue
 for p,T in x['timing'].items():print(a,'spline',p,'cart a %.2f j %.2f | joint a max %.0f deg/s2 j max %.0f deg/s3 | TCP v %.3f a %.2f j %.1f | CoM a %.2f | PGC %s (static %s) | ramp %.1f s (%.0f%%)'%(T['peak_a'][0],T['peak_j'][0],mx(T['peak_a']),mx(T['peak_j']),T['peak_v_tcp'],T['peak_a_tcp'],T['peak_j_tcp'],T['peak_a_com'],T['pgc'],T['pgc_static'],T['ramp_s'],100*T['ramp_fraction']))
