"""Real model import and fixed kitchen / independent wall carriage plumbing."""
import copy,json,math
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import mujoco
from scipy.spatial.transform import Rotation
HERE=Path(__file__).resolve().parent
SOURCES=HERE/'sources'
MODEL_FILES={'UR5e':('universal_robots_ur5e','ur5e.xml'),
 'xArm7':('ufactory_xarm7','xarm7.xml'),'FR3':('franka_fr3','fr3.xml')}
SIDES=('R','L','C')
CONFIG=dict(arm='xArm7',count=2,height=.30,orientation='horizontal',standoff=.15)
# Output-side *rated* torques = manufacturer motor rated torque x transmission,
# without overload multiplier. Older <=1304 generation matches Menagerie mass model.
RATINGS={'xArm7':dict(values=[64,64,32,32,32,12,12],status='rated_motor_times_100_gearing_ideal',
 source='https://docs.supportarticle.ufactory.cc/support_articles/hardware/ufactory-joint-parameters.html',
 note='<=1304 hardware. Published motor-rated 0.64,0.64,0.32,0.32,0.32,0.12,0.12 Nm; 100:1. Gear efficiency/thermal output certification unavailable.'),
 'UR5e':dict(values=[150,150,150,28,28,28],status='maximum_only_not_continuous',
 source='https://forum.universal-robots.com/t/maximum-axis-speed-acceleration/13338',note='Official staff maximums; diagnostic only, not binding continuous ratings.'),
 'FR3':dict(values=[87,87,87,87,12,12,12],status='maximum_only_not_continuous',
 source='https://support.franka.de/docs/control_parameters.html',note='FCI maximum torque; diagnostic only, not continuous.'),
 'AUBO_i5':dict(values=[133,133,98,30,30,30],status='urdf_effort_not_continuous',
 source='https://github.com/AuboRobot/aubo_description/blob/main/urdf/aubo_i5.urdf',note='Official URDF effort; replaced with actual imported values below; diagnostic only.')}
RATINGS['xArm6']=dict(values=[64,64,32,32,12,12],status='rated_motor_times_100_gearing_ideal',source=RATINGS['xArm7']['source'],note=RATINGS['xArm7']['note'])
def fmt(v): return ' '.join(f'{float(x):.12g}' for x in v)
def box(parent,name,pos,size,mass=None,color=(.35,.4,.45,1),robot=True):
    a=dict(name=name,type='box',pos=fmt(pos),size=fmt(np.array(size)/2),rgba=fmt(color),
      contype='2' if robot else '1',conaffinity='3' if robot else '2',margin='.01')
    if mass is not None: a['mass']=str(mass)
    return ET.SubElement(parent,'geom',**a)
def quat(r): return fmt(r.as_quat()[[3,0,1,2]])
def source_root(arm):
    if arm=='xArm6':
        p=HERE/'models/xarm6.xml'
        if not p.exists():convert_xarm6(p)
        return ET.parse(p).getroot(),p.parent
    if arm=='AUBO_i5':
        p=HERE/'models/aubo_i5.xml'
        if not p.exists(): convert_aubo(p)
        return ET.parse(p).getroot(),p.parent
    folder,file=MODEL_FILES[arm]; p=SOURCES/'menagerie'/folder/file
    r=ET.parse(p).getroot()
    if arm=='xArm7':
        b=r.find(".//body[@name='link7']")
        for child in list(b):
            if child.tag=='body': b.remove(child)
        ET.SubElement(b,'site',name='attachment_site',pos='0 0 0')
        r.find('worldbody/body').set('pos','0 0 0') # remove 120mm demo pedestal only
    return r,p.parent/'assets'
