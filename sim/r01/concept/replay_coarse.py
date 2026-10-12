"""Recheck saved IK configurations after robot carriage geometry refinement."""
import os
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[n]='1'
import json,time,copy,sys
from pathlib import Path
import numpy as np
import checker as ck
from run import delta
HERE=Path(__file__).resolve().parent
start=time.monotonic();changed=0;poses=0;files=0;stage=sys.argv[1] if len(sys.argv)>1 else 'coarse'
for directory in sorted((HERE/'results'/stage).iterdir()):
    if not directory.is_dir() or directory.name.startswith('group'):continue
    phasefiles=sorted(directory.glob('P*.json'))
    if not phasefiles:continue
    ck.configure(json.loads(phasefiles[0].read_text())['config'])
    for file in phasefiles:
        r=json.loads(file.read_text());definition=r['definition'];checkers=[ck.Checker(definition,s,delta(r['id'])) for s in definition['segments']]
        for row in r['rows']:
            for ch,part in zip(checkers,row['segments']):
                part['hits']=[];was_ik=part.get('blocker',{}).get('kind')=='IK';part.pop('ok',None)
                for pi,po in enumerate(part['poses']):
                    if any(max(e['position_mm']/5,e['orientation_deg']/3)>1 for e in po['errors']):break
                    ch.environment_pose(pi);part['hits'] += [dict(pose=pi,**hit) for hit in ch.forbidden(np.asarray(po['q']))];poses+=1
                if was_ik:continue
                if part['hits']:part['blocker']=dict(kind='collision',**min(part['hits'],key=lambda h:h['real_gap_mm']-h['required_gap_mm']))
                elif part['nominal']['torque']['ratio']>1:part['blocker']=dict(kind='torque',**part['nominal']['torque'])
                elif part['nominal']['grip']['margin']<1:part['blocker']=dict(kind='grip',**part['nominal']['grip'])
                else:part['ok']=True;part.pop('blocker',None)
            row['ok']=all(p.get('ok',False) for p in row['segments']);row['collision_free']=all(not p['hits'] for p in row['segments'])
            if row['ok']:row.pop('blocker',None)
            else:row['blocker']=next(p['blocker'] for p in row['segments'] if not p.get('ok',False))
        out=ck.normalize_result(ck.summarize(definition,r['rows'],r['elapsed_s'],delta(r['id'])))
        for key in ('config','rating_status'):out[key]=r[key]
        if 'sampling' in r:out['sampling']=r['sampling']
        out['binding_rated_admission']=False
        out['conditional_rated_reference_admission']=out['verdict']=='FEASIBLE' and r['config']['arm'] in ('xArm7','xArm6')
        out['robot_geometry_revision']='v7_arm_specific_mount_plates';out['reused_IK_solutions']=True
        changed += out['verdict']!=r['verdict'];files+=1;ck.json_write(file,out)
        if time.monotonic()-start>1100:raise TimeoutError('coarse contact replay bound')
ck.json_write(HERE/'audit'/f'{stage}_replay_v7.json',dict(files=files,poses=poses,changed_verdicts=changed,elapsed_s=time.monotonic()-start,
   reason='Arm-specific adapter envelopes: 140 mm xArm, 180 mm UR5e, 200 mm FR3/AUBO. Mass remains the relieved-plate budget within 8 kg carriage. Best xArm geometry is unchanged. Joint kinematics, limits, source collision shapes and force/grip rules unchanged. Replayed contacts at saved IK q.'))
print('REPLAY',files,poses,changed,time.monotonic()-start)
