"""Only robot and process plumbing around an unchanged R01 reference checker."""
import os,sys,copy,json,hashlib,time
sys.dont_write_bytecode=True
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[n]='1'
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import mujoco
from scipy.spatial.transform import Rotation
import reference as ck
import model
HERE=model.HERE;P=model.P;SIDES=model.SIDES
PARK_CACHE={}

def wrench_cases(hands,level):
    """Use supplied world-frame forces AND free moments; no new force value."""
    import itertools
    values=[]
    for hd in hands.values():
        fs=hd[level+'_forces_N'] or hd['nominal_forces_N']
        ms=hd.get(level+'_moments_Nm') or hd.get('nominal_moments_Nm') or [[0,0,0]]
        values.append(list(itertools.product(fs,ms)))
    for combo in itertools.product(*values):
        yield dict(zip(hands,[c[0] for c in combo])),dict(zip(hands,[c[1] for c in combo]))

def process_instances():
    out=copy.deepcopy(P['checker_instances'])
    for ph in out:
        ph['id']=ph['instance_id']
        for seg in ph['segments']:
            for hands in seg['poses']:
                for hd in hands.values():hd['pos'][2]+=.85;hd['frame']='world'
    return out

def resolve_contacts(hd):
    # Old contact identities relocated to the same physical work/support faces.
    aliases={'peeler_support':['tool_support_0','tool_support_2'],
             'peeler_tray':['tool_support_0'], 'knife_dock':['covered_tool_support'],
             'catch_dock':['catch_bowl_bottom'], 'board_clamp':['peel_endcup-1','peel_endcup1'],
             'cutting_board':['peel_fixture_tray']}
    return list(dict.fromkeys(n for name in hd['intended'] for n in aliases.get(name,[name])))

def held(parent,hd,side,product):
    typ=hd['held'];data=P['tools'][typ]
    geometry=copy.deepcopy(data['geometry'])
    if typ=='colander':
        # C06 is rectangular in the delivered CAD. Use one physical envelope
        # whether supported or held, rather than the JSON circular shorthand.
        geometry=[dict(name='colander_bottom',type='box',center_m=[.13975,0,0],size_m=[.0005,.230,.260])]
        for s in (-1,1):
            geometry += [dict(name=f'colander_wall_y{s}',type='box',center_m=[.1,s*.11475,0],size_m=[.080,.0005,.260]),dict(name=f'colander_wall_z{s}',type='box',center_m=[.1,0,s*.12975],size_m=[.080,.230,.0005]),dict(name=f'colander_rim_y{s}',type='box',center_m=[.0595,s*.11575,0],size_m=[.001,.0035,.264]),dict(name=f'colander_rim_z{s}',type='box',center_m=[.0595,0,s*.13075],size_m=[.001,.227,.0035])]
        geometry += [a for a in data['geometry'] if a['name']=='colander_key']
    for a in geometry:
        a=copy.deepcopy(a)
        if a['type']=='ingredient_box_or_ellipsoid':
            size=next(p['input_size_m'] for p in P['finished_products'] if p['product']==product)
            # Long root axis along tool Z, matching R01 held-root frame.
            a=dict(name='food',type='box',center_m=[0,0,0],size_m=[size[2],size[1],size[0]])
        gs=model.primitive(parent,a,prefix=side+'_held_',robot=True)
        for g in gs:g.set('mass','.000001')
    if typ!='root_food' and hd['held_kg']>data['mass_kg'] and typ in ('food_cup','carried_bowl','colander','cut_cassette'):
        # Full original flesh envelope: do not replace food by a small mass cube.
        sz=next(p['input_size_m'] for p in P['finished_products'] if p['product']==product)
        size=[sz[2],sz[1],sz[0]]
        if typ=='food_cup':center=[.096-size[0]/2,0,.15]
        elif typ=='carried_bowl':center=[.179-size[0]/2,0,0]
        elif typ=='colander':center=[.1395-size[0]/2,0,0]
        else:center=[.095-size[0]/2,0,0]
        gs=model.primitive(parent,dict(name='contents',type='box',center_m=center,size_m=size),prefix=side+'_held_',robot=True)
        for g in gs:g.set('mass','.000001')
    if hd['grip']=='keyed':
        for s in (-1,1):
            g=model.box(parent,side+f'_held_key_shoulder{s}',[s*.036,0,0],[.008,.046,.030]);g.set('mass','.000001')
    for label,key in (('work','work_offset_m'),('mass','mass_offset_m')):
        ET.SubElement(parent,'site',name=side+'_'+label,pos=model.fmt(ck.offset_vector(hd[key])),size='.003',rgba='.9 .15 .1 1')

