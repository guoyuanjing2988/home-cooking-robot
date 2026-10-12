"""R13 non-rigid food models for softbench.py (lumped multibody, MuJoCo 3.2.5).

Flex FEM in MuJoCo 3.2.5 was unstable at the masses and stiffness of meat (probe:
NaN within 0.03 s at dt 0.25-0.5 ms), so non-rigid items are lumped models:
 chain : segments along the long axis joined by ball joints whose bending stiffness
         k = E I / L_seg (meat, fish);
 bunch : a rigid base (root, banded white part or stem cluster) with leaf chains
         (scallion, chives, spinach, bok choy, celery bunch, enoki);
 block : one rigid body (firm tofu; its sag on a fork tine is negligible);
 boxed : silken tofu as a block inside its open plastic box (the box is grasped);
 bulk  : many small free bodies in a handled basket (the handle is grasped).
Numbers: research/food_catalog_inputs.md (tags as in foods.py)."""
import numpy as np,xml.etree.ElementTree as E
from scipy.spatial.transform import Rotation
def fmt(v):return ' '.join(f'{float(x):.9g}' for x in v)
def S(zh,kind,dims,kg,dmg,dsrc,mu_d=.15,**k):
 return dict(zh=zh,kind=kind,dims=list(dims),kg=kg,dmg=dmg,dsrc=dsrc,mu=.3,mu_d=mu_d,rng=(1.,1.),src=None,prim=None,**k)
