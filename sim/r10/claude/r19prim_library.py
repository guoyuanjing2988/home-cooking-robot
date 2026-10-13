"""R19 motion library: schema, four movement sets encoded from the checked data, two sets composed only
from already-verified segments, the plating sequence joined at hub states, and the library size for
meals A/B/C (meal16.py ARM=r18). Reads results/r19/prim/inventory.json, segments.json, swept.json,
transit.json (r19prim_inventory.py, r19prim_swept.py, r19prim_transit.py) and the R17/R18 chains.
New checks done here (unchanged checker, as r17chain.py):
 - per-segment clearance reserve of the encoded sets (full check every 5th state and at segment ends):
   the tolerance budget of each primitive beyond the 10 mm / 5 mm gaps;
 - WOK_DUMP (no plating) and WOK_FILL (1 L taken at the running tap, nothing emptied) are the verified
   wok chain with its tip loops left out. The states before and after a tip loop differ by <= 0.04 deg,
   so the splice is a micro-join, checked here; FILL carries 1.0 kg of water from the tap back to the
   cooker, a load the chain never had there, so PGC moment and joint torque ratios are computed at every
   state of that part (r17chain.load() method; water CoM 2 cm above the wok bottom as r17chain's food).
Everything else (meal mapping, set catalogue, statuses) is a DESIGN PROPOSAL and marked so.
python r19prim_library.py -> results/r19/prim/schema.json, library_examples.json, library_size.json"""
import sys;sys.path.insert(0,'.')
import json,math,collections,numpy as np,mujoco
import chain
from scene import build
from checker import Checker
import kitchen15 as K15,kitchen16 as K,kitchen17 as K17
K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.)
BASE=dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True)
OUT='results/r19/prim';QW=60.
inv=json.load(open(f'{OUT}/inventory.json'));sw=json.load(open(f'{OUT}/swept.json'));tr=json.load(open(f'{OUT}/transit.json'))
CH=dict(wok='results/r17/chain_wok_s-1_final.json',wok2='results/r17/chain_wok_s-1_r18plate2b.json',lever='results/r17/chain_lever_s+1_final.json',lid='results/r17/chain_lid_s-1_final.json',
 spider='results/r17/chain_spider_s+1_final.json',spatula='results/r17/chain_spatula_s-1_r18roll-1.15_.30.json')
INV=dict(wok='wok_plate_rinse',wok2='wok_plate2_rinse',lever='faucet_open',lid='lid_off_to_rack',spider='spider_pot_to_plate',spatula='spatula_fetch')
R={k:json.load(open(f)) for k,f in CH.items()}
CONTACT={'approach','seat_lift','seat_lower','insert','extract','lever','stroke'};PROCESS={'tip','untip','dwell','gripper'}
def rq(q,n=5):return [round(float(v),n) for v in q]
def model(r,extra=None):
 for k,v in r.get('tool_xy',{}).items():K.TOOL_XY[k]=tuple(v)
 if r['obj']=='wok':K17.set_wok_tilt(r.get('wok_tilt',0.))
 cfg=chain.chain_cfg('SD',**{**BASE,**r.get('scene',{}),**(extra or {}),**K17.held_cfg(r['obj'],r['grasp_sense'])});tree,meta=build(cfg,None);return Checker(tree,meta)
def reserve(ch,q):
 c=ch.check(np.asarray(q,float),full=True,mass=0.);return min((v['reserve_mm'] for cat,v in c['clearance'].items() if cat!='self'),default=None),[h['pair'] for h in c['hits']]
