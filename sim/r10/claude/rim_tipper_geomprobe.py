import sys;sys.path.insert(0,'.')
import r34holder,chain,mujoco,numpy as np
from scene import build
from checker import Checker
import kitchen16 as K
K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);K.TOOL_XY['spider']=(1.52,.36)
cs=chain.chain_cfg('SD',r14=True,present=[],r15=True,r15_spatula=.45,r15_spatula_jaw=-1,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None,'spatula':None})
for ex in (dict(r34_holder=[105,.035,.03],r34_cup=True),dict(r34_holder=[105,.035,.03],r34_tipped=True)):
 tree,meta=build({**cs,**ex},None);ch=Checker(tree,meta);m=ch.m
 names=[m.geom(g).name for g in range(m.ngeom) if m.geom(g).name.startswith('r34_')]
 print(names,[ (m.geom(n).id, round(float(m.geom_rbound[m.geom(n).id]),3)) for n in names])
