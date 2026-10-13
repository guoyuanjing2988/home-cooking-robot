"""R19 motion-library inventory (read-only on earlier results; no re-planning, no new collision checks).
Decomposes the checked whole-action chains (r17chain.py, results/r17/chain_*_final.json and the R18
ones) and the R15 stir cycle (r15stirwalk2.py, results/r15/stirwalk2_h_scrape_dice_r17.json) into
recurring sub-motions ("primitive classes") and tabulates counts, states, times and compute time.

How a chain is split (all from the saved data):
 - every saved playback state ('play', 11 values: cart x, base y, base yaw, 6 arm joints, 2 jaws) is put
   through forward kinematics (TCP site R_prep); the held object's pose follows from
   kitchen16.T_tool_obj (the same grasp transform r17chain.py used), so each state has an object pose;
 - the play order of r17chain.py is: reversed piece (first anchor -> keyframe 0), the anchor, then per
   pair of anchors: piece (anchor -> meet), join states, reversed piece (next anchor -> meet) without its
   meet state, the next anchor; then the piece (last anchor -> last keyframe). Keyframe arrivals are
   found as the state where the object is at the keyframe position (< 6 mm, the closest state of that run), and the end of each join
   from the saved piece step counts, so every state gets its keyframe segment or its join;
 - each keyframe segment is labelled with a primitive class (table SEG below, from the keyframe labels
   in r17chain.action());
 - times follow r17chain.py's timing model (object <= 0.10 m/s and 45 deg/s, joints <= 60 deg/s,
   cart <= 0.25 m/s per step; dwells from r17chain.action(); joins as saved; grasp and release 0.8 s
   each; the grasp approaches as saved) and are compared with the chain's saved time_s.
The stir cycle saves no states; its state counts follow from r15stirwalk2.py's parameters (10 ms IK
steps over 0.76 of the 2.4 s bench period per stroke, 39 interior checks per air return).
Also: identical states shared between chains and inside a chain (reverse reuse), and the compute
spent on every saved R17/R18 chain run (elapsed_s).
python r19prim_inventory.py -> results/r19/prim/inventory.json (+ segments.json, per-state segment labels)"""
import sys;sys.path.insert(0,'.')
import json,os,glob,collections,numpy as np,mujoco
from scipy.spatial.transform import Rotation
import chain
from scene import build
from checker import Checker
import kitchen15 as K15,kitchen16 as K,kitchen17 as K17
K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.)
BASE=dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True)
VW,WW,QW,CW,GRASP_S=.10,45.,60.,.25,.8   # r17chain.py timing assumptions
TOL=.006   # keyframe p is saved rounded to 1 mm and the IK accepts <= 5 mm pose error
OUT='results/r19/prim'
CHAINS={   # name -> (file, action label used in the meal schedule)
 'wok_plate_rinse':'results/r17/chain_wok_s-1_final.json',
 'wok_plate2_rinse':'results/r17/chain_wok_s-1_r18plate2b.json',
 'faucet_open':'results/r17/chain_lever_s+1_final.json',
 'lid_off_to_rack':'results/r17/chain_lid_s-1_final.json',
 'spider_pot_to_plate':'results/r17/chain_spider_s+1_final.json',
 'spatula_fetch':'results/r17/chain_spatula_s-1_r18roll-1.15_.30.json'}
# dwells at keyframe arrival (r17chain.action(): kf(..., dw=...))
DWELL={('wok','tipped 90 (plated)'):2.,('wok','under the tap'):5.,('wok','emptied'):1.,('spider','drain'):5.}
# primitive class of every keyframe transition k -> k+1 (labels from r17chain.action(); the comments say why)
SEG={
 'wok':['seat_lift',        # pick -> lifted: 2.2 cm straight up off the cooker bowl (contact window)
        'carry','carry',    # leave the cooker diagonally, to the lane
        'carry',            # lane -> over the plate
        'tip','untip',      # tip 90 deg toward the robot over the plate, level again
        'carry',            # to the sink lane
        'insert',           # lane -> under the tap (into the space under the spout)
        'extract',          # 7 cm forward, 6 cm up, out from under the spout
        'tip','untip',      # emptied into the sink
        'carry','carry','carry','carry',   # back to the cooker
        'seat_lower'],      # lowered -> set down (contact window)
 'lever':['lever'],         # 30 deg about the lever pivot
 'lid':['seat_lift','extract','carry','reorient','carry','carry','carry','insert'],   # off the pot, slide out of the hood, up, roll 90, carry high, down into the rack
 'spider':['seat_lift','carry','carry','carry','insert','extract','carry','carry','carry','carry','tip','untip','carry','carry','carry','carry','carry','seat_lower'],
 'spatula_b':['seat_lift','carry','carry','carry','insert']}   # rest -> lifted -> out and up -> lane -> over the wok -> down to the stroke start