# =================== 1. schema ===================
schema={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'r19-motion-library','title':'R19 home cooking robot motion library',
 'description':'recipe step -> task -> movement set -> primitive -> controller command. Every set starts and ends at a hub state; sets join only at identical hub states, so a sequence of sets needs no new geometric check. Verification is offline, per primitive and per set, with the unchanged checker.',
 '$defs':{
  'State':{'type':'array','items':{'type':'number'},'minItems':11,'maxItems':11,'description':'cart x (m), base y, base yaw, 6 UR5e joints (rad, winding kept), 2 jaw openings (m)'},
  'Hub':{'type':'object','required':['id','hand','q','station'],'properties':{
   'id':{'type':'string'},'hand':{'enum':['empty','wok','spatula','spider','lid','carrier','cup','basket','lever']},'station':{'type':'string'},
   'q':{'$ref':'#/$defs/State'},'match_tol':{'type':'object','properties':{'joint_deg':{'type':'number'},'cart_mm':{'type':'number'}},'description':'runtime: the measured state must be within this of q before a set may start (default 0.05 deg / 0.5 mm)'},
   'object_pose':{'type':'object','description':'held object or target pose at the hub (p, R) for runtime cross-checks'},
   'source':{'$ref':'#/$defs/Source'}}},
  'Source':{'type':'object','properties':{'file':{'type':'string'},'play':{'type':'array','items':{'type':'integer'},'minItems':2,'maxItems':2,'description':'state index range in the file playback'},'approach':{'type':'array'},'keyframes':{'type':'array','items':{'type':'string'}}}},
  'Primitive':{'type':'object','required':['id','class','trajectory','verification'],'properties':{
   'id':{'type':'string'},'class':{'enum':['approach','seat_lift','seat_lower','carry','insert','extract','reorient','tip','untip','lever','stroke','stroke_return','meet_join','transit','dwell','gripper']},
   'params':{'type':'object','description':'named parameters with their verified range/grid, e.g. {"cart_shift_m":{"verified":[0,-0.26]}}'},
   'trajectory':{'type':'object','properties':{'states':{'type':'array','items':{'$ref':'#/$defs/State'}},'source':{'$ref':'#/$defs/Source'},'reversible':{'type':'boolean'},
     'timing':{'type':'object','properties':{'law':{'enum':['per_step_limits','jerk_limited_along_path','servo_dense']},'tcp_mps':{'type':'number'},'deg_per_s':{'type':'number'},'joint_degps':{'type':'number'},'cart_mps':{'type':'number'}}}}},
   'contact_window':{'type':'boolean','description':'slow, straight, no blending; only the named intended contacts allowed (DECISIONS 2026-10-08)'},
   'blend':{'type':'object','properties':{'allowed':{'type':'boolean'},'max_path_deviation_mm':{'type':'number','description':'<= min clearance reserve of the segment minus tracking error'}}},
   'load':{'type':'object','properties':{'held_kg':{'type':'number'},'max_pgc_moment_Nm':{'type':'number'},'max_joint_ratio':{'type':'number'}}},
   'verification':{'$ref':'#/$defs/Verification'},'monitors':{'type':'array','items':{'$ref':'#/$defs/Monitor'}}}},
  'Verification':{'type':'object','required':['status'],'properties':{
   'status':{'enum':['verified','composed_from_verified','partially_verified','not_verified']},'checker':{'type':'string'},'gaps_mm':{'type':'object'},'step_bound':{'type':'string'},
   'min_reserve_mm':{'type':['number','null']},'scene_version':{'type':'string','description':'hash of the fixture layout the check ran in'},'swept_volume':{'type':'string','description':'voxel set key (2 cm) for layout-change screening'},
   'fixture_dependencies':{'type':'array','items':{'type':'string'}},'param_grid':{'type':'object'},'elapsed_s':{'type':['number','null']},'evidence':{'type':'string'}}},
  'Condition':{'type':'object','required':['name','check'],'properties':{'name':{'type':'string'},'check':{'type':'string','description':'how it is established at runtime: sensor or state flag'},'on_false':{'type':'string'}}},
  'Monitor':{'type':'object','properties':{'signal':{'type':'string'},'nominal':{'description':'recorded during verification / commissioning'},'limit':{},'action':{'enum':['slow','pause','retreat_to_hub','stop','protective_stop']}}},
  'MovementSet':{'type':'object','required':['id','start_hub','end_hub','steps','pre','post','verification'],'properties':{
   'id':{'type':'string'},'params':{'type':'object'},'start_hub':{'type':'string'},'end_hub':{'type':'string'},
   'pre':{'type':'array','items':{'$ref':'#/$defs/Condition'}},'post':{'type':'array','items':{'$ref':'#/$defs/Condition'}},
   'steps':{'type':'array','items':{'type':'object','properties':{'primitive':{'type':'string'},'reverse':{'type':'boolean'},'params':{'type':'object'},'io':{'type':'string','description':'gripper / cooker / drum command at this point'}}}},
   'reverse_of':{'type':'string'},'time_s':{'type':'number'},'stops':{'type':'integer','description':'velocity zeros (contact windows, dwells, gripper)'},
   'on_failure':{'type':'object','description':'per step: where to retreat (a hub or the last safe state) and what to report'},'verification':{'$ref':'#/$defs/Verification'}}},
  'Task':{'type':'object','properties':{'id':{'type':'string'},'sets':{'type':'array','items':{'type':'string'}},'resources':{'type':'array'}}},
  'RecipeStep':{'type':'object','properties':{'dish':{'type':'string'},'label':{'type':'string'},'tasks':{'type':'array'},'heat':{'type':'object'},'wait_s':{'type':'number'},'end_cue':{'type':'string'}}}},
 'type':'object','properties':{'hubs':{'type':'array','items':{'$ref':'#/$defs/Hub'}},'primitives':{'type':'array','items':{'$ref':'#/$defs/Primitive'}},'sets':{'type':'array','items':{'$ref':'#/$defs/MovementSet'}}}}
json.dump(schema,open(f'{OUT}/schema.json','w'),indent=1,ensure_ascii=False)
# =================== 2. primitives from the chains ===================
def prims_of(key,ch,check_reserve=True):
 r=R[key];P=np.array(r['play']);segs=inv['chains'][INV[key]]['segments'];out=[]
 for s in segs:
  pid=f"{INV[key]}.{s['cls']}.{len(out)}";e=dict(id=pid,**{'class':s['cls']},time_s=s['time_s'],states=s['states'],contact_window=s['cls'] in CONTACT)
  if 'i0' in s:
   e['trajectory']=dict(source=dict(file=CH[key],play=[s['i0'],s['i1']],keyframes=[s['frm'],s['to']]),start=rq(P[s['i0']]),end=rq(P[s['i1']]))
   if check_reserve and s['i1']>s['i0']:
    idx=sorted(set(list(range(s['i0'],s['i1']+1,5))+[s['i0'],s['i1']]));rs=[reserve(ch,P[i]) for i in idx]
    e['min_reserve_mm']=round(min(x[0] for x in rs),1);assert not any(x[1] for x in rs),(pid,[x[1] for x in rs if x[1]])
  elif s['cls']=='approach':e['trajectory']=dict(source=dict(file=CH[key],approach=s['frm']));e['min_reserve_mm']=s.get('min_reserve_mm')
  e['blend']=dict(allowed=s['cls'] in ('carry','meet_join','reorient','transit'),max_path_deviation_mm=max(0.,round(e.get('min_reserve_mm',0.) or 0.,1)-1.) if s['cls'] in ('carry','meet_join','reorient') else 0.)
  out.append(e)
 return out
