"""R19 #42: every arm option that existed before this round is unchanged by the arms.py edit (new file; the method of
r19cable2_md5.py). Builds the scene XML (md5, geom count) and the envelope file name of each option, with either the current
arms.py or the backup arms.py.bak_r19mount loaded as 'arms' (OLD=1). The OLD run writes the option list; the NEW run checks
the same list. Scenes: the lid chain's held-object scene for every option, and the wok chain's for the options without a
cable plus the adopted cable options (as r19cable2_md5.py).
python r19mount_md5.py OLD=1 [PART=i/n]  then  python r19mount_md5.py [PART=i/n]  then  python r19mount_md5.py COMPARE=1
 -> results/r19/mount/md5_<old|new>[_i].json, md5_compare.json"""
import sys,os,json,glob,hashlib,importlib.util,importlib.machinery
sys.path.insert(0,'.')
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
D='results/r19/mount';LIST=D+'/md5_options.json'
if KV.get('COMPARE')=='1':
 load=lambda k:{kk:vv for f in sorted(glob.glob(f'{D}/md5_{k}*.json')) for kk,vv in json.load(open(f)).items()}
 old,new=load('old'),load('new');opts=json.load(open(LIST))
 diff=[k for k in old if old[k]!=new.get(k)];miss=[k for k in old if k not in new]
 out=dict(options=len(opts),scenes_old=len(old),scenes_new=len(new),identical=sum(old[k]==new.get(k) for k in old),different=diff,missing_in_new=miss)
 json.dump(out,open(D+'/md5_compare.json','w'),indent=1);print(json.dumps(out));sys.exit(0)
OLD=KV.get('OLD')=='1'
if OLD:
 spec=importlib.util.spec_from_loader('arms',importlib.machinery.SourceFileLoader('arms',os.path.abspath('arms.py.bak_r19mount')));mod=importlib.util.module_from_spec(spec);sys.modules['arms']=mod;spec.loader.exec_module(mod)
import xml.etree.ElementTree as E
import arms,chain
from scene import build
import kitchen16 as K,kitchen17 as K17
os.makedirs(D,exist_ok=True)
if OLD and not os.path.exists(LIST):json.dump(sorted(arms.ARMS),open(LIST,'w'))
OPTS=json.load(open(LIST))
i,n=map(int,KV.get('PART','0/1').split('/'));OPTS=OPTS[i::n]
CH={'lid':'results/r17/chain_lid_s-1_final_ur5e_enc2_pgc.json','wok':'results/r17/chain_wok_s-1_final_py.15_ur5e_enc2_pgc.json'}
K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.)
out={}
for a in OPTS:
 os.environ['ARM']=a
 for key,f in CH.items():
  if key=='wok' and arms.ARMS[a].get('cable') not in (None,'both_dn','yp_a-45'):continue
  r=json.load(open(f));cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None},**K17.held_cfg(r['obj'],r['grasp_sense']))
  tree,meta=build(cfg,None);xml=E.tostring(tree.getroot(),encoding='unicode')
  out[f'{a}/{key}']=dict(xml_md5=hashlib.md5(xml.encode()).hexdigest(),ngeom=xml.count('<geom '),envelope=arms.envelope_file(0,a))
 print(a,{k:v['xml_md5'][:8] for k,v in out.items() if k.startswith(a+'/')},flush=True)
fn=f"{D}/md5_{'old' if OLD else 'new'}{'_'+str(i) if n>1 else ''}.json";json.dump(out,open(fn,'w'),indent=1);print(fn,len(out))
