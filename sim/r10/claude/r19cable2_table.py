"""R19 #36 part 2: pass / fail table of the tool-connector runs (new file; reads results/r19/cable only).
Per set and routing: states, hit states (cable group), smallest cable reserve past the gate against the environment and
the robot (self), plume (stir), and the checker's own verdict for certificate runs (one routing, no CABLEONLY).
python r19cable2_table.py -> results/r19/cable/summary2.json and a markdown table on stdout"""
import json,glob,os
R='results/r19/cable'
SETS=[('wok','chains/chain_wok_s-1_final_py.1?_*'),('plate 2','chains/chain_wok_s-1_r18plate2b_*'),('lever','chains/chain_lever_*'),
 ('lid','chains/chain_lid_*'),('spatula','chains/chain_spatula_*'),('spider','chains/chain_spider_*'),('stir work','stir/lib_stir_cycle_*_work__*'),
 ('stir return','stir/lib_stir_cycle_*_return__*'),('hub a','hub/hubtcf_a__*'),('hub b','hub/hubtcf_b__*'),('hub c','hub/hubtcf_c__*'),
 ('hub a','hub/flexhub_a__*'),('hub b','hub/flexhub_b__*'),('hub c','hub/flexhub_c__*')]+[(f'prep {p}',f'prep/chain_{p}_ur5e_enc2_pgc__*') for p in
 ('carrot_full','press_full','tomato_full','bascarrot_full','basket_y20p30','ctray_full','soak_full','tubempty_full','tubfill_t15fin')]
RUNS={'ur5e_enc2_pgcc_yp_a-45_tcf':'cert','ur5e_enc2_pgcc_TC_cableonly':'screen','fr5_j6_pgc_sp20c_TC_cableonly':'screen','ur5e_enc2_pgcc_TCX_cableonly':'screen'}
out={}
for run,kind in RUNS.items():
 for label,pat in SETS:
  for f in sorted(glob.glob(f'{R}/{pat}')):
   if not f.endswith(f'__{run}.json'):continue
   d=json.load(open(f));rows={}
   for p,v in d['parts'].items():
    for g,c in v['cable_groups'].items():
     r=rows.setdefault(g,dict(states=0,hits=0,env=1e9,self=1e9,plume=None,checker_hits=0,noncable_hits=0))
     r['states']+=v['states'];r['hits']+=c['hit_states'];r['env']=min(r['env'],c['min_env']);r['self']=min(r['self'],c['min_self'])
     if 'min_plume' in c:r['plume']=c['min_plume'] if r['plume'] is None else min(r['plume'],c['min_plume'])
     if kind=='cert':r['checker_hits']+=v['hit_states'];r['noncable_hits']+=v['noncable_hit_states']
   for g,r in rows.items():out.setdefault(run,{}).setdefault(g,{})[label+(' ('+os.path.basename(f).split('__')[0]+')' if label.startswith(('wok','plate')) and 'fr5' in f else '')]=dict(file=f,**r)
json.dump(out,open(f'{R}/summary2.json','w'),indent=1)
for run,G in out.items():
 for g,S in G.items():
  print(f'\n### {run} / {g}\n\n| Set | States | Hit states | Cable env / self reserve (mm) |\n|---|---|---|---|')
  for k,r in S.items():print(f"| {k} | {r['states']} | {r['hits']}{' (checker '+str(r['checker_hits'])+')' if 'cableonly' not in run else ''} | {r['env']:.1f} / {r['self']:.1f}{' , plume '+format(r['plume'],'.1f') if r['plume'] is not None else ''} |")
