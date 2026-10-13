"""R19 prep audit: where can prep appliances stand without blocking the checked cooking motion?
(read-only screen; new file, nothing else changed)

Uses the stored swept volumes of r19prim_swept.py (results/r19/prim/swept_voxels.npz: 84 segments of the
checked R17/R18 actions: wok plate + sink rinse at both plating spots, faucet, lid, spider, spatula fetch)
and adds the 22 checked R19 hub-roadmap edges (results/r19/hub/edge_*.json 'qs', empty hand, every 4th
state). A candidate appliance is an axis-aligned envelope box on the counter (sizes from the market
research, labelled). A segment is FLAGGED if its swept voxels, dilated by 2 (hub edges: 3, because of the
4th-state subsampling), meet the appliance voxels dilated by 1, as in r19prim_swept.py. Flagged = must be
replayed with the checker (it may still pass); not flagged = cannot be hit (conservative by construction).
NOT screened: the arm's own reach to the appliance (chute, lever), and prep motions themselves.
python r19prep_screen.py -> results/r19/prep/screen.json"""
import sys,json,glob,os,time,collections
sys.path.insert(0,'.')
import numpy as np,mujoco
from scipy import ndimage
import chain
from scene import build,save
from checker import Checker
import kitchen15 as K15,kitchen16 as K,kitchen17 as K17
VOX=.02;LO=np.array([-2.6,-1.2,-.2]);DIM=np.array([270,130,130])   # as r19prim_swept.py
def lin(ix):return (ix[:,0]*DIM[1]+ix[:,1])*DIM[2]+ix[:,2]
def unlin(L):return np.stack([L//(DIM[1]*DIM[2]),(L//DIM[2])%DIM[1],L%DIM[2]],1)
def vox(pts):
 ix=np.floor((pts-LO)/VOX).astype(int);ok=np.all((ix>=0)&(ix<DIM),1);return np.unique(lin(ix[ok]))
def dilate(L,k):
 if len(L)==0:return L
 ix=unlin(L);a=ix.min(0)-k;b=ix.max(0)+k+1;g=np.zeros(b-a,bool);g[tuple((ix-a).T)]=True
 g=ndimage.binary_dilation(g,structure=np.ones((3,3,3),bool),iterations=k);w=np.argwhere(g)+a
 w=w[np.all((w>=0)&(w<DIM),1)];return np.unique(lin(w))
def box_pts_local(h):
 ax=[np.linspace(-h[i],h[i],max(2,int(np.ceil(2*h[i]/VOX))+1)) for i in range(3)];return np.stack(np.meshgrid(*ax,indexing='ij'),-1).reshape(-1,3)
def box_vox(c,s):return vox(box_pts_local(np.asarray(s,float)/2)+np.asarray(c,float))
# ---- swept volumes: stored chain segments + hub edges ----
t0=time.monotonic();Z=np.load('results/r19/prim/swept_voxels.npz');SW={k:dilate(Z[k].astype(np.int64),2) for k in Z.files}
K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);K.TOOL_XY['spatula']=(-1.15,.30);K.SPAT_ELEV=8.;K.SPAT_ROLL=180.
cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,r16=True,r17=True,r15_drum_taken=True,r16_tools={'ladle':None})
tree,meta=build(cfg,None);ch=Checker(tree,meta);m,d=ch.m,ch.d
rob=[g for g in range(m.ngeom) if m.geom(g).name.startswith('R_') and m.geom_type[g]!=mujoco.mjtGeom.mjGEOM_PLANE]
cache={g:box_pts_local(m.geom_aabb[g,3:])+m.geom_aabb[g,:3] for g in rob}
for f in sorted(glob.glob('results/r19/hub/edge_*.json')):
 e=json.load(open(f))
 if not e.get('ok') or not e.get('qs'):continue
 acc=[]
 for q in e['qs'][::4]+[e['qs'][-1]]:
  d.qpos[:]=q;mujoco.mj_kinematics(m,d);acc.append(vox(np.concatenate([(d.geom_xmat[g].reshape(3,3)@cache[g].T).T+d.geom_xpos[g] for g in rob])))
 SW['hub_edge__'+os.path.basename(f)[5:-5]]=dilate(np.unique(np.concatenate(acc)),3)
t_sw=time.monotonic()-t0
# ---- candidate appliances (envelope boxes, metres; x along the counter, y toward the wall, counter top z .85) ----
APP={ # name: (size x,y,z, basis)
 'slicer_3in1':((.50,.21,.28),'卓晋 3-in-1 21x33x28 cm (market_r10 13.2 M2) + its out bowl at the discharge end (R11 model: body 33 cm + bowl 17 cm)'),
 'meat_slicer':((.37,.34,.42),'850 W 切肉切菜一体机 32-37 x 30-34 x 31-42 cm, ~21 kg (market_r10 13.8 A), largest values'),
 'belt_cutter':((.28,.26,.38),'切葱花机 belt cutter 28 x 26 x 38 cm, 8.7 kg (market_r10 13.8 B)'),
 'lever_base':((.22,.26,.42),'AY-403 lever base: 223 mm deep, 420 mm tall incl. handle (market_r10 13.2 M1); width ~22 cm (R11 base plate)'),
 'tool_work_spot':((.39,.26,.45),'R11 peeler station envelope at the fetched-tool spot (scene.py peel station, guards + open lid)')}
def spots(sx,sy):
 front=.025+sy/2;back=.58-sy/2
 return {'R11 slicer spot (0.30, front)':(.30,front),'right counter back (0.30, back)':(.30,back),
  'left counter front (-1.00)':(-1.00,front),'left counter back (-1.00)':(-1.00,back),'left counter back by the sink (-0.88)':(-.88,back),
  'far left front (-1.62)':(-1.62,front),'far left back (-1.62)':(-1.62,back),'left counter middle front (-1.30)':(-1.30,front)}
rows=[];t1=time.monotonic()
for a,(s,basis) in APP.items():
 for sp,(x,y) in spots(s[0],s[1]).items():
  F=dilate(box_vox([x,y,.85+s[2]/2],s),1);flag=[k for k,v in SW.items() if np.intersect1d(v,F,assume_unique=True).size]
  by=collections.Counter(k.split('__')[0] for k in flag)
  rows.append(dict(appliance=a,spot=sp,center=[round(x,3),round(y,3)],size_m=list(s),flagged=len(flag),of=len(SW),by_action=dict(by),flagged_segments=flag))
  print(f'{a:15s} {sp:40s} ({x:+.2f},{y:.2f})  flagged {len(flag):3d}/{len(SW)}  {dict(by)}',flush=True)
# also the R18b spatula rest itself vs the fetched-tool spot is a static overlap (r19prep_replay / audit), not screened here
save('results/r19/prep/screen.json',dict(method=__doc__,swept_build_s=round(t_sw,1),screen_s=round(time.monotonic()-t1,1),segments=len(SW),
 hub_edges=[k for k in SW if k.startswith('hub_edge__')],appliances={a:dict(size_m=s,basis=b) for a,(s,b) in APP.items()},rows=rows))
print('swept build',round(t_sw,1),'s; screen',round(time.monotonic()-t1,1),'s')