CONTACT={'approach','seat_lift','seat_lower','insert','extract','lever','stroke'}   # slow straight / process segments (contact windows or within mm of a fixture)
os.makedirs(OUT,exist_ok=True)
def wrap(a):return (a+np.pi)%(2*np.pi)-np.pi
def idx_of(label):return int(label.rsplit('#',1)[1])
def analyse(name,fn):
 r=json.load(open(fn));obj,sign=r['obj'],r['grasp_sense']
 for k,v in r.get('tool_xy',{}).items():K.TOOL_XY[k]=tuple(v)
 if obj=='wok':K17.set_wok_tilt(r.get('wok_tilt',0.))
 cfg=chain.chain_cfg('SD',**{**BASE,**r.get('scene',{}),**K17.held_cfg(obj,sign)});tree,meta=build(cfg,None);ch=Checker(tree,meta)
 m,d=ch.m,ch.d;sid=m.site('R_prep').id;T=np.asarray(K.T_tool_obj(obj,sign),float)
 P=np.array(r['play'],float);N=len(P)
 def fk(q):
  d.qpos[:]=q;mujoco.mj_kinematics(m,d);pt=d.site_xpos[sid].copy();Rt=d.site_xmat[sid].reshape(3,3).copy()
  return pt+Rt@T[:3,3],Rt@T[:3,:3],pt
 PO,RO,PT=zip(*[fk(q) for q in P]);PO,RO,PT=np.array(PO),np.array(RO),np.array(PT)
 KF=r['keyframes'];nk=len(KF);A=[k['i'] for k in KF if k['anchor']];M=[k['i'] for k in KF if k['meet']]
 steps={(idx_of(p['frm']),idx_of(p['to'])):p['steps'] for p in r['pieces']}
 # keyframe arrivals (sequential, object position at the keyframe)
 arr=[];i=0
 for k in range(nk):
  pk=np.array(KF[k]['p'])
  if k>0 and np.allclose(pk,KF[k-1]['p'],atol=1e-6):   # same position, different rotation (lever): reached at the end of the run at that position
   j=i
   while j+1<N and np.linalg.norm(PO[j+1]-pk)<TOL:j+=1
   arr.append(j);i=j;continue
  dd=np.linalg.norm(PO-pk,axis=1);c=np.where(dd[i:]<TOL)[0]
  assert len(c),(name,k,KF[k]['label'],float(dd[i:].min()))
  j=i+c[0]
  while j+1<N and dd[j+1]<TOL and dd[j+1]<=dd[j]:j+=1
  arr.append(j);i=j+1 if k in M else j
 # end of each join: the reversed piece (next anchor -> meet) minus its meet state precedes the next anchor
 leave={}
 for a,b in zip(A,A[1:]):
  x=[mm for mm in M if a<mm<b][0];leave[x]=arr[b]-steps[(b,x)]
 jn={x:j for x,j in zip([x for x in M if A[0]<x<A[-1]],r['joins'])}
 segs=[];lab=['']*N
 def seg_stats(i0,i1):
  qa=P[i0:i1+1];dq=np.degrees(np.abs(wrap(np.diff(qa[:,3:9],axis=0))));dc=np.abs(np.diff(qa[:,0]))
  dp=np.linalg.norm(np.diff(PO[i0:i1+1],axis=0),axis=1)
  da=np.array([np.degrees(np.linalg.norm(Rotation.from_matrix(RO[s+1]@RO[s].T).as_rotvec())) for s in range(i0,i1)])
  dt=np.maximum.reduce([dp/VW,da/WW,dq.max(1)/QW,dc/CW]) if i1>i0 else np.zeros(0)
  return dict(states=int(i1-i0),obj_path_m=round(float(dp.sum()),3),obj_rot_deg=round(float(da.sum()),1),cart_m=round(float(dc.sum()),3),
   joint_path_deg=round(float(dq.sum(0).max()) if i1>i0 else 0.,1),max_step_deg=round(float(dq.max()) if i1>i0 else 0.,2),max_step_obj_mm=round(float(dp.max()*1000) if i1>i0 else 0.,1),time_s=round(float(dt.sum()),2))
 for k in range(nk-1):
  i0=leave.get(k,arr[k]);i1=arr[k+1]
  if k in leave:   # the join at meet k (incl. any cart shuffle), timed as saved
   j=jn[k];st=seg_stats(arr[k],leave[k]);st['time_s']=j['s'];segs.append(dict(cls='meet_join',frm=KF[k]['label']+f'#{k}',to=KF[k]['label']+f'#{k}',i0=arr[k],i1=leave[k],arm_deg=j['arm_deg'],cart_shuffle_m=j.get('cart_m',0.),**st))
   for s in range(arr[k]+1,leave[k]+1):lab[s]=f'join@{k}'
  st=seg_stats(i0,i1);segs.append(dict(cls=SEG[obj][k],frm=KF[k]['label']+f'#{k}',to=KF[k+1]['label']+f'#{k+1}',i0=int(i0),i1=int(i1),**st))
  for s in range(i0+1,i1+1):lab[s]=f'{k}->{k+1}'
  dw=DWELL.get((obj,KF[k+1]['label']),0.)
  if dw:segs.append(dict(cls='dwell',frm=KF[k+1]['label']+f'#{k+1}',to=KF[k+1]['label']+f'#{k+1}',i0=int(i1),i1=int(i1),states=0,time_s=dw))
 for a in r['approaches']:   # empty gripper, jaws open, 6 cm along the grasp approach axis (+ grasp / release 0.8 s)
  segs.append(dict(cls='approach',frm=KF[a['kf']]['label']+f"#{a['kf']}",to='pre-grasp',states=7,time_s=a['time_s'],min_reserve_mm=a['min_reserve_mm']))
 segs.append(dict(cls='gripper',frm='grasp+release',to='',states=0,time_s=2*GRASP_S))
 tsum=sum(s['time_s'] for s in segs)
 # identical states inside the chain (a path planned twice, e.g. out and back from the same anchor)
 keys=[tuple(np.round(q[:9],6)) for q in P];cnt=collections.Counter(keys)
 rep=sum(v-1 for v in cnt.values() if v>1)
 return dict(name=name,file=fn,act=r['act'],obj=obj,grasp_sense=sign,ok=r['ok'],time_s=r['time_s'],time_recomputed_s=round(tsum,1),elapsed_s=r['elapsed_s'],
  play_states=N,approach_states=sum(len(q) for q in r['approach_qs'] if q),anchors=len(A),meets=len(M),keyframes=nk,
  candidates_followed=len(r['tries']),min_reserve_mm=r['min_reserve_mm'],max_pgc_moment_Nm=r.get('max_pgc_moment_Nm'),max_joint_ratio=r.get('max_joint_ratio'),
  repeated_states_in_chain=int(rep),start_state=np.round(P[0],4).tolist(),end_state=np.round(P[-1],4).tolist(),
  start_equals_end=bool(np.allclose(P[0],P[-1],atol=1e-9)),segments=segs),keys,lab,dict(obj_p=np.round(PO,4).tolist(),tcp_p=np.round(PT,4).tolist())
