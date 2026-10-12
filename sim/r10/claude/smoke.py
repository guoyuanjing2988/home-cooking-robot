import numpy as np, json
from scene import build, targets, load
from checker import Checker
cfg=load('results/selected.json')['config']; cfg.update(dock=True,mount_height=1.20,mount_y=.12,mount_tilt_deg=0,fix_bowl_target=True)
tree,meta=build(cfg); ch=Checker(tree,meta)
q=ch.m.qpos0.copy(); q[:3]=[-1.0,-.21,0]; q[-2:]=.015
r=ch.check(q)
print('ok',r['ok'],'mobile',r['mobile']['ok'],'stab',round(r['stability']['min_margin_m'],3),'mass',round(r['stability']['mass_kg'],1),'bumperN',round(r['stability']['max_bumper_force_N'],1))
print('hits',[h['pair'] for h in r['hits']][:10])
