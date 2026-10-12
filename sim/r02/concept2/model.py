"""R02 transport/robot plumbing; original source link geometry and inertia retained."""
import sys, importlib.util, copy, json, math
sys.dont_write_bytecode=True
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import mujoco
from scipy.spatial.transform import Rotation
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
spec=importlib.util.spec_from_file_location('r01_model_readonly',ROOT/'sim/r01/concept/model.py')
OEM=importlib.util.module_from_spec(spec);spec.loader.exec_module(OEM)
T=json.loads((ROOT/'sim/r02/transport/results/transport_options.json').read_text())
P=json.loads((ROOT/'sim/r02/tools/results/process_v2.json').read_text())
SIDES=('R','L','C','D')
CONFIG=dict(transport='passing_rails_cable',arm='xArm6',count=2,height=1.23,pitch=.52,orientation='inverted',grip_extension=.11,switching=False)
RATINGS=OEM.RATINGS
fmt=OEM.fmt
box=OEM.box
quat=OEM.quat

def primitive(parent,a,prefix='',offset=(0,0,0),robot=False):
    name=prefix+a['name'];typ=a['type'];pos=np.array(a.get('center_m',[0,0,0]),float)+offset
    color=(.32,.55,.68,1) if robot else (.62,.70,.68,1)
    if typ=='box':return [box(parent,name,pos,a['size_m'],color=color,robot=robot)]
    if typ in ('cylinder_shell','cylinder') and a.get('shell',typ=='cylinder_shell'):
        # Explicit shell: conservative circumscribed polygon, not a filled bowl.
        rad=a['radius_m'];height=a['height_m'];th=a.get('thickness_m',.001)
        axis=np.array(a.get('axis_local',a.get('axis_counter',[0,0,1])))
        rot=Rotation.align_vectors([axis],[[0,0,1]])[0]
        sign=1 if 'axis_local' in a and axis[0]>.9 else -1
        nodes=[box(parent,name+'_bottom',pos+rot.apply([0,0,sign*(height/2-th/2)]),[2*rad,2*rad,th],color=color,robot=robot)]
        nodes[0].set('quat',quat(rot))
        for i in range(16):
            ang=2*math.pi*i/16
            g=box(parent,name+f'_wall{i}',pos+rot.apply([(rad-th/2)*math.cos(ang),(rad-th/2)*math.sin(ang),0]),[th,2*rad*math.tan(math.pi/16),height],color=color,robot=robot)
            g.set('quat',quat(rot*Rotation.from_euler('z',ang)));nodes.append(g)
        return nodes
    if typ=='cylinder':
        axis=a.get('axis_local',a.get('axis_counter',[0,0,1]));rot=Rotation.align_vectors([axis],[[0,0,1]])[0]
        g=ET.SubElement(parent,'geom',name=name,type='cylinder',pos=fmt(pos),quat=quat(rot),size=fmt([a['radius_m'],a['height_m']/2]),rgba=fmt(color),contype='2' if robot else '1',conaffinity='3' if robot else '2',margin='.01')
        return [g]
    if typ=='capsule':
        g=ET.SubElement(parent,'geom',name=name,type='capsule',fromto=fmt([*(np.array(a['from_m'])+offset),*(np.array(a['to_m'])+offset)]),size=str(a['radius_m']),rgba=fmt(color),contype='2' if robot else '1',conaffinity='3' if robot else '2',margin='.01');return [g]
    raise ValueError(typ)

