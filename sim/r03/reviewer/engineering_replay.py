"""Independent rated-load, connected-path and idle-access replay."""
from reverify import *
import xml.etree.ElementTree as E
def envelope():
 tree,meta=s.model.build(dict(s.model.CONFIG,transport_only=True))
 m=mujoco.MjModel.from_xml_string(E.tostring(tree.getroot(),encoding='unicode'));d=mujoco.MjData(m)
 for side in s.model.SIDES:
  for n in (side+'_tool',side+'_jaw_minus',side+'_jaw_plus'):
   b=m.body(n).id;m.body_mass[b]=1e-9;m.body_inertia[b]=1e-12
 mujoco.mj_setConst(m,d)
 # Use literal reference for the arm's OEM self-collision, never installed
 # kitchen collisions to narrow the manufacturer's capability workspace.
 ch=object.__new__(s.ck.Checker);ch.desc=s.ck.hand([0,0,1],jaw_axis=[0,1,0]);ch.bind_model(m)
 env=json.loads((I/'results/torque_envelope.json').read_text());rows=[];jp=np.zeros((3,m.nv));jr=np.zeros_like(jp)
 for n,w in env['witnesses'].items():
  side=n[0];q=m.qpos0.copy()
  for joint,x in zip(meta['arms'][side],w['joints_rad']):q[ch.qa[joint]]=x
  d.qpos[:]=q;d.qvel[:]=0;mujoco.mj_forward(m,d)
  sid=m.site(side+'_attachment_site').id;point=d.site_xpos[sid]+d.site_xmat[sid].reshape(3,3)@np.array(w['CoM_flange_m'])
  mujoco.mj_jac(m,d,jp,jr,point,int(m.site_bodyid[sid]))
  tau=d.qfrc_bias+49.05*jp[2]
  demand=float(abs(tau[ch.da[n]]));off=np.array(w['CoM_flange_m'])
  com_ok=np.linalg.norm(off)<=.350+1e-9 if side=='R' else np.linalg.norm(off[:2])<=.030+1e-9 and -.000000001<=off[2]<=.015000001
  blockers=[h for h in s.ck.Checker.forbidden(ch,q) if all(a.startswith(('R_geom_',) if side=='R' else ('L_link',)) for a in h['pair'])]
  ranges=all(m.jnt_range[ch.jid[a],0]-1e-8<=q[ch.qa[a]]<=m.jnt_range[ch.jid[a],1]+1e-8 for a in meta['arms'][side])
  rows.append(dict(joint=n,rated_total_flange_kg=w['rated_payload_total_kg'],CoM_flange_m=w['CoM_flange_m'],CoM_chart_ok=bool(com_ok),point_Jacobian_static_Nm=demand,submitted_Nm=env['envelope_Nm'][n],delta_Nm=demand-env['envelope_Nm'][n],OEM_self_blockers=blockers,public_ranges_ok=bool(ranges)))
 rng=np.random.default_rng(93008);scan=[]
 for side in s.model.SIDES:
  names=meta['arms'][side];dofs=[ch.da[n] for n in names];bounds=np.array([m.jnt_range[ch.jid[n]] for n in names]);maximum=np.zeros(6)
  for k in range(8000):
   q=m.qpos0.copy();x=rng.uniform(bounds[:,0],bounds[:,1])
   for n,a in zip(names,x):q[ch.qa[n]]=a
   d.qpos[:]=q;mujoco.mj_forward(m,d);sid=m.site(side+'_attachment_site').id
   mujoco.mj_jacSite(m,d,jp,jr,sid);rt=d.site_xmat[sid].reshape(3,3)
   baseline=d.qfrc_bias[dofs]+49.05*jp[2,dofs]
   c=np.array([49.05*np.cross(jr[:,dofs].T,rt[:,i])[:,2] for i in range(3)]).T
   caps=abs(baseline)+.35*np.linalg.norm(c,axis=1) if side=='R' else np.maximum(abs(baseline),abs(baseline+.015*c[:,2]))+.03*np.linalg.norm(c[:,:2],axis=1)
   maximum=np.maximum(maximum,caps)
  scan.append(dict(side=side,seed=93008,samples=8000,unfiltered_sample_max_Nm=maximum.tolist(),submitted_envelope_Nm=[env['envelope_Nm'][n] for n in names],sample_to_submitted_ratios=[float(v/env['envelope_Nm'][n]) for n,v in zip(names,maximum)],note='Coverage sensitivity only; random configurations not collision-filtered and not substituted into capability denominators.'))
 out=dict(rows=rows,all_witnesses_valid=all(r['CoM_chart_ok'] and r['public_ranges_ok'] and not r['OEM_self_blockers'] and abs(r['delta_Nm'])<1e-6 and r['rated_total_flange_kg']==5 for r in rows),mount_angles_deg=dict(R=s.model.CONFIG['mount_deg'],L=s.model.CONFIG['helper_mount_deg']),gravity_world_m_s2=m.opt.gravity.tolist(),EOAT_replaced_by_total_rated_payload=True,workspace_sensitivity=scan,limitation='Submitted DE values are feasible conservative numerical maxima estimates. No numerical search certifies the global workspace maximum. Both arms use their actual mounting orientation; translation does not alter angular static gravity demands.')
 dump('envelope_independent.json',out);print('envelope',out['all_witnesses_valid'],flush=True)
