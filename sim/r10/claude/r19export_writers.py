"""R19 #6: thin playback writers for the neutral export of r19export.py (results/r19/export/<name>/stream.csv). New file.

 UR    ur_servoj_500hz.csv   t_s, q1..q6 (rad): one row per 2 ms = the period of URScript servoj(q, a, v, t=0.002,
       lookahead_time, gain) fed over RTDE on an e-Series controller (500 Hz) [S: UR script manual,
       https://docs.universal-robots.com/PolyScopeX_SDK_Documentation/build/SDK-v0.13/_static/pdf/scriptManualG5.pdf].
       The carriage (cart) axis is not a UR joint: its column is in stream.csv on the same clock.
 FR5   fr5_servoj_deg_8ms.csv  t_s, j1..j6 (deg), every 4th row of the stream (8 ms): Fairino SDK ServoJ(joint_pos [deg],
       axisPos, acc, vel, cmdT [s], filterT, gain), the SDK example streams with cmdT = 0.008 s [S:
       https://fairino-doc-en.readthedocs.io/latest/SDKManual/CPPRobotMovement.html]. The on-controller trajectory file
       (TrajectoryJUpLoad / LoadTrajectoryJ / MoveTrajectoryJ, files in /fruser/traj/) exists in the SDK, but its file
       content format is not published in the SDK / manual pages reached [S:
       https://fairino-doc-en.readthedocs.io/latest/SDKManual/CPPRobotTrajectoryRecurrence.html]: this CSV is the
       neutral input for it, the conversion to the TrajectoryJ file is NOT written [E].
Each writer reads its file back and measures speed / acceleration / jerk by finite differences on the file's own grid
against the limits of the export's time law (what the controller actually receives).
python r19export_writers.py DIR=results/r19/export/<name> [WHICH=ur|fr5|auto] [FR5_PERIOD=.008]"""
import sys,os,json
import numpy as np
H=.002
def read_stream(d):
 X=np.loadtxt(f'{d}/stream.csv',delimiter=',',skiprows=1);return X[:,0],X[:,1:12],X[:,12].astype(int)
def _limits(d,E):
 """per-row joint v limit and uniform a / j limits (rad units) from export.json"""
 ex=json.load(open(f'{d}/export.json'));V=np.full((len(E),6),np.inf);A=np.inf;J=np.inf
 for el in ex['sequence']:
  if el['type']!='motion':continue
  lm=el['time_law']['limits'];m=E==el['id']
  if 'v' in lm:V[m]=np.array(lm['v'][1:]);A=min(A,min(lm['a'][1:]));J=min(J,min(lm['j'][1:]))
  else:V[m]=np.radians(lm['v_degps']);A=min(A,np.radians(lm['A_degps2']));J=min(J,np.radians(lm['J_degps3']))
 return V,A,J
def _check(t,q,E,d):
 h=float(np.median(np.diff(t)));v=np.gradient(q,h,axis=0);a=np.gradient(v,h,axis=0);j=np.gradient(a,h,axis=0);V,A,J=_limits(d,E)
 return dict(rows=len(t),period_s=round(h,6),grid_ok=bool(np.allclose(np.diff(t),h,atol=1e-6)),peak_v_degps=round(float(np.degrees(np.abs(v).max())),3),peak_a_degps2=round(float(np.degrees(np.abs(a).max())),3),
  peak_j_degps3=round(float(np.degrees(np.abs(j).max())),2),max_ratio=dict(v=round(float((np.abs(v)/V).max()),4),a=round(float(np.abs(a).max()/A),4),j=round(float(np.abs(j).max()/J),4)))
def ur(d):
 t,Q,E=read_stream(d);fn=f'{d}/ur_servoj_500hz.csv'
 with open(fn,'w',newline='') as f:
  f.write('t_s,q1_rad,q2_rad,q3_rad,q4_rad,q5_rad,q6_rad\n')
  for tt,q in zip(t,Q[:,3:9]):f.write(f'{tt:.3f},'+','.join(f'{x:.10f}' for x in q)+'\n')
 X=np.loadtxt(fn,delimiter=',',skiprows=1);return dict(file=fn,**_check(X[:,0],X[:,1:7],E,d))
def fr5(d,period=.008):
 t,Q,E=read_stream(d);k=int(round(period/H));assert abs(k*H-period)<1e-9,'the FR5 period must be a multiple of 2 ms'
 idx=np.r_[np.arange(0,len(t),k)];idx=idx if idx[-1]==len(t)-1 else np.r_[idx,len(t)-1]   # the last (rest) state is always sent
 fn=f'{d}/fr5_servoj_deg_{int(round(period*1000))}ms.csv'
 with open(fn,'w',newline='') as f:
  f.write('t_s,j1_deg,j2_deg,j3_deg,j4_deg,j5_deg,j6_deg\n')
  for i in idx:f.write(f'{t[i]:.3f},'+','.join(f'{x:.8f}' for x in np.degrees(Q[i,3:9]))+'\n')
 X=np.loadtxt(fn,delimiter=',',skiprows=1);n=len(X)-1 if idx[-1]-idx[-2]!=k else len(X)   # the check skips a short last step
 return dict(file=fn,trajectoryj_file='not written [E]: the TrajectoryJ file content format is not in the public SDK / manual pages',**_check(X[:n,0],np.radians(X[:n,1:7]),E[idx[:n]],d))
def write_for_arm(d,arm,which='auto',fr5_period=.008):
 out={}
 if which in ('ur',) or (which=='auto' and arm.startswith('ur')):out['ur']=ur(d)
 if which in ('fr5',) or (which=='auto' and arm.startswith('fr5')):out['fr5']=fr5(d,fr5_period)
 return out
if __name__=='__main__':
 KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a);d=KV['DIR'];ex=json.load(open(f'{d}/export.json'))
 print(json.dumps(write_for_arm(d,ex['arm'],KV.get('WHICH','auto'),float(KV.get('FR5_PERIOD',.008))),indent=1))
