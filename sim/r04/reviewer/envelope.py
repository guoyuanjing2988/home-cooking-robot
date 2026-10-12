"""Independent rated-load, connected-path and idle-access replay."""
from reverify import *
import xml.etree.ElementTree as E
def envelope():
 tree,meta=s.model.build(dict(s.model.CONFIG,transport_only=True))
 m=mujoco.MjModel.from_xml_string(E.tostring(tree.getroot(),encoding='unicode'));d=mujoco.MjData(m)
 for side in s.model.SIDES:
  for n in (side+'_tool',side+'_jaw_minus',side+'_jaw_plus'):
   b=m.body(n).id;m.body_mass[b]=1e-9;m.body_inertia[b]=1e-12
 mujoco.mj_setConst(m,d)
 # Use literal reference for the arm's OEM self-collision, never installed
 # kitchen collisions to narrow the manufacturer's capability workspace.
 ch=object.__new__(s.ck.Checker);ch.desc=s.ck.hand([0,0,1],jaw_axis=[0,1,0]);ch.bind_model(m)
 env=json.loads((I/'results/torque_envelope.json').read_text());rows=[];jp=np.zeros((3,m.nv));jr=np.zeros_like(jp)
 for n,w in env['witnesses'].items():
  side=n[0];q=m.qpos0.copy()
  for joint,x in zip(meta['arms'][side],w['joints_rad']):q[ch.qa[joint]]=x
  d.qpos[:]=q;d.qvel[:]=0;mujoco.mj_forward(m,d)
  sid=m.site(side+'_attachment_site').id;point=d.site_xpos[sid]+d.site_xmat[sid].reshape(3,3)@np.array(w['CoM_flange_m'])
  mujoco.mj_jac(m,d,jp,jr,point,int(m.site_bodyid[sid]))
  tau=d.qfrc_bias+49.05*jp[2]
  demand=float(abs(tau[ch.da[n]]));off=np.array(w['CoM_flange_m'])
  com_ok=np.linalg.norm(off)<=.350+1e-9 if side=='R' else np.linalg.norm(off[:2])<=.030+1e-9 and -.000000001<=off[2]<=.015000001
  blockers=[h for h in s.ck.Checker.forbidden(ch,q) if all(a.startswith(('R_geom_',) if side=='R' else ('L_link',)) for a in h['pair'])]
  ranges=all(m.jnt_range[ch.jid[a],0]-1e-8<=q[ch.qa[a]]<=m.jnt_range[ch.jid[a],1]+1e-8 for a in meta['arms'][side])
  rows.append(dict(joint=n,rated_total_flange_kg=w['rated_payload_total_kg'],CoM_flange_m=w['CoM_flange_m'],CoM_chart_ok=bool(com_ok),point_Jacobian_static_Nm=demand,submitted_Nm=env['envelope_Nm'][n],delta_Nm=demand-env['envelope_Nm'][n],OEM_self_blockers=blockers,public_ranges_ok=bool(ranges)))
 rng=np.random.default_rng(93008);scan=[]
 for side in s.model.SIDES:
  names=meta['arms'][side];dofs=[ch.da[n] for n in names];bounds=np.array([m.jnt_range[ch.jid[n]] for n in names]);maximum=np.zeros(6)
  for k in range(8000):
   q=m.qpos0.copy();x=rng.uniform(bounds[:,0],bounds[:,1])
   for n,a in zip(names,x):q[ch.qa[n]]=a
   d.qpos[:]=q;mujoco.mj_forward(m,d);sid=m.site(side+'_attachment_site').id
   mujoco.mj_jacSite(m,d,jp,jr,sid);rt=d.site_xmat[sid].reshape(3,3)
   baseline=d.qfrc_bias[dofs]+49.05*jp[2,dofs]
   c=np.array([49.05*np.cross(jr[:,dofs].T,rt[:,i])[:,2] for i in range(3)]).T
   caps=abs(baseline)+.35*np.linalg.norm(c,axis=1) if side=='R' else np.maximum(abs(baseline),abs(baseline+.015*c[:,2]))+.03*np.linalg.norm(c[:,:2],axis=1)
   maximum=np.maximum(maximum,caps)
  scan.append(dict(side=side,seed=93008,samples=8000,unfiltered_sample_max_Nm=maximum.tolist(),submitted_envelope_Nm=[env['envelope_Nm'][n] for n in names],sample_to_submitted_ratios=[float(v/env['envelope_Nm'][n]) for n,v in zip(names,maximum)],note='Coverage sensitivity only; random configurations not collision-filtered and not substituted into capability denominators.'))
 out=dict(rows=rows,all_witnesses_valid=all(r['CoM_chart_ok'] and r['public_ranges_ok'] and not r['OEM_self_blockers'] and abs(r['delta_Nm'])<1e-6 and r['rated_total_flange_kg']==5 for r in rows),mount_angles_deg=dict(R=s.model.CONFIG['mount_deg'],L=s.model.CONFIG['helper_mount_deg']),gravity_world_m_s2=m.opt.gravity.tolist(),EOAT_replaced_by_total_rated_payload=True,workspace_sensitivity=scan,limitation='Submitted DE values are feasible conservative numerical maxima estimates. No numerical search certifies the global workspace maximum. Both arms use their actual mounting orientation; translation does not alter angular static gravity demands.')
 dump('envelope_independent.json',out);print('envelope',out['all_witnesses_valid'],flush=True)

if __name__=='__main__':envelope()
