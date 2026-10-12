"""Connected meal audit: no object teleporting and no intended-contact windows."""
import os
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[n]='1'
import json,copy,math,time,sys,xml.etree.ElementTree as E
import numpy as np,mujoco
import final_check as f
s=f.s;H=s.HERE;O=H/'results';began=time.monotonic();calls=0

def plain_contacts(hands):return {side:dict(h,contacts=[]) for side,h in hands.items()}
def common_contacts(a,b):
 out=copy.deepcopy(a)
 for side,h in out.items():
  other=b.get(side,{})
  h['contacts']=[c for c in h.get('contacts',[]) if any(c['face']==x['face'] and c['held_parts']==x['held_parts'] for x in other.get('contacts',[]))]
 return out
def state(ch,q,hands):
 global calls
 calls+=1;ch.set_contacts(hands);hits,mins,ca=f.contacts(ch,q)
 reserve=min(v['reserve_mm'] for v in mins.values())
 return hits,reserve,mins
def shortq(ch,a,b):
 b=np.array(b).copy()
 for side in s.model.SIDES:
  for n in s.ck.ARMS[side]:
   ix=ch.qa[n];lo,hi=ch.m.jnt_range[ch.jid[n]]
   vs=[b[ix]+j*2*math.pi for j in range(-2,3) if lo<=b[ix]+j*2*math.pi<=hi]
   b[ix]=min(vs,key=lambda v:abs(v-a[ix]))
 return b
def displacement_bound(ch,dq):
 #2m exceeds this model's flange reach+full EOAT/held-object radius.
 return 2*sum(abs(dq[ch.qa[n]]) for n in s.ck.JOINTS)+sum(abs(dq[ch.qa[n]]) for n in s.ck.BASE if n.endswith('carriage_x'))+sum(abs(dq[ch.qa[n]]) for n in s.ck.JAWS)
def edge(ch,a,b,ha,hb,max_states=24000):
 a=np.array(a);b=shortq(ch,a,b);dq=b-a;bound=displacement_bound(ch,dq)
 checked=0;min_reserve=1e30;certified=0;max_certificate_bound=0
 midhands=common_contacts(ha,hb)
 def sample(alpha,hands):
  nonlocal checked,min_reserve
  q=a+dq*alpha;hits,reserve,mins=state(ch,q,hands);checked+=1;min_reserve=min(min_reserve,reserve)
  if hits:return dict(pass_=False,reason='unchanged gap/contact gate',states_checked=checked,alpha=alpha,q_blocked=q.tolist(),first_blockers=hits[:8],min_reserve_mm=min_reserve)
  return reserve
 for alpha,hands in ((0,ha),(1,hb)):
  result=sample(alpha,hands)
  if isinstance(result,dict):return result
 # A midpoint reserve certifies its whole interval when it exceeds the maximum
 # relative movement of both geoms away from that midpoint. Uncertain intervals
 # subdivide to <=1mm bound; gaps and literal endpoint contacts remain unchanged.
 stack=[(0.,1.)]
 while stack:
  lo,hi=stack.pop();alpha=(lo+hi)/2;result=sample(alpha,midhands)
  if isinstance(result,dict):return result
  half=bound*(hi-lo)*500
  if result>=half:
   certified+=1;max_certificate_bound=max(max_certificate_bound,half);continue
  if bound*(hi-lo)<=.001:
   return dict(pass_=False,reason='Samples clear; insufficient separation reserve for continuous certificate',states_checked=checked,min_reserve_mm=min_reserve,uncertified_interval=[lo,hi],required_midpoint_reserve_mm=half)
  if checked>=max_states:return dict(pass_=False,reason='Edge exceeds bounded24000state allocation',states_checked=checked,displacement_bound_m=bound)
  stack.extend(((alpha,hi),(lo,alpha)))
 return dict(pass_=True,reason='adaptive midpoint clearance certificate, uncertain intervals refined to1mm displacement bound',states_checked=checked,min_reserve_mm=min_reserve,certified_intervals=certified,max_half_interval_bound_mm=max_certificate_bound,carriage_delta_m={side:float(dq[ch.qa[side+'_carriage_x']]) for side in s.model.SIDES},q_start=a.tolist(),q_end=b.tolist())

