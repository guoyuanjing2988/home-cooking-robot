"""R19 #42: payload and CoG offset of the mount options (new file; reads only). The method of r19fr5_payload.py (R19_FR5.md
4.2), whose held-load models are used unchanged (copied here because that script computes at import):
 - wok with the heaviest dish: r17chain.py MASS['wok'] (wok 1.5 kg, CoG 45 mm above its origin; handle + grip block 0.3 kg
   at the handle middle) + food 1.15 kg at 20 mm, grasp of the stored FR5 wok chain (GTILT, sign);
 - full soak tub: r19prep3_actions.py tub 0.50 kg + 2.28 kg water, CoG COM_T in the tub frame, grasp of the stored
   UR5e tub-fill chain.
The held load is rigid in the TCP frame (same grasp on every mount), so its CoG relative to the TCP is the same for every
option; it is composed with each option's flange -> TCP transform (built model). The EOAT is R_tool + both jaws of the
built model: for the mount options R_tool's inertial already holds the bracket and DH's standard flange (r19mount.py);
for fr5_j6_pgc_sp20 the 0.25 kg sp20 plate at 10 mm (R19_FR5.md 4.1, not in its model) is added as r19fr5_payload.py did;
the current UR5e pose has no adapter at all (it cannot be built).
Reported per load and option: payload, combined CoG offset from the flange centre (axial / radial), the static moment at
the flange (worst orientation, g M |CoG|), the rated-payload margin, the full-performance check, and the PGC jaw moment
(gravity moment of the held load about the TCP: level carry as at the grasp keyframe, and worst orientation). The jaw
moment does not depend on the mount (same grasp).
Limits: FR5 5 kg at <= 300 mm CoG offset [S: Fairino Cobots manual 3.4.5.2.5, Fig. 3.4-19]; UR5e 5 kg [S: UR5e datasheet]
with the 0.35 m CoG radius the repo's UR5e envelope uses (arms.py com_radius_m, R19_ARM_SWAP.md 5; the UR5e payload
diagram was not re-read here); PGC 7 N.m static Mx/My/Mz [S: DH PGC-140 manual Table 1.2].
python r19mount_payload.py [ARMS=..] -> results/r19/mount/payload.json"""
import sys,os,json
sys.path.insert(0,'.')
import numpy as np,mujoco
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
import chain,arms,kitchen15 as K15,kitchen16 as K,kitchen17 as K17
from scene import build
from checker import Checker
SP20=dict(kg=.25,z=.010,src='E: R19_FR5.md 4.1, 6061 disc Ø75 x 20 mm, CoG on the flange axis 10 mm out; not in the fr5_j6_pgc_sp20 model')
def arm_frames(arm):
 cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,r16=True,r17=True,arm=arm);tree,meta=build(cfg,None);ch=Checker(tree,meta);m,d=ch.m,ch.d
 mujoco.mj_kinematics(m,d);mujoco.mj_comPos(m,d);fl=m.site('R_attachment_site').id;sid=m.site('R_prep').id
 Rf=d.site_xmat[fl].reshape(3,3);pf=d.site_xpos[fl];Rt=d.site_xmat[sid].reshape(3,3);pt=d.site_xpos[sid]
 ids=[m.body(n).id for n in ['R_tool','R_jaw_minus','R_jaw_plus']];me=float(sum(m.body_mass[b] for b in ids))
 ce=Rf.T@(sum(m.body_mass[b]*d.xipos[b] for b in ids)/me-pf)
 return dict(R_ft=Rf.T@Rt,t_ft=Rf.T@(pt-pf),eoat_kg=me,eoat_com_f=ce,com_radius_limit_m=arms.ARMS[arm]['com_radius_m'],payload_limit_kg=arms.ARMS[arm]['payload_kg'])
