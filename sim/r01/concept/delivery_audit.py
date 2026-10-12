"""Final bounded integrity check of deliverables, not a new numerical sweep."""
import csv,hashlib,json,math,re,struct,subprocess,time
from pathlib import Path
import mujoco

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def finite(o):
    if isinstance(o,float):assert math.isfinite(o)
    elif isinstance(o,dict):
        for x in o.values():finite(x)
    elif isinstance(o,list):
        for x in o:finite(x)

def main():
    start=time.monotonic();verify=read(HERE/'audit/final_verification.json')
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'inputs').iterdir() if p.is_file()}
    assert hashes==verify['input_hashes']
    b=read(HERE/'results/best.json');finite(b)
    assert b['phases_passed']==10 and b['full_payload_service_verified'] is False
    designs=[]
    for d in b['designs']:
        phases=sorted((HERE/'results/final'/d['id']).glob('P*.json'))
        assert len(phases)==16
        for p in phases:
            r=read(p);finite(r);assert r['seeds']>=96
        g=read(HERE/f"results/golden/{d['config']['arm']}x{d['config']['count']}.json")
        finite(g);assert g['seeds']>=96 and len(g['rows'])==g['seeds']
        designs.append(dict(id=d['id'],phases=16,min_seeds=min(read(p)['seeds'] for p in phases),admitted_phases=d['phases_passed'],golden_seeds=g['seeds']))
    sweep=list(csv.DictReader((HERE/'results/sweep.csv').open(encoding='utf-8',newline='')))
    assert len(sweep)==754 and all(r['stage'] in ('static','coarse','refine','final') for r in sweep)
    assert any(r['id']==b['id'] and int(r['phases_passed'])==10 and int(r['seeds'])>=96 for r in sweep)
    sources=read(HERE/'sources/sources.json');revisions={}
    for name,folder in (('menagerie','menagerie'),('aubo','aubo_description'),('xArm6','xarm_ros')):
        value=subprocess.check_output(['git','-C',str(HERE/'sources'/folder),'rev-parse','HEAD'],timeout=20,text=True).strip()
        assert value==sources[name]['commit'];revisions[name]=value
    permanent=Path(sources['permanent_scene']['source'])
    assert hashlib.sha256(permanent.read_bytes()).hexdigest()==sources['permanent_scene']['sha256']
    images={}
    for name in ('washing','peeling','mandoline','parked','overview'):
        p=HERE/'renders'/f'{name}.png';buf=p.read_bytes();assert buf[:8]==b'\x89PNG\r\n\x1a\n'
        w,h=struct.unpack('>II',buf[16:24]);assert (w,h)==(1440,960) and max(w,h)<=1600
        images[name]=dict(width=w,height=h,bytes=len(buf),sha256=hashlib.sha256(buf).hexdigest())
    park=read(HERE/'renders/parked.validation.json');assert park['collision_free']
    models={}
    for name in ('best_scene.xml','best_scene_visual.xml'):
        p=HERE/'models'/name;m=mujoco.MjModel.from_xml_path(str(p))
        assert m.nkey>=1 and m.key('P06_witness').id==0
        models[name]=dict(nq=m.nq,nbody=m.nbody,ngeom=m.ngeom,nkey=m.nkey,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    post=ROOT/'posts/r01/concept.md';body=post.read_text(encoding='utf-8')
    assert body.startswith('本轮') and '1.473' in body and '577.1' in body
    assert len(re.findall(r'^\| P\d\d \|',body,flags=re.M))==16
    local_links=[]
    for target in re.findall(r'!?\[[^\]]+\]\(([^)]+)\)',body):
        if target.startswith(('http:','https:')):continue
        p=(post.parent/target).resolve();assert p.is_relative_to(ROOT) and p.exists();local_links.append(str(p.relative_to(ROOT)))
    resources={}
    for p in (HERE/'audit').glob('*.resource.json'):
        r=read(p);assert r['timeout_s']<1200 and r['peak_MiB']<1900 and r['exit_code']==0
        resources[p.name]={k:r[k] for k in ('elapsed_s','peak_MiB','timeout_s','exit_code')}
    files=[p for p in HERE.rglob('*') if p.is_file()]+[post]
    output_bytes=sum(p.stat().st_size for p in files);assert output_bytes<2_000_000_000
    result=dict(status='PASS',elapsed_s=time.monotonic()-start,input_hashes=hashes,source_commits=revisions,
        designs=designs,sweep_rows=len(sweep),images=images,standalone_models=models,report_bytes=post.stat().st_size,
        report_local_links=local_links,verified_admitted_poses=verify['checked_poses'],
        max_frozen_delta=verify['max_frozen_delta'],resources=resources,output_bytes=output_bytes,
        conditional_phases=b['phases_passed'],fully_verified_continuous_output_torque_phases=0,
        full_payload_service_verified=False,max_rail_moment_Nm=b['max_rail_moment_Nm'])
    (HERE/'audit/delivery.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','output_bytes','sweep_rows','conditional_phases','max_rail_moment_Nm')}))
if __name__=='__main__':main()
