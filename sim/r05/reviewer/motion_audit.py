"""Read-only independent R05 trajectory replay on a model-derived point grid."""
import os,sys,json,math,time,copy,itertools
from pathlib import Path
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[n]='1'
import numpy as np,mujoco
from scipy.spatial.transform import Rotation,Slerp
H=Path(__file__).resolve().parent;I=H.parent/'integrator';sys.path.insert(0,str(I))
import final_check as f
import distance
original=(distance.Bounds.check,distance.Bounds.support,distance.Bounds.pair)
import motion_r05 as mo
distance.Bounds.check,distance.Bounds.support,distance.Bounds.pair=original
from point_bound import PointBound
O=H/'results';M=json.loads((I/'results/motion.json').read_text());W=json.loads((I/'results/static_all.json').read_text())['witnesses']
WORK={'clamped_food','wash_food','root_brush_work_face','secondary_work_face','greens_crease_land'}

class IndependentBound:
 """Triangle inequality, ancestor pivots and full slide travel, no imported weights."""
 def __init__(self,ch):
  self.ch=ch;m=ch.m;self.B=np.zeros((m.ngeom,m.nq));self.anc={};self.ids=np.flatnonzero(ch.robot|ch.held);self.radius=0.
  for g in self.ids:
   b=int(m.geom_bodyid[g]);r=float(np.linalg.norm(m.geom_pos[g])+m.geom_rbound[g]);down=[];a=[]
   while b:
    js=list(range(m.body_jntadr[b],m.body_jntadr[b]+m.body_jntnum[b]))
    for j in js:
     k=int(m.jnt_qposadr[j]);typ=int(m.jnt_type[j]);a.append((j,k,tuple(down)))
     if typ==3:self.B[g,k]=r+np.linalg.norm(m.jnt_pos[j])
     elif typ==2:self.B[g,k]=1
     else:raise ValueError('unsupported joint')
     down.append(k)
    r+=np.linalg.norm(m.body_pos[b])+sum(max(abs(m.jnt_range[j])) for j in js if m.jnt_type[j]==2)+sum(2*np.linalg.norm(m.jnt_pos[j]) for j in js)
    b=int(m.body_parentid[b])
   self.anc[g]=a;self.radius=max(self.radius,float(r))
 def segment(self,a,b):
  ch=self.ch;m=ch.m;dq=abs(b-a);ch.d.qpos[:]=a;mujoco.mj_kinematics(m,ch.d);loc=np.zeros(m.ngeom)
  for g,anc in self.anc.items():
   for j,k,down in anc:
    if m.jnt_type[j]==2:loc[g]+=dq[k]
    else:
     r=np.linalg.norm(ch.d.geom_xpos[g]-ch.d.xanchor[j])+m.geom_rbound[g]
     if down:r+=self.B[g,list(down)]@dq[list(down)]
     loc[g]+=r*dq[k]
  return float(min(np.max(self.B@dq),np.max(loc)))
 def actual(self,a,b):
  ch=self.ch;p=[]
  for q in (a,b):
   ch.d.qpos[:]=q;mujoco.mj_kinematics(ch.m,ch.d)
   # An enclosing sphere remains an enclosure after every rigid transform;
   # operator norm bounds *all* its points, including every mesh vertex.
   p.append((ch.d.geom_xpos[self.ids].copy(),ch.d.geom_xmat[self.ids].reshape(-1,3,3).copy()))
  c=np.linalg.norm(p[1][0]-p[0][0],axis=1);dr=p[1][1]-p[0][1]
  return float(np.max(c+np.linalg.svd(dr,compute_uv=False)[:,0]*ch.m.geom_rbound[self.ids]))

def valid(ch,w):
 sid=ch.m.site(w['side']+'_prep').id;n=np.array(w['normal']);dp=ch.d.site_xpos[sid]-w['tcp_origin_m'];ax=dp@n
 return bool(abs(np.linalg.norm(n)-1)<1e-10 and w['max_window_mm']<=50 and np.linalg.norm(dp-ax*n)<=.00002 and -.00002<=ax<=.05000001 and np.max(abs(ch.d.site_xmat[sid].reshape(3,3)-w['tcp_rotation']))<=.0002)

def state(ch,q,hands,working=False):
 ch.set_contacts(hands);ch.d.qpos[:]=q;mujoco.mj_kinematics(ch.m,ch.d)
 windows=getattr(ch,'contact_windows',[]);vs=[w for w in windows if valid(ch,w)]
 ch.allowed=[c for c in ch.allowed if (working and (c['face'] in WORK or c['face']=='peel_food_land' and hands[c['side']]['held']=='wash_pad')) or any(c['side']==w['side'] and c['face']==w['face'] for w in vs)]
 for w in vs:
  c={k:w[k] for k in ('side','face','held_parts','reason') if k in w}
  if c not in ch.allowed:ch.allowed.append(c)
 hits,mins,audit=f.contacts(ch,q);remain=[];discrep=[]
 for h in hits:
  if not h.get('reason') and h.get('real_gap_mm',0)>0:
   a,b=[ch.gnames.index(n) for n in h['pair']];v=ch.bounds.pair(a,b)
   if v['lower_m']>=h['required_gap_mm']/1000-1e-6:
    discrep.append(dict(pair=h['pair'],margin_mm=h['real_gap_mm'],proved_mm=v['lower_m']*1000));continue
  remain.append(h)
 return remain,mins,vs,discrep

