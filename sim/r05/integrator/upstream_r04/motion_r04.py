"""Real bounded RRT-Connect tests; template paths and conserved meal differ."""
import json,copy,sys,time
import numpy as np
import final_check as f
from planner import Planner
s=f.s;H=s.HERE;O=H/'results';static=json.loads((O/'static_all.json').read_text());ws=static['witnesses'];rows=static['rows']
lo=int(sys.argv[1]);hi=int(sys.argv[2]);beg=time.monotonic();internal=[];connections=[]
items=[(ph,sg,ph['id']+'__'+sg['label'].replace(' ','_')) for ph in s.P['phases'] for sg in ph['segments']]
def sig(hands):
 return {side:tuple(json.dumps(h.get(n),sort_keys=True) for n in ['held','product','food_state','object_rotation_deg','food_tool_roll_deg','food_center_local_m']) for side,h in hands.items()}
def shortq(ch,a,b):
 b=np.array(b).copy()
 for n in s.ck.JOINTS:
  j=ch.qa[n];l,u=ch.m.jnt_range[ch.jid[n]];choices=[b[j]+k*2*np.pi for k in range(-2,3) if l<=b[j]+k*2*np.pi<=u]
  b[j]=min(choices,key=lambda v:abs(v-a[j]))
 return b
for i in range(lo,min(hi,len(items))):
 ph,sg,key=items[i];w=ws.get(key);entry=dict(stroke=key,index=i,static_verified=bool(w),edges=[])
 if not w:entry.update(ok=False,reason='No independently verified endpoint')
 else:
  ch=s.Checker(ph,sg)
  for j in range(len(w['poses'])-1):
   a=np.array(w['poses'][j]['q']);b=shortq(ch,a,w['poses'][j+1]['q']);pl=Planner(ch,sg['poses'][j],seed=4400+i*7+j,seconds=10)
   result=pl.plan(a,b,sg['poses'][j],sg['poses'][j+1],max_nodes=100);entry['edges'].append(result)
  entry['ok']=all(e['ok'] for e in entry['edges']);entry['scope']='Full template geometry; joint+carriage clearance only. RRT detours are not a Cartesian processing/coverage or transient-wrench certificate.'
 internal.append(entry)
 if i+1<len(items):
  ph2,sg2,key2=items[i+1];w2=ws.get(key2);c=dict(index=i,from_stroke=key,to_stroke=key2,meal_verified=False)
  if not(w and w2):c.update(ok=False,reason='Unverified endpoint')
  elif sig(sg['poses'][-1])!=sig(sg2['poses'][0]):c.update(ok=False,reason='Ownership/attachment changes: explicit jaw, support, clamp or container transfer events required; instantaneous object substitution rejected')
  elif sg['station']!=sg2['station'] and (sg['station'] in ['peel','secondary'] or sg2['station'] in ['peel','secondary']):c.update(ok=False,reason='Conserved scene has unverified clamp/lid/fixture event; separate template cannot certify it')
  else:
   ch=s.Checker(ph,sg);hands={side:dict(h,contacts=[]) for side,h in sg['poses'][-1].items()};a=np.array(w['poses'][-1]['q']);b=shortq(ch,a,w2['poses'][0]['q']);pl=Planner(ch,hands,seed=5400+i,seconds=8);result=pl.plan(a,b,hands,hands,max_nodes=100)
   c.update(ok=result['ok'],template_geometry_diagnostic=result,reason='Template geometry diagnostic only: complete persistent scene and intervening discrete events remain unverified')
  connections.append(c)
 print(i,key,'internal',entry['ok'],'connection',connections[-1]['ok'] if connections and connections[-1]['index']==i else '-',round(time.monotonic()-beg,1),flush=True)
 (O/f'motion_chunk_{lo}_{hi}.json').write_text(json.dumps(dict(internal=internal,connections=connections,elapsed_s=time.monotonic()-beg),indent=2))
print('motion chunk complete',lo,hi,flush=True)
