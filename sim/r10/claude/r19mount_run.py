"""R19 #42: run a planning runner UNCHANGED (r17chain.py, r19pot_chain.py, r19prepchain.py, r19fr5prep_actions.py, ...)
with its result written to results/r19/mount/<the runner's own file name> instead of the runner's folder, never over an
existing file. New file. Only scene.save (which every one of these runners writes its chain with) is wrapped; the runner
is executed from its file as __main__ with the remaining arguments.
python r19mount_run.py RUNNER=<runner.py> <the runner's arguments>   (e.g. RUNNER=r19pot_chain.py ACT=lid ... ARM=fr5_j6_pgc_m1)"""
import sys,os,runpy
sys.path.insert(0,'.')
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
RUNNER=KV['RUNNER'];sys.argv=[RUNNER]+[a for a in sys.argv[1:] if not a.startswith('RUNNER=')]
import scene
_save=scene.save
def save(name,value):
 out='results/r19/mount/'+os.path.basename(str(name))
 assert not os.path.exists(scene.H/out),('exists, not overwritten',out)
 if isinstance(value,dict):value=dict(value,r19mount_run=dict(runner=RUNNER,argv=sys.argv[1:],runner_path=str(name)))
 r=_save(out,value);print('r19mount_run: written',out,flush=True);return r
scene.save=save
runpy.run_path(RUNNER,run_name='__main__')
