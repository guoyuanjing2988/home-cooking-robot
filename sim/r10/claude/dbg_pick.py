import json,numpy as np,mujoco
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from mystat import config
from scene import build,targets
from checker import Checker
cfg=config('T');_,meta=build(cfg);t=targets(cfg,meta)[0];c2=dict(cfg);c2['present']=[]
tree,m2=build(c2,'carrot');ch=Checker(tree,m2)
d=json.load(open('results/T/0.json'));sol=d['endpoints'][1]['best'];q=np.array(sol['q']);R=np.array(sol['rotation'])
ch.configure_target(t,R)
print('windows',len(ch.windows),'registry',list(ch.registry))
g=ch.gnames.index('R_held_carrot');print('extent',abs(R)@ch.m.geom_size[g],'real',np.array(meta['raw_objects']['carrot']['size'])/2)
m,dd=ch.m,ch.d;sid=m.site('R_prep').id;ids=ch.arm_ids;p0=np.array(t['points'][0])
def res(x):
 qq=q.copy();qq[ids]=x;dd.qpos[:]=qq;mujoco.mj_kinematics(m,dd)
 return np.r_[10*(dd.site_xpos[sid]-p0),Rotation.from_matrix(R@dd.site_xmat[sid].reshape(3,3).T).as_rotvec()]
r=least_squares(res,q[ids]);q0=q.copy();q0[ids]=r.x
print('pose err',ch.pose_error(q0,p0,R))
out=ch.check(q0,mass=.12)
print('ok',out['ok'],[ (h['pair'],round(h.get('real_gap_mm',0),2),h.get('reason','')) for h in out['hits']][:6])
print('allowed',ch.permissions('transfer'))
mujoco.mj_forward(m,dd)
tray=ch.gnames.index('raw_tray')
for c in dd.contact[:dd.ncon]:
 if set(map(int,c.geom))=={tray,g}:
  local=dd.geom_xmat[tray].reshape(3,3).T@(c.pos-dd.geom_xpos[tray]);print('contact dist',c.dist,'local',local,'size',m.geom_size[tray],'frame z',c.frame[2])
w=ch.windows[0];p=dd.site_xpos[sid];print('site',p,'origin',w['origin'],'delta',p-np.array(w['origin']))
print('rot diff',np.max(abs(dd.site_xmat[sid].reshape(3,3)-np.array(w['rotation']))))
