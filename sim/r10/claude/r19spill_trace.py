"""R19 #41: per-piece trajectories of the stir physics. New file; r19stir2_phys.py is NOT edited.

The run is r19stir2_phys.py itself (its source is compiled and executed unchanged, with ONE path replacement:
OUTD 'results/r19/stir/phys' -> 'results/r19/stir/spill', so its result json and its checkpoints land here and the
#40 files are not overwritten). The instrumentation is a wrapper around mujoco.mj_step that, AFTER the original step,
reads (never writes) the MuJoCo state every REC_EVERY steps (default 10 = 10 ms) and records:
 t, the 90 food positions and linear velocities (freejoint qvel, world frame), which food touches a spatula geom,
 the spatula body pose and velocity (free body on the compliant weld) and the mocap target pose.
Reading the state does not change the integration: the traced run's metrics must equal the stored #40 run of the
same seed and driver (checked by r19spill_ana.py repro).
Arm runs: when LAWNPZ= is not given, the #40 default law results/r19/stir/phys/fromrest_<arm>.npz is passed
explicitly (it would otherwise be looked up in the new OUTD).
python r19spill_trace.py <r19stir2_phys.py options> [REC_EVERY=10]
  -> results/r19/stir/spill/stir2_<TAG>.json (the run's own result), trace_<TAG>_<chunk start ms>.npz (one per
     command; STOP= / RESUME=1 chunking as r19stir2_phys.py)"""
import sys,os,numpy as np,mujoco
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
OUTD='results/r19/stir/spill';os.makedirs(OUTD,exist_ok=True)
if KV.get('DRIVER')=='arm' and 'LAWNPZ' not in KV:
 arm=KV.get('ARM','ur5e_enc2_pgc');sys.argv.append(f'LAWNPZ=results/r19/stir/phys/fromrest_{arm}.npz')
EVERY=int(KV.get('REC_EVERY',10))
src=open('r19stir2_phys.py',encoding='utf-8').read();old="OUTD='results/r19/stir/phys'"
assert src.count(old)==1;src=src.replace(old,f"OUTD='{OUTD}'")
REC=dict(t=[],fp=[],fv=[],fc=[],sp=[],sq=[],sv=[],mp=[],mq=[]);_S={}
_step=mujoco.mj_step
def _setup(m):
 FB=[];k=0
 while True:
  try:FB.append(m.body(f'f{k}').id);k+=1
  except KeyError:break
 FB=np.array(FB);sb=m.body('spatula').id;fadr=np.array([m.jnt_dofadr[m.body_jntadr[b]] for b in FB]);sadr=m.jnt_dofadr[m.body_jntadr[sb]]
 gmap=np.full(m.ngeom,-1);gmap[[m.geom(f'f{i}_g').id for i in range(len(FB))]]=np.arange(len(FB))
 spg=np.zeros(m.ngeom,bool);spg[[m.geom(f'blade{i}').id for i in range(5)]+[m.geom('handle').id]]=True
 _S.update(m=m,FB=FB,sb=sb,fadr=fadr,sadr=sadr,gmap=gmap,spg=spg,n=0)
def step(m,d,*a,**k):
 _step(m,d,*a,**k)
 if not _S or _S['m'] is not m:_setup(m)
 _S['n']+=1
 if _S['n']%EVERY:return
 FB=_S['FB'];R=REC;R['t'].append(d.time);R['fp'].append(d.xpos[FB].astype(np.float32));R['fv'].append(d.qvel[_S['fadr'][:,None]+np.arange(3)].astype(np.float32))
 c=np.zeros(len(FB),bool)
 if d.ncon:
  g=d.contact.geom[:d.ncon];gm=_S['gmap'];sp=_S['spg']
  a_=g[sp[g[:,1]]&(gm[g[:,0]]>=0),0];b_=g[sp[g[:,0]]&(gm[g[:,1]]>=0),1];c[gm[a_]]=True;c[gm[b_]]=True
 R['fc'].append(c);R['sp'].append(d.xpos[_S['sb']].copy());R['sq'].append(d.xquat[_S['sb']].copy());R['sv'].append(d.qvel[_S['sadr']:_S['sadr']+6].copy())
 R['mp'].append(d.mocap_pos[0].copy());R['mq'].append(d.mocap_quat[0].copy())
mujoco.mj_step=step
def save(g):
 if not REC['t']:return
 tag=g.get('TAG','x');fn=f"{OUTD}/trace_{tag}_{int(round(REC['t'][0]*1000)):05d}.npz"
 np.savez_compressed(fn,**{k:np.array(v) for k,v in REC.items()},every=EVERY,seed=int(g.get('SEED',-1)));print('trace',fn,len(REC['t']),'samples',flush=True)
G={'__name__':'__main__','__file__':os.path.abspath('r19stir2_phys.py')}
try:exec(compile(src,os.path.abspath('r19stir2_phys.py'),'exec'),G)
except SystemExit as e:
 save(G);raise
save(G)
