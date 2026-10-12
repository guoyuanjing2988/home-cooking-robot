import os,sys,json,time
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[n]='1'
sys.dont_write_bytecode=True
import numpy as np,mujoco
import reference as ck,model
from collections import Counter
c=dict(model.CONFIG,transport_only=True)
hd=ck.hand([-.9,.16,1.06],approach=(0,0,-1),jaw_axis=(0,1,0))
ph=ck.phase('probe','probe',[ck.segment('probe',[hd],'probe')])
class Probe(ck.Checker):
    def __init__(self):
        self.phase=ph;self.seg=ph['segments'][0];self.desc=hd
        tr,meta=model.build(c);ck.META=meta;ck.ARMS=meta['arms'];ck.BASE=meta['base'];ck.JAWS=meta['jaws'];ck.LIM=meta['torque_limits'];ck.JOINTS=sum(ck.ARMS.values(),[])
        self.bind_model(mujoco.MjModel.from_xml_string(__import__('xml.etree.ElementTree',fromlist=['']).tostring(tr.getroot(),encoding='unicode')))
    def randomq(self,rng):
        q=self.m.qpos0.copy()
        for s in model.SIDES:
            q[self.qa[s+'_carriage_x']]=-.5
            for n in ck.ARMS[s]:q[self.qa[n]]=rng.uniform(*self.m.jnt_range[self.jid[n]])
            for label in ('minus','plus'):q[self.qa[s+'_jaw_'+label]]=.01
        return q
ch=Probe();rng=np.random.default_rng(831);best=None;counts=Counter();clear=0
for k in range(4000):
    q=ch.randomq(rng);hits=ch.forbidden(q)
    for h in hits:counts.update([tuple(h['pair'])])
    if not hits:
        clear+=1
        ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d)
        # Prefer compact TCP y/z and nominal rail-clearance.
        score=sum(np.linalg.norm(ch.d.site_xpos[ch.m.site(s+'_prep').id]-[-.5,model.CONFIG['front_mount_y']-model.CONFIG['pitch']*i,1.04]) for i,s in enumerate(model.SIDES))
        if best is None or score<best['score']:best=dict(q=q.tolist(),score=float(score),k=k)
print('clear',clear,'best',best,'blockers',counts.most_common(8))
ck.json_write(model.HERE/'results/parking_probe.json',dict(config=c,starts=4000,clear=clear,best=best,blockers=[dict(pair=p,count=n) for p,n in counts.most_common(20)]))
