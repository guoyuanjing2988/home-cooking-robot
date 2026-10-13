"""R19 smooth: the R15 stir cycle's hand-offs, from its stored bench keys (no arm states are stored for
the checked cycle). r15stirwalk2 follows each stroke's working part (phase 0 .. 0.76 of PERIOD) at the
bench timing and joins strokes with straight joint-space returns timed rest to rest (trapezoid). This
prints the grip-point (TCP) speed and acceleration of the bench path where the working part ends and
where the next one starts: a non-zero speed there is a velocity jump into / out of the rest-to-rest return.
python r19smooth_stir.py  -> results/r19/smooth/stir_handoff.json"""
import sys,json;sys.path.insert(0,'.')
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.spatial.transform import Rotation,RotationSpline
import kitchen15 as K
KEYS='results/r15/stir_h_scrape_dice_keys.json';GRIP=.45;LIFT=.01;KPS=16;NS=5;P=2.4
keys=json.load(open(KEYS))['keys'];KT=np.array([k['t'] for k in keys])
PS=CubicSpline(KT,np.array([k['p'] for k in keys]),bc_type='clamped');RS=RotationSpline(KT,Rotation.from_matrix(np.array([k['R'] for k in keys])))
b=K.SP.grip_point(GRIP)
def grip(t):
 p=PS(t);R=RS(t).as_matrix();n=K.SP.C-p;n/=np.linalg.norm(n);return p+LIFT*n+R@b
h=1e-4;out=[]
w=json.load(open('results/r15/stirwalk2_h_scrape_dice_r17.json'))
ret={s['stroke']:s['ret_into'] for s in w['attempts'][-1]['strokes'] if s.get('ret_into')}
for k in range(NS):
 t0=KT[k*KPS];te=t0+.76*P
 for name,t in (('start',t0),('end',te)):
  v=(grip(t+h)-grip(t-h))/(2*h);a=(grip(t+h)-2*grip(t)+grip(t-h))/h**2;om=np.linalg.norm(RS(t,1))
  out.append(dict(stroke=k,where=name,t=round(float(t),3),grip_speed_m_s=round(float(np.linalg.norm(v)),3),grip_acc_m_s2=round(float(np.linalg.norm(a)),2),blade_rot_deg_s=round(float(np.degrees(om)),1)))
  print(out[-1])
res=dict(keys=KEYS,period_bench_s=P,returns=ret,handoffs=out,working_part_joint_speed_max_degps=w['working_part_joint_speed_max_degps'],feasible_period_s=w['feasible_period_s'])
json.dump(res,open('results/r19/smooth/stir_handoff.json','w'),indent=1);print('returns',ret)
