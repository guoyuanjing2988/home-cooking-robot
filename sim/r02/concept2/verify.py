"""Final deliverable contract checks; no added robot acceptance rules."""
import os,sys,json,csv,hashlib,re
sys.dont_write_bytecode=True
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[n]='1'
from pathlib import Path
import numpy as np,mujoco
from PIL import Image
import model,adapter
H=model.HERE;O=H/'results';A=H/'audit';ROOT=model.ROOT

def main():
    contract=json.loads((A/'checker_contract.json').read_text());assert contract['reference_identical'] and all(contract['unchanged_core_AST'].values())
    assert (H/'reference.py').read_bytes()==(ROOT/'sim/r01/concept/checker.py').read_bytes()
    for path,digest in contract['inputs'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest
    for path,digest in json.loads((A/'source_models.json').read_text()).items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest
    files=sorted((O/'final_v4/c0684').glob('Q*.json'));assert len(files)==36
    instances={p['id'] for p in adapter.process_instances()};assert instances=={f.stem for f in files}
    rows=0;poses=0;strokes=0;max_frozen_delta=0.
    for f in files:
        r=json.loads(f.read_text());assert r['seeds']>=96 and len(r['parts'])==len(r['definition']['segments'])
        for si,part in enumerate(r['parts']):
            ch=adapter.Checker(r['definition'],r['definition']['segments'][si],r['config']);active=set(ch.seg['poses'][0]);frozen=adapter.ck.BASE+adapter.ck.JAWS+sum([ns for side,ns in adapter.ck.ARMS.items() if side not in active],[])
            assert len(part['rows'])==part['seeds']>=96 and {row['k'] for row in part['rows']}==set(range(part['seeds']))
            strokes+=1;rows+=len(part['rows'])
            for row in part['rows']:
                q0=np.array(row['poses'][0]['q'])
                for po in row['poses']:
                    q=np.array(po['q']);assert np.isfinite(q).all() and len(q)==ch.m.nq;poses+=1
                    delta=max(abs(q[ch.qa[n]]-q0[ch.qa[n]]) for n in frozen);max_frozen_delta=max(max_frozen_delta,delta);assert delta<1e-10
                if row['ok']:
                    assert not row['hits'] and len(row['poses'])==len(ch.seg['poses'])
                    assert all(e['position_mm']<=5 and e['orientation_deg']<=3 for po in row['poses'] for e in po['errors'])
                    assert row['nominal']['torque']['ratio']<=1 and row['nominal']['grip']['margin']>=1
            assert part['feasible_seeds']==sum(row['ok'] for row in part['rows'])
    resc=json.loads((A/'rescore_final_v4.json').read_text());assert len(resc['instances'])==36 and all(x['all_poses_errors_identical'] and x['zero_moment_load_ratios_identical'] for x in resc['instances'])
    for entry in resc['instances']:
        src=O/'final_v3'/entry['config']/(entry['instance']+'.json');dst=O/'final_v4'/entry['config']/(entry['instance']+'.json')
        assert hashlib.sha256(src.read_bytes()).hexdigest()==entry['source_sha256'];assert hashlib.sha256(dst.read_bytes()).hexdigest()==entry['output_sha256']
    base=[json.loads(f.read_text()) for f in (O/'baseline_r01').glob('P*.json')];assert len(base)==16 and all(r['seeds']>=96 for r in base)
    exact=json.loads((ROOT/'sim/r01/concept/results/best.json').read_text())['config'];assert all(r['config']==exact for r in base)
    sweep=list(csv.DictReader((O/'sweep.csv').open(newline='',encoding='utf-8')));assert len(sweep)==1296 and len({r['id'] for r in sweep})==1296
    assert {r['arms'] for r in sweep}=={'2','3','4'} and {r['mount_height_m'] for r in sweep}=={'1.2','1.23','1.28'}
    best=json.loads((O/'best.json').read_text());assert best['logical_phases_passed']==sum(p['nominal_pass'] for p in best['phases']);assert best['binding_phases_passed']==0 and not best['fully_verified']
    image_checks={}
    for name in ('overview','passing','washing','peeling','eye_core','root_cutting','greens_washing','greens_cutting','tomato_cutting','delivery','parked'):
        with Image.open(H/'renders'/(name+'.png')) as im:assert max(im.size)<=1600;image_checks[name]=list(im.size)
    xml_checks={}
    for f in (H/'models').glob('*.xml'):
        m=mujoco.MjModel.from_xml_path(str(f));xml_checks[f.name]=dict(nq=m.nq,ngeom=m.ngeom)
    report=(ROOT/'posts/r02/concept2.md').read_text(encoding='utf-8');assert '\u4e00'<=report[0]<='\u9fff'
    for link in re.findall(r'\]\((\.\./[^)]+)\)',report):assert ((ROOT/'posts/r02')/link).resolve().exists(),link
    total=sum(f.stat().st_size for f in H.rglob('*') if f.is_file())+(ROOT/'posts/r02/concept2.md').stat().st_size;assert total<2*1024**3
    resources=[json.loads(f.read_text()) for f in A.glob('*.resource.json')]
    assert all(r['timeout_s']<1200 and r['peak_MiB']<2048 for r in resources)
    result=dict(status='DELIVERABLE_CHECKS_PASS;ENGINEERING_ADMISSION_REMAINS_NEGATIVE',logical_phases=27,instances=36,strokes=strokes,seed_stroke_evaluations=rows,saved_poses=poses,maximum_frozen_coordinate_delta=max_frozen_delta,baseline_phases=16,sweep_rows=len(sweep),images=image_checks,compiled_models=xml_checks,total_output_bytes=total,resource_records=len(resources),checker_source_identical=True,input_and_source_hashes_unchanged=True)
    (A/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
