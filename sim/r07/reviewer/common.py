"""Read-only R07 audit runtime. Numerical results are written only here."""
import os,sys,json,math,copy,itertools,time
from pathlib import Path
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[n]='1'
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent; I=H.parent/'integrator'; O=H/'results'
O.mkdir(exist_ok=True)
sys.path.insert(0,str(I))
import numpy as np,mujoco
from scipy.spatial.transform import Rotation
import r07_runtime as rt
import motion_r05 as mo
f=rt.f;s=rt.s
ENV=json.loads((I/'results/torque_envelope.json').read_text())['envelope_Nm']
def read(n):return json.loads((I/'results'/n).read_text(encoding='utf-8-sig'))
def dump(n,x):(O/n).write_text(json.dumps(x,indent=2,allow_nan=False),encoding='utf-8')
def seed(i):
    r=read('static/'+str(i)+'.json')
    return min(r['rows'],key=lambda r:sum(e['position_mm']+3*e['orientation_deg'] for p in r['raw']['poses'] for e in p['errors']))['raw']['k']
def independent_pose(ch,q,hands,k):
    m,d=ch.m,ch.d;ch.set_contacts(hands);d.qpos[:]=q;d.qvel[:]=0;mujoco.mj_forward(m,d)
    errors=[];payload=[];jac={};rot={};jp=np.zeros((3,m.nv));jr=np.zeros_like(jp)
    for side,h in hands.items():
        sid=m.site(side+'_prep').id;rot[side]=d.site_xmat[sid].reshape(3,3).copy()
        target=ch.target_rotation(h,k);phi=Rotation.from_matrix(target.T@rot[side]).as_rotvec();theta=np.linalg.norm(phi);p=target.T@(d.site_xpos[sid]-h['pos'])
        coeff=1/12+theta**2/720 if theta<1e-5 else 1/theta**2-(1+math.cos(theta))/(2*theta*math.sin(theta))
        log_translation=p-.5*np.cross(phi,p)+coeff*np.cross(phi,np.cross(phi,p))
        errors.append(dict(side=side,position_mm=float(np.linalg.norm(log_translation)*1000),direct_TCP_position_mm=float(np.linalg.norm(p)*1000),orientation_deg=float(np.degrees(theta))))
        mujoco.mj_jacSite(m,d,jp,jr,m.site(side+'_work').id);jw=jp.copy();jm=jr.copy()
        mujoco.mj_jacSite(m,d,jp,jr,m.site(side+'_mass').id);jac[side]=(jw,jm,jp.copy())
        bids=[m.body(side+n).id for n in ('_tool','_jaw_minus','_jaw_plus')]
        mass=sum(m.body_mass[b] for b in bids)+h['held_kg']
        com=(sum(m.body_mass[b]*d.xipos[b] for b in bids)+h['held_kg']*d.site_xpos[m.site(side+'_mass').id])/mass
        sid=m.site(side+'_attachment_site').id;loc=d.site_xmat[sid].reshape(3,3).T@(com-d.site_xpos[sid])
        valid=mass<=5 and np.linalg.norm(loc)<=.350 if side=='R' else mass<=2 and np.linalg.norm(loc[:2])<=.200 and abs(loc[2])<=.180
        task_cap=side!='L' or h['held_kg']<=.25+1e-9
        payload.append(dict(side=side,total_flange_kg=float(mass),held_kg=h['held_kg'],CoM_flange_m=loc.tolist(),chart_ok=bool(valid),helper_task_cap_ok=bool(task_cap)))
    bias=d.qfrc_bias.copy();tq={};gm={}
    for level in ('nominal','check'):
        ratio=0;grip=math.inf
        for forces in itertools.product(*[h[level+'_forces_N'] for h in hands.values()]):
            for moments in itertools.product(*[h[level+'_moments_Nm'] for h in hands.values()]):
                tau=bias.copy()
                for (side,h),force,moment in zip(hands.items(),forces,moments):
                    force=np.array(force);moment=np.array(moment);g=np.array([0,0,-h['held_kg']*9.81]);jw,jm,jg=jac[side]
                    tau-=jw.T@force+jm.T@moment+jg.T@g
                    F=np.linalg.norm(force+g);T=np.linalg.norm(np.cross(rot[side]@np.array(s.ck.offset_vector(h['work_offset_m'])),force)+np.cross(rot[side]@np.array(s.ck.offset_vector(h['mass_offset_m'])),g)+moment)
                    v=.5*150/(1.5*max(F,1e-12)) if h['grip']=='friction' else min(150/(1.5*max(F,1e-12)),15/(1.5*max(T,1e-12)))
                    grip=min(grip,float(v))
                ratio=max(ratio,max(float(abs(tau[ch.da[n]])/ENV[n]) for n in s.ck.JOINTS))
        tq[level]=ratio;gm[level]=grip
    ranges=all(m.jnt_range[ch.jid[n],0]-1e-8<=q[ch.qa[n]]<=m.jnt_range[ch.jid[n],1]+1e-8 for n in ch.qa)
    hits,mins,audit=f.contacts(ch,q)
    ok=not hits and ranges and all(e['position_mm']<=5 and e['orientation_deg']<=3 for e in errors) and tq['check']<=1 and gm['check']>=1 and all(p['chart_ok'] and p['helper_task_cap_ok'] for p in payload)
    return dict(ok=bool(ok),errors=errors,ranges_ok=bool(ranges),forbidden=hits,min_clearance=mins,torque=tq,grip=gm,payload=payload)

class IndependentBound:
    """Reconstructed ancestor bound; no imported PointBound weights."""
    def __init__(self,ch):
        self.ch=ch;m=ch.m;self.B=np.zeros((m.ngeom,m.nq));self.anc={};self.ids=np.flatnonzero(ch.robot|ch.held)
        for g in self.ids:
            b=int(m.geom_bodyid[g]);r=float(np.linalg.norm(m.geom_pos[g])+m.geom_rbound[g]);down=[];a=[]
            while b:
                js=list(range(m.body_jntadr[b],m.body_jntadr[b]+m.body_jntnum[b]))
                for j in js:
                    k=int(m.jnt_qposadr[j]);typ=int(m.jnt_type[j]);a.append((j,k,tuple(down)))
                    if typ==3:self.B[g,k]=r+np.linalg.norm(m.jnt_pos[j])
                    elif typ==2:self.B[g,k]=1
                    else:raise ValueError('Unsupported joint')
                    down.append(k)
                r+=np.linalg.norm(m.body_pos[b])+sum(max(abs(m.jnt_range[j])) for j in js if m.jnt_type[j]==2)+sum(2*np.linalg.norm(m.jnt_pos[j]) for j in js)
                b=int(m.body_parentid[b])
            self.anc[g]=a
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
        ch=self.ch;ps=[]
        for q in (a,b):
            ch.d.qpos[:]=q;mujoco.mj_kinematics(ch.m,ch.d)
            ps.append((ch.d.geom_xpos[self.ids].copy(),ch.d.geom_xmat[self.ids].reshape(-1,3,3).copy()))
        c=np.linalg.norm(ps[1][0]-ps[0][0],axis=1);dr=ps[1][1]-ps[0][1]
        return float(np.max(c+np.linalg.svd(dr,compute_uv=False)[:,0]*ch.m.geom_rbound[self.ids]))