def loads(ch,q,h):
 ch.d.qpos[:]=q;ch.d.qvel[:]=0;mujoco.mj_forward(ch.m,ch.d);m,d=ch.m,ch.d
 jac={};rot={};jp=np.zeros((3,m.nv));jr=np.zeros_like(jp)
 for side in h:
  mujoco.mj_jacSite(m,d,jp,jr,m.site(side+'_work').id);jw=jp.copy();jm=jr.copy();mujoco.mj_jacSite(m,d,jp,jr,m.site(side+'_mass').id);jac[side]=(jw,jm,jp.copy());rot[side]=d.site_xmat[m.site(side+'_prep').id].reshape(3,3).copy()
 env=json.loads((I/'results/torque_envelope.json').read_text())['envelope_Nm'];ratio=0;grip=math.inf
 for fs in itertools.product(*[v['check_forces_N'] for v in h.values()]):
  for ms in itertools.product(*[v['check_moments_Nm'] for v in h.values()]):
   tau=d.qfrc_bias.copy()
   for (side,v),force,moment in zip(h.items(),fs,ms):
    force=np.array(force);moment=np.array(moment);gravity=np.array([0,0,-9.81*v['held_kg']]);jw,jm,jg=jac[side];tau-=jw.T@force+jm.T@moment+jg.T@gravity
    F=np.linalg.norm(force+gravity);T=np.linalg.norm(np.cross(rot[side]@np.array(f.s.ck.offset_vector(v['work_offset_m'])),force)+np.cross(rot[side]@np.array(f.s.ck.offset_vector(v['mass_offset_m'])),gravity)+moment)
    gm=.5*150/(1.5*max(F,1e-12)) if v['grip']=='friction' else min(150/(1.5*max(F,1e-12)),15/(1.5*max(T,1e-12)));grip=min(grip,gm)
   ratio=max(ratio,max(abs(tau[ch.da[n]])/env[n] for n in f.s.ck.JOINTS))
 return float(ratio),float(grip)

def replay_path(ch,path,ha,hb,windows,working=False,work_k=0,second=None):
 ch.contact_windows=windows;ib=IndependentBound(ch);pb=PointBound(ch);path=np.array(path);count=0;maxstep=0;observed=0;bdiff=0;ratio=0;grip=math.inf;minres={};bad=None;discrep=[];window_states=0;both=0
 common={side:dict(v,contacts=[c for c in v.get('contacts',[]) if c in hb.get(side,{}).get('contacts',[])]) for side,v in ha.items()}
 rots={side:Slerp([0,1],Rotation.from_matrix([ch.target_rotation(ha[side],work_k),ch.target_rotation(hb[side],work_k)])) for side in ha} if working else {}
 for si,(a,b) in enumerate(zip(path,path[1:])):
  independent=ib.segment(a,b);submitted=pb.segment_bound(a,b);bdiff=max(bdiff,abs(independent-submitted));n=max(1,math.ceil(independent/.004));maxstep=max(maxstep,independent/n)
  moving=[side for side in f.s.model.SIDES if any(abs(a[ch.qa[j]]-b[ch.qa[j]])>1e-8 for j in f.s.ck.ARMS[side]+[side+'_carriage_x'])]
  both+=int(len(moving)==2)
  if second:n=max(n,math.ceil(IndependentBound(second[0]).segment(a,b)/.004))
  for k in range(n+1):
   q=a+(b-a)*k/n;h=ha if si==0 and k==0 else hb if si==len(path)-2 and k==n else common
   if k:observed=max(observed,ib.actual(a+(b-a)*(k-1)/n,q))
   hits,mins,vs,ds=state(ch,q,h,working);count+=1;window_states+=bool(vs);discrep.extend(ds[:1])
   for cat,v in mins.items():
    if cat not in minres or v['reserve_mm']<minres[cat]['reserve_mm']:minres[cat]=v
   if hits:bad=dict(kind='collision',segment=si,k=k,q=q.tolist(),pairs=hits[:5]);break
   if not all(ch.m.jnt_range[ch.jid[name],0]-1e-8<=q[ch.qa[name]]<=ch.m.jnt_range[ch.jid[name],1]+1e-8 for name in ch.qa):bad=dict(kind='joint range');break
   tr,gm=loads(ch,q,h);ratio=max(ratio,tr);grip=min(grip,gm)
   if tr>1 or gm<1:bad=dict(kind='static load/grip',ratio=tr,grip=gm);break
   if working:
    t=(si+k/n)/(len(path)-1)
    for side in ha:
     sid=ch.m.site(side+'_prep').id;target=(1-t)*np.array(ha[side]['pos'])+t*np.array(hb[side]['pos']);pe=np.linalg.norm(ch.d.site_xpos[sid]-target);oe=Rotation.from_matrix(rots[side](t).as_matrix().T@ch.d.site_xmat[sid].reshape(3,3)).magnitude()
     if pe>.005 or oe>math.radians(3):bad=dict(kind='working pose',position_mm=pe*1000,orientation_deg=math.degrees(oe));break
   if second:
    ch2,h2=second;hits2,_,_,_=state(ch2,q,h2,False);count+=1
    if hits2:bad=dict(kind='following-scene collision',segment=si,k=k,pairs=hits2[:5]);break
    tr,gm=loads(ch2,q,h2);ratio=max(ratio,tr);grip=min(grip,gm)
    if tr>1 or gm<1:bad=dict(kind='following-scene load/grip',ratio=tr,grip=gm);break
   if bad:break
  if bad:break
 return dict(pass_=bad is None,states_checked=count,maximum_independent_grid_bound_mm=maxstep*1000,maximum_enclosing_sphere_point_step_mm=observed*1000,maximum_bound_disagreement_m=bdiff,max_envelope_ratio=ratio,min_grip=None if grip==math.inf else grip,min_clearance=minres,valid_window_states=window_states,two_arm_moving_segments=both,first_rejection=bad,positive_margin_discrepancies=discrep[:10])

