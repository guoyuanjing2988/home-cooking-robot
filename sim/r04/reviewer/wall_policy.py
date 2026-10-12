"""Probe the inherited fixed wall-mount reference exclusion explicitly."""
from geometry import *
ch,hands=mo.empty_cell();mujoco.mj_forward(ch.m,ch.d)
wall=ch.gnames.index('north_wall');rows=[]
for g,n in enumerate(ch.gnames):
 if not n.startswith('wall_mount_'):continue
 va,vb=points(ch,wall),points(ch,g);pr=qp(va,vb)
 rows.append(dict(pair=['north_wall',n],**pr,strict_10mm_proved=pr['lower_m']>=.01-1e-6,wall_weld_id=int(ch.weld[wall]),mount_weld_id=int(ch.weld[g]),same_weld=bool(ch.weld[wall]==ch.weld[g]),wall_robot=bool(ch.robot[wall]),mount_robot=bool(ch.robot[g])))
dump('wall_policy_probe.json',dict(inherited_exclusion='reference.forbidden and final_check.required skip north_wall versus every wall_mount_ geom. This predates R04 and is not in the task-intended ledger.',rows=rows,all_fixed_pairs_strict_10mm_proved=all(r['strict_10mm_proved'] for r in rows),all_pairs_already_same_weld=all(r['same_weld'] for r in rows),moving=False,scope='Audit name exclusion versus unchanged welded/adjacent mechanical semantics; mounting is not a task-intended contact permission.'))
print('fixed wall mount strict gap',all(r['strict_10mm_proved'] for r in rows),[(r['pair'][1],r['lower_m']*1000) for r in rows])
