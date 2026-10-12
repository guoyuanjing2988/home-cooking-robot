import json,sys,csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
H=Path(__file__).resolve().parent;O=H/'results';ID=sys.argv[1];d=json.loads((O/'reachability'/ID/'R.json').read_text());rows=d['rows'];fig,axes=plt.subplots(2,3,figsize=(15,9),subplot_kw={'projection':'3d'})
flat=[]
clear=[r for r in rows if r['pass_']];maximum=max(r['witness']['dexterity']['min_singular_value'] for r in clear)
for column,orientation in enumerate(('down','front','side')):
 ax=axes[0,column]
 subset=[r for r in rows if r['orientation']==orientation]
 for ok,color,label in [(False,'#bb7777','No admitted seed'),(True,'#197f78','Clear seed')]:
  points=np.array([r['pos'] for r in subset if bool(r['pass_'])==ok])
  if len(points):ax.scatter(points[:,0],points[:,1],points[:,2],c=color,s=16,label=label,alpha=.7)
 ax.set(xlabel='X (m)',ylabel='Y (m)',zlabel='Z (m)',title=orientation);ax.view_init(elev=25,azim=-65)
 ax=axes[1,column];good=[r for r in subset if r['pass_']];points=np.array([r['pos'] for r in good]);values=[r['witness']['dexterity']['min_singular_value'] for r in good]
 if len(points):color=ax.scatter(points[:,0],points[:,1],points[:,2],c=values,s=25,cmap='viridis',vmin=0,vmax=maximum)
 ax.set(xlabel='X (m)',ylabel='Y (m)',zlabel='Z (m)',title=orientation+' / dexterity of clear seed');ax.view_init(elev=25,azim=-65)
axes[0,0].legend(fontsize=8);fig.suptitle(ID+' UR5e: '+str(sum(r['pass_'] for r in rows))+'/'+str(len(rows))+' clear targets; movable fixtures excluded\nExploratory reach and dexterity, not full-scene stroke or meal acceptance',fontsize=13);fig.subplots_adjust(left=.03,right=.89,top=.89,bottom=.06,wspace=.18,hspace=.25);bar=fig.add_axes([.925,.12,.015,.29]);fig.colorbar(color,cax=bar,label='Minimum singular value; orientation length = 0.25 m');fig.savefig(H/'renders/reachability_study.png',dpi=100);plt.close(fig)
for n in range(54,int(ID[1:])+1):
 for side in ('R','L'):
  p=O/'reachability'/('L'+str(n))/(side+'.json')
  if not p.exists():continue
  data=json.loads(p.read_text())
  for i,r in enumerate(data['rows']):
   best=(r.get('witness') if r['pass_'] else r.get('best')) or {};dex=best.get('dexterity') or {};flat.append(dict(layout='L'+str(n),side=side,target=i,x_m=r['pos'][0],y_m=r['pos'][1],z_m=r['pos'][2],orientation=r['orientation'],region=r.get('region'),clear=r['pass_'],starts=r['starts'],min_singular_value=dex.get('min_singular_value'),condition_number=dex.get('condition_number'),source=str(p.relative_to(H)),reuse_note=data.get('reuse_note')))
with (O/'reachability_map_v5.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=flat[0]);w.writeheader();w.writerows(flat)
print('MAP_ROWS',len(flat))

