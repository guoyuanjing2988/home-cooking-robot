"""R19 cart docking (GitHub #39): screens of the kitchen19dock hardware. New file; r19prep5_screen.py (and through it
r19prep4_screen.py / r19pot_screen.py) is imported for its scene builders, stored-path lists, sampling and exact
pair measurement and is not changed. Writes only to results/r19/dock/.

PART=travel   the cart's own travel (single process, static): with the cart at every x of its travel (R_carriage_x
              -1.48..2.46, step STEP m, default 5 mm; docked y -0.21 and y +-0.5 mm), the exact distance (checker
              distance.Bounds.pair: GJK dual lower bound; plane analytic) of
              (a) every CART geom (chassis, drive wheels, castors and their spindles, bumper, electrics, mast, beam and
                  the new dock parts) vs every FIXED dock part (rail, V track, scale, V-blocks, plinth angles, end stops);
              (b) every NEW cart dock part vs every environment geom (floor, cabinets, toe channel ...);
              except the declared contacts (V wheels on the V track; the seated pin on its V-block) and the running gap
              (read head over the scale, ride height). The criterion is a mechanical running clearance RUN (default
              5 mm [D]) for cart vs fixed parts; the read head must keep > 0 at its ride height.
              Also: PIN=down at every station (pin + nose vs every fixed part except its own V-block; the cart is stationary,
              so the requirement is no contact with STATIC = 1 mm margin), the V wheel /
              track geometry, the travel ends vs the end buffers.
PART=arm      every adopted stored path replayed (as r19prep5_screen: 2pi-unwrapped, joint-linear, <= 4 mm; pot-zone
              layer RACK=keyed SPX 1.56 SPY 0.20) with the dock parts in its scene; only the pairs (moving robot / held
              geom) x (dock part) are measured, exactly; gate = distance - the checker's required gap (ch.required:
              10 mm arm / 5 mm gripper + held vs the fixed parts; 10 mm arm vs a CART part). Paths: KINDS=prep,play,app,
              edge,other,stir (default all): the cooking chains + approaches, the 22 hub edges, the cup chains, the stir
              cycle, the 10 certified prep sets of r19prep5_screen + fold / unfold / stgwok (SETS= to override).
python r19dock_screen.py PART=travel [STEP=.005] [RUN=.005] ARM=ur5e_enc2_pgc PY=.15
python r19dock_screen.py PART=arm [PIN=up|down] [KINDS=..] [WORKERS=16] [TLIM=280] [TAG=..] ARM=ur5e_enc2_pgc PY=.15
 -> results/r19/dock/screen_travel.json, results/r19/dock/screen_arm[_<PIN>][_<TAG>].json"""
