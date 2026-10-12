import os,sys
os.environ['R07_LAYOUT']=sys.argv[1]
from v4_common import *
from planner_r05 import Planner
import xml.etree.ElementTree as E
data=read(f'layouts/{v.ID}_idle.json');ch=v.scene(len(v.items)-1);ch.xml=(I/data['model_xml']).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False;q=np.array(data['q'])
original_required=f.required;submitted_door_gates=[]
for a,n in enumerate(ch.gnames):
    if not n.startswith('idle_full_sweep_cover_'):continue
    for b,nn in enumerate(ch.gnames):
        if ch.robot[b] and ch.gripper(b):submitted_door_gates.append(dict(pair=[n,nn],required_mm=original_required(ch,a,b)[0]*1000,binding_required_mm=10))
def corrected_required(cc,a,b):
    if (cc.gnames[a].startswith('idle_full_sweep_cover_') and cc.robot[b]) or (cc.gnames[b].startswith('idle_full_sweep_cover_') and cc.robot[a]):return (.01,'robot_door_sweep')
    return original_required(cc,a,b)
f.required=corrected_required
hits,mins,_=f.contacts(ch,q);parts=[]
strip=(np.array([-1.8,0,.85]),np.array([1.8,.23,1.35]));corridor=(np.array([-1.6,-.75,.85]),np.array([.6,-.05,1.85]))
def overlaps(lo,hi,box):return bool(np.all(hi>box[0]) and np.all(lo<box[1]))
for g,n in enumerate(ch.gnames):
    if not ch.robot[g]:continue
    lo=np.array([ch.bounds.support(g,-u)[k] for k,u in enumerate(np.eye(3))]);hi=np.array([ch.bounds.support(g,u)[k] for k,u in enumerate(np.eye(3))]);parts.append(dict(name=n,lo_m=lo.tolist(),hi_m=hi.tolist(),door_sweep_gap_mm=float((1.35-hi[2])*1000),front_strip_intersection=overlaps(lo,hi,strip),corridor_intersection=overlaps(lo,hi,corridor)))
folded=[]
for side in ('R',):
    pp=[p for p in parts if p['name'].startswith(side+'_')];lo=np.min([p['lo_m'] for p in pp],axis=0);hi=np.max([p['hi_m'] for p in pp],axis=0);folded.append(dict(side=side,lo_m=lo.tolist(),hi_m=hi.tolist(),dimensions_m=(hi-lo).tolist()))
hold=ch.torque_multi(q,{},{});ranges=all(ch.m.jnt_range[ch.jid[n],0]-1e-8<=q[ch.qa[n]]<=ch.m.jnt_range[ch.jid[n],1]+1e-8 for n in ch.qa)
doors=[]
for body in E.parse(I/data['doors_model_xml']).findall('.//body'):
    if not body.get('name','').startswith('r07_open_door'):continue
    p=np.fromstring(body.get('pos'),sep=' ');g=body.find('geom');gp=np.fromstring(g.get('pos'),sep=' ');sz=np.fromstring(g.get('size'),sep=' ');j=body.find('joint');doors.append(dict(name=body.get('name'),dimensions_m=(2*sz).tolist(),axis=j.get('axis'),range_rad=j.get('range'),z_bottom_m=float(p[2]+gp[2]-sz[2])))
routes=[];ib=IndependentBound(ch)
for ri,r in enumerate(data['fold_paths']):
    goal=np.array(r['endpoint_reference']['poses'][0]['q']);hands=v.items[next(i for i,x in enumerate(v.items) if x[2]==r['canonical_stroke'])][1]['poses'][r['canonical_pose']] if 'canonical_stroke' in r else {'R':s.ck.hand(r['working_tcp_m'],held='empty',approach=[0,1,0],jaw_axis=[1,0,0])}
    for h in hands.values():
        for level in ('nominal','check'):h[level+'_forces_N']=[[0,0,0]];h[level+'_moments_Nm']=[[0,0,0]]
    park=np.array(r.get('park_q_equivalent_public_range',q));saved_path=r['planner'].get('path',[])
    for direction,path in [('fold',saved_path or [goal.tolist(),park.tolist()]),('unfold',list(reversed(saved_path or [goal.tolist(),park.tolist()])) )]:
        pl=Planner(ch,hands,seconds=65);ch.contact_windows=[];ch.working_stroke=False;states=0;bad=None;step=0.;mt=0.
        for si,(a,b) in enumerate(zip(np.array(path),np.array(path)[1:])):
            D=ib.segment(a,b);N=max(1,math.ceil(D/.004));step=max(step,D/N*1000)
            for k in range(N+1):
                state=a+(b-a)*k/N;states+=1
                if not pl.state(state):bad=dict(segment=si,grid=k,rejection=pl.last);break
                tq=ch.torque_multi(state,hands,{s:[0,0,0] for s in hands},{s:[0,0,0] for s in hands});mt=max(mt,tq['ratio'])
                if tq['ratio']>1:bad=dict(kind='load',torque=tq);break
            if bad:break
        routes.append(dict(index=ri,direction=direction,saved_path_available=bool(saved_path),diagnostic_pass=bad is None,states_checked=states,max_point_step_mm=step,max_torque_ratio=mt,first_rejection=bad,scope='Full saved path if present; otherwise straight rejection diagnostic only, retaining all five door-sweep supersets.'))
        print('IDLE',v.ID,ri,direction,bad is None,states,flush=True)
dump(f'idle_{v.ID}.json',dict(layout=v.ID,populated_geometry_pass=not hits,snapshot_hits=hits,min_clearance=mins,parts=parts,folded_envelopes=folded,doors=doors,door_sweep_pass=min(p['door_sweep_gap_mm'] for p in parts)>=10-1e-3,door_sweep_min_gap_mm=min(p['door_sweep_gap_mm'] for p in parts),front_strip_pass=not any(p['front_strip_intersection'] for p in parts),corridor_pass=not any(p['corridor_intersection'] for p in parts),doors_checked_against_corridor=False,holding_torque=hold,public_ranges_ok=bool(ranges),fold_replays=routes,saved_fold_paths=sum(bool(r['planner'].get('path')) for r in data['fold_paths']),submitted_gripper_door_gates=submitted_door_gates,reviewer_all_robot_door_gate_mm=10,full_idle_pass=False,method='Exact original-shape support AABBs for all robot parts; vertical separating plane proves clearance to every 0..90 degree door angle. Strip/corridor concern robot parts only. Both fold directions independently sampled with corrected10mm door-sweep gate for grippers too; no path invented as acceptance evidence.'))
