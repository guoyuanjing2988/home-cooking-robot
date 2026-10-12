"""Adaptive ninth iteration after the first eight structural screens."""
import csv,sys
import numpy as np
from scene import load,save,build,targets,H
from checker import Checker
from solver import solve
from run import station_audit
cfg=load('results/iterations/M05.json')['config'];cfg.update(trial='M09',verified_wheels=True,wash_front_high=True,change='Keep .85m/20deg fixed mount; correct all four full OEM wheel envelopes and mass; raise wash centre40mm onto actual water axis to clear sink rim. Full peeler retained.')
trial=sys.argv[1] if len(sys.argv)>1 else 'M09'
if trial=='M10':cfg.update(trial=trial,correct_peel_seat=True,change='Correct peeler seat to actual cradle top plus17.5mm food half-thickness (+9mm); no geometry/gate reduction. Retain M09 whole drive and high front wash.')
if trial=='M11':cfg.update(trial=trial,correct_peel_seat=True,upright_basket=True,change='Replace tilted unsupported wash placement with full upright basket at(-.55,.36,.670), three20mm physical support pads. Water axis crosses opening76mm off centre. Retain corrected cradle datum and all full OEM hardware.')
tree,meta=build(cfg);ch=Checker(tree,meta);audit=station_audit(ch,meta);probes=[]
for label in ['wash_load','peel_load','mandoline_work']:
 t=next(x for x in targets(cfg,meta) if x['name']==label);ht,hm=build(cfg,t['held']);hc=Checker(ht,hm)
 print(trial,label,flush=True);r=solve(hc,np.array(t['points'][0]),t['approach'],seed=929,target=t)
 save(f'results/iterations/{trial}_{label}.json',r);probes.append(dict(target=label,ok=r['ok'],starts=r['starts'],counts=r['status_counts'],best=r['best'],elapsed_s=r['elapsed_s']))
save(f'results/iterations/{trial}.json',dict(config=cfg,audit=audit,probes=probes,clear_samples=sum(r['ok'] for r in probes),total_samples=3,kind='full-scene endpoint screen; not execution'))
save('results/selected.json',dict(config=cfg,reason='Best upright-vs-canted comparison retains .85m fixed mount; M09 includes actual sourced wheel envelope and corrected wash datum. Peeler and ownership remain unclosed.'))
tree.write(H/'models/selected.xml',encoding='unicode')
rows=[]
for p in sorted((H/'results/iterations').glob('M??.json')):
 r=load(str(p.relative_to(H)));rows.append(dict(iteration=r['config']['trial'],change=r['config']['change'],clear_samples=r['clear_samples'],samples=3,starts=sum(x['starts'] for x in r['probes']),packing_penetrations=len(r['audit']['packing_hits']),evidence=str(p.relative_to(H))))
with (H/'results/iterations.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
print('M09 complete',sum(r['ok'] for r in probes),flush=True)
