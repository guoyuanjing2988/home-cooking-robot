"""R19 #42: the stir entry / exit (r19stir2_join.py) for a mount option. New file. r19stir2_join.py is executed unchanged from
its source; its two per-arm file tables, SPAT (the checked spatula chain whose end is the stroke start) and HUBS (the
hubs.json whose 2pi relabels it applies), have entries only for ur5e_enc2_pgc / fr5_j6_pgc_sp20, so this wrapper adds the
mount option's files before it runs. Everything else (stir library lib_stir_cycle_<arm>.json, layer, checker, time law,
outputs results/r19/stir/join_<arm>/ and lib_stir_join_<arm>.json) is r19stir2_join.py's, keyed by ARM=.
python r19mount_stirjoin.py join ARM=<mount option> SPATCHAIN=<re-certified spatula chain json> [HUBSFILE=<hubs.json>]
       [WORKERS=24] [JERK=<deg/s^3>]"""
import sys,os
sys.path.insert(0,'.')
KV=dict(a.split('=',1) for a in sys.argv[2:] if '=' in a)
_s=open('r19stir2_join.py',encoding='utf-8').read();_a="CYC=f'results/r19/stir/lib_stir_cycle_{ARM}.json'"
assert _s.count(_a)==1,'r19stir2_join.py changed'
_s=_s.replace(_a,"SPAT.update({ARM:KV['SPATCHAIN']} if 'SPATCHAIN' in KV else {})\nHUBS.update({ARM:KV['HUBSFILE']} if 'HUBSFILE' in KV else {})\n"+_a)
exec(compile(_s,'r19stir2_join.py','exec'))
