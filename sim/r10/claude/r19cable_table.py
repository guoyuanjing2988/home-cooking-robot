"""R19 #36: table of the cable-routing screens and certificates in results/r19/cable/ (new file, read-only on the results).
python r19cable_table.py [PAT=<glob under results/r19/cable>] -> per file and part: for each cable group, hit states and the
minimum env / self reserve (mm past the gate); for a certificate run (single routing) also the checker's own verdict."""
import sys,json,glob,os
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
rows={}
for f in sorted(glob.glob('results/r19/cable/'+KV.get('PAT','*/*.json'))):
 if os.path.basename(f).startswith(('md5','static')):continue
 r=json.load(open(f))
 if 'parts' not in r:continue
 print(f"\n{os.path.basename(f)}  ok={r['ok']}  {r.get('elapsed_s')} s")
 for p,v in r['parts'].items():
  cg=v.get('cable_groups',{})
  s=' '.join(f"{g.replace('cable.','')}:{x['hit_states']}/{x['min_env']:.1f}/{x['min_self']:.1f}"+(f"/pl{x['min_plume']:.1f}" if 'min_plume' in x else '') for g,x in cg.items())
  extra='' if r['arm'].endswith(('_ALL','_SEL')) and 'cableonly' in f else f" | checker hits {v['hit_states']} env {v.get('min_env_reserve_mm')} self {v['min_reserve_by_category'].get('self',{}).get('reserve_mm')} noncable {v.get('noncable_hit_states')}"
  print(f"  {p:12s} {v['states']:6d} st  {s}{extra}")
