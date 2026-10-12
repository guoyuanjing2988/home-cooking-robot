"""Saved front-stage joint limits; linear segments inherit endpoint interval bounds."""
from v7_common import *
data=read('idle.json');rows=[];cache={}
for group in ('front_fold','front_unfold','front_return','high_front_fold','high_front_unfold','high_front_return'):
    bundle=data[group]
    for r in bundle['attempts']:
        model=r.get('motion_model_xml',bundle['model_xml'])
        if model not in cache:
            ch=v.scene(0);ch.xml=(I/model).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));cache[model]=ch
        ch=cache[model]
        for ei,e in enumerate(r.get('edges',[])):
            if not e.get('path'):continue
            bad=[]
            for k,q in enumerate(e['path']):
                for name,adr in ch.qa.items():
                    lo,hi=ch.m.jnt_range[ch.jid[name]]
                    if not lo-1e-8<=q[adr]<=hi+1e-8:bad.append(dict(node=k,joint=name,q=q[adr],lo=float(lo),hi=float(hi)))
            rows.append(dict(group=group,candidate=r['candidate'],edge=ei,nodes=len(e['path']),pass_=not bad,violations=bad))
out=dict(rows=rows,pass_=all(x['pass_'] for x in rows),scope='Every node in every saved front-stage path against compiled joint ranges. Each segment is joint-linear, so endpoint interval membership certifies its range.')
dump('front_ranges.json',out);print(json.dumps(out,indent=2));assert out['pass_']