res={};keysets={};labels={};poses={}
for n,fn in CHAINS.items():
 a,ks,lab,po=analyse(n,fn);res[n]=a;keysets[n]=ks;labels[n]=lab;poses[n]=po
 print(n,'states',a['play_states'],'time',a['time_s'],'recomputed',a['time_recomputed_s'],'elapsed',a['elapsed_s'],'repeated',a['repeated_states_in_chain'],flush=True)
# ---- the R15 stir cycle (no saved states; counts from r15stirwalk2.py's parameters) ----
sw=json.load(open('results/r15/stirwalk2_h_scrape_dice_r17.json'));best=[a for a in sw['attempts'] if a['ok']][0]
P_B,DT=sw['period_bench_s'],.01;work_states=len(np.arange(0,.76*P_B+1e-9,DT))
st_segs=[]
for s in best['strokes']:
 if s.get('ret_into'):st_segs.append(dict(cls='stroke_return',stroke=s['stroke'],states=39,checked_points=39,max_joint_deg=s['ret_into']['max_joint_deg'],time_s=s['ret_into']['time_s']))
 if s.get('work'):st_segs.append(dict(cls='stroke',stroke=s['stroke'],states=work_states,time_s=round(.76*P_B*sw['working_slowdown'],2),vmax_degps=max(s['work']['vmax']),min_reserve_mm=s['work']['min_reserve_mm'],min_plume_mm=s['work']['min_plume_mm']))
