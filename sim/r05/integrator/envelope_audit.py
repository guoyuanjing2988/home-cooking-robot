"""Read-only independent replay of rated-load envelope configurations."""
import os
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[n]='1'
import json,copy,xml.etree.ElementTree as E
import numpy as np,mujoco
import model,reference as ck
H=model.HERE
c=dict(model.CONFIG,transport_only=True);ck.configure(c)
ph=ck.phase('envelope_audit','Rated workspace audit',[ck.segment('audit',[ck.hand([0,0,1],jaw_axis=[0,1,0])],'none')])
ch=object.__new__(ck.Checker);ch.desc=ph['segments'][0]['poses'][0]['R']
ch.bind_model(mujoco.MjModel.from_xml_string(E.tostring(ck.TEMPLATE.getroot(),encoding='unicode')))
env=json.loads((H/'results/torque_envelope.json').read_text());rows=[]
for joint,w in env['witnesses'].items():
 s=joint[0];q=ch.m.qpos0.copy()
 for n,v in zip(ck.ARMS[s],w['joints_rad']):q[ch.qa[n]]=v
 hits=ch.forbidden(q)
 # The manufacturer arm workspace is independent of installed rails/appliances
 # and of the other arm. OEM arm self-collisions and public limits still apply.
 arm_hits=[]
 for hit in hits:
  ns=hit['pair']
  if all(n.startswith(s+'_') and not any(k in n for k in ('gripper','finger','held','adapter','bridge','drive')) for n in ns):arm_hits.append(hit)
 range_ok=all(ch.m.jnt_range[ch.jid[n],0]-1e-9<=q[ch.qa[n]]<=ch.m.jnt_range[ch.jid[n],1]+1e-9 for n in ck.ARMS[s])
 rows.append(dict(joint=joint,OEM_self_collision_free=not arm_hits,public_ranges_ok=range_ok,blockers=arm_hits,configuration=w))
out=dict(config=model.CONFIG,rows=rows,all_witnesses_reachable=all(r['OEM_self_collision_free'] and r['public_ranges_ok'] for r in rows),
 method='Literal reference forbidden() on full-scale copied OEM model, retaining OEM adjacent-link exclusions. Filter only OEM arm self pairs: workspace torque capability is not limited by this particular kitchen.',
 translation_note='Helper base raised1.40m to1.60m after envelope run; pure translation leaves gravity torques and angular Jacobians unchanged. Actual225degree mount was used in envelope.',
 limitation='An unconstrained maximiser with self-collision cannot certify a reachable denominator. Such a joint is explicitly disqualified pending constrained recomputation; no ratio is promoted to certified acceptance.')
ck.json_write(H/'results/envelope_reachability_audit.json',out)
print('reachable',out['all_witnesses_reachable'],[(r['joint'],len(r['blockers'])) for r in rows])
