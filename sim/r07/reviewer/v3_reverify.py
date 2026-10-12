from v3_common import *
import hashlib
started=time.monotonic();rows=[]
for i,(ph,sg,key) in enumerate(mo.items):
    w=candidate(i);ch=v.scene(i)
    checks=[] if not w else [independent_pose(ch,np.array(p['q']),hs,w['k']) for p,hs in zip(w['poses'],sg['poses'])]
    saved=read(f'final_static_v2/{v.ID}/{i}.json')
    ref=None if not w else f.replay(ch,w)
    delta=[]
    if ref:
        for a,b in zip(checks,ref['poses']):
            delta.extend(abs(x['position_mm']-y['position_mm']) for x,y in zip(a['errors'],b['errors']))
    row=dict(index=i,stroke=key,submitted_ok=saved['ok'],ok=bool(len(checks)==len(sg['poses']) and all(c['ok'] for c in checks)),seed=None if not w else w['k'],required_poses=len(sg['poses']),checks=checks,reference_ok=None if not ref else ref['ok'],model_sha256=hashlib.sha256(ch.xml.encode()).hexdigest(),model_matches_submission=hashlib.sha256(ch.xml.encode()).hexdigest()==saved['model_sha256'],max_position_error_delta_mm=max(delta,default=0),max_torque_ratio_delta=abs(max(c['torque']['check'] for c in checks)-ref['max_envelope_ratios']['check']) if checks else None)
    rows.append(row)
    print(i,key,row['ok'],len(checks),'/',len(sg['poses']),flush=True)
    dump('reverify.json',dict(layout=v.ID,strokes_passed=sum(r['ok'] for r in rows),strokes_total=len(rows),poses_total=sum(len(r['checks']) for r in rows),rows=rows,elapsed_s=time.monotonic()-started,method='Independent SE3 pose, range, Jacobian load, flange CoM, grip and reconstructed full-scene checks. Partial failed witnesses remain partial; no substituted v1 poses.'))