models={k:model(R[k]) for k in ('wok','lever','lid','spatula')}
PR={k:prims_of(k,models[k]) for k in ('wok','lever','lid','spatula')}
print('reserves done',flush=True)
def hub(id_,hand,station,q,src):return dict(id=id_,hand=hand,station=station,q=rq(q),match_tol=dict(joint_deg=.05,cart_mm=.5),source=src)
W,L,LI,S=R['wok'],R['lever'],R['lid'],R['spatula']
H=[hub('H_wok_pre','empty','cooker (wok on it)',W['approach_qs'][0][-1],dict(file=CH['wok'],approach='pick#0 (6 cm back, jaws open)')),
   hub('H_fau_closed_pre','empty','faucet (lever closed)',L['approach_qs'][0][-1],dict(file=CH['lever'],approach='closed#0')),
   hub('H_fau_open_post','empty','faucet (lever open)',L['approach_qs'][1][-1],dict(file=CH['lever'],approach='open#1')),
   hub('H_lid_on_pre','empty','zone-2 pot (lid on)',LI['approach_qs'][0][-1],dict(file=CH['lid'],approach='lift off#0')),
   hub('H_lid_rack_post','empty','lid rack (lid in it)',LI['approach_qs'][1][-1],dict(file=CH['lid'],approach='in the rack#8')),
   hub('H_spat_pre','empty','spatula rest (-1.15, 0.30), flipped',S['approach_qs'][0][-1],dict(file=CH['spatula'],approach='pick#0')),
   hub('H_spat_stroke','spatula','wok, stroke start (before the 0.5 s hand-off)',S['play'][-1],dict(file=CH['spatula'],play=[len(S['play'])-1]*2,keyframes=['stroke start#5'])),
   dict(id='H_stir0',hand='spatula',station='wok, R15 stroke-0 start',q=None,note='verified (README_R10 R18b hand-off; r15stirwalk2 SCENE=r17) but its state is NOT saved: r15stirwalk2.py writes no joint states. Must be stored before the stir cycle can be a library entry.')]
wa=np.array(W['approach_qs']);eq_wok=bool(np.array_equal(wa[0],wa[1]))
# =================== 3. sets from the chains ===================
STOP={'approach','gripper','dwell','seat_lift','seat_lower','insert','extract','lever'}   # velocity zero at both ends (contact windows, dwells, gripper)
def stops(ps):
 """play order: approach (in), grasp, chain segments, release, approach (out). Today every boundary is a velocity zero
 (keyframe moves, joins at 0.6 s each); with blends only boundaries next to a STOP class are."""
 ap=[p for p in ps if p['class']=='approach'];body=[p for p in ps if p['class'] not in ('approach','gripper')]
 seq=ap[:1]+[{'class':'gripper'}]+body+([{'class':'gripper'}]+ap[1:] if len(ap)>1 else [])
 return len(seq)+1,2+sum(1 for a,b in zip(seq,seq[1:]) if a['class'] in STOP or b['class'] in STOP)
def set_from(id_,key,start,end,pre,post,params=None,rev=None,extra=None):
 c=inv['chains'][INV[key]];ps=PR[key];st_today,stops_lib=stops(ps)
 return dict(id=id_,params=params or {},start_hub=start,end_hub=end,pre=pre,post=post,steps=[dict(primitive=p['id']) for p in ps],reverse_of=rev,time_s=c['time_s'],
  stops_today=st_today,stops_library=stops_lib,
  verification=dict(status='verified',checker='checker.py (binding R05 reference), 10 mm robot-env, 5 mm gripper/held-env, joint ranges',step_bound='object <= 1 cm / 2 deg per state; joins <= 1 deg; full bounds every 5th state',
   min_reserve_mm=c['min_reserve_mm'],max_pgc_moment_Nm=c['max_pgc_moment_Nm'],max_joint_ratio=c['max_joint_ratio'],elapsed_s=c['elapsed_s'],evidence=CH[key],
   swept_volume=f"swept_voxels.npz: {INV[key]}__*",fixture_dependencies=sorted(g for g,d in sw['fixture_dependency_detail'].items() if INV[key] in d)),**(extra or {}))
C=lambda n,chk,f='retreat to the start hub, report':dict(name=n,check=chk,on_false=f)
sets=[]
sets.append(set_from('FAUCET_OPEN','lever','H_fau_closed_pre','H_fau_open_post',
 [C('lever closed','faucet lever angle 0 (camera or the gripper at the block)'),C('hand empty','gripper open, force 0'),C('clip-on block present','camera / grasp width at closing')],
 [C('lever open 30 deg','water flowing: camera / sound; gripper released')],extra=dict(note='FAUCET_CLOSE = the same primitives reversed, H_fau_open_post -> H_fau_closed_pre (r17seq.py uses 2 x lever_s)')))
sets.append(set_from('WOK_PLATE_RINSE','wok','H_wok_pre','H_wok_pre',
 [C('wok on the cooker, keyed','cooker slot switch / camera'),C('heat off (power 0)','servo knob position'),C('food in wok <= 1.15 kg','cooker scale or recipe estimate'),C('plate in the guarded stand at spot','camera'),C('faucet open','FAUCET_OPEN done and water seen'),C('hand empty','gripper')],
 [C('wok back on the cooker, rinsed, empty','slot switch + camera'),C('dish on the plate','camera'),C('hand empty','gripper')],
 params=dict(spot=dict(values={'1':dict(plate_x=.43,cart_shift_m=0.),'2':dict(plate_x=.17,cart_shift_m=-.26)},verified=['1','2'],
  note='spot 2 (R18 chain_wok_s-1_r18plate2b) = spot 1 with the tip/untip arm motion identical (0.0000 deg) and the cart 0.26 m left; only the two carries to and from the plate change length (inventory.json reuse.plate_spot_2)')),
 extra=dict(start_equals_end=inv['chains']['wok_plate_rinse']['start_equals_end'],approach_equals_retreat=eq_wok)))
sets.append(set_from('LID_OFF_TO_RACK','lid','H_lid_on_pre','H_lid_rack_post',
 [C('lid on the zone-2 pot, tab to the front','camera'),C('rack slot free','camera / slot switch'),C('heat off or steam vented','zone-2 power level 0 for >= N s (steam on the fingers, not simulated)'),C('hand empty','gripper')],
 [C('lid upright in the rack','camera / rack switch'),C('hand empty','gripper')],extra=dict(note='LID_ON = reversed (R16: lid on = reverse)')))
