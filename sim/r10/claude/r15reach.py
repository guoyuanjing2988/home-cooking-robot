"""R15 reach + clearance probes for the cooking station (kitchen15.py), docked cart, UR5e,
PGC + R12 fingers: 96-start collision-aware IK (solver.solve) with the unchanged checker
(10 mm robot-environment, 5 mm gripper/held-environment), SEEDS seeds x 2 jaw senses.
Plume post-check (not part of the checker): every robot geom except the held tool must stay
at least PLUME m (default 0.20) from the wok axis between the rim and the hood bottom;
the plume estimate (r15_cooking_market.md 5.4) puts ~90 °C on the axis 30 cm above an
induction wok and near-ambient 20 cm off it, and the UR5e is rated to 50 °C.
Probes:
 stir KEYS=<stirbench keys json> I=<index> [GRIP=.40]  spatula at a stroke keyframe
 pour A=<tip deg> [GRASP=end|top] [FOOD=kg] [DROP=m] [PH=plate height] [R16=1]   wok held by its grip block: A=0 lifted
                                                         4 cm in place; A>0 tipped toward the robot
                                                         about the handle axis, lip DROP above the plate
 rim AZ=<deg>                                           cup over the wok wall at azimuth AZ (edge pour)
 stand [GRIP=.40]                                       spatula lifted just out of its stand
 drum                                                   pour drum seated in its servo holder (loading)
Options: SEEDS=1|2, CARTX=.., TAG=..
-> results/r15/reach_<probe>_<tag>.json: ok, best (max reserve among plume-clear candidates),
   all candidates (q, reserve_mm, plume_mm) for the continuity DP, load (pour)."""
import sys,os,json,numpy as np,mujoco,xml.etree.ElementTree as E
import chain
from scene import build,save,fmt
from checker import Checker,reference
from solver import solve
import kitchen15 as K
probe=sys.argv[1];KV=dict(a.split('=',1) for a in sys.argv[2:])
PLUME=float(KV.get('PLUME',0. if probe=='pour' else .20));   # plating and oil pour-out happen with the heat off
GRIP=float(KV.get('GRIP',.40));SEEDS=(14,15)[:int(KV.get('SEEDS',2))]
ex=np.array([1.,0,0])
def models(extra):
 cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,**extra);tree,meta=build(cfg,None);ch=Checker(tree,meta)
 # plume model: the same tree plus a non-colliding cylinder, used only for the post-check
 E.SubElement(tree.find('worldbody'),'geom',name='r15_plume',type='cylinder',pos=fmt([K.WOK0[0],K.WOK0[1],(K.RIM_Z+1.25)/2]),size=fmt([max(PLUME,.01),(1.25-K.RIM_Z)/2]),contype='0',conaffinity='0',rgba='1 .5 0 .2')
 pm=mujoco.MjModel.from_xml_string(E.tostring(tree.getroot(),encoding='unicode'));pd=mujoco.MjData(pm)
 pl=pm.geom('r15_plume').id
 rob=[g for g in range(pm.ngeom) if pm.geom(g).name.startswith('R_') and not pm.geom(g).name.startswith(('R_gripper_spatula','R_gripper_r15_wok','R_cart','R_dock'))]
 def plume_mm(q):
  pd.qpos[:]=q;mujoco.mj_forward(pm,pd);ft=np.zeros(6)
  return 1000*min(mujoco.mj_geomDistance(pm,pd,g,pl,1.,ft) for g in rob) if PLUME>0 else None
 return ch,plume_mm
def run(name,p,approach,jaw_of,extra_of,jaw_q=.015):
 """jaw_of(sign) -> jaw axis, extra_of(sign) -> scene cfg extras: the held tool's geometry
 depends on which way round it sits in the fingers, so each sense gets its own model."""
 out=[];stat={};ch=None
 for sign in (1,-1):
  ch,plume_mm=models(extra_of(sign))
  for seed in SEEDS:
   t=dict(name=name,points=[list(p)]*2,held=None,kind='transfer',force=None,approach=list(approach),jaws=[tuple(jaw_of(sign))],jaw_q=jaw_q)
   if 'CARTX' in KV:t['cart_x']=float(KV['CARTX'])
   r=solve(ch,np.asarray(p,float),list(approach),target=t,seed=seed)
   for k,v in r['status_counts'].items():stat[k]=stat.get(k,0)+v
   out+=[dict(q=c['q'],reserve_mm=c['reserve_mm'],plume_mm=plume_mm(np.array(c['q'])),jaw_sign=sign) for c in r['candidates']]
   if not r['ok'] and not stat.get('blockers'):stat['blockers']=sorted({tuple(h['pair']) for row in r['rows'] if row.get('check') for h in row['check'].get('hits',[])},key=str)[:10]
 good=[c for c in out if PLUME<=0 or c['plume_mm']>=0]
 best=max(good,key=lambda c:c['reserve_mm']) if good else (max(out,key=lambda c:c['plume_mm']) if out and PLUME>0 else None)
 return dict(ok=bool(good),n_candidates=len(out),n_plume_clear=len(good),status_counts=stat,best=best,cands=out),ch
