from v5_common import *
schedule=read('schedule.json');rows=[]
for r in schedule['accepted_internal_paths']:
 saved=json.loads((I/r['source']).read_text());ch=v.scene(r['index']);ib=IndependentBound(ch);total=0.
 for edge in saved['edges']:
  for a,b in zip(np.array(edge['path']),np.array(edge['path'])[1:]):
   dq=abs(b-a);D=ib.segment(a,b);inverse_speed=max([D/.05,dq[ch.qa['R_carriage_x']]/.1]+[dq[ch.qa[n]]/.35 for n in s.ck.ARMS['R']]);inverse_accel=max([D/.3,dq[ch.qa['R_carriage_x']]/.3]+[dq[ch.qa[n]]/.35 for n in s.ck.ARMS['R']]);vmax=1/inverse_speed if inverse_speed else math.inf;amax=1/inverse_accel if inverse_accel else math.inf
   total+=2/math.sqrt(amax) if vmax*vmax>=amax else 1/vmax+vmax/amax
 rows.append(dict(index=r['index'],independent_s=total,submitted_s=r['duration_s'],difference_s=abs(total-r['duration_s'])))
dump('timing.json',dict(rows=rows,max_difference_s=max(r['difference_s'] for r in rows),isolated_total_s=sum(r['independent_s'] for r in rows),peeler_per_root_s=6*2*.16/.0034/.20,two_root_allowance_min=2*6*2*.16/.0034/.20/60,prep_min=None,scope='Rest-to-rest synchronized trapezoids with independent point bound. Isolated motion sum, not meal makespan; derived peeler design allowance, not measured appliance throughput.'))
print('TIMING',len(rows),max(r['difference_s'] for r in rows),sum(r['independent_s'] for r in rows),flush=True)
