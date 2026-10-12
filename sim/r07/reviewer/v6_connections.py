from v6_common import *
import hashlib
# The imported motion module expects the layout at argv[1].
sys.argv.insert(1,v.ID)
from binding_v6_r07 import Planner
from point_bound import PointBound
root=I/'results/connections_v6'/v.ID
saved_rows=[json.loads(x.read_text()) for x in sorted(root.glob('*.json'),key=lambda p:int(p.stem))]
bundle=read(f'meal_pose_proposals_v6/{v.ID}.json')['records']
out=O/'connection_rows';out.mkdir(exist_ok=True)
selected=set(map(int,sys.argv[2:])) if len(sys.argv)>2 else set(range(110))
for row in saved_rows:
 if row['connection'] not in selected:continue
 dest=out/f"{row['connection']}.json"
 if dest.exists():continue
 result=dict(index=row['connection'],submitted_status=row['status'],submitted_conditional_pass=row['pass_'],submitted_geometric_pass=row['geometric_connection_pass'],legs=[],meal_pass=False,two_arm_overlap=False)
 for leg in row['legs']:
  aa,bb=row['from_stroke'],row['to_stroke'];which=bb if leg['name']=='loaded_transfer_to_next_stroke' else aa
  h=copy.deepcopy(v.items[which['index']][1]['poses'][0 if which is bb else -1]['R']);h['roll_deg']+=which['roll_deg']
  for level in ('nominal','check'):h[level+'_forces_N']=[[0,0,0]];h[level+'_moments_Nm']=[[0,0,0]]
  h['contacts']=[c for c in h.get('contacts',[]) if c['kind']=='grasp_release_support']
  attached=leg['state']['attached']
  if leg['name']=='empty_approach_existing_object' or attached is None:h.update(held='empty',held_kg=0,grip='key',work_offset_m=0,mass_offset_m=0,contacts=[])
  else:h['held_kg']=leg['state']['objects'][attached]['mass_kg']
  hands={'R':h};ch=v.scene(which['index']);xml=(I/leg['model_xml']).read_text();ch.xml=xml;ch.bind_model(mujoco.MjModel.from_xml_string(xml));ch.hands=hands;ch.working_stroke=False;ch.contact_windows=leg['planner'].get('contact_windows',[]);ch.pending_grasp=leg.get('grasp_window');ch.set_contacts(hands)
  # Saved own supports are added by support_hand during planning; reconstruct only those named declarations.
  for w in ch.contact_windows:
   if w.get('kind')=='grasp_release_support':rt.SUPPORT_REGISTRY.setdefault(w['object_id'],set()).add(w['support_id'])
  pl=Planner(ch,hands,seconds=65);ib=IndependentBound(ch);pb=PointBound(ch)
  path=leg['planner'].get('path') or [];bad=None;states=0;maxstep=delta=actual=mt=arc=0.;mg=math.inf;mins={};leaks=[];reject=None
  if not path:
   last=leg['planner'].get('last_rejection')
   if last:
    reject=dict(reproduced=not pl.state(np.array(last['q']),hands),blocker=pl.last);states+=1
   # Fresh straight diagnostic for the retained-attachment leg. Other failed binding legs have no complete requested endpoint witness.
   if leg['name']=='retained_attachment':path=[bundle[aa['id']][-1]['q'],bundle[bb['id']][0]['q']]
  for si,(a,b) in enumerate(zip(np.array(path),np.array(path)[1:])):
   D=ib.segment(a,b);delta=max(delta,abs(D-pb.segment_bound(a,b)));arc+=D;N=max(1,math.ceil(D/.004));maxstep=max(maxstep,D/N*1000)
   for k in range(N+1):
    q=a+(b-a)*k/N;states+=1
    if k:actual=max(actual,ib.actual(a+(b-a)*(k-1)/N,q)*1000)
    if not pl.state(q,hands):bad=dict(segment=si,grid=k,kind='gap',detail=pl.last);break
    leaks.extend(c for c in ch.allowed if c.get('kind')=='working_stroke')
    load=independent_pose(ch,q,hands,0,geometry=False);mt=max(mt,load['torque']['check']);mg=min(mg,load['grip']['check'])
    if not load['ranges_ok'] or load['torque']['check']>1 or load['grip']['check']<1 or not all(p['chart_ok'] for p in load['payload']):bad=dict(kind='load/range',load=load);break
    for cat,ix in ch.bounds.catids.items():
     vals=(ch.bounds.last_lower[ix]-ch.bounds.need[ix])*1000;vals=vals[np.isfinite(vals)&(vals<1e6)]
     if len(vals):mins[cat]=min(mins.get(cat,math.inf),float(min(vals)))
   if bad:break
  rr=dict(name=leg['name'],model_hash_matches=hashlib.sha256(xml.encode()).hexdigest()==leg['model_sha256'],saved_path=bool(leg['planner'].get('path')),pass_=bool(path) and bad is None,states_checked=states,max_point_step_mm=maxstep,max_actual_sphere_step_mm=actual,max_bound_delta_m=delta,point_arc_bound_m=arc,minimum_reserves_mm=mins,torque_ratio=mt,grip_margin=None if math.isinf(mg) else mg,working_leaks=leaks,blocker=bad,saved_rejection=reject,allocated_s=leg['allocated_budget_s'],planner_states=leg['planner']['states_checked'])
  result['legs'].append(rr)
 dest.write_text(json.dumps(result,indent=2,allow_nan=False));print('CONNECTION',row['connection'],[(x['saved_path'],x['pass_'],x['states_checked']) for x in result['legs']],flush=True)
rows=[json.loads(x.read_text()) for x in sorted(out.glob('*.json'),key=lambda p:int(p.stem))]
dump('connections.json',dict(rows=rows,checked_connections=len(rows),states_checked=sum(l['states_checked'] for r in rows for l in r['legs']),saved_legs=sum(l['saved_path'] for r in rows for l in r['legs']),passed_saved_legs=sum(l['saved_path'] and l['pass_'] for r in rows for l in r['legs']),method='Every saved full leg is interpolated at independently reconstructed <=4mm bound in its hash-matched persistent XML. Missing paths get saved rejection replay and retained-attachment straight diagnostics; these are not successful trajectories.'))
