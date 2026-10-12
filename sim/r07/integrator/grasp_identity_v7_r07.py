"""Adversarial grasp identity regression in a real compiled full-object world."""
import os,sys,json,copy
os.environ['R07_LAYOUT']=sys.argv[1]
import numpy as np,mujoco
import persistent_v7_r07 as p
from binding_v7_r07 import grasp_window,admitted_pairs
w=p.World();old=json.loads((p.v.O/'connections_v6/L84/8.json').read_text());leg=next(x for x in old['legs'] if x.get('grasp_window'));saved=leg['grasp_window']
ch,_=w.build(3,None);q=np.array(leg['planner']['path'][-1]);q[ch.qa['R_jaw_minus']]=q[ch.qa['R_jaw_plus']]=.020
# The old joint vector is only a fixture proposal. Register the full carrot at
# this mount's actual TCP, rather than its previous-layout world coordinates.
o=w.objects['food:carrot'];o['pose']=p.fk(ch,q).copy();ch,_=w.build(3,None)
ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d)
genuine=grasp_window(w,'food:carrot');checks={};rows=[]
def probe(name,window,expected):
 pairs=sorted([sorted(a) for a in admitted_pairs(ch,window)]);checks[name]=bool(pairs)==expected;rows.append(dict(name=name,admitted_pairs=pairs,expected_permission=expected,pass_=checks[name]))
probe('genuine_registered_carrot',genuine,True)
for name,change in [('foreign_object',dict(object_id='food:potato')),('foreign_support',dict(support_id='persistent_food_potato_grasp_faces')),('nonexistent_identities',dict(object_id='nonexistent',support_id='nonexistent')),('working_on_nonworking_path',dict(kind='working_stroke')),('forged_parts',dict(parts=['persistent_food_potato_food'])),('forged_frame',dict(tcp_origin_m=[9,9,9])),('forged_normal',dict(normal=[0,0,1])),('forged_finger',dict(fingers=['R_geom_17'])),('enlarged_window',dict(max_window_mm=51))]:
 bad=copy.deepcopy(genuine);bad.update(change);probe(name,bad,False)
registry=ch.registered_grasp_faces;ch.registered_grasp_faces={};probe('loaded_xml_without_live_registry',genuine,False);ch.registered_grasp_faces=registry
gi=ch.gnames.index(genuine['parts'][0]);ch.d.geom_xpos[gi,0]+=.001;probe('stale_actual_object_frame',genuine,False)
out=dict(layout=p.v.ID,pass_=all(checks.values()),checks=checks,rows=rows,scope='Real full carrot and registered support/grasp-face identities; old valid grasp endpoint is a test proposal only. No connection execution credit.')
(p.v.O/'grasp_identity_regression_v7.json').write_text(json.dumps(out,indent=2));print('GRASP_IDENTITY',out['pass_'],checks);assert out['pass_']
