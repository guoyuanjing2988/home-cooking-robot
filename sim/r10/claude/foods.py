"""R13 food catalog, finger sets and grippers for the food-variety grasp bench.

Item fields (SI units): zh name; src = RoboCasa mesh (resized by foodmesh.make) or
prim = MuJoCo primitive; dims = world size when lying in the raw basket (x = the
width the jaws close across, y = long axis, z = height); kg; dmg = per-finger force
limit (damage / bruise / crack, N); mu = wet pad friction; cls = handling class.
Numbers marked est are placeholders until research/food_catalog_inputs.md is
merged (catalog values then carry its source keys)."""
import numpy as np
G=9.81
# ---------------- grippers ----------------
GRIPPERS={
 'PGC':dict(label='DH PGC-140-50',stroke=.050,Fmin=40.,Fmax=140.,M_allow=7.,ip='IP67'),
 'HE100':dict(label='Robotiq Hand-E 100 mm',stroke=.100,Fmin=20.,Fmax=185.,M_allow=None,ip='IP67'),
}
# ---------------- finger sets (fingers.dyn_parts parameters) ----------------
# fo = closed half gap at the pad datum; jaw range per finger q in [0, stroke/2]:
# grip width (datum to datum) = 2 (fo + q). P - D = how far the fingertip reaches
# past the item centre (top-down picks from a flat floor need P - D < height of centre).
_D=dict(c=.02,T=.008,tp=.004,profile='dual',e=.001,ks=1500.,travel=.006)
def make_set(label,w_lo,w_hi,tip=.012,rock=8.):
 """Finger set for grip widths [w_lo, w_hi] (approach clearance and e included in
 w_hi by the caller): closed half gap fo, housing face D behind the item centre
 (largest item radius + 6 mm), fingertip `tip` past the item centre, pad height H."""
 fo=(w_lo-.002)/2;D=max(.036,w_hi/2+.006);H=float(np.clip(.6*w_hi,.04,.09))
 return dict(_D,label=label,fo=fo,D=D,P=D+tip,H=H,w=round(.4*H,4),rock=rock)
def family(stroke,lo=.005,hi=.19,overlap=.016):
 """Sets covering lo..hi for a gripper stroke: each spans 2*(stroke/2 - e - 4 mm);
 neighbours overlap by 16 mm so round items near a set's closed gap (which need the
 soft centre's travel to build force) have a set where they sit mid-range."""
 span=2*(stroke/2-.001-.004);out=[];a=lo
 while not out or out[-1][1]<hi:out.append((a,a+span));a=a+span-overlap
 return out
SETS={}
for gr_,st in (('PGC',.05),('HE100',.10)):
 for i,(a,b) in enumerate(family(st)):
  n=('P1','P2','P3','P4','P5','P6','P7','P8')[i] if gr_=='PGC' else ('H1','H2','H3')[i]
  SETS[n]=dict(make_set(n,a,b,tip=.006 if i==0 else .012),gripper=gr_)
SETS['D']=dict(_D,label='R12 dual (P75)',P=.075,D=.045,H=.048,w=.019,fo=.016,gripper='PGC')
def width_range(s,gr='PGC'):
 d=SETS[s];return 2*d['fo'],2*(d['fo']+GRIPPERS[gr]['stroke']/2)
# ---------------- catalog ----------------
# Numbers from research/food_catalog_inputs.md (2026-10-11): dmg = settled per-finger
# limit (tag in dsrc: M measured, der derived, est estimate), fail = failure force,
# kg/dims = Chinese retail typical (estimates unless tagged), rng = size factors
# for the small / large variant. mu_d = design friction: the binding cook_ref rule
# (wet 0.15, SF 1.5) unless a lower value is known.
RC='objaverse/';AG='aigen_objs/'
def I(zh,dims,kg,dmg,dsrc,src=None,prim=None,fail=None,mu_d=.15,rng=(.85,1.15),cls='rigid',rgba=(.8,.5,.3,1),note=''):
 return dict(zh=zh,dims=list(dims),kg=kg,dmg=dmg,dsrc=dsrc,fail=fail,mu=.3,mu_d=mu_d,rng=rng,src=src,prim=prim,cls=cls,rgba=rgba,note=note)