def convert_xarm6(dest):
    """Expand official older-model arm fields without ROS or gripper dependencies."""
    import sys
    sys.path.insert(0,str(HERE/'vendor'));import yaml
    src=SOURCES/'xarm_ros/xarm_description'
    u=ET.parse(src/'urdf/xarm6/xarm6.urdf.xacro').getroot()
    kin=yaml.safe_load((src/'config/kinematics/default/xarm6_default_kinematics.yaml').read_text())['kinematics']
    dyn=yaml.safe_load((src/'config/link_inertial/xarm6_type6_HT_BR2.yaml').read_text())
    r=ET.Element('mujoco',model='xArm6');ET.SubElement(r,'compiler',angle='radian',autolimits='true')
    asset=ET.SubElement(r,'asset');w=ET.SubElement(r,'worldbody');base=ET.SubElement(w,'body',name='link_base')
    for i,b in enumerate([base]):pass
    parent=base
    limits=[[-2*math.pi,2*math.pi],[-2.059,2.0944],[-3.927,.19198],[-2*math.pi,2*math.pi],[-1.69297,math.pi],[-2*math.pi,2*math.pi]]
    for i in range(7):
        name='link_base' if i==0 else f'link{i}'
        if i:
            k=kin[f'joint{i}'];parent=ET.SubElement(parent,'body',name=name,pos=fmt([k[a] for a in ('x','y','z')]),quat=quat(Rotation.from_euler('xyz',[k[a] for a in ('roll','pitch','yaw')])))
            ET.SubElement(parent,'joint',name=f'joint{i}',axis='0 0 1',range=fmt(limits[i-1]))
        if i==0:
            it=u.find(".//link[@name='${prefix}link_base']/inertial");o=it.find('origin');iv=it.find('inertia')
            ET.SubElement(parent,'inertial',mass=it.find('mass').get('value'),pos=o.get('xyz'),fullinertia=' '.join(iv.get(a) for a in ('ixx','iyy','izz','ixy','ixz','iyz')))
        else:
            a=dyn[name];ET.SubElement(parent,'inertial',mass=str(a['mass']),pos=fmt([a['origin'][k] for k in ('x','y','z')]),fullinertia=fmt([a['inertia'][k] for k in ('ixx','iyy','izz','ixy','ixz','iyz')]))
        file=src/('meshes/xarm6/visual/'+name+'.stl') if i<6 else src/'meshes/end_tool/collision/end_tool.stl'
        ET.SubElement(asset,'mesh',name=name,file=str(file.resolve()))
        ET.SubElement(parent,'geom',name=name+'_collision',type='mesh',mesh=name,rgba='.86 .86 .86 1')
    ET.SubElement(parent,'site',name='attachment_site',pos='0 0 0')
    dest.parent.mkdir(exist_ok=True);ET.ElementTree(r).write(dest,encoding='unicode')
def convert_aubo(dest):
    """Direct official URDF transform: inertias, limits and collision STL unchanged."""
    src=SOURCES/'aubo_description'; u=ET.parse(src/'urdf/aubo_i5.urdf').getroot()
    r=ET.Element('mujoco',model='AUBO_i5'); ET.SubElement(r,'compiler',angle='radian',autolimits='true')
    asset=ET.SubElement(r,'asset'); w=ET.SubElement(r,'worldbody')
    links={l.get('name'):l for l in u.findall('link')}; joints=u.findall('joint')
    children={j.find('parent').get('link'):j for j in joints}
    values=[]
    def walk(link,parent,j=None):
        a=dict(name=link)
        if j is not None:
            o=j.find('origin'); a['pos']=o.get('xyz','0 0 0'); a['quat']=quat(Rotation.from_euler('xyz',np.fromstring(o.get('rpy','0 0 0'),sep=' ')))
        b=ET.SubElement(parent,'body',**a); l=links[link]
        it=l.find('inertial')
        if it is not None:
            o=it.find('origin'); i=it.find('inertia')
            ET.SubElement(b,'inertial',pos=o.get('xyz'),mass=it.find('mass').get('value'),
             fullinertia=' '.join(i.get(k) for k in ('ixx','iyy','izz','ixy','ixz','iyz')))
        if j is not None and j.get('type')!='fixed':
            lim=j.find('limit'); values.append(float(lim.get('effort')))
            ET.SubElement(b,'joint',name=j.get('name'),axis=j.find('axis').get('xyz'),range=lim.get('lower')+' '+lim.get('upper'))
        for idx,c in enumerate(l.findall('collision')):
            o=c.find('origin'); mesh=c.find('geometry/mesh')
            if mesh is None: continue
            file=src/mesh.get('filename').replace('package://aubo_description/','')
            n=f'{link}_{idx}'; ET.SubElement(asset,'mesh',name=n,file=str(file.resolve()))
            ET.SubElement(b,'geom',name=n,type='mesh',mesh=n,pos=o.get('xyz','0 0 0'),
             quat=quat(Rotation.from_euler('xyz',np.fromstring(o.get('rpy','0 0 0'),sep=' '))),rgba='.8 .55 .20 1')
        if link in children:
            nxt=children[link]; walk(nxt.find('child').get('link'),b,nxt)
        else: ET.SubElement(b,'site',name='attachment_site',pos='0 0 0')
    base=next(n for n in links if n not in {j.find('child').get('link') for j in joints})
    walk(base,w); dest.parent.mkdir(exist_ok=True); ET.ElementTree(r).write(dest,encoding='unicode')
    RATINGS['AUBO_i5']['values']=values
