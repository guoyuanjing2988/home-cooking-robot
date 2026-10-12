"""Static rail inputs, separate from unchanged phase acceptance."""
import os
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[n]='1'
import json,time,math
from pathlib import Path
import numpy as np,mujoco
import checker as ck
from run import identifier,delta
HERE=Path(__file__).resolve().parent

def descendants(m,root):
    ids=[]
    for b in range(1,m.nbody):
        p=b
        while p and p!=root:p=int(m.body_parentid[p])
        if p==root:ids.append(b)
    return ids

def loads(ch,q,hd,force,payload,work_mass=False):
    m,d=ch.m,ch.d;d.qpos[:]=q;d.qvel[:]=0;mujoco.mj_forward(m,d)
    records={};pointloads=[]
    for side in ck.ARMS:
        origin=d.body(side+'_carriage').xpos.copy();ids=descendants(m,m.body(side+'_carriage').id)
        F=np.zeros(3);M=np.zeros(3)
        for b in ids:
            f=np.array([0,0,-9.81*m.body_mass[b]]);p=d.xipos[b].copy()
            F+=f;M+=np.cross(p-origin,f);pointloads.append((p,f))
        if side=='R':
            for p,f in ((d.site('R_work').xpos.copy(),np.asarray(force,float)),(d.site('R_work' if work_mass else 'R_mass').xpos.copy(),np.array([0,0,-payload*9.81]))):
                F+=f;M+=np.cross(p-origin,f);pointloads.append((p,f))
        else:
            site=d.site(side+'_prep');p=site.xpos+site.xmat.reshape(3,3)@ck.offset_vector(hd['mass_offset_m'])
            f=np.array([0,0,-payload*9.81]);F+=f;M+=np.cross(p-origin,f);pointloads.append((p.copy(),f))
        records[side]=dict(force_N=F.tolist(),force_norm_N=float(np.linalg.norm(F)),moment_Nm=M.tolist(),moment_norm_Nm=float(np.linalg.norm(M)),
            carriage_x_m=float(origin[0]),robot_mass_kg=float(sum(m.body_mass[ids])),payload_kg=payload,
            drive_ideal_static_N=float(abs(F[0])),drive_with_assumed_drag_N=float(abs(F[0])+.01*np.linalg.norm(F[1:])+15))
    z=origin[2];cantilevers={}
    for name,x,direction in (('left',-1.5,-1),('right',.55,1)):
        support=np.array([x,.60,z]);moment=np.zeros(3);F=np.zeros(3)
        for p,f in pointloads:
            if direction*(p[0]-x)>0:moment+=np.cross(p-support,f);F+=f
        L=(2.3-x) if direction==1 else (x+2.3)
        weight_per_m=(24+1.6*len(ck.ARMS))*9.81/4.6
        # Beam and carrier distributed weight, plus their 25mm wall offset.
        f=np.array([0,0,-weight_per_m*L]);p=np.array([x+direction*L/2,.575,z]);F+=f;moment+=np.cross(p-support,f)
        cantilevers[name]=dict(force_N=F.tolist(),moment_Nm=moment.tolist(),moment_norm_Nm=float(np.linalg.norm(moment)),unsupported_length_m=L)
    # Net rail wrench about wall-centre datum; this is NOT one bracket's reaction.
    datum=np.array([0,.60,z]);netF=np.zeros(3);netM=np.zeros(3)
    for p,f in pointloads:netF+=f;netM+=np.cross(p-datum,f)
    rail_weight=(24+1.6*len(ck.ARMS)+1.6+.001)*9.81
    netF+=[0,0,-rail_weight];netM+=np.cross([0,-.025,0],[0,0,-rail_weight])
    return dict(carriages=records,cantilevers=cantilevers,net_wall_force_N=netF.tolist(),net_wall_moment_Nm=netM.tolist())

def capacity_torque(ch,hd,force,work_mass=False):
    tau=ch.d.qfrc_bias.copy();jp=np.zeros((3,ch.m.nv));jr=np.zeros_like(jp)
    mujoco.mj_jacSite(ch.m,ch.d,jp,jr,ch.m.site('R_work').id);tau-=jp.T@np.asarray(force)
    mujoco.mj_jacSite(ch.m,ch.d,jp,jr,ch.m.site('R_work' if work_mass else 'R_mass').id);tau-=jp.T@np.array([0,0,-3*9.81])
    for side in ck.ARMS:
        if side=='R':continue
        sid=ch.m.site(side+'_prep').id;off=ch.d.site_xmat[sid].reshape(3,3)@ck.offset_vector(hd['mass_offset_m']);f=np.array([0,0,-3*9.81])
        mujoco.mj_jacSite(ch.m,ch.d,jp,jr,sid);tau-=jp.T@f+jr.T@np.cross(off,f)
    ratios={n:float(abs(tau[ch.da[n]])/ck.LIM[n]['continuous_Nm']) for n in ck.JOINTS};j=max(ratios,key=ratios.get)
    return dict(ratio=ratios[j],joint=j,joints=ratios)

