"""R19 #36: default / existing arm options unchanged by the arms.py edit (new file).
Builds the compiled scene XML (md5) and one full check of a mid-path state for several arm options, with either the
current arms.py or its backup arms.py.bak_r19cable loaded as the module 'arms' (OLD=1). Run twice and compare.
python r19cable_md5.py [OLD=1] -> results/r19/cable/md5_<old|new>.json"""
import sys,os,json,hashlib,importlib.util
sys.path.insert(0,'.')
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
if KV.get('OLD')=='1':
 import importlib.machinery;spec=importlib.util.spec_from_loader('arms',importlib.machinery.SourceFileLoader('arms',os.path.abspath('arms.py.bak_r19cable')));mod=importlib.util.module_from_spec(spec);sys.modules['arms']=mod;spec.loader.exec_module(mod)
import numpy as np,xml.etree.ElementTree as E
import arms,chain
from scene import build
from checker import Checker
import kitchen16 as K,kitchen17 as K17
ARMS_=('ur5e','ur5e_enc','ur5e_enc2','ur5e_enc2_pgc','fr5','fr5_j6','fr5_pgc','fr5_j6_pgc','fr5_pgc_sp20','fr5_j6_pgc_sp20','cs66','cs66_pgc')   # every option that existed before R19 #36
CH={'lid':'results/r17/chain_lid_s-1_final_ur5e_enc2_pgc.json','wok':'results/r17/chain_wok_s-1_final_py.15_ur5e_enc2_pgc.json'}
out={}
K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.)
for a in ARMS_:
 os.environ['ARM']=a
 for key,f in CH.items():
  r=json.load(open(f));cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None},**K17.held_cfg(r['obj'],r['grasp_sense']))
  tree,meta=build(cfg,None);xml=E.tostring(tree.getroot(),encoding='unicode');md=hashlib.md5(xml.encode()).hexdigest()
  ch=Checker(tree,meta);q=np.array(r['play'][len(r['play'])//2],float);c=ch.check(q,full=True,mass=0.)
  out[f'{a}/{key}']=dict(xml_md5=md,ngeom=ch.m.ngeom,check_ok=bool(c['ok']),hits=len(c['hits']),clearance={k:round(v['reserve_mm'],6) for k,v in c['clearance'].items()},envelope=arms.envelope_file(0,a))
  print(a,key,md,ch.m.ngeom,c['ok'],out[f'{a}/{key}']['clearance'],flush=True)
os.makedirs('results/r19/cable',exist_ok=True)
fn=f"results/r19/cable/md5_{'old' if KV.get('OLD')=='1' else 'new'}.json";json.dump(out,open(fn,'w'),indent=1);print(fn)
