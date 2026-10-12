"""Export MuJoCo geometry and exact solved configurations to a CPU Blender scene."""
import os,time,json,xml.etree.ElementTree as ET
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import numpy as np,mujoco
import checker as ck
from run import delta,identifier
HERE=Path(__file__).resolve().parent
OUT=HERE/'renders';OUT.mkdir(exist_ok=True)
def chosen_row(r):
    if r['composite_rows']:return r['composite_rows'][0]
    pool=[x for x in r['rows'] if x['ok']] or [x for x in r['rows'] if x['ik_ok']] or r['rows']
    return min(pool,key=lambda x:(not x['ok'],sum(len(s['hits']) for s in x['segments']),x['nominal']['torque']['ratio'] if x['nominal'] else 99))
def export(c,pid,q,label,status):
    ck.configure(dict(c,visual=True));definition=ck.PHASES[pid](delta(pid));ch=ck.Checker(definition,definition['segments'][0],delta(pid));m=ch.m;d=ch.d
    d.qpos[:]=q;mujoco.mj_forward(m,d)
    meshes={};geoms=[]
    # Same joint list/order; appearance-only shapes do not change qpos.
    visual_bodies={int(m.geom_bodyid[g]) for g in range(m.ngeom) if m.geom_contype[g]==0}
    for g in range(m.ngeom):
        n=m.geom(g).name
        if n in ('south_wall','south_cabinets') or n.startswith(('cabinet_door_sweep','outlet_access')):continue
        if int(m.geom_bodyid[g]) in visual_bodies and m.geom_group[g]==3:continue
        if 'held_' in n and m.geom_rgba[g,3]==0:continue
        kind=int(m.geom_type[g]);a=dict(name=n,type=kind,size=m.geom_size[g].tolist(),pos=d.geom_xpos[g].tolist(),rot=d.geom_xmat[g].reshape(3,3).tolist(),rgba=m.geom_rgba[g].tolist())
        mat=m.geom_matid[g]
        if mat>=0:a['rgba']=m.mat_rgba[mat].tolist()
        if kind==int(mujoco.mjtGeom.mjGEOM_MESH):
            idx=int(m.geom_dataid[g]);a['mesh']=str(idx)
            if str(idx) not in meshes:
                va=m.mesh_vertadr[idx];fa=m.mesh_faceadr[idx]
                meshes[str(idx)]=dict(vertices=m.mesh_vert[va:va+m.mesh_vertnum[idx]].tolist(),faces=m.mesh_face[fa:fa+m.mesh_facenum[idx]].tolist())
        geoms.append(a)
    (OUT/f'{label}.scene.json').write_text(json.dumps(dict(label=label,status=status,config=c,geoms=geoms,meshes=meshes)))
    print(label,len(geoms),len(meshes),flush=True)
def main():
    began=time.monotonic();best=json.loads((HERE/'results/best.json').read_text());c=best['config'];directory=HERE/'results/final'/identifier(c)
    for label,pid in [('washing','P02'),('peeling','P04'),('mandoline','P06'),('overview','P06')]:
        if time.monotonic()-began>180:raise TimeoutError('export 180sec')
        r=json.loads((directory/f'{pid}.json').read_text());row=chosen_row(r);part=row['segments'][0]
        q=part['poses'][-1]['q'];export(c,pid,q,label,'Admitted model pose; torque reference conditional' if row['ok'] else 'REJECTED diagnostic pose')
    # Use a real admitted witness for the parked image when possible; R arm's joints
    # copy L's independently cleared parking posture, and R moves to the right end.
    ck.configure(c);p=ck.P06();ch=ck.Checker(p,p['segments'][0]);q,_=ch.initial(np.random.default_rng(0),0)
    q[ch.qa['R_carriage_x']]=(-2.12 if c.get('parking')=='right' else 2.12) if c['count']==2 else -.40
    for rn,ln in zip(ck.ARMS['R'],ck.ARMS['L']):q[ch.qa[rn]]=q[ch.qa[ln]]
    hits=ch.forbidden(q)
    # Search parking at right end without changing scene or collision thresholds.
    rng=np.random.default_rng(412)
    for k in range(500):
        if not hits:break
        for n in ck.ARMS['R']:
            lo,hi=ch.m.jnt_range[ch.jid[n]];q[ch.qa[n]]=rng.uniform(lo,hi)
        hits=ch.forbidden(q)
    ck.json_write(OUT/'parked.validation.json',dict(q=q.tolist(),hits=hits,collision_free=not hits))
    export(c,'P06',q.tolist(),'parked','Collision-free parking' if not hits else 'REJECTED parking diagnostic')
if __name__=='__main__':main()
