"""Independent arm reach maps: original kitchen, new complete transport hardware."""
import os,sys,time,json,hashlib,xml.etree.ElementTree as E,collections
from pathlib import Path
import numpy as np,mujoco
H=Path(__file__).resolve().parent;O=H/'results';layout=sys.argv[1];side=sys.argv[2]
cfg=json.loads((O/'layouts'/f'{layout}.json').read_text())
import r07_model
r07_model.CONFIG=cfg;r07_model.CONFIG.pop('transport_only',None)
import r07_runtime as rt
from distance import Bounds
from ik_v2_r07 import fast_ik,dexterity
tr,meta=rt.s.model.build(dict(cfg,transport_only=True))
ch=object.__new__(rt.Checker);ch.desc=rt.s.ck.hand([0,0,1],jaw_axis=[0,1,0]);xml=E.tostring(tr.getroot(),encoding='unicode');ch.bind_model(mujoco.MjModel.from_xml_string(xml));ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False
ch.phase={'id':'REACH_MAP'};ch.seg={'jaw_axes':[[0,1,0]]}
other='L' if side=='R' else 'R'
def required(ch,a,b):
 if any(ch.gnames[g].startswith(other+'_') for g in (a,b)):return None
 return rt.f.required(ch,a,b)
ch.d.qpos[:]=ch.m.qpos0;mujoco.mj_forward(ch.m,ch.d)
bounds=Bounds(ch,required)
# Bounds deliberately restores OEM/frame pairs after required() returnsNone.
# A per-arm map must explicitly remove opposite-arm/frame pairs too; final
# two-arm admission uses the untouched full policy and never this filter.
keep=np.array([not any(ch.gnames[g].startswith(other+'_') for g in (a,b)) for a,b,_,_ in bounds.pairs],bool)
bounds.pairs=[p for p,v in zip(bounds.pairs,keep) if v]
bounds.aa=bounds.aa[keep];bounds.bb=bounds.bb[keep];bounds.need=bounds.need[keep];bounds.cats=bounds.cats[keep];bounds.relative_influence=bounds.relative_influence[keep]
bounds.pair_lookup={frozenset([ch.gnames[a],ch.gnames[b]]):i for i,(a,b,_,_) in enumerate(bounds.pairs)}
bounds.catids={cat:np.flatnonzero(bounds.cats==cat) for cat in set(bounds.cats)}
outdir=O/'reachability'/layout;outdir.mkdir(parents=True,exist_ok=True)
points=[dict(pos=[x,y,z],region='counter_sink') for x in (-1.65,-1.25,-.95,-.65,-.4,-.15,.20,.55) for y in (.075,.22,.37) for z in (.93,1.08,1.24)]
points +=[dict(pos=[x,y,z],region='faucet_surrounding') for x in (-.52,-.4,-.28) for y in (.30,.405) for z in (.96,1.12)]
if cfg.get('replacement_faucet'):
 fc=cfg['replacement_faucet']
 if fc.get('mount_type')=='wall':outlet=np.array(fc['wash_reference_pos_m'][:2])
 else:
  fx,fy=fc['deck_xy_m'];yaw=np.radians(fc['yaw_deg']);outlet=np.array([fx,fy])+.227*np.array([np.cos(yaw),np.sin(yaw)])
 points=[p for p in points if p['region']!='faucet_surrounding']
 points +=[dict(pos=[float(x),float(y),z],region='replacement_faucet_surrounding') for x in (outlet[0]-.10,outlet[0],outlet[0]+.10) for y in (max(.08,outlet[1]-.12),min(.45,outlet[1]+.08)) for z in (.94,1.12)]
points += [dict(pos=[x,y,z],region='appliance_loading') for x in (-1.635, .425, 1.53, 1.6325) for y in (.11,.205) for z in (1.32,1.45)]
orientations=[dict(id='down',approach=[0,0,-1],jaw_axis=[0,1,0]),dict(id='front',approach=[0,1,0],jaw_axis=[1,0,0]),dict(id='side',approach=[1,0,0],jaw_axis=[0,1,0])]
rows=[];rng=np.random.default_rng(87000+int(layout[1:])*10+(side=='L'));names=rt.s.ck.ARMS[side]+[side+'_carriage_x'];ix=[ch.qa[n] for n in names];lim=np.array([ch.m.jnt_range[ch.jid[n]] for n in names]);began=time.monotonic();previous=[];blockers=collections.Counter()
for point in points:
 for orient in orientations:
  hand=rt.s.ck.hand(point['pos'],held='empty',jaw_axis=orient['jaw_axis'],approach=orient['approach']);hand['check_forces_N']=[[0,0,0]]
  best=None;found=None;kin_count=0
  for seed in range(12):
   q=ch.m.qpos0.copy();q[ch.qa[side+'_jaw_minus']]=q[ch.qa[side+'_jaw_plus']]=.015
   q[ix]=rng.uniform(lim[:,0],lim[:,1]);q[ch.qa[side+'_carriage_x']]=np.clip(point['pos'][0]+rng.uniform(-.55,.55),*lim[-1])
   if previous and seed<3:q=np.array(previous[(len(previous)-1-seed)%len(previous)]).copy()
   q,err,its=fast_ik(ch,q,{side:hand},seed,max_iter=180)
   kin=all(e['position_mm']<=5 and e['orientation_deg']<=3 for e in err)
   item=dict(seed=seed,q=q.tolist(),errors=err,iterations=its,kinematic_pass=kin)
   if best is None or sum(e['position_mm']+e['orientation_deg'] for e in err)<sum(e['position_mm']+e['orientation_deg'] for e in best['errors']):best=item
   if not kin:continue
   kin_count+=1;ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d);hits,mins,proof=bounds.check()
   for hit in hits:blockers[' | '.join(hit['pair'])]+=1
   item.update(clearance_pass=not hits,blockers=hits[:4],minima=mins)
   if not hits:
    item['dexterity']=dexterity(ch,q,side);found=item;previous.append(q.tolist());previous=previous[-20:];break
  rows.append(dict(pos=point['pos'],region=point['region'],orientation=orient['id'],starts=seed+1,kinematic_solutions=kin_count,pass_=bool(found),witness=found,best=best))
  if len(rows)%24==0:
   rt.write(f'reachability/{layout}/{side}.json',dict(layout=layout,side=side,complete=False,rows=rows));print(layout,side,len(rows),sum(r['pass_'] for r in rows),round(time.monotonic()-began),flush=True)
out=dict(layout=layout,side=side,complete=True,config=cfg,model_sha256=hashlib.sha256(xml.encode()).hexdigest(),rows=rows,targets=len(rows),reachable=sum(r['pass_'] for r in rows),kinematic_reachable=sum(r['kinematic_solutions']>0 for r in rows),starts=sum(r['starts'] for r in rows),elapsed_s=time.monotonic()-began,blockers=[dict(pair=k.split(' | '),count=v) for k,v in blockers.most_common(20)],scope='Independent empty-EOAT arm reach/dexterity map with full original fixed kitchen and complete new rail/chain/mount hardware. Opposite arm excluded only from this per-arm map; full two-arm static/motion replay excludes no arm. Counter fixtures are deliberately not present to guide movable station placement. Not a meal/parking proof.')
rt.write(f'reachability/{layout}/{side}.json',out)
print(layout,side,'REACH',out['reachable'],'/',len(rows),'kinematic',out['kinematic_reachable'],'s',out['elapsed_s'],flush=True)
