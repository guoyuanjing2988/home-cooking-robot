"""Foreground bounded chunks. At most two CPU workers, <=1900 MiB, <=1140 sec each."""
import os
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[n]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import argparse,json,time,subprocess,concurrent.futures,csv,math
from pathlib import Path
import numpy as np
import mujoco
import checker as ck
from model import CONFIG,RATINGS,build
HERE=Path(__file__).resolve().parent
RESULT=HERE/'results'; RESULT.mkdir(exist_ok=True)
def delta(pid): return .05 if pid in ('P01','P03','P05') else -.08 if pid=='P11' else 0.
def identifier(c):
    return f"{c['arm']}_{c['count']}_h{c['height']:.3f}_{c['orientation']}_s{c['standoff']:.3f}"+('_hang' if c.get('hanging') else '')+(f"_g{c['grip_extension']:.3f}" if c.get('grip_extension',.14)!=.14 else '')+('_parkright' if c.get('parking')=='right' else '')
def static_gate(c):
    tree,meta=build(c);m=mujoco.MjModel.from_xml_string(__import__('xml.etree.ElementTree',fromlist=['tostring']).tostring(tree.getroot(),encoding='unicode'));d=mujoco.MjData(m);mujoco.mj_forward(m,d)
    infra=[g for g in range(m.ngeom) if m.geom(g).name=='rail_beam' or m.geom(g).name.startswith(('wall_mount_','cable_carrier_track_'))]
    env=[g for g in range(m.ngeom) if m.geom_bodyid[g]==0]
    hits=[]
    for a in infra:
        for b in env:
            if m.geom(a).name.startswith('wall_mount_') and m.geom(b).name=='north_wall':continue
            gap=mujoco.mj_geomDistance(m,d,a,b,.0101,None)
            if gap<.010-1e-6:hits.append(dict(pair=[m.geom(a).name,m.geom(b).name],gap_mm=gap*1000))
    return hits
def setup():
    configs=[];deadline=time.monotonic()+1140; gates={}
    for arm in ('UR5e','xArm7','FR3','AUBO_i5','xArm6'):
        for h,hang in ((0,False),(.15,False),(.30,False),(.45,False),(.40,True)):
            for ori in ('horizontal','down30','down60','vertical','inverted'):
                for stand in (.05,.15,.25):
                    for count in (2,3):
                        if time.monotonic()>deadline:raise TimeoutError('setup chunk >1140s')
                        c=dict(arm=arm,count=count,height=h,orientation=ori,standoff=stand,hanging=hang)
                        gate_key=(h,count)
                        if gate_key not in gates:gates[gate_key]=static_gate(c)
                        configs.append(dict(id=identifier(c),config=c,static_hits=gates[gate_key]))
    ck.json_write(RESULT/'configs.json',configs)
    print('CONFIGS',len(configs),'static viable',sum(not c['static_hits'] for c in configs),flush=True)
def worker(cid,seeds,phases,stage):
    if cid.startswith('group'):
        manifest=json.loads((RESULT/'groups.json').read_text())
        for item in manifest[cid]:worker(item,seeds,phases,stage)
        return
    entries=json.loads((RESULT/'configs.json').read_text());c=next(e['config'] for e in entries if e['id']==cid)
    ck.configure(c);outdir=RESULT/stage/cid;outdir.mkdir(parents=True,exist_ok=True)
    began=time.monotonic()
    for pid in phases:
        p=outdir/f'{pid}.json'
        if p.exists() and json.loads(p.read_text())['seeds']>=seeds:continue
        r=ck.normalize_result(ck.run_phase(pid,seeds,delta(pid)));r['config']=c
        r['rating_status']=RATINGS[c['arm']]['status']
        r['sampling']=dict(carriage_window_m=1.0,carriage_limits_m=[-2.12,2.12],joint_initial_central_fraction=.5,robot_geometry_revision='v5',parking_revision='v6_low_gravity_400_candidates')
        # Numerical success with non-continuous public values remains a diagnostic.
        r['binding_rated_admission']=False # Continuous output torque is not verified by the public tables.
        r['conditional_rated_reference_admission']=r['verdict']=='FEASIBLE' and c['arm'] in ('xArm7','xArm6')
        ck.json_write(p,r)
        print(cid,pid,r['feasible_seeds'],r['blocker_counts'],f"{time.monotonic()-began:.1f}s",flush=True)