def signature(hands):
 return {side:(h['held'],h['product'] if h['held'] in ('root_food','food_cup','cut_cassette','colander','carried_bowl') else '',h.get('food_state'),h.get('object_rotation_deg'),h.get('food_tool_roll_deg'),h.get('food_center_local_m')) for side,h in hands.items()}
def transit(ch,a,b,hands):
 none=plain_contacts(hands);direct=edge(ch,a,b,none,none)
 if direct['pass_']:return dict(pass_=True,method='direct joint/carriage segment',edges=[direct])
 # Collision-aware alternative: folded waypoint at the active carriage centres.
 # All held geometry remains attached; no disappearance to reach the waypoint.
 waypoint=np.array(s.PARK)
 for n in s.ck.BASE+s.ck.JAWS:waypoint[ch.qa[n]]=a[ch.qa[n]]
 bad,_,_=state(ch,waypoint,none)
 if bad:return dict(pass_=False,method='direct plus folded-waypoint search',edges=[direct],waypoint_blockers=bad[:8])
 first=edge(ch,a,waypoint,none,none)
 if not first['pass_']:return dict(pass_=False,method='direct plus folded-waypoint search',edges=[direct,first])
 last=edge(ch,waypoint,b,none,none)
 return dict(pass_=last['pass_'],method='direct plus folded-waypoint search',edges=[direct,first,last])

def empty_cell():
 ph=copy.deepcopy(s.P['phases'][0]);sg=copy.deepcopy(ph['segments'][0]);sg['station']='parking';sg['poses']=sg['poses'][:1]
 ch=s.Checker(ph,sg);root=E.fromstring(ch.xml);w=root.find('worldbody')
 for prod,x,y in [('carrot',-1.685,.095),('potato',-1.535,.095),('leafy_greens',-1.685,.245),('tomato',-1.535,.245)]:
  size=next(a['input_size_m'] for a in s.P['finished_products'] if a['product']==prod)
  s.model.box(w,'staged_raw_'+prod,[x,y,.942+size[2]/2],size,robot=False)
 ch.xml=E.tostring(root,encoding='unicode');ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.set_contacts(sg['poses'][0]);return ch,sg['poses'][0]

def passing():
 ch,hands=empty_cell();rng=np.random.default_rng(831);candidate_records=[];best=None;verified_routes=[];tried=0
 rlo,rhi=-1.7,.045;llo,lhi=-1.7,.2
 cross_alpha=(lhi-rlo)/((rhi-rlo)+(lhi-llo));cross_x=rlo+(rhi-rlo)*cross_alpha
 # At the crossing, include every fixture, parked tool, bowl and raw input.
 for k in range(4000):
  if k>=96 and verified_routes:break
  tried=k+1
  q=np.array(s.PARK) if k==0 else ch.m.qpos0.copy()
  for side in s.model.SIDES:
   q[ch.qa[side+'_carriage_x']]=cross_x
   if k:
    for n in s.ck.ARMS[side]:q[ch.qa[n]]=rng.uniform(*ch.m.jnt_range[ch.jid[n]])
   for label in ('minus','plus'):q[ch.qa[side+'_jaw_'+label]]=.01
  hits,reserve,mins=state(ch,q,hands)
  if hits:continue
  # First reject quickly at full route samples, then certify both moving lanes.
  fail=None
  for alpha in np.linspace(0,1,21):
   cand=q.copy();cand[ch.qa['R_carriage_x']]=rlo+(rhi-rlo)*alpha;cand[ch.qa['L_carriage_x']]=lhi+(llo-lhi)*alpha
   hs,rv,mn=state(ch,cand,hands)
   if hs:fail=dict(alpha=float(alpha),first_blockers=hs[:5]);break
  candidate_records.append(dict(k=k,crossing_clear=True,route_screen_pass=fail is None,blocker=fail))
  if best is None:best=dict(q=q.tolist(),k=k,screen=fail)
  if fail:continue
  a=q.copy();b=q.copy();a[ch.qa['R_carriage_x']]=rlo;a[ch.qa['L_carriage_x']]=lhi;b[ch.qa['R_carriage_x']]=rhi;b[ch.qa['L_carriage_x']]=llo
  path=edge(ch,a,b,hands,hands)
  if path['pass_']:
   verified_routes.append(dict(k=k,path=path,q_crossing=q.tolist()))
 if verified_routes:
  chosen=verified_routes[0]
  out=dict(pass_=True,starts_tried=tried,clear_crossing_candidates=len(candidate_records),verified_routes=len(verified_routes),path=chosen['path'],q_crossing=chosen['q_crossing'],xml='models/passing.xml',screen_records=candidate_records,route_witnesses=verified_routes,operating_carriage_range_m={'R':[rlo,rhi],'L':[llo,lhi]},mechanical_carriage_range_m=[-1.7,.2])
  (H/'models/passing.xml').write_text(ch.xml,encoding='utf-8');f.write('passing.json',out);return out
 if best is None:best=dict(q=s.PARK,k=None,screen={'reason':'No full-cell crossing candidate found'})
 out=dict(pass_=False,starts_tried=4000,clear_crossing_candidates=len(candidate_records),q_crossing=best['q'],first_blocker=best['screen'],xml='models/passing.xml',screen_records=candidate_records,operating_carriage_range_m={'R':[rlo,rhi],'L':[llo,lhi]},mechanical_carriage_range_m=[-1.7,.2])
 (H/'models/passing.xml').write_text(ch.xml,encoding='utf-8');f.write('passing.json',out);return out