def build(config=None):
    c=copy.deepcopy(CONFIG if config is None else config)
    if 'transport' not in c:return OEM.build(c)
    count=c['count'];arms=c.get('arms',[c['arm']]*count)
    r=ET.Element('mujoco',model='r02_'+c['transport']);ET.SubElement(r,'compiler',angle='radian',autolimits='true',inertiafromgeom='auto')
    ET.SubElement(r,'option',gravity='0 0 -9.81',integrator='implicitfast')
    v=ET.SubElement(r,'visual');ET.SubElement(v,'global',offwidth='1440',offheight='960')
    defaults=ET.SubElement(r,'default');ET.SubElement(defaults,'geom',margin='.01')
    assets=ET.SubElement(r,'asset');w=ET.SubElement(r,'worldbody');contact=ET.SubElement(r,'contact')
    for g in ET.parse(ROOT/'sim/r01/concept/sources/permanent_kitchen.xml').findall('worldbody/geom'):
        if g.get('name').startswith(('basket_','board_','cutting_board','drain_tray','knife_dock','peeler_tray')):continue
        g=copy.deepcopy(g)
        if g.get('name')=='counter_right':g.set('pos','.845 .3 .835');g.set('size','.955 .3 .015')
        w.append(g)
    for i,a in enumerate(T['geometry']['upper_cabinets']):
        lo,hi=a['x_m'];box(w,f'upper_cabinet_{i}',[(lo+hi)/2,.415,1.65],[hi-lo,.37,.6],robot=False,color=(.85,.82,.75,1))
        g=box(w,f'cabinet_door_sweep_{i}',[(lo+hi)/2,-.065,1.65],[hi-lo,.6,.6],robot=False,color=(.9,.8,.4,.03));g.set('contype','4');g.set('conaffinity','8')
    for i,a in enumerate(T['geometry']['outlet_access']):box(w,f'outlet_access_{i}',a['center_m'],a['size_m'],robot=False,color=(.8,.9,.95,.2))
    # Appliances are fixed kitchen obstacles to arms; their own mounting gap is
    # audited independently, excluding only the four explicitly designated feet.
    for a in P['layout_geometry_primitives']:
        primitive(w,a,offset=(0,0,.85),robot=False)
    root=ET.SubElement(w,'body',name='wall_anchor')
    ET.SubElement(root,'joint',name='anchor_lock',type='slide',axis='0 0 1',range='-1e-12 1e-12')
    ET.SubElement(root,'inertial',mass='.001',pos='0 0 0',diaginertia='1e-6 1e-6 1e-6')
    rail=ET.SubElement(root,'body',name='rail_structure')
    ET.SubElement(rail,'joint',name='rail_lock',type='slide',axis='0 0 1',range='-1e-12 1e-12')
    infra=[];base=['anchor_lock','rail_lock'];arm_names={};jaw_names=[];lims={};lane_data=[]
    def ib(parent,name,pos,size,mass=0):
        # Exact touching-box union, reducing long-box MPR conditioning problems.
        axis=int(np.argmax(size));n=max(1,math.ceil(size[axis]/.35))
        first=None
        for j in range(n):
            sz=np.array(size,float);ps=np.array(pos,float);sz[axis]/=n;ps[axis]+=(j-(n-1)/2)*sz[axis]
            nm=name if j==0 else name+f'_piece{j}'
            g=box(parent,nm,ps,sz,mass=(mass or .000001)/n,color=(.25,.29,.34,1));g.set('contype','8');g.set('conaffinity','7');infra.append(nm)
            if first is None:first=g
        return first
    # Fixed household power track split around sink, with wall clearance 20mm.
    for i,(lo,hi) in enumerate(((-1.77,-.72),(-.10,.66))):
        ib(rail,f'appliance_power_track_{i}',[(lo+hi)/2,.566,1.125],[hi-lo,.028,.070],.6)
        ib(rail,f'wall_mount_power_{i}',[(lo+hi)/2,.59,1.125],[.05,.02,.02],.1)
        ib(rail,f'appliance_power_adapter_{i}',[hi-.07,.5305,1.125],[.067,.043,.067],.15)
    y0=c.get('front_mount_y',-.06)
    orientations={'inverted':Rotation.from_euler('x',180),'down60':Rotation.from_euler('x',150),'down30':Rotation.from_euler('x',120),'horizontal':Rotation.from_euler('x',90),'vertical':Rotation.identity()}
    for i,(side,arm) in enumerate(zip(SIDES,arms)):
        y=y0-c['pitch']*i;z=c['height'];by=y+.225;bz=z+.04
        lane_data.append(dict(side=side,y=y,z=z,rail=i,beam_y=by,beam_z=bz))
        ib(rail,f'rail_beam_{i}',[-.38,by,bz],[2.8,.3,.05],51.16944)
        for s in (-1,1):ib(rail,f'rail_guide_{i}_{s}',[-.3,by+s*.17,z+.046],[2.4,.04,.048],2.)
        if c['transport'] in ('passing_rails_cable','passing_xz_cable'):
            ib(rail,f'cable_carrier_track_{i}',[-.3,by-.0025,z+.0795],[2.4,.245,.025],1.6)
        else:
            ib(rail,f'conductor_track_{i}',[-.3,by,z+.08],[2.4,.04,.025],1.6)
        carr=ET.SubElement(rail,'body',name=side+'_carriage',pos=fmt([0,y0 if c.get('switching') else y,z]))
        j=side+'_carriage_x';base.append(j);ET.SubElement(carr,'joint',name=j,type='slide',axis='1 0 0',range='-1.2 .7')
        if c.get('switching'):
            j=side+'_carriage_lane';base.append(j);ET.SubElement(carr,'joint',name=j,type='slide',axis='0 1 0',range=f"{-c['pitch']*(count-1)} 0")
        for part,mass in (('header',2),('front_leg',3),('rear_leg',3)):
            a=T['geometry']['carriage'];ib(carr,side+'_arch_'+part,a['arch_'+part+'_center_local_m'],a['arch_'+part+'_size_m'],mass)
        stage=carr
        if c['transport']=='passing_xz_cable':
            a=T['geometry']['carriage'];ib(carr,side+'_Z_column',a['Z_column_center_local_m'],a['Z_column_size_m'],4)
            stage=ET.SubElement(carr,'body',name=side+'_Z_stage');j=side+'_carriage_z';base.append(j)
            ET.SubElement(stage,'joint',name=j,type='slide',axis='0 0 1',range='-.18 0');ET.SubElement(stage,'inertial',mass='4',pos='0 0 0',diaginertia='.01 .01 .01')
        ib(stage,side+'_base_adapter_plate',[0,0,.0075],[.15,.15,.015],.7)
        ori=c.get('orientations',[c['orientation']]*count)[i]
        mount=ET.SubElement(stage,'body',name=side+'_mount',quat=quat(orientations[ori]))
        raw,folder=OEM.source_root(arm);a=OEM.namespaced(raw,folder,side)
        for e in a.find('default') or []:defaults.append(copy.deepcopy(e))
        for e in a.find('asset') or []:assets.append(copy.deepcopy(e))
        body=copy.deepcopy(a.find('worldbody/body'));mount.append(body)
        at=body.find(f".//site[@name='{side}_attachment_site']");par=next(b for b in body.iter('body') if at in list(b))
        ar=Rotation.from_quat(np.fromstring(at.get('quat','1 0 0 0'),sep=' ')[[1,2,3,0]]);ap=np.fromstring(at.get('pos','0 0 0'),sep=' ')
        ext=c.get('grip_extension',.11)
        tool=ET.SubElement(par,'body',name=side+'_tool',pos=fmt(ap+ar.apply([0,0,ext])),quat=quat(ar*Rotation.from_euler('y',-90)))
        ET.SubElement(tool,'inertial',mass='1',pos=fmt([.05-ext,0,0]),diaginertia='.001 .003 .003')
        box(tool,side+'_gripper_palm',[.04-ext,0,0],[.07,.08,.04])
        for sign,label in ((-1,'minus'),(1,'plus')):
            jaw=ET.SubElement(tool,'body',name=f'{side}_jaw_{label}',pos=fmt([-.02,sign*.004,0]));j=f'{side}_jaw_{label}';jaw_names.append(j)
            ET.SubElement(jaw,'joint',name=j,type='slide',axis=fmt([0,sign,0]),range='0 .045')
            ET.SubElement(jaw,'inertial',mass='.1',pos='-.015 0 0',diaginertia='.00002 .00008 .00008');box(jaw,f'{side}_finger_{label}',[-.015,0,0],[.075,.008,.02])
        ET.SubElement(tool,'site',name=side+'_prep',pos='0 0 0',size='.004')
        arm_names[side]=[j.get('name') for j in body.iter('joint') if j.get('name') not in jaw_names]
        for ex in a.findall('contact/exclude'):
            if any(b.get('name')==ex.get('body1') for b in body.iter('body')) and any(b.get('name')==ex.get('body2') for b in body.iter('body')):contact.append(copy.deepcopy(ex))
        for g in body.iter('geom'):
            if 'visual' not in g.get('class',''):g.set('contype','2');g.set('conaffinity','3');g.set('margin','.01')
        for n,val in zip(arm_names[side],RATINGS[arm]['values']):lims[n]=dict(continuous_Nm=val,provenance=RATINGS[arm]['status'])
        if c.get('switching'):
            # Declared 48V OEM DC controller and enclosure, not a tiny naked PCB.
            sz=[.282,.18,.096] if arm.startswith('xArm') else [.460,.449,.254]
            ib(carr,side+'_onboard_controller',[0,.16,.18],sz,3.1 if arm.startswith('xArm') else 12)
    front=y0-c['pitch']*(count-1)-.17
    for x in (-1.80,1.04):
        ib(rail,f'frame_top_{x}',[x,(front+.58)/2,2.10],[.04,.58-front,.1],3.)
        ib(rail,f'frame_post_{x}',[x,-.425,1.685],[.04,.04,.83],3.)
        ib(rail,f'frame_lower_{x}',[x,(front+.58)/2,1.27],[.04,.58-front,.05],3.)
        for z in (1.27,2.10):ib(rail,f'wall_mount_{x}_{z}',[x,.59,z],[.05,.02,.04],.5)
    if c.get('switching'):
        for x in (-1.5,.9):ib(rail,f'transfer_deck_{x}',[x,(y0+y0-c['pitch']*(count-1))/2,c['height']+.05],[.50,c['pitch']*(count-1)+.50,.12],15)
    if not c.get('visual',False):
        for b in w.iter('body'):
            for g in list(b.findall('geom')):
                if 'visual' in g.get('class',''):b.remove(g)
        used={g.get('mesh') for g in w.iter('geom') if g.get('mesh')}
        for a in list(assets.findall('mesh')):
            if a.get('name') not in used:assets.remove(a)
    return ET.ElementTree(r),dict(config=c,arms=arm_names,jaws=jaw_names,base=base,torque_limits=lims,disabled_robot_pairs=[],scene=json.loads((ROOT/'sim/r01/concept/sources/permanent_scene.json').read_text()),ratings={s:RATINGS[a] for s,a in zip(SIDES,arms)},infrastructure_names=infra,lanes=lane_data)
