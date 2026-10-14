"""R19 #42 (R19_M2JOIN.md): the stir entry / exit (r19stir2_join.py) for a mount option, with the stir library and the
output paths selectable. New file. Like r19mount_stirjoin.py (which it extends): r19stir2_join.py is executed unchanged
from its source except for these textual changes, each asserted to occur once:
 - SPAT / HUBS get the mount option's spatula chain (SPATCHAIN=) and hub roadmap (HUBSFILE=, optional);
 - CYCFILE=<lib json> replaces the stir library results/r19/stir/lib_stir_cycle_<arm>.json (default unchanged);
 - JOINOUT=<dir> / JOINLIB=<file> replace results/r19/stir/join_<arm> / lib_stir_join_<arm>.json (defaults unchanged).
The IK-branch rule (the self-motion must arrive exactly at H_stir0, else no join), the scenes, checker and time laws
are r19stir2_join's.
python r19m2join_join.py join ARM=<arm> SPATCHAIN=<json> [HUBSFILE=<hubs.json>] [CYCFILE=..] [JOINOUT=.. JOINLIB=..]
       [WORKERS=24] [JERK=<deg/s^3>]"""
import sys,os
sys.path.insert(0,'.')
KV=dict(a.split('=',1) for a in sys.argv[2:] if '=' in a)
_s=open('r19stir2_join.py',encoding='utf-8').read()
_R=[("OUT=f'results/r19/stir/join_{ARM}';LIBF=f'results/r19/stir/lib_stir_join_{ARM}.json'",
     "OUT=KV.get('JOINOUT',f'results/r19/stir/join_{ARM}');LIBF=KV.get('JOINLIB',f'results/r19/stir/lib_stir_join_{ARM}.json')"),
    ("CYC=f'results/r19/stir/lib_stir_cycle_{ARM}.json'",
     "SPAT.update({ARM:KV['SPATCHAIN']} if 'SPATCHAIN' in KV else {})\nHUBS.update({ARM:KV['HUBSFILE']} if 'HUBSFILE' in KV else {})\n"
     "CYC=KV.get('CYCFILE',f'results/r19/stir/lib_stir_cycle_{ARM}.json')")]
for a,b in _R:
 assert _s.count(a)==1,('r19stir2_join.py changed',a);_s=_s.replace(a,b)
exec(compile(_s,'r19stir2_join.py','exec'))
