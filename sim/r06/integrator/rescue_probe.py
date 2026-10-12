from rescue_cell import *
import argparse
p=argparse.ArgumentParser();p.add_argument('--variant',type=int,required=True);p.add_argument('--goal',default='pickup');p.add_argument('--product',default='carrot');p.add_argument('--lo',type=int,default=0);p.add_argument('--hi',type=int,default=24);a=p.parse_args()
cfg=config(a.variant);obj='output_'+a.product;loc=initial_locations(cfg);held=None if a.goal in ('pickup','pregrasp','retreat') else obj
station='dock_'+a.product if a.goal in ('pickup','pregrasp','lift','retreat') else 'wash_basin' if a.goal.startswith('wash') else 'process_cell'
origin=loc[obj] if station.startswith('dock') else seats(cfg)[station]
ch=Workcell(a.variant,held,loc);target=key_position(origin,cfg)
if a.goal in ('pregrasp','lift','wash_pre','process_pre','retreat'):target=target+[0,0,.08]
if held:ch.contact_windows=ch.window(obj,station,origin)
else:ch.capture(obj,origin)
model=f'v2/models/L{a.variant}_{a.product}_{a.goal}.xml';(H/model).parent.mkdir(parents=True,exist_ok=True);(H/model).write_text(ch.xml)
rng=np.random.default_rng(606000+a.variant*10000+a.lo);rows=[];beg=time.monotonic()
for k in range(a.lo,a.hi):
 q=ch.q0.copy()
 for n in ch.variables:
  lo,hi=ch.m.jnt_range[ch.jid[n]];q[ch.qa[n]]=rng.uniform(max(-math.pi,lo),min(math.pi,hi))
 row=ch.collision_solve(target,ch.rot,q,seconds=20);row['seed']=k
 hs=hand(ch,target);tq,gr,cases=check_load(ch,np.array(row['q']),hs);row.update(torque_ratio=tq,grip_margin=gr,force_cases=cases,pass_=row['okay'] and tq<=1 and gr>=1,torque_envelope_orientation_provisional=cfg['angle']!=155)
 rows.append(row);write(f'v2/probes/L{a.variant}_{a.product}_{a.goal}_{a.lo}_{a.hi}.json',dict(config=cfg,goal=a.goal,product=a.product,station=station,target_m=target.tolist(),held=held,rows=rows,starts_completed=len(rows),elapsed_s=time.monotonic()-beg,xml=model))
 print(k,a.goal,row['pass_'],round(row['elapsed_s'],2),round(row['reserve_mm'],3),row['reason'],flush=True)
print('PROBE',a.variant,a.goal,sum(r['pass_'] for r in rows),'/',len(rows),'elapsed',round(time.monotonic()-beg,2))
