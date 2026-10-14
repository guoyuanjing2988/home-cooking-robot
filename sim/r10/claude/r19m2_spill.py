"""R19 #42: r19spill_cycle.py for a mount option. New file. The 'std' stage of r19spill_cycle imports r19stir2_join, whose
per-arm tables SPAT (spatula chain) and HUBS (hubs.json) have entries only for ur5e_enc2_pgc / fr5_j6_pgc_sp20. This
wrapper imports r19stir2_join first, with the argv r19spill_cycle.std gives it, adds the mount option's files (the same
ones r19mount_stirjoin.py adds), then imports r19spill_cycle.py unchanged and runs the stage. The patch is at module
level so the spawned pool workers (which re-run this file as __mp_main__) get it too.
python r19m2_spill.py <stage> ARM=<mount option> SPATCHAIN=<spatula chain json> [HUBSFILE=<hubs.json>] [WORKERS=16]"""
import sys
sys.path.insert(0,'.')
KV=dict(a.split('=',1) for a in sys.argv[2:] if '=' in a)
sv=sys.argv;sys.argv=['r19stir2_join.py','cycle',f"ARM={KV['ARM']}",f"WORKERS={KV.get('WORKERS',16)}"]
import r19stir2_join as JN
sys.argv=sv
JN.SPAT[KV['ARM']]=KV['SPATCHAIN']
if 'HUBSFILE' in KV:JN.HUBS[KV['ARM']]=KV['HUBSFILE']
import r19spill_cycle as SC
if __name__=='__main__':
 {'std':SC.std,'lib':SC.lib,'report':SC.report}[sys.argv[1]]()