sets.append(set_from('SPATULA_FETCH','spatula','H_spat_pre','H_spat_stroke',
 [C('spatula on its pad, flipped (sense -1)','camera: blade face up/down'),C('wok on the cooker','slot switch'),C('pour drum swung away except while stirring','drum servo state'),C('hand empty','gripper')],
 [C('spatula in hand, sense -1','grasp width + finger-root force'),C('blade 1 cm off the steel at stroke 0','camera / joint state at hub')],
 extra=dict(note='then the 0.5 s hand-off into H_stir0 (README_R10 R18b: cart 7.8 cm, joints <= 11 deg, no hits, reserve 2.0 mm); SPATULA_STOW = reversed')))
st=inv['stir_cycle']
sets.append(dict(id='STIR_CYCLE',params=dict(cycles='n >= 1 (13.15 s each)',stroke='h_scrape_dice (R15)'),start_hub='H_stir0',end_hub='H_stir0',
 pre=[C('spatula in hand, sense -1','grasp width + finger-root force'),C('heat <= half power while the spatula stops','cooker servo (R15 policy)'),C('person not within reach of the wok','presence sensor','pause (arm stops, heat to half)')],
 post=[C('spatula at stroke-0 start','joint state at hub')],steps=[dict(primitive=f"stir.{s['cls']}.{i}") for i,s in enumerate(st['segments'])],time_s=st['cycle_time_s'],stops_today=10,stops_library=0,
 verification=dict(status='partially_verified',evidence=st['file'],min_reserve_mm=st['min_reserve_mm'],min_plume_mm=st['min_plume_mm'],
  note='5 strokes + close checked in the current kitchen (feasible period 2.63 s, 184 deg/s peak). States not saved by r15stirwalk2.py: re-run with state output to store the trajectory; elapsed_s not recorded. Stroke force: contact p95 6-8 N, grip moment p95 2.2-2.9 N.m (R15 rigid-dice bench); real food untested.')))
# =================== 4. sets composed only from verified segments: WOK_DUMP, WOK_FILL ===================
ch=models['wok'];m,d=ch.m,ch.d;P=np.array(W['play']);seg={(s['frm'],s['to']):s for s in inv['chains']['wok_plate_rinse']['segments'] if 'i0' in s}
def idx(lbl):return [s for s in inv['chains']['wok_plate_rinse']['segments'] if s.get('to')==lbl and s['cls']!='meet_join'][0]['i1']
i4,i6,i9,i11=idx('over the plate#4'),idx('level#6'),idx('forward#9'),idx('level#11')
def microjoin(a,b):
 qa,qb=P[a].copy(),P[b].copy();dq=np.degrees(np.abs((qb[3:9]-qa[3:9]+np.pi)%(2*np.pi)-np.pi)).max();n=max(2,int(math.ceil(dq/.01)))
 res=[reserve(ch,qa+(qb-qa)*k/n) for k in range(n+1)]
 return dict(frm=a,to=b,max_joint_deg=round(float(dq),4),cart_mm=round(float(abs(qb[0]-qa[0])*1000),2),states=n+1,ok=not any(x[1] for x in res),min_reserve_mm=round(min(x[0] for x in res),1),time_s=round(dq/QW,3))
mj_plate,mj_sink=microjoin(i4,i6),microjoin(i9,i11)
MASS=[(1.5,np.array([0,0,.045])),(.3,(K15.HANDLE['root']+K15.HANDLE['end'])/2-K15.WOK0)];sid=m.site('R_prep').id;T=np.asarray(K.T_tool_obj('wok',-1),float)
def load(q,extra_kg):
 d.qpos[:]=q;d.qvel[:]=0;mujoco.mj_forward(m,d);pt=d.site_xpos[sid].copy();Rt=d.site_xmat[sid].reshape(3,3);Ro=Rt@T[:3,:3];po=pt+Rt@T[:3,3]
 parts=MASS+[(extra_kg,np.array([0,0,.02]))];mass=sum(x for x,_ in parts);com=po+Ro@(sum(x*c for x,c in parts)/mass)
 jp=np.zeros((3,m.nv));jr=jp.copy();mujoco.mj_jac(m,d,jp,jr,com,m.site_bodyid[sid]);tau=d.qfrc_bias-jp.T@np.array([0,0,-mass*9.81])
 return max(float(abs(tau[ch.da[n]])/v) for n,v in ch.env.items()),float(np.linalg.norm(np.cross(com-pt,[0,0,-mass*9.81])))
i8=idx('under the tap#8');water=[load(P[i],1.0) for i in list(range(i8,i9+1))+list(range(i11,len(P)))]
food_ref=[load(P[i],1.15) for i in range(0,i4+1)]
segs_w=[s for s in inv['chains']['wok_plate_rinse']['segments']]
def tsum(excl):return round(sum(s['time_s'] for s in segs_w if not any(s.get('frm','').startswith(e) and s['cls'] in ('tip','untip','dwell') for e in excl) and not (s['cls']=='dwell' and any(s['frm'].startswith(e) for e in excl))),1)
t_dump=round(tsum(['over the plate#4','tipped 90 (plated)#5'])+mj_plate['time_s'],1)
t_fill=round(tsum(['over the plate#4','tipped 90 (plated)#5','forward#9','emptied#10'])+mj_plate['time_s']+mj_sink['time_s'],1)
comp=dict(status='composed_from_verified',evidence=CH['wok'],note='all states are states of the verified wok chain; the only new geometry is the micro-join where a tip loop is left out (checked here)',
 micro_joins=dict(plate=mj_plate,sink=mj_sink))