stir=dict(name='stir_cycle',file='results/r15/stirwalk2_h_scrape_dice_r17.json',keys=sw['keys'],strokes=sum(1 for s in st_segs if s['cls']=='stroke'),
 period_s=sw['feasible_period_s'],cycle_time_s=round(sw['feasible_period_s']*5,2),states=sum(s['states'] for s in st_segs),min_reserve_mm=sw['min_reserve_mm'],min_plume_mm=sw['min_plume_mm'],
 attempts=len(sw['attempts']),elapsed_s=None,note='elapsed_s not saved by r15stirwalk2.py; the 80 stroke-start poses were solved before by r15reach.py (96-start IK each)',segments=st_segs)
hand=dict(name='spatula_handoff',source='README_R10 R18b: chain end -> R15 stir start, cart 7.8 cm, joints <= 11 deg, 0.5 s, min reserve 2.0 mm',cls='meet_join',time_s=.5)
# ---- the R16 dish carrier (pieces only; no play states saved) ----
car=json.load(open('results/r16/chain_plate_in_r17layout.json'))
carrier=dict(name='carrier_into_pot',file='results/r16/chain_plate_in_r17layout.json',time_s=car['time_s'],states=sum(p['steps'] for p in car['pieces']),min_reserve_mm=car['min_reserve_mm'],note='R16 format: no playback states saved; pieces only',pieces=car['pieces'])
# ---- per primitive class ----
cls=collections.OrderedDict()
def add(c,act,states,t):
 e=cls.setdefault(c,dict(count=0,states=0,time_s=0.,actions=set()));e['count']+=1;e['states']+=states;e['time_s']+=t;e['actions'].add(act)
MAIN=['wok_plate_rinse','faucet_open','lid_off_to_rack','spider_pot_to_plate','spatula_fetch']   # the distinct checked actions (plate2 is a variant of the wok one)
for n in MAIN:
 for s in res[n]['segments']:add(s['cls'],n,s['states'],s['time_s'])
for s in st_segs:add(s['cls'],'stir_cycle',s['states'],s['time_s'])
add('meet_join','spatula_handoff',0,.5)
tot_states=sum(e['states'] for e in cls.values());tot_t=sum(e['time_s'] for e in cls.values())
classes={c:dict(count=e['count'],states=e['states'],state_share=round(e['states']/tot_states,3),time_s=round(e['time_s'],1),time_share=round(e['time_s']/tot_t,3),
 n_actions=len(e['actions']),actions=sorted(e['actions']),contact_or_process=c in CONTACT) for c,e in cls.items()}
shared=[c for c,e in classes.items() if e['n_actions']>=3];bespoke=[c for c,e in classes.items() if e['n_actions']==1]
summary_cls=dict(total_states=tot_states,total_time_s=round(tot_t,1),
 shared_classes=shared,shared_state_share=round(sum(classes[c]['states'] for c in shared)/tot_states,3),shared_time_share=round(sum(classes[c]['time_s'] for c in shared)/tot_t,3),
 bespoke_classes=bespoke,bespoke_state_share=round(sum(classes[c]['states'] for c in bespoke)/tot_states,3),bespoke_time_share=round(sum(classes[c]['time_s'] for c in bespoke)/tot_t,3))
# ---- literal reuse: identical states between the two wok chains (plate spot x .43 vs .17) ----
def shared_states(a,b):
 sb=set(keysets[b]);n=sum(1 for k in keysets[a] if k in sb);return n
