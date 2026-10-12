"""Re-run an R16 whole-action chain (r16chain.py) in the R17 tool layout (kitchen17: spider moved,
spatula and ladle off the rest, pour drum swung away). Every step is checked again in the new scene.
python r17r16recheck.py ACT=lid|plate_in [TAG=..] -> results/r16/chain_<ACT>_r17layout.json"""
import sys,runpy,chain
import kitchen16 as K
import kitchen17 as K17   # R17 counter end: spider moved, spatula and ladle off the rest
_orig=chain.chain_cfg
def cfg17(*a,**k):
 k=dict(k);t=dict(k.get('r16_tools') or {});t.update(K17.R17_TOOLS_OFF);k['r16_tools']=t;k['r15_drum_taken']=True;return _orig(*a,**k)
chain.chain_cfg=cfg17
sys.argv=['r16chain.py']+[a for a in sys.argv[1:] if not a.startswith('TAG=')]+['TAG=r17layout']
runpy.run_path('r16chain.py',run_name='__main__')