def main():
 best=json.loads((O/'best.json').read_text());intra=[];connections=[];previous=None
 for ph in s.P['phases']:
  for sg in ph['segments']:
   key=ph['id']+'__'+sg['label'].replace(' ','_');w=best['witnesses'].get(key);ch=s.Checker(ph,sg)
   if w is None:
    intra.append(dict(stroke=key,pass_=False,reason='No independently verified static stroke witness'))
    if previous:connections.append(dict(from_stroke=previous[0],to_stroke=key,pass_=False,reason='Required next stroke has no verified endpoint'))
    previous=(key,None,None,None);continue
   edges=[]
   for i in range(len(w['poses'])-1):edges.append(edge(ch,w['poses'][i]['q'],w['poses'][i+1]['q'],sg['poses'][i],sg['poses'][i+1]))
   intra.append(dict(stroke=key,pass_=all(x['pass_'] for x in edges),edges=edges,action=sg['action']))
   if previous:
    pk,pw,ps,pch=previous
    if pw is None:connections.append(dict(from_stroke=pk,to_stroke=key,pass_=False,reason='Required predecessor has no verified endpoint'))
    elif signature(ps['poses'][-1])!=signature(sg['poses'][0]) or ps.get('action') in ('place','helper_index') or sg.get('action') in ('pick','helper_index'):
     connections.append(dict(from_stroke=pk,to_stroke=key,pass_=False,reason='Object ownership, grasp/release, support/clamp or food-state transition requires an explicit continuous handoff; none is certified',predecessor_holding=signature(ps['poses'][-1]),successor_holding=signature(sg['poses'][0])))
    else:
     path=transit(ch,np.array(pw['poses'][-1]['q']),np.array(w['poses'][0]['q']),sg['poses'][0])
     # Both scene states must permit the transit; snapshot changes cannot hide
     # the prior clamp, lid or parked fixture state.
     if path['pass_']:
      dual=edge(pch,pw['poses'][-1]['q'],w['poses'][0]['q'],plain_contacts(ps['poses'][-1]),plain_contacts(ps['poses'][-1]));path['prior_scene_edge']=dual;path['pass_']=dual['pass_']
     connections.append(dict(from_stroke=pk,to_stroke=key,**path))
   previous=(key,w,sg,ch)
  print(ph['id'],'motion checked',flush=True)
 pass_result=passing();parkch,hands=empty_cell();parkq=np.array(pass_result['q_crossing']);parkq[parkch.qa['R_carriage_x']]=-1.7;parkq[parkch.qa['L_carriage_x']]=.2
 hs,rv,mins=state(parkch,parkq,hands);parking=dict(pass_=not hs,q=parkq.tolist(),first_blockers=hs[:8],min_clearance=mins)
 # Connect the final verified empty-hand phase to parking when available.
 final_empty=best['witnesses'].get('Q27__water_off_final');park_edges=[]
 if final_empty:
  park_edges.append(edge(parkch,final_empty['poses'][-1]['q'],parkq,hands,hands))
 initial=best['witnesses'].get('Q01__water_on')
 if initial:park_edges.append(edge(parkch,parkq,initial['poses'][0]['q'],hands,hands))
 semantic=[
  'The six root-wash rolls are declared recipe loops, not expanded collision-checked roll/regrasp states.',
  'Raw greens/tomato cup acquisition and cup-to-cutting-nest transfer have no connected witnesses.',
  'Bowl acquisition, slicer-to-rinse-vessel transfer, contents collection, and final bowl ownership are incomplete.',
  'OEM lever/pusher actuation, pusher clearance and detached cutting/restart states lack an executable guarded sequence.',
  'Each helper release/reclamp and peel-stop actuator transition needs a persistent food/body state and path.',
  'All vision-dependent eyes, basal creases, wide stalks and repeated cut/feed cycles must be expanded for this reference meal.',
  'Cleaning includes a planning allowance for disassembly, blade underside, channels and draining; these manipulation strokes are not all present.',
  'Lid closed-to-open swept path and full cable-chain motion are not certified by alternate snapshot positions/full envelopes alone.'
 ]
 out=dict(schema='r03.connected.reference_meal.audit',pass_=False,motion='fail',config=s.model.CONFIG,meal_order=[p['id'] for p in s.P['phases']],strokes=intra,between_strokes=connections,passing=pass_result,parking=parking,park_connections=park_edges,
  collision_states_checked=calls,elapsed_s=time.monotonic()-began,stroke_paths_passed=sum(x['pass_'] for x in intra),stroke_paths_total=len(intra),connections_passed=sum(x['pass_'] for x in connections),connections_total=len(connections),semantic_blockers=semantic,
  contact_policy='Working-face contacts only when common to both endpoint states; own pickup/return support contacts only at exact grasp/release endpoints. All positive-time departures/arrivals retain5mm/10mm gaps. No blanket fixture or collision exemption.',
  path_check='Joint and carriage interpolation with adaptive midpoint clearance certificates from a conservative relative geometry-displacement bound; uncertain intervals subdivide to<=1mm and then fail unless certified. Equivalent2pi representations stay within public joint ranges. Failed compatible transitions also try a folded waypoint without removing held bodies.',
  limits='Failure describes this candidate and these bounded searches, not a proof that no redesign/path exists. Static witnesses do not certify an autonomous meal; topology/ownership changes and repeated food operations cannot be skipped.')
 f.write('motion.json',out);best['motion_status']='fail';best['overall_pass']=False;best['passing_pass']=pass_result['pass_'];f.write('best.json',best)
 print('motion FAIL','states',calls,'passing',pass_result['pass_'],'elapsed',round(out['elapsed_s'],2),flush=True)
