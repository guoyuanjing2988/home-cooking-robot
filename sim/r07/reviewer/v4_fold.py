from v4_common import *
from planner_r05 import Planner
data=read('idle.json');ch=v.scene(len(v.items)-1);ch.xml=(I/data['model_xml']).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False
ib=IndependentBound(ch);pl=Planner(ch,{},seconds=65);rows=[];rejects=[]
work=np.array(data['task_fold']['working_endpoint_reference']['poses'][0]['q']);park=np.array(data['task_fold']['periodic_park_q'])
def run(label,path,saved):
    states=0;step=0.;bad=None;mt=0.
    for a,b in zip(np.array(path),np.array(path)[1:]):
        D=ib.segment(a,b);N=max(1,math.ceil(D/.004));step=max(step,D/N*1000)
        for k in range(N+1):
            q=a+(b-a)*k/N;states+=1
            if not pl.state(q,{}):bad=dict(kind='gap',rejection=pl.last);break
            tq=ch.torque_multi(q,{},{});mt=max(mt,tq['ratio'])
            if tq['ratio']>1 or not all(not ch.m.jnt_limited[ch.jid[n]] or ch.m.jnt_range[ch.jid[n],0]-1e-8<=q[ix]<=ch.m.jnt_range[ch.jid[n],1]+1e-8 for n,ix in ch.qa.items()):bad=dict(kind='load/range');break
        if bad:break
    rows.append(dict(route=label,saved_path=saved,pass_=bad is None,states_checked=states,max_point_step_mm=step,max_torque_ratio=mt,blocker=bad));print('FOLD',label,bad is None,states,flush=True)
def rejection(label,result):
    last=result.get('last_rejection')
    if last:
        ok=pl.state(np.array(last['q']),{});rejects.append(dict(label=label,independently_rejected=not ok,blocker=pl.last if not ok else None))
for i,r in enumerate(data['task_fold']['attempts']):
    pp=r['planner'].get('path') or [work.tolist(),park.tolist()]
    run(f'task_{i}_fold',pp,bool(r['planner'].get('path')));run(f'task_{i}_unfold',list(reversed(pp)),bool(r['planner'].get('path')));rejection(f'task_{i}',r['planner'])
for i,r in enumerate(data['staged_fold']['attempts']):
    w=candidate(r['staging_stroke']);stage=mo.shortq(ch,park,np.array(w['poses'][0]['q']))
    pp=r.get('path') or [park.tolist(),stage.tolist(),mo.shortq(ch,stage,work).tolist()]
    run(f'stage_{i}_unfold',pp,bool(r.get('path')));run(f'stage_{i}_fold',list(reversed(pp)),bool(r.get('path')))
    for j,e in enumerate(r['edges']):rejection(f'stage_{i}_{j}',e)
alt=[]
for i,r in enumerate(data['alternative_fold_goals']['attempts']):
    candidate_record=json.loads((I/r['candidate_file']).read_text());q=np.array(r.get('park_q',candidate_record['q']));ok=pl.state(q,{})
    alt.append(dict(index=i,snapshot_geometry_pass=ok,blocker=None if ok else pl.last))
    if 'planner' in r:
        pp=r['planner'].get('path') or [work.tolist(),q.tolist()]
        run(f'alternative_{i}_fold',pp,bool(r['planner'].get('path')));run(f'alternative_{i}_unfold',list(reversed(pp)),bool(r['planner'].get('path')));rejection(f'alternative_{i}',r['planner'])
dump('fold.json',dict(routes=rows,rejections=rejects,alternative_snapshots=alt,states_checked=sum(r['states_checked'] for r in rows),saved_complete_routes=sum(r['saved_path'] for r in rows),full_idle_pass=False,method='All saved direct/staged/alternative attempts. Reproduce rejection states and diagnose both directions at <=4mm when no complete path is supplied. Doors are not checked against corridor.'))