import sys,os,json,time
sys.path.insert(0,'.')
import numpy as np
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a);PART=KV.get('PART','travel')
OUT='results/r19/dock'
DOCK_SETS=['results/r19/prep5/chain_fold_full_ur5e_enc2_pgc.json','results/r19/prep5/chain_unfold_full_ur5e_enc2_pgc.json','results/r19/prep4/chain_stgwok_m5_ur5e_enc2_pgc.json']
def dock_cfg():return dict(r19dock=dict(pin=KV.get('PIN','up')))
PREFIX=('R_cart_dock_','dock_')
# ---------------------------------------------------------------- arm-path screen: r19prep5_screen with the dock parts
if PART=='arm':
 _argv=sys.argv;sys.argv=[sys.argv[0],'MODE=dock']+[a for a in _argv[1:] if not a.startswith('MODE=')]
 import r19prep5_screen as P5S;sys.argv=_argv
 P5S.OUT=OUT
 if 'SETS' not in KV:P5S.SETS=list(P5S.SETS)+DOCK_SETS
 P5S.KV.setdefault('ENV','0')   # environment pairs of the fixed dock parts (rail on the floor, angles on the plinth) are PART=travel's job
 def parts_cfg():return dock_cfg(),PREFIX
 def add_parts(tree):
  import kitchen19dock as D
  D.add(tree,dock_cfg());D.mesh(tree);return PREFIX
 P5S.parts_cfg=parts_cfg;P5S.add_parts=add_parts;P5S.S4.my_parts=add_parts
 def prep_scene(R,key):
  """a stored prep set's own scene, exactly as r19prep5_screen.prep_scene builds it (its own T2L / fold state kept), plus
  the dock parts."""
  import chain
  from scene import build
  from checker import Checker
  import kitchen16 as K,kitchen17 as K17,kitchen19 as K19,kitchen19p3 as P3,kitchen19p4 as P4
  names=[R['obj']]+[o[0] for o in (R['scene'].get('r19') or {}).get('objs',[])]+[o[0] for g in R.get('grasps',[]) for o in ((g['world'].get('r19') if 'r19' in g['world'] else g['world']) or {}).get('objs',[])]
  P3.ensure([n for n in names if not str(n).startswith(('dbh_','stg_p','fold_'))]);P4.ensure([n for n in names if not str(n).startswith('fold_')])   # as r19prep5_verify
  import kitchen19p5 as P5;P5.ensure(names)
  if R['obj'].startswith('pusher_y'):K19.pusher_turned(float(R['obj'][8:]))
  K.TOOL_XY['spatula']=(-1.15,.30);K.SPAT_ELEV,K.SPAT_YAW,K.SPAT_ROLL=8.,0.,180.
  K19.LAYOUT.update({k:(tuple(v) if isinstance(v,list) and k!='drop_bowls' else v) for k,v in R['layout'].items()})
  BASE=dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None},r14_fridge=True,r17_lever=0.,**K19.base_cfg())
  if key=='play':extra=K17.held_cfg(R['obj'],R['grasp_sense']);wo=None
  else:
   g=R['grasps'][key];kf=R['keyframes'][g['kf']];extra=g['world'] if 'r19' in g['world'] else dict(r19=g['world'])
   seat=kf.get('seat',.008 if R['obj'] in ('carrot','tomato') else 0.);wo=[R['obj'],kf['R'],(np.array(kf['p'])-[0,0,seat]).tolist()] if g['object_in_world'] is True else None
  cfg=chain.chain_cfg('SD',**{**BASE,**R['scene'],**extra})
  if wo is not None:cfg['r19']=dict(cfg['r19'],objs=list(cfg['r19'].get('objs',[]))+[wo])
  tree,meta=build(cfg,None);K19.add(tree,cfg);P4.add(tree,cfg);P3.mesh_held(tree)
  if cfg.get('r19p5'):P5.add(tree,cfg)
  Rl,p=K17.lever_pose(K17.LEVER_OPEN);K._add(tree.find('worldbody'),'u_open_',K.OBJ['lever']['parts'],Rl,p,rgba='.75 .77 .8 1')
  P4.mesh(tree)
  if cfg.get('r19p5'):P5.mesh(tree)
  pre=add_parts(tree);return Checker(tree,meta),pre
 P5S.prep_scene=prep_scene
