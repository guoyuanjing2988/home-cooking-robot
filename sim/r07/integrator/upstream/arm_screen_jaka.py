"""Cheaper main-arm screen; no use of nominal payload as a torque limit."""
import json,copy,time,itertools,sys
import numpy as np,mujoco
from scipy.optimize import differential_evolution
import jaka_model
import solver as s
import final_check as f
arm=sys.argv[1];rated=7 if arm=='JAKA_Zu7' else 5
H=s.HERE;beg=time.monotonic();out=[]
# AUBO's full CoM curve/revision is not substituted with UR or xArm data.
# Numerical screen here is limited to the matched, publicly charted xArm model.
c=copy.deepcopy(s.model.CONFIG);c.update(arm=arm+'+xArm6',arms=[arm,'xArm6'])
tree,meta=s.model.build(dict(c,transport_only=True));m=mujoco.MjModel.from_xml_string(__import__('xml.etree.ElementTree',fromlist=['']).tostring(tree.getroot(),encoding='unicode'))
for side in ['R','L']:
 for n in [side+'_tool',side+'_jaw_minus',side+'_jaw_plus']:
  m.body_mass[m.body(n).id]=1e-9;m.body_inertia[m.body(n).id]=1e-12
d=mujoco.MjData(m);mujoco.mj_setConst(m,d);qa={m.joint(i).name:int(m.jnt_qposadr[i]) for i in range(m.njnt)};da={m.joint(i).name:int(m.jnt_dofadr[i]) for i in range(m.njnt)}
audit=object.__new__(s.ck.Checker);audit.desc=s.ck.hand([0,0,1],jaw_axis=[0,1,0]);audit.bind_model(m)
env={n:v for n,v in json.loads((H/'results/torque_envelope.json').read_text())['envelope_Nm'].items() if n.startswith('L_')};maxima=[]
for side in ['R']:
 names=meta['arms'][side];ds=[da[n] for n in names];jp=np.zeros((3,m.nv));jr=np.zeros_like(jp);site=m.site(side+'_attachment_site').id;bounds=[m.jnt_range[m.joint(n).id] for n in names]
 def evaluate(x,gate=True):
  d.qpos[:]=m.qpos0
  for n,v in zip(names,x):d.qpos[qa[n]]=v
  mujoco.mj_forward(m,d);mujoco.mj_jacSite(m,d,jp,jr,site);tau=d.qfrc_bias[ds]+rated*9.81*jp[2,ds];rt=d.site_xmat[site].reshape(3,3)
  coef=np.array([rated*9.81*np.cross(jr[:,ds].T,rt[:,i])[:,2] for i in range(3)]).T
  cap=abs(tau)+.075*np.linalg.norm(coef,axis=1)
  audit.d.qpos[:]=d.qpos
  hits=s.ck.Checker.forbidden(audit,d.qpos)
  valid=not any(all(n.startswith(side+'_') and not any(k in n for k in ['adapter','bearing','drive','gripper','finger']) for n in h['pair']) for h in hits)
  return cap,valid,tau,coef
 for j,n in enumerate(names):
  witnesses=[]
  for seed in [401,402,403]:
   def obj(x):
    cap,ok,*_=evaluate(x);return -cap[j] if ok else 1000.
   res=differential_evolution(obj,bounds,popsize=7,maxiter=30,seed=seed,polish=False,workers=1)
   cap,ok,tau,co=evaluate(res.x)
   if ok:witnesses.append((float(cap[j]),res.x.tolist(),seed,res.nfev))
  value,x,seed,evals=max(witnesses);env[n]=value;maxima.append(dict(joint=n,envelope_Nm=value,joints_rad=x,retained_seed=seed,starts=3,evaluations=evals,OEM_self_collision_ok=True))
  print(n,round(value,4),flush=True)
