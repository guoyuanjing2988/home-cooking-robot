"""R19 #12: adopt a stored UR5e chain for an arm option when it re-checks clean with that arm.

A stored chain (results/r17/chain_*.json, planned with the UR5e) is written as chain_<act>_..._<arm>.json, so that
r19hub.py and the meal tools can use it under ARM=<arm>, only when
 1. its play passes the <= 4 mm re-check of r19enc_check.py with that arm: results/r19/<dir>/<set>[_py<y>].json, column
    <arm>: 0 hit states, joint ranges ok, and the re-check was made on exactly this play (stored-state count and
    md5 of the play are compared);
 2. its grasp approaches / release retreats (approach_qs) pass too: each is cut to <= 4 mm (point bound, as the
    re-check) and every state goes through Checker.check(full=True) in r17chain's own empty-gripper scene for that
    keyframe (r17chain.py is executed up to its main loop with the chain's original options, nothing is planned).
The adopted file is the stored chain unchanged, plus: "arm": <arm>, "adopted_from": <source file>, "adopted":
{certificate}; with PY=<y> also "plate_y" and the name gets _py<y> before the arm suffix (the layout moved).
Nothing is overwritten: an existing target is renamed to <target>.replaced_<n>.json first.

python r19enc_adopt.py ARM=<arm> SETS=lever,spatula,lid,spider [PY=.15]
python r19enc_adopt.py one SET=<set> ARM=<arm> [PY=.15]   (one set; the main command runs this in a subprocess)"""
import sys,os,json,hashlib,subprocess
sys.path.insert(0,'.')
OPTS={   # the UR5e finals' r17chain options (R19_ARM_SWAP.md 8)
 'lever':('results/r17/chain_lever_s+1_final.json','ACT=lever SIGN=1 SPX=1.52 SPY=.36 TRIES=8 TAG=final'),
 'lid':('results/r17/chain_lid_s-1_final.json','ACT=lid SIGN=-1 SPX=1.52 SPY=.36 TRIES=16 TAG=final'),
 'spider':('results/r17/chain_spider_s+1_final.json','ACT=spider SIGN=1 SPX=1.52 SPY=.36 TRIES=12 TAG=final'),
 'spatula':('results/r17/chain_spatula_s-1_r18roll-1.15_.30.json','ACT=spatula SIGN=-1 SPATREST=-1.15,.30 SPATELEV=8 SPATROLL=180 SPX=1.52 SPY=.36 TRIES=16 TAG=r18roll-1.15_.30'),
 'wok':('results/r17/chain_wok_s-1_final.json','ACT=wok SIGN=-1 GTILT=25 L2X=-.25 SINKC=-1.06 SPX=1.52 SPY=.36 TRIES=8 TAG=final'),
 'wok_plate2b':('results/r17/chain_wok_s-1_r18plate2b.json','ACT=wok SIGN=-1 GTILT=25 L2X=-.25 SINKC=-1.06 SPX=1.52 SPY=.36 PX=.17 PLATE2=.43 TRIES=16 TAG=r18plate2b')}
