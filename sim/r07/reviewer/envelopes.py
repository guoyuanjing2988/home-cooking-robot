from common import *
import xml.etree.ElementTree as E
env=read('torque_envelope.json');root=E.parse(I/'models/aux_empty_fixed_kitchen.xml');m=mujoco.MjModel.from_xml_string(E.tostring(root.getroot(),encoding='unicode'));d=mujoco.MjData(m)
ch=object.__new__(rt.Checker);ch.desc=s.ck.hand([0,0,1],jaw_axis=[0,1,0]);ch.bind_model(m)
for side in ('R','L'):
    for name in (side+'_tool',side+'_jaw_minus',side+'_jaw_plus'):
        bid=m.body(name).id;m.body_mass[bid]=1e-9;m.body_inertia[bid]=1e-12
mujoco.mj_setConst(m,d);rows=[];jp=np.zeros((3,m.nv));jr=np.zeros_like(jp)
for name,w in env['witnesses'].items():
    side=name[0];d.qpos[:]=m.qpos0
    for joint,v in zip(s.ck.ARMS[side],w['joints_rad']):d.qpos[ch.qa[joint]]=v
    mujoco.mj_forward(m,d);site=m.site(side+'_attachment_site').id;R=d.site_xmat[site].reshape(3,3);local=np.array(w['CoM_flange_m']);point=d.site_xpos[site]+R@local
    mujoco.mj_jac(m,d,jp,jr,point,m.site_bodyid[site]);demand=float(abs(d.qfrc_bias[ch.da[name]]+49.05*jp[2,ch.da[name]]))
    qok=all(m.jnt_range[ch.jid[j],0]<=v<=m.jnt_range[ch.jid[j],1] for j,v in zip(s.ck.ARMS[side],w['joints_rad']))
    comok=np.linalg.norm(local)<=.350+1e-8 if side=='R' else np.linalg.norm(local[:2])<=.030+1e-8 and -.00000001<=local[2]<=.01500001
    collisions=[]
    for ct in d.contact[:d.ncon]:
        a,b=map(int,ct.geom)
        if ct.dist>=-1e-8 or not all(ch.gnames[g].startswith(side+'_') for g in (a,b)):continue
        if any(any(k in ch.gnames[g] for k in ('palm','finger','plate','mount','carriage','brake')) for g in (a,b)):continue
        if f.required(ch,a,b) is not None:collisions.append(dict(pair=[ch.gnames[a],ch.gnames[b]],gap_mm=float(ct.dist*1000)))
    rows.append(dict(joint=name,independent_Nm=demand,saved_Nm=ENV[name],delta_Nm=abs(demand-ENV[name]),public_ranges_ok=qok,OEM_CoM_boundary_ok=bool(comok),OEM_self_hits=collisions))
# Full original-shape support for arm + EOAT + moving mount/carriage, at bare tuck.
root=E.parse(I/'models/aux_empty_fixed_kitchen.xml');mm=mujoco.MjModel.from_xml_string(E.tostring(root.getroot(),encoding='unicode'));ch.bind_model(mm);ch.hands={};ch.allowed=[];q=np.array(read('aux_paths.json')['path'][0]);f.contacts(ch,q);fold=[]
for side in ('R','L'):
    geos=[]
    for g,n in enumerate(ch.gnames):
        if not ch.robot[g] or not n.startswith(side+'_'):continue
        lo=[ch.bounds.support(g,-v)[k] for k,v in enumerate(np.eye(3))];hi=[ch.bounds.support(g,v)[k] for k,v in enumerate(np.eye(3))];geos.append((lo,hi))
    lo=np.min([g[0] for g in geos],axis=0);hi=np.max([g[1] for g in geos],axis=0)
    fold.append(dict(side=side,dimensions_m=(hi-lo).tolist(),lo_m=lo.tolist(),hi_m=hi.tolist()))
dump('envelopes.json',dict(rated_witnesses=rows,max_delta_Nm=max(r['delta_Nm'] for r in rows),folded_envelopes=fold,main_capability_kg=3,main_EOAT_kg=1.2,main_total_kg=4.2,main_capability_path_witness=False,helper_task_cap_kg=.25,helper_EOAT_kg=1.5,method='Independent mass-point Jacobian reconstruction of saved rated-envelope witnesses on actual R07 mounting, replacing EOAT with total OEM 5kg rated payload. Fold boxes include full copied collision solids, fingers, EOAT and declared moving mounting hardware. Feasible maxima are conservative denominators; no claim of continuous output torque or global optimum.'))
print('envelopes delta',max(r['delta_Nm'] for r in rows),'fold',fold)
