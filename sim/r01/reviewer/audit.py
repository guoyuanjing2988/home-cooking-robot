"""Read-only evidence audit, independent diffs and admitted-pose diagnostics."""
import os
for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
import sys, ast, json, hashlib, difflib, re
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import mujoco
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];CONCEPT=HERE.parent/'concept'
sys.path.insert(0,str(CONCEPT));import checker as ck
AUDIT=HERE/'audit';AUDIT.mkdir(exist_ok=True)
def write(name,obj):(AUDIT/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False),encoding='utf-8')
def funcs(source):
    out={}
    for n in ast.parse(source).body:
        if isinstance(n,ast.FunctionDef):out[n.name]=ast.dump(n,include_attributes=False)
        elif isinstance(n,ast.ClassDef):
            for f in n.body:
                if isinstance(f,ast.FunctionDef):out[n.name+'.'+f.name]=ast.dump(f,include_attributes=False)
    return out
diffs={}
for original,adapted in [('prep_checker.py','checker.py'),('mandoline_golden.py','golden.py')]:
    a=(ROOT/'inputs'/original).read_text(encoding='utf-8');b=(CONCEPT/adapted).read_text(encoding='utf-8')
    (AUDIT/(adapted+'.diff')).write_text(''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='inputs/'+original,tofile='concept/'+adapted)),encoding='utf-8')
    fa,fb=funcs(a),funcs(b)
    diffs[original]=dict(unchanged=[k for k,v in fa.items() if fb.get(k)==v],changed=[k for k,v in fa.items() if fb.get(k)!=v],added=[k for k in fb if k not in fa])
write('rule_ast.json',diffs)
paths=list((ROOT/'inputs').glob('*'))+[ROOT/'posts/r01/concept.md',ROOT/'posts/r01/market.md']
paths+=list(CONCEPT.glob('*.py'))+list(CONCEPT.glob('models/*.xml'))+list(CONCEPT.glob('models/*.json'))
write('input_artifact_hashes.json',{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()})
best=json.loads((CONCEPT/'results/best.json').read_text());ck.configure(best['config'])
pdef=ck.P06();c=ck.Checker(pdef,pdef['segments'][0]);m=c.m
summary={}
for arm in ['xArm6','xArm7','UR5e','FR3','AUBO_i5']:
    from model import build,RATINGS
    tree,meta=build(dict(best['config'],arm=arm));mm=mujoco.MjModel.from_xml_string(ET.tostring(tree.getroot(),encoding='unicode'))
    ids=[i for i in range(mm.nbody) if mm.body(i).name.startswith('R_arm_')]
    summary[arm]=dict(source_arm_mass_kg=float(mm.body_mass[ids].sum()),torque_reference=meta['ratings'],limits_rad={n:mm.jnt_range[mm.joint(n).id].tolist() for n in meta['arms']['R']})
write('model_inventory.json',summary)
# Audit xArm6 conversion against the pinned official kinematics/inertias, not only against itself.
sys.path.insert(0,str(CONCEPT/'vendor'));import yaml
src=CONCEPT/'sources/xarm_ros/xarm_description'
kin=yaml.safe_load((src/'config/kinematics/default/xarm6_default_kinematics.yaml').read_text())['kinematics']
dyn=yaml.safe_load((src/'config/link_inertial/xarm6_type6_HT_BR2.yaml').read_text())
source=ET.parse(src/'urdf/xarm6/xarm6.urdf.xacro').getroot();mjcf=ET.parse(CONCEPT/'models/xarm6.xml').getroot()
fields=[]
from scipy.spatial.transform import Rotation
for i in range(1,7):
    b=mjcf.find(f".//body[@name='link{i}']");v=dyn[f'link{i}'];k=kin[f'joint{i}'];it=b.find('inertial')
    expected_inertia=[v['inertia'][key] for key in ('ixx','iyy','izz','ixy','ixz','iyz')]
    expected_quat=Rotation.from_euler('xyz',[k[key] for key in ('roll','pitch','yaw')]).as_quat()[[3,0,1,2]]
    fields.append(dict(link=i,mass_equal=abs(float(it.get('mass'))-v['mass'])<1e-10,
      com_equal=np.allclose(np.fromstring(it.get('pos'),sep=' '),[v['origin'][key] for key in ('x','y','z')]),
      inertia_equal=np.allclose(np.fromstring(it.get('fullinertia'),sep=' '),expected_inertia),
      position_equal=np.allclose(np.fromstring(b.get('pos'),sep=' '),[k[key] for key in ('x','y','z')]),
      quaternion_equal=np.allclose(np.fromstring(b.get('quat'),sep=' '),expected_quat),axis=b.find('joint').get('axis')))
