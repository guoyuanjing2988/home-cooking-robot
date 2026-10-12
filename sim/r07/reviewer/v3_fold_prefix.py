from v3_common import *
from planner_r05 import Planner
from point_bound import PointBound
saved=read('layouts/L34_fold_continuation.json')
ch=v.scene(104);ch.xml=(I/saved['model_xml']).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False
ib=IndependentBound(ch);pb=PointBound(ch);rows=[]
for i,r in enumerate(saved['attempts']):
    if len(r.get('path',[]))<2:continue
    for direction,path in [('unfold_prefix',r['path']),('fold_prefix',list(reversed(r['path'])))]:
        pl=Planner(ch,{},seconds=65);states=0;bad=None;step=delta=ratio=0.
        for si,(a,b) in enumerate(zip(np.array(path),np.array(path)[1:])):
            D=ib.segment(a,b);delta=max(delta,abs(D-pb.segment_bound(a,b)));N=max(1,math.ceil(D/.004));step=max(step,D/N*1000)
            for k in range(N+1):
                q=a+(b-a)*k/N;states+=1
                if not pl.state(q,{}):bad=dict(segment=si,grid=k,rejection=pl.last);break
                ranges=all(ch.m.jnt_range[ch.jid[n],0]-1e-8<=q[ch.qa[n]]<=ch.m.jnt_range[ch.jid[n],1]+1e-8 for n in ch.qa)
                torque=ch.torque_multi(q,{},{});ratio=max(ratio,torque['ratio'])
                if not ranges or torque['ratio']>1:bad=dict(kind='range/load');break
            if bad:break
        rows.append(dict(attempt=i,side=r['side'],direction=direction,prefix_pass=bad is None,complete_fold_pass=False,submitted_goal_reached=r['pass_'],states_checked=states,max_point_step_mm=step,max_bound_delta_m=delta,max_holding_ratio=ratio,blocker=bad))
        print('PREFIX',i,direction,states,bad,flush=True)
dump('fold_prefix.json',dict(layout=v.ID,rows=rows,scope='All saved continuation prefixes replayed both directions; no complete route or meal-end return credit. Door sweep gate is10mm for all robot geometry. Front strip is a parked-state exclusion, not a ban on entering working counter during deployment.'))