class Alt(s.Checker):
 def torque_multi(self,q,hands,forces,moments=None):
  m,d=self.m,self.d;d.qpos[:]=q;d.qvel[:]=0;mujoco.mj_forward(m,d);tau=d.qfrc_bias.copy();jp=np.zeros((3,m.nv));jr=np.zeros_like(jp)
  for side,h in hands.items():
   mujoco.mj_jacSite(m,d,jp,jr,m.site(side+'_work').id);tau-=jp.T@np.array(forces[side])+jr.T@np.array((moments or {}).get(side,[0,0,0]));mujoco.mj_jacSite(m,d,jp,jr,m.site(side+'_mass').id);tau-=jp.T@np.array([0,0,-h['held_kg']*9.81])
  vals={n:float(abs(tau[self.da[n]])) for n in s.ck.JOINTS};rat={n:v/env[n] for n,v in vals.items()};n=max(rat,key=rat.get)
  return dict(ratio=rat[n],joint=n,required_Nm=vals[n],reference_Nm=env[n],joints=rat,demand_Nm=vals,reference_type=arm+' rated payload at75mm sphere, constrained sampling lower estimate')
for pid,label in [('Q02.carrot','wash'),('Q05.carrot','peel_index_0'),('Q05.potato','peel_index_0'),('Q22','Remove hard core without seed cavity'),('Q25','Deliver tomato next-step bowl')]:
 ph=next(x for x in s.P['phases'] if x['id']==pid);sg=next(x for x in ph['segments'] if x['label']==label);ch=Alt(ph,sg,c);rng=np.random.default_rng(1000);rs=[ch.run_seed(k,rng) for k in range(96)];good=[r for r in rs if r['ok']]
 verified=[]
 for row in good[:8]:
  audit=f.replay(ch,row)
  actual_ok=all(p['total_flange_kg']<=3 and p['CoM_radius_m']<=(.35 if rated==7 else .25) for po in audit['poses'] for p in po['payload'] if p['side']=='R')
  if audit['ok'] and actual_ok:verified.append(audit)
 out.append(dict(phase=pid,stroke=label,seeds_tried=96,solutions_found=len(good),verified_witnesses=len(verified),hardware_admitted_witnesses=0,witnesses=verified,rows=rs,status='Raw published-model diagnostic only: link masses do not match catalogue hardware; all105 strokes, persistent motion and idle not admitted'))
 print(pid,label,len(good),'verified',len(verified),flush=True)
source=__import__('xml.etree.ElementTree',fromlist=['']).parse(H/'sources/jaka_description/urdf'/('jaka_zu'+arm[-1]+'.urdf')).getroot();source_mass=sum(float(x.get('value')) for x in source.findall('.//link/inertial/mass'))
(H/('results/arm_screen_'+arm+'.json')).write_text(json.dumps(dict(config=c,envelope_Nm=env,envelope_witnesses=maxima,screen=out,elapsed_s=time.monotonic()-beg,source_arm_mass_kg=source_mass,catalog_arm_mass_kg=22 if rated==7 else 23,model_mass_match=False,hardware_admitted_witnesses=0,model_admission='URDF mass sum91.9115kg for Zu7 versus22kg catalogue; Zu5 sum15.483kg versus23kg. Do not scale masses or promote these torque ratios as hardware capacity.',chart_boundary=dict(total_flange_kg=rated,CoM_radius_m=.075,chart_source='JAKA Zu V11 pp65-67;75mm inside flat rated segment ending approximately90mm'),actual_payload_conservative_gate=dict(total_flange_kg=3,CoM_radius_m=.35 if rated==7 else .25),status='NOT_ADMITTED_COMPLETE_CONFIGURATION',published_joint_output_torques_Nm=None,method='Three constrained DE starts/joint in actual152.114degree mounting; source EOAT removed and replaced with total rated mass at75mm. Conservative finite lower estimates for this URDF, not admitted real hardware or exact global maximum. Self collisions and public source ranges checked; no URDF effort admission.'),indent=2))
