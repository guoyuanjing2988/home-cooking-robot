"""Park in place, piece (c) for other stroke starts (Mac, 2026-10-13; new file): the cup chain play states
(results/mac/chain_cup_final.json, as r19cup_recheck.py) with the spatula left at the held pose of the first
state of stroke KEY (work1..work4) of results/r19/stir/stirwalk2_h_scrape_dice_r17.json -> results/mac/park_in_wok_c_<KEY>.json"""
import sys,json,numpy as np,mujoco,xml.etree.ElementTree as E
import cupobj   # noqa: F401
import chain
from scene import build,save,fmt
from checker import Checker
import kitchen16 as K16,kitchen17 as K17
KV=dict(a.split('=',1) for a in sys.argv[1:]);ST=json.load(open('results/r19/stir/stirwalk2_h_scrape_dice_r17.json'))
r=json.load(open('results/mac/chain_cup_final.json'))
def spatula_geoms(Q0):
 K16.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);sv=dict(K16.TOOL_XY);K16.TOOL_XY['spider']=(1.52,.36)
 SCN=dict(r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None,'spatula':None})
 cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,r15_spatula=.45,r15_spatula_jaw=-1,**SCN);tree,meta=build(cfg,None)
 m=mujoco.MjModel.from_xml_string(E.tostring(tree.getroot(),encoding='unicode'));d=mujoco.MjData(m);d.qpos[:]=Q0;mujoco.mj_kinematics(m,d)
 K16.TOOL_XY.clear();K16.TOOL_XY.update(sv)
 tn={mujoco.mjtGeom.mjGEOM_BOX:('box',3),mujoco.mjtGeom.mjGEOM_CYLINDER:('cylinder',2),mujoco.mjtGeom.mjGEOM_CAPSULE:('capsule',2),mujoco.mjtGeom.mjGEOM_SPHERE:('sphere',1),mujoco.mjtGeom.mjGEOM_ELLIPSOID:('ellipsoid',3)}
 out=[]
 for g in range(m.ngeom):
  n=m.geom(g).name
  if not n.startswith('R_gripper_spatula'):continue
  t,ns=tn[m.geom_type[g]];qq=np.zeros(4);mujoco.mju_mat2Quat(qq,d.geom_xmat[g])
  out.append(dict(name='park_'+n[2:],type=t,size=m.geom_size[g][:ns].tolist(),pos=d.geom_xpos[g].tolist(),quat=qq.tolist()))
 return out
for KEY in KV.get('KEYS','work1,work2,work3,work4').split(','):
 Q0=np.array(ST['states']['q'][ST['states']['kinds'].index(KEY)],float);SG=spatula_geoms(Q0)
 K16.set_design(**r['design'])
 for k_,v in r.get('tool_xy',{}).items():K16.TOOL_XY[k_]=tuple(v)
 cfg=chain.chain_cfg('SD',**{**dict(r19_station=True,r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools=dict(K17.R17_TOOLS_OFF)),**r['scene'],**K17.held_cfg(r['obj'],r['grasp_sense'])})
 tree,meta=build(cfg,None);w=tree.find('worldbody')
 for g in SG:E.SubElement(w,'geom',name=g['name'],type=g['type'],size=fmt(g['size']),pos=fmt(g['pos']),quat=fmt(g['quat']),rgba='.8 .8 .82 1',contype='1',conaffinity='2',mass='.000001')
 cc=Checker(tree,meta);worst={};nh=0;hl=[]
 for i,q in enumerate(r['play']):
  c=cc.check(np.array(q),full=True,mass=0.)
  if c['hits']:nh+=1;hl.append(dict(step=i,hits=[h['pair'] for h in c['hits']][:3]))
  for cat,v in c['clearance'].items():
   if cat not in worst or v['reserve_mm']<worst[cat][0]:worst[cat]=(v['reserve_mm'],i)
 hp=sorted({p for h in hl for pr in h['hits'] for p in pr if p.startswith('park_')})
 C=dict(key=KEY,stroke_start_q=Q0.tolist(),ok=nh==0,steps=len(r['play']),steps_with_hits=nh,spatula_parts_hit=hp,hits=hl[:20],min_reserve_by_cat={k:dict(mm=round(v[0],1),step=v[1]) for k,v in worst.items()},
  handle_top_z=max(g['pos'][2] for g in SG if 'handle' in g['name']))
 save(f'results/mac/park_in_wok_c_{KEY}.json',C);print('C',KEY,json.dumps({k:v for k,v in C.items() if k not in('hits','stroke_start_q')}),flush=True)
