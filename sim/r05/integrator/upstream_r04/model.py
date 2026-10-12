"""R03 integrated cell. OEM arm geometry/inertias are copied without scaling."""
import copy,json,math
from pathlib import Path
import xml.etree.ElementTree as E
import numpy as np
from scipy.spatial.transform import Rotation
import oem_model as OEM
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SIDES=('R','L')
CONFIG=dict(arm='UR5e+xArm6',arms=['UR5e','xArm6'],count=2,height=1.23,helper_height=1.60,helper_mount_deg=225,pitch=.45,front_mount_y=-.10,orientation='main_tilt152p114_helper_tilt225',mount_deg=math.degrees(210)%360,grip_extension=.11,helper_gripper_total_mass_kg=1.5,helper_opening_m=.110)
fmt=OEM.fmt;box=OEM.box;quat=OEM.quat
def splitbox(p,n,pos,size,**kw):
    ax=int(np.argmax(size));num=max(1,math.ceil(size[ax]/.30));out=[]
    for i in range(num):
        s=np.array(size,float);v=np.array(pos,float);s[ax]/=num;v[ax]+=(i-(num-1)/2)*s[ax]
        opts=dict(kw)
        if 'mass' in opts:opts['mass']/=num
        out.append(box(p,n+('' if i==0 else f'_piece{i}'),v,s,**opts))
    return out
def shell(p,n,pos,size,th=.002,robot=False):
    # Open top rectangular vessel, physical bottom and four walls.
    x,y,z=size;px,py,pz=pos
    out=[box(p,n+'_bottom',[px,py,pz-z/2+th/2],[x,y,th],robot=robot)]
    for sign in (-1,1):
        out.append(box(p,n+f'_x{sign}',[px+sign*(x-th)/2,py,pz],[th,y,z],robot=robot))
        out.append(box(p,n+f'_y{sign}',[px,py+sign*(y-th)/2,pz],[x-2*th,th,z],robot=robot))
    return out
def primitive(p,a,prefix='',robot=False):
    n=prefix+a['name'];typ=a['type'];pos=np.array(a.get('center_m',[0,0,0]),float)
    if typ=='box':return [box(p,n,pos,a['size_m'],robot=robot)]
    if typ=='capsule':return [E.SubElement(p,'geom',name=n,type='capsule',fromto=fmt(a['from_m']+a['to_m']),size=str(a['radius_m']),margin='.01',contype='2' if robot else '1',conaffinity='3' if robot else '2')]
    if typ in ('cylinder','cylinder_shell'):
        rot=Rotation.align_vectors([a.get('axis_local',[0,0,1])],[[0,0,1]])[0];rad=a['radius_m'];h=a['height_m'];th=a.get('thickness_m',.001)
        if a.get('shell',typ=='cylinder_shell'):
            g=box(p,n+'_bottom',pos+rot.apply([0,0,h/2-th/2]),[2*rad,2*rad,th],robot=robot);g.set('quat',quat(rot));out=[g]
            for i in range(16):
                ang=2*math.pi*i/16;g=box(p,n+f'_wall{i}',pos+rot.apply([(rad-th/2)*math.cos(ang),(rad-th/2)*math.sin(ang),0]),[th,2*rad*math.tan(math.pi/16),h],robot=robot);g.set('quat',quat(rot*Rotation.from_euler('z',ang)));out.append(g)
            return out
        return [E.SubElement(p,'geom',name=n,type='cylinder',pos=fmt(pos),quat=quat(rot),size=fmt([rad,h/2]),margin='.01',contype='2' if robot else '1',conaffinity='3' if robot else '2')]
    raise ValueError(typ)
