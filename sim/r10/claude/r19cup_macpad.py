"""R19 #5 cross-check (new file): are the 6 stored, checked cooking chains (results/r17/chain_*) clear of the
Mac session's seasoning-cup pad? Geometry from renders/mac/cup_pour_report.md only (no Mac code used): a 60 mm
disc pad 10 mm thick under a 60 x 70 mm cup whose bottom centre is at (0.45, 0.30, 1.085), on a 24 mm post from the
counter (the report says the real hanger from the cabinet is not modelled; the post is its stand-in). Fast checker
(full=False) on every stored state, as r19cup_screen.py MODE=replay, plus the least mj_geomDistance.
python r19cup_macpad.py > results/r19/cups/macpad_replay.txt"""
import sys,json;sys.path.insert(0,'.')
import numpy as np,mujoco,xml.etree.ElementTree as E
import kitchen15 as K15,kitchen16 as K,kitchen17 as K17,kitchen19seas as S
from scene import fmt
from checker import Checker
P=np.array([.45,.30,1.085])
def addpad(tree):
 w=tree.find('worldbody')
 E.SubElement(w,'geom',name='mac_pad',type='cylinder',pos=fmt(P-[0,0,.005]),size=fmt([.03,.005]),contype='1',conaffinity='2',mass='.000001')
 h=P[2]-.01-.85;E.SubElement(w,'geom',name='mac_post',type='cylinder',pos=fmt([P[0],P[1],.85+h/2]),size=fmt([.012,h/2]),contype='1',conaffinity='2',mass='.000001')
 E.SubElement(w,'geom',name='mac_cup',type='cylinder',pos=fmt(P+[0,0,.035]),size=fmt([.03,.035]),contype='1',conaffinity='2',mass='.000001')
CH=dict(wok_plate_rinse='wok_s-1_final',wok_plate2_rinse='wok_s-1_r18plate2b',faucet_open='lever_s+1_final',lid_off_to_rack='lid_s-1_final',spider_pot_to_plate='spider_s+1_final',spatula_fetch='spatula_s-1_r18roll-1.15_.30')
for n,f in CH.items():
 r=json.load(open(f'results/r17/chain_{f}.json'));S.setup_kitchen()
 for k,v in r.get('tool_xy',{}).items():
  if k!='spatula':K.TOOL_XY[k]=tuple(v)
 if r['obj']=='wok':K17.set_wok_tilt(r.get('wok_tilt',0.))
 ex={'r17_plate2':[.43,K15.PLATE['c'][1],K15.PLATE['c'][2]]} if 'plate2' in n else {}
 tree,meta=S.build_tree({**r.get('scene',{}),**ex,'r16_tools':{'ladle':None},**K17.held_cfg(r['obj'],r['grasp_sense'])});addpad(tree);ch=Checker(tree,meta);m,d=ch.m,ch.d
 st=[ch.gnames.index(x) for x in ('mac_pad','mac_post','mac_cup')];mv=[g for g in range(m.ngeom) if (ch.robot[g] or ch.held[g]) and m.geom_type[g]!=0];ft=np.zeros(6)
 hits=0;first=None;best=(1e9,None)
 for i,q in enumerate(r['play']):
  c=ch.check(np.array(q),full=False,mass=0.);hs=[h for h in c['hits'] if any(x.startswith('mac_') for x in h['pair'])]
  if hs:
   hits+=1
   if first is None:first=(i,hs[0]['pair'],hs[0].get('real_gap_mm'))
  for a in mv:
   for b in st:
    if np.linalg.norm(d.geom_xpos[a]-d.geom_xpos[b])-m.geom_rbound[a]-m.geom_rbound[b]>.1:continue
    dd=mujoco.mj_geomDistance(m,d,a,b,.1,ft)
    if dd<best[0]:best=(dd,(ch.gnames[a],ch.gnames[b]))
 print(n,len(r['play']),'states, hit states',hits,'first',first,'min dist mm',round(best[0]*1000,1),best[1],flush=True)