def main():
 mode=sys.argv[1];ids=list(map(int,sys.argv[2:]));rows=[];t0=time.monotonic()
 for i in ids:
  ph,sg,key=mo.items[i]
  if mode=='internal':
   r=M['internal'][i];sg=r.get('segment_override',sg);ch=mo.scene(ph,sg,i);edges=[]
   for j,e in enumerate(r['edges']):
    if not e.get('path'):edges.append(dict(pass_=False,reason='No submitted proposal',last_rejection=e.get('last_rejection')));continue
    if j and np.max(abs(np.array(r['edges'][j-1]['path'][-1])-e['path'][0]))>1e-9:edges.append(dict(pass_=False,reason='Disconnected edges'));break
    old=ch.seg;ch.seg=dict(old,poses=[sg['poses'][j],sg['poses'][j+1]]);ep=f.replay(ch,dict(k=W[key]['k'],poses=[dict(q=e['path'][0]),dict(q=e['path'][-1])]))['ok'];ch.seg=old
    out=replay_path(ch,e['path'],sg['poses'][j],sg['poses'][j+1],e.get('contact_windows',[]),sg['action']=='process',W[key]['k']);out['reference_endpoints_pass']=ep;out['pass_'] &= ep;edges.append(out)
   row=dict(index=i,stroke=key,submitted_pass=r['ok'],pass_=bool(edges) and all(x['pass_'] for x in edges),edges=edges)
  else:
   r=M['between_strokes'][i];ph2,sg2,key2=mo.items[i+1];ch=mo.scene(ph,sg,i);ch2=mo.scene(ph2,sg2,i+1);ha=sg['poses'][-1];hb=sg2['poses'][0];path=r['planner'].get('path',[])
   if path:
    ch2.contact_windows=r['planner'].get('contact_windows',[]);out=replay_path(ch,path,ha,hb,r['planner'].get('contact_windows',[]),second=(ch2,hb));kind='Full supplied proposal'
   else:
    a=np.array(W[key]['poses'][-1]['q']);b=np.array(W[key2]['poses'][0]['q']);out=replay_path(ch,[a,b],ha,{side:dict(h,contacts=[]) for side,h in ha.items()},r['planner'].get('contact_windows',[]));kind='Independent direct connection, stopped at first rejection'
   rejection=r['planner'].get('last_rejection');saved=None
   if rejection:
    hits,_,_,_=state(ch,np.array(rejection['q']),ha);saved=dict(reference_rejection_reproduced=bool(hits),pairs=hits[:5])
   row=dict(index=i,from_stroke=key,to_stroke=key2,submitted_pass=r['ok'],compatible_attachment=r['compatible_attachment'],replay_kind=kind,isolated_geometry=out,saved_rejection=saved,conserved_meal_pass=False)
  rows.append(row);print(mode,i,'PASS',row.get('pass_',row.get('isolated_geometry',{}).get('pass_')),'states',sum(e.get('states_checked',0) for e in row.get('edges',[row.get('isolated_geometry',{})])),flush=True)
  (O/f'motion_{mode}_{ids[0]}_{ids[-1]}.json').write_text(json.dumps(dict(rows=rows,elapsed_s=time.monotonic()-t0),indent=2,allow_nan=False))
if __name__=='__main__':main()
