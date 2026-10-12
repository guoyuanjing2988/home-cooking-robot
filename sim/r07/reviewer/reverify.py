from common import *
started=time.monotonic();rows=[]
lo=int(sys.argv[1]) if len(sys.argv)>1 else 0;hi=int(sys.argv[2]) if len(sys.argv)>2 else 105
for i in range(lo,min(hi,len(mo.items))):
    ph,sg,key=mo.items[i];saved=read('final_static/'+str(i)+'.json');ch=mo.scene(ph,sg,i);k=seed(i)
    checks=[independent_pose(ch,np.array(p['q']),hs,k) for p,hs in zip(saved['poses'],sg['poses'])]
    delta=[]
    for a,b in zip(checks,saved['poses']):
        delta.extend(abs(x['position_mm']-y['position_mm']) for x,y in zip(a['errors'],b['errors']))
    row=dict(index=i,stroke=key,submitted_ok=saved['ok'],ok=len(checks)==len(sg['poses']) and all(c['ok'] for c in checks),seed=k,checks=checks,max_position_error_delta_mm=max(delta),max_torque_ratio_delta=abs(max(c['torque']['check'] for c in checks)-saved['max_envelope_ratios']['check']),min_grip_delta=abs(min(c['grip']['check'] for c in checks)-saved['min_grip_margin']))
    rows.append(row);print(i,key,row['ok'],flush=True)
    dump(f'reverify_{lo}_{hi}.json',dict(elapsed_s=time.monotonic()-started,strokes_passed=sum(r['ok'] for r in rows),strokes_total=len(rows),poses_total=sum(len(r['checks']) for r in rows),rows=rows,method='Fresh compiled-scene pose, Jacobian/wrench/grip and flange mass/CoM arithmetic. R05 unchanged reference and conservative pair-distance code retained. All failed endpoints are diagnostic only; no fresh IK search or accepted working path inferred.'))
