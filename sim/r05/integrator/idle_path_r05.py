"""A static storage pass is not a deployable park: explicit4mm lift trial."""
import json,numpy as np,mujoco,xml.etree.ElementTree as E
import final_check as f
H=f.s.HERE;O=H/'results';idle=json.loads((O/'idle_repair.json').read_text());ph=f.s.P['phases'][0];sg=ph['segments'][0];q=np.array(idle['parked_snapshot']['q']);goal=idle['parked_snapshot']['lift_m'];trials=[]
for order in ('appliance_transfer_before_elevator','elevator_before_appliance_transfer'):
 root=E.parse(H/'models/idle_r05.xml')
 if order=='elevator_before_appliance_transfer':
  for g in root.findall('worldbody/geom'):
   if g.get('name','').startswith('slicer_'):
    p=np.fromstring(g.get('pos'),sep=' ');p[0]+=2.95;g.set('pos',f.s.model.fmt(p))
  root.write(H/'models/idle_before_transfer.xml',encoding='unicode')
 ch=f.s.Checker(ph,sg);ch.bind_model(mujoco.MjModel.from_xml_string(E.tostring(root.getroot(),encoding='unicode')));ch.set_contacts(sg['poses'][0]);body=ch.m.body('rail_structure').id;records=[];blocked=None
 for alpha in np.linspace(0,1,max(1,int(np.ceil(goal/.004)))+1):
  ch.m.body_pos[body,2]=goal*alpha;hits,mins,audit=f.contacts(ch,q);records.append(dict(alpha=float(alpha),rail_lift_m=float(goal*alpha),blockers=hits[:12]))
  if hits:blocked=records[-1];break
 trials.append(dict(order=order,pass_=blocked is None,checked_states=len(records),first_rejection=blocked,records=records))
 print(order,'clear',blocked is None,'lift',blocked['rail_lift_m'] if blocked else goal,'pair',blocked['blockers'][0]['pair'] if blocked else None,flush=True)
blocked=trials[-1]['first_rejection']
out=dict(schema='r05.idle-deployment-trial',pass_=any(t['pass_'] for t in trials),max_robot_point_step_mm=float(goal/max(1,int(np.ceil(goal/.004)))*1000),checked_states=sum(t['checked_states'] for t in trials),first_rejection=blocked,trials=trials,proof='Every rail/arm/held point translates by exactly the elevator increment; all other geometry remains fixed in each alternative order. Cabinet bodies and wall are retained. A collision of a fixed crossbar/power track cannot be removed by arm IK or carriage seeds.',limits='Two initial-state/order candidates, not a credited appliance teleport. Appliance transfer and meal-to-bay arm paths are additionally unverified. This trial does not certify deployment even if its samples were clear.')
(O/'idle_path.json').write_text(json.dumps(out,indent=2));idle.update(static_storage_snapshot_pass=idle['pass_'],pass_=False,status='FAIL_DEPLOYMENT',storage_motion_verified=False,deployment_trial='results/idle_path.json',deployment_blocker=blocked,baseline_idle_audit='results/idle.json');(O/'idle.json').write_text(json.dumps(idle,indent=2));print('IDLE_DEPLOYMENT',out['pass_'],'blocker',blocked['blockers'][0]['pair'] if blocked else None)
