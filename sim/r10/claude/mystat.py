"""R10 (orchestrator) statics screen for the docked cart: all carrot templates, both endpoints, 96 starts."""
import sys,json,time
import numpy as np
from scene import build,targets,load,save,jaw_q
from checker import Checker
from solver import solve
PRESETS={'A':dict(mount_height=1.05,mount_tilt_deg=0),'B':dict(mount_height=1.20,mount_tilt_deg=0),'C':dict(mount_height=1.35,mount_tilt_deg=0),'D':dict(mount_height=1.20,mount_tilt_deg=-20),'E':dict(mount_height=1.05,mount_tilt_deg=-20),'F':dict(mount_height=1.35,mount_tilt_deg=-20),'G':dict(mount_height=1.20,mount_tilt_deg=-20,mount_y=.16),'H':dict(mount_height=1.20,mount_tilt_deg=-20,mount_y=.20,cantilever=True,long_spout=True),'I':dict(mount_height=1.35,mount_tilt_deg=-20,mount_y=.20,cantilever=True,long_spout=True),'J':dict(mount_height=1.20,mount_tilt_deg=-20,mount_y=.20,cantilever=True,long_spout=True,peel_top=True,mand_raise=.12,mand=[.20,.135],tomato=[.52,.14]),'K':dict(mount_height=1.35,mount_tilt_deg=-20,mount_y=.20,cantilever=True,long_spout=True,peel_top=True,mand_raise=.12,mand=[.20,.135],tomato=[.52,.14]),'L':dict(mount_height=1.05,mount_y=.20,mount_tilt_deg=-20,cantilever=True,long_spout=True,peel_top=True,mand_raise=.12,mand=[.20,.135],tomato=[.52,.14]),'M':dict(mount_height=1.20,mount_y=.08,mount_tilt_deg=-20,cantilever=True,long_spout=True,peel_top=True,mand_raise=.12,mand=[.20,.135],tomato=[.52,.14]),'N':dict(mount_height=1.05,mount_y=.08,mount_tilt_deg=-20,cantilever=True,long_spout=True,peel_top=True,mand_raise=.12,mand=[.20,.135],tomato=[.52,.14]),'P':dict(mount_height=1.05,mount_y=.08,mount_tilt_deg=-20,cantilever=True,long_spout=True,peel_top=True,peel_fwd=True,peel=[-1.21,.10],mand_raise=.12,mand=[.20,.135],tomato=[.52,.14]),'Q':dict(mount_height=1.20,mount_y=.08,mount_tilt_deg=-20,cantilever=True,long_spout=True,peel_top=True,peel_fwd=True,peel=[-1.21,.10],mand_raise=.12,mand=[.20,.135],tomato=[.52,.14]),'R':dict(mount_height=1.12,mount_y=.08,mount_tilt_deg=-20,cantilever=True,long_spout=True,peel_top=True,peel_fwd=True,peel=[-1.21,.10],mand_raise=.12,mand=[.20,.135],tomato=[.52,.14]),'S':dict(mount_height=1.12,mount_y=.04,mount_tilt_deg=-20,cantilever=True,long_spout=True,peel_top=True,peel_fwd=True,peel=[-1.21,.10],mand_raise=.12,mand=[.20,.135],tomato=[.52,.14]),'T':dict(mount_height=1.12,mount_y=.04,per_step=True,mount_tilt_deg=-20,cantilever=True,long_spout=True,peel_top=True,peel_fwd=True,peel=[-1.21,.10],mand_raise=.12,mand=[.20,.135],tomato=[.52,.14]),'U':dict(mount_height=1.12,mount_y=.08,per_step=True,mount_tilt_deg=-20,cantilever=True,long_spout=True,peel_top=True,peel_fwd=True,peel=[-1.21,.10],mand_raise=.12,mand=[.20,.135],tomato=[.52,.14]),'V':dict(mount_height=1.12,mount_y=.04,raw_shift=.20,mount_tilt_deg=-20,cantilever=True,long_spout=True,peel_top=True,peel_fwd=True,peel=[-1.00,.10],mand_raise=.12,mand=[.20,.135],tomato=[.52,.14],per_step=True,fixed_jaws=True),'W':dict(mount_height=1.12,mount_y=.08,raw_shift=.20,mount_tilt_deg=-20,cantilever=True,long_spout=True,peel_top=True,peel_fwd=True,peel=[-1.00,.10],mand_raise=.12,mand=[.20,.135],tomato=[.52,.14],per_step=True,fixed_jaws=True),'X':dict(mount_height=1.12,mount_y=.08,raw_shift=.20,mount_tilt_deg=-20,cantilever=True,long_spout=True,peel_top=True,peel_fwd=True,peel=[-1.00,.16],mand_raise=.12,mand=[.20,.135],tomato=[.52,.14],per_step=True,fixed_jaws=True),'Y':dict(mount_height=1.12,mount_y=.06,raw_shift=.20,mount_tilt_deg=-20,cantilever=True,long_spout=True,peel_top=True,peel_fwd=True,peel=[-1.00,.16],mand_raise=.12,mand=[.20,.135],tomato=[.52,.14],per_step=True,fixed_jaws=True),'Z':dict(mount_height=1.12,mount_y=.04,raw_shift=.20,mount_tilt_deg=-20,cantilever=True,long_spout=True,peel_open=True,peel_fwd=True,peel=[-1.00,.20],mand_raise=.12,mand=[.20,.135],tomato=[.52,.14],per_step=True,fixed_jaws=True),'Z8':dict(mount_height=1.12,mount_y=.08,raw_shift=.20,mount_tilt_deg=-20,cantilever=True,long_spout=True,peel_open=True,peel_fwd=True,peel=[-1.00,.20],mand_raise=.12,mand=[.20,.135],tomato=[.52,.14],per_step=True,fixed_jaws=True),'Z9':dict(mount_height=1.12,mount_y=.08,raw_shift=.20,yaw=90,mand=[.20,.15],mount_tilt_deg=-20,cantilever=True,long_spout=True,peel_open=True,peel_fwd=True,peel=[-1.00,.20],mand_raise=.12,tomato=[.52,.14],per_step=True,fixed_jaws=True),'AA':dict(mount_height=1.12,mount_y=.08,raw_shift=.20,yaw=90,mand=[.20,.15],mount_tilt_deg=-20,cantilever=True,long_spout=True,peel_open=True,peel_fwd=True,peel=[-1.00,.20],mand_raise=.12,tomato=[.52,.14],per_step=True,fixed_jaws=True,deep_cart=True,rib_tray=True),'AB':dict(mount_height=1.12,mount_y=.08,raw_shift=.20,yaw=0,mand=[.20,.135],mount_tilt_deg=-20,cantilever=True,long_spout=True,peel_open=True,peel_fwd=True,peel=[-1.00,.20],mand_raise=.12,tomato=[.52,.14],per_step=True,fixed_jaws=True,deep_cart=True,rib_tray=True),'AC':dict(mount_height=1.12,mount_y=.08,raw_shift=.20,yaw=90,mand=[.20,.14],mand_raise=.07,mand_leg=.12,bowl_r=.082,mount_tilt_deg=-20,cantilever=True,long_spout=True,peel_open=True,peel_fwd=True,peel=[-1.00,.20],tomato=[.52,.14],per_step=True,fixed_jaws=True,deep_cart=True,rib_tray=True),'AD':dict(mount_height=1.05,mount_y=.08,raw_shift=.20,yaw=90,mand=[.20,.14],mand_raise=.07,mand_leg=.12,bowl_r=.082,mount_tilt_deg=-20,cantilever=True,long_spout=True,peel_open=True,peel_fwd=True,peel=[-1.00,.20],tomato=[.52,.14],per_step=True,fixed_jaws=True,deep_cart=True,rib_tray=True),'AE':dict(mount_height=1.05,mount_y=.08,raw_shift=.20,mount_tilt_deg=-20,cantilever=True,long_spout=True,peel_open=True,peel_fwd=True,peel=[-1.00,.20],tomato=[.52,.14],per_step=True,fixed_jaws=True,deep_cart=True,rib_tray=True,yaw=90,mand=[.20,.08],mand_raise=.07,mand_legs=[-.06,.12],bowl_r=.068,bowl_dx=.03),'AF':dict(mount_height=1.12,mount_y=.08,raw_shift=.20,mount_tilt_deg=-20,cantilever=True,long_spout=True,peel_open=True,peel_fwd=True,peel=[-1.00,.20],tomato=[.52,.14],per_step=True,fixed_jaws=True,deep_cart=True,rib_tray=True,yaw=90,mand=[.20,.08],mand_raise=.07,mand_legs=[-.06,.12],bowl_r=.068,bowl_dx=.03),'AG':dict(mount_height=1.12,mount_y=.08,raw_shift=.20,cart_spots={'raw_pick':-1.0,'wash_load':-1.0,'wash_work':-1.0,'peel_load':-1.0,'peel_retrieve':-1.0},mount_tilt_deg=-20,cantilever=True,long_spout=True,peel_open=True,peel_fwd=True,peel=[-1.00,.20],tomato=[.52,.14],per_step=True,fixed_jaws=True,deep_cart=True,rib_tray=True,yaw=90,mand=[.20,.15],mand_raise=.12),'AH':dict(mount_height=1.12,mount_y=.08,raw_shift=.20,cart_spots={'raw_pick':-1.05,'wash_load':-1.05,'wash_work':-1.05,'peel_load':-1.05,'peel_retrieve':-1.05},mount_tilt_deg=-20,cantilever=True,long_spout=True,peel_open=True,peel_fwd=True,peel=[-1.00,.20],tomato=[.52,.14],per_step=True,fixed_jaws=True,deep_cart=True,rib_tray=True,yaw=90,mand=[.20,.15],mand_raise=.12),'AI':dict(mount_height=1.12,mount_y=.08,raw_shift=.20,mast_y=-.17,mount_tilt_deg=-20,cantilever=True,long_spout=True,peel_open=True,peel_fwd=True,peel=[-1.00,.20],tomato=[.52,.14],per_step=True,fixed_jaws=True,deep_cart=True,rib_tray=True,yaw=90,mand=[.20,.15],mand_raise=.12)}
# R11: market tool set. Counter-resident electric slicer replaces the mandoline.
PRESETS['AJ']=dict(PRESETS['AI'],no_mand=True,slicer=[.30,.13])
PRESETS['AK']=dict(PRESETS['AJ'],cradle_d=.035,peel_len=.048)
PRESETS['AL']=dict(PRESETS['AK'])
PRESETS['AM']=dict(PRESETS['AK'],raw_shift=.27)
# R11 tomato: 3D-printed finger pads (30-80 mm), tomato on a pad at the tray front,
# fetched lever cutter base at the peeler work spot; carrot/potato already gone.
PRESETS['AO']=dict(PRESETS['AM'])
PRESETS['AP']=dict(PRESETS['AM'],mesh_tool=True)
PRESETS['AR']=dict(PRESETS['AP'],peel_hover=.001)
PRESETS['AS']=dict(PRESETS['AR'])
PRESETS['AN']=dict(PRESETS['AM'],finger_offset=.015,r11_tomato=True,lever_base=[-1.00,.13],raw_absent=['potato','carrot'],present_chain=['slicer','lever'])
# Per-target scene state: where the tomato is while each stroke runs.
PRESETS['AQ']=dict(PRESETS['AN'],mesh_tool=True)
PRESETS['AT']=dict(PRESETS['AQ'])
PRESETS['AU']=dict(PRESETS['AQ'],press_front=True)
# Lever base 35 mm toward the aisle (base plate still within the counter edge).
PRESETS['AV']=dict(PRESETS['AU'],lever_base=[-1.00,.095],lever_plate_dy=.035)
# Whole lever station 30 mm lower above its base plate (78 mm bin): knob 30 mm lower.
PRESETS['AW']=dict(PRESETS['AV'],lever_dz=-.03)
# R12 finger designs (fingers.py): one finger set for both chains, the tomato gripped
# at its equator (tomato_dz 0). S* = carrot chain (from AS), W* = tomato chain (from AW).
for _k in ('L','V','K','R','D'):
 PRESETS['S'+_k]=dict(PRESETS['AS'],finger=_k)
 PRESETS['W'+_k]=dict(PRESETS['AW'],finger=_k,tomato_dz=0.)
