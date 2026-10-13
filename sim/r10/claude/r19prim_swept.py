"""R19 stored swept volumes per segment, and the layout-change screen they allow.
For every saved playback state of the checked chains (results/r17, as r19prim_inventory.py), the
robot's geoms (cart, arm, gripper, fingers, held object: every geom named R_*) are sampled inside their
local bounding boxes (MuJoCo geom_aabb, a box that contains the geom) every <= 2 cm, put into world
coordinates by forward kinematics, and recorded as 2 cm voxels. Between two saved states the motion is
interpolated (cart and joints linear, as the checker's own steps) so that no point moves more than 1 cm
per sub-step (bound: |d cart| + sum |d joint| x 1.0 m). The union over a segment's states is that
segment's swept volume (segments from results/r19/prim/segments.json, so they match the inventory).
Screen for a fixture change: the fixture's geoms are sampled the same way; a segment is FLAGGED for
re-verification if its swept voxels, dilated by 2 voxels (box sampling + the 10 mm gap), meet the
fixture's voxels dilated by 1. This is conservative (no false negatives by construction; it may flag too
much). It is not a verification: flagged segments are then replayed with the unchanged checker.
Ground truth: the replay of r18spatreplay.py (every saved state, checker full=False, spatula in the
scene) for spatula rests R18 tried, timed here.
Also a fixture-dependency matrix: for each fixture group (cooker, faucet, sink, upper cabinets, ...),
which segments would have to be re-verified if it moved or changed shape.
python r19prim_swept.py -> results/r19/prim/swept.json, swept_voxels.npz"""
import sys;sys.path.insert(0,'.')
import json,time,collections,numpy as np,mujoco
from scipy import ndimage
import chain
from scene import build
from checker import Checker
import kitchen15 as K15,kitchen16 as K,kitchen17 as K17
K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.)
BASE=dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True)
OUT='results/r19/prim';VOX=.02;LO=np.array([-2.6,-1.2,-.2]);DIM=np.array([270,130,130]);REACH=1.0
CHAINS=dict(wok_plate_rinse='wok_s-1_final',wok_plate2_rinse='wok_s-1_r18plate2b',faucet_open='lever_s+1_final',lid_off_to_rack='lid_s-1_final',spider_pot_to_plate='spider_s+1_final',spatula_fetch='spatula_s-1_r18roll-1.15_.30')
QUERIES=[   # spatula rests tried in R18 (README_R10 R18 / R18b, results/r18/spatscan.json): x, y, yaw, elev, roll
 dict(name='spatula (-0.85,0.30) elev 50',x=-.85,y=.30,yaw=0.,elev=50.,roll=0.,r18='rejected: hit by the upper arm on the wok sink trip and the faucet'),
 dict(name='spatula (-1.15,0.30) elev 50',x=-1.15,y=.30,yaw=0.,elev=50.,roll=0.,r18='spatscan: blocks wok_s-1_final at state 230'),
 dict(name='spatula (-1.15,0.30) elev 8 flipped',x=-1.15,y=.30,yaw=0.,elev=8.,roll=180.,r18='chosen R18b rest: no hits'),
 dict(name='spatula (1.60,0.30) elev 8',x=1.60,y=.30,yaw=0.,elev=8.,roll=0.,r18='see spatscan.json')]
GROUPS=[('cooker_wok_zone',('r15_cooker','r15_knob','r15_camera','r15_drum')),('hood',('r14_hood',)),('upper_cabinets',('upper_cabinet','r14_upper')),
 ('season_staple_station',('r14_season','r14_cup','r14_staple')),('plating_spots',('r15_plate','r17_plate2')),('sink',('sink_',)),('faucet',('r17_faucet','r17_lever','faucet_v3')),
 ('zone2_pot',('r16_pot','r16_ind2')),('lid_rack',('r16_rack','r16_lid')),('tool_rest_spider',('r16_rest','r16_spider')),('counters_cabinet_fronts',('counter_','north_cabinet','south_cabinets','sink_cabinet')),
 ('walls',('north_wall','south_wall')),('prep_items',('raw_','stored_bowl'))]