sets.append(dict(id='WOK_DUMP_RINSE',start_hub='H_wok_pre',end_hub='H_wok_pre',params={},pre=[C('wok on the cooker','slot switch'),C('heat off','servo'),C('faucet open','FAUCET_OPEN done')],post=[C('wok back, rinsed, empty','slot switch + camera')],
 steps=[dict(primitive='WOK_PLATE_RINSE steps without tip#4-5, dwell 2 s, untip#5-6'),dict(primitive='micro-join play %d -> %d'%(i4,i6))],time_s=t_dump,verification=comp,
 meal_estimate_s=json.load(open('results/r18/arm18.json'))['arm_s']['dump'],note='meal16 dump = 73.5 s (r17seq estimate incl. faucet and free moves); the wok part alone is this time_s'))
sets.append(dict(id='WOK_FILL',start_hub='H_wok_pre',end_hub='H_wok_pre',params=dict(water_l=dict(max=1.0,verified=[1.0]),fill_dwell_s=dict(value=5.,note='= V / faucet flow; the flow of the user\'s faucet is not measured (the 5 s is the rinse dwell of the chain)')),
 pre=[C('wok on the cooker, empty','slot switch + camera'),C('faucet open','FAUCET_OPEN done')],post=[C('wok on the cooker with <= 1 L water','cooker scale / camera')],
 steps=[dict(primitive='WOK_PLATE_RINSE steps without both tip loops'),dict(primitive='micro-joins play %d -> %d and %d -> %d'%(i4,i6,i9,i11))],time_s=t_fill,
 verification=dict(**comp,load_with_1kg_water=dict(states=len(water),max_joint_ratio=round(max(w[0] for w in water),3),max_pgc_moment_Nm=round(max(w[1] for w in water),2),pgc_limit_Nm=7.,
  reference_food_1p15kg_pick_to_plate=dict(max_joint_ratio=round(max(f[0] for f in food_ref),3),max_pgc_moment_Nm=round(max(f[1] for f in food_ref),2)))),
 meal_estimate_s=json.load(open('results/r18/arm18.json'))['arm_s']['fill']))
print('dump',t_dump,'fill',t_fill,mj_plate,mj_sink,'water load',sets[-1]['verification']['load_with_1kg_water'],flush=True)
# spider: its out-and-back keyframes are identical states -> natural hubs (split for free)
sp=inv['chains']['spider_pot_to_plate'];Psp=np.array(R['spider']['play'])
def sidx(lbl,last=False):
 c=[s for s in sp['segments'] if s.get('to')==lbl and s['cls']!='meet_join'];return c[0]['i1']
pairs=[('lane#3','lane#15'),('over the pot#4','drain#6'),('lane middle#8','lane middle#14'),('#9','lane#13'),('over the plate#10','level again#12')]
spider_hubs=[dict(keyframes=[a,b],max_joint_diff_deg=round(float(np.degrees(np.abs((Psp[sidx(a)][3:9]-Psp[sidx(b)][3:9]+np.pi)%(2*np.pi)-np.pi)).max()),6),cart_diff_m=round(float(Psp[sidx(a)][0]-Psp[sidx(b)][0]),6)) for a,b in pairs]
# =================== 5. the plating sequence joined at hubs ===================
TR={t['transit']:t for t in tr['transits']};hq={h['id']:h['q'] for h in H}
def same(a,b):return a is not None and b is not None and np.allclose(a,b,atol=1e-9)
seq=[('SPATULA_STOW (reverse of SPATULA_FETCH)','H_spat_stroke','H_spat_pre',S['time_s']+.5,'verified'),
 ('TRANSIT rest_to_faucet','H_spat_pre','H_fau_closed_pre',TR['rest_to_faucet']['time_s'] or TR['rest_to_faucet']['estimate_s'],'verified' if TR['rest_to_faucet']['ok'] else 'NOT FOUND (estimate)'),
 ('FAUCET_OPEN','H_fau_closed_pre','H_fau_open_post',L['time_s'],'verified'),
 ('TRANSIT faucet_to_wok','H_fau_open_post','H_wok_pre',TR['faucet_to_wok']['time_s'] or TR['faucet_to_wok']['estimate_s'],'verified' if TR['faucet_to_wok']['ok'] else 'NOT FOUND (estimate)'),
 ('WOK_PLATE_RINSE(spot)','H_wok_pre','H_wok_pre',W['time_s'],'verified'),
 ('TRANSIT wok_to_faucet','H_wok_pre','H_fau_open_post',TR['wok_to_faucet']['time_s'] or TR['wok_to_faucet']['estimate_s'],'verified' if TR['wok_to_faucet']['ok'] else 'NOT FOUND (estimate)'),
 ('FAUCET_CLOSE (reverse)','H_fau_open_post','H_fau_closed_pre',L['time_s'],'verified'),
 ('TRANSIT faucet_to_rest','H_fau_closed_pre','H_spat_pre',TR['faucet_to_rest']['time_s'] or TR['faucet_to_rest']['estimate_s'],'verified' if TR['faucet_to_rest']['ok'] else 'NOT FOUND (estimate)'),
 ('SPATULA_FETCH','H_spat_pre','H_spat_stroke',S['time_s']+.5,'verified')]
Lq=[np.array(L['approach_qs'][i][-1]) for i in (0,1)];Wq=[np.array(W['approach_qs'][i][-1]) for i in (0,1)];Sq=np.array(S['approach_qs'][0][-1])
ENDS={   # (start state, end state) of each set, taken from the data (transits: r19prim_transit.py uses these same approach_qs ends)
 'SPATULA_STOW (reverse of SPATULA_FETCH)':(np.array(S['play'][-1]),Sq),'TRANSIT rest_to_faucet':(Sq,Lq[0]),'FAUCET_OPEN':(Lq[0],Lq[1]),'TRANSIT faucet_to_wok':(Lq[1],Wq[0]),
 'WOK_PLATE_RINSE(spot)':(Wq[0],Wq[1]),'TRANSIT wok_to_faucet':(Wq[0],Lq[1]),'FAUCET_CLOSE (reverse)':(Lq[1],Lq[0]),'TRANSIT faucet_to_rest':(Lq[0],Sq),'SPATULA_FETCH':(Sq,np.array(S['play'][-1]))}