class Checker(ck.Checker):
    def __init__(self,definition,seg,config):
        ck.configure(config);self.phase=definition;self.seg=copy.deepcopy(seg);self.desc=next(iter(self.seg['poses'][0].values()))
        self.config=config;self.product=definition.get('product',definition.get('products',['carrot'])[0])
        if self.product in ('all','roots'):self.product='carrot'
        if 'potato' in definition['id']:self.product='potato'
        if definition['id'].split('.')[0] in [f'Q{i:02}' for i in range(13,21)]:self.product='leafy_greens'
        if definition['id'].split('.')[0] in [f'Q{i:02}' for i in range(21,26)]:self.product='tomato'
        self.product=self.product if self.product in ('carrot','potato','leafy_greens','tomato') else 'carrot'
        tree=copy.deepcopy(ck.TEMPLATE);w=tree.getroot().find('worldbody')
        hd0=self.seg['poses'][0]
        # Do not leave a duplicate vessel at the destination of a carried vessel.
        for hd in hd0.values():
            if hd['held']=='carried_bowl' and hd['work_site'].startswith('output_'):
                target=hd['work_site'].replace('_handle','')
                for g in list(w.findall('geom')):
                    if g.get('name').startswith(target+'_'):w.remove(g)
        # Retained tools remain physically at their docks when not held.
        for typ,site in (('peeler','peeler_dock'),('wash_pad','pad_dock'),('eye_core_spoon','eyer_dock')):
            if typ in [hd['held'] for hd in hd0.values()]:continue
            pos=np.array(P['work_sites'][site])+[0,0,.85]
            b=ET.SubElement(w,'body',name='stored_'+typ,pos=model.fmt(pos),quat=model.quat(Rotation.from_matrix(ck.rotation([0,0,-1],[0,1,0]))))
            for a in P['tools'][typ]['geometry']:model.primitive(b,a,prefix='stored_'+typ+'_',robot=False)
        # Unhandled ingredients stay in supported raw tray with actual dimensions.
        # Active food is represented by held/support geometry, never duplicated.
        for i,a in enumerate(P['finished_products']):
            if a['product']==self.product:continue
            positions=[[-1.675,.09],[-1.525,.095],[-1.675,.24],[-1.525,.24]]
            pos=[*positions[i],.858+a['input_size_m'][2]/2]
            model.box(w,'stored_food_'+a['product'],pos,a['input_size_m'],robot=False,color=(.5,.65,.2,1))
        if self.seg['station']=='peel_food' and any(h['held'] in ('peeler','eye_core_spoon','wash_pad') for h in hd0.values()):
            sz=next(a['input_size_m'] for a in P['finished_products'] if a['product']==self.product)
            model.box(w,'clamped_food',[-.935,.17,.95],sz,robot=False,color=(.9,.55,.15,1))
        # C06 is the handled insert itself. Never duplicate it while it is carried.
        # Stationary C06 uses the delivered CAD rectangular260x230x80mm envelope.
        if not any(h['held']=='colander' for h in hd0.values()):
            model.box(w,'rinse_basket_bottom',[-.4,.3,.72525],[.260,.230,.0005],robot=False)
            for sign in (-1,1):
                model.box(w,f'rinse_basket_wall{0 if sign<0 else 1}',[-.4+sign*.12975,.3,.765],[.0005,.230,.080],robot=False)
                model.box(w,f'rinse_basket_wall{2 if sign<0 else 3}',[-.4,.3+sign*.11475,.765],[.260,.0005,.080],robot=False)
            for sign in (-1,1):
                model.box(w,f'rinse_basket_rim_x{sign}',[-.4+sign*.13075,.3,.8045],[.0035,.234,.001],robot=False)
                model.box(w,f'rinse_basket_rim_y{sign}',[-.4,.3+sign*.11575,.8045],[.259,.0035,.001],robot=False)
        # State-specific door, parked blade and bowl-support solids.
        powered=definition['id'].split('.')[0] in ('Q10','Q14','Q18','Q19','Q24')
        self.powered=powered
        self.closed_on_last=powered and self.seg['label'].startswith('withdraw')
        for a in P['moving_geometry_states']['front_doors']:
            pos=a['open_center_m']
            g=model.box(w,a['id'],np.array(pos)+[0,0,.85],a['size_m'],robot=False,color=(.7,.75,.8,1))
            g.set('quat',model.quat(Rotation.from_euler('z',a['rotation_open_deg'],degrees=True)))
        model.box(w,'parked_blade',[.4,.29,1.175],[.22,.003,.03],robot=False,color=(.8,.8,.8,1))
        model.box(w,'catch_bowl_bottom',[.4,.11,.88],[.20,.20,.002],robot=False)
        for side,hd in hd0.items():held(w.find(f".//body[@name='{side}_tool']"),hd,side,self.product)
        self.xml=ET.tostring(tree.getroot(),encoding='unicode');self.bind_model(mujoco.MjModel.from_xml_string(self.xml))
        # Same inherited intended-held contact branch, exact relocated surfaces.
        # Keep the literal bind_model expansion (notably rinse_basket faces).
        # Add only the explicitly relocated identities; never discard the
        # source indexed family when its original geometry names still exist.
        self.intended |= {i for i,n in enumerate(self.gnames) if n in set(resolve_contacts(self.desc))}
        self.held=np.array([n.startswith(tuple(s+'_held_' for s in SIDES)) for n in self.gnames])
        self.fixed_infra=ck.META['infrastructure_names']

    def side(self,g):
        n=self.bnames[g]
        return next((s for s in SIDES if n.startswith(s.lower()+'_')),None)

    def initial(self,rng,k):
        m=self.m;q=m.qpos0.copy();hands=self.seg['poses'][0]
        for i,(side,names) in enumerate(ck.ARMS.items()):
            xs=[p[side]['pos'][0] for p in self.seg['poses'] if side in p]
            x=float(np.mean(xs)) if xs else (-1.2 if i%2 else .7)
            q[self.qa[side+'_carriage_x']]=rng.uniform(max(-1.2,x-.65),min(.7,x+.65)) if xs else x
            if side+'_carriage_z' in self.qa:q[self.qa[side+'_carriage_z']]=rng.uniform(-.18,0) if xs else 0
            if side+'_carriage_lane' in self.qa:q[self.qa[side+'_carriage_lane']]=-(int(rng.integers(len(ck.ARMS))) if xs else i)*self.config['pitch']
            for nm in names:
                lo,hi=m.jnt_range[self.jid[nm]];q[self.qa[nm]]=(lo+hi)/2+rng.uniform(-.5,.5)*(hi-lo)*.5
            opening=hands.get(side,{}).get('jaw_opening_m',.02)
            for label in ('minus','plus'):q[self.qa[side+'_jaw_'+label]]=opening/2
        key=json.dumps(self.config,sort_keys=True)
        cache=PARK_CACHE.setdefault(key,{})
        for side,names in ck.ARMS.items():
            if side in hands:continue
            if side not in cache:
                prng=np.random.default_rng(811+SIDES.index(side));best=None;score=(999,999.)
                for attempt in range(600):
                    candidate=q.copy()
                    for nm in names:
                        lo,hi=m.jnt_range[self.jid[nm]];candidate[self.qa[nm]]=prng.uniform(lo,hi)
                    bad=[h for h in self.forbidden(candidate) if any(n.startswith(side+'_') for n in h['pair']) and not any(n.startswith(s+'_') for n in h['pair'] for s in hands)]
                    self.d.qpos[:]=candidate;self.d.qvel[:]=0;mujoco.mj_forward(m,self.d)
                    ratio=max(abs(self.d.qfrc_bias[self.da[n]])/ck.LIM[n]['continuous_Nm'] for n in names)
                    this=(len(bad),ratio)
                    if this<score:score=this;best=[candidate[self.qa[n]] for n in names]
                    if not bad and ratio<.45:break
                cache[side]=dict(joints=best,score=score)
            for nm,val in zip(names,cache[side]['joints']):q[self.qa[nm]]=val
        self.d.qpos[:]=q;mujoco.mj_kinematics(m,self.d)
        return q,self.d.site_xpos[m.site('L_prep').id].copy()

    def floor_margin(self,q):
        return min(min(q[self.qa[n]]-self.m.jnt_range[self.jid[n],0],self.m.jnt_range[self.jid[n],1]-q[self.qa[n]]) for n in ck.BASE if n.endswith('carriage_x'))

    def torque_multi(self,q,hands,forces,payload=None,moments=None):
        m,d=self.m,self.d;d.qpos[:]=q;d.qvel[:]=0;mujoco.mj_forward(m,d)
        tau=d.qfrc_bias.copy();jp=np.zeros((3,m.nv));jr=np.zeros_like(jp)
        for side,hd in hands.items():
            mujoco.mj_jacSite(m,d,jp,jr,m.site(side+'_work').id);tau-=jp.T@np.asarray(forces[side])+jr.T@np.array((moments or {}).get(side,[0,0,0]))
            mujoco.mj_jacSite(m,d,jp,jr,m.site(side+'_mass').id);tau-=jp.T@np.array([0,0,-(hd['held_kg'] if payload is None else payload)*9.81])
        ratios={n:float(abs(tau[self.da[n]])/ck.LIM[n]['continuous_Nm']) for n in ck.JOINTS};j=max(ratios,key=ratios.get)
        return dict(ratio=ratios[j],joint=j,required_Nm=float(abs(tau[self.da[j]])),reference_Nm=ck.LIM[j]['continuous_Nm'],joints=ratios)

    def grip_side(self,q,hd,force,side,moment_Nm=None):
        # Literal inherited friction/key equations, only site name becomes side.
        f=np.array(force,float)+[0,0,-hd['held_kg']*9.81];demand=float(np.linalg.norm(f))
        self.d.qpos[:]=q;mujoco.mj_kinematics(self.m,self.d);rot=self.d.site_xmat[self.m.site(side+'_prep').id].reshape(3,3)
        moment=float(np.linalg.norm(np.cross(rot@ck.offset_vector(hd['work_offset_m']),force)+np.cross(rot@ck.offset_vector(hd['mass_offset_m']),[0,0,-hd['held_kg']*9.81])+np.array([0,0,0] if moment_Nm is None else moment_Nm)))
        if hd['grip']=='friction':margin=ck.MU*ck.NORMAL_SUM_N/(ck.SF*max(demand,1e-12))
        else:margin=min(ck.KEY_FORCE_N/(ck.SF*max(demand,1e-12)),ck.KEY_MOMENT_NM/(ck.SF*max(moment,1e-12)))
        return dict(margin=margin,force_demand_N=demand,moment_demand_Nm=moment,side=side,mu=ck.MU,mode=hd['grip'])

    def environment_pose(self,pidx):
        closed=self.closed_on_last and pidx==len(self.seg['poses'])-1
        for a in P['moving_geometry_states']['front_doors']:
            g=self.m.geom(a['id']).id
            self.m.geom_pos[g]=np.array(a['closed_center_m'] if closed else a['open_center_m'])+[0,0,.85]
            self.m.geom_quat[g]=[1,0,0,0] if closed else Rotation.from_euler('z',a['rotation_open_deg'],degrees=True).as_quat()[[3,0,1,2]]

    def run_seed(self,k,rng,previous=None):
        q,park=self.initial(rng,k);out=dict(k=k,segment=self.seg['label'],poses=[],hits=[],nominal=None,check=None,ok=False)
        import itertools
        for pi,hands in enumerate(self.seg['poses']):
            self.environment_pose(pi)
            q,errors=self.solve(q,hands,park,k) # original 600-iteration Mink solve
            out['poses'].append(dict(q=q.tolist(),errors=errors,floor_margin_mm=self.floor_margin(q)*1000))
            if any(e['position_mm']>5 or e['orientation_deg']>3 for e in errors):
                out['blocker']=dict(kind='IK',pose=pi,**max(errors,key=lambda e:max(e['position_mm']/5,e['orientation_deg']/3)));return out
            out['hits'] += [dict(pose=pi,**h) for h in self.forbidden(q)]
            for level in ('nominal','check'):
                for forces,moments in wrench_cases(hands,level):
                    tq=self.torque_multi(q,hands,forces,moments=moments)
                    gr=min((self.grip_side(q,hd,forces[side],side,moments[side]) for side,hd in hands.items()),key=lambda x:x['margin'])
                    case=dict(torque=tq,grip=gr,forces_N=forces,moments_Nm=moments,pose=pi)
                    if out[level] is None:out[level]=case
                    else:
                        if tq['ratio']>out[level]['torque']['ratio']:out[level]['torque']=tq;out[level]['forces_N']=forces;out[level]['pose']=pi
                        if gr['margin']<out[level]['grip']['margin']:out[level]['grip']=gr
        if out['hits']:out['blocker']=dict(kind='collision',**min(out['hits'],key=lambda h:h['real_gap_mm']-h['required_gap_mm']))
        elif out['nominal']['torque']['ratio']>1:out['blocker']=dict(kind='torque',**out['nominal']['torque'])
        elif out['nominal']['grip']['margin']<1:out['blocker']=dict(kind='grip',**out['nominal']['grip'])
        else:out['ok']=True
        return out

