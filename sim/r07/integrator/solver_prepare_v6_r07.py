from pathlib import Path
H=Path(__file__).resolve().parent
for stem in ('least_analytic','collision_ik','mink'):
 s=(H/(stem+'_v4_r07.py')).read_text().replace('robust_search_v4_r07','robust_search_v6_r07');(H/(stem+'_v6_r07.py')).write_text(s)
p=H/'least_fixed_v6_r07.py';p.write_text(p.read_text().replace('robust_search_v4_r07','robust_search_v6_r07'))
p=H/'static_v6_r07.py';s=p.read_text()
for stem in ('least_analytic','collision_ik','mink'):s=s.replace(stem+'_v4_r07',stem+'_v6_r07')
s=s.replace("compact['proposal_methods']=sorted(set(methods));", "compact['proposal_methods']=sorted(set(methods));compact['extra_clearance_objective_policy']='v6 certified bounds; unresponsive pairs reported for layout changes';compact['unresponsive_extra_pairs']=getattr(ch,'immobile_extra_objective',{});" )
p.write_text(s)