write('xarm6_conversion.json',dict(fields=fields,official_total_mass_kg=12.5,model_total_mass_kg=summary['xArm6']['source_arm_mass_kg'],source_commit='aad7e1611c9c46eb719045414394bfdd42dcb0f8'))
# The current manufacturer's datasheet ranges are narrower than the pinned legacy xacro.
manual=np.radians([[-360,360],[-117,116],[-219,10],[-360,360],[-97,180],[-360,360]])
violations=[];phases=[];all_freeze=[]
worst3=None;capacity=[];replay_hits=[];ratio_error=0.;grip_min=100.;limit_min=100.;filtered=[]
for p in sorted((CONCEPT/'results/final'/best['id']).glob('P*.json')):
    r=json.loads(p.read_text());phasecheckers=[ck.Checker(r['definition'],seg,r.get('adjustment_parameter_m',0)) for seg in r['definition']['segments']]
    phaseviol=[];posecount=0;stroke_capacity=[];valid_stroke_counts=[]
    for si,cc in enumerate(phasecheckers):
        pool=[row['segments'][si] for row in r['rows'] if row['segments'][si].get('ok')]
        row3=[];valid_strokes=0
        for seg in pool:
            q0=np.array(seg['poses'][0]['q']);highest=0;recomputed_ratio=0.;in_current_range=True
            for pi,po in enumerate(seg['poses']):
                q=np.array(po['q']);posecount+=1
                cc.environment_pose(pi)
                replay_hits.extend(cc.forbidden(q))
                frozen=ck.BASE+ck.JAWS+ck.ARMS['L']
                all_freeze.append(max(abs(q[cc.qa[n]]-q0[cc.qa[n]]) for n in frozen))
                for side,names in ck.ARMS.items():
                    for ji,n in enumerate(names):
                        value=q[cc.qa[n]]
                        if value<manual[ji,0]-1e-8 or value>manual[ji,1]+1e-8:
                            in_current_range=False
                            hit=dict(phase=r['id'],segment=si,seed=seg['k'],pose=pi,joint=n,value_deg=float(np.degrees(value)),datasheet_deg=np.degrees(manual[ji]).tolist())
                            violations.append(hit);phaseviol.append(hit)
                hd=cc.seg['poses'][pi]['R'];hd3=dict(hd,held_kg=3.)
                for force in hd['nominal_forces_N']:
                    original_tq=cc.torque(q,hd,force);recomputed_ratio=max(recomputed_ratio,original_tq['ratio'])
                    grip_min=min(grip_min,cc.grip(q,hd,force)['margin'])
                    tq=cc.torque(q,hd3,force);highest=max(highest,tq['ratio'])
                    if worst3 is None or tq['ratio']>worst3['torque']['ratio']:
                        worst3=dict(phase=r['id'],segment=si,seed=seg['k'],pose=pi,force_N=force,torque=tq)
            row3.append(dict(seed=seg['k'],ratio=highest))
            ratio_error=max(ratio_error,abs(recomputed_ratio-seg['nominal']['torque']['ratio']))
            valid_strokes+=in_current_range
        valid_stroke_counts.append(valid_strokes)
        stroke_capacity.append(dict(segment=si,admitted_stroke_seeds=len(pool),capacity3_pass=sum(a['ratio']<=1 for a in row3),best_ratio=min((a['ratio'] for a in row3),default=None)))
    phases.append(dict(phase=r['id'],feasible_seeds=r['feasible_seeds'],admitted_stroke_pose_count=posecount,datasheet_violations=len(phaseviol)))
    capacity.append(dict(phase=r['id'],strokes=stroke_capacity))
    filtered.append(dict(phase=r['id'],datasheet_range_filtered_stroke_seeds=valid_stroke_counts,has_remaining_witness=all(valid_stroke_counts)))
write('datasheet_limit_audit.json',dict(model_deg=np.degrees(np.array(list(summary['xArm6']['limits_rad'].values()))).tolist(),datasheet_deg=np.degrees(manual).tolist(),violations=violations,phases=phases,max_frozen_drift_rad_or_m=max(all_freeze)))
write('capacity3_diagnostic.json',dict(note='Additional hardware-capacity diagnostic only. No prescribed phase mass, acceptance or force modified.',worst=worst3,phases=capacity))
write('phase_inventory.json',phases)
write('witness_replay.json',dict(poses=sum(a['admitted_stroke_pose_count'] for a in phases),forbidden_hits=replay_hits,nominal_ratio_max_recompute_error=ratio_error,minimum_grip_margin=grip_min,range_filtered_phases=filtered,range_filtered_phase_count=sum(a['has_remaining_witness'] for a in filtered)))
print(json.dumps(dict(diff_changed={k:v['changed'] for k,v in diffs.items()},model_masses={k:v['source_arm_mass_kg'] for k,v in summary.items()},datasheet_limit_violations=len(violations),max_frozen_drift=max(all_freeze),capacity3_worst=worst3),indent=2))