SOFT={
 # dims: x across (grip width), y along the item, z height lying in the basket
 'chicken_breast':S('鸡胸肉','chain',(.072,.172,.035),.25,56,'der CK1 (half-thickness squash)',E=48.6e3,nseg=5,rgba=(.95,.75,.7,1),mu_meas='0.5 wet on steel (CK)'),
 'pork':S('猪肉块','chain',(.06,.12,.05),.40,56,'est (chicken proxy)',E=48.6e3,nseg=3,rgba=(.85,.45,.45,1)),
 'fish':S('整鱼（鲈鱼）','chain',(.096,.35,.04),.60,None,'not found',mu_d=.12,E=48.6e3,nseg=7,taper=True,rgba=(.6,.65,.7,1),mu_meas='0.12 wet with mucus'),
 'fish_fillet':S('鱼片','chain',(.08,.18,.02),.20,None,'indentation < 5 mm',mu_d=.10,E=20e3,nseg=4,rgba=(.95,.9,.85,1)),
 'tofu_firm':S('老豆腐','block',(.08,.10,.05),.40,15,'der TF',mu_d=.10,rgba=(.97,.95,.85,1)),
 'tofu_silken':S('嫩豆腐（盒装）','boxed',(.10,.10,.055),.40,3,'der TF',mu_d=.10,rgba=(.98,.97,.9,1)),
 'scallion':S('小葱（一把）','bunch',(.03,.40,.025),.20,16.5,'est (white shaft)',base=(.10,.06),nleaf=8,leaf=(.30,.004),Eleaf=2.4e6,rgba=(.4,.75,.3,1)),
 'chives':S('韭菜（一把）','bunch',(.03,.35,.025),.30,140,'M CV1 (banded base)',base=(.05,.15),nleaf=10,leaf=(.30,.003),Eleaf=1e6,rgba=(.3,.6,.25,1)),
 'spinach':S('菠菜（一把）','bunch',(.05,.30,.04),.30,113.8,'M (root crown, axial)',base=(.05,.15),nleaf=10,leaf=(.25,.012),Eleaf=.5e6,rgba=(.2,.5,.2,1)),
 'bok_choy':S('上海青（一棵）','bunch',(.05,.18,.045),.11,12.2,'M BC2 (stem base)',base=(.06,.55),nleaf=6,leaf=(.12,.02),Eleaf=.9e6,rgba=(.45,.7,.35,1)),
 'celery_bunch':S('芹菜（一把）','bunch',(.08,.45,.06),.60,12,'est',base=(.08,.25),nleaf=8,leaf=(.37,.012),Eleaf=5e6,rgba=(.55,.8,.4,1)),
 'enoki':S('金针菇（一把）','bunch',(.045,.14,.03),.15,None,'not found',base=(.04,.4),nleaf=8,leaf=(.10,.003),Eleaf=.5e6,rgba=(.96,.94,.85,1)),
 'bean_sprouts':S('豆芽（筐）','bulk',(.005,.09,.005),.30,None,'never pinch',n=40,piece=('capsule',.0025,.03),rgba=(.95,.95,.85,1),note='sprouts modelled 5 mm thick (2.3 mm real) for solver stability'),
 'strawberry_box':S('草莓（筐）','bulk',(.03,.035,.03),.25,.6,'M S3',n=10,piece=('ellipsoid',.015,.015,.0175),rgba=(.85,.1,.15,1)),
 'cherry_tomato_box':S('圣女果（筐）','bulk',(.026,.028,.025),.20,1.5,'est',n=14,piece=('ellipsoid',.013,.013,.0125),rgba=(.9,.15,.1,1)),
 'bell_pepper_box':S('青椒（筐）','bulk',(.075,.08,.075),.45,3,'est',n=3,piece=('ellipsoid',.036,.036,.038),rgba=(.2,.6,.2,1)),
 'lettuce':S('生菜（整棵）','ball',(.15,.15,.12),.40,2.2,'LE1 (leaf injury)',rgba=(.6,.85,.4,1)),
 'lettuce_box':S('生菜（筐）','bulk',(.15,.15,.13),.40,2.2,'LE1',n=1,piece=('ellipsoid',.075,.075,.06),rgba=(.6,.85,.4,1)),
 'shrimp':S('虾（筐）','bulk',(.015,.07,.015),.30,None,'not found',n=25,piece=('capsule',.0075,.027),rgba=(.75,.65,.6,1)),
 'garlic_cloves':S('蒜瓣（筐）','bulk',(.015,.03,.015),.15,14,'est',n=25,piece=('ellipsoid',.0075,.0075,.014),rgba=(.95,.92,.85,1)),
 'green_beans':S('四季豆（筐）','bulk',(.009,.15,.009),.30,None,'not found',n=30,piece=('capsule',.0045,.07),rgba=(.4,.7,.3,1)),
}
FI=dict(contype='1',conaffinity='7',friction='0 0 0',condim='4',solref='.002 1')
def _seg_k(E_,w,h,L):return E_*w*h**3/12/L  # bending stiffness of one joint (N m/rad)
def build(it,wb,asset,z0,BF):
 """Build the item at the basket origin; returns (root body element, extra free
 bodies (bulk contents), grasp spec dict)."""
 k=it['kind'];W,L,H=it['dims'];rg=fmt(it['rgba'])
 if k in ('chain','block'):
  n=it.get('nseg',1);Ls=L/n;mseg=it['kg']/n;mid=n//2
  def seg_size(i):
   if not it.get('taper'):return W/2,Ls/2,H/2
   f=.45+.55*np.sin(np.pi*(i+.5)/n)  # fish: thick middle, thin head/tail
   return W/2*f,Ls/2,H/2*max(f,.6)
  y0=-L/2+(mid+.5)*Ls;root=E.SubElement(wb,'body',name='food',pos=fmt([0,y0,z0]));E.SubElement(root,'freejoint',name='food_free')
  E.SubElement(root,'geom',name=f'food_c{mid}',type='box',size=fmt(seg_size(mid)),mass=str(mseg),rgba=rg,**FI)
  for dirn in (1,-1):
   par=root;idx=mid
   while 0<=idx+dirn<n:
    idx+=dirn;b=E.SubElement(par,'body',name=f'food_s{idx}',pos=fmt([0,dirn*Ls,0]))
    w_,l_,h_=seg_size(idx);kb=_seg_k(it['E'],2*w_,2*h_,Ls)
    E.SubElement(b,'joint',name=f'food_j{idx}',type='ball',pos=fmt([0,-dirn*Ls/2,0]),stiffness=str(kb),damping=str(kb/20),armature='1e-5')
    E.SubElement(b,'geom',name=f'food_c{idx}',type='box',size=fmt((w_,l_,h_)),mass=str(mseg),rgba=rg,**FI);par=b
  return root,[],dict(at='com')
 if k=='ball':  # one soft round head (lettuce): an ellipsoid
  root=E.SubElement(wb,'body',name='food',pos=fmt([0,0,z0]));E.SubElement(root,'freejoint',name='food_free')
  E.SubElement(root,'geom',name='food_c0',type='ellipsoid',size=fmt([W/2,L/2,H/2]),mass=str(it['kg']),rgba=rg,**FI)
  return root,[],dict(at='com')
 if k=='bunch':
  bl,bfrac=it['base'];mb=it['kg']*bfrac;nl=it['nleaf'];ll,lt=it['leaf'];ml=(it['kg']-mb)/nl
  y0=-L/2+bl/2;root=E.SubElement(wb,'body',name='food',pos=fmt([0,y0,z0-H/2+W/2*.9]));E.SubElement(root,'freejoint',name='food_free')
  E.SubElement(root,'geom',name='food_c0',type='capsule',size=fmt([W/2*.9,max(bl/2-W/2*.9,.003)]),quat=fmt(Rotation.from_euler('x',np.pi/2).as_quat()[[3,0,1,2]]),mass=str(mb),rgba=fmt([c*.8 for c in it['rgba'][:3]]+[1]),**FI)
  ns=5;Ls=ll/ns;rng=np.random.default_rng(1);cnt=0
  for j in range(nl):
   a=2*np.pi*j/nl;off=np.array([np.cos(a)*W*.3,0,np.sin(a)*W*.25]);par=root;pos=np.array([off[0],bl/2+Ls/2,off[2]])
   for i in range(ns):
    b=E.SubElement(par,'body',name=f'food_l{j}_{i}',pos=fmt(pos));th=lt*(1 if it['leaf'][1]<.008 else .25)
    kb=_seg_k(it['Eleaf'],lt,th,Ls)
    E.SubElement(b,'joint',name=f'food_lj{j}_{i}',type='ball',pos=fmt([0,-Ls/2,0]),stiffness=str(kb),damping=str(kb/10+1e-5),armature='1e-6')
    if lt<.008:E.SubElement(b,'geom',name=f'food_lc{j}_{i}',type='capsule',size=fmt([lt/2,Ls/2-lt/2]),quat=fmt(Rotation.from_euler('x',np.pi/2).as_quat()[[3,0,1,2]]),mass=str(ml/ns),rgba=rg,**FI)
    else:E.SubElement(b,'geom',name=f'food_lc{j}_{i}',type='box',size=fmt([lt/2,Ls/2,th/2]),mass=str(ml/ns),rgba=rg,**FI)
    par=b;pos=np.array([0,Ls,0])
  return root,[],dict(at='base')
 if k=='boxed':
  # open PP box 2 mm walls; the tofu block sits inside (gap 2 mm); the robot pinches the box
  bw,bl_,bh=W+.006,L+.006,H+.005;root=E.SubElement(wb,'body',name='food',pos=fmt([0,0,z0]));E.SubElement(root,'freejoint',name='food_free')
  C=dict(FI,friction='0 0 0');E.SubElement(root,'geom',name='food_c0',type='box',size=fmt([bw/2,bl_/2,.001]),pos=fmt([0,0,-bh/2+.001]),mass='.02',rgba='.85 .9 .95 .5',**C)
  for s in (-1,1):
   E.SubElement(root,'geom',name=f'food_wx{s}',type='box',size=fmt([.001,bl_/2,bh/2]),pos=fmt([s*(bw/2-.001),0,0]),mass='.01',rgba='.85 .9 .95 .5',**C)
   E.SubElement(root,'geom',name=f'food_wy{s}',type='box',size=fmt([bw/2,.001,bh/2]),pos=fmt([0,s*(bl_/2-.001),0]),mass='.01',rgba='.85 .9 .95 .5',**C)
  t=E.SubElement(wb,'body',name='tofu',pos=fmt([0,0,z0-bh/2+.002+H/2]));E.SubElement(t,'freejoint',name='tofu_free')
  E.SubElement(t,'geom',name='tofu_g',type='box',size=fmt([W/2-.001,L/2-.001,H/2]),mass=str(it['kg']),rgba=rg,contype='1',conaffinity='7',condim='4',friction=f"{it['mu_d']} .001 .0001",solref='.002 1')
  return root,[t],dict(at='com',width=bw)
 if k=='bulk':
  # basket: 200 mm, 70 mm walls, bridge handle with a 30 mm keyed knob at 110 mm
  R_=.1 if max(it['piece'][1:])<.03 else .11;Hh=.07 if max(it['piece'][1:])<.05 else .1;root=E.SubElement(wb,'body',name='food',pos=fmt([0,0,z0]));E.SubElement(root,'freejoint',name='food_free')
  E.SubElement(root,'geom',name='food_c0',type='cylinder',size=fmt([R_,.002]),pos=fmt([0,0,.002]),mass='.12',rgba='.3 .55 .75 1',**FI)
  for j in range(20):
   a=2*np.pi*j/20;g=E.SubElement(root,'geom',name=f'food_w{j}',type='box',size=fmt([.0015,R_*np.tan(np.pi/20),Hh/2]),pos=fmt([R_*np.cos(a),R_*np.sin(a),Hh/2]),mass='.006',rgba='.3 .55 .75 1',**FI)
   g.set('quat',fmt(Rotation.from_euler('z',a).as_quat()[[3,0,1,2]]))
  # side handle (like a pot handle): an arm off the rim at -x with a 30 mm keyed knob;
  # a bridge handle over the top jammed big items (lettuce) and long ones (beans)
  E.SubElement(root,'geom',name='food_arm',type='box',size='.022 .012 .006',pos=fmt([-R_-.02,0,Hh-.006]),mass='.015',rgba='.3 .55 .75 1',**FI)
  E.SubElement(root,'geom',name='food_knob',type='box',size='.015 .02 .015',pos=fmt([-R_-.035,0,Hh+.015]),mass='.01',rgba='.95 .6 .1 1',**FI)
  pk,*psz=it['piece'];n=it['n'];mp=it['kg']/n;rng=np.random.default_rng(0);extra=[]
  # pieces lying flat in layers without initial overlap: grid cells of the piece's
  # footprint inside the basket, layers stacked by the piece height
  foot=(psz[1]+psz[0]) if pk=='capsule' else max(psz[0],psz[1]);half_h=psz[0] if pk=='capsule' else psz[2]
  cell=2*foot+.003;ng=int(2*(R_-.004)//cell);cs=[((i-(ng-1)/2)*cell,(j-(ng-1)/2)*cell) for i in range(ng) for j in range(ng)]
  cs=[c for c in cs if np.hypot(*c)+foot<R_-.004] or [(0.,0.)]
  for i in range(n):
   cx,cy=cs[i%len(cs)];layer=i//len(cs);p=[cx,cy,z0+.004+half_h+layer*(2*half_h+.002)];yaw=rng.uniform(0,np.pi)
   q=Rotation.from_euler('zx',[yaw,np.pi/2]).as_quat()[[3,0,1,2]] if pk=='capsule' else Rotation.from_euler('z',yaw).as_quat()[[3,0,1,2]]
   b=E.SubElement(wb,'body',name=f'piece{i}',pos=fmt(p),quat=fmt(q))
   E.SubElement(b,'freejoint');E.SubElement(b,'geom',type=pk,size=fmt(psz),mass=str(mp),rgba=fmt(it['rgba']),contype='1',conaffinity='1',condim='3',friction='.5 .005 .0001',solref='.006 1')
   extra.append(b)
  return root,extra,dict(at='knob',knob=[-R_-.035,0,Hh+.015],width=.04)
 raise ValueError(k)