TOMATO_STATE={'pusher_grasp':dict(tomato_at='plate'),'pusher_press':dict(tomato_gone=True),'pusher_return':dict(tomato_gone=True)}
def config(name):
 cfg=load('results/selected.json')['config'];cfg.update(dock=True,mount_y=.12,fix_bowl_target=True,front_grasp=False,trial='R10'+name);cfg.update(PRESETS[name]);return cfg
def target_state(cfg,meta,name):
 st=dict(TOMATO_STATE.get(name,{})) if cfg.get('r11_tomato') else {}
 if st.get('tomato_at')=='plate':st['tomato_at']=(np.array(meta['lever_origin'])+[0,0,.124+cfg.get('lever_dz',0.)+.03]).tolist()
 return st
def run(name,indices):
 cfg=config(name);_,meta=build(cfg);ts=targets(cfg,meta)
 STEP={'raw_pick':[],'wash_load':[],'wash_work':[],'peel_load':['peeler'],'peel_retrieve':['peeler'],'holder_load':['mandoline'],'mandoline_work':['mandoline'],'holder_retreat':['mandoline'],'wedge_load@tomato':['lever'],'wedge_slide@tomato':['lever'],'pusher_grasp':['lever'],'pusher_press':['lever'],'pusher_return':['lever']}
 for i in indices:
  t=ts[i]
  c2=dict(cfg);c2.update(target_state(cfg,meta,t['name']))
  if cfg.get('finger_offset') or cfg.get('finger'):t['jaw_q']=.025 if t['held'] is None else jaw_q(cfg,t['held'])
  if cfg.get('per_step'):c2['present']=STEP.get(t['name'],[])+(['slicer'] if cfg.get('slicer') else [])
  tree,m2=build(c2,t['held']);ch=Checker(tree,m2);ends=[]
  for k,p in enumerate([t['points'][0],t['points'][-1]]):
   b=time.monotonic();r=solve(ch,np.array(p),t['approach'],seed=5000+i*2+k,target=t)
   ends.append(dict(ok=r['ok'],counts=r['status_counts'],best_reserve=(r['candidates'][0]['reserve_mm'] if r['candidates'] else None),best=r['best'] if not r['ok'] else r['candidates'][0],elapsed=time.monotonic()-b))
   print(name,i,t['name'],k,r['ok'],r['status_counts'],flush=True)
  save(f'results/{name}/{i}.json',dict(index=i,name=t['name'],target=t,endpoints=ends,static_ok=all(e['ok'] for e in ends)))
if __name__=='__main__':
 cfg=config(sys.argv[1]);_,meta=build(cfg);n=len(targets(cfg,meta))
 run(sys.argv[1],[int(x) for x in sys.argv[2:]] or list(range(n)))
