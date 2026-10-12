from pathlib import Path
H=Path(__file__).resolve().parent
(H/'audit_v3').mkdir(exist_ok=True)
(H/'results_v3').mkdir(exist_ok=True)
for name in ('common','reverify','rules','envelopes','connections','idle','internal'):
    t=(H/f'v2_{name}.py').read_text()
    t=t.replace('v2_common','v3_common').replace("H/'results_v2'","H/'results_v3'").replace("H/'audit_v2'","H/'audit_v3'").replace("'R07_LAYOUT','L13'","'R07_LAYOUT','L34'").replace('actual L13 mount','actual L34 mount')
    if name=='internal':
        t=t.replace("if ch.working_stroke:raise RuntimeError('Working path requires explicit Cartesian interpolation audit')", """if ch.working_stroke:
                from scipy.spatial.transform import Slerp
                alpha=(si+k/N)/(len(path)-1)
                for side in ha:
                    target=(1-alpha)*np.array(ha[side]['pos'])+alpha*np.array(hb[side]['pos'])
                    rot=Slerp([0,1],Rotation.from_matrix([ch.target_rotation(ha[side],w['k']),ch.target_rotation(hb[side],w['k'])]))(alpha).as_matrix()
                    sid=ch.m.site(side+'_prep').id
                    pe=np.linalg.norm(ch.d.site_xpos[sid]-target)*1000
                    oe=np.degrees(np.linalg.norm(Rotation.from_matrix(rot.T@ch.d.site_xmat[sid].reshape(3,3)).as_rotvec()))
                    if pe>5 or oe>3:bad=dict(kind='working line',side=side,position_mm=float(pe),orientation_deg=float(oe));break
                if bad:break""")
    (H/f'v3_{name}.py').write_text(t,encoding='utf-8')
print('v3 adapters ready')