def build(config=None):
    c=copy.deepcopy(CONFIG if config is None else config)
    r=E.Element('mujoco',model='R03_integrated');E.SubElement(r,'compiler',angle='radian',autolimits='true')
    E.SubElement(r,'option',gravity='0 0 -9.81',integrator='implicitfast')
    v=E.SubElement(r,'visual');E.SubElement(v,'global',offwidth='1440',offheight='960')
    defaults=E.SubElement(r,'default');E.SubElement(defaults,'geom',margin='.01')
    assets=E.SubElement(r,'asset');w=E.SubElement(r,'worldbody');contact=E.SubElement(r,'contact')
    removable=('basket_','board_','cutting_board','drain_tray','knife_dock','peeler_tray')
    for g0 in E.parse(HERE/'sources/permanent_kitchen.xml').findall('worldbody/geom'):
        if g0.get('name').startswith(removable):continue
        g=copy.deepcopy(g0)
        if g.get('name')=='counter_right':g.set('pos','.845 .3 .835');g.set('size','.955 .3 .015')
        # Subdivide long aligned solids; same exact union, no geometric shrink.
        if g.get('type')=='box' and g.get('name')!='north_wall' and max(np.fromstring(g.get('size'),sep=' '))>.35:
            splitbox(w,g.get('name'),np.fromstring(g.get('pos'),sep=' '),2*np.fromstring(g.get('size'),sep=' '),robot=False,color=(.65,.65,.65,1))
        else:w.append(g)
    for i,(lo,hi) in enumerate(((-1.8,-.7),(-.1,.69),(1.47,1.8))):
        splitbox(w,f'upper_cabinet_{i}',[(lo+hi)/2,.415,1.65],[hi-lo,.37,.6],robot=False,color=(.85,.82,.75,1))
        for g in splitbox(w,f'cabinet_door_sweep_{i}',[(lo+hi)/2,-.065,1.65],[hi-lo,.6,.6],robot=False):g.set('contype','4');g.set('conaffinity','8')
    for i,x in enumerate((-.9,.15)):box(w,f'outlet_access_{i}',[x,.56,1.01],[.10,.08,.08],robot=False)
    # Protected stove volume retained above the physical stove.
    box(w,'protected_stove',[1.076,.30,1.10],[.772,.60,.50],robot=False,color=(.7,.3,.2,.1))
    root=E.SubElement(w,'body',name='wall_anchor');E.SubElement(root,'joint',name='anchor_lock',type='slide',axis='0 0 1',range='-1e-12 1e-12')
    E.SubElement(root,'inertial',mass='.001',pos='0 0 0',diaginertia='1e-6 1e-6 1e-6')
    rail=E.SubElement(root,'body',name='rail_structure');E.SubElement(rail,'joint',name='rail_lock',type='slide',axis='0 0 1',range='-1e-12 1e-12')
    infra=[];base=['anchor_lock','rail_lock'];arms={};jaws=[];lims={};lanes=[]
    def ib(p,n,pos,size,mass=0):
        gs=splitbox(p,n,pos,size,mass=mass or .000001)
        for g in gs:g.set('contype','8');g.set('conaffinity','7');infra.append(g.get('name'))
    for i,(lo,hi) in enumerate(((-1.76,-.74),(-.05,.66))):
        ib(rail,f'appliance_power_track_{i}',[(lo+hi)/2,.566,1.16],[hi-lo,.028,.070],.6)
        ib(rail,f'wall_mount_power_{i}',[(lo+hi)/2,.59,1.16],[.05,.02,.02],.1)
        ib(rail,f'appliance_power_adapter_{i}',[hi-.07,.5305,1.16],[.067,.043,.067],.15)
    ori=Rotation.from_euler('x',c.get('mount_deg',180 if c['orientation']=='inverted' else 120),degrees=True)
    for i,side in enumerate(SIDES):
        arm=c.get('arms',['xArm6','xArm6'])[i]
        y=c['front_mount_y']-c['pitch']*i;z=c.get('helper_height',c['height']) if i else c['height'];by=y-.40
        lanes.append(dict(side=side,base_y=y,base_z=z,beam_y=by))
        # Same R02 300x50 beam union, relocated behind the base.
        ib(rail,f'rail_beam_{i}',[-.75,by,z+.04],[2.8,.3,.05],51.16944)
        for s in (-1,1):ib(rail,f'rail_guide_{i}_{s}',[-.75,by+s*.17,z+.046],[2.4,.04,.048],2.)
        ib(rail,f'cable_chain_swept_cover_{i}',[-.75,by-.05,z+.0795],[2.4,.245,.025],1.6)
        carr=E.SubElement(rail,'body',name=side+'_carriage',pos=fmt([0,y,z]))
        j=side+'_carriage_x';base.append(j);E.SubElement(carr,'joint',name=j,type='slide',axis='1 0 0',range='-1.7 .2')
        # Cantilever adapter replaces R02 overhead arch/header; a new sized part.
        ib(carr,side+'_adapter',[0,-.2025,.010],[.26,.555,.02],4.4)
        ib(carr,side+'_bearing_bridge',[0,-.40,.065],[.34,.40,.03],5.)
        ib(carr,side+'_rail_drive_brake',[.18,-.515,.070],[.10,.11,.10],1.5)
        mountori=Rotation.from_euler('x',c.get('helper_mount_deg',c.get('mount_deg',152.1136977473)),degrees=True) if i else ori
        mount=E.SubElement(carr,'body',name=side+'_mount',quat=quat(mountori))
        raw,folder=OEM.source_root(arm);a=OEM.namespaced(raw,folder,side)
        for e in a.find('default') or []:defaults.append(copy.deepcopy(e))
        for e in a.find('asset') or []:
            q=copy.deepcopy(e)
            if q.tag=='mesh' and arm=='xArm6':
                file=Path(q.get('file'));target=HERE/'sources'/('end_tool' if file.name=='end_tool.stl' else 'xarm6_meshes')/('collision' if file.name=='end_tool.stl' else 'visual')/file.name
                q.set('file',str(target))
            assets.append(q)
        body=copy.deepcopy(a.find('worldbody/body'));mount.append(body)
        # R04 restores both original unscaled UR5e base meshes as collision
        # geometry. The explicit source inertia is unchanged.
        if arm=='UR5e':
            for bi,bg in enumerate(body.findall('geom')):
                bg.attrib.pop('class',None)
                bg.set('name',side+'_geom_base_source'+str(bi))
                bg.set('type','mesh');bg.set('mass','1e-9')
        at=body.find(f".//site[@name='{side}_attachment_site']");par=next(b for b in body.iter('body') if at in list(b))
        ar=Rotation.from_quat(np.fromstring(at.get('quat','1 0 0 0'),sep=' ')[[1,2,3,0]])
        ap=np.fromstring(at.get('pos','0 0 0'),sep=' ')
        ext=c['grip_extension'];tool=E.SubElement(par,'body',name=side+'_tool',pos=fmt(ap+ar.apply([0,0,ext])),quat=quat(ar*Rotation.from_euler('y',-90)))
        E.SubElement(tool,'inertial',mass='1.3' if i else '1',pos=fmt([.05-ext,0,0]),diaginertia='.0015 .004 .004' if i else '.001 .003 .003')
        box(tool,side+'_gripper_palm',[.04-ext,0,0],[.07,.10 if i else .08,.04])
        for sign,label in ((-1,'minus'),(1,'plus')):
            jaw=E.SubElement(tool,'body',name=side+'_jaw_'+label,pos=fmt([-.02,sign*.004,0]));j=side+'_jaw_'+label;jaws.append(j)
            E.SubElement(jaw,'joint',name=j,type='slide',axis=fmt([0,sign,0]),range='0 .055' if i else '0 .045')
            E.SubElement(jaw,'inertial',mass='.1',pos='-.015 0 0',diaginertia='.00002 .00008 .00008');box(jaw,side+'_finger_'+label,[-.015,0,0],[.075,.008,.02])
        E.SubElement(tool,'site',name=side+'_prep',pos='0 0 0',size='.004')
        arms[side]=[j.get('name') for j in body.iter('joint') if j.get('name') not in jaws]
        # Public current ranges, narrower than imported legacy model.
        if arm=='xArm6':
            for j,rg in zip([b for b in body.iter('joint') if b.get('name') in arms[side]], [(-360,360),(-117,116),(-219,10),(-360,360),(-97,180),(-360,360)]):j.set('range',fmt(np.radians(rg)))
        if arm=='UR5e':
            body.find(f".//joint[@name='{side}_elbow_joint']").set('range',fmt(np.radians([-160,160])))
        for ex in a.findall('contact/exclude'):contact.append(copy.deepcopy(ex))
        for b in body.iter('body'):
            for g in list(b.findall('geom')):
                if 'visual' in g.get('class',''):b.remove(g)
                else:g.set('contype','2');g.set('conaffinity','3');g.set('margin','.01')
        for n,val in zip(arms[side],[64,64,32,32,12,12]):lims[n]=dict(continuous_Nm=val,provenance='diagnostic_initial_only')
    # Wall supports terminate below cabinet doors; uprights at free end strips.
    for x in (-1.84,.18):
        rear=lanes[-1]['beam_y']
        ib(rail,f'wall_crossbar_{x}',[x,(.58+rear)/2,1.28],[.055,.58-rear,.06],10.)
        pad_x=x+.10 if x>0 else x
        ib(rail,f'wall_mount_{x}',[pad_x,.59,1.13],[.10,.02,.30],4.71)
        if x>0:ib(rail,'wall_mount_offset_connector',[x+.05,.59,1.27],[.16,.02,.05],.4)
        for i,l in enumerate(lanes):
            low=l['base_z']+.04
            ib(rail,f'lane_hanger_{i}_{x}',[x,l['beam_y'],(1.28+low)/2],[.055,.10,abs(1.28-low)+.06],6. if i else 2.)
    # No appliances in the transport-only probe; integrated fixtures added by process.
    if (HERE/'results/process_v3.json').exists() and not c.get('transport_only'):
        p=json.loads((HERE/'results/process_v3.json').read_text())
        for a in p['installed_geometry']:
            if a['type']=='box':box(w,a['name'],a['pos'],a['size'],robot=False,color=a.get('rgba',(.5,.65,.6,1)))
            elif a['type']=='shell':shell(w,a['name'],a['pos'],a['size'],robot=False)
    used={g.get('mesh') for g in w.iter('geom') if g.get('mesh')}
    for a in list(assets.findall('mesh')):
        if a.get('name') not in used:assets.remove(a)
    return E.ElementTree(r),dict(config=c,arms=arms,jaws=jaws,base=base,torque_limits=lims,disabled_robot_pairs=[],scene=json.loads((HERE/'sources/permanent_scene.json').read_text()),ratings={s:OEM.RATINGS[a] for s,a in zip(SIDES,c.get('arms',['xArm6','xArm6']))},infrastructure_names=infra,lanes=lanes)