def required(ch,a,b):
 ra,rb=ch.robot[a],ch.robot[b];m=ch.m;ns=(ch.gnames[a],ch.gnames[b])
 if not ra and not rb:return None
 if 'north_wall' in ns and any(n.startswith('wall_mount_') for n in ns):return None
 if ch.weld[a]==ch.weld[b] or tuple(sorted((a,b))) in ch.acm:return None
 wa,wb=ch.weld[a],ch.weld[b]
 if m.body_weldid[m.body_parentid[wa]]==wb or m.body_weldid[m.body_parentid[wb]]==wa:return None
 if 'floor' in ns and not(ch.held[a] or ch.held[b]):
  other=b if ns[0]=='floor' else a
  if not any(k in ch.bnames[other] for k in ('arm','tool','gripper','finger')):return None
 if ra and rb:
  if ch.gripper(a) and ch.gripper(b) and ch.side(a)==ch.side(b):return None
  return (0.,'self') if ch.side(a)==ch.side(b) else (.01,'robot_robot')
 g=a if ra else b
 return (.005,'gripper_held_environment') if ch.gripper(g) or ch.held[g] else (.010,'robot_environment')
def clearance(ch,q,hands):
 hits,_=contacts(ch,q,hands);reserve=.010;closest=None
 for c in ch.d.contact[:ch.d.ncon]:
  req=required(ch,*map(int,c.geom))
  if req is None or permission(ch,c,hands):continue
  if c.dist-req[0]<reserve:
   reserve=float(c.dist-req[0]);closest=dict(pair=[ch.gnames[int(g)] for g in c.geom],clearance_mm=float(c.dist*1000),required_mm=req[0]*1000)
 for a,n in enumerate(ch.gnames):
  if not n.startswith(('R_geom_','L_link')):continue
  for b,nn in enumerate(ch.gnames):
   if nn.startswith(('rail_beam_','rail_guide_','cable_chain_','wall_crossbar_','lane_hanger_')):
    dist=mujoco.mj_geomDistance(ch.m,ch.d,a,b,.02,None)
    if dist-.01<reserve:reserve=float(dist-.01);closest=dict(pair=[n,nn],clearance_mm=float(dist*1000),required_mm=10)
 return hits,reserve,closest
def edge(ch,a,b,ha,hb):
 a=np.array(a);b=np.array(b).copy()
 for n in s.ck.JOINTS:
  ix=ch.qa[n];lo,hi=ch.m.jnt_range[ch.jid[n]];options=[b[ix]+2*math.pi*j for j in range(-2,3) if lo<=b[ix]+2*math.pi*j<=hi]
  b[ix]=min(options,key=lambda x:abs(x-a[ix]))
 dq=b-a;bound=2*sum(abs(dq[ch.qa[n]]) for n in s.ck.JOINTS)+sum(abs(dq[ch.qa[n]]) for n in s.ck.BASE if n.endswith('carriage_x'))+sum(abs(dq[ch.qa[n]]) for n in s.ck.JAWS)
 mid=copy.deepcopy(ha)
 for side,h in mid.items():h['contacts']=[c for c in h.get('contacts',[]) if any(c['face']==x['face'] and c['held_parts']==x['held_parts'] for x in hb.get(side,{}).get('contacts',[]))]
 count=0;minrv=.01;cert=0
 def sample(t,hands):
  nonlocal count,minrv
  hits,rv,nearest=clearance(ch,a+t*dq,hands);count+=1;minrv=min(minrv,rv)
  if hits:return dict(pass_=False,alpha=t,first_blockers=hits[:8],states_checked=count,min_reserve_mm=minrv*1000)
  return rv
 for t,hands in ((0,ha),(1,hb)):
  x=sample(t,hands)
  if isinstance(x,dict):return x
 stack=[(0.,1.)]
 while stack:
  lo,hi=stack.pop();t=(lo+hi)/2;x=sample(t,mid)
  if isinstance(x,dict):return x
  need=bound*(hi-lo)/2
  if x>=need:cert+=1;continue
  if bound*(hi-lo)<=.001 or count>=24000:return dict(pass_=False,reason='Uncertified interval',states_checked=count,interval=[lo,hi],required_reserve_mm=need*1000,actual_reserve_mm=x*1000)
  stack.extend(((t,hi),(lo,t)))
 return dict(pass_=True,states_checked=count,min_reserve_mm=minrv*1000,certified_intervals=cert)
