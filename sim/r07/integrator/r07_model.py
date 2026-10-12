"""R07 geometry adapter. All copied R05 Python modules remain byte-identical.

Only new rail hardware and replacement appliance geometry are defined here.
OEM arm transforms, collision solids, masses, inertia and tools are unscaled.
"""
import copy, json
from pathlib import Path
import xml.etree.ElementTree as E
import numpy as np
from scipy.spatial.transform import Rotation
import model as old
H=Path(__file__).resolve().parent
original_build=old.build
CONFIG=dict(old.CONFIG, height=.94, helper_height=1.09, front_mount_y=.375,
            pitch=0., mount_deg=0., helper_mount_deg=180.,
            orientation='R07_under_cabinet_stacked')
if (H/'results/config.json').exists():
    CONFIG.update(json.loads((H/'results/config.json').read_text()))
    CONFIG.pop('transport_only',None)

def build(config=None):
    c=dict(CONFIG if config is None else config)
    old.SIDES=('R',) if c.get('count')==1 else ('R','L')
    tr,meta=original_build(c);r=tr.getroot();w=r.find('worldbody')
    rail=w.find(".//body[@name='rail_structure']")
    oldinfra=set(meta['infrastructure_names'])
    for p in r.iter():
        for g in list(p.findall('geom')):
            if g.get('name') in oldinfra:p.remove(g)
    infra=[]
    def hardware(p,n,pos,size,mass):
        g=old.box(p,n,pos,size,mass=mass,robot=True)
        g.set('contype','8');g.set('conaffinity','7');infra.append(n)
    lanes=[]
    # New wall-mounted 60x70mm rail envelopes; full declared hardware size.
    for i,side in enumerate(old.SIDES):
        z=c['height'] if i==0 else c['helper_height']
        angle=c['mount_deg'] if i==0 else c['helper_mount_deg']
        rz=c.get('rail_centres_z',[1.15,1.235])[i]
        if i==0 or c.get('lane_count',2)==2:
            hardware(rail,f'rail_beam_{i}',[-.55,c.get('beam_y',.555),rz],[2.42,.060,.070],11.2)
            hardware(rail,f'rail_guide_{i}',[-.55,c.get('guide_y',.511),rz],[2.38,.024,.038],2.1)
        # Full cable-chain swept rectangle: 110mm bend radius +25mm links.
        # Bends run in XY, so vertical height need not equal bend diameter.
        hardware(rail,f'cable_chain_cover_{i}',[-.55,c.get('chain_y',.3625),c.get('chain_centres_z',[1.2875,1.3225])[i]],
                 [2.38,.245,.025],1.6)
        carr=rail.find(f"body[@name='{side}_carriage']")
        by=c.get('helper_y',c['front_mount_y']) if i else c['front_mount_y']
        carr.set('pos',old.fmt([0,by,z]))
        carr.find('joint').set('range','-1.55 .46')
        offset=c.get('guide_y',.511)-by
        hardware(carr,side+'_carriage_block',[0,offset,rz-z],[.18,.025,.085],2.4)
        # Native rail/base attachment parts are a declared mechanical assembly.
        az=z-.012 if angle<90 else z+.012
        mount=carr.find(f"body[@name='{side}_mount']")
        hardware(mount,side+'_base_plate',[0,0,-.012],[.17,.17,.024],1.1)
        hardware(carr,side+'_mount_bracket',[0,offset,(az+rz)/2-z],
                 [.15,.06,abs(az-rz)+.024],2.1)
        hardware(carr,side+'_mount_arm',[0,offset/2,az-z],[.15,abs(offset)+.03,.024],1.0)
        hardware(carr,side+'_rail_brake',[.13 if i==0 else -.13,offset,rz-z],[.065,.055,.080],.8)
        lanes.append(dict(side=side,base_y=by,base_z=z,beam_z=rz))
    for i,x in enumerate((-1.70,-1.05,-.10,.56)):
        bt=c.get('bracket_thickness',.018)
        hardware(rail,f'r07_wall_bracket_{i}',[x,.60-bt/2,1.10],[.070,bt,.46],1.8*bt/.018)
        for lane in lanes[:c.get('lane_count',2)]:
            hardware(rail,f'r07_wall_tie_{i}_{lane["side"]}',[x,c.get('tie_y',.555),lane['beam_z']],
                     [.070,.068,.04],.25)
    # Dry power tracks remain behind front plane, separated from the wall.
    for i,(lo,hi) in enumerate(((-1.76,-.74),(-.05,.66))):
        hardware(rail,f'appliance_power_track_{i}',[(lo+hi)/2,.565,c.get('power_z',1.175)],
                 [hi-lo,.028,.070],.6)
        hardware(rail,f'appliance_power_adapter_{i}',[hi-.07,.521,c.get('power_z',1.175)],
                 [.067,.043,.067],.15)
    # R211 is removed. BFP610's conservative envelope and removable bowl are
    # the appliance redesign; no R211 envelope is relabelled as lower hardware.
    for p in r.iter():
        for g in list(p.findall('geom')):
            if g.get('name','').startswith('slicer_'):p.remove(g)
            elif g.get('name')=='secondary_drive_guard':
                g.set('pos','-1.27 .55 .70')
            elif g.get('name')=='presence_sensor':g.set('pos','-1.35 .57 1.30')
    if not c.get('transport_only'):
        old.box(w,'bfp610_complete_envelope',[.425,.16,1.0475],
                [.395,.295,.395],robot=False,color=(.2,.3,.38,1))
    if c.get('replacement_faucet'):
        from faucet_v3_r07 import replace
        replace(r,c)
    meta.update(config=c,infrastructure_names=infra,lanes=lanes)
    return tr,meta

def install(config=None):
    old.CONFIG=dict(CONFIG if config is None else config);old.build=build
    return old
