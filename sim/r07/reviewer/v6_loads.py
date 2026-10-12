from v6_common import *
rows=[]
for file in sorted((I/'results/connections_v6'/v.ID).glob('*.json'),key=lambda f:int(f.stem)):
 r=json.loads(file.read_text())
 for leg in r['legs']:
  path=leg['planner'].get('path')
  if not path:continue
  aa,bb=r['from_stroke'],r['to_stroke'];which=bb if leg['name']=='loaded_transfer_to_next_stroke' else aa
  h=copy.deepcopy(v.items[which['index']][1]['poses'][0 if which is bb else -1]['R']);h['roll_deg']+=which['roll_deg'];attached=leg['state']['attached']
  if leg['name']=='empty_approach_existing_object' or attached is None:h.update(held='empty',held_kg=0,grip='key',work_offset_m=0,mass_offset_m=0,contacts=[])
  else:h['held_kg']=leg['state']['objects'][attached]['mass_kg']
  # Reconstruct six signed inertial alternatives independently of zero().
  for level,factor in (('nominal',1),('check',1.5)):
   h[level+'_forces_N']=[(np.eye(3)[axis]*sign*h['held_kg']*.3*factor).tolist() for axis in range(3) for sign in (-1,1)]
   h[level+'_moments_Nm']=[[0,0,0]]
  hands={'R':h};ch=v.scene(which['index']);ch.xml=(I/leg['model_xml']).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.working_stroke=False;ch.contact_windows=[];ib=IndependentBound(ch);count=0;mt=0;mg=1e9;bad=[];step=0.
  for a,b in zip(np.array(path),np.array(path)[1:]):
   D=ib.segment(a,b);N=max(1,math.ceil(D/.004));step=max(step,D/N*1000)
   for k in range(N+1):
    q=a+(b-a)*k/N;v0=independent_pose(ch,q,hands,0,geometry=False);count+=1;mt=max(mt,v0['torque']['check']);mg=min(mg,v0['grip']['check'])
    if v0['torque']['check']>1 or v0['grip']['check']<1 or not v0['ranges_ok'] or not all(x['chart_ok'] for x in v0['payload']):bad.append(v0)
  rows.append(dict(connection=r['connection'],leg=leg['name'],pass_=not bad,states=count,max_point_step_mm=step,max_torque_ratio=mt,min_grip_margin=mg,held_mass_kg=h['held_kg'],check_acceleration_m_s2=.45,failures=bad));print('LOAD',r['connection'],leg['name'],count,not bad,flush=True)
  dump('connection_loads.json',dict(rows=rows,passed=sum(x['pass_'] for x in rows),states=sum(x['states'] for x in rows),scope='Independent Jacobian gravity plus six signed payload acceleration alternatives, 0.3m/s2 times SF1.5. Source geometric replays are separate; no working wrench or permission.'))