ITEMS={
 'carrot':I('胡萝卜',(.035,.19,.035),.15,56.7,'M C1',RC+'carrot/carrot_2',fail=71.9,rng=(.75,1.25)),
 'potato':I('土豆',(.065,.10,.055),.20,40,'der',RC+'potato/potato_1',rng=(.8,1.2)),
 'daikon':I('白萝卜',(.075,.33,.075),1.0,40,'est',RC+'carrot/carrot_2',rng=(.8,1.2)),
 'ginger':I('生姜',(.045,.12,.035),.15,55,'est',AG+'ginger/ginger_0',fail=110),
 'garlic':I('蒜头',(.055,.055,.045),.05,20,'est',RC+'garlic/garlic_0',fail=40),
 'onion':I('洋葱',(.085,.085,.075),.25,170,'est',RC+'onion/onion_0',fail=341,rng=(.82,1.18)),
 'lotus_root':I('莲藕',(.075,.16,.07),.40,64,'est',prim=('capsule',.036,.044),rgba=(.85,.75,.6,1)),
 'yam':I('山药（去皮，切段）',(.04,.40,.04),.40,40,'est',prim=('capsule',.02,.18),mu_d=.10,rgba=(.95,.93,.85,1)),
 'corn':I('玉米',(.055,.26,.055),.35,50,'est',RC+'corn/corn_0'),
 'apple':I('苹果',(.08,.08,.075),.25,112.5,'M A1',RC+'apple/apple_0'),
 'pumpkin':I('南瓜块',(.09,.16,.07),1.0,50,'est',prim=('box',.045,.08,.035),rgba=(.95,.6,.15,1),rng=(.8,1.2)),
 'tomato':I('番茄',(.075,.075,.065),.18,11.13,'M T1',RC+'tomato/tomato_0',fail=83.5,rng=(.8,1.2)),
 'cherry_tomato':I('圣女果',(.026,.028,.025),.015,1.5,'est',RC+'tomato/tomato_1'),
 'cucumber':I('黄瓜',(.038,.28,.038),.25,19,'est',RC+'cucumber/cucumber_0',fail=148),
 'eggplant':I('长茄子',(.05,.30,.05),.25,10,'est',RC+'eggplant/eggplant_0',rgba=(.35,.15,.4,1)),
 'bell_pepper':I('青椒',(.075,.08,.075),.15,3,'est',RC+'bell_pepper/bell_pepper_0'),
 'chili':I('尖椒',(.02,.14,.02),.03,3,'est',AG+'chili_pepper/chili_pepper_0',fail=24),
 'zucchini':I('西葫芦',(.06,.25,.06),.50,22,'est',AG+'zucchini/zucchini_0',fail=167),
 'strawberry':I('草莓',(.03,.035,.03),.025,.6,'M S3 (safe; bruise 9.8)',AG+'strawberry/strawberry_0',fail=9.8),
 'cabbage':I('卷心菜',(.165,.165,.155),1.9,200,'est (crush 1198)',AG+'cabbage/cabbage_0',fail=1198,rng=(.85,1.1)),
 'napa':I('大白菜',(.155,.38,.15),2.8,200,'est (crush 820)',AG+'cabbage/cabbage_0',fail=820,rng=(.85,1.1)),
 'shiitake':I('香菇',(.062,.062,.054),.025,42,'der (stem); cap not found',prim=[('ellipsoid',(.031,.031,.0105),(0,0,.0165)),('cylinder',(.0066,.0165),(0,0,-.0105))],rgba=(.55,.38,.25,1),note='cap up, standing on the stem; grasped at the widest section (cap)'),
 'king_oyster':I('杏鲍菇',(.045,.15,.045),.08,84,'est',prim=('capsule',.0225,.0525),rgba=(.93,.88,.78,1)),
 'egg':I('鸡蛋',(.0455,.058,.0455),.055,10,'M EGG2 (weakest egg)',RC+'egg/egg_0',rgba=(.93,.86,.74,1),rng=(.9,1.1)),
 'celery':I('芹菜（单根）',(.025,.40,.015),.06,12,'est',prim=('box',.0125,.2,.0075),rgba=(.55,.8,.4,1)),
 'garlic_clove':I('蒜瓣',(.015,.03,.015),.006,14,'est',prim=('ellipsoid',.0075,.015,.0075),rgba=(.95,.92,.85,1)),
}
def size_variant(it,f):
 """Scaled copy (all axes by f; mass by f^3)."""
 o=dict(it);o['dims']=[x*f for x in it['dims']];o['kg']=it['kg']*f**3
 if isinstance(o['prim'],list):o['prim']=[(k,tuple(x*f for x in sz),tuple(x*f for x in pp)) for k,sz,pp in o['prim']]
 elif o['prim']:o['prim']=(o['prim'][0],)+tuple(x*f for x in o['prim'][1:])
 return o
def need_N(it,mu=None,a=0.,sf=1.5):
 """Per-finger squeeze for a friction hold, gravity in the pad plane: binding
 cook_ref rule sf 1.5 at the design friction (static); a adds an acceleration."""
 return sf*it['kg']*(G+a)/(2*(mu or it['mu_d']))
def pick_set(it,gr="PGC",clear=.004,lip=0.):
 """Smallest finger set whose open fingers clear the item (+2 % on the catalog width)
 and whose closed gap leaves room to build force: round items need the soft centre's
 travel (2 x (e + travel + 1 mm)), elongated ones only 2 x (e + 1 mm) because their
 length bears on the rims. With lips, the open lip tips must also clear the item's
 footprint at lip height (0.65 x half width for round items, the full half width for
 flat-bottomed ones)."""
 w=it['dims'][0]*1.02;wl=w/2*(1. if it.get('flat') else .65);rnd=it['dims'][1]<1.6*it['dims'][0]
 for s in [k for k,v in SETS.items() if v.get('gripper')==gr and k!='D']:
  d=SETS[s];lo,_=width_range(s,gr);need=2*(d['e']+.001+(d['travel'] if rnd else 0))
  q=max(w/2+d['e']+clear,wl+lip*.966+.003 if lip else 0)-d['fo']
  if lo+need<=w and q<=GRIPPERS[gr]['stroke']/2+1e-9:return s
 return None
def pick_mode(it,gr='PGC',s=None):
 """force: gripper force mode at F; ctl: position mode closed on the finger-root force
 sensor to F. F is as high as is safe, not the bare minimum: min(dmg/1.4, max(2 x the
 design hold force, the gripper's force-mode minimum), gripper max, and for the PGC the
 7 N m jaw moment at the pad centre of finger set s). Returned flag: the binding rule
 (sf 1.5 at the design friction) is met with F."""
 n=need_N(it);g=GRIPPERS[gr];F=min(it['dmg']/1.4,max(2*n,g['Fmin']),g['Fmax'])  # 1.4: closing overshoot + dynamic peaks
 if g['M_allow'] and s in SETS:F=min(F,g['M_allow']/(SETS[s]['D']+.016))
 ok=F>=n
 return ('force' if F>=g['Fmin'] else 'ctl',float(max(F,.5)),ok)