def refresh_passing():
 old=json.loads((O/'motion.json').read_text())
 if not (O/'motion_pre_passing_limit.json').exists():f.write('motion_pre_passing_limit.json',old)
 if not (O/'passing_pre_operational_limit.json').exists():f.write('passing_pre_operational_limit.json',old['passing'])
 pr=passing();ch,hands=empty_cell();q=np.array(pr['q_crossing']);q[ch.qa['R_carriage_x']]=-1.7;q[ch.qa['L_carriage_x']]=.2
 hits,rv,mins=state(ch,q,hands);old['passing']=pr;old['parking']=dict(pass_=not hits,q=q.tolist(),first_blockers=hits[:8],min_clearance=mins)
 best=json.loads((O/'best.json').read_text());edges=[]
 last=best['witnesses'].get('Q27__water_off_final');first=best['witnesses'].get('Q01__water_on')
 if last:edges.append(edge(ch,last['poses'][-1]['q'],q,hands,hands))
 if first:edges.append(edge(ch,q,first['poses'][0]['q'],hands,hands))
 old['park_connections']=edges;old['collision_states_checked']+=calls;old['passing_limit_iteration']=dict(additional_states_checked=calls,elapsed_s=time.monotonic()-began,reason='R adapter intersects slicer casing above task travel. Use existing main solver limitx<=0.045 for operational passing; retain unchanged full rail, model limits, arm and environment geometry. Prior complete motion/4000start failed travel search archived; all105stroke path results unchanged.')
 f.write('motion.json',old);best['passing_pass']=pr['pass_'];f.write('best.json',best)
 print('passing operating-range',pr['pass_'],'starts',pr['starts_tried'],'states',calls,'elapsed',time.monotonic()-began,flush=True)
if __name__=='__main__':refresh_passing() if '--passing-only' in sys.argv else main()
