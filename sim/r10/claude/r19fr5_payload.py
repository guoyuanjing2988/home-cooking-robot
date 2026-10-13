"""R19 #2 (FR5): payload and CoG-offset check of the 20 mm flange adapter (fr5_j6_pgc_sp20). New file; reads only.

Held loads (the same mass models the chains use):
 - wok with the heaviest dish: r17chain.py MASS['wok'] (wok 1.5 kg, CoG 45 mm above its origin; handle + grip block
   0.3 kg at the handle middle) + food 1.15 kg at 20 mm, grasp of the stored FR5 wok chain (GTILT, sign);
 - full soak tub: r19prep3_actions.py tub 0.50 kg + 2.28 kg water = 2.78 kg, CoG COM_T (0, 0, 30 mm) in the tub frame,
   grasp of the stored tub-fill chain (tub_p15, sign +1).
Arm side: the flange (R_attachment_site) -> TCP (R_prep) transform and the modelled EOAT (R_tool + jaws, 1.2 kg) of the
built arm model; the adapter as a point mass ADAPTER_KG at ADAPTER_Z (its centre) on the flange axis (not in the model).
Because the held object is rigid in the TCP frame, its CoG offset from the flange centre is a constant of the grasp
(independent of the arm posture). Reported per load: total payload, combined CoG offset from the flange centre (the
quantity of the Fairino FR5 load curve), and the moment about the TCP (the PGC jaw moment; the adapter is above the
gripper, so it cannot change it). Also the same numbers without the adapter (fr5_j6_pgc).
python r19fr5_payload.py [ADAPTER_KG=0.25] [ADAPTER_Z=0.010] [FLANGE_KG=0]  -> results/r19/fr5/payload_fr5_j6_pgc_sp20.json"""
import sys,os,json
sys.path.insert(0,'.')
import numpy as np,mujoco
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
import chain,kitchen15 as K15,kitchen16 as K,kitchen17 as K17
from scene import build
from checker import Checker
AD_KG=float(KV.get('ADAPTER_KG',.25));AD_Z=float(KV.get('ADAPTER_Z',.010));FL_KG=float(KV.get('FLANGE_KG',0.))
def arm_frames(arm):
 cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,r16=True,r17=True,arm=arm);tree,meta=build(cfg,None);ch=Checker(tree,meta);m,d=ch.m,ch.d
 mujoco.mj_kinematics(m,d);mujoco.mj_comPos(m,d);fl=m.site('R_attachment_site').id;sid=m.site('R_prep').id
 Rf=d.site_xmat[fl].reshape(3,3);pf=d.site_xpos[fl];Rt=d.site_xmat[sid].reshape(3,3);pt=d.site_xpos[sid]
 ids=[m.body(n).id for n in ['R_tool','R_jaw_minus','R_jaw_plus']];me=float(sum(m.body_mass[b] for b in ids))
 ce=Rf.T@(sum(m.body_mass[b]*d.xipos[b] for b in ids)/me-pf)
 return dict(R_ft=Rf.T@Rt,t_ft=Rf.T@(pt-pf),eoat_kg=me,eoat_com_f=ce)
def held(kind):
 """(mass kg, CoG in the TCP frame m) of the held load, from the stored chain's grasp."""
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
 return M,Rt.T@(com-pt),Rt.T@np.array([0,0,1.]),dict(chain=r.get('arm'),obj=r['obj'],sign=r['grasp_sense'],parts_kg=[m_ for m_,_ in parts])
out=dict(method=__doc__,adapter_kg_E=AD_KG,adapter_com_z_m=AD_Z,extra_flange_kg=FL_KG,loads={})
F={a:arm_frames(a) for a in ('fr5_j6_pgc','fr5_j6_pgc_sp20')}
for kind in ('wok','tub'):
 M,c_t,z_t,info=held(kind);row=dict(held_kg=round(M,3),held_com_tcp_mm=np.round(c_t*1000,1).tolist(),**info)
 row['pgc_jaw_moment_at_grasp_Nm']=round(M*9.81*float(np.linalg.norm(np.cross(c_t,z_t))),2)   # gravity moment about the TCP with the object level, as at the grasp keyframe
 for a,fr in F.items():
  sp=a.endswith('sp20');held_f=fr['t_ft']+fr['R_ft']@c_t
  masses=[(M,held_f),(fr['eoat_kg'],fr['eoat_com_f'])]+([(AD_KG,np.array([0,0,AD_Z]))] if sp else [])+([(FL_KG,np.array([0,0,AD_Z]))] if FL_KG else [])
  tot=sum(m_ for m_,_ in masses);cog=sum(m_*c for m_,c in masses)/tot
  row[a]=dict(payload_kg=round(tot,3),cog_offset_from_flange_mm=round(float(np.linalg.norm(cog))*1000,1),cog_axial_mm=round(float(cog[2])*1000,1),cog_radial_mm=round(float(np.hypot(cog[0],cog[1]))*1000,1),
   held_cog_offset_mm=round(float(np.linalg.norm(held_f))*1000,1),tcp_in_flange_mm=np.round(fr['t_ft']*1000,1).tolist(),
   flange_static_moment_max_Nm=round(9.81*tot*float(np.linalg.norm(cog)),2),
   rated_5kg_margin_kg=round(5-tot,3),within_full_performance=bool(tot<=5 and np.linalg.norm(cog)<=.300))
 # PGC jaw moment: gravity moment about the TCP of the held load, worst orientation = M g |c_t| (any tool orientation);
 # level carry (tool frame as at the stored grasp keyframe): M g * horizontal distance; the adapter changes neither
 row['pgc_jaw_moment_worst_Nm']=round(M*9.81*float(np.linalg.norm(c_t)),2)
 out['loads'][kind]=row
os.makedirs('results/r19/fr5',exist_ok=True);fn='results/r19/fr5/payload_fr5_j6_pgc_sp20'+(f"_ad{AD_KG:g}" if 'ADAPTER_KG' in KV else '')+(f"_fl{FL_KG:g}" if FL_KG else '')+'.json'
json.dump(out,open(fn,'w'),indent=1,default=float);print(fn)
for kind,row in out['loads'].items():print(kind,json.dumps({k:v for k,v in row.items()},default=float))
