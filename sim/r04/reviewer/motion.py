"""Fresh connection/section replay. Read-only submitted models and witnesses."""
from reverify import *
from planner import Planner
def sig(hands):
 return {side:tuple(json.dumps(h.get(n),sort_keys=True) for n in ['held','product','food_state','object_rotation_deg','food_tool_roll_deg','food_center_local_m']) for side,h in hands.items()}
def shortq(ch,a,b):
 b=np.array(b).copy()
 for n in s.ck.JOINTS:
  j=ch.qa[n];lo,hi=ch.m.jnt_range[ch.jid[n]];choices=[b[j]+k*2*np.pi for k in range(-2,3) if lo<=b[j]+k*2*np.pi<=hi]
  b[j]=min(choices,key=lambda v:abs(v-a[j]))
 return b

def main():
 began=time.monotonic(); sub=json.loads((I/'results/motion.json').read_text()); ws=json.loads((I/'results/static_all.json').read_text())['witnesses']
 items=[(ph,sg,ph['id']+'__'+sg['label'].replace(' ','_')) for ph in s.P['phases'] for sg in ph['segments']]
 selected=[]
 for i,(ph,sg,key) in enumerate(items[:-1]):
  ph2,sg2,key2=items[i+1]
  if sig(sg['poses'][-1])==sig(sg2['poses'][0]):selected.append(i)
 # At least 10 actual geometric replays, distributed across recipe sections.
 chosen=selected[:6]+selected[-6:]
 chosen=list(dict.fromkeys(chosen))
 if len(chosen)<12:chosen=list(dict.fromkeys(chosen+selected))[:12]
 connections=[]; state_count=0
 for i in chosen:
  ph,sg,key=items[i];ph2,sg2,key2=items[i+1];ch=s.Checker(ph,sg);ch2=s.Checker(ph2,sg2)
  a=np.array(ws[key]['poses'][-1]['q']);b=shortq(ch,a,ws[key2]['poses'][0]['q'])
  ha={k:dict(h,contacts=[]) for k,h in sg['poses'][-1].items()}; hb={k:dict(h,contacts=[]) for k,h in sg2['poses'][0].items()}
  samples=[]
  for alpha in [0.,.25,.5,.75,1.]:
   q=a+(b-a)*alpha
   ch.set_contacts(ha);h1,m1,p1=f.contacts(ch,q)
   ch2.set_contacts(hb);h2,m2,p2=f.contacts(ch2,q)
   state_count+=2
   samples.append(dict(alpha=alpha,prior_scene_hits=h1[:8],next_scene_hits=h2[:8],prior_reserve_mm=min(v['reserve_mm'] for v in m1.values()),next_reserve_mm=min(v['reserve_mm'] for v in m2.values())))
  clear=all(not x['prior_scene_hits'] and not x['next_scene_hits'] for x in samples)
  cert=None
  if clear:
   pl=Planner(ch,ha,seed=8400+i,seconds=6);cert=pl.edge(a,b,ha,ha,deadline=time.monotonic()+6);state_count+=pl.calls
  connections.append(dict(index=i,from_stroke=key,to_stroke=key2,samples=samples,sampled_clear=clear,direct_certificate=cert,conserved_meal_pass=False,reason='Both original template scenes rechecked. Persistent attachments, clamp/lid/jaw event trajectories are unverified. A failed sample is a path witness, not a global infeasibility proof.'))
  print('connection',i,key,'->',key2,'clear',clear,flush=True)
 sections=[]
 keys=['Q05.carrot__peel_index_0','Q05.carrot__helper_index_0','Q04.carrot__pick_peeler','Q16__soak_bok_choy','Q21__Wash_unpeeled_tomato','Q22__acquire_eye_core_spoon','Q10.potato__withdraw']
 for key in keys:
  ph,sg,_=next(x for x in items if x[2]==key);ch=s.Checker(ph,sg);w=ws[key];edges=[]
  for j in range(len(w['poses'])-1):
   pl=Planner(ch,sg['poses'][j],seed=9400+j,seconds=6);a=np.array(w['poses'][j]['q']);b=shortq(ch,a,w['poses'][j+1]['q'])
   edges.append(pl.edge(a,b,sg['poses'][j],sg['poses'][j+1],deadline=time.monotonic()+6));state_count+=pl.calls
  sections.append(dict(stroke=key,pass_=all(e['ok'] for e in edges),edges=edges))
  print('section',key,sections[-1]['pass_'],flush=True)
 # Independently enumerate every semantic link; a topology change cannot be
 # validated by replacing the held object or loading another snapshot.
 ledger=[]
 for i,(ph,sg,key) in enumerate(items[:-1]):
  ph2,sg2,key2=items[i+1];c=sub['connections'][i]
  ledger.append(dict(index=i,from_stroke=key,to_stroke=key2,attachment_signature_changes=sig(sg['poses'][-1])!=sig(sg2['poses'][0]),submitted_template_ok=c['ok'],meal_verified=c['meal_verified'],reason=c.get('reason')))
 out=dict(method='Fresh models, no new IK search or invented support window. Twelve inter-stroke connection sections sampled in BOTH prior and next full template geometry; direct edges continuously checked if samples clear.',connections_replayed=len(connections),connections_passed=0,connections_total=len(ledger),states_checked=state_count,sections=sections,connections=connections,all_connection_ledger=ledger,submitted_internal_paths_passed=sum(x['ok'] for x in sub['internal_paths']),submitted_internal_paths_total=len(sub['internal_paths']),elapsed_s=time.monotonic()-began)
 dump('motion_independent.json',out)
 print('motion complete',state_count,len(connections),flush=True)
if __name__=='__main__':main()
