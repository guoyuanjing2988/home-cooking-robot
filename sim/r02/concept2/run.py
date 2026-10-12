import os,sys,json,time,argparse,csv,itertools,copy
sys.dont_write_bytecode=True
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[n]='1'
import numpy as np,mujoco
import xml.etree.ElementTree as ET
import model,adapter
H=model.HERE;O=H/'results'
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False))
def static_gate(c):
    tree,meta=model.build(c);m=mujoco.MjModel.from_xml_string(ET.tostring(tree.getroot(),encoding='unicode'));d=mujoco.MjData(m);mujoco.mj_forward(m,d)
    infra=[m.geom(n).id for n in meta['infrastructure_names'] if not any(s in n for s in ('_arch_','base_adapter','Z_column','onboard_controller'))]
    env=[g for g in range(m.ngeom) if m.geom_bodyid[g]==0 and m.geom(g).name!='floor']
    hits=[]
    for a in infra:
        for b in env:
            na,nb=m.geom(a).name,m.geom(b).name
            if na.startswith('wall_mount_') and nb=='north_wall':continue
            dist=mujoco.mj_geomDistance(m,d,a,b,.011,None)
            if dist<.01-1e-6:hits.append(dict(pair=[na,nb],gap_mm=float(dist*1000)))
    return hits
def setup():
    rows=[]
    mixtures=[['xArm6'],['UR5e'],['xArm6','UR5e'],['xArm6','xArm7'],['AUBO_i5'],['FR3']]
    for y0,count,tr,h,pitch,ori,armset in itertools.product((-.06,.12),(2,3,4),('passing_rails_cable','passing_xz_cable','end_transfer_busbar'),(1.20,1.23,1.28),(.44,.52),('inverted','down30'),mixtures):
        arms=(armset*((count+len(armset)-1)//len(armset)))[:count]
        c=dict(model.CONFIG,count=count,transport=tr,height=h,pitch=pitch,orientation=ori,arm=arms[0],arms=arms,switching=tr=='end_transfer_busbar',front_mount_y=y0)
        # Static geometry is arm-independent; cache each transport layout.
        key=(y0,count,tr,h,pitch,ori)
        if key not in cache:cache[key]=static_gate(c)
        rows.append(dict(id=f'c{len(rows):04}',config=c,static_hits=cache[key],static_viable=not cache[key]))
    write(O/'configs.json',rows)
    print('CONFIGS',len(rows),'STATIC_CLEAR',sum(r['static_viable'] for r in rows),flush=True)
def worker(cid,seeds,ids,stage):
    c=next(r['config'] for r in json.loads((O/'configs.json').read_text()) if r['id']==cid)
    for ph in adapter.process_instances():
        if ids and ph['id'] not in ids:continue
        path=O/stage/cid/(ph['id']+'.json')
        if path.exists() and json.loads(path.read_text())['seeds']>=seeds:continue
        r=adapter.run_instance(ph,c,seeds);r['model_revision']='ownership_and_CAD_sink_v3';write(path,r);print('RESULT',cid,ph['id'],r['feasible_seeds'],r['best_torque_ratio'],round(r['elapsed_s']),flush=True)
def baseline(ids):
    c=json.loads((model.ROOT/'sim/r01/concept/results/best.json').read_text())['config']
    ck=adapter.ck;ck.configure(c)
    for pid in ids:
        path=O/'baseline_r01'/(pid+'.json')
        if path.exists():continue
        dz=.05 if pid in ('P01','P03','P05') else -.08 if pid=='P11' else 0
        r=ck.normalize_result(ck.run_phase(pid,96,dz));r['config']=c;write(path,r)
        print('BASELINE',pid,r['feasible_seeds'],flush=True)
def aggregate():
    rows=[]
    for ent in json.loads((O/'configs.json').read_text()):
        c=ent['config'];r=dict(id=ent['id'],transport=c['transport'],count=c['count'],rails=c['count'],arms='/'.join(c['arms']),height=c['height'],pitch=c['pitch'],orientation=c['orientation'],switching=c['switching'],static_viable=ent['static_viable'],static_blocker=json.dumps(ent['static_hits'][:3]),stage='static',seeds=0,instances_tested=0,instances_passed=0,phases_passed=0,binding_rated_phases=0,worst_best_ratio=None)
        for stage in ('coarse','final'):
            files=list((O/stage/ent['id']).glob('Q*.json'))
            if files:
                rs=[json.loads(f.read_text()) for f in files];qids={s['logical_id'] for s in rs}
                r.update(stage=stage,seeds=min(s['seeds'] for s in rs),instances_tested=len(rs),instances_passed=sum(s['ok'] for s in rs),phases_passed=sum(all(s['ok'] for s in rs if s['logical_id']==q) for q in qids),worst_best_ratio=max((s['best_torque_ratio'] for s in rs if s['ok']),default=None))
        rows.append(r)
    with (O/'sweep.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    measured=[r for r in rows if r['stage']!='static'];measured.sort(key=lambda r:(-r['instances_passed'],not r['static_viable'],r['count'],r['worst_best_ratio'] or 999))
    write(O/'ranking.json',measured);print(json.dumps(measured[:12],indent=2))
cache={}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['setup','worker','baseline','aggregate','coarse']);p.add_argument('--config');p.add_argument('--configs',nargs='*');p.add_argument('--seeds',type=int,default=96);p.add_argument('--ids',nargs='*');p.add_argument('--stage',default='final');a=p.parse_args()
    if a.mode=='setup':setup()
    elif a.mode=='worker':worker(a.config,a.seeds,a.ids,a.stage)
    elif a.mode=='baseline':baseline(a.ids)
    elif a.mode=='coarse':
        for cid in a.configs:worker(cid,a.seeds,a.ids,'coarse' if a.stage=='final' else a.stage)
    else:aggregate()
