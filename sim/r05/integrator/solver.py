"""Collision-aware search; reference forbidden(), target_rotation and grip gates reused."""
import os,sys,copy,json,time,itertools,math,hashlib
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[n]='1'
sys.dont_write_bytecode=True
import xml.etree.ElementTree as E
import numpy as np,mujoco,mink
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares
from collections import Counter
import model,reference as ck
HERE=model.HERE
P=json.loads((HERE/'results/process_v3.json').read_text())
PARK=json.loads((HERE/'results/parking_probe.json').read_text())['best']['q']
def rot(h):return ck.rotation(h['approach'],h['jaw_axis'])
def food_size(h):
    size=next(f['input_size_m'] for f in P['finished_products'] if f['product']==h['product'])
    if h.get('food_state')=='half':size=[size[0],size[1]/2,size[2]]
    if h.get('food_state')=='leaf':size=[.17,.03,.012]
    if h.get('food_state')=='terminal':size=[.010,size[1],size[2]]
    return [size[2],size[1],size[0]]
def held(p,h,prefix):
    if h.get('object_rotation_deg'):p=E.SubElement(p,'body',name=prefix+'object',quat=model.quat(Rotation.from_euler('xyz',h['object_rotation_deg'],degrees=True)))
    typ=h['held'];geos=copy.deepcopy(P['tools'][typ]['geometry'])
    if typ=='eye_core_spoon':
        shaft=next(g for g in geos if g['name']=='spoon_shaft');shaft['to_m']=[.065,0,0]
        geos.append(dict(name='spoon_neck_work_face',type='capsule',from_m=[.065,0,0],to_m=[.075,0,0],radius_m=.004))
    for g in geos:
        if g['type']=='ingredient_box_or_ellipsoid':g=dict(name='food',type='box',center_m=h.get('food_center_local_m',[0,0,0]),size_m=food_size(h))
        for a in model.primitive(p,g,prefix=prefix,robot=prefix.startswith(('R_','L_'))):
            a.set('mass','.000001')
            if typ=='root_food' and h.get('food_tool_roll_deg') is not None:a.set('quat',model.quat(Rotation.from_euler('z',-h['food_tool_roll_deg'],degrees=True)))
    if typ in ('food_cup','cut_cassette','colander','carried_bowl') and h['held_kg']>P['tools'][typ]['mass_kg']:
        sz=food_size(h);cx={'food_cup':.096,'cut_cassette':.095,'colander':.1395,'carried_bowl':.179}[typ]-sz[0]/2
        model.box(p,prefix+'contents',[cx,0,.15 if typ=='food_cup' else 0],sz,robot=prefix.startswith(('R_','L_')),mass=.000001)
    if typ not in ('root_food','empty'):
        for s in (-1,1):model.box(p,prefix+f'key_shoulder{s}',[s*.036,0,0],[.008,.046,.030],mass=.000001,robot=prefix.startswith(('R_','L_')))
