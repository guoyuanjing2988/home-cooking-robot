"""R14 single-door fridge reach batch: handle poses along the door arc (door at each angle,
bar held = removed from the checker) and basket-knob poses on the robot shelf (door 105°),
for several cart poses; runs r14reach.py probes in parallel. python fridge14_batch.py [NPAR]"""
import sys,subprocess,itertools,numpy as np
from concurrent.futures import ThreadPoolExecutor
import kitchen14 as K
F=K.FRIDGE;H=np.array([F['x'][0],F['y_face']+F['door_t']]);BAR=np.array([F['bar_x'],F['bar_y']]);ZG=1.10
CARTS=[(-1.48,-.21),(-1.58,-.21),(-1.80,-.75),(-2.00,-.85),(-2.20,-.85)]
ANG=[0,15,30,45,60,75,90,105]
rz=lambda th,v:np.array([v[0]*np.cos(th)+v[1]*np.sin(th),-v[0]*np.sin(th)+v[1]*np.cos(th)])  # rotation by -th about z
f=lambda v:'_'.join(f'{x:.3f}' for x in v)
jobs=[]
for (cx,cy),a in itertools.product(CARTS,ANG):
 th=np.radians(a);p=H+rz(th,BAR-H);ap=rz(th,(-1,0));jw=rz(th,(0,1))
 jobs.append([f'pt{f([p[0],p[1],ZG,ap[0],ap[1],0,jw[0],jw[1],0])}',f'FRIDGE={a}','HELD=1','JAWQ=0',f'CARTX={cx}',f'CARTY={cy}','TAG=hdl'])
B=F['basket'];z0=F['shelves'][2]
for (cx,cy),(k,(bx,by)) in itertools.product(CARTS,enumerate(F['baskets'])):
 kn=[bx,by-B['R']-.035,z0+B['H']+.015]
 jobs.append([f'pt{f(kn+[0,1,0,0,0,1])}','FRIDGE=105',f'BASKET={k}','JAWQ=.0015',f'CARTX={cx}',f'CARTY={cy}',f'TAG=knob{k}'])
 jobs.append([f'pt{f([bx,-.25,kn[2]+.01,0,1,0,0,0,1])}','FRIDGE=105',f'BASKET={k}','JAWQ=.0015',f'CARTX={cx}',f'CARTY={cy}',f'TAG=out{k}'])
for cx,cy in CARTS[:2]:  # basket set down on the counter end beside the docked cart
 jobs.append([f'pt{f([-1.66,.155,.965,0,1,0,0,0,1])}','FRIDGE=0','JAWQ=.0015',f'CARTX={cx}',f'CARTY={cy}','TAG=stage'])
PY=sys.executable;N=int(sys.argv[1]) if len(sys.argv)>1 else 14
def run(j):
 r=subprocess.run([PY,'r14reach.py']+j,capture_output=True,text=True);return j,(r.stdout.strip().splitlines() or [r.stderr[-300:]])[-1]
with ThreadPoolExecutor(N) as ex:
 for j,o in ex.map(run,jobs):print(' '.join(j[1:]),o[:160],flush=True)
