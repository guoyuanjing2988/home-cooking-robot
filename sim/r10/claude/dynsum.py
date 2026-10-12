"""Summarise dyn results: python dynsum.py <glob> ... (results/dyn_*.json)."""
import sys,json,glob
rows=[]
for pat in sys.argv[1:]:
 for f in sorted(glob.glob(pat)):
  if f.endswith(('_labels.json',)):continue
  d=json.load(open(f));ok=d.get('on_plate',d.get('in_chute'))
  rel=[e.get('moved_after_release_mm') for e in d['events']]
  rows.append((f.split('dyn_')[1][:-5],d['item'],d.get('finger') or 'stock',d['mu'],d.get('grip',''),d.get('item_d'),d['max_slip_in_grip_mm'],d['max_slip_in_grip_deg'],d.get('max_pad_contact_N'),ok,rel))
print(f"{'tag':48s} {'item':6s} {'fing':5s} {'mu':>4s} {'grip':>12s} {'slip mm':>8s} {'deg':>6s} {'padN':>6s} ok  release-moves")
for r in rows:print(f"{r[0][:48]:48s} {r[1]:6s} {r[2]:5s} {r[3]:4.2f} {r[4][:12]:>12s} {r[6]:8.1f} {r[7]:6.1f} {r[8] if r[8] is not None else '':>6} {str(r[9]):5s} {r[10]}")
