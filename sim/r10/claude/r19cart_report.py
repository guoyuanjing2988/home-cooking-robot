"""R19 cart (issue #14): tables from results/r19/cart/*.json -> results/r19/cart/summary.json + markdown on stdout.
python r19cart_report.py"""
import json,glob,os
import numpy as np
D='results/r19/cart'
def load(n):
 p=f'{D}/{n}.json';return json.load(open(p)) if os.path.exists(p) else None
def rows(act):
 out={}
 for f in sorted(glob.glob(f'{D}/dyn_{act}*.json')):
  if f.endswith('_sweep.json'):continue
  for pro,P in json.load(open(f))['profiles'].items():out[pro]=P
 return out
def mu_s(x):return '>5 (wheel unloaded)' if x>5 else f'{x:.2f}'
def main():
 S={};print('## A. Dynamic margins along the smoothed laws (BOM cart, swivel casters, tether 20 N; rigid body)\n')
 print('| Action | Profile | Motion s | Min tip margin mm (edge) | Static mm | Cart moving mm | max mu_req | min drive load N | elastic 3/5/8 Hz mm (E) | slope 1 deg mm | rigid castors: mm / mu |')
 print('|---|---|---|---|---|---|---|---|---|---|---|')
 for act in ('wok','spider','spatula','lid','lever','stir'):
  for pro,P in rows(act).items():
   r=P['rows'].get('bom')
   if not r:continue
   S.setdefault(act,{})[pro]=r
   print(f"| {act} | {pro} | {P['motion_s']} | {r['min_margin_mm']} ({r['edge']}) | {r['static_min_margin_mm']} | {r['min_margin_cart_moving_mm']} | {r['max_mu']:.2f} | {r['min_drive_load_N']} | "
    f"{r.get('sdof_3Hz_min_margin_mm')} / {r.get('sdof_5Hz_min_margin_mm')} / {r.get('sdof_8Hz_min_margin_mm')} | {r['sens_slope1deg']['min_margin_mm']} | {r['sens_rigid_castors']['min_margin_mm']} / {r['sens_rigid_castors']['max_mu']:.2f} |")
 print('\n## B. Mass model sensitivity (min tip margin mm / max mu_req)\n')
 print('| Action | Profile | sim boxes | BOM steel mast | BOM Al mast | chassis -30 % | chassis +30 % |');print('|---|---|---|---|---|---|---|')
 for act in ('wok','spider','spatula','lid','lever','stir'):
  for pro,P in rows(act).items():
   R=P['rows'];g=lambda k:f"{R[k]['min_margin_mm']} / {R[k]['max_mu']:.2f}" if k in R and 'min_margin_mm' in R[k] and 'max_mu' in R[k] else '-'
   print(f"| {act} | {pro} | {g('sim')} | {g('bom')} | {g('bom_al')} | {g('bom_m30')} | {g('bom_p30')} |")
 print('\n## C. Protective stops (BOM, swivel). Worst over all start instants: min instantaneous ZMP margin mm | rocking energy ratio (1 = tips) | lift mm | slip mm\n')
 print('| Action / profile | decel set | arm cat0, cart on law | arm cat1/2, cart on law | arm cat0 + cart E-stop 0.5 | arm cat1/2 + cart E-stop 0.5 | arm cat0 + cart E-stop traction-limited | cart E-stop 0.5 only | cart E-stop traction-limited only |')
 print('|---|---|---|---|---|---|---|---|---|')
 for act in ('wok','spider','spatula','lid','lever','stir'):
  for pro,P in rows(act).items():
   r=P['rows'].get('bom',{})
   for al in ('max','66'):
    st=r.get('stops_alpha_'+al)
    if not st:continue
    cells=[]
    for k in ('cat0+law','cat12+law','cat0+es05','cat12+es05','cat0+esmax','none+es05','none+esmax'):
     x=st[k];cells.append('-' if not x['n'] else f"{x['min_margin_mm']} \\| {x['energy_ratio']:.4f} \\| {x['lift_mm']:.2f} \\| {x['slip_mm']:.1f}")
    print(f"| {act} {pro} | {al} | "+' | '.join(cells)+' |')
    S.setdefault('stops',{}).setdefault(act,{}).setdefault(pro,{})[al]=st
 print('\n## D. Cart acceleration sweep (fast caps, cart jerk = a / 0.1 s; BOM, swivel)\n')
 print('| Action | a_cart limit | reached | motion s | min margin mm | max mu_req | elastic 5 Hz mm | rigid castors mu | slope 0.5 deg mm |');print('|---|---|---|---|---|---|---|---|---|')
 amax={}
 for act in ('wok','spider','spatula','lid'):
  sw=None
  for f in glob.glob(f'{D}/dyn_{act}*.json'):
   j=json.load(open(f))
   if j.get('a_sweep'):sw=j['a_sweep']
  if not sw:continue
  for x in sw:print(f"| {act} | {x['a_cart']} | {x['max_cart_a']} | {x['motion_s']} | {x['min_margin_mm']} | {x['max_mu']:.2f} | {x['sdof_5Hz_min_margin_mm']} | {x['rigid_castors']['max_mu']:.2f} | {x['slope05']['min_margin_mm']} |")
  a=np.array([x['a_cart'] for x in sw]);m=np.array([x['max_mu'] for x in sw]);mr=np.array([x['rigid_castors']['max_mu'] for x in sw])
  def cross(y,lim):
   if y[0]>lim:return 0.
   for i in range(1,len(y)):
    if y[i]>lim:return round(float(a[i-1]+(lim-y[i-1])*(a[i]-a[i-1])/(y[i]-y[i-1])),2)
   return f'>{a[-1]}'
  amax[act]=dict(swivel={f'mu{l}':cross(m,l) for l in (.5,.4,.3,.24,.2)},rigid={f'mu{l}':cross(mr,l) for l in (.5,.4,.3,.24,.2)})
 S['a_max']=amax;print('\nLargest cart-acceleration limit with max mu_req <= value (linear interpolation of the sweep):',json.dumps(amax,indent=0))
 o=[];[o.extend(json.load(open(f))['options']) for f in sorted(glob.glob(f'{D}/options_opt_*.json'))]
 if o:
  print('\n## E. Design options (min tip margin mm | max mu_req | elastic 5 Hz mm)\n')
  cases=[];[cases.append((x['act'],x['profile'])) for x in o if (x['act'],x['profile']) not in cases]
  print('| Option | '+' | '.join(f'{a} {p}' for a,p in cases)+' |');print('|---|'+'---|'*len(cases))
  names=[];[names.append(x['option']) for x in o if x['option'] not in names]
  for n in names:
   cells=[]
   for c in cases:
    x=next((y for y in o if y['option']==n and (y['act'],y['profile'])==c),None);cells.append('-' if not x else f"{x['min_margin_mm']} \\| {x['max_mu']:.2f} \\| {x['sdof5_mm']}")
   print(f'| {n} | '+' | '.join(cells)+' |')
  S['options']=o
 j=load('options_jerk')
 if j:
  print('\n## F. Cart jerk (wok, fast caps)\n');print('| a_cart | j_cart | ramp s | motion s | rigid mm | max mu_req | elastic 3 / 5 / 8 Hz mm |');print('|---|---|---|---|---|---|---|')
  for x in j['jerk']:print(f"| {x['a_cart']} | {x['j_cart']} | {x['ramp_s']} | {x['motion_s']} | {x['rigid_mm']} | {x['max_mu']:.2f} | {x['sdof3_mm']} / {x['sdof5_mm']} / {x['sdof8_mm']} |")
  print('\nFriction mechanism (wok fastcart, worst instant):',json.dumps(j['friction']));S['jerk']=j
 b=load('bom')
 if b:S['bom']=dict(machine=b['machine'],steel=b['bom']['steel']['cart_kg'],al=b['bom']['al']['cart_kg'])
 json.dump(S,open(f'{D}/summary.json','w'),indent=1,default=float);print('\nsaved',f'{D}/summary.json')
if __name__=='__main__':main()
