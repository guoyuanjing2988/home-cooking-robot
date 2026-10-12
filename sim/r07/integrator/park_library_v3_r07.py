"""Stage independently clear folded arm shapes, then check the complete pair.
This is only a proposal generator. No opposite arm is excluded in admission.
"""
import json,time
import numpy as np,mujoco
from search_distance_v2_r07 import hits as proposal_hits
def seed(ch,c,q,b):
 import runtime_v2_r07 as v
 start=time.monotonic();pools={};audit=[]
 for si,side in enumerate(('R','L')):
  other='L' if side=='R' else 'R';angle=c['mount_deg' if si==0 else 'helper_mount_deg'];sources=[]
  for label in ('L28','L25','L21','L19','L18','L13','L29','L30'):
   file=v.O/'layouts'/f'{label}_park_full.json'
   if not file.exists():continue
   d=json.loads(file.read_text());sc=d['config']
   if sc['arms'][si]==c['arms'][si] and abs(sc['mount_deg' if si==0 else 'helper_mount_deg']-angle)<1e-8:sources.append((label,np.array(d['q'])))
  ids=[g for g,n in enumerate(ch.gnames) if ch.robot[g] and n.startswith(side+'_')];names=v.s.ck.ARMS[side]+[side+'_carriage_x'];ix=[ch.qa[n] for n in names];pool=[];seen=set()
  for label,src in sources:
   for x in sorted(set([float(src[ch.qa[side+'_carriage_x']])]+list(np.linspace(-1.50,.44,25)))):
    trial=q.copy();trial[ix]=src[ix];trial[ch.qa[side+'_carriage_x']]=x
    key=tuple(np.round(trial[ix],5))
    if key in seen:continue
    seen.add(key);hs=proposal_hits(ch,trial)
    relevant=[h for h in hs if any(n.startswith(side+'_') for n in h['pair']) and not any(n.startswith(other+'_') for n in h['pair'])]
    if relevant:continue
    band=True
    for g in ids:
     low=np.array([b.support(g,-a)[i] for i,a in enumerate(np.eye(3))]);high=np.array([b.support(g,a)[i] for i,a in enumerate(np.eye(3))])
     if low[0]<-1.789 or high[0]>.679 or low[1]<.241 or high[1]>.589 or low[2]<.861 or high[2]>1.34:band=False;break
    if band:pool.append(dict(source=label,q=trial,carriage_x_m=x))
  pools[side]=pool;audit.append(dict(side=side,source_shapes=[p[0] for p in sources],proposals=len(seen),independent_clear=len(pool)))
  print('PARK_LIBRARY',v.ID,side,audit[-1],flush=True)
 found=None;combinations=0
 for a in pools['R']:
  if found:break
  for bb in pools['L']:
   if combinations>=2500 or time.monotonic()-start>100:break
   combinations+=1;trial=a['q'].copy();names=v.s.ck.ARMS['L']+['L_carriage_x'];ix=[ch.qa[n] for n in names];trial[ix]=bb['q'][ix]
   if proposal_hits(ch,trial):continue
   hs,_,_=v.f.contacts(ch,trial)
   if not hs:found=dict(q=trial,sources=[a['source'],bb['source']],carriages=[a['carriage_x_m'],bb['carriage_x_m']]);break
 out=dict(layout=v.ID,rows=audit,combinations=combinations,found=found is not None,elapsed_s=time.monotonic()-start,scope='Independent folded-shape screening is only a proposal. Each combined winner passes full unfiltered geometry before park band/load/fold admission.')
 if found:out.update(q=found['q'].tolist(),sources=found['sources'],carriages=found['carriages'])
 (v.H/'audit'/f'{v.ID}_park_library.json').write_text(json.dumps(out,indent=2));return found['q'] if found else q
