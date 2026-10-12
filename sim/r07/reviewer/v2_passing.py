from v2_common import *
from planner_r05 import Planner
saved=read('passing.json');ch=v.scene(2);ch.xml=(I/saved['model_xml']).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));hands=copy.deepcopy(v.items[2][1]['poses'][0])
for h in hands.values():h['contacts']=[]
ch.working_stroke=False;ch.contact_windows=[];a=np.array(candidate(2)['poses'][0]['q']);b=a.copy();ix=[ch.qa[s+'_carriage_x'] for s in ('R','L')];b[ix]=a[ix[::-1]];pl=Planner(ch,hands,seconds=65);ib=IndependentBound(ch);D=ib.segment(a,b);N=max(1,math.ceil(D/.004));first=None;states=0
for k in range(N+1):
    q=a+(b-a)*k/N;states+=1
    if not pl.state(q):first=dict(grid_index=k,rejection=pl.last);break
mid=np.array(saved['q_crossing']);pl.state(mid);crossing=pl.last;old=saved['planner'].get('last_rejection');rejected=None
if old:
    ok=pl.state(np.array(old['q']));rejected=dict(still_rejected=not ok,rejection=pl.last)
dump('passing.json',dict(layout=v.ID,pass_=False,saved_path_available=bool(saved['planner'].get('path')),straight_diagnostic_pass=first is None,states_checked=states,max_grid_bound_mm=D/N*1000,first_rejection=first,equal_carriage_x_rejection=crossing,saved_rejection_replay=rejected,submitted_budget_s=saved['planner']['allocated_budget_s'],submitted_actual_s=saved['planner']['planner_time_s'],two_arms_move=True,scope='Loaded carrot full-scene passing diagnostic and saved failure state; no wash/cut overlap or meal credit.'))
print('PASSING',states,first,flush=True)