def main():
    start=time.monotonic();best=json.loads((HERE/'results/best.json').read_text());c=best['config'];ck.configure(c)
    maxima={};cases=0;payload_torque={};deadline=start+1100
    def add(key,value,witness):
        if key not in maxima or value>maxima[key]['value']:maxima[key]=dict(value=float(value),witness=witness)
    for file in sorted((HERE/'results/final'/identifier(c)).glob('P*.json')):
        r=json.loads(file.read_text());pid=r['id'];definition=r['definition']
        for si,seg in enumerate(definition['segments']):
            ch=ck.Checker(definition,seg,delta(pid))
            # Include every IK-complete configuration, clearly flagging rejected poses.
            for row in r['rows']:
                part=row['segments'][si]
                if len(part['poses'])!=2 or any(max(e['position_mm']/5,e['orientation_deg']/3)>1 for po in part['poses'] for e in po['errors']):continue
                for pi,po in enumerate(part['poses']):
                    q=np.asarray(po['q']);hd=seg['poses'][pi]['R'];ch.environment_pose(pi)
                    for level in ('nominal','check'):
                        for force in hd[level+'_forces_N'] or []:
                            if time.monotonic()>deadline:raise TimeoutError('load chunk')
                            w=dict(phase=pid,segment=si,seed=row['k'],pose=pi,level=level,force_N=force,phase_admitted=bool(part.get('ok')),payload_kg=3.)
                            result=loads(ch,q,hd,force,3.);cases+=1
                            for side,a in result['carriages'].items():
                                for metric in ('force_norm_N','moment_norm_Nm','drive_ideal_static_N','drive_with_assumed_drag_N'):
                                    add('carriage_'+metric,a[metric],dict(w,side=side,result=a))
                            for side,a in result['cantilevers'].items():add('cantilever_moment_Nm',a['moment_norm_Nm'],dict(w,end=side,result=a))
                            add('net_wall_force_N',np.linalg.norm(result['net_wall_force_N']),dict(w,result=result))
                            add('net_wall_moment_Nm',np.linalg.norm(result['net_wall_moment_Nm']),dict(w,result=result))
                            tq=capacity_torque(ch,hd,force)
                            if part.get('ok'):add('admitted_pose_full_payload_torque_ratio',tq['ratio'],dict(w,torque=tq))
    # Golden q has exactly the same joint order and source link inertias. Its held
    # sphere differs from P06 only by negligible proxy masses; capacity load is external.
    golden=json.loads((HERE/'results/golden'/f"{c['arm']}x{c['count']}.json").read_text());p=ck.P06();ch=ck.Checker(p,p['segments'][0]);hd=dict(mass_offset_m=.08)
    for row in golden['rows']:
        if 'torque' not in row:continue
        for pi,key in enumerate(('q_start','q_end')):
            q=np.asarray(row[key])
            for feed in (40,70,100):
                for lat in (-10,10):
                    f=[-feed,lat,20];w=dict(phase='GOLDEN',seed=row['k'],pose=pi,level=f'feed_{feed}',force_N=f,phase_admitted=bool(row.get('ok')) and row['torque_unrounded'][str(feed)]<=1,payload_kg=3.)
                    result=loads(ch,q,hd,f,3.,work_mass=True);cases+=1
                    for side,a in result['carriages'].items():
                        for metric in ('force_norm_N','moment_norm_Nm','drive_ideal_static_N','drive_with_assumed_drag_N'):add('carriage_'+metric,a[metric],dict(w,side=side,result=a))
                    for side,a in result['cantilevers'].items():add('cantilever_moment_Nm',a['moment_norm_Nm'],dict(w,end=side,result=a))
                    add('net_wall_force_N',np.linalg.norm(result['net_wall_force_N']),dict(w,result=result));add('net_wall_moment_Nm',np.linalg.norm(result['net_wall_moment_Nm']),dict(w,result=result))
                    if w['phase_admitted']:add('admitted_pose_full_payload_torque_ratio',capacity_torque(ch,hd,f,True)['ratio'],w)
                    if time.monotonic()>deadline:raise TimeoutError('load chunk')
    out=dict(config=c,payload_sizing_kg=3.,tool_holder_mass_kg=1.2,cases=cases,maxima=maxima,elapsed_s=time.monotonic()-start,
      assumptions=['Static gravity plus original prescribed forces. Rail is frozen. No acceleration or impact.',
       'Every carriage carries 3 kg for capacity sizing. R uses the original R_mass site; unused arms use the same phase COM offset transformed from their prep sites. Phase acceptance is unchanged.',
       'Includes original golden 40/70/100 N, +/-10 N lateral and +20 N vertical cases at its saved IK poses. Golden mass is at the original R_work site.',
       'Drive estimate: |Fx| + 0.01*transverse load + 15 N cable drag. These are declared engineering allowances, not vendor data.',
       'Cantilever envelope treats each link COM as a point load beyond the outer supports x=-1.50,+0.55; beam/carrier weight is uniform. Support sharing and stiffness need structural design.',
       'Maxima include IK-complete rejected poses for conservative concept sizing; witness states admission. No claim of verified continuous-load operation.'])
    ck.json_write(HERE/'results/loads.json',out);print(json.dumps({k:v['value'] for k,v in maxima.items()},indent=2))
if __name__=='__main__':main()