def held(kind):
 """(mass kg, CoG in the TCP frame m, world z in the TCP frame at the grasp) of the held load (r19fr5_payload.held, unchanged)"""
 if kind=='wok':
  r=json.load(open('results/r17/chain_wok_s-1_final_py.17_fr5_j6_pgc_sp20.json'));K17.set_wok_tilt(float(r.get('wok_tilt') or 0.))
  W0=K15.WOK0;R=np.eye(3);p=W0.copy();parts=[(1.5,np.array([0,0,.045])),(.3,(K15.HANDLE['root']+K15.HANDLE['end'])/2-W0),(1.15,np.array([0,0,.02]))]
  pt,Rt=K.tcp_pose('wok',R,p,r['grasp_sense'])
 else:
  import kitchen19p3 as P3,r19prep3_actions as A3
  r=json.load(open('results/r19/prep/chain_tubfill_full_ur5e_enc2_pgc.json'));P3.pitched(r['obj']);kf=r['keyframes'][1]
  R=np.array(kf['R']);p=np.array(kf['p']);w=A3.tub_water_kg();parts=[(P3.MASS_EST['tub']+w,np.asarray(A3.COM_T,float))]
  pt,Rt=K.tcp_pose(r['obj'],R,p,r['grasp_sense'])
 M=sum(m_ for m_,_ in parts);com=p+R@(sum(m_*c for m_,c in parts)/M)
 return M,Rt.T@(com-pt),Rt.T@np.array([0,0,1.])
A=KV.get('ARMS','ur5e_enc2_pgc,ur5e_enc2_pgc_m1,ur5e_enc2_pgc_m2,ur5e_enc2_pgc_m3,fr5_j6_pgc_sp20,fr5_j6_pgc_m1,fr5_j6_pgc_m2,fr5_j6_pgc_m3').split(',')
F={a:arm_frames(a) for a in A}
out=dict(method=__doc__,sp20_plate=SP20,arms={a:dict(tcp_in_flange_mm=np.round(f['t_ft']*1e3,1).tolist(),eoat_kg=round(f['eoat_kg'],3),eoat_com_flange_mm=np.round(f['eoat_com_f']*1e3,1).tolist()) for a,f in F.items()},loads={})
for kind in ('wok','tub'):
 M,c_t,z_t=held(kind);row=dict(held_kg=round(M,3),held_com_tcp_mm=np.round(c_t*1000,1).tolist(),
  pgc_jaw_moment_level_Nm=round(M*9.81*float(np.linalg.norm(np.cross(c_t,z_t))),2),pgc_jaw_moment_worst_Nm=round(M*9.81*float(np.linalg.norm(c_t)),2),per_arm={})
 for a,fr in F.items():
  held_f=fr['t_ft']+fr['R_ft']@c_t;masses=[(M,held_f),(fr['eoat_kg'],fr['eoat_com_f'])]+([(SP20['kg'],np.array([0,0,SP20['z']]))] if a.endswith('sp20') else [])
  tot=sum(m_ for m_,_ in masses);cog=sum(m_*c for m_,c in masses)/tot;off=float(np.linalg.norm(cog))
  row['per_arm'][a]=dict(payload_kg=round(tot,3),cog_offset_from_flange_mm=round(off*1e3,1),cog_axial_mm=round(float(cog[2])*1e3,1),cog_radial_mm=round(float(np.hypot(cog[0],cog[1]))*1e3,1),
   held_cog_offset_mm=round(float(np.linalg.norm(held_f))*1e3,1),flange_static_moment_max_Nm=round(9.81*tot*off,2),
   rated_margin_kg=round(fr['payload_limit_kg']-tot,3),cog_limit_mm=fr['com_radius_limit_m']*1e3,within_rated=bool(tot<=fr['payload_limit_kg'] and off<=fr['com_radius_limit_m']))
 out['loads'][kind]=row
os.makedirs('results/r19/mount',exist_ok=True);fn='results/r19/mount/payload.json';json.dump(out,open(fn,'w'),indent=1,default=float);print(fn)
print(json.dumps(out['arms']))
for kind,row in out['loads'].items():
 print(kind,{k:v for k,v in row.items() if k!='per_arm'})
 for a,v in row['per_arm'].items():print('  ',a,v)
