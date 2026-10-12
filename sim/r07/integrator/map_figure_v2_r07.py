"""Scientific reachability/dexterity plot and flat machine-readable map table."""
import json,csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
H=Path(__file__).resolve().parent;O=H/'results';layouts=[];flat=[]
for directory in sorted((O/'reachability').iterdir()):
 if not all((directory/(s+'.json')).exists() for s in ('R','L')):continue
 files={s:json.loads((directory/(s+'.json')).read_text()) for s in ('R','L')}
 if not all(x.get('complete') for x in files.values()):continue
 layouts.append((directory.name,files))
 for side,x in files.items():
  for r in x['rows']:
   dex=(r.get('witness') or {}).get('dexterity',{});flat.append(dict(layout=directory.name,arm=side,x_m=r['pos'][0],y_m=r['pos'][1],z_m=r['pos'][2],orientation=r['orientation'],region=r['region'],kinematic_solutions=r['kinematic_solutions'],starts=r['starts'],clearance_pass=r['pass_'],min_singular_value=dex.get('min_singular_value'),condition_number=dex.get('condition_number'),source=f'results/reachability/{directory.name}/{side}.json'))
with (O/'reachability_map.csv').open('w',newline='',encoding='utf-8') as file:w=csv.DictWriter(file,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
fig,axes=plt.subplots(1,2,figsize=(14,6),dpi=100);x=np.arange(len(layouts))
for side,offset,color in [('R',-.19,'#287da5'),('L',.19,'#ce7537')]:
 count=[sum(r['pass_'] for r in data[side]['rows']) for _,data in layouts];axes[0].bar(x+offset,count,.36,label=side+' arm',color=color)
 for xx,n in zip(x+offset,count):axes[0].text(xx,n+3,str(n),ha='center',fontsize=9)
 med=[np.median([r['witness']['dexterity']['min_singular_value'] for r in data[side]['rows'] if r['pass_']]) for _,data in layouts];axes[1].plot(x,med,'o-',color=color,label=side+' arm')
axes[0].set_ylim(0,280);axes[0].axhline(252,color='gray',ls='--',lw=1);axes[0].set_ylabel('Accepted independent empty-arm targets / 252');axes[0].set_title('Original fixed kitchen + full rails, chains and mounts')
axes[1].set_ylabel('Median smallest singular value');axes[1].set_title('Jacobian dexterity at accepted map poses')
for ax in axes:ax.set_xticks(x,[name for name,_ in layouts]);ax.legend();ax.grid(axis='y',alpha=.2)
fig.suptitle('R07 reachability study: individual arms; opposite arm and movable fixtures excluded',fontsize=12);fig.text(.5,.025,'252 targets per arm: counter/sink and faucet surroundings, three orientations. Dexterity uses 0.25 m angular characteristic length. Not meal or idle acceptance.',ha='center',fontsize=8);fig.tight_layout(rect=[0,.045,1,.94]);fig.savefig(H/'renders/reachability_study.png');plt.close(fig)
print('MAPS',len(layouts),'rows',len(flat),flush=True)