def md5_play(r):return hashlib.md5(json.dumps(r['play']).encode()).hexdigest()
def one(KV):
 import numpy as np
 key,arm=KV['SET'],KV['ARM'];src,opts=OPTS[key];py=KV.get('PY');sfx=KV.get('SRCSFX','');ur_src=src;src=src[:-5]+sfx+'.json';r=json.load(open(src))   # R19 #2: SRCSFX=_<arm> adopts that arm's stored chain (e.g. _fr5_j6 -> fr5_j6_pgc)
 import arms
 rdir='results/r19/'+(arm[len('ur5e_'):] if arm.startswith('ur5e_') else arm);rc_fn=f"{rdir}/{key}{sfx}{'_py'+py if py else ''}.json"
 cert=dict(arm=arm,play_recheck=rc_fn)
 if not os.path.exists(rc_fn):return dict(ok=False,why='no re-check '+rc_fn+' (run r19enc_check.py recheck SET=%s NEW=%s%s)'%(key,arm,' PY='+py if py else ''))
 rc=json.load(open(rc_fn));p=rc['paths'][key][arm]
 if rc['paths'][key]['stored_states']!=len(r['play']):return dict(ok=False,why='re-check was made on another play')
 if not p['ok'] or p['hit_states'] or p['out_of_range_states']:return dict(ok=False,why='play re-check not clean: %d hit states %s'%(p['hit_states'],list(p['hit_pairs'])[:3]))
 cert.update(play_states=rc['paths'][key]['states'],play_max_step_bound_mm=rc['paths'][key]['max_step_bound_mm'],play_hit_states=0,play_min_reserve_by_category=p['min_reserve_by_category'])
 # approaches in r17chain's own empty-gripper scenes
 sys.argv=['r17chain.py']+opts.split()+(['PY='+py] if py else [])+['ARM='+arm]
 s=open('r17chain.py',encoding='utf-8').read();g={'__name__':'r17chain_defs','__file__':os.path.abspath('r17chain.py')}
 exec(compile(s[:s.index('t0=time.monotonic();pieces={}')],'r17chain.py','exec'),g)
 assert g['ARM']==arm
 import r19smooth as S
 apps=[]
 for (k,world),a,qs in zip(g['GR'],r['approaches'],r['approach_qs']):
  if a.get('kf')!=k or not qs:return dict(ok=False,why=f'approach for kf {k} missing in the stored chain')
  c=g['model'](world);QS,src_,sp=S.sample_poly(np.array(qs,float),S.FastBound(c));hit=[];res=[]
  for q in QS:
   x=c.check(np.asarray(q),full=True,mass=0.)
   if x['hits'] or not x['ranges']:hit.append([h['pair'] for h in x['hits']][:2])
   res.append(min([v['reserve_mm'] for cc,v in x['clearance'].items() if cc!='self'],default=1e9))
  apps.append(dict(kf=k,states=len(QS),max_step_bound_mm=round(sp*1e3,3),hit_states=len(hit),hits=hit[:3],min_env_reserve_mm=round(min(res),2)))
  if hit:return dict(ok=False,why=f'approach kf {k}: {len(hit)} hit states {hit[:2]}',approaches=apps)
 cert.update(approaches=apps,source_md5_play=md5_play(r))
 base=ur_src[:-5]+(f'_py{py}' if py else '');dst=base+arms.tag(arm)+'.json'
 out=dict(r,arm=arm,adopted_from=src,adopted=cert,**({'plate_y':float(py)} if py else {}))
 if os.path.exists(dst):
  n=1
  while os.path.exists(dst[:-5]+f'.replaced_{n}.json'):n+=1
  os.rename(dst,dst[:-5]+f'.replaced_{n}.json');cert['replaced']=dst[:-5]+f'.replaced_{n}.json'
 json.dump(out,open(dst,'w'));return dict(ok=True,file=dst,certificate=cert)
if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='one':
  KV=dict(a.split('=',1) for a in sys.argv[2:]);print('RESULT '+json.dumps(one(KV),default=float))
 else:
  KV=dict(a.split('=',1) for a in sys.argv[1:]);allres={}
  for key in KV['SETS'].split(','):
   cmd=[sys.executable,'r19enc_adopt.py','one','SET='+key,'ARM='+KV['ARM']]+(['PY='+KV['PY']] if 'PY' in KV else [])+(['SRCSFX='+KV['SRCSFX']] if 'SRCSFX' in KV else [])
   o=subprocess.run(cmd,capture_output=True,text=True);line=[l for l in o.stdout.splitlines() if l.startswith('RESULT ')]
   allres[key]=json.loads(line[-1][7:]) if line else dict(ok=False,why='crashed: '+o.stderr[-400:])
   print(key,json.dumps({k:v for k,v in allres[key].items() if k!='certificate'}),flush=True)
  fn=f"results/r19/{KV['ARM'][len('ur5e_'):] if KV['ARM'].startswith('ur5e_') else KV['ARM']}/adopt{KV.get('SRCSFX','')}{'_py'+KV['PY'] if 'PY' in KV else ''}.json";json.dump(allres,open(fn,'w'),indent=1,default=float);print(fn)
