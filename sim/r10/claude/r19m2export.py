"""R19 #42 / #6: r19export.py for the adopted m2 sets (new file; r19export.py is executed from its source with the
replacements below, nothing shared is edited). Commands and outputs are r19export.py's (export / recheck / report).
 1. Chains without r19enc's 'adopted' block (the m2 cooking chains in results/r19/mount/) take their pot-zone certificate
    results/r19/mount/check_<chain>_rack_sp1.56_.20.json (r19pot_check.py) and a scene spec of type 'pot':
    r19pot_check.ctx(file, 'play' | 'app<k>') with RACK=keyed, spider rest (1.56, .20), PY=.15, i.e. the scene of that
    certificate; the play tolerance is then uniform from the certificate's minimum reserve (as for the prep sets).
 2. The kitchen19pot layer (keyed rack, spider rest 1.56, .20) is installed before a hub scene is built, as
    r19fr5_hub.py did when the m2 edges were planned and checked.
 3. ARMX=1: every scene (export fit checks and the dense re-check) is built with the m2 cable option
    <base>c_yp_a-45_m2tc (R19_M2CABLE.md) instead of the file's bare m2 arm, so the re-check certifies the cable too.
 5. An m2 prep set in results/r19/mount/ whose certificate is <file>_verify4mm_pot.json (the T2L cradle sets: fold,
    unfold, stgwok, ct2s) is re-checked with r19prep5_verify, the verifier of that certificate (r19export picks the
    verifier by folder, and the m2 sets all live in results/r19/mount/).
 4. ROADMAP: both m2 arms relabel their chains by their own hub roadmap (results/r19/fr5/hub_py.15_<arm>/hubs.json), as
    r19export.py does for ur5e_enc2_pgc, so the exported chains and hub edges carry the same 2pi labels.
python r19m2export.py export FILE=<m2 result json> ARMX=1 [r19export.py options]
python r19m2export.py recheck NAME=<name>[,..] ARMX=1 [WORKERS=16]"""
import sys,os
sys.path.insert(0,'.')
KV=dict(a.split('=',1) for a in sys.argv[2:] if '=' in a)
M2=('ur5e_enc2_pgc_m2','fr5_j6_pgc_m2');CABLE='c_yp_a-45_m2tc'
def armx(a):return a+CABLE if KV.get('ARMX')=='1' and a in M2 else a
def pot_spec_cert(f,r,arm):
 """the pot-zone certificate of an m2 chain -> (cert file, cert, spec, certsum)"""
 import json
 cf='results/r19/mount/check_'+os.path.basename(f)[:-5]+'_rack_sp1.56_.20.json';cert=json.load(open(cf))
 assert os.path.normpath(cert['file'])==os.path.normpath(f),('certificate of another file',cf)
 pl=cert['parts']['play'];app={k:v for k,v in cert['parts'].items() if k!='play'}
 env=pl.get('min_env_reserve_mm');slf=(pl['min_reserve_by_category'].get('self') or {}).get('reserve_mm')
 spec=dict(type='pot',arm=arm,file=f.replace('\\','/'),part='play')
 cs=dict(ok=cert['ok'],hit_states=pl['hit_states'],out_of_range_states=pl['out_of_range'],min_env_reserve_mm=env,min_self_reserve_mm=slf)
 certsum=dict(file=cf,checker='r19pot_check.py: Checker.check(full=True), MuJoCo contacts + GJK lower-bound certificate, 10 mm robot-environment, 5 mm gripper/held-environment, self, joint ranges; pot-zone layout RACK=keyed, spider rest (1.56, .20), PY=.15',
  rule='stored play 2pi-unwrapped, joint-linear between stored states, cut so that consecutive states are <= 4 mm apart (r19smooth.sample_poly)',
  states=pl['states'],max_step_bound_mm=pl['max_step_bound_mm'],ok=cert['ok'],hit_states=pl['hit_states'],out_of_range_states=pl['out_of_range'],
  min_env_reserve_mm=env,min_self_reserve_mm=slf,approaches={k:dict(states=v['states'],hit_states=v['hit_states'],min_env_reserve_mm=v.get('min_env_reserve_mm')) for k,v in app.items()})
 return cf,cert,spec,cs,certsum
