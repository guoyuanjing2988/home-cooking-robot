"""Top view of the R19 prep layout (kitchen19.LAYOUT) with the object keyframe paths of the stored prep
sets (results/r19/prep/chain_<act>_<TAG>.json). New file; drawing only, no check.
python r19prep_render.py [TAG=smoke] -> renders/r19/prep_layout_r19.png"""
import sys,json,os
sys.path.insert(0,'.')
import numpy as np
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
import kitchen19 as K19
KV=dict(a.split('=',1) for a in sys.argv[1:]);TAG=KV.get('TAG','smoke')
fig,ax=plt.subplots(figsize=(14,5.2))
def rect(x0,x1,y0,y1,fc,ec='k',lw=.6,ls='-',a=1.,lab=None,z=1):
 ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,fc=fc,ec=ec,lw=lw,ls=ls,alpha=a,zorder=z,label=lab))
rect(-1.80,-0.70,0,.60,'#ece6dc');rect(-0.08,.709,0,.60,'#ece6dc');rect(-0.70,-0.10,.08,.52,'#cfe0ea',lab='sink')
rect(.63,1.03,0,.42,'#555555',a=.8,lab='wok cooker');rect(-2.44,-1.89,-.05,.55,'#dfe7ee',lab='fridge (estimated)')
ax.plot([-1.80,-0.70],[.212,.212],'k--',lw=.8);ax.plot([-0.10,.69],[.212,.212],'k--',lw=.8);ax.text(-1.79,.222,'upper-cabinet front plane (cabinets above 1.35 m)',fontsize=7)
for c in ((.17,.13),(.43,.13)):ax.add_patch(Circle(c,.12,fc='white',ec='k',lw=.6))
ax.text(.30,-.04,'plating spots',ha='center',fontsize=7)
rect(-1.515,-1.195,.04,.34,'#c9d8b6',lab='raw tray (unchanged)');ax.text(-1.355,.19,'raw tray',ha='center',fontsize=7)
rect(-1.19,-1.11,.26,.34,'#999999');ax.plot([-1.15,-1.15],[-.077,.272],color='#777777',lw=3);ax.text(-1.14,-.07,'spatula (R18b)',fontsize=6)
for x,n in ((-1.40,'potato'),(-1.13,'greens')):ax.add_patch(Circle((x,.46),.10,fc='none',ec='#888888',ls=':'))
ax.text(-1.40,.46,'staging\nbowl',ha='center',va='center',fontsize=5,color='#666666')
ax.add_patch(Circle((-0.86,.46),.10,fc='none',ec='#cc6666',ls=':'));ax.text(-0.86,.46,'tomato bowl\nmoved off',ha='center',va='center',fontsize=5,color='#cc6666')
x,y,yaw=K19.LAYOUT['slicer'];rect(x-.105,x+.105,y-.165,y+.165,'#f2c94c',lab='slicer (Zhuojin 3-in-1, resident, turned 90 deg)');c=K19.chute_top(x,y,yaw)
rect(c[0]-.035,c[0]+.035,c[1]-.05,c[1]+.05,'white',lw=.8);ax.add_patch(Circle((x,y+.275),.085,fc='#f9e4a0',ec='k',lw=.6))
ax.text(c[0],c[1]-.075,'chute',ha='center',fontsize=6)
x,y,yaw=K19.LAYOUT['lever'];rect(x-.11,x+.11,y-.095,y+.165,'#9ec5e8',lab='work spot: lever base (fetched)');rect(x-.065,x+.065,y-.065,y+.065,'#cfe3f5')
ax.plot([x],[y],'k+');ax.text(x,y-.13,'work spot\n(lever base / cold box,\none at a time)',ha='center',fontsize=6)
x,y,yaw=K19.LAYOUT['cold_box'];rect(x-.15,x+.15,y-.04,y+.04,'none',ec='#2f6f9f',ls='--',lw=1.2,lab='cold-box set-down (instead of the lever base)')
ax.add_patch(Rectangle((-0.4225,.533),.045,.045,fc='#bbbbbb',ec='k',lw=.6));ax.plot([-0.40,-0.40],[.37,.555],color='#888888',lw=3);ax.plot([-0.40],[.37],'bo',ms=4);ax.text(-0.39,.355,'faucet outlet',fontsize=6)
cols=dict(carrot='#e07b24',tomato='#d0312d',press='#3060b0')
for a in ('carrot','tomato','press'):
 f=f'results/r19/prep/chain_{a}_{TAG}.json'
 if not os.path.exists(f):continue
 r=json.load(open(f));P=np.array([k['p'] for k in r['keyframes']])
 ax.plot(P[:,0],P[:,1],'-o',color=cols[a],ms=3,lw=1.2,label=f"{a} set ({r['time_s']} s, {'pass' if r['ok'] else 'fail'})",zorder=5)
ax.set_xlim(-2.5,1.1);ax.set_ylim(-.12,.62);ax.set_aspect('equal');ax.set_xlabel('x along the counter (m)');ax.set_ylabel('y toward the wall (m)')
ax.set_title('R19 prep layout in the R18b sim kitchen (top view, estimated sizes); lines = held-object keyframe paths')
ax.legend(loc='upper right',fontsize=6,ncol=2);fig.tight_layout();os.makedirs('renders/r19',exist_ok=True);o=KV.get('OUT','renders/r19/prep_layout_r19.png');fig.savefig(o,dpi=120);print(o)
