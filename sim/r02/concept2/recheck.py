"""Literal contact restoration on the saved, unchanged 96-seed IK witnesses.

No optimization, pose, tolerance or grip-rule change is made here.
The original indexed rinse_basket work-face expansion is restored in adapter.
The handed-off eye/core free moments are included in the wrench plumbing.
The C06 held shorthand is resolved to the same delivered rectangular CAD shell
as the supported C06; inertial allocation and force/COM definitions are retained.
"""
import sys,os,copy,json,time,itertools,hashlib,collections
sys.dont_write_bytecode=True
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[n]='1'
import numpy as np
import adapter
H=adapter.HERE;O=H/'results'

def rescore(ch,old):
    out=copy.deepcopy(old);out.update(hits=[],nominal=None,check=None,ok=False)
    out.pop('blocker',None)
    for pi,po in enumerate(out['poses']):
        hands=ch.seg['poses'][pi];errors=po['errors'];ch.environment_pose(pi)
        if any(e['position_mm']>5 or e['orientation_deg']>3 for e in errors):
            out['blocker']=dict(kind='IK',pose=pi,**max(errors,key=lambda e:max(e['position_mm']/5,e['orientation_deg']/3)))
            return out
        q=np.array(po['q']);out['hits'] += [dict(pose=pi,**h) for h in ch.forbidden(q)]
        for level in ('nominal','check'):
            for forces,moments in adapter.wrench_cases(hands,level):
                tq=ch.torque_multi(q,hands,forces,moments=moments)
                gr=min((ch.grip_side(q,hd,forces[side],side,moments[side]) for side,hd in hands.items()),key=lambda x:x['margin'])
                case=dict(torque=tq,grip=gr,forces_N=forces,moments_Nm=moments,pose=pi)
                if out[level] is None:out[level]=case
                else:
                    if tq['ratio']>out[level]['torque']['ratio']:out[level]['torque']=tq;out[level]['forces_N']=forces;out[level]['pose']=pi
                    if gr['margin']<out[level]['grip']['margin']:out[level]['grip']=gr
    assert len(out['poses'])==len(ch.seg['poses'])
    if out['hits']:out['blocker']=dict(kind='collision',**min(out['hits'],key=lambda h:h['real_gap_mm']-h['required_gap_mm']))
    elif out['nominal']['torque']['ratio']>1:out['blocker']=dict(kind='torque',**out['nominal']['torque'])
    elif out['nominal']['grip']['margin']<1:out['blocker']=dict(kind='grip',**out['nominal']['grip'])
    else:out['ok']=True
    return out

def recheck(source,dest):
    audit=[]
    for f in sorted((O/source).glob('*/Q*.json')):
        began=time.monotonic();r=json.loads(f.read_text());parts=[];removed=0;changed=0;moment_plumbed=False;deltas=[]
        for si,part in enumerate(r['parts']):
            ch=adapter.Checker(r['definition'],r['definition']['segments'][si],r['config'])
            rows=[];hasmom=any(h.get('nominal_moments_Nm') or h.get('check_moments_Nm') for po in ch.seg['poses'] for h in po.values());moment_plumbed |= hasmom
            for old in part['rows']:
                row=rescore(ch,old)
                assert row['poses']==old['poses']
                for level in ('nominal','check'):
                    if old[level] is not None:
                        dt=abs(old[level]['torque']['ratio']-row[level]['torque']['ratio']);dg=abs(old[level]['grip']['margin']-row[level]['grip']['margin'])
                        if not hasmom:assert dt<1e-9 and dg<1e-9
                        deltas.append(dict(torque_ratio_change=dt,grip_margin_change=dg))
                removed+=len(old['hits'])-len(row['hits']);changed+=old['ok']!=row['ok'];rows.append(row)
            good=sorted([x for x in rows if x['ok']],key=lambda x:x['nominal']['torque']['ratio'])
            ik=[x for x in rows if x.get('blocker',{}).get('kind')!='IK'];cf=[x for x in ik if not x['hits']]
            pool=good or cf or ik
            chosen=min(pool,key=lambda x:x['nominal']['torque']['ratio']) if pool else rows[0]
            p=copy.deepcopy(part);p.update(rows=rows,best=chosen,feasible_seeds=len(good),ik_seeds=len(ik),collision_free_seeds=len(cf),blocker_counts=dict(collections.Counter(x.get('blocker',{}).get('kind') for x in rows if not x['ok'])))
            parts.append(p)
        passed=all(p['feasible_seeds'] for p in parts)
        r.update(parts=parts,ok=passed,conditional_reference_admission=passed,binding_rated_admission=False,feasible_seeds=min(p['feasible_seeds'] for p in parts),best_torque_is_feasible=passed,best_torque_ratio=max(p['best']['nominal']['torque']['ratio'] for p in parts if p['best']['nominal']) if any(p['best']['nominal'] for p in parts) else None,model_revision='original_workfaces_full_wrench_CAD_C06_v4',rescore_source=str(f.relative_to(H)),rescore_elapsed_s=time.monotonic()-began)
        path=O/dest/f.parent.name/f.name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(r,indent=2,allow_nan=False))
        entry=dict(instance=r['id'],config=f.parent.name,seeds=r['seeds'],source_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),output_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),all_poses_errors_identical=True,zero_moment_load_ratios_identical=True,supplied_eye_core_free_moment_plumbed=moment_plumbed,C06_rectangular_CAD_envelope=True,max_torque_ratio_change=max((d['torque_ratio_change'] for d in deltas),default=0),max_grip_margin_change=max((d['grip_margin_change'] for d in deltas),default=0),net_removed_contact_records=removed,changed_admissions=changed,elapsed_s=time.monotonic()-began)
        audit.append(entry);print('RECHECK',r['id'],r['feasible_seeds'],removed,round(entry['elapsed_s'],2),flush=True)
    (H/'audit'/('rescore_'+dest+'.json')).write_text(json.dumps(dict(source=source,dest=dest,rule='Source indexed workfaces retained;supplied eye/core free moment applied;C06CAD shell consistent;no new exemption or force',instances=audit),indent=2))

if __name__=='__main__':recheck(sys.argv[1],sys.argv[2])