junc=[dict(after=a[0],before=b[0],hub=a[2],identical=bool(np.array_equal(ENDS[a[0]][1],ENDS[b[0]][0]))) for a,b in zip(seq,seq[1:])]
plating=dict(steps=[dict(set=s[0],start=s[1],end=s[2],time_s=round(s[3],2),status=s[4]) for s in seq],junctions=junc,all_junctions_at_identical_hubs=all(j['identical'] for j in junc),
 time_s=round(sum(s[3] for s in seq),1),r17seq_estimate_s=json.load(open('results/r18/arm18.json'))['arm_s']['wok_plate'],
 unverified=[s[0] for s in seq if s[4]!='verified'],note='H_spat_stroke -> H_stir0 hand-off (0.5 s each way) is counted in the spatula times as in r17seq.py')
# =================== 6. library size for meals A/B/C (DESIGN PROPOSAL) ===================
# movement-set catalogue: status from the data where it exists; hubs each set needs
V,CV,PV,NV='verified','composed_from_verified','partially_verified','not_verified'
CAT={
 'FAUCET_OPEN':(V,['H_fau_closed_pre','H_fau_open_post']),'FAUCET_CLOSE':(V,['H_fau_open_post','H_fau_closed_pre']),
 'WOK_PLATE_RINSE':(V,['H_wok_pre']),'WOK_DUMP_RINSE':(CV,['H_wok_pre']),'WOK_FILL':(CV,['H_wok_pre']),'WOK_OIL_POUR':(NV,['H_wok_pre']),
 'SPATULA_FETCH':(V,['H_spat_pre','H_stir0']),'SPATULA_STOW':(V,['H_stir0','H_spat_pre']),'STIR_CYCLE_dice':(PV,['H_stir0']),'STIR_CYCLE_shreds_leafy':(NV,['H_stir0']),
 'SPIDER_FETCH':(V,['H_spider_pre','H_spider_lane']),'SPIDER_SCOOP_pot':(V,['H_spider_lane']),'SPIDER_SCOOP_wok':(NV,['H_spider_lane']),'SPIDER_SCOOP_fryer':(NV,['H_spider_lane']),
 'SPIDER_DUMP_plate':(V,['H_spider_lane']),'SPIDER_STOW':(V,['H_spider_lane','H_spider_pre']),
 'LID_OFF_pot':(V,['H_lid_on_pre','H_lid_rack_post']),'LID_ON_pot':(V,['H_lid_rack_post','H_lid_on_pre']),
 'LID_OFF_wok':(NV,['H_wlid_on_pre','H_wlid_rack_post']),'LID_ON_wok':(NV,['H_wlid_rack_post','H_wlid_on_pre']),
 'LID_OFF_stew':(NV,['H_slid_on_pre','H_slid_rack_post']),'LID_ON_stew':(NV,['H_slid_rack_post','H_slid_on_pre']),
 'CARRIER_IN':(V,['H_carrier_stage_pre','H_carrier_pot_post']),'CARRIER_OUT':(V,['H_carrier_pot_post','H_carrier_stage_pre']),'CARRIER_DRAIN':(NV,['H_carrier_pot_post']),
 'CUP_FETCH':(NV,['H_cup_station','H_cup_lane']),'CUP_POUR_wok':(NV,['H_cup_lane']),'CUP_POUR_stew':(NV,['H_cup_lane']),'CUP_POUR_plate':(NV,['H_cup_lane']),'CUP_POUR_fryer':(NV,['H_cup_lane']),'CUP_RETURN':(NV,['H_cup_lane','H_cup_station']),
 'DRUM_LOAD':(NV,['H_cup_station','H_drum']),'DRUM_UNLOAD':(NV,['H_drum','H_cup_station']),
 'STEW_CUP_IN':(NV,['H_stage_cups','H_stew_pre']),'STEW_CUP_OUT':(NV,['H_stew_pre','H_stage_cups']),
 'RICE_DOSE':(NV,['H_rice_port']),'RICE_WASH':(NV,['H_rice_port','H_fau_open_post']),'RICE_TO_COOKER':(NV,['H_rice_cooker']),'ARRANGE':(NV,['H_plate_spot'])}
# meal steps (labels of results/r16/meal_stew_r18.json) -> set instances, from the arm-time formulas in meal16.py (ARM=r18)
PL=dict(SPATULA_STOW=1,FAUCET_OPEN=1,WOK_PLATE_RINSE=1,FAUCET_CLOSE=1,SPATULA_FETCH=1)   # one wok_plate (r17seq.py plating sequence)
DU=dict(FAUCET_OPEN=1,WOK_DUMP_RINSE=1,FAUCET_CLOSE=1);FI=dict(FAUCET_OPEN=1,WOK_FILL=1,FAUCET_CLOSE=1)
SPI=lambda v:dict(SPIDER_FETCH=1,**{f'SPIDER_SCOOP_{v}':1},SPIDER_DUMP_plate=1,SPIDER_STOW=1)
def cup(t,n):return dict(CUP_FETCH=n,**{f'CUP_POUR_{t}':n},CUP_RETURN=n)
def stir(s,kind='dice'):return {f'STIR_CYCLE_{kind}':math.ceil(s/st['cycle_time_s'])}
def M(*ds):
 o=collections.Counter()
 for d_ in ds:o.update(d_)
 return dict(o)