PH=float(KV.get('PH',K.PLATE['h']))   # R16: PH=.15 = waste bucket at the plating spot (wok rinse)
TIP=KV.get('TIP','x');PLATE_C=np.array([float(KV.get('PX',K.PLATE['c'][0])),float(KV.get('PY',K.PLATE['c'][1])),K.PLATE['c'][2]])
def wok_world(A,lift=.04):
 """Wok pose (R, origin of the wok frame) for plating, as in pourwok.py: A=0 lifted LIFT in
 place on the cooker; with CARRY=1 (A=0) or A>0 the wok is at the plating spot, tipped by A
 about a level axis through its rim centre (TIP=y: sideways away from the handle, lip = right
 rim; TIP=x: toward the robot, lip = front rim); at A=A_MAX (default 90) the lip sits LIPX from
 the plate centre and DROP above the plate."""
 c,s=np.cos(np.radians(A)),np.sin(np.radians(A))
 rot=(lambda a:np.array([[1,0,0],[0,np.cos(np.radians(a)),-np.sin(np.radians(a))],[0,np.sin(np.radians(a)),np.cos(np.radians(a))]])) if TIP=='x' else (lambda a:np.array([[np.cos(np.radians(a)),0,np.sin(np.radians(a))],[0,1,0],[-np.sin(np.radians(a)),0,np.cos(np.radians(a))]]))
 lip=np.array([0,-K.A_RIM,0]) if TIP=='x' else np.array([K.A_RIM,0,0]);toward=np.array([0,-1.,0]) if TIP=='x' else np.array([1.,0,0])   # lip relative to the rim centre
 R=rot(A)
 if A==0 and not KV.get('CARRY'):return R,K.WOK0+[0,0,lift]
 target=PLATE_C+[0,0,PH+float(KV.get('DROP',.08))]+float(KV.get('LIPX',-.05))*toward
 piv=target-rot(float(KV.get('A_MAX',90)))@lip
 return R,piv-R@np.array([0,0,K.DEPTH])
res={}
if probe=='stir':
 keys=json.load(open(KV['KEYS']))['keys'];k=keys[int(KV['I'])];Rb=np.array(k['R']);pw=np.array(k['p'])
 # the stroke keys put the blade's lowest corner 1.5 mm off the steel (its working contact); here it is
 # lifted LIFT more along the wall normal so the unchanged 5 mm gripper rule does not count that contact
 nrm=K.SP.C-pw;nrm/=np.linalg.norm(nrm);pb=pw+float(KV.get('LIFT',.004))*nrm+K.WOK0
 _,_,b=K.spatula_tool(GRIP);p=pb+Rb@b;approach=Rb@(-K.HD)
 r,ch=run(probe,p,approach,lambda s:Rb@(s*ex),lambda s:dict(r15_spatula=GRIP,r15_spatula_jaw=s));res=dict(probe='stir',keys=KV['KEYS'],i=int(KV['I']),t=k['t'],grip_m=GRIP,tcp=p.tolist(),**r)
 tag=f"stir_{os.path.basename(KV['KEYS'])[5:-10]}_i{int(KV['I']):03d}_g{GRIP:g}"
