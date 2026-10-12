"""Select a park encoder branch once, before downstream fold/unfold paths."""
import os,sys,json,hashlib,shutil
os.environ['R07_LAYOUT']=sys.argv[1]
import numpy as np,mujoco
import runtime_v7_r07 as v
from motion_v7_r07 import mo
O=v.O;H=v.H;ID=v.ID;out=O/f'normalized_park_v7_{ID}.json'
if out.exists():print('PARK_BRANCH_ALREADY_RECORDED',ID);raise SystemExit(0)
idlefile=O/'layouts'/f'{ID}_idle.json';parkfile=O/'layouts'/f'{ID}_park_full.json'
idle=json.loads(idlefile.read_text());park=json.loads(parkfile.read_text());source=O/'static_v7'/ID/'0.json';working=np.array(json.loads(source.read_text())['witness']['poses'][0]['q']);old=np.array(idle['q']);assert np.max(abs(old-np.array(park['q'])))<1e-8
ch=v.scene(58);ch.xml=(H/idle['model_xml']).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));new=mo.shortq(ch,working.copy(),old.copy())
frames=[]
for q in (old,new):
 ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d);frames.append((ch.d.geom_xpos.copy(),ch.d.geom_xmat.copy()))
error=max(float(np.max(abs(a-b))) for a,b in zip(*frames));within=all(not ch.m.jnt_limited[ch.jid[n]] or ch.m.jnt_range[ch.jid[n],0]-1e-9<=new[ix]<=ch.m.jnt_range[ch.jid[n],1]+1e-9 for n,ix in ch.qa.items());assert error<1e-9 and within
archive=H/'history/v7_park_branch';archive.mkdir(exist_ok=True)
for f in (idlefile,parkfile,H/idle['model_xml']):
 target=archive/f.name
 if not target.exists():shutil.copy2(f,target)
record=dict(layout=ID,old_q=old.tolist(),new_q=new.tolist(),same_full_geometry=True,maximum_geometry_frame_difference=error,within_joint_limits=within,source_static_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),model_sha256=hashlib.sha256(ch.xml.encode()).hexdigest(),scope='Choose the equivalent allowed hinge branch nearest the working state before any qualified deployment. No physical joint-state teleport is credited. The full idle check is rerun, and all downstream endpoints must match the chosen exact joint state.')
park['q']=new.tolist();park['joint_branch_selection']=record;parkfile.write_text(json.dumps(park,indent=None));out.write_text(json.dumps(record,indent=2));print('PARK_BRANCH',ID,error,new.tolist())