def motion_and_layout():
 best=json.loads((I/'results/best.json').read_text());results=[]
 keys=['Q05.carrot__peel_index_0','Q05.carrot__helper_index_0','Q22__acquire_eye_core_spoon','Q22__Remove_hard_core_without_seed_cavity','Q10.potato__withdraw']
 for key in keys:
  w=best['witnesses'][key];ph=next(p for p in s.P['phases'] if p['id']==w['phase']);sg=next(x for x in ph['segments'] if x['label']==w['label']);ch=s.Checker(ph,sg)
  es=[edge(ch,w['poses'][i]['q'],w['poses'][i+1]['q'],sg['poses'][i],sg['poses'][i+1]) for i in range(len(w['poses'])-1)]
  results.append(dict(stroke=key,pass_=all(x['pass_'] for x in es),edges=es));print('motion',key,results[-1]['pass_'],flush=True)
 pr=json.loads((I/'results/passing.json').read_text());ph=s.P['phases'][0];ch=s.Checker(ph,ph['segments'][0]);ch.bind_model(mujoco.MjModel.from_xml_path(str(I/'models/passing.xml')))
 hands=copy.deepcopy(ph['segments'][0]['poses'][0]);empty=copy.deepcopy(hands)
 for h in empty.values():h['contacts']=[]
 passing=edge(ch,pr['path']['q_start'],pr['path']['q_end'],empty,empty)
 motion=json.loads((I/'results/motion.json').read_text());q=np.array(motion['parking']['q']);hs,_=contacts(ch,q,empty);door=[]
 door_ids=[i for i,n in enumerate(ch.gnames) if n.startswith('cabinet_door_sweep_')]
 targets=[i for i,n in enumerate(ch.gnames) if ch.robot[i] or n.startswith(('slicer_','secondary_','dock_','raw_','output_'))]
 closest=None
 for a in door_ids:
  for b in targets:
   dist=mujoco.mj_geomDistance(ch.m,ch.d,a,b,.5,None)
   row=dict(pair=[ch.gnames[a],ch.gnames[b]],gap_mm=float(dist*1000),robot_part=bool(ch.robot[b]))
   if closest is None or row['gap_mm']<closest['gap_mm']:closest=row
   if dist<.01-1e-6:door.append(row)
 # Workspace intrusion relative to original front edge y=0 and slab top .85.
 ext=[]
 for n in ['R_mount','L_mount','R_tool','L_tool']:
  bid=ch.m.body(n).id;ext.append(dict(body=n,world_position_m=ch.d.xpos[bid].tolist()))
 out=dict(sections=results,passing=passing,parking_reference_clear=not hs,parked_door_sweep_minimum=closest,parked_door_sweep_infringements=door,parked_key_positions=ext,method='Fresh independent reference contacts plus adaptive midpoint relative-displacement certificate; identical held geometry, no extra support windows. Cabinet sweep distance includes environmental appliances even when collision masks suppress them.',scope='Section replay plus empty-arm passing; does not certify any complete meal connection, loaded overtaking, human posture, or real hinge/door geometry.')
 dump('motion_layout_independent.json',out);print('passing',passing,'door infringements',len(door),flush=True)
if __name__=='__main__':
 if sys.argv[1:]==['envelope']:envelope()
 elif sys.argv[1:]==['motion']:motion_and_layout()
 else:envelope();motion_and_layout()