elif probe=='pour':
 A=float(KV.get('A',0));grasp=KV.get('GRASP','end');Rw,ow=wok_world(A)
 a_w,j_w=((0,0,-1.),(0,1.,0)) if grasp=='top' else ((1.,0,0),(0,0,1.))   # in the wok frame; end-on: jaws close top/bottom on the block
 bc=K.GRIP['c']-K.WOK0;p=ow+Rw@bc;approach=Rw@np.array(a_w)
 def held(s):   # wok frame -> tool frame for jaw sense s
  Rwt=reference.rotation(a_w,s*np.array(j_w));T=np.eye(4);T[:3,:3]=Rwt.T;T[:3,3]=-Rwt.T@bc
  return dict(r15_wok_held=dict(T_tool_wok=T.tolist()),r15_plate=True)
 r,ch=run(probe,p,approach,lambda s:Rw@(s*np.array(j_w)),lambda s:{**held(s),'r15_plate_c':PLATE_C.tolist(),'r15_plate_h':PH,**({'r16':True} if 'R16' in KV else {})},jaw_q=.015)
 # held load (own model of the checker's load terms): wok 1.5 kg (CoG 45 mm above the bottom),
 # handle + block 0.3 kg, food FOOD kg on the bottom; joint torque ratios vs the rated envelope
 # (the checker's envelope file), PGC moment about the TCP vs its 7 N.m limit, payload <= 5 kg
 food=float(KV.get('FOOD',1.15));parts=[(1.5,np.array([0,0,.045])),(.3,(K.HANDLE['root']+K.HANDLE['end'])/2-K.WOK0),(food,np.array([0,0,.02]))]
 mass=sum(m_ for m_,_ in parts);com_w=ow+Rw@(sum(m_*c for m_,c in parts)/mass)
 load=None
 if r['best']:
  q=np.array(r['best']['q']);m,d=ch.m,ch.d;d.qpos[:]=q;d.qvel[:]=0;mujoco.mj_forward(m,d)
  sid=m.site('R_prep').id;bid=m.site_bodyid[sid];jp=np.zeros((3,m.nv));jr=jp.copy();mujoco.mj_jac(m,d,jp,jr,com_w,bid)
  tau=d.qfrc_bias-jp.T@np.array([0,0,-mass*9.81]);ratios={n:float(abs(tau[ch.da[n]])/v) for n,v in ch.env.items()}
  eoat=sum(m.body_mass[m.body(n).id] for n in ['R_tool','R_jaw_minus','R_jaw_plus'])
  load=dict(held_kg=round(mass,2),payload_kg=round(mass+eoat,2),max_joint_ratio=round(max(ratios.values()),3),ratios={k_:round(v,3) for k_,v in ratios.items()},
   pgc_moment_Nm=round(float(np.linalg.norm(np.cross(com_w-d.site_xpos[sid],[0,0,-mass*9.81]))),2),pgc_limit_Nm=7,com_from_tcp_m=round(float(np.linalg.norm(com_w-d.site_xpos[sid])),3))
 res=dict(probe='pour',pitch_deg=A,grasp=grasp,food_kg=food,tcp=p.tolist(),load=load,**r);tag=f"pour_a{A:g}_{grasp}_f{food:g}"+(f"_tip{TIP}_p{PLATE_C[0]:g},{PLATE_C[1]:g}" if A>0 or KV.get('CARRY') else '')+(f"_ph{PH:g}" if 'PH' in KV else '')
elif probe=='rim':
 az=np.radians(float(KV['AZ']));rad=np.array([np.cos(az),np.sin(az),0])
 p=np.array([K.WOK0[0],K.WOK0[1],K.RIM_Z+.08])+rad*(K.A_RIM-.03);approach=np.array([0,0,-1.])+.18*rad;approach/=np.linalg.norm(approach)
 r,ch=run(probe,p,approach,lambda s:s*np.cross([0,0,1.],rad),lambda s:dict(r14_cup=True),jaw_q=.014);res=dict(probe='rim',az_deg=float(KV['AZ']),tcp=p.tolist(),**r);tag=f"rim_az{float(KV['AZ']):g}"
elif probe=='drum':
 # load (or take) the pour drum in its servo holder: drum axis along +y, gripper on the end knob from the robot side
 c=np.array([float(x) for x in KV['DC'].split(',')]) if 'DC' in KV else K.DRUM_HOLD['c'];p=c-np.array([0,.10,0]);jw=(0,0,1.) if KV.get('JZ') else (1.,0,0)
 r,ch=run(probe,p,(0,1.,0),lambda s:tuple(s*np.array(jw)),lambda s:dict(r14_drum=True,r15_drum_taken=True,**({'r15_drum_c':c.tolist()} if 'DC' in KV else {})),jaw_q=.015);res=dict(probe='drum',drum_c=c.tolist(),tcp=p.tolist(),**r);tag='drumload'+('_'+KV['DC'] if 'DC' in KV else '')
elif probe=='stand':
 # blade frame with the handle (HD) straight up and the blade width along world x
 c_,s_=np.cos(K.SP.BEND),np.sin(K.SP.BEND);Rb=np.c_[ex,[0,s_,c_],[0,-c_,s_]];assert np.allclose(Rb@K.HD,[0,0,1])
 _,_,b=K.spatula_tool(GRIP);pb=K.STAND['c']+[0,0,K.STAND['h']+.01];p=pb+Rb@b
 r,ch=run(probe,p,Rb@(-K.HD),lambda s:Rb@(s*ex),lambda s:dict(r15_spatula=GRIP,r15_spatula_jaw=s));res=dict(probe='stand',grip_m=GRIP,tcp=p.tolist(),handle_dir=(Rb@K.HD).tolist(),**r);tag=f"stand_g{GRIP:g}"
os.makedirs('results/r15',exist_ok=True)
tag+=('_cx'+KV['CARTX'] if 'CARTX' in KV else '')+('_'+KV['TAG'] if 'TAG' in KV else '')
res['plume_m']=PLUME;save(f'results/r15/reach_{tag}.json',res)
print(json.dumps({k:v for k,v in res.items() if k not in ('cands','best')}|{'best_reserve':res['best'] and res['best']['reserve_mm'],'best_plume':res['best'] and res['best']['plume_mm']},default=str))
