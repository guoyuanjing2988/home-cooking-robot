"""Replay the new front-staging routes and continuations, without new planning."""
from v7_common import *
import hashlib
from planner_r05 import Planner
data=read('idle.json');previous=json.loads((O/'front_paths.json').read_text());rows=previous['rows'];rejects=previous['rejections'];seen=set();attempts=[]
completed={(x['group'],x['candidate'],x['edge']) for x in rows}
rejected={(x['group'],x['candidate'],x['edge']) for x in rejects}
for group in ('front_fold','front_unfold','front_return','high_front_fold','high_front_unfold','high_front_return'):
    bundle=data[group]
    for r in bundle['attempts']:
        attempts.append((group,bundle,r))
for group,bundle,r in attempts:
    model=r.get('motion_model_xml',bundle['model_xml']);ch=v.scene(0);ch.xml=(I/model).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml))
    assert hashlib.sha256(ch.xml.encode()).hexdigest()==r.get('motion_model_sha256',bundle['model_sha256'])
    assert not any(n.startswith(('cabinet_door_sweep_','idle_full_sweep_cover_')) for n in ch.gnames)
    ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False;pl=Planner(ch,{},seconds=65);ib=IndependentBound(ch)
    for ei,e in enumerate(r.get('edges',[])):
        ident=hashlib.sha256(json.dumps([model,e.get('path'),e.get('last_rejection')],sort_keys=True).encode()).hexdigest()
        if ident in seen:continue
        seen.add(ident)
        key=(group,r['candidate'],ei)
        if key in completed or (not e.get('path') and key in rejected):continue
        last=e.get('last_rejection')
        if last and key not in rejected:rejects.append(dict(group=group,candidate=r['candidate'],edge=ei,reproduced=not pl.state(np.array(last['q']),{}),blocker=copy.deepcopy(pl.last)))
        path=e.get('path')
        if not path:continue
        count=0;step=0.;bad=None;mt=0.
        for direction,pth in [('forward',path),('reverse',list(reversed(path)))]:
            for a,b in zip(np.array(pth),np.array(pth)[1:]):
                D=ib.segment(a,b);N=max(1,math.ceil(D/.004));step=max(step,D/N*1000)
                for k in range(N+1):
                    q=a+(b-a)*k/N;count+=1
                    if not pl.state(q,{}):bad=copy.deepcopy(pl.last);break
                    mt=max(mt,ch.torque_multi(q,{},{})['ratio'])
                    if mt>1:bad={'reason':'load'};break
                if bad:break
            if bad:break
        rows.append(dict(group=group,candidate=r['candidate'],edge=ei,pass_=bad is None,states_checked=count,max_point_step_mm=step,torque_ratio=mt,blocker=bad))
        print('FRONT',group,r['candidate'],ei,bad is None,count,flush=True)
        dump('front_paths.json',dict(rows=rows,rejections=rejects,attempts_total=len(attempts),scope='Saved front-stage legs in both directions and rejection witnesses; incomplete routes receive no full folding credit.'))
dump('front_paths.json',dict(rows=rows,rejections=rejects,attempts_total=len(attempts),scope='Saved front-stage legs in both directions and rejection witnesses; incomplete routes receive no full folding credit.'))