def namespaced(r,folder,side):
    r=copy.deepcopy(r); prefix=side+'_'
    for e in r.iter():
        if e.tag=='mesh' and 'file' in e.attrib:
            e.set('name',e.get('name',Path(e.get('file')).stem))
            p=Path(e.get('file')); e.set('file',str(p if p.is_absolute() else (folder/p).resolve()))
    for idx,g in enumerate(r.findall('.//worldbody//geom')):
        if not g.get('name'): g.set('name',f'geom_{idx}')
    for e in r.iter():
        for attr in ('name','class','childclass','mesh','material','joint','joint1','joint2','body1','body2','target'):
            if attr in e.attrib: e.set(attr,prefix+e.get(attr))
    # Preserve the reference floor-contact taxonomy: all source links are arms.
    # Only body identifiers change; transforms, collision shapes and inertias do not.
    body_names={b.get('name'):prefix+'arm_'+b.get('name')[len(prefix):] for b in r.findall('.//worldbody//body')}
    for e in r.iter():
        if e.tag=='body' and e.get('name') in body_names:e.set('name',body_names[e.get('name')])
        for attr in ('body1','body2','target'):
            if e.get(attr) in body_names:e.set(attr,body_names[e.get(attr)])
    return r
def build(config=None):
    c=dict(CONFIG if config is None else config); arm=c['arm']; count=c['count']
    raw,folder=source_root(arm)
    r=ET.Element('mujoco',model=f"{arm}_{count}_wall_rail")
    ET.SubElement(r,'compiler',angle='radian',autolimits='true',inertiafromgeom='auto')
    ET.SubElement(r,'option',gravity='0 0 -9.81',integrator='implicitfast')
    vis=ET.SubElement(r,'visual'); ET.SubElement(vis,'global',offwidth='1440',offheight='1000')
    d=ET.SubElement(r,'default'); ET.SubElement(d,'geom',margin='.01')
    asset=ET.SubElement(r,'asset'); w=ET.SubElement(r,'worldbody'); contact=ET.SubElement(r,'contact')
    for g in ET.parse(SOURCES/'permanent_kitchen.xml').findall('worldbody/geom'):
        g=copy.deepcopy(g)
        if g.get('name')=='counter_right':
            g.set('pos','.845 .3 .835');g.set('size','.955 .3 .015') # exact T08 x=-.110 edge
        w.append(g)
    # 500mm worktop-to-cabinet gap, 600H x 370D: IKEA METOD guide.
    # Solid door swept keep-out: fully open 600mm doors must remain available.
    for i,(lo,hi) in enumerate(((-1.8,-.7),(-.1,.69),(1.47,1.8))):
        box(w,f'upper_cabinet_{i}',[(lo+hi)/2,.415,1.65],[hi-lo,.37,.60],robot=False,color=(.85,.82,.75,1))
        door=box(w,f'cabinet_door_sweep_{i}',[(lo+hi)/2,-.065,1.65],[hi-lo,.60,.60],robot=False,color=(.9,.8,.4,.07))
        # Door sweep is a mounting/access constraint on fixed rail hardware.
        # Closed cabinetry is physical collision geometry for every arm.
        door.set('contype','4');door.set('conaffinity','8')
    # No sockets were specified. Two declared representative outlets + plug access.
    for i,x in enumerate((-.90,.15)):
        box(w,f'outlet_access_{i}',[x,.56,1.01],[.10,.08,.08],robot=False,color=(.8,.9,.95,.15))
    z=.85+c['height']; rail_y=.575
    anchor=ET.SubElement(w,'body',name='wall_anchor',pos=fmt([0,rail_y,z]))
    ET.SubElement(anchor,'joint',name='anchor_lock',type='slide',axis='0 0 1',range='-1e-12 1e-12')
    ET.SubElement(anchor,'inertial',mass='.001',pos='0 0 0',diaginertia='1e-6 1e-6 1e-6')
    rail=ET.SubElement(anchor,'body',name='rail_structure')
    # Locked scalar DOF separates rail's weld-id from environment for gap checking.
    ET.SubElement(rail,'joint',name='rail_lock',type='slide',axis='0 0 1',range='-1e-12 1e-12')
    box(rail,'rail_beam',[0,0,0],[4.6,.030,.070],mass=24,color=(.2,.23,.28,1))
    # Brackets are the sole wall-mount contact identity.
    for x in (-1.5,-.75,0,.55): box(rail,'wall_mount_'+str(x),[x,.025,0],[.10,.04,.05],mass=.4)
    for i in range(count):
        box(rail,f'cable_carrier_track_{i}',[0,0,(i-1)*.015],[4.6,.020,.012],mass=1.6,color=(.12,.14,.17,1))
    acm=[]; arm_names={}; jaw_names=[]; base_names=['anchor_lock','rail_lock']
    rot={'horizontal':Rotation.from_euler('x',90),
      'down30':Rotation.from_euler('x',120),'down60':Rotation.from_euler('x',150),
      'vertical':Rotation.identity(),'inverted':Rotation.from_euler('x',180)}[c['orientation']]
    for side in SIDES[:count]:
        a=namespaced(raw,folder,side)
        for e in a.find('default') or []: d.append(e)
        for e in a.find('asset') or []: asset.append(e)
        # Independent carriage, 8kg including plate/drive/brake/cable moving allowance.
        carr=ET.SubElement(rail,'body',name=side+'_carriage',pos='0 0 0')
        jname=side+'_carriage_x'; base_names.append(jname)
        ET.SubElement(carr,'joint',name=jname,type='slide',axis='1 0 0',range='-2.12 2.12')
        box(carr,side+'_carriage_block',[0,-.015,-.055],[.24,.06,.18],mass=5)
        s=c['standoff']; basey=.60-s
        # Structural stand-off in side-local (world-aligned) frame.
        box(carr,side+'_carriage_bracket',[0,(basey-rail_y)/2,-.04],[.18,max(abs(rail_y-basey),.025),.025],mass=1)
        box(carr,side+'_connecting_cleat',[0,basey-rail_y,-.025],[.10,.05,.05],mass=.3)
        # Cable carrier swept envelope follows whole travel, partitioned by parked ends.
        box(carr,side+'_cable_loop',[0,-.035,0],[.20,.025,.06],mass=1,color=(.1,.12,.15,1))
        mount=ET.SubElement(carr,'body',name=side+'_mount',pos=fmt([0,basey-rail_y,0]),quat=quat(rot))
        plate_width={'UR5e':.18,'FR3':.20,'AUBO_i5':.20}.get(arm,.14)
        box(mount,side+'_base_adapter_plate',[0,0,-.009],[plate_width,plate_width,.018],mass=.7)
        body=copy.deepcopy(a.find('worldbody/body')); mount.append(body)
        attach=body.find(f".//site[@name='{side}_attachment_site']")
        parent=next(b for b in body.iter('body') if attach in list(b))
        ar=Rotation.from_quat(np.fromstring(attach.get('quat','1 0 0 0'),sep=' ')[[1,2,3,0]])
        ap=np.fromstring(attach.get('pos','0 0 0'),sep=' ')
        extension=c.get('grip_extension',.14)
        tool=ET.SubElement(parent,'body',name=side+'_tool',pos=fmt(ap+ar.apply([0,0,extension])),
          quat=quat(ar*Rotation.from_euler('y',-90)))
        # Palm geometry/COM stay fixed relative to the flange; shorter jaw extension places
        # the grasp nearer it. The held-tool definition and reference force sites stay exact.
        ET.SubElement(tool,'inertial',mass='1.0',pos=fmt([.05-extension,0,0]),diaginertia='.001 .003 .003')
        box(tool,side+'_gripper_palm',[.04-extension,0,0],[.07,.080,.04])
        for sign,label in ((-1,'minus'),(1,'plus')):
            jaw=ET.SubElement(tool,'body',name=f'{side}_jaw_{label}',pos=fmt([-.02,sign*.004,0]))
            j=f'{side}_jaw_{label}'; jaw_names.append(j)
            ET.SubElement(jaw,'joint',name=j,type='slide',axis=fmt([0,sign,0]),range='0 .045')
            ET.SubElement(jaw,'inertial',mass='.10',pos='-.015 0 0',diaginertia='.00002 .00008 .00008')
            box(jaw,f'{side}_finger_{label}',[-.015,0,0],[.075,.008,.020])
        ET.SubElement(tool,'site',name=side+'_prep',pos='0 0 0',size='.004')
        arm_names[side]=[j.get('name') for j in body.findall('.//joint') if j.get('name') not in jaw_names]
        # Preserve only source supplied exclusions, no broad new ACM exemptions.
        for ex in a.findall('contact/exclude'):
            if body.find(f".//body[@name='{ex.get('body1')}']") is not None and body.find(f".//body[@name='{ex.get('body2')}']") is not None:
                contact.append(copy.deepcopy(ex))
        for g in body.iter('geom'):
            cl=g.get('class',''); visual='visual' in cl
            if not visual: g.set('contype','2');g.set('conaffinity','3');g.set('margin','.01')
    # Rail-to-wall mount only; flange collision meshes are not exempted.
    # Custom rail/cable body-name taxonomy avoids being mistaken for grippers.
    for g in r.findall('.//worldbody//geom'):
        name=g.get('name','')
        if name=='rail_beam' or name.startswith(('wall_mount_','cable_carrier_track_')) or any(k in name for k in ('carriage_block','carriage_bracket','cable_loop','base_adapter_plate','connecting_cleat')):
            g.set('contype','8');g.set('conaffinity','7')
    # Numerical models retain every source collision shape, inertial and joint.
    # Inert visual meshes are optional to keep two CPU workers far below 2GB.
    if not c.get('visual',False):
        for b in w.iter('body'):
            for g in list(b.findall('geom')):
                if 'visual' in g.get('class',''):b.remove(g)
        used={g.get('mesh') for g in w.iter('geom') if g.get('mesh')}
        for a in list(asset.findall('mesh')):
            if a.get('name') not in used:asset.remove(a)
    values=RATINGS[arm]['values']
    if arm=='AUBO_i5':
        urdf=ET.parse(SOURCES/'aubo_description/urdf/aubo_i5.urdf')
        values=[float(j.find('limit').get('effort')) for j in urdf.findall('joint') if j.find('limit') is not None]
        RATINGS[arm]['values']=values
    lim={n:dict(continuous_Nm=t,provenance=RATINGS[arm]['status']) for side,names in arm_names.items() for n,t in zip(names,values)}
    return ET.ElementTree(r),dict(config=c,arms=arm_names,jaws=jaw_names,base=base_names,torque_limits=lim,
      scene=json.loads((SOURCES/'permanent_scene.json').read_text()),disabled_robot_pairs=acm,ratings=RATINGS[arm])

if __name__=='__main__':
    for arm in ('UR5e','xArm7','FR3','AUBO_i5'):
        tree,meta=build(dict(CONFIG,arm=arm)); p=HERE/'models'/f'{arm}_wall_rail.xml';p.parent.mkdir(exist_ok=True)
        tree.write(p,encoding='unicode'); m=mujoco.MjModel.from_xml_path(str(p))
        p.with_suffix('.json').write_text(json.dumps(meta,indent=2)); print(arm,m.nq,m.ngeom,sum(m.body_mass),meta['arms'])