def lin(ix):return (ix[:,0]*DIM[1]+ix[:,1])*DIM[2]+ix[:,2]
def unlin(L):return np.stack([L//(DIM[1]*DIM[2]),(L//DIM[2])%DIM[1],L%DIM[2]],1)
def vox(pts):
 ix=np.floor((pts-LO)/VOX).astype(int);ok=np.all((ix>=0)&(ix<DIM),1);return np.unique(lin(ix[ok]))
def dilate(L,k):
 if len(L)==0:return L
 ix=unlin(L);a=ix.min(0)-k;b=ix.max(0)+k+1;g=np.zeros(b-a,bool);g[tuple((ix-a).T)]=True
 g=ndimage.binary_dilation(g,structure=np.ones((3,3,3),bool),iterations=k);w=np.argwhere(g)+a
 w=w[np.all((w>=0)&(w<DIM),1)];return np.unique(lin(w))
def box_pts(m,g):
 c,h=m.geom_aabb[g,:3],m.geom_aabb[g,3:];ax=[np.linspace(c[i]-h[i],c[i]+h[i],max(2,int(np.ceil(2*h[i]/VOX))+1)) for i in range(3)]
 return np.stack(np.meshgrid(*ax,indexing='ij'),-1).reshape(-1,3)
def geom_world_pts(m,d,gs,cache):
 return np.concatenate([(d.geom_xmat[g].reshape(3,3)@cache[g].T).T+d.geom_xpos[g] for g in gs])
def model_for(n,r,extra=None):
 for k,v in r.get('tool_xy',{}).items():
  if k!='spatula':K.TOOL_XY[k]=tuple(v)
 if r['obj']=='wok':K17.set_wok_tilt(r.get('wok_tilt',0.))
 cfg=chain.chain_cfg('SD',**{**BASE,**r.get('scene',{}),**(extra or {}),**K17.held_cfg(r['obj'],r['grasp_sense'])});tree,meta=build(cfg,None);return Checker(tree,meta)
seglab=json.load(open(f'{OUT}/segments.json'))['labels'];inv=json.load(open(f'{OUT}/inventory.json'))
swept={};stats={};t0=time.monotonic()
for n,f in CHAINS.items():
 r=json.load(open(f'results/r17/chain_{f}.json'));ch=model_for(n,r);m,d=ch.m,ch.d
 rob=[g for g in range(m.ngeom) if m.geom(g).name.startswith('R_') and m.geom_type[g]!=mujoco.mjtGeom.mjGEOM_PLANE];cache={g:box_pts(m,g) for g in rob}
 P=np.array(r['play']);lab=seglab[n];lab=[lab[1] if i==0 else l for i,l in enumerate(lab)];acc=collections.defaultdict(list);nsub=0
 def add(q,key):
  d.qpos[:]=q;mujoco.mj_kinematics(m,d);acc[key].append(vox(geom_world_pts(m,d,rob,cache)))
 for i in range(len(P)):
  if i==0:add(P[0],lab[0]);continue
  dq=np.abs((P[i,3:9]-P[i-1,3:9]+np.pi)%(2*np.pi)-np.pi);b=abs(P[i,0]-P[i-1,0])+dq.sum()*REACH;k=max(1,int(np.ceil(b/.01)))
  step=P[i]-P[i-1];step[3:9]=(step[3:9]+np.pi)%(2*np.pi)-np.pi
  for s in range(1,k+1):add(P[i-1]+step*s/k,lab[i]);nsub+=1
 for a,qs in zip(r['approaches'],r['approach_qs']):   # empty-gripper approach states (the held object geoms are still on the gripper here: conservative)
  for q in qs:add(np.array(q),f"approach@{a['kf']}")
 for key,v in acc.items():swept[f'{n}|{key}']=np.unique(np.concatenate(v))
 stats[n]=dict(states=len(P),substeps=nsub,segments=len(acc),voxels=int(len(np.unique(np.concatenate([swept[f'{n}|{k}'] for k in acc])))))
 print(n,stats[n],round(time.monotonic()-t0,1),flush=True)
t_vox=time.monotonic()-t0
np.savez_compressed(f'{OUT}/swept_voxels.npz',**{k.replace('|','__').replace('>','').replace('@','_'):v.astype(np.int32) for k,v in swept.items()})
D2={k:dilate(v,2) for k,v in swept.items()}
def segname(n,key):
 if key.startswith('approach@'):return f'approach at kf {key[9:]}'
 if key.startswith('join@'):return f'meet join at kf {key[5:]}'
 a,b=key.split('->');segs=[s for s in inv['chains'][n]['segments'] if s.get('i1') is not None and s['frm'].endswith(f'#{a}') and s['to'].endswith(f'#{b}')]
 return f"{segs[0]['cls']}: {segs[0]['frm']} -> {segs[0]['to']}" if segs else key
def nstates(n,key):
 if key.startswith('approach@'):return 7
 return sum(1 for l in seglab[n] if l==key)+(1 if seglab[n][1]==key else 0)
# ---- fixture-dependency matrix (the chains' own scenes) ----
dep={};fix_vox={}
for n,f in CHAINS.items():
 r=json.load(open(f'results/r17/chain_{f}.json'));ch=model_for(n,r);m,d=ch.m,ch.d;mujoco.mj_kinematics(m,d)
 for gname,pref in GROUPS:
  gs=[g for g in range(m.ngeom) if not m.geom(g).name.startswith('R_') and m.geom(g).name.startswith(pref) and m.geom_type[g]!=mujoco.mjtGeom.mjGEOM_PLANE]
  if not gs:continue
  F=dilate(vox(geom_world_pts(m,d,gs,{g:box_pts(m,g) for g in gs})),1)
  for key in [k.split('|',1)[1] for k in swept if k.startswith(n+'|')]:
   if np.intersect1d(D2[f'{n}|{key}'],F,assume_unique=True).size:dep.setdefault(gname,{}).setdefault(n,[]).append(segname(n,key))
nseg_total=sum(1 for k in swept)
dep_summary={g:dict(segments_flagged=sum(len(v) for v in dd.values()),of=nseg_total,chains=sorted(dd)) for g,dd in dep.items()}
# ---- layout-change queries: screen (voxels) vs ground truth (replay, r18spatreplay.py method) ----
RE=['wok_plate_rinse','wok_plate2_rinse','faucet_open','lid_off_to_rack','spider_pot_to_plate']   # the actions r18spatreplay.py replays
qres=[]
for Q in QUERIES:
 K.TOOL_XY['spatula']=(Q['x'],Q['y']);K.SPAT_ELEV,K.SPAT_YAW,K.SPAT_ROLL=Q['elev'],Q['yaw'],Q['roll']
 row=dict(query=Q,screen={},truth={},screen_ms=0.,replay_s=0.,replay_states=0)
 for n in RE:
  r=json.load(open(f"results/r17/chain_{CHAINS[n]}.json"));ex={'r17_plate2':[.43,K15.PLATE['c'][1],K15.PLATE['c'][2]]} if 'plate2' in n else {}
  ch=model_for(n,r,{**ex,'r16_tools':{'ladle':None}});m,d=ch.m,ch.d;mujoco.mj_kinematics(m,d)
  gs=[g for g in range(m.ngeom) if 'spatula' in m.geom(g).name and not m.geom(g).name.startswith('R_')]
  ts=time.perf_counter();F=dilate(vox(geom_world_pts(m,d,gs,{g:box_pts(m,g) for g in gs})),1)
  flag=[k.split('|',1)[1] for k in swept if k.startswith(n+'|') and np.intersect1d(D2[k],F,assume_unique=True).size]
  row['screen_ms']+=(time.perf_counter()-ts)*1000;row['screen'][n]=[segname(n,k) for k in flag]
  row.setdefault('screen_states',0);row['screen_states']+=sum(nstates(n,k) for k in flag)
  ts=time.perf_counter();hit=collections.Counter()
  for i,q in enumerate(r['play']):
   c=ch.check(np.array(q),full=False,mass=0.)
   if any(any('spatula' in g for g in h['pair']) for h in c['hits']):hit[seglab[n][i] or seglab[n][1]]+=1
  row['replay_s']+=time.perf_counter()-ts;row['replay_states']+=len(r['play'])
  row['truth'][n]={segname(n,k):v for k,v in hit.items()}
  missed=[segname(n,k) for k in hit if segname(n,k) not in row['screen'][n]]
  row.setdefault('missed_by_screen',[]).extend(missed)
 row['replay_s']=round(row['replay_s'],1);row['screen_ms']=round(row['screen_ms'],1)
 row['flagged_segments']=sum(len(v) for v in row['screen'].values());row['truly_hit_segments']=sum(len(v) for v in row['truth'].values())
 row['segments_total']=sum(1 for k in swept if k.split('|')[0] in RE)
 qres.append(row);print(Q['name'],'flagged',row['flagged_segments'],'of',row['segments_total'],'hit',row['truly_hit_segments'],'missed',row['missed_by_screen'],'replay',row['replay_s'],'s',flush=True)
ms_per_state=1000*sum(q['replay_s'] for q in qres)/sum(q['replay_states'] for q in qres)
out=dict(source='r19prim_swept.py',voxel_m=VOX,dilation=dict(swept=2,fixture=1,why='box sampling <= 2 cm (1 voxel) + the 10 mm robot gap (1 voxel); fixture box sampling (1 voxel)'),
 voxelize_s=round(t_vox,1),per_chain=stats,segments_stored=nseg_total,npz_bytes=None,
 replay_ms_per_state=round(ms_per_state,1),fixture_dependency=dep_summary,fixture_dependency_detail=dep,queries=qres)
import os;out['npz_bytes']=os.path.getsize(f'{OUT}/swept_voxels.npz')
json.dump(out,open(f'{OUT}/swept.json','w'),indent=1)
print(json.dumps(dep_summary,indent=0));print('replay ms/state',round(ms_per_state,1),'npz bytes',out['npz_bytes'])
