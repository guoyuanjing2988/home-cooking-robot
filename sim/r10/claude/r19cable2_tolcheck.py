"""R19 #36 (cable, part 2): proof that the r19tol_core.py cable exclusion leaves the tolerance results unchanged (new file).

r19tol_core.Ev marked every R_tool geom except the palm and R_gripper_oem* as HELD, so the cable shapes R_pgc_cable* of the
*_pgcc options (r19cable.py) counted as part of the held object (grasp perturbations moved them with it). The fix
(r19tol_core.py, backup r19tol_core.py.bak_r19cable2) excludes R_pgc_cable* from the held set (the cable is part of the
robot) and lets a cable option use the stored paths of its base option (tagged() / hubdir(); the cable does not change
the kinematics). This script re-runs stored tolerance tasks with the patched core, unchanged r19tol_replay._run, into
results/r19/cable/tolcheck/<arm>[_py<y>]/ (never into the stored folder), and compares every field with the stored file
(timing fields excluded): 'identical' means the JSON values are equal after dropping elapsed_s / nominal_s / nominal_cached.
With a cable option there is no stored file; it reports the held / cable geom counts and, if REF=<arm> is given, compares
with that arm's stored result (the cable must not change it unless the cable itself binds).
python r19cable2_tolcheck.py ARM=<arm> [PY=.15] TASKS=play:lever/grasp-x,play:lever/cart-x,... [REF=<arm>]
 -> results/r19/cable/tolcheck/<arm>[_py<y>]/scene_*.json and compare.json"""
import sys,os,json,time
sys.path.insert(0,'.')
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
import r19tol_core as C
import r19tol_replay as R
STORED=C.OUT
def stored_dir(arm):
 sub=(arm if arm!='ur5e' else '')+(('_' if arm!='ur5e' else '')+'py'+C.PYARG if C.PYARG else '')
 return 'results/r19/tol'+('/'+sub if sub else '')
C.OUT='results/r19/cable/tolcheck/'+(C._SUB or 'ur5e')
SKIP={'elapsed_s','nominal_s','nominal_cached'}
def diff(a,b,path=''):
 if isinstance(a,dict) and isinstance(b,dict):
  out=[]
  for k in sorted(set(a)|set(b)):
   if k in SKIP:continue
   if k not in a or k not in b:out.append(f'{path}/{k}: only in {"new" if k in a else "stored"}');continue
   out+=diff(a[k],b[k],f'{path}/{k}')
  return out
 if isinstance(a,list) and isinstance(b,list):
  if len(a)!=len(b):return [f'{path}: length {len(a)} vs {len(b)}']
  out=[]
  for i,(x,y) in enumerate(zip(a,b)):out+=diff(x,y,f'{path}[{i}]')
  return out
 return [] if a==b else [f'{path}: {a!r} vs {b!r}']
def main():
 import mujoco
 res=dict(arm=C.ARM,py=C.PYARG,stored_dir=STORED,out_dir=C.OUT,path_arm=C._path_arm(C.ARM),tasks={})
 for t in KV['TASKS'].split(','):
  key,part=t.split('/');t0=time.monotonic()
  fn=R._run((key,part));new=json.load(open(fn))
  ch,_,_=C.build_scene(key);ev=C.Ev(ch);nm=ch.gnames
  rec=dict(file=fn,elapsed_s=round(time.monotonic()-t0,1),held_geoms=int(len(ev.hg)),cable_geoms=sum(n.startswith('R_pgc_cable') for n in nm),
   cable_in_held=sum(nm[g].startswith('R_pgc_cable') for g in ev.hg),path_file=new['info'].get('file'))
  for lab,d in (('stored',STORED),)+((('ref',stored_dir(KV['REF'])),) if 'REF' in KV else ()):
   f=f"{d}/scene_{key.replace(':','_')}__{part}.json"
   if os.path.exists(f):
    old=json.load(open(f));dd=diff(new,old);
    if lab=='ref':dd=[x for x in dd if not x.startswith(('/arm:','/info/file:'))]   # another arm option: its name differs by definition
    rec[lab]=dict(file=f,identical=not dd,n_diffs=len(dd),diffs=dd[:20])
   else:rec[lab]=dict(file=f,missing=True)
  res['tasks'][t]=rec;print(t,json.dumps({k:v for k,v in rec.items() if k!='file'})[:600],flush=True)
 os.makedirs(C.OUT,exist_ok=True);json.dump(res,open(f'{C.OUT}/compare.json','w'),indent=1);print('saved',f'{C.OUT}/compare.json')
if __name__=='__main__':main()
