"""Physical signed-distance transport screen, OEM collision shapes, no added ACM."""
import json,copy,importlib.util,math
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np,mujoco
from scipy.spatial.transform import Rotation
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=HERE/'results'
D=json.loads((OUT/'transport_options.json').read_text());F=D['geometry']['carriage']['folded']
def box(p,name,center,size,rgba='0.3 0.4 0.45 1'):
    return ET.SubElement(p,'geom',name=name,type='box',pos=' '.join(map(str,center)),size=' '.join(str(x/2) for x in size),rgba=rgba,margin='0')
def make(v):
    root=ET.Element('mujoco',model=v['id']);ET.SubElement(root,'compiler',angle='radian',autolimits='true');ET.SubElement(root,'option',gravity='0 0 -9.81')
    defaults=ET.SubElement(root,'default');assets=ET.SubElement(root,'asset');world=ET.SubElement(root,'worldbody')
    env=[];robot=[];arms=[];mounts=[]
    def eb(name,c,s):box(world,name,c,s);env.append(name)
    kitchen=ET.parse(ROOT/'sim/r01/concept/sources/permanent_kitchen.xml').getroot()
    for g in kitchen.findall('worldbody/geom'):
        name=g.get('name')
        if name.startswith(('basket_','board_','cutting_board','drain_tray','knife_dock','peeler_tray')):continue
        if name=='floor':continue
        g=copy.deepcopy(g);g.set('margin','0');world.append(g);env.append(name)
    for i,c in enumerate(D['geometry']['upper_cabinets']):
        x=c['x_m'];eb(f'upper_{i}',[(x[0]+x[1])/2,.415,1.65],[x[1]-x[0],.37,.6])
        y=c['door_sweep_y_m'];eb(f'door_sweep_{i}',[(x[0]+x[1])/2,sum(y)/2,1.65],[x[1]-x[0],y[1]-y[0],.6])
    for i,c in enumerate(D['geometry']['outlet_access']):eb(f'outlet_{i}',c['center_m'],c['size_m'])
    # Conservative whole-fixture boxes reproduce T08 assembly footprints/heights.
    stations=[('board',[.08,.19,.8675],[.315,.295,.035]),('mandoline',[.47,.1413,.9025],[.345,.1606,.105]),('wedger',[.39,.48,1.0913],[.280,.216,.4826]),('bowl',[0,.47,.897],[.204,.204,.094]),('peeler',[.59,.41,.9337],[.09,.16,.1674]),('basket',[-1.53,.20,.9375],[.42,.34,.175]),('spinner',[-1.125,.20,.951],[.27,.27,.202]),('knife',[-1.005,.475,.935],[.36,.10,.170])]
    for n,c,s in stations:eb('fixture_'+n,c,s)
    spec=importlib.util.spec_from_file_location('r01_model_read_only',ROOT/'sim/r01/concept/model.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    raw,folder=module.source_root('UR5e')
    common=ET.SubElement(world,'body',name='transport_fixed_frame')
    ET.SubElement(common,'joint',name='frame_lock',type='slide',axis='0 0 1',range='-1e-12 1e-12')
    ET.SubElement(common,'inertial',mass='1',pos='0 0 0',diaginertia='1 1 1')
    front=min(r['beam_center_y_m'] for r in v['rails'])-.15
    for x in D['geometry']['mount']['support_x_m']:
        for suffix,c,s in [('upper_cross',[x,(front+.58)/2,2.10],[.04,.58-front,.10]),('post',[x,-.425,1.685],[.04,.04,.83]),('lower_end',[x,(front+.58)/2,1.27],[.04,.58-front,.05])]:
            name='frame_'+suffix+'_'+str(x);box(common,name,c,s);robot.append(name)
    for r in v['rails']:
        i=int(r['id'].split('_')[-1])-1;y=r['arm_mount_y_m'];prefix=f'A{i}_'
        # Fixed transport parts live on a separate locked robot root, not environment weld.
        rb=ET.SubElement(common,'body',name=prefix+'railroot')
        box(rb,prefix+'beam',[-.38,r['beam_center_y_m'],r['beam_center_z_m']],r['beam_size_m']);robot.append(prefix+'beam')
        # HGH square blocks have48mm width; mounted sideways, width becomes z.
        for sign in [-1,1]:
            gy=r['beam_center_y_m']+sign*r['guide_pair_spacing_m']/2
            box(rb,prefix+'guide_'+str(sign),[-.30,gy,r['guide_z_center_m']],[2.4,.040,.048]);robot.append(prefix+'guide_'+str(sign))
        c=r['chain'];box(rb,prefix+'chain_sweep',[-.30,sum(c['swept_y_m'])/2,sum(c['swept_z_m'])/2],[2.4,c['swept_y_m'][1]-c['swept_y_m'][0],c['swept_z_m'][1]-c['swept_z_m'][0]]);robot.append(prefix+'chain_sweep')
        carr=ET.SubElement(rb,'body',name=prefix+'carriage',pos=f"0 {y} {r['arm_mount_z_m']}")
        ET.SubElement(carr,'joint',name=prefix+'x',type='slide',axis='1 0 0',range='-1.20 .70')
        ET.SubElement(carr,'inertial',mass='8',pos='0 .1 .02',diaginertia='.03 .03 .03')
        for part in ['header','front_leg','rear_leg']:
            name=prefix+'arch_'+part;box(carr,name,D['geometry']['carriage']['arch_'+part+'_center_local_m'],D['geometry']['carriage']['arch_'+part+'_size_m']);robot.append(name)
        stage=carr
        if v['vertical_slide']['enabled']:
            box(carr,prefix+'Z_column',D['geometry']['carriage']['Z_column_center_local_m'],D['geometry']['carriage']['Z_column_size_m']);robot.append(prefix+'Z_column')
            stage=ET.SubElement(carr,'body',name=prefix+'Z_stage')
            ET.SubElement(stage,'joint',name=prefix+'z',type='slide',axis='0 0 1',range='-.18 0')
            ET.SubElement(stage,'inertial',mass='4',pos='0 0 0',diaginertia='.01 .01 .01')
        box(stage,prefix+'flange_plate',[0,0,.0075],[.15,.15,.015]);robot.append(prefix+'flange_plate')
        arm=module.namespaced(raw,folder,f'A{i}')
        for e in arm.find('default'):defaults.append(copy.deepcopy(e))
        for e in arm.find('asset'):assets.append(copy.deepcopy(e))
        ar=copy.deepcopy(arm.find('worldbody/body'));ar.set('quat','0 1 0 0');stage.append(ar)
        for b in ar.iter('body'):
            for geom in list(b.findall('geom')):
                if 'visual' in geom.get('class',''):b.remove(geom);continue
                if not geom.get('name'):geom.set('name',prefix+'collision_'+str(len(robot)))
                geom.set('margin','0');robot.append(geom.get('name'))
        ET.SubElement(ar,'geom',name=prefix+'base_proxy',type='cylinder',pos='0 0 .04',size='.075 .04',rgba='.25 .30 .36 1');robot.append(prefix+'base_proxy')
        arms.append([j.get('name') for j in ar.iter('joint')])
        attach=ar.find(f".//site[@name='A{i}_attachment_site']")
        parent=next(b for b in ar.iter('body') if attach in list(b))
        arot=Rotation.from_quat(np.fromstring(attach.get('quat'),sep=' ')[[1,2,3,0]])
        ap=np.fromstring(attach.get('pos'),sep=' ')
        gr=ET.SubElement(parent,'body',name=prefix+'tool',pos=' '.join(map(str,ap+arot.apply([0,0,.14]))),quat=' '.join(map(str,(arot*Rotation.from_euler('y',-90)).as_quat()[[3,0,1,2]])))
        box(gr,prefix+'gripper_palm',[-.10,0,0],[.07,.08,.04]);robot.append(prefix+'gripper_palm')
        for sign in [-1,1]:
            name=prefix+'finger_'+str(sign);box(gr,name,[-.035,sign*.019,0],[.075,.008,.02]);robot.append(name)
    # Only source collision primitives, no render meshes needed.
    used={g.get('mesh') for g in root.iter('geom') if g.get('mesh')}
    for a in list(assets.findall('mesh')):
        if a.get('name') not in used:assets.remove(a)
    path=OUT/(v['id']+'.xml');ET.ElementTree(root).write(path,encoding='unicode')
    m=mujoco.MjModel.from_xml_path(str(path));d=mujoco.MjData(m)
    for names in arms:
        for name,q in zip(names,F['q_rad']):d.qpos[m.jnt_qposadr[m.joint(name).id]]=q
    return m,d,env,robot,arms
def evaluate(v):
    m,d,env,robot,arms=make(v)
    ei=[m.geom(n).id for n in env];ri=[m.geom(n).id for n in robot]
    worst_env=(.05,None);worst_cross=(.05,None);worst_self=(.05,None)
    def lower_gap(a,b):
        def bounds(g):
            R=d.geom_xmat[g].reshape(3,3);s=m.geom_size[g];typ=int(m.geom_type[g]);p=d.geom_xpos[g]
            if typ==3:ext=np.abs(R[:,2])*s[1]+s[0]
            elif typ==5:ext=np.sqrt(np.maximum(0,1-R[:,2]**2))*s[0]+np.abs(R[:,2])*s[1]
            elif typ==6:ext=np.abs(R)@s
            else:ext=np.full(3,s[0])
            return p-ext,p+ext
        al,ah=bounds(a);bl,bh=bounds(b)
        return float(np.linalg.norm(np.maximum(0,np.maximum(al-bh,bl-ah))))
    def distance(a,b):
        lb=lower_gap(a,b)
        # A positive AABB separation is a conservative geometric distance lower
        # bound, not an ACM exemption. Avoid MuJoCo3.2.5 far-pair cylinder/long-box
        # MPR distance anomalies. Near/overlapping AABBs use native signed distance.
        return min(lb,.05) if lb>=.01 else float(mujoco.mj_geomDistance(m,d,a,b,.05,None))
    # Same-x crossing and complete individual travel sweeps with other arms parked.
    states=[[-1.20]*v['rail_count'],[.70]*v['rail_count'],[-.30]*v['rail_count']]
    for i in range(v['rail_count']):
        for x in np.linspace(-1.20,.70,17):
            a=[-.30]*v['rail_count'];a[i]=float(x);states.append(a)
    for state in states:
        for i,x in enumerate(state):d.qpos[m.jnt_qposadr[m.joint(f'A{i}_x').id]]=x
        mujoco.mj_forward(m,d)
        for a in ri:
            for b in ei:
                dist=distance(a,b)
                if dist<worst_env[0]:worst_env=(dist,[m.geom(a).name,m.geom(b).name,state])
        for k,a in enumerate(ri):
            sa=m.geom(a).name.split('_')[0]
            for b in ri[k+1:]:
                sb=m.geom(b).name.split('_')[0]
                ba=int(m.geom_bodyid[a]);bb=int(m.geom_bodyid[b]);wa=int(m.body_weldid[ba]);wb=int(m.body_weldid[bb])
                if wa==wb or m.body_weldid[m.body_parentid[wa]]==wb or m.body_weldid[m.body_parentid[wb]]==wa:continue
                dist=distance(a,b)
                if sa==sb:
                    if dist<worst_self[0]:worst_self=(dist,[m.geom(a).name,m.geom(b).name,state])
                elif dist<worst_cross[0]:worst_cross=(dist,[m.geom(a).name,m.geom(b).name,state])
    d.qpos[m.jnt_qposadr[m.joint('A0_x').id]]=-1.0
    for i in range(1,v['rail_count']):d.qpos[m.jnt_qposadr[m.joint(f'A{i}_x').id]]=-1.0+.70*i
    mujoco.mj_forward(m,d)
    geoms=[]
    for i in range(m.ngeom):
        geoms.append(dict(name=m.geom(i).name,type=int(m.geom_type[i]),size=m.geom_size[i].tolist(),position=d.geom_xpos[i].tolist(),rotation=d.geom_xmat[i].reshape(3,3).tolist()))
    (OUT/(v['id']+'_draw.json')).write_text(json.dumps(dict(variant=v,geoms=geoms),indent=2),encoding='utf-8')
    return dict(variant=v['id'],sample_states=len(states),minimum_robot_environment_gap_lower_bound_m=worst_env[0],environment_witness=worst_env[1],minimum_different_lane_robot_gap_lower_bound_m=worst_cross[0],crossing_witness=worst_cross[1],minimum_same_lane_self_gap_m=worst_self[0],self_witness=worst_self[1],screen_pass=bool(worst_env[0]>=.01-1e-9 and worst_cross[0]>=.01-1e-9 and worst_self[0]>=-1e-9),same_arm_self_gap_from_fold_m=F['minimum_nonadjacent_self_gap_m'],distance_method='Conservative AABB lower bound when >=10mm; native signed distance for near pairs; values above50mm censored.',limitations='Sampled static empty folded transport, unchanged R01 gripper, conservative full station/chain boxes. No process IK, jaw grip, continuous trajectory, dynamic brakes or controller claim. Only inherited same-weld/parent-weld skips; same-lane self nonpenetration and different-lane10mm retained.')
if __name__=='__main__':
    records=[evaluate(v) for v in D['geometry']['variants'] if v['carriage_count'] in (2,3)]
    (OUT/'geometry_check.json').write_text(json.dumps(records,indent=2),encoding='utf-8');print(json.dumps(records,indent=2))