MEALS={'A':[('桂花糖芋头','taro plate into the pot steamer, lid',M(dict(CARRIER_IN=1,LID_ON_pot=1))),('米饭','rice',M(dict(RICE_DOSE=1,RICE_WASH=1,RICE_TO_COOKER=1))),
  ('蛤蜊排骨盅','4 cups into the stew pot, lid',M(dict(STEW_CUP_IN=4,LID_ON_stew=1))),('干锅土豆','fry potato, lift out',M(cup('fryer',1),SPI('fryer'))),
  ('蚝油西兰花','oil, broccoli, sauce; lid 30 s; stir; plate',M(cup('wok',2),dict(LID_ON_wok=1,LID_OFF_wok=1),stir(26,'shreds_leafy'),PL)),
  ('干锅土豆','pork, 豆瓣, chili, potato, sauce; stir 90 s; plate',M(cup('wok',3),stir(117),PL)),
  ('蒜蓉蒸丝瓜','taro out (lid), luffa in, lid',M(dict(LID_OFF_pot=1,CARRIER_OUT=1,CARRIER_IN=1,LID_ON_pot=1))),
  ('蒜蓉蒸丝瓜','heat oil 60 s; pour over garlic bowl',M(cup('wok',1),dict(WOK_OIL_POUR=1))),('桂花糖芋头','drizzle syrup',M(cup('plate',1))),
  ('蒜蓉蒸丝瓜','luffa out (lid), pour sauce',M(dict(LID_OFF_pot=1,CARRIER_OUT=1),cup('plate',1)))],
 'B':[('红烧肉','wok to the tap 1 L; pork in; blanch 5 min; lift out',M(FI,cup('wok',1),SPI('wok'))),('鲜笋排骨汤','4 additions into the stew pot; lid',M(cup('stew',4),dict(LID_ON_stew=1))),
  ('红烧肉','wok emptied at the sink; fry, 糖色, sauce, water; lid; braise',M(DU,dict(SPATULA_FETCH=1,SPATULA_STOW=1),stir(195),cup('wok',5),dict(LID_ON_wok=1))),('米饭','rice',M(dict(RICE_DOSE=1,RICE_WASH=1,RICE_TO_COOKER=1))),
  ('清蒸鲈鱼','fish plate into the steamer, lid',M(dict(CARRIER_IN=1,LID_ON_pot=1))),('清蒸鲈鱼','fish out, pour off water, soy, shreds',M(dict(LID_OFF_pot=1,CARRIER_OUT=1,CARRIER_DRAIN=1),cup('plate',2))),
  ('红烧肉','lid off, reduce 3 min stirring, plate',M(dict(LID_OFF_wok=1,SPATULA_FETCH=1,SPATULA_STOW=1),stir(180),PL)),
  ('白灼汁','heat oil; over fish + garlic bowl; mix sauce',M(cup('wok',1),dict(WOK_OIL_POUR=2),cup('plate',3))),
  ('番茄炒蛋','oil, eggs, out; tomato, lid 30 s, eggs back; plate',M(cup('wok',5),dict(LID_ON_wok=1,LID_OFF_wok=1),stir(78),PL)),
  ('白灼秋葵娃娃菜','wok to the tap 1 L; oil, salt; boil',M(FI,cup('wok',2))),('鲜笋排骨汤','salt, celery',M(cup('stew',1))),
  ('白灼秋葵娃娃菜','blanch, lift out x2, arrange, sauce',M(cup('wok',2),SPI('wok'),SPI('wok'),dict(ARRANGE=1),cup('plate',1)))],
 'C':[('米饭','rice',M(dict(RICE_DOSE=1,RICE_WASH=1,RICE_TO_COOKER=1))),('芋头蒸排骨','plate into the steamer, lid',M(dict(CARRIER_IN=1,LID_ON_pot=1))),('青瓜肉片汤','ginger, cucumber into the stew pot',M(cup('stew',2))),
  ('青椒炒鱿鱼','aromatics, pepper, wine, squid, sauce; stir 60 s; plate',M(cup('wok',5),stir(78),PL)),('清炒荷兰豆','oil, garlic, peas, salt, water; stir 45 s; plate',M(cup('wok',3),stir(58.5,'shreds_leafy'),PL)),
  ('酸辣土豆丝','wok to the tap 1 L; boil; shreds in',M(FI,cup('wok',1))),('青瓜肉片汤','pork slices; salt',M(cup('stew',2))),
  ('酸辣土豆丝','blanch, lift out; wok emptied; stir-fry 45 s; plate',M(SPI('wok'),DU,cup('wok',3),stir(58.5,'shreds_leafy'),PL)),
  ('芋头蒸排骨','out (lid), chili, scallion, hot oil from the wok',M(dict(LID_OFF_pot=1,CARRIER_OUT=1),cup('plate',2),dict(WOK_OIL_POUR=1)))]}
# transits: hub-and-spoke (each station hub <-> its travel hub at the same cart x, travel hubs joined by cart-only moves with a fixed tucked posture)
size={};allsets=set();allhubs=set()
for k,steps in MEALS.items():
 c=collections.Counter()
 for _,_,dd in steps:c.update(dd)
 used=sorted(c);allsets|=set(used);hubs=sorted({h for s in used for h in CAT[s][1]});allhubs|=set(hubs)
 size[k]=dict(set_instances=sum(c.values()),distinct_sets=len(used),hubs=len(hubs),by_status={s_:sum(1 for x in used if CAT[x][0]==s_) for s_ in (V,CV,PV,NV)},
  instances_by_status={s_:sum(v for x,v in c.items() if CAT[x][0]==s_) for s_ in (V,CV,PV,NV)},counts=dict(c))
