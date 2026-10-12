"""Honest CPU-only geometry renders, maximum1600px. No synthetic execution."""
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scene import H,load,build
from checker import Checker
from render import polygons,draw
from mobile import floor_check
def overlay(ax,ch,q):
 r=floor_check(ch,q);a,b=np.array(r['cable_branch_m']);ax.plot([a[0],b[0]],[a[1],b[1]],[a[2],b[2]],color='red',linewidth=3)
 ax.plot([-1.8,2.8],[-.025,-.025],[.03,.03],color='goldenrod',linewidth=3)
def main():
 cfg=load('results/selected.json')['config'];park=np.array(load('assets/park_mobile.json')['q']);t,meta=build(cfg);ch=Checker(t,meta)
 record=load('results/strokes/6.json');qs=record['internal'].get('path',[])
 q=np.array(qs[len(qs)//2]) if qs else park
 t,hm=build(cfg,'holder');held=Checker(t,hm)
 fig=plt.figure(figsize=(13,8),dpi=110);ax=fig.add_subplot(111,projection='3d');draw(ax,polygons(held,q),([-1.85,-.95,0],[2.80,.67,2.0]));overlay(ax,held,q)
 fig.suptitle('R09 tethered cart at counter | locally checked mandoline pose',fontsize=14)
 fig.text(.03,.025,'660 x 500 mm cart; fixed 850 mm / 20 deg mount. No connected carrot execution. Kitchen is estimated; cutaway view.',fontsize=10)
 fig.savefig(H/'renders/overview.png');plt.close(fig)
 fig=plt.figure(figsize=(13,8),dpi=110);ax=fig.add_subplot(111,projection='3d');draw(ax,polygons(ch,park,doors=True),([-1.85,-.95,0],[2.80,.67,2.1]));overlay(ax,ch,park)
 fig.suptitle('Folded parked snapshot | conditional end alcove; full idle fails',fontsize=14)
 fig.text(.03,.025,'All cabinet/oven sweeps x <= 1.80 m; robot stays beyond boundary. Alcove is assumed, not established by kitchen photos.',fontsize=10)
 fig.savefig(H/'renders/parked.png');plt.close(fig)
 limits=[('wash',([-.75,.05,.62],[-.20,.59,1.1])),('peeler',([-1.53,-.04,.83],[-.87,.37,1.07])),('mandoline',([.18,-.05,.83],[.70,.36,1.13])),('bowls',([-1.81,.23,.83],[-.70,.60,1.1])),('greens',([-1.00,.01,.83],[-.66,.32,1.12])),('tomato',([-.12,-.02,.83],[.16,.30,1.12]))]
 fig=plt.figure(figsize=(15,8),dpi=100);items=polygons(ch,park)
 for i,(name,lim) in enumerate(limits):
  ax=fig.add_subplot(2,3,i+1,projection='3d');draw(ax,items,lim,True);ax.set_title(name+' | full geometry',fontsize=11)
 fig.suptitle('Station design envelopes | fixture mechanisms and food quality remain unqualified',fontsize=14);fig.tight_layout();fig.savefig(H/'renders/stations.png');plt.close(fig)
 fig=plt.figure(figsize=(16,11),dpi=100)
 for i,k in enumerate(np.linspace(0,max(len(qs)-1,0),24).astype(int)):
  qq=np.array(qs[k]) if qs else q;ax=fig.add_subplot(4,6,i+1,projection='3d');draw(ax,polygons(held,qq),([-.15,-.8,0],[.95,.55,1.5]));ax.set_axis_off();ax.set_title(f'Local mandoline sample {k}',fontsize=8)
 fig.suptitle('24 frames of one locally checked stroke | NOT an executed carrot sequence',fontsize=15)
 fig.text(.025,.015,'No end-to-end carrot sequence exists. These frames show only saved, bounded local mandoline path states.',fontsize=11)
 fig.savefig(H/'renders/carrot_local_strip.png');plt.close(fig)
 # Reach map exposes base distribution and tested design heights, not just TCP.
 fig,axes=plt.subplots(2,4,figsize=(16,8),dpi=100)
 for ax,i in zip(axes.flat,range(1,9)):
  r=load(f'results/iterations/M{i:02d}.json')
  for j,probe in enumerate(r['probes']):
   bank=load(f'results/iterations/M{i:02d}_{probe["target"]}.json')
   rows=[x for x in bank['rows'] if 'q' in x]
   ax.scatter([x['q'][0] for x in rows],[x['q'][1] for x in rows],c=['green' if x['status']=='ok' else '#d38b83' for x in rows],marker=['o','^','s'][j],s=9,alpha=.6)
  ax.set(xlim=(-1.85,1.55),ylim=(-.62,-.27),xlabel='base X (m)',ylabel='base Y (m)',title=f'M{i:02d}: h={r["config"]["mount_height"]:.2f}m, {r["clear_samples"]}/3 targets')
 fig.suptitle('96 starts per corridor per design | green=admitted endpoint; red=rejected | yaw sampled +/-0.17rad')
 fig.tight_layout();fig.savefig(H/'renders/reach_map.png');plt.close(fig)
 print('Five CPU figures written, max1600px')
if __name__=='__main__':main()