def pot_scene(spec):
 """scene type 'pot' (point 1)"""
 import numpy as np,r19pot_check as RP,kitchen19pot as P
 RP.KV.update(RACK='keyed',SPX='1.56',SPY='.20',PY='.15');P.install(rack='keyed')
 part=spec['part'] if isinstance(spec['part'],str) else 'app%d'%spec['part'][1]
 ch=RP.ctx(spec['file'],part)
 def cm(Qs,ch=ch):
  out=[]
  for q in Qs:
   c=ch.check(np.asarray(q),full=True,mass=0.);cl=c['clearance'];env=[v['reserve_mm'] for k,v in cl.items() if k!='self']
   out.append(dict(bad=bool(c['hits']) or not c['ranges'],hits=[h['pair'] for h in c['hits']][:2],ranges=bool(c['ranges']),env=min(env) if env else None,self=cl['self']['reserve_mm'] if 'self' in cl else None,plume=None))
  return out
 return dict(ch=ch,check_many=cm)
def source():
 s=open('r19export.py',encoding='utf-8').read()
 R=[("ROADMAP={'ur5e_enc2_pgc':('results/r19/hub_py.15_ur5e_enc2_pgc/hubs.json',.15)}",
     "ROADMAP={'ur5e_enc2_pgc':('results/r19/hub_py.15_ur5e_enc2_pgc/hubs.json',.15)};import r19m2export as _M2\n"
     "for _a in _M2.M2:ROADMAP[_a]=ROADMAP[_a+_M2.CABLE]=('results/r19/fr5/hub_py.15_'+_a+'/hubs.json',.15)"),
    (" arm=r['arm'];info.update(arm=arm)\n if kind=='chain':\n",
     " arm=_M2.armx(r['arm']);info.update(arm=arm)\n if kind=='chain' and 'adopted' not in r:cf,cert,spec,cs,certsum=_M2.pot_spec_cert(f,r,arm);key=py=P=None\n elif kind=='chain':\n"),
    (" if kind=='chain' and rep['reproduced']:"," if kind=='chain' and P is not None and rep['reproduced']:"),
    ("  if kind=='chain':return dict(type='chain_app',arm=arm,key=key,py=py,kf=r['approaches'][i]['kf'])",
     "  if kind=='chain' and spec['type']=='pot':return dict(spec,part=['app',i])\n  if kind=='chain':return dict(type='chain_app',arm=arm,key=key,py=py,kf=r['approaches'][i]['kf'])"),
    (" t=spec['type'];arm=spec['arm']\n"," t=spec['type'];arm=_M2.armx(spec['arm'])\n if t=='pot':\n  os.environ['ARM']=arm;M=_M2.pot_scene(dict(spec,arm=arm));M['md5']=hashlib.md5(M['ch'].xml.encode()).hexdigest();_SC[key]=M;return M\n"),
    (r"  ver='r19prep5_verify' if '/prep5/' in f.replace('\\','/') else",r"  ver='r19prep5_verify' if '/prep5/' in f.replace('\\','/') or ('/mount/' in f.replace('\\','/') and os.path.exists(f[:-5]+'_verify4mm_pot.json')) else"),
    ("  sys.argv=['r19hub.py','edge']","  import kitchen19pot as _P;_P.install(rack='keyed',spider=('1.56','.20'))\n  sys.argv=['r19hub.py','edge']")]
 for a,b in R:
  assert s.count(a)==1,('r19export.py changed:',a[:60]);s=s.replace(a,b)
 return s
# in this module's own namespace, so the pool workers (which re-run this file as __mp_main__) define the same functions;
# r19export's command block runs only under __main__
if __name__ in ('__main__','__mp_main__'):
 exec(compile(source(),os.path.abspath('r19export.py'),'exec'),globals())
