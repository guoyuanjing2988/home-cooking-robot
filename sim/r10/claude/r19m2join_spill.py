"""R19 #42 (R19_M2JOIN.md): r19spill_cycle.py (#41, the short-push stir cycle) for a mount option, with its base library
and output paths selectable (used for the smoke runs on not-yet-adopted stir libraries). New file; extends r19m2_spill.py.
Like r19m2_spill.py it imports r19stir2_join first (argv as r19spill_cycle.std gives it) and adds the mount option's
spatula chain / hub roadmap to its SPAT / HUBS tables, then imports r19spill_cycle.py unchanged and, if given, replaces
its module paths:
 BASEFILE=<lib json>  for BASE  (default results/r19/stir/lib_stir_cycle_<arm>.json)
 SPILLOUT=<dir>       for OUT   (default results/r19/stir/spill/cycle_<arm>_short01_u06)
 SPILLLIB=<file>      for LIBN  (default results/r19/stir/lib_stir_cycle_<arm>_short01_u06_j8000.json)
The patches are at module level, so the spawned pool workers (which re-run this file as __mp_main__) get them too.
python r19m2join_spill.py works|returns|cert|std|law|lib|report ARM=<arm> SPATCHAIN=<json> [HUBSFILE=..] [BASEFILE=..]
       [SPILLOUT=..] [SPILLLIB=..] [PART=new|old] [W=..] [WORKERS=16]"""
import sys
sys.path.insert(0,'.')
KV=dict(a.split('=',1) for a in sys.argv[2:] if '=' in a)
sv=sys.argv;sys.argv=['r19stir2_join.py','cycle',f"ARM={KV['ARM']}",f"WORKERS={KV.get('WORKERS',16)}"]
import r19stir2_join as JN
sys.argv=sv
JN.SPAT[KV['ARM']]=KV['SPATCHAIN']
if 'HUBSFILE' in KV:JN.HUBS[KV['ARM']]=KV['HUBSFILE']
import r19spill_cycle as SC
if 'BASEFILE' in KV:SC.BASE=KV['BASEFILE']
if 'SPILLOUT' in KV:SC.OUT=KV['SPILLOUT']
if 'SPILLLIB' in KV:SC.LIBN=KV['SPILLLIB']
if __name__=='__main__':
 {'works':SC.works,'returns':SC.returns,'cert':SC.cert,'std':SC.std,'law':SC.law,'lib':SC.lib,'report':SC.report}[sys.argv[1]]()
