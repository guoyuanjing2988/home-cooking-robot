import json,copy,xml.etree.ElementTree as E
import numpy as np,mujoco
import r07_runtime as rt
import policy_r05 as policy
from motion_r05 import windows
from planner_r05 import Planner
rows=[]
for typ in ('eye_core_spoon','wash_pad'):
 candidates=[(p,sg) for p in rt.s.P['phases'] for sg in p['segments'] if any(h['held']==typ and any(c['kind']=='working_stroke' for c in h.get('contacts',[])) for h in sg['poses'][0].values())]
 ph,sg=candidates[0];ch=rt.s.Checker(ph,sg);q=np.array(rt.s.PARK);ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d)
 ws=windows(ch,q,sg['poses'][0]);w=next(x for x in ws if x['kind']=='working_stroke')
 ch.working_stroke=False;transit=policy.valid_window(ch,w)
 ch.working_stroke=True;work=policy.valid_window(ch,w)
 forged=dict(w,kind='grasp_release_support');mislabel=policy.valid_window(ch,forged)
 own=next(iter(rt.SUPPORT_REGISTRY[w['object_id']]));support=dict(w,kind='grasp_release_support',face=own,support_id=own)
 ch.working_stroke=False;own_support=policy.valid_window(ch,support)
 wrong_id=dict(support,object_id='another_object');wrong=policy.valid_window(ch,wrong_id)
 ch.contact_windows=ws;ch.working_stroke=False
 planner=Planner(ch,sg['poses'][0],seed=709,seconds=65);planner.state(q)
 actual_transit_leak=any(c.get('kind')=='working_stroke' for c in ch.allowed)
 row=dict(tool=typ,nonworking_work_permission=transit,planner_actual_nonworking_permission_leak=actual_transit_leak,declared_work_permission=work,mislabeled_food_as_tool_support_permission=mislabel,registered_own_support_permission=own_support,wrong_object_permission=wrong,pass_=not transit and not actual_transit_leak and work and not mislabel and own_support and not wrong)
 rows.append(row)
rt.write('contact_policy_regression.json',dict(pass_=all(x['pass_'] for x in rows),rows=rows,method='Semantic regression on compiled full-size scenes and actual TCP origins/rotations, including the actual Planner.state contact filter. This is not a trajectory certificate.',support_registry={k:sorted(v) for k,v in rt.SUPPORT_REGISTRY.items()},work_registry={k:sorted(v) for k,v in rt.WORK_REGISTRY.items()}))
print('policy regression',all(x['pass_'] for x in rows),rows)