def run_instance(ph,c,seeds):
    from collections import Counter
    began=time.monotonic();parts=[];best=[]
    for si,seg in enumerate(ph['segments']):
        ch=Checker(ph,seg,c);rng=np.random.default_rng(si);rows=[]
        for k in range(seeds):
            rows.append(ch.run_seed(k,rng))
            if (k+1)%24==0:print(ph['id'],seg['label'],k+1,sum(r['ok'] for r in rows),round(time.monotonic()-began),flush=True)
        good=sorted([r for r in rows if r['ok']],key=lambda r:r['nominal']['torque']['ratio'])
        ik=[r for r in rows if r.get('blocker',{}).get('kind')!='IK']
        cf=[r for r in ik if not r['hits']]
        pool=good or cf or ik
        chosen=min(pool,key=lambda r:r['nominal']['torque']['ratio']) if pool else rows[0]
        parts.append(dict(label=seg['label'],seeds=seeds,feasible_seeds=len(good),ik_seeds=len(ik),collision_free_seeds=len(cf),blocker_counts=dict(Counter(r.get('blocker',{}).get('kind') for r in rows if not r['ok'])),best=chosen,rows=rows))
    passed=all(p['feasible_seeds'] for p in parts)
    return dict(id=ph['id'],logical_id=ph['id'].split('.')[0],name=ph['name'],seeds=seeds,feasible_seeds=min(p['feasible_seeds'] for p in parts),ok=passed,
        conditional_reference_admission=passed,binding_rated_admission=False,
        best_torque_ratio=max(p['best']['nominal']['torque']['ratio'] for p in parts if p['best']['nominal']) if any(p['best']['nominal'] for p in parts) else None,
        best_torque_is_feasible=passed,parts=parts,definition=ph,config=c,elapsed_s=time.monotonic()-began)
