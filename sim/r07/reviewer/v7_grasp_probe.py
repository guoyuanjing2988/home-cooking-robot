from v7_common import *
sys.argv.insert(1,v.ID)
from binding_v7_r07 import admitted_pairs,Planner
from v7_registry import restore_registry
r=read('connections_v7/L101/8.json');leg=next(l for l in r['legs'] if l['grasp_window'])
ch=v.scene(r['from_stroke']['index']);ch.xml=(I/leg['model_xml']).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml))
checks=restore_registry(ch,leg['state']);ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False;pl=Planner(ch,{},seconds=65)
q=np.array(leg['planner']['path'][-1]);q[ch.qa['R_jaw_minus']]=q[ch.qa['R_jaw_plus']]=.020
w=leg['grasp_window'];out=[]
variants=[('genuine',{}),('foreign_object',dict(object_id='food:potato')),('foreign_support',dict(support_id='persistent_food_potato_grasp_faces')),('nonexistent',dict(object_id='nonexistent',support_id='nonexistent')),('working_on_transfer',dict(kind='working_stroke')),('forged_parts',dict(parts=['persistent_food_potato_food'])),('forged_frame',dict(tcp_origin_m=[9,9,9])),('forged_fingers',dict(fingers=['R_geom_17'])),('enlarged_window',dict(max_window_mm=51)),('forged_normal',dict(normal=[0,0,1]))]
for name,change in variants:
    ww=dict(w,**change);ch.pending_grasp=None;without=pl.state(q,{});ch.pending_grasp=ww;withwin=pl.state(q,{});pairs=admitted_pairs(ch,ww)
    out.append(dict(test=name,base_pass=without,window_pass=withwin,pairs=[sorted(x) for x in pairs],pass_=bool(pairs)==(name=='genuine') and (withwin if name=='genuine' else not withwin)))
ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d);reg=ch.registered_grasp_faces;ch.registered_grasp_faces={};no_registry=not admitted_pairs(ch,w);ch.registered_grasp_faces=reg
gi=ch.gnames.index(w['parts'][0]);ch.d.geom_xpos[gi,0]+=.001;stale=not admitted_pairs(ch,w)
dump('grasp_identity_probe.json',dict(tests=out,registry_checks=checks,no_registry_rejected=no_registry,stale_frame_rejected=stale,pass_=all(x['pass_'] for x in out) and no_registry and stale))
print('GRASP',[(x['test'],x['window_pass'],x['pass_']) for x in out],no_registry,stale)
