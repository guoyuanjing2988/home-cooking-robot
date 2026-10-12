"""Explicit stationary jaw travel probes at registered template endpoints.

These use real slide joints and full finger/object geometry. They are isolated
geometry evidence, not a substitute for the conserved-scene approach/departure.
"""
import json,copy,time,math,sys
import numpy as np,mujoco
import final_check as f,motion_r05 as mo
from planner_r05 import Planner
from point_bound import PointBound
H=f.s.HERE;O=H/'results';seq=json.loads((O/'state_sequence.json').read_text());ws=json.loads((O/'static_all.json').read_text())['witnesses'];cache={};rows=[];counts={};t0=time.monotonic()
lo,hi=map(int,sys.argv[1:3])
events=[e for e in seq['events'] if e.get('stage') in ('jaw_close','jaw_open')]
for event_index,e in enumerate(events):
 tag=(e['phase'],e['stage']);ordinal=counts.get(tag,0);counts[tag]=ordinal+1
 if not lo<=event_index<hi:continue
 after=e['state_after'];before=e['state_before'];side=next((x for x in ('R','L') if after['arms'][x]['held']!=before['arms'][x]['held']),None)
 if side is None:rows.append(dict(event=e['id'],pass_=False,reason='No single arm ownership change identifies a grasp'));continue
 obj=after['arms'][side]['held'] if e['stage']=='jaw_close' else before['arms'][side]['held'];held='root_food' if obj.startswith('food:') else after['objects'].get(obj,before['objects'].get(obj,{})).get('kind');candidates=[(i,ph,sg,key) for i,(ph,sg,key) in enumerate(mo.items) if ph['id']==e['phase'] and any(h.get(side,{}).get('held')==held for h in sg['poses'])]
 if held=='root_food' and e['phase'].startswith('Q05'):
  candidates=[x for x in candidates if x[2]['action']=='helper_index'];candidates=candidates[ordinal:ordinal+1]
 if not candidates:rows.append(dict(event=e['id'],pass_=False,reason='No corresponding full geometry endpoint for '+str(obj)));continue
 # Prefer the explicitly matching pick/place rather than an unrelated work pose.
 desired='pick' if e['stage']=='jaw_close' else 'place';candidates.sort(key=lambda x:x[2]['action']!=desired);i,ph,sg,key=candidates[0];pi=0 if e['stage']=='jaw_close' else len(sg['poses'])-1;h=sg['poses'][pi]
 if side not in h:rows.append(dict(event=e['id'],pass_=False,reason='Arm absent at selected endpoint'));continue
 token=(key,pi,side,e['stage'])
 if token not in cache:
  ch=mo.scene(ph,sg,i);q=np.array(ws[key]['poses'][pi]['q']);ch.contact_windows=mo.windows(ch,q,h);closed=q.copy();opened=q.copy();jids=[ch.qa[side+'_jaw_'+x] for x in ('minus','plus')]
  opening=h[side]['jaw_opening_m']+.020
  for label,j in zip(('minus','plus'),jids):opened[j]=min(opening/2,ch.m.jnt_range[ch.jid[side+'_jaw_'+label],1])
  a,b=(opened,closed) if e['stage']=='jaw_close' else (closed,opened);pb=PointBound(ch);n=max(1,int(math.ceil(pb.bound(b-a)/.004)));pl=Planner(ch,h,seed=90500+event_index);path=[];bad=None
  for alpha in np.linspace(0,1,n+1):
   candidate=a+(b-a)*alpha;path.append(candidate.tolist())
   if not pl.state(candidate,h):bad=pl.last;break
  cache[token]=dict(template=key,side=side,endpoint_pose=pi,pass_=bad is None,states_checked=pl.states,path=path,blocker=bad,max_point_step_mm=pb.bound(b-a)/n*1000,closed_jaw_m=h[side]['jaw_opening_m'],open_jaw_m=opening,own_support_faces=[c['face'] for c in h[side].get('contacts',[])],scene='Full template + staged raw inputs and delivered contents; not yet the globally conserved meal scene',object_transform='Object/tool is stationary during jaw slide; transfer world pose must be retained by the persistent body after ownership update',force_scope='Jaw geometric travel only. 150N/15Nm capacity and friction gates are not inferred from this animation.')
  print(e['id'],key,e['stage'],cache[token]['pass_'],'states',pl.states,flush=True)
 rows.append(dict(event=e['id'],phase=e['phase'],stage=e['stage'],object=obj,probe=copy.deepcopy(cache[token]),persistent_event_verified=False))
 (O/f'jaw_events_{lo}_{hi}.json').write_text(json.dumps(dict(rows=rows,unique_probes=len(cache),elapsed_s=time.monotonic()-t0),indent=2))
print('JAW_GEOMETRY_PROBES',len(rows),sum(r.get('probe',{}).get('pass_',False) for r in rows),len(cache),round(time.monotonic()-t0,1),flush=True)
