from v6_common import *
sys.argv.insert(1,v.ID)
from binding_v6_r07 import admitted_pairs,Planner
r=read('connections_v6/L84/8.json');leg=next(l for l in r['legs'] if l['grasp_window']);ch=v.scene(r['from_stroke']['index']);ch.xml=(I/leg['model_xml']).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False;pl=Planner(ch,{},seconds=65);q=np.array(leg['planner']['path'][-1]);q[ch.qa['R_jaw_minus']]=.020;q[ch.qa['R_jaw_plus']]=.020;ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d);w=leg['grasp_window'];out=[]
for name,change in [('original',{}),('wrong_object',{'object_id':'food:potato'}),('wrong_support',{'support_id':'persistent_food_potato_grasp_faces'}),('fake_object_support',{'object_id':'nonexistent','support_id':'nonexistent'}),('wrong_kind',{'kind':'working_stroke'})]:
 ww=dict(w,**change);pairs=admitted_pairs(ch,ww);ch.pending_grasp=None;without=pl.state(q,{});ch.pending_grasp=ww;with_window=pl.state(q,{});out.append(dict(test=name,window=ww,state_without_window=without,state_with_window=with_window,admitted_pairs=[sorted(x) for x in pairs]))
dump('grasp_identity_probe.json',dict(connection=8,leg=leg['name'],q=q.tolist(),tests=out));print([(x['test'],x['admitted_pairs']) for x in out])