# ---------------------------------------------------------------- travel screen
def travel():
 import mujoco,chain,kitchen19dock as D
 import r19tol_core as C
 from scene import build
 from checker import Checker
 t0=time.monotonic();step=float(KV.get('STEP',.005));RUN=float(KV.get('RUN',.005))
 def scene(pin):
  cfg=chain.chain_cfg('SD',**C.BASE);cfg['r19dock']=dict(pin=pin)
  tree,meta=build(cfg,None);D.add(tree,cfg);D.mesh(tree);return Checker(tree,meta)
 out=dict(design=D.summary(),run_clearance_required_mm=RUN*1e3,step_m=step,method=__doc__)
 for pin in ('up','down'):
  ch=scene(pin);m,d=ch.m,ch.d;nm=ch.gnames;cart=m.body('rail_structure').id
  cartg=[g for g in range(m.ngeom) if m.geom_bodyid[g]==cart]
  newc=[g for g in cartg if nm[g].startswith('R_cart_dock_')]
  fixed=[g for g in range(m.ngeom) if nm[g].startswith('dock_')]
  env=[g for g in range(m.ngeom) if not ch.robot[g] and not ch.held[g] and not nm[g].startswith('dock_')]
  def declared(a,b):
   A,B=nm[a],nm[b]
   for p,q in D.INTENDED:
    if (A==p and B==q) or (A==q and B==p):return 'contact (V wheel on V track)'
   if pin=='down':
    for p,q in D.INTENDED_DOWN:
     if (A==p and B.startswith(q)) or (B==p and A.startswith(q)):return 'contact (seated pin in its V-block, let into the rail top)'
   if A in D.REPLACED or B in D.REPLACED:return 'superseded R10 toe channel (inside the rail)'
   for p,q,_ in D.RUNNING:
    if (A.startswith(p) and B.startswith(q)) or (B.startswith(p) and A.startswith(q)):
     if 'keeper' in A+B:return 'keeper in the aisle-face slot (slot not modelled: 1 mm all round by design)' if 'dock_rail' in (A,B) else 'keeper T-head vs the scale tape (must exceed the 1 mm keeper clearance)'
     return 'read head over the scale (ride 0.7 mm nominal; must stay > 0 at y +-0.5 mm)'
   return None
  pairs=[(a,b,'cart_vs_fixed_dock') for a in cartg for b in fixed]+[(a,b,'new_cart_part_vs_environment') for a in newc for b in env]
  q0=np.zeros(m.nq)
  if pin=='up':xs=np.round(np.arange(-1.48,2.46+1e-9,step),4);ys=(-.21,-.2105,-.2095)
  else:xs=np.array(sorted(D.STATIONS.values()));ys=(-.21,)
  def aabb(g):
   if m.geom_type[g]==0:return np.full(3,-1e6),np.full(3,1e6)
   return np.array([ch.bounds.support(g,-e)[k] for k,e in enumerate(np.eye(3))]),np.array([ch.bounds.support(g,e)[k] for k,e in enumerate(np.eye(3))])
  d.qpos[:]=q0;d.qpos[1]=-.21;mujoco.mj_kinematics(m,d)
  BOX={g:aabb(g) for g in set(fixed)|set(env)}   # static
  CB0={g:aabb(g) for g in cartg}   # cart geoms at cart x 0, y -0.21 (the cart only translates)
  PA=np.array([p[0] for p in pairs]);PB=np.array([p[1] for p in pairs]);CAT=[p[2] for p in pairs];DEC=[declared(a,b) for a,b,_ in pairs]
  LOb=np.array([BOX[b][0] for b in PB]);HIb=np.array([BOX[b][1] for b in PB]);LOa0=np.array([CB0[a][0] for a in PA]);HIa0=np.array([CB0[a][1] for a in PA])
  best={};decl={};nst=0;CAPM=.03
  for x in xs:
   for y in ys:
    q=q0.copy();q[0]=x;q[1]=y;d.qpos[:]=q;mujoco.mj_kinematics(m,d);nst+=1;sh=np.array([x,y+.21,0.])
    dl=np.maximum(np.maximum(LOa0+sh-HIb,LOb-(HIa0+sh)),0.);ab=np.sqrt((dl*dl).sum(1))
    for i in np.flatnonzero(ab<CAPM):
     a,b=int(PA[i]),int(PB[i]);k=DEC[i]
     r=max(float(ab[i]),ch.bounds.pair(a,b)['lower_m'])
     key=(CAT[i] if k is None else k);rec=best if k is None else decl
     cur=rec.get(key)
     if cur is None or r<cur['dist_mm']/1e3:
      rec[key]=dict(dist_mm=round(r*1e3,3),pair=[nm[a],nm[b]],cart_x=float(x),cart_y=float(y))
  for cat in ('cart_vs_fixed_dock','new_cart_part_vs_environment'):
   if cat not in best:best[cat]=dict(dist_mm=f'>={CAPM*1e3:g}',pair=None)
  # the travel limits vs the end buffers (truck plates): distance at the two soft limits
  ends={}
  for x in (-1.48,2.46):
   q=q0.copy();q[0]=x;q[1]=-.21;d.qpos[:]=q;mujoco.mj_kinematics(m,d)
   ends[str(x)]=min((round(ch.bounds.pair(a,b)['lower_m']*1e3,2),nm[a],nm[b]) for a in newc for b in fixed if nm[b].startswith('dock_stop'))
  # per original cart part: its closest fixed dock part (castors / wheels / chassis / bumper)
  per={}
  for a in cartg:
   if nm[a].startswith('R_cart_dock_'):continue
   v=1e9;pp=None
   for x in xs[::max(1,len(xs)//40)]:
    q=q0.copy();q[0]=x;q[1]=-.21;d.qpos[:]=q;mujoco.mj_kinematics(m,d)
    for b in fixed:
     r=ch.bounds.pair(a,b)['lower_m']
     if r<v:v=r;pp=nm[b]
   per[nm[a]]=dict(min_mm=round(v*1e3,2),closest=pp)
  need=RUN if pin=='up' else float(KV.get('STATIC',.001))   # docked (pin down, cart stationary): no contact with a 1 mm margin; travel: the running clearance
  ok=all(isinstance(r['dist_mm'],str) or r['dist_mm']>=need*1e3-1e-6 for r in best.values())
  out[f'pin_{pin}']=dict(states=nst,min_by_category=best,declared=decl,end_buffers_mm=ends,original_cart_parts=per,required_mm=need*1e3,clearance_ok=ok)
  print('pin',pin,'states',nst,json.dumps(best),'\n  declared',json.dumps(decl),'\n  ends',ends,flush=True)
 out['elapsed_s']=round(time.monotonic()-t0,1)
 os.makedirs(OUT,exist_ok=True);fn=f'{OUT}/screen_travel.json';json.dump(out,open(fn,'w'),indent=1,default=float);print(fn,out['elapsed_s'],'s')
def arm_main():
 P5S.main()
 # P5S.main names the file screen_<MODE>[_TAG].json = screen_dock[_TAG].json in OUT; nothing else to do
if __name__=='__main__':
 if PART=='travel':travel()
 elif PART=='arm':arm_main()
 else:raise SystemExit('PART=travel|arm')
