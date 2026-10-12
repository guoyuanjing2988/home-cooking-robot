"""Faucet-enabled reachability maps; same216-target grid compared separately."""
import sys,json,csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
H=Path(__file__).resolve().parent;O=H/'results';ID=sys.argv[1];layouts=[];flat=[]
for d in sorted((O/'reachability').iterdir()):
 if not d.is_dir() or int(d.name[1:])<20 or not all((d/(s+'.json')).exists() for s in ('R','L')):continue
 data={s:json.loads((d/(s+'.json')).read_text()) for s in ('R','L')}
 if not all(len(x['rows'])==252 for x in data.values()):continue
 layouts.append((d.name,data))
 for side,x in data.items():
  for i,r in enumerate(x['rows']):
   dex=(r.get('witness') or {}).get('dexterity',{})
   flat.append(dict(layout=d.name,arm=side,target=i,x_m=r['pos'][0],y_m=r['pos'][1],z_m=r['pos'][2],orientation=r['orientation'],grid='common216' if i<216 else 'faucet_relative36',kinematic_solutions=r['kinematic_solutions'],starts=r['starts'],clearance_pass=r['pass_'],min_singular_value=dex.get('min_singular_value'),condition_number=dex.get('condition_number'),source=f'results/reachability/{d.name}/{side}.json'))
with (O/'reachability_map_v3.csv').open('w',newline='',encoding='utf-8') as file:w=csv.DictWriter(file,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
fig,axes=plt.subplots(2,2,figsize=(15,9),dpi=100);x=np.arange(len(layouts))
for side,dx,color in [('R',-.18,'#287da5'),('L',.18,'#ce7537')]:
 count=[sum(r['pass_'] for r in data[side]['rows'][:216]) for _,data in layouts]
 axes[0,0].bar(x+dx,count,.34,label=side,color=color)
 for xx,n in zip(x+dx,count):axes[0,0].text(xx,n+2,str(n),ha='center',fontsize=8)
 med=[]
 for _,data in layouts:
  a=[r['witness']['dexterity']['min_singular_value'] for r in data[side]['rows'][:216] if r['pass_']];med.append(np.median(a) if a else np.nan)
 axes[0,1].plot(x,med,'o-',color=color,label=side)
for ax in axes[0]:ax.set_xticks(x,[n for n,_ in layouts]);ax.legend();ax.grid(axis='y',alpha=.2)
axes[0,0].set_ylim(0,230);axes[0,0].set_ylabel('Clear independent targets / common216');axes[0,0].set_title('Fixed kitchen + full rail / mount / chain / new faucet')
axes[0,1].set_title('Median smallest Jacobian singular value');axes[0,1].set_ylabel('0.25m angular characteristic length')
selected=dict(layouts)[ID]
for ax,side in zip(axes[1],('R','L')):
 rows=selected[side]['rows'][:216];points={}
 for r in rows:
  pos=tuple(r['pos']);points.setdefault(pos,[]).append(r['pass_'])
 xyz=np.array(list(points));colors=np.array([sum(v) for v in points.values()]);sc=ax.scatter(xyz[:,0],xyz[:,1]+(xyz[:,2]-.93)*.27,c=colors,cmap='viridis',vmin=0,vmax=3,s=95,edgecolors='gray',linewidths=.5)
 ax.set_title(ID+' '+side+': orientations clear at each XYZ sample');ax.set_xlabel('Counter X (m)');ax.set_ylabel('Y + 0.27*(Z-0.93), separated height layers');ax.grid(alpha=.2)
 fig.colorbar(sc,ax=ax,label='0..3 sampled orientations')
fig.suptitle('Faucet-enabled R07: independent-arm exploration, not full-scene stroke acceptance',fontsize=13)
fig.text(.5,.014,'Opposite arm and movable fixtures excluded ONLY from maps. 36 faucet-relative samples kept in CSV; different faucet locations are not identical targets.',ha='center',fontsize=9)
fig.tight_layout(rect=[0,.035,1,.96]);fig.savefig(H/'renders/reachability_study.png');plt.close(fig)
print('NEW_MAPS',len(layouts),'rows',len(flat),flush=True)
