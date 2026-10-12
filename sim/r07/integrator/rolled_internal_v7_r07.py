"""Check every distinct repeated wash roll; isolated diagnostics, never meal credit."""
import os,sys,json,time,copy,hashlib
os.environ['R07_LAYOUT']=sys.argv[1]
import numpy as np
import persistent_v7_r07 as p
from motion_v7_r07 import mo,continuation_ik,replay
v=p.v;H=v.H;O=v.O;ID=v.ID;began=time.monotonic();lane=int(sys.argv[2]);stride=int(sys.argv[3]);out=O/'rolled_internal_v7'/ID;out.mkdir(parents=True,exist_ok=True)
assert (O/f'frozen_v7_{ID}.json').exists()
variants=[r for r in p.expanded() if r['roll_deg']]
for ordinal,r in enumerate(variants):
 if ordinal%stride!=lane:continue
 file=out/f'{ordinal}.json'
 if file.exists():continue
 if time.monotonic()-began>700:break
 index=r['index'];source=O/'static_v7'/ID/f'{index}.json';saved=json.loads(source.read_text());original=saved.get('witness') or saved['best_failed']['raw'];sg=copy.deepcopy(v.items[index][1]);ch=v.scene(index)
 for hands in sg['poses']:
  for h in hands.values():h['roll_deg']+=r['roll_deg']
 ch.seg=sg;ch.witness_k=original['k'];ch.refine_support_endpoints=True;ch.working_stroke=sg['action']=='process';poses=[];proposals=[]
 for j,hands in enumerate(sg['poses']):
  base=np.array(original['poses'][min(j,len(original['poses'])-1)]['q']);ch.hands=hands;ch.set_contacts(hands)
  targets={side:(np.array(h['pos']),ch.target_rotation(h,original['k'])) for side,h in hands.items()}
  q,exact=continuation_ik(ch,base,targets);poses.append(dict(q=q.tolist()));proposals.append(dict(pose=j,exact_ik=bool(exact)))
 witness=dict(k=original['k'],poses=poses);reference=v.f.replay(ch,witness);edges=[];v.s.PARK=np.array(poses[0]['q'])
 for j in range(len(poses)-1):
  a=np.array(edges[-1]['path'][-1]) if edges and edges[-1]['ok'] else np.array(poses[j]['q']);b=mo.shortq(ch,a,poses[j+1]['q']);ch.refine_start_allowed=j==0
  edge=mo.plan_section(ch,a,b,sg['poses'][j],sg['poses'][j+1],987000+ordinal*10+j,process=sg['action']=='process');edges.append(edge);print('ROLLED_EDGE',ordinal,j,edge['ok'],flush=True)
 final=replay(ch,sg,witness,edges);model=H/'models'/f'{ID}_rolled_{ordinal}.xml';model.write_text(ch.xml)
 row=dict(layout=ID,ordinal=ordinal,expanded_stroke=r,ok=bool(reference['ok'] and final['pass_']),source_static_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),model_xml=str(model.relative_to(H)),model_sha256=hashlib.sha256(ch.xml.encode()).hexdigest(),endpoint_witness=witness,endpoint_reference=reference,proposals=proposals,edges=edges,final_replay=final,meal_state_verified=False,scope='Distinct rolled internal geometry and working targets; isolated scene only. Base96-start result is not relabelled as a96-start rolled static search. No continuous meal or appliance-interface execution credit.')
 file.write_text(json.dumps(row,indent=None,allow_nan=False));print('ROLLED_INTERNAL',ordinal,r['id'],row['ok'],flush=True)
 # One variant per foreground chunk keeps three full65s edge searches plus
 # any independent replay comfortably inside the external1120s timeout.
 break
print('ROLLED_CHUNK',lane,round(time.monotonic()-began,2),flush=True)
