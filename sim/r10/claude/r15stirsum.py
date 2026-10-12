"""Table of stirbench results (results/r15/stir_*.json with the 2-zone metrics)."""
import json,glob
rows=[]
for f in sorted(glob.glob('results/r15/stir_*.json')):
 if f.endswith('_keys.json'):continue
 d=json.load(open(f))
 if 'zones' not in d:continue
 z={round(x['hot_r_m'],2):x for x in d['zones']}
 def zs(r):x=z[r];return f"hot {x['hot_frac']['mean']:.2f} cv {x['hot_frac']['cv']:.2f} p10 {x['hot_frac']['p10']:.2f} never {x['never_hot']:2d} dwell {x['dwell_max_s']:5.2f} cold50/90/max {x['cold_p50_s']:.1f}/{x['cold_p90_s']:.1f}/{x['cold_max_s']:.1f}"
 sp=d.get('spatula_F_N');mo=d.get('spatula_M_grip_Nm')
 print(f.split('stir_')[1][:-5][:36].ljust(36),f"n{d['n']} {d['mass_g']}g spill {d['spilled']:2d} |r.09 {zs(.09)} |r.13 {zs(.13)} | flips {d['flips_per_10s']['mean']:.1f}",
  f"| F p95 {sp['p95']:.1f} M p95 {mo['p95']:.2f} max {mo['max']:.1f} jam {d['jam_samples_over_30N']} v {d['blade_v_mps']['max']} a {d['blade_a_mps2']['max']} w {d['blade_w_degps']['max']}" if sp else '')
