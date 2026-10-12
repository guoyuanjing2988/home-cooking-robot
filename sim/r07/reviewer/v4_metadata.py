from v4_common import *
import hashlib,collections
R05=I.parents[1]/'r05/integrator';old=mujoco.MjModel.from_xml_path(str(R05/'models/witnesses/Q01__water_on.xml'));ch=v.scene(0);new=ch.m
names={mujoco.mj_id2name(old,mujoco.mjtObj.mjOBJ_GEOM,i):i for i in range(old.ngeom)};fixed=[]
for j,n in enumerate(ch.gnames):
    if n not in names or not n.startswith(('north_wall','upper_cabinet','counter','sink','stove','floor','south_wall')):continue
    i=names[n];keys=('geom_type','geom_size','geom_pos','geom_quat');fixed.append(dict(name=n,unchanged=all(np.array_equal(getattr(old,k)[i],getattr(new,k)[j]) for k in keys)))
bodies=[dict(name=mujoco.mj_id2name(new,mujoco.mjtObj.mjOBJ_BODY,i),mass_kg=float(new.body_mass[i])) for i in range(new.nbody)]
dimensions={n:(2*new.geom_size[i]).tolist() for i,n in enumerate(ch.gnames) if n in ('bfp610_complete_envelope','rotato_complete_guard_reservation','north_wall','rail_beam_0')}
seq=read('state_sequence.json');errors=[]
for e in seq['events']:
    for label in ('state_before','state_after'):
        st=e[label]
        if st['food_mass_kg']!=seq['initial_state']['food_mass_kg']:errors.append([e['id'],label,'mass'])
        if len(st['owners'])!=len(seq['initial_state']['owners']):errors.append([e['id'],label,'object count'])
model=mujoco.MjModel.from_xml_path(str(I/'models/persistent_meal.xml'))
policies=[]
from types import SimpleNamespace
for i in (5,20):
    cc=v.scene(i);cc.set_contacts(v.items[i][1]['poses'][0]);mujoco.mj_forward(cc.m,cc.d);c=cc.allowed[0];g=cc.gnames.index(c['face']);part=cc.gnames.index('R_held_'+c['held_parts'][0]);rot=cc.d.geom_xmat[g].reshape(3,3);center=cc.d.geom_xpos[g];sz=cc.m.geom_size[g]
    for name,p,n,expected in [('front',[0,0,sz[2]],[0,0,1],True),('back',[0,0,-sz[2]],[0,0,-1],False),('side',[sz[0],0,0],[1,0,0],False)]:
        ct=SimpleNamespace(geom=[g,part],pos=center+rot@p,frame=np.r_[rot@n,np.zeros(6)]);answer=f.intentional(cc,ct);policies.append(dict(index=i,test=name,answer=answer,expected=expected,pass_=answer==expected))
    cc.allowed=[dict(c,object_id='wrong')];policies.append(dict(index=i,test='wrong_identity',pass_=not f.intentional(cc,SimpleNamespace(geom=[g,part],pos=center+rot@np.array([0,0,sz[2]]),frame=np.r_[rot[:,2],np.zeros(6)]))))
dump('metadata.json',dict(fixed_kitchen=fixed,all_fixed_unchanged=all(r['unchanged'] for r in fixed),compiled_bodies=bodies,helper_bodies=[b for b in bodies if b['name'] and b['name'].startswith('L_')],dimensions_m=dimensions,meal_mass_errors=errors,executed_state_is_initial=seq['executed_state']==seq['initial_state'],persistent_food_bodies=[mujoco.mj_id2name(model,mujoco.mjtObj.mjOBJ_BODY,i) for i in range(model.nbody) if mujoco.mj_id2name(model,mujoco.mjtObj.mjOBJ_BODY,i).startswith('meal_food_')],event_names=[e['name'] for e in seq['events'] if 'half' in e['name'] or 'BFP610' in e['name']],rotated_contact_probes=policies,model_hash=hashlib.sha256(ch.xml.encode()).hexdigest()))
print('METADATA',len(fixed),all(r['unchanged'] for r in fixed),all(p['pass_'] for p in policies),len(errors))
