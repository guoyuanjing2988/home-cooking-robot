"""Runtime adaptation: geometry plus explicit-kind contact-window repair."""
import copy,json
import r07_model
r07_model.install()
import final_check as f
_ordinary_required=f.required
def required(ch,a,b):
    # Idle door sweeps apply the ROBOT gate to fingers and EOAT too.
    names=[ch.gnames[a],ch.gnames[b]]
    if any(n.startswith(('idle_full_sweep_cover_','r07_open_door_')) for n in names):
        other=b if names[0].startswith(('idle_full_sweep_cover_','r07_open_door_')) else a
        if ch.robot[other]:return (.010,'robot_door_sweep')
    return _ordinary_required(ch,a,b)
f.required=required
import policy_r05 as policy
import fast_bounds
fast_bounds.install()
policy.WALL_FACES={f'r07_wall_bracket_{i}':'rear +Y face' for i in range(4)}
old_valid=policy.valid_window
def object_identity(h):
    typ=h['held'];prod=h.get('product')
    return 'food:'+prod if typ=='root_food' else 'bowl_'+prod if typ=='carried_bowl' else {'food_cup':'cup','cut_cassette':'cassette'}.get(typ,typ)
def valid_window(ch,w):
    kind=w.get('kind')
    if kind not in ('grasp_release_support','working_stroke'):return False
    if not w.get('object_id') or w.get('support_id')!=w.get('face'):return False
    if w.get('side') not in getattr(ch,'hands',{}):return False
    if w['object_id']!=object_identity(ch.hands[w['side']]):return False
    if kind=='working_stroke' and not getattr(ch,'working_stroke',False):return False
    registry=WORK_REGISTRY if kind=='working_stroke' else SUPPORT_REGISTRY
    if w['face'] not in registry.get(w['object_id'],set()):return False
    return old_valid(ch,w)
policy.valid_window=valid_window
s=f.s;H=s.HERE;O=H/'results'
SUPPORT_REGISTRY={};WORK_REGISTRY={}
for phase in s.P['phases']:
    for stroke in phase['segments']:
        for hands in stroke['poses']:
            for h in hands.values():
                for c in h.get('contacts',[]):
                    registry=WORK_REGISTRY if c.get('kind')=='working_stroke' else SUPPORT_REGISTRY
                    registry.setdefault(object_identity(h),set()).add(c['face'])
def write(n,obj):s.ck.json_write(O/n,obj)
BaseChecker=s.Checker
class Checker(BaseChecker):
    def __init__(self,ph,seg,c=None):
        import xml.etree.ElementTree as E,mujoco
        super().__init__(ph,seg,c)
        root=E.fromstring(self.xml)
        for b in root.findall('.//body'):
            if b.get('name') in ('stored_peeler','stored_wash_pad','stored_eye_core_spoon'):
                p=__import__('numpy').fromstring(b.get('pos'),sep=' ');p[1]-=.35;b.set('pos',s.model.fmt(p))
        self.xml=E.tostring(root,encoding='unicode');self.bind_model(mujoco.MjModel.from_xml_string(self.xml));self.set_contacts(self.hands)
    def forbidden(self,q):
        return f.contacts(self,q)[0]
    def initial(self,rng,k):
        import numpy as np,mujoco
        q=np.array(s.PARK,float)
        for side in self.hands:
            for name in s.ck.ARMS[side]:
                lo,hi=self.m.jnt_range[self.jid[name]]
                q[self.qa[name]]=rng.uniform(max(lo,-np.pi),min(hi,np.pi)) if k%3 else np.clip(q[self.qa[name]]+rng.normal(0,.6),lo+1e-6,hi-1e-6)
            x=np.mean([h[side]['pos'][0] for h in self.seg['poses'] if side in h])
            lo,hi=self.m.jnt_range[self.jid[side+'_carriage_x']]
            q[self.qa[side+'_carriage_x']]=np.clip(x+rng.uniform(-.4,.4),lo+1e-6,hi-1e-6)
            for label in ('minus','plus'):q[self.qa[side+'_jaw_'+label]]=self.hands[side]['jaw_opening_m']/2
        for n,j in self.jid.items():
            if self.m.jnt_limited[j]:q[self.qa[n]]=np.clip(q[self.qa[n]],*self.m.jnt_range[j])
        self.d.qpos[:]=q;mujoco.mj_kinematics(self.m,self.d)
        return q,self.d.site_xpos[self.m.site('L_prep').id].copy()
s.Checker=Checker
def install_motion_policy():
    """Make working permission local to a call, including reused checkers."""
    import motion_r05 as mo
    if getattr(mo,'r07_policy_installed',False):return mo
    base_plan=mo.plan_section
    def plan_section(ch,a,b,ha,hb,seed,process=False):
        ch.working_stroke=bool(process)
        try:return base_plan(ch,a,b,ha,hb,seed,process=process)
        finally:
            ch.working_stroke=False
            ch.contact_windows=[]
    mo.plan_section=plan_section;mo.r07_policy_installed=True
    return mo
install_motion_policy()