w1,w2='wok_plate_rinse','wok_plate2_rinse';same=shared_states(w2,w1)
segsame=[];PA,PB=np.array(json.load(open(CHAINS[w1]))['play']),np.array(json.load(open(CHAINS[w2]))['play'])
for s1,s2 in zip(res[w1]['segments'],res[w2]['segments']):
 if 'i0' not in s2:continue
 ks=set(keysets[w1]);sub=keysets[w2][s2['i0']+1:s2['i1']+1];e=dict(seg=f"{s2['frm']}->{s2['to']}",cls=s2['cls'],states=len(sub),identical=sum(1 for k in sub if k in ks))
 qa,qb=PA[s1['i0']:s1['i1']+1],PB[s2['i0']:s2['i1']+1]
 if len(qa)==len(qb):   # same arm motion with the cart shifted? (a primitive that only moves along the rail)
  e['max_arm_joint_diff_deg']=round(float(np.degrees(np.abs(wrap(qa[:,3:9]-qb[:,3:9]))).max()),4);e['cart_shift_m']=[round(float((qb[:,0]-qa[:,0]).min()),3),round(float((qb[:,0]-qa[:,0]).max()),3)]
 segsame.append(e)
carries=[s for n in MAIN for s in res[n]['segments'] if s['cls']=='carry']
cart_dom=[s for s in carries if s['joint_path_deg']<10.]
summary_cls['carry_cart_dominant']=dict(note='carry segments whose arm joints move < 10 deg in total: the cart carries the object, the arm keeps its posture',
 count=len(cart_dom),of=len(carries),time_s=round(sum(s['time_s'] for s in cart_dom),1),of_time_s=round(sum(s['time_s'] for s in carries),1))
reuse=dict(
 plate_spot_2=dict(note='R18: the whole wok chain was re-planned for plating 26 cm further left (elapsed_s 279) although only the plate segments change',
  states=res[w2]['play_states'],identical_to_spot1=same,identical_share=round(same/res[w2]['play_states'],3),elapsed_s=res[w2]['elapsed_s'],per_segment=segsame),
 within_chain={n:dict(states=res[n]['play_states'],repeated=res[n]['repeated_states_in_chain'],share=round(res[n]['repeated_states_in_chain']/res[n]['play_states'],3),start_equals_end=res[n]['start_equals_end']) for n in MAIN},
 reversed_actions=dict(faucet_close='faucet_open reversed (r17seq.py: 2 x lever_s)',lid_on='lid_off_to_rack reversed',spatula_stow='spatula_fetch reversed (r17seq.py: 2 x spat)',carrier_out='carrier_into_pot reversed (arm_checked.json plate_out)'))
# ---- compute spent: every saved R17/R18 chain run, grouped by action ----
hist=collections.OrderedDict()
for f in sorted(glob.glob('results/r17/chain_*.json')):
 r=json.load(open(f));h=hist.setdefault(r['act'],dict(saved_runs=0,ok_runs=0,elapsed_s=0.,ok_elapsed_s=0.))
 h['saved_runs']+=1;h['ok_runs']+=bool(r['ok']);h['elapsed_s']+=r.get('elapsed_s') or 0.;h['ok_elapsed_s']+=(r.get('elapsed_s') or 0.) if r['ok'] else 0.
effort=dict(final_chains={n:dict(elapsed_s=res[n]['elapsed_s'],play_states=res[n]['play_states'],time_s=res[n]['time_s'],elapsed_per_motion_s=round(res[n]['elapsed_s']/res[n]['time_s'],1),candidates_followed=res[n]['candidates_followed']) for n in CHAINS},
 all_saved_runs=hist,all_saved_elapsed_h=round(sum(h['elapsed_s'] for h in hist.values())/3600,2),
 note='only the last run per file name is saved, so the history is a lower bound; R15/R16 runs (stir reach, r16chain) did not save elapsed_s')
out=dict(source='r19prim_inventory.py',chains=res,stir_cycle=stir,spatula_handoff=hand,carrier=carrier,classes=classes,class_summary=summary_cls,reuse=reuse,effort=effort)
def ser(o):
 if isinstance(o,set):return sorted(o)
 if isinstance(o,(np.floating,np.integer)):return o.item()
 raise TypeError(type(o))
json.dump(out,open(f'{OUT}/inventory.json','w'),indent=1,default=ser)
json.dump(dict(labels=labels,poses=poses),open(f'{OUT}/segments.json','w'),default=ser)
print(json.dumps(dict(classes={c:{k:v for k,v in e.items() if k!='actions'} for c,e in classes.items()},summary=summary_cls),default=ser,indent=0))
print('plate spot 2 identical states',same,'of',res[w2]['play_states'])
print({a:{k:round(v) for k,v in h.items()} for a,h in hist.items()})