class Checker(ck.Checker):
    def __init__(self,ph,seg,c=None):
        self.config=c or model.CONFIG;ck.configure(self.config);self.phase=ph;self.seg=copy.deepcopy(seg);self.desc=next(iter(seg['poses'][0].values()))
        tr=copy.deepcopy(ck.TEMPLATE);w=tr.getroot().find('worldbody');self.hands=seg['poses'][0]
        if seg['station']=='secondary':
            lid=w.find("geom[@name='secondary_closed_lid']");lid.set('name','secondary_open_lid');lid.set('pos','-1.27 .435 1.326')
        product=self.desc.get('product','carrot')
        # All four vessels are installed and retained. Active vessel is not duplicated.
        for prod,x,m in zip(['carrot','potato','leafy_greens','tomato'],[-1.665,-1.415,-1.165,-.915],[.12,.20,.10,.15]):
            if self.desc['held']=='carried_bowl' and prod==product:continue
            h=dict(self.desc,pos=[x,.435,1.042],held='carried_bowl',held_kg=.52,product=prod,approach=[0,0,-1],jaw_axis=[0,1,0],object_rotation_deg=[0,0,0])
            b=E.SubElement(w,'body',name='stored_bowl_'+prod,pos=model.fmt(h['pos']),quat=model.quat(Rotation.from_matrix(rot(h))));held(b,h,'stored_bowl_'+prod+'_')
        for typ,x in [('peeler',-.55),('wash_pad',-.18),('eye_core_spoon',-.325)]:
            if any(h['held']==typ for h in self.hands.values()):continue
            h=dict(self.desc,held=typ,held_kg=P['tools'][typ]['mass_kg'],pos=[x,.46,1.0715 if typ=='peeler' else 1.0865 if typ=='eye_core_spoon' else 1.080],approach=[0,0,-1],jaw_axis=[0,1,0],object_rotation_deg=[0,0,0])
            b=E.SubElement(w,'body',name='stored_'+typ,pos=model.fmt(h['pos']),quat=model.quat(Rotation.from_matrix(rot(h))));held(b,h,'stored_'+typ+'_')
        if seg['station']=='peel':
            sz=next(f['input_size_m'] for f in P['finished_products'] if f['product']==product)
            for sgn in (-1,1):
                stop=w.find(f"geom[@name='peel_endstop{sgn}']");stop.set('pos',model.fmt([-.935+sgn*(.145 if self.desc['held']=='wash_pad' else sz[0]/2+.0075),.17,1.1025]))
            if self.desc['held'] in ('peeler','eye_core_spoon') and not any(h['held']=='root_food' for s,h in self.hands.items() if s!='R'):
                angle=math.radians(seg.get('food_roll_deg',0));ext=abs(math.sin(angle))*sz[1]+abs(math.cos(angle))*sz[2]
                g=model.box(w,'clamped_food',[-.935,.17,1.105+ext/2],sz,robot=False);g.set('quat',model.quat(Rotation.from_euler('x',angle)))
        if seg['station']=='sink' and self.desc['held']=='root_food' and product=='potato':
            for n in ('root_brush_work_face','root_brush_height_slide'):
                g=w.find(f"geom[@name='{n}']");pos=np.fromstring(g.get('pos'),sep=' ');pos[2]-=.0175;g.set('pos',model.fmt(pos))
        if ph['id']=='Q16':model.box(w,'wash_food',[-.23,.17,.96],[.17,.03,.012],robot=False)
        if self.desc['held']=='colander':
            rotation=Rotation.from_euler('x',90,degrees=True);pivot=np.array([-.42,.40,.69])
            for name in ('root_brush_work_face','root_brush_fixed_stem','root_brush_height_slide'):
                g=w.find(f"geom[@name='{name}']");pos=np.fromstring(g.get('pos'),sep=' ');g.set('pos',model.fmt(pivot+rotation.apply(pos-pivot)));g.set('quat',model.quat(rotation))
        for s,h in self.hands.items():
            p=w.find(f".//body[@name='{s}_tool']");held(p,h,s+'_held_')
            for label,key in [('work','work_offset_m'),('mass','mass_offset_m')]:E.SubElement(p,'site',name=s+'_'+label,pos=model.fmt(ck.offset_vector(h[key])),size='.003')
        self.xml=E.tostring(tr.getroot(),encoding='unicode');self.bind_model(mujoco.MjModel.from_xml_string(self.xml));self.set_contacts(self.hands)
        self.avoid_iterations=0
    def target_rotation(self,h,k):
        if (h['held'] in ('key_handle','peeler','wash_pad','eye_core_spoon','root_food') or h['held']=='carried_bowl' and h.get('object_rotation_deg')==[0,0,0]) and k%2:
            h=dict(h,jaw_axis=(-np.array(h['jaw_axis'])).tolist())
        return ck.Checker.target_rotation(self,h,k)
    def set_contacts(self,hands):
        self.intended=set();self.allowed=[]
        for s,h in hands.items():
            for a in h.get('contacts',[]):
                if a['face'] in self.gnames:self.intended.add(self.gnames.index(a['face']));self.allowed.append(dict(side=s,**a))
    def forbidden(self,q):
        # Run the literal reference with no broad held-part exception, then apply
        # only explicitly enumerated own-support or working-edge pairs.
        intended=self.intended;self.intended=set();hits=ck.Checker.forbidden(self,q);self.intended=intended
        partmap={'root_food':['food'],'peeler':['peeler_edge','peeler_y_head'],'wash_pad':['wash_pad_contact'],'eye_core_spoon':['spoon_edge','spoon_neck_work_face'],'carried_bowl':['bowl_outer_bottom']+['bowl_outer_wall'+str(i) for i in range(16)],'cut_cassette':['cassette_floor'],'colander':['colander_shell_bottom']+['colander_shell_wall'+str(i) for i in range(16)],'food_cup':['cup_floor']}
        allowed=set()
        for c in self.allowed:
            side=c['side'];typ=self.hands[side]['held']
            parts=c['held_parts'] if isinstance(c.get('held_parts'),list) else partmap.get(typ,[])
            for part in parts:allowed.add(frozenset([c['face'],side+'_held_'+part]))
        return [h for h in hits if frozenset(h['pair']) not in allowed]
    def grip_side(self,q,h,force,moment,side):
        self.d.qpos[:]=q;mujoco.mj_kinematics(self.m,self.d)
        rt=self.d.site_xmat[self.m.site(side+'_prep').id].reshape(3,3)
        gravity=np.array([0,0,-h['held_kg']*9.81]);demand=float(np.linalg.norm(np.array(force)+gravity))
        torque=float(np.linalg.norm(np.cross(rt@ck.offset_vector(h['work_offset_m']),force)+np.cross(rt@ck.offset_vector(h['mass_offset_m']),gravity)+moment))
        if h['grip']=='friction':return dict(side=side,mode='wet_pad_friction',mu=ck.MU,normal_sum_N=ck.NORMAL_SUM_N,force_demand_N=demand,force_capacity_N=ck.MU*ck.NORMAL_SUM_N,SF=ck.MU*ck.NORMAL_SUM_N/max(demand,1e-12),margin=ck.MU*ck.NORMAL_SUM_N/(ck.SF*max(demand,1e-12)))
        margin=min(ck.KEY_FORCE_N/(ck.SF*max(demand,1e-12)),ck.KEY_MOMENT_NM/(ck.SF*max(torque,1e-12)))
        return dict(side=side,mode='positive_key_bearing',force_demand_N=demand,moment_demand_Nm=torque,bearing_capacity_N=ck.KEY_FORCE_N,moment_capacity_Nm=ck.KEY_MOMENT_NM,margin=margin,SF=ck.SF*margin)
    def initial(self,rng,k):
        q=np.array(PARK,float)
        for i,s in enumerate(model.SIDES):
            if s not in self.hands:
                active_x=np.mean([h['pos'][0] for h in self.hands.values()])
                q[self.qa[s+'_carriage_x']]=.045 if s=='L' and active_x<-1.0 else -1.7 if s=='L' else -1.6
                continue
            xs=[h[s]['pos'][0] for h in self.seg['poses'] if s in h]
            x=np.mean(xs);q[self.qa[s+'_carriage_x']]=rng.uniform(max(-1.7,x-.65),min(.2,x+.65))
            for n in ck.ARMS[s]:
                lo,hi=self.m.jnt_range[self.jid[n]];lo=max(lo,-math.pi);hi=min(hi,math.pi)
                q[self.qa[n]]=rng.uniform(lo,hi) if k%4 else np.clip(PARK[self.qa[n]]+rng.normal(0,.5),lo+1e-6,hi-1e-6)
            for label in ('minus','plus'):q[self.qa[s+'_jaw_'+label]]=self.hands[s]['jaw_opening_m']/2
        if k%3==0 and hasattr(self,'warm') and self.warm:
            base=self.warm[(k//3)%len(self.warm)]
            wn=ck.ARMS['R']+['R_carriage_x']
            if self.seg.get('action')=='helper_index':wn+=ck.ARMS['L']+['L_carriage_x']
            for n in wn:
                lo,hi=self.m.jnt_range[self.jid[n]];q[self.qa[n]]=np.clip(base[self.qa[n]]+rng.normal(0,.015 if n.endswith('carriage_x') else .04),lo+1e-7,hi-1e-7)
        self.d.qpos[:]=q;mujoco.mj_kinematics(self.m,self.d)
        return q,self.d.site_xpos[self.m.site('L_prep').id].copy()
    def solve(self,q0,hands,park,k,iters=180):
        return self.solve_least(q0,hands,k)
    def solve_least(self,q0,hands,k):
        m,d=self.m,self.d;names=sum([ck.ARMS[s] for s in hands],[])
        if self.search_carriage:names += [s+'_carriage_x' for s in hands]
        ix=[self.qa[n] for n in names];bounds=np.array([m.jnt_range[self.jid[n]] for n in names]).T
        for i,n in enumerate(names):
            if n=='R_carriage_x':bounds[1,i]=.045
        targets={s:(np.array(h['pos']),self.target_rotation(h,k)) for s,h in hands.items()};q=q0.copy();pairs={};evals=0
        def residual(x,collision=False):
            nonlocal evals
            evals+=1;q[ix]=x;d.qpos[:]=q;mujoco.mj_kinematics(m,d)
            vals=[]
            for s,(pos,rt) in targets.items():
                sid=m.site(s+'_prep').id;vals.extend((d.site_xpos[sid]-pos)*10)
                vals.extend(Rotation.from_matrix(rt.T@d.site_xmat[sid].reshape(3,3)).as_rotvec()*2.)
            if collision:
                mujoco.mj_comPos(m,d)
                for (a,b),gap in pairs.items():
                    dist=mujoco.mj_geomDistance(m,d,a,b,gap+.045,None)
                    vals.append(max(0,gap+.001-dist)*30)
            return np.array(vals)
        x=np.clip(q[ix],bounds[0]+1e-8,bounds[1]-1e-8)
        res=least_squares(residual,x,bounds=bounds,xtol=1e-7,ftol=1e-7,gtol=1e-7,max_nfev=200)
        q[ix]=res.x
        for iteration in range(4):
            hs=self.forbidden(q)
            if not hs:break
            for h in hs:pairs[tuple(self.gnames.index(n) for n in h['pair'])]=h['required_gap_mm']/1000
            res=least_squares(lambda x:residual(x,True),q[ix].copy(),bounds=bounds,xtol=1e-6,ftol=1e-6,gtol=1e-6,max_nfev=70)
            q[ix]=res.x;self.avoid_iterations+=res.nfev
        cfg=mink.Configuration(m,q=q.copy());err=[]
        for s,(pos,rt) in targets.items():
            task=mink.FrameTask(s+'_prep','site',position_cost=1.,orientation_cost=.5,lm_damping=1e-4)
            task.set_target(mink.SE3.from_rotation_and_translation(mink.SO3.from_matrix(rt),pos));e=task.compute_error(cfg)
            err.append(dict(side=s,position_mm=float(np.linalg.norm(e[:3])*1000),orientation_deg=float(np.degrees(np.linalg.norm(e[3:])))))
        return q.copy(),err
    def solve_mink(self,q0,hands,park,k,iters=180):
        # First explore a kinematic branch. Then constrain actual blocker pairs.
        q,err=super().solve(q0,hands,park,k,iters=iters)
        hits=self.forbidden(q)
        if not hits:return q,err
        m=self.m;cfg=mink.Configuration(m,q=q.copy());tasks=[];active=[]
        for s,h in hands.items():
            t=mink.FrameTask(s+'_prep','site',position_cost=1.,orientation_cost=.5,lm_damping=1e-4);t.set_target(mink.SE3.from_rotation_and_translation(mink.SO3.from_matrix(self.target_rotation(h,k)),np.array(h['pos'])));tasks.append(t);active.append((s,t))
        post=mink.PostureTask(m,cost=1e-5);post.set_target(q0.copy());tasks.append(post)
        frozen=[self.da[n] for n in ck.BASE+ck.JAWS+sum([ns for s,ns in ck.ARMS.items() if s not in hands],[])]
        freeze=mink.VelocityLimit(m,{n:0. for n in self.da if self.da[n] in frozen});pairs={}
        for it in range(100):
            hs=self.forbidden(cfg.q)
            for h in hs:pairs[tuple(h['pair'])]=h['required_gap_mm']/1000
            limits=[mink.ConfigurationLimit(m),freeze]
            for gap in sorted(set(pairs.values())):
                pp=[([a],[b]) for (a,b),d in pairs.items() if d==gap]
                limits.append(mink.CollisionAvoidanceLimit(m,pp,minimum_distance_from_collisions=gap+.001,collision_detection_distance=gap+.035,gain=.75))
            try:v=mink.solve_ik(cfg,tasks,.05,'daqp',1e-3,limits=limits)
            except Exception:break
            v[frozen]=0;cfg.integrate_inplace(v,.05);self.avoid_iterations+=1
            errors=[t.compute_error(cfg) for s,t in active]
            if not hs and all(np.linalg.norm(e[:3])<.002 and np.linalg.norm(e[3:])<.015 for e in errors):break
        err=[]
        for s,t in active:
            e=t.compute_error(cfg);err.append(dict(side=s,position_mm=float(np.linalg.norm(e[:3])*1000),orientation_deg=float(np.degrees(np.linalg.norm(e[3:])))))
        return cfg.q.copy(),err
    def torque_multi(self,q,hands,forces,moments=None):
        m,d=self.m,self.d;d.qpos[:]=q;d.qvel[:]=0;mujoco.mj_forward(m,d);tau=d.qfrc_bias.copy();jp=np.zeros((3,m.nv));jr=np.zeros_like(jp)
        for s,h in hands.items():
            mujoco.mj_jacSite(m,d,jp,jr,m.site(s+'_work').id);tau-=jp.T@np.array(forces[s])+jr.T@np.array((moments or {}).get(s,[0,0,0]))
            mujoco.mj_jacSite(m,d,jp,jr,m.site(s+'_mass').id);tau-=jp.T@np.array([0,0,-h['held_kg']*9.81])
        vals={n:float(abs(tau[self.da[n]])) for n in ck.JOINTS}
        limits=ck.LIM
        if (HERE/'results/torque_envelope.json').exists():
            env=json.loads((HERE/'results/torque_envelope.json').read_text());limits={n:dict(continuous_Nm=env['envelope_Nm'][n]) for n in ck.JOINTS}
        ratios={n:v/max(limits[n]['continuous_Nm'],1e-9) for n,v in vals.items()};j=max(ratios,key=ratios.get)
        return dict(ratio=ratios[j],joint=j,required_Nm=vals[j],reference_Nm=limits[j]['continuous_Nm'],joints=ratios,demand_Nm=vals,reference_type='rated_payload_envelope' if (HERE/'results/torque_envelope.json').exists() else 'R02_diagnostic_only',published_output_torque_ratios=None)
    def run_seed(self,k,rng):
        q,park=self.initial(rng,k);out=dict(k=k,ok=False,poses=[],hits=[],nominal=None,check=None)
        for pi,hands in enumerate(self.seg['poses']):
            self.search_carriage=pi==0 or self.seg.get('action')=='helper_index' or any(h['held'] in ('carried_bowl','colander','cut_cassette','root_food','food_cup','empty') for h in hands.values()) or self.seg['station']=='secondary'
            self.set_contacts(hands);q,err=self.solve(q,hands,park,k)
            hits=self.forbidden(q);out['poses'].append(dict(q=q.tolist(),errors=err));out['hits'] += [dict(pose=pi,**h) for h in hits]
            if any(e['position_mm']>5 or e['orientation_deg']>3 for e in err):out['blocker']=dict(kind='IK',pose=pi,errors=err);return out
            for level in ('nominal','check'):
                fs=[hands[s][level+'_forces_N'] for s in hands];ms=[hands[s][level+'_moments_Nm'] for s in hands]
                for fv in itertools.product(*fs):
                    for mv in itertools.product(*ms):
                        forces=dict(zip(hands,fv));moments=dict(zip(hands,mv));tq=self.torque_multi(q,hands,forces,moments)
                        gr=[]
                        for s,h in hands.items():
                            # Literal reference grip equation. R frame is used for R strokes.
                            g=self.grip_side(q,h,forces[s],moments[s],s);gr.append(g)
                        case=dict(torque=tq,grip=min(gr,key=lambda g:g['margin']),forces_N=forces,moments_Nm=moments)
                        if out[level] is None:out[level]=case
                        else:
                            if tq['ratio']>out[level]['torque']['ratio']:out[level]['torque']=tq
                            if case['grip']['margin']<out[level]['grip']['margin']:out[level]['grip']=case['grip']
        if out['hits']:out['blocker']=dict(kind='collision',**min(out['hits'],key=lambda h:h['real_gap_mm']-h['required_gap_mm']))
        elif out['check']['torque']['ratio']>1:out['blocker']=dict(kind='torque',**out['check']['torque'])
        elif out['check']['grip']['margin']<1:out['blocker']=dict(kind='grip',**out['check']['grip'])
        else:out['ok']=True
        return out
def run(ph,seeds,stage,labels=None):
    began=time.monotonic();parts=[]
    d=HERE/'results'/stage;d.mkdir(exist_ok=True);sd=d/'strokes';sd.mkdir(exist_ok=True)
    signature=hashlib.sha256((json.dumps(P,sort_keys=True)+json.dumps(model.CONFIG,sort_keys=True)+(HERE/'model.py').read_text()+(HERE/'solver.py').read_text()).encode()).hexdigest()
    for si,sg in enumerate(ph['segments']):
        cache=sd/(ph['id']+'__'+sg['label'].replace(' ','_')+'.json')
        if cache.exists():
            prior=json.loads(cache.read_text())
            if prior.get('signature')==signature and prior['starts']>=seeds:parts.append(prior);continue
        if labels and sg['label'] not in labels:continue
        ch=Checker(ph,sg);rng=np.random.default_rng(1000+si);rows=[]
        ch.warm=[]
        ch.warm += [np.array(pt['best']['poses'][0]['q']) for pt in parts if pt['best'].get('ok') and (sg['label'].startswith('peel_index') and pt['label'].startswith('peel_index') or sg['label'].startswith('helper_index') and pt['label'].startswith('helper_index'))]
        for oldstage in ('final5','final4','final3','full_v10','full_v7','full_v5','full_v3','mixed_v1'):
            oldfile=HERE/'results'/oldstage/(('Q04.carrot' if sg.get('action')=='helper_index' and not oldstage.startswith('final') else ph['id'])+'.json')
            if not oldfile.exists():continue
            old=json.loads(oldfile.read_text())
            for pt in old['parts']:
                if pt['best'].get('ok') and (sg.get('action')=='helper_index' or pt['label']==sg['label'] or sg['label'].startswith('peel_index') and pt['label'].startswith('peel')):
                    ch.warm.append(np.array(pt['best']['poses'][-1 if sg.get('action')=='helper_index' else 0]['q']))
            if sg['label'].startswith('peel_index') and ph['id']=='Q05.carrot':
                f=HERE/'results'/oldstage/'Q05.potato.json'
                if f.exists():
                    for pt in json.loads(f.read_text())['parts']:
                        if pt['best'].get('ok') and pt['label'].startswith('peel_index'):ch.warm.append(np.array(pt['best']['poses'][0]['q']))
        for k in range(seeds):
            rows.append(ch.run_seed(k,rng))
            if (k+1)%24==0:print(ph['id'],sg['label'],k+1,sum(r['ok'] for r in rows),round(time.monotonic()-began),flush=True)
        good=[r for r in rows if r['ok']];pool=good or [r for r in rows if r['check']] or rows
        best=min(pool,key=lambda r:r['check']['torque']['ratio'] if r['check'] else sum(e['position_mm'] for p in r['poses'] for e in p['errors']))
        part=dict(signature=signature,label=sg['label'],starts=seeds,solutions_found=len(good),verified_witnesses=len(good),best=best,rows=rows,avoidance_iterations=ch.avoid_iterations,blocker_counts=dict(Counter(r.get('blocker',{}).get('kind') for r in rows if not r['ok'])))
        parts.append(part);ck.json_write(cache,part)
    out=dict(id=ph['id'],logical_id=ph['id'].split('.')[0],ok=len(parts)==len(ph['segments']) and all(x['solutions_found']>0 for x in parts),complete=len(parts)==len(ph['segments']),starts_per_stroke=seeds,parts=parts,definition=ph,config=model.CONFIG,elapsed_s=time.monotonic()-began)
    ck.json_write(d/(ph['id']+'.json'),out)
    print(ph['id'],out['ok'],round(out['elapsed_s'],2),flush=True)
if __name__=='__main__':
    import argparse
    pa=argparse.ArgumentParser();pa.add_argument('--ids',nargs='+',required=True);pa.add_argument('--seeds',type=int,default=96);pa.add_argument('--stage',default='final');pa.add_argument('--labels',nargs='+');args=pa.parse_args()
    for ph in P['phases']:
        if ph['id'] in args.ids:run(ph,args.seeds,args.stage,args.labels)
