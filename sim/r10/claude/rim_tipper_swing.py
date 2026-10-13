"""Issue #34 (Mac 2026-10-13, new file): the holder's cup at intermediate tip angles (the swing between loaded 0 and poured
120 deg) replayed against the stir cycle and the cup / bowl pour paths with the unchanged checker (full, every state).
python rim_tipper_swing.py HOLDER=az,gap,dz [ANGLES=30,60,90] [TAG=..] -> results/mac/rim_tipper_swing_<TAG>.json"""
import sys,json,runpy
import r34holder
KV=dict(a.split('=',1) for a in sys.argv[1:]);out={}
for a in [float(x) for x in KV.get('ANGLES','30,60,90').split(',')]:
 r34holder.TIPDEG=a
 g=runpy.run_path('rim_tipper_confirm.py',init_globals=None,run_name='__swing__') if False else None
 sys.argv=['rim_tipper_confirm.py','HOLDER='+KV['HOLDER'],'TAG=swing%d_%s'%(a,KV.get('TAG','x'))]
 runpy.run_path('rim_tipper_confirm.py',run_name='__main__')
 r=json.load(open('results/mac/rim_tipper_confirm_swing%d_%s.json'%(a,KV.get('TAG','x'))))
 out[str(a)]={k:dict(states=v['states'],steps_with_hits=v['steps_with_hits'],holder_hits=v['holder_hits']) for k,v in r['results'].items() if k.endswith('_tipped')}
 out[str(a)]['ok']=r['ok'];print('angle',a,'ok',r['ok'],flush=True)
json.dump(dict(holder=KV['HOLDER'],angles=out),open('results/mac/rim_tipper_swing_%s.json'%KV.get('TAG','x'),'w'),indent=1)
