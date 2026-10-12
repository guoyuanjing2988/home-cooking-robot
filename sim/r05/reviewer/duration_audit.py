"""Independent common-progress profiles for every accepted isolated path."""
import os,sys,json,math
from pathlib import Path
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[n]='1'
import numpy as np,mujoco
import motion_audit as a
H=Path(__file__).resolve().parent;I=H.parent/'integrator';O=H/'results';S=json.loads((I/'results/schedule.json').read_text());rows=[]
def profile(ch,path,h,bound,other=None):
 duration=0;segments=[];maxspeed=0;maxacc=0;both=0
 hinges=[int(ch.m.jnt_qposadr[j]) for j in range(ch.m.njnt) if ch.m.jnt_type[j]==3];slides=[int(ch.m.jnt_qposadr[j]) for j in range(ch.m.njnt) if ch.m.jnt_type[j]==2]
 for x,y in zip(np.array(path),np.array(path)[1:]):
  dq=abs(y-x);vs=[];acc=[]
  for name in a.f.s.ck.JOINTS:
   d=dq[ch.qa[name]]
   if d>1e-12:vs.append(.35/d);acc.append(.35/d)
  for side in ('R','L'):
   d=dq[ch.qa[side+'_carriage_x']];v=.2 if h.get(side,{}).get('held','empty')=='empty' else .1
   if d>1e-12:vs.append(v/d);acc.append(.3/d)
  D=float(np.max(bound.B@dq));angle=sum(dq[hinges]);slide=sum(dq[slides]);C=bound.radius*angle**2+2*angle*slide
  if other:
   D=max(D,float(np.max(other.B@dq)));C=max(C,other.radius*angle**2+2*angle*slide)
  if D>1e-12:vs.append(.05/D);acc.append(.15/D)
  if C>1e-12:vs.append(math.sqrt(.15/C))
  v=min(vs) if vs else 0.;aa=min(acc) if acc else 0.;T=2*math.sqrt(1/aa) if v and 1<=v*v/aa else 1/v+v/aa if v else 0
  # True peak progress speed of triangular/trapezoidal rest-to-rest motion.
  peak=min(v,math.sqrt(aa)) if v else 0.;point_speed=D*peak;point_acc=D*aa+C*peak**2;maxspeed=max(maxspeed,point_speed);maxacc=max(maxacc,point_acc)
  active=[side for side in ('R','L') if any(dq[ch.qa[name]]>1e-8 for name in a.f.s.ck.ARMS[side]+[side+'_carriage_x'])];both+=int(len(active)==2)
  duration+=T;segments.append(dict(duration_s=T,point_speed_bound_m_s=point_speed,point_accel_bound_m_s2=point_acc,active_arms=active))
 return dict(duration_s=float(duration),segments=segments,max_point_speed_m_s=float(maxspeed),max_point_accel_m_s2=float(maxacc),two_arm_moving_segments=both)
for r in a.M['internal']:
 if not r['ok']:continue
 ph,sg,key=a.mo.items[r['index']];sg=r.get('segment_override',sg);ch=a.mo.scene(ph,sg,r['index']);bound=a.IndependentBound(ch);out=[profile(ch,e['path'],sg['poses'][0],bound) for e in r['edges']];T=sum(e['duration_s'] for e in out);submitted=S['path_catalog'][r['index']]['duration_s']
 rows.append(dict(kind='internal',index=r['index'],stroke=key,duration_s=T,submitted_duration_s=submitted,difference_s=T-submitted,max_point_speed_m_s=max(e['max_point_speed_m_s'] for e in out),max_point_accel_m_s2=max(e['max_point_accel_m_s2'] for e in out),two_arm_moving_segments=sum(e['two_arm_moving_segments'] for e in out)))
for r in a.M['between_strokes']:
 if not r['ok']:continue
 i=r['index'];ph,sg,key=a.mo.items[i];p2,s2,_=a.mo.items[i+1];ch=a.mo.scene(ph,sg,i);ch2=a.mo.scene(p2,s2,i+1);out=profile(ch,r['planner']['path'],sg['poses'][-1],a.IndependentBound(ch),a.IndependentBound(ch2));submitted=S['connection_path_catalog'][i]['duration_s'];rows.append(dict(kind='connection',index=i,**out,submitted_duration_s=submitted,difference_s=out['duration_s']-submitted))
result=dict(rows=rows,max_duration_difference_s=max(abs(r['difference_s']) for r in rows),max_point_speed_bound_m_s=max(r['max_point_speed_m_s'] for r in rows),max_point_accel_bound_m_s2=max(r['max_point_accel_m_s2'] for r in rows),simultaneous_accepted_segments=sum(r['two_arm_moving_segments'] for r in rows),internal_seconds=sum(r['duration_s'] for r in rows if r['kind']=='internal'),connection_seconds=sum(r['duration_s'] for r in rows if r['kind']=='connection'),verified_meal_time=None,proof='Independent serial-chain point speed D*sdot and acceleration D*sddot+C*sdot^2; rest at every retained waypoint. Two 0.15m/s^2 allocations total at most0.3. Jaw/event motion absent from admitted paths cannot be inferred into this catalog.')
(O/'duration_audit.json').write_text(json.dumps(result,indent=2));print('DURATION_AUDIT',len(rows),result['max_duration_difference_s'],result['max_point_speed_bound_m_s'],result['max_point_accel_bound_m_s2'],flush=True)
