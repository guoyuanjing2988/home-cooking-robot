"""R14 fridge reach, round 2 (docked cart at its leftmost dock x = -1.48): handle at 50-60°
over the bar height, and the robot baskets (front-right, then the one behind it) with the
door held at 50/60° by its own friction (not by the arm). python fridge14_batch2.py [NPAR]"""
import sys,subprocess,itertools,numpy as np
from concurrent.futures import ThreadPoolExecutor
import kitchen14 as K
F=K.FRIDGE;H=np.array([F['x'][0],F['y_face']+F['door_t']]);BAR=np.array([F['bar_x'],F['bar_y']])
rz=lambda th,v:np.array([v[0]*np.cos(th)+v[1]*np.sin(th),-v[0]*np.sin(th)+v[1]*np.cos(th)])
f=lambda v:'_'.join(f'{x:.3f}' for x in v);C=['CARTX=-1.48','CARTY=-0.21']
jobs=[]
for a,z in itertools.product([50,55,60],[1.00,1.10,1.20]):
 th=np.radians(a);p=H+rz(th,BAR-H);ap=rz(th,(-1,0));jw=rz(th,(0,1))
 jobs.append([f'pt{f([p[0],p[1],z,ap[0],ap[1],0,jw[0],jw[1],0])}',f'FRIDGE={a}','HELD=1','JAWQ=0']+C+[f'TAG=hdl2z{z:.2f}'])
B=F['basket'];z0=F['shelves'][2]
for (k,(bx,by)),door,ya in itertools.product(enumerate(F['baskets']),[50,60],[0,20,35]):
 kn=[bx,by-B['R']-.035,z0+B['H']+.015];ap=[-np.sin(np.radians(ya)),np.cos(np.radians(ya)),0]
 jobs.append([f'pt{f(kn+ap+[0,0,1])}',f'FRIDGE={door}',f'BASKET={k}','JAWQ=.0015']+C+[f'TAG=knob{k}a{ya}'])
PY=sys.executable;N=int(sys.argv[1]) if len(sys.argv)>1 else 14
def run(j):
 r=subprocess.run([PY,'r14reach.py']+j,capture_output=True,text=True);return j,(r.stdout.strip().splitlines() or [r.stderr[-300:]])[-1]
with ThreadPoolExecutor(N) as ex:
 for j,o in ex.map(run,jobs):print(' '.join(j[1:]),'OK' if '"ok": true' in o else 'FAIL',flush=True)
