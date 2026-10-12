"""Explain the large native contact depth in a rejected direct-fold diagnostic."""
from v7_common import *
from planner_r05 import Planner
idle=read('idle.json');r=next(x for x in idle['task_fold']['attempts'] if x['name']=='direct')
ch=v.scene(0);ch.xml=(I/r['motion_model_xml']).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False
pl=Planner(ch,{},seconds=65);ib=IndependentBound(ch);a=np.array(r['start_q']);b=np.array(r['goal_q']);D=ib.segment(a,b);N=max(1,math.ceil(D/.004))
reject=json.loads((O/'fold.json').read_text())['routes'][0]['blocker']['rejection'];q0=np.array(reject['q']);alpha=float((q0-a)@(b-a)/np.sum((b-a)**2));k=round(alpha*N);rows=[]
ga=ch.gnames.index('secondary_side_guard-1');gb=ch.gnames.index('R_finger_minus')
for j in (k-2,k-1,k):
    q=a+(b-a)*j/N;valid=pl.state(q,{});mujoco.mj_forward(ch.m,ch.d)
    pairs=[dict(dist_mm=float(c.dist*1000),pos=c.pos.tolist()) for c in ch.d.contact[:ch.d.ncon] if set(map(int,c.geom))=={ga,gb}]
    ra=ch.d.geom_xmat[ga].reshape(3,3);rb=ch.d.geom_xmat[gb].reshape(3,3);axes=[*ra.T,*rb.T]+[np.cross(x,y) for x in ra.T for y in rb.T]
    assert ch.m.geom_type[ga]==ch.m.geom_type[gb]==6
    sat=max((abs((ch.d.geom_xpos[gb]-ch.d.geom_xpos[ga])@(u/np.linalg.norm(u)))-abs(ra.T@(u/np.linalg.norm(u)))@ch.m.geom_size[ga]-abs(rb.T@(u/np.linalg.norm(u)))@ch.m.geom_size[gb]) for u in axes if np.linalg.norm(u)>1e-10)
    rows.append(dict(grid=j,valid=valid,pair=ch.bounds.pair(ga,gb),independent_box_projection_gap_mm=float(sat*1000),native=pairs,blocker=copy.deepcopy(pl.last) if not valid else None))
dump('direct_gap_probe.json',dict(intervals=N,index=k,point_bound_mm=D/N*1000,actual_sphere_step_mm=ib.actual(a+(b-a)*(k-1)/N,a+(b-a)*k/N)*1000,rows=rows))
print('GAP_PROBE',N,k,[(x['grid'],x['valid'],x['pair'],x['native']) for x in rows])