held_hubs={h for h in allhubs if any(t in h for t in ('lane','stir0','H_drum'))};station_hubs=allhubs-held_hubs
n_travel=6   # proposal: travel hubs (tucked posture) at cart x of the station clusters: spatula/prep end, sink, plate spots, wok, zone 2/stew, counter end
transits=len(station_hubs)+(n_travel-1)   # one spoke per empty-hand station hub + cart-only moves between neighbouring travel hubs (reverses free)
# primitive templates and segment count (verified sets: measured; others: the median verified set)
nseg={'FAUCET_OPEN':len(PR['lever']),'WOK_PLATE_RINSE':len(PR['wok']),'LID_OFF_pot':len(PR['lid']),'SPATULA_FETCH':len(PR['spatula']),'CARRIER_IN':5,
 'SPIDER_FETCH':6,'SPIDER_DUMP_plate':6,'STIR_CYCLE_dice':len(st['segments']),'WOK_DUMP_RINSE':1,'WOK_FILL':2}   # spider: its chain (25 segments) split at its identical hubs; carrier: R16 pieces; DUMP/FILL: only the micro-joins are new
REV={'FAUCET_CLOSE','LID_ON_pot','LID_ON_wok','LID_ON_stew','SPATULA_STOW','CARRIER_OUT','SPIDER_STOW','CUP_RETURN','STEW_CUP_OUT','DRUM_UNLOAD'}
med=int(np.median([len(PR[k]) for k in PR]+[len(sp['segments'])]))
nprim=sum(nseg.get(x,med) for x in allsets if x not in REV)
tot=dict(distinct_sets=len(allsets),reverse_only_sets=sum(1 for x in allsets if x in REV),
 by_status={s_:sorted(x for x in allsets if CAT[x][0]==s_) for s_ in (V,CV,PV,NV)},station_hubs=len(station_hubs),held_hubs=len(held_hubs),travel_hubs=n_travel,hubs_total=len(allhubs)+n_travel,
 transit_sets=transits,primitive_classes=len(inv['classes'])+1,primitive_segments_estimate=nprim+3*transits,primitive_segments_note='verified sets: their measured segment counts; others: the median verified set (%d); reversed sets add none; transits 3 each (depart, cart move, arrive)'%med,
 note='DESIGN PROPOSAL: the catalogue and the meal-to-set mapping follow meal16.py ARM=r18 arm-time formulas; statuses come from the data. Seasoning additions while stirring may come from the drum (R15) instead of arm pours; both are counted as cup pours here.')
# =================== 7. checking effort: today vs library (measured basis) ===================
eff=inv['effort'];fc=eff['final_chains'];ms=sw['replay_ms_per_state']
q_chosen=[q for q in sw['queries'] if 'flipped' in q['query']['name']][0];q_worst=max(sw['queries'],key=lambda q:q['screen_states'])
effort=dict(
 today=dict(new_action_final_run_elapsed_s={k:v['elapsed_s'] for k,v in fc.items()},all_saved_runs_elapsed_h=eff['all_saved_elapsed_h'],saved_runs=sum(h['saved_runs'] for h in eff['all_saved_runs'].values()),
  ok_runs=sum(h['ok_runs'] for h in eff['all_saved_runs'].values()),
  layout_change='re-plan every affected whole chain (R18 plate spot 2: %d s, although %d of %d states and the whole tip were identical) or replay every chain state (%d states x %.1f ms = %.0f s per candidate spot)'%(fc['wok_plate2_rinse']['elapsed_s'],inv['reuse']['plate_spot_2']['identical_to_spot1'],inv['reuse']['plate_spot_2']['states'],q_chosen['replay_states'],ms,q_chosen['replay_s']),
  free_moves='never checked (estimate |dx|/0.25 + 1 + 1.6 s)',runtime='sequence of whole actions + unchecked free moves'),
 library=dict(design_time='each set verified once with the same planner; a new set that reuses verified primitives needs only its new segments (WOK_DUMP/FILL here: %d + %d micro-join states and a load computation, no planning)'%(mj_plate['states'],mj_sink['states']),
  composition='0 geometric checks: consecutive sets meet at identical hub states (exact vector equality); %d of %d junctions in the plating sequence are identical hubs'%(sum(j['identical'] for j in junc),len(junc)),
  layout_change='swept-voxel screen %.0f ms per fixture, then replay only flagged segments: R18b spatula rest %d segments / %d states (%.1f s) instead of %d states (%.1f s) or a re-plan of all chains (%d s); worst query %d segments / %d states; 0 missed hits in %d queries'%(q_chosen['screen_ms'],q_chosen['flagged_segments'],q_chosen['screen_states'],q_chosen['screen_states']*ms/1000,q_chosen['replay_states'],q_chosen['replay_s'],sum(fc[k]['elapsed_s'] for k in ('wok_plate_rinse','wok_plate2_rinse','faucet_open','lid_off_to_rack','spider_pot_to_plate')),q_worst['flagged_segments'],q_worst['screen_states'],len(sw['queries'])),
  transits='verified once per hub pair: %d of 4 plating transits found as straight decoupled moves (%s); 2 need a planned path and better clearance hubs'%(sum(t['ok'] for t in tr['transits']),', '.join(f"{t['transit']} {t['time_s']} s" for t in tr['transits'] if t['ok'])),
  runtime='no geometric check; hub-state match, pre/post conditions, monitors'))
lib=dict(source='r19prim_library.py',schema='schema.json',hubs=H,primitives={k:v for k,v in PR.items()},sets=sets,spider_natural_hubs=spider_hubs,plating_sequence=plating)
json.dump(lib,open(f'{OUT}/library_examples.json','w'),indent=1,ensure_ascii=False)
json.dump(dict(source='r19prim_library.py',catalogue={k:dict(status=v[0],hubs=v[1]) for k,v in CAT.items()},meals=size,total=tot,effort=effort),open(f'{OUT}/library_size.json','w'),indent=1,ensure_ascii=False)
print(json.dumps(dict(plating={k:v for k,v in plating.items() if k!='steps'},meals={k:{x:y for x,y in v.items() if x!='counts'} for k,v in size.items()},total=tot),indent=1,ensure_ascii=False))
print(json.dumps(spider_hubs))
