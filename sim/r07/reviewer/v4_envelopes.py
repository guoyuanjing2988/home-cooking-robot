from v4_common import *
env=read(f'layouts/{v.ID}_envelope.json');ch=v.scene(0);m=ch.m;d=ch.d
for side in ('R',):
    for name in (side+'_tool',side+'_jaw_minus',side+'_jaw_plus'):
        bid=m.body(name).id;m.body_mass[bid]=1e-9;m.body_inertia[bid]=1e-12
mujoco.mj_setConst(m,d);rows=[];jp=np.zeros((3,m.nv));jr=np.zeros_like(jp)
for name,w in env['witnesses'].items():
    if name not in s.ck.JOINTS:continue
    side=name[0];d.qpos[:]=m.qpos0
    for joint,x in zip(s.ck.ARMS[side],w['joints_rad']):d.qpos[ch.qa[joint]]=x
    mujoco.mj_forward(m,d);site=m.site(side+'_attachment_site').id;rot=d.site_xmat[site].reshape(3,3);local=np.array(w['CoM_flange_m']);point=d.site_xpos[site]+rot@local;mujoco.mj_jac(m,d,jp,jr,point,m.site_bodyid[site]);demand=float(abs(d.qfrc_bias[ch.da[name]]+49.05*jp[2,ch.da[name]]))
    qok=all(m.jnt_range[ch.jid[j],0]<=x<=m.jnt_range[ch.jid[j],1] for j,x in zip(s.ck.ARMS[side],w['joints_rad']));comok=np.linalg.norm(local)<=.350+1e-8 if side=='R' else np.linalg.norm(local[:2])<=.030+1e-8 and -1e-8<=local[2]<=.01500001
    collisions=[]
    for ct in d.contact[:d.ncon]:
        a,b=map(int,ct.geom)
        if ct.dist>=-1e-8 or not all(ch.gnames[g].startswith(side+'_') for g in (a,b)):continue
        if any(any(k in ch.gnames[g] for k in ('palm','finger','plate','mount','carriage','brake')) for g in (a,b)):continue
        if f.required(ch,a,b) is not None:collisions.append(dict(pair=[ch.gnames[a],ch.gnames[b]],gap_mm=float(ct.dist*1000)))
    rows.append(dict(joint=name,independent_Nm=demand,saved_Nm=ENV[name],delta_Nm=abs(demand-ENV[name]),public_ranges_ok=qok,OEM_CoM_boundary_ok=bool(comok),OEM_self_hits=collisions))
dump('envelopes.json',dict(layout=v.ID,rated_witnesses=rows,max_delta_Nm=max(r['delta_Nm'] for r in rows),main_capability_kg=3,main_EOAT_kg=1.2,helper_task_cap_kg=.25,helper_EOAT_kg=1.5,method='Independent point Jacobian with OEM 5kg replacing total EOAT at submitted CoM in the actual L53 mount. Feasible maxima are conservative denominator estimates, not published continuous output ratings.'))
print('ENVELOPES',max(r['delta_Nm'] for r in rows),flush=True)