def bounded(spec):
    cid,seeds,phases,stage=spec
    out=RESULT/stage/cid;out.mkdir(parents=True,exist_ok=True); log=out/('chunk_'+'_'.join(phases)+'.log')
    cmd=[sys.executable,'-B','-u',str(HERE/'run.py'),'--worker',cid,'--seeds',str(seeds),'--phases',*phases,'--stage',stage]
    began=time.monotonic();peak=0.
    with log.open('w',encoding='utf-8') as f:
        p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT)
        try:
            while p.poll() is None:
                peak=max(peak,ck.tree_peak_memory(p.pid))
                if time.monotonic()-began>1140:raise TimeoutError('1140 s chunk bound')
                if peak>1900:raise MemoryError('1900 MiB worker bound')
                time.sleep(1)
            if p.returncode:raise RuntimeError(log.read_text()[-2500:])
        finally:
            if p.poll() is None:ck.kill_tree(p)
    rec=dict(id=cid,seeds=seeds,phases=phases,elapsed_s=time.monotonic()-began,peak_MiB=peak,exit_code=p.returncode,timeout_s=1140)
    ck.json_write(log.with_suffix('.resource.json'),rec);print(json.dumps(rec),flush=True)
def batch(ids,seeds,phases,stage):
    if len(ids)>2:raise ValueError('At most two worker processes per foreground chunk')
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        fs=[ex.submit(bounded,(i,seeds,phases,stage)) for i in ids]
        for f in concurrent.futures.as_completed(fs):f.result()
def grid_chunk(index,seeds):
    entries=[]
    # Fractional factorial numerical coarse sweep: every arm, height, orientation,
    # stand-off and count is represented. All 750 combinations get static screening.
    stands={'horizontal':.05,'down30':.15,'down60':.25,'vertical':.15,'inverted':.25}
    for e in json.loads((RESULT/'configs.json').read_text()):
        c=e['config']
        if not e['static_hits'] and c['standoff']==stands[c['orientation']]:entries.append(e['id'])
    # Two workers each do at most 15 design entries; each chunk remains bounded.
    groups={f'group{i}':entries[i*15:(i+1)*15] for i in range(math.ceil(len(entries)/15))}
    ck.json_write(RESULT/'groups.json',groups)
    names=[f'group{index*2+j}' for j in range(2) if f'group{index*2+j}' in groups]
    batch(names,seeds,list(ck.PHASES),'coarse')
def aggregate():
    rows=[]
    for e in json.loads((RESULT/'configs.json').read_text()):
        c=e['config']; row=dict(id=e['id'],**c,static_viable=not e['static_hits'],static_hits=json.dumps(e['static_hits']))
        row.update(phases_passed=None,rated_phases_passed=None,conditional_rated_reference_phases=None,ik_phases=None,collision_free_phases=None,seeds=0,stage='static',best_worst_ratio=None)
        for stage in ('coarse','refine','final'):
            ps=list((RESULT/stage/e['id']).glob('P*.json'))
            if not ps:continue
            rs=[json.loads(p.read_text()) for p in ps]
            row.update(stage=stage,phases_tested=len(rs),seeds=min(r['seeds'] for r in rs),phases_passed=sum(r['verdict']=='FEASIBLE' for r in rs),
              rated_phases_passed=0,conditional_rated_reference_phases=sum(r['verdict']=='FEASIBLE' and c['arm'] in ('xArm7','xArm6') for r in rs),ik_phases=sum(r['ik_seeds']>0 for r in rs),collision_free_phases=sum(r['collision_free_seeds']>0 for r in rs),
              best_worst_ratio=max((r['best_nominal']['torque']['ratio'] for r in rs if r['verdict']=='FEASIBLE' and r['best_nominal']),default=None))
        row['phases_tested']=row.get('phases_tested',0);row['rating_status']=RATINGS[c['arm']]['status']
        row['nominal_payload_eligible']=c['arm'] not in ('xArm7','FR3')
        row['cost_basis']='relative installed complexity only; no supplier quote'
        rows.append(row)
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with (RESULT/'sweep.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fields);w.writeheader();w.writerows(rows)
    measured=[r for r in rows if r['stage']!='static'];measured.sort(key=lambda r:(-r['phases_passed'],r['best_worst_ratio'] or 99,r['count']))
    print(json.dumps(measured[:20],indent=2))
    ck.json_write(RESULT/'ranking.json',{'basis':'Observed admissions, admitted torque margin, then arm count; mixed seed stages are explicitly recorded, and payload/rating eligibility is separate. No absolute price estimate.', 'rows':measured})
    return rows
if __name__=='__main__':
    import sys
    p=argparse.ArgumentParser();p.add_argument('--setup',action='store_true');p.add_argument('--worker');p.add_argument('--batch',nargs='+');p.add_argument('--seeds',type=int,default=96);p.add_argument('--phases',nargs='+',default=list(ck.PHASES));p.add_argument('--stage',default='final');p.add_argument('--aggregate',action='store_true');p.add_argument('--grid-chunk',type=int);a=p.parse_args()
    if a.setup:setup()
    elif a.worker:worker(a.worker,a.seeds,a.phases,a.stage)
    elif a.batch:batch(a.batch,a.seeds,a.phases,a.stage)
    elif a.aggregate:aggregate()
    elif a.grid_chunk is not None:grid_chunk(a.grid_chunk,a.seeds)
