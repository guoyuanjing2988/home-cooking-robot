"""Required preservation, witness, standalone-scene and output-size verification."""
import os
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[n]='1'
import json,hashlib,ast,subprocess,time,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np,mujoco
import checker as ck
from run import identifier,delta
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def functions(code):
    out={}
    for n in ast.walk(ast.parse(code)):
        if isinstance(n,ast.FunctionDef):out[n.name]=ast.dump(n,include_attributes=False)
    return out
def main():
    start=time.monotonic();a=json.loads((HERE/'audit/checker_ast.json').read_text());inp=ROOT/'inputs/prep_checker.py'
    assert hashlib.sha256(inp.read_bytes()).hexdigest()==a['input_sha256']
    original=functions(inp.read_text());adapted=functions((HERE/'checker.py').read_text())
    for name in [f'P{i:02}' for i in range(1,17)]+['torque','grip','run_seed','run_phase','summarize','add_held']:
        assert original[name]==adapted[name],name
    gold=functions((ROOT/'inputs/mandoline_golden.py').read_text());newgold=functions((HERE/'golden.py').read_text())
    for name in ('torque_ratios','grasp_rot','build'):assert gold[name]==newgold[name],name
    rec=dict(input_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'inputs').iterdir() if p.is_file()},checker_AST=a,
      golden_AST_unchanged=[n for n in gold if gold[n]==newgold.get(n)],checked_poses=0,admitted_strokes=0,max_frozen_delta=0.,max_torque_recompute_delta=0.,designs=[])
    best=json.loads((HERE/'results/best.json').read_text());configs=json.loads((HERE/'results/chosen_configs.json').read_text())
    for c in configs:
        ck.configure(c);n=0
        for pid in ck.PHASES:
            r=json.loads((HERE/'results/final'/identifier(c)/f'{pid}.json').read_text());assert r['seeds']>=96 and len(r['rows'])==r['seeds']
            for si,seg in enumerate(r['definition']['segments']):
                ch=ck.Checker(r['definition'],seg,delta(pid));frozen=ck.BASE+ck.JAWS+sum([names for side,names in ck.ARMS.items() if side!='R'],[])
                for row in r['rows']:
                    part=row['segments'][si]
                    if len(part['poses'])==2:
                        q1,q2=[np.asarray(po['q']) for po in part['poses']];v=max(abs(q1[ch.qa[name]]-q2[ch.qa[name]]) for name in frozen)
                        rec['max_frozen_delta']=max(rec['max_frozen_delta'],float(v));assert v<1e-9
                    if not part.get('ok'):continue
                    rec['admitted_strokes']+=1;n+=1;worst=0.
                    for pi,po in enumerate(part['poses']):
                        assert all(e['position_mm']<=5 and e['orientation_deg']<=3 for e in po['errors'])
                        q=np.asarray(po['q']);ch.environment_pose(pi);assert not ch.forbidden(q)
                        for name in ck.JOINTS:
                            lo,hi=ch.m.jnt_range[ch.jid[name]];assert lo-1e-7<=q[ch.qa[name]]<=hi+1e-7
                        hd=seg['poses'][pi]['R']
                        for force in hd['nominal_forces_N']:
                            tq=ch.torque(q,hd,force);gr=ch.grip(q,hd,force);assert tq['ratio']<=1+1e-7 and gr['margin']>=1-1e-7;worst=max(worst,tq['ratio'])
                        rec['checked_poses']+=1
                    err=abs(worst-part['nominal']['torque']['ratio']);rec['max_torque_recompute_delta']=max(rec['max_torque_recompute_delta'],err);assert err<1e-7
            if time.monotonic()-start>1100:raise TimeoutError('verification chunk')
        rec['designs'].append(dict(config=c,seeds_per_phase=96,admitted_strokes=n))
    # Standalone files refer only to copied local sources; no robot_v5 dependency.
    c=best['config'];ck.configure(c);p=ck.P06();ch=ck.Checker(p,p['segments'][0]);r=json.loads((HERE/'results/final'/identifier(c)/'P06.json').read_text())
    pool=[row for row in r['rows'] if row['ok']] or r['rows'];chosen=min(pool,key=lambda row:row['nominal']['torque']['ratio'] if row['nominal'] else 99);q=chosen['segments'][0]['poses'][-1]['q']
    for visual,name in ((False,'best_scene.xml'),(True,'best_scene_visual.xml')):
        ck.configure(dict(c,visual=visual));ch=ck.Checker(p,p['segments'][0]);dest=HERE/'models'/name;mujoco.mj_saveLastXML(str(dest),ch.m)
        tree=ET.parse(dest)
        for asset in tree.getroot().findall('.//asset/*'):
            if asset.get('file'):
                file=Path(asset.get('file'));assert file.is_relative_to(ROOT)
                asset.set('file',os.path.relpath(file,dest.parent).replace('\\','/'))
        keyframes=tree.getroot().find('keyframe')
        if keyframes is None:keyframes=ET.SubElement(tree.getroot(),'keyframe')
        ET.SubElement(keyframes,'key',name='P06_witness',qpos=' '.join(f'{x:.16g}' for x in q))
        tree.write(dest,encoding='unicode');loaded=mujoco.MjModel.from_xml_path(str(dest));assert loaded.nq==len(q)
        data=mujoco.MjData(loaded);mujoco.mj_resetDataKeyframe(loaded,data,0);mujoco.mj_forward(loaded,data)
    ck.json_write(HERE/'models/best_scene.json',dict(config=c,joint_names=[ch.m.joint(i).name for i in range(ch.m.njnt)],q=q,source_commits=best['source_commits'],keyframe='P06_witness',note='Load keyframe 0 to display the admitted P06 pose; source collision approximations and every T08 station are included.'))
    rec['output_bytes']=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file());assert rec['output_bytes']<2_000_000_000
    rec['elapsed_s']=time.monotonic()-start;rec['verdict']='PASS';ck.json_write(HERE/'audit/final_verification.json',rec)
    print('VERIFIED',rec['checked_poses'],'poses',rec['admitted_strokes'],'strokes',rec['max_frozen_delta'],'frozen delta',rec['output_bytes'],'bytes')
if __name__=='__main__':main()
