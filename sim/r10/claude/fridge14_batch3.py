"""R14 fridge reach, round 3 (docked cart at x = -1.48): the robot cold box in the top door bin,
top-down pinch on its bridge bar with the door at 40-55°, the lift (+80 mm) and the slide out
along the door past its free edge, and the set-down on the counter end beside the cart.
python fridge14_batch3.py [NPAR]"""
import sys,subprocess,itertools,numpy as np
from concurrent.futures import ThreadPoolExecutor
import kitchen14 as K
F=K.FRIDGE;H=np.array([F['x'][0],F['y_face']+F['door_t']]);BX=F['rbox'];ZB=F['rbin']['z']
rz=lambda th,v:np.array([v[0]*np.cos(th)+v[1]*np.sin(th),-v[0]*np.sin(th)+v[1]*np.cos(th)])
f=lambda v:'_'.join(f'{x:.3f}' for x in v);C=['CARTX=-1.48','CARTY=-0.21']
uc,vc=sum(BX['u'])/2,sum(BX['v'])/2;zbar=ZB+BX['h']+BX['bar_z']
jobs=[]
ZBS=[float(x) for x in sys.argv[2].split(',')] if len(sys.argv)>2 else [ZB]
for a,ZB in itertools.product([int(x) for x in sys.argv[3].split(",")] if len(sys.argv)>3 else [45,50,55],ZBS):
 th=np.radians(a);jw=rz(th,(1,0));zbar=ZB+BX['h']+BX['bar_z']
 for tag,u,dz,box in (('grasp',uc,0,'1'),('lift',uc,.07,'taken'),('slide',.45,.07,'taken'),('clear',.62,.07,'taken')):
  p=H+rz(th,(u,vc))
  jobs.append([f'pt{f([p[0],p[1],zbar+dz,0,0,-1,jw[0],jw[1],0])}',f'FRIDGE={a}',f'BOX={box}','JAWQ=0',f'RBINZ={ZB}']+C+[f'TAG=box_{tag}'])
for sx,sy in itertools.product((-1.75,-1.25,-1.05),(.20,.30)):jobs.append([f'pt{f([sx,sy,.85+BX["h"]+BX["bar_z"],0,0,-1,1,0,0])}','FRIDGE=0','BOX=taken','JAWQ=0']+C+['TAG=box_stage'])
PY=sys.executable;N=int(sys.argv[1]) if len(sys.argv)>1 else 14
def run(j):
 r=subprocess.run([PY,'r14reach.py']+j,capture_output=True,text=True);return j,(r.stdout.strip().splitlines() or [r.stderr[-300:]])[-1]
with ThreadPoolExecutor(N) as ex:
 for j,o in ex.map(run,jobs):print(' '.join(j[1:]),'OK' if '"ok": true' in o else 'FAIL '+o[-260:],flush=True)
