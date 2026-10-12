"""Re-verify a connection path found for one preset against another preset's model
(different fingers, same endpoints) and save it as that preset's connection if every
edge passes the planner's own edge() replay (<= 4 mm steps, full checker).
Usage: python transplant.py <src preset> <dst preset> <k>"""
import sys,time,json,numpy as np,chain
from planner import edge
from scene import jaw_q,save,load
S,Dp,k=sys.argv[1],sys.argv[2],int(sys.argv[3])
src=load(f'results/chain_{S}/C{k}.json');path=np.array(src['path'])
held={1:'carrot',2:'carrot',3:'carrot'}[k] if not chain.config(Dp).get('r11_tomato') else {1:'tomato',2:'tomato',3:None}[k]
extra=chain.tstate(Dp,'pusher_grasp') if held is None else {}
ch,_=chain.checker(Dp,held,**extra);ch.active=ch.arm_ids;M=chain.MASS[held]
qj=jaw_q(chain.chain_cfg(Dp),held) if held else .025;path[:,-2:]=qj
# endpoints must equal the destination's group ends
names=['GT1','GT2','GT3','GT4'] if chain.config(Dp).get('r11_tomato') else ['G1','G2','G3','G4S']
A=load(f'results/chain_{Dp}/{names[k-1]}.json');B=load(f'results/chain_{Dp}/{names[k]}.json')
qa=np.array([s for s in A['segments'] if s.get('path')][-1]['path'][-1]);qb=np.array(B['segments'][0]['path'][0])
print('end gaps',float(np.max(abs(path[0]-qa))),float(np.max(abs(path[-1]-qb))))
# bridge: if the source path's ends differ from the destination's group ends, join them by
# direct edges (also replayed below); jaw columns follow the destination's held state
if np.max(abs(path[0]-qa))>1e-9:path=np.r_[[qa],path]
if np.max(abs(path[-1]-qb))>1e-9:path=np.r_[path,[qb]]
out=[path[0].tolist()];t=time.monotonic()
for i in range(len(path)-1):
 e=edge(ch,path[i],path[i+1],time.monotonic()+60,mass=M)
 if not e['ok']:print('edge',i,'rejected',str(e.get('rejection') or e.get('reason'))[:300]);sys.exit(1)
 out+=e['path'][1:]
import os
save(f'results/chain_{Dp}/C{k}'+os.environ.get('OUT_SUFFIX','')+'.json',dict(k=k,held=held,ok=True,strategy=f'transplanted from {S} C{k} (bridged to this preset ends where they differ), every edge re-replayed with the {Dp} model',path=out,elapsed_s=time.monotonic()-t))
print(Dp,'C',k,'ok transplanted',len(out),'states',round(time.monotonic()-t),'s')
