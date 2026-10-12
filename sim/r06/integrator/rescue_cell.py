"""R06 revision 2: open pan corridors, owner-bound interfaces, collision-aware IK.

The source checker, planner, geometry oracle and point bound are imported without
edits. Search penalties encourage extra clearance; reference gates still decide.
"""
import cell as c
from cell import *
from jobs import check_load
from collections import Counter
OLD_SCENE=c.make_scene
PRODUCTS=('carrot','potato','bok_choy','tomato')
CONFIGS={
 8:dict(id=8,name='Original cell, displaced complete food cup',width=1.45,depth=.75,base=[0,.53,1.77],angle=155,rail=0,old=True,cup_shift=-.14),
9:dict(id=9,name='Open docks replace shared processing cage',width=1.45,depth=.75,base=[0,.53,1.77],angle=155,rail=0,old=False,cup_shift=-.14,work_z=.90,front_y=.25,rear_y=.55,pitch=.35,station_x=.46),
10:dict(id=10,name='Correct OEM base-plane plate; modest wider/deeper cell',width=1.60,depth=.90,base=[0,.59,1.77],angle=155,rail=0,old=False,cup_shift=-.14,work_z=.90,front_y=.29,rear_y=.63,pitch=.36,station_x=.47,correct_plate=True),
11:dict(id=11,name='Fixed rear-facing side mount opens overhead corridor',width=1.60,depth=.90,base=[0,.70,1.30],angle=90,rail=0,old=False,cup_shift=-.14,work_z=.85,front_y=.29,rear_y=.62,pitch=.36,station_x=.47,correct_plate=True),
12:dict(id=12,name='Short500mm rear rail for redundant pan approach',width=1.60,depth=.90,base=[0,.70,1.30],angle=90,rail=.25,old=False,cup_shift=-.14,work_z=.85,front_y=.29,rear_y=.62,pitch=.36,station_x=.47,correct_plate=True),
13:dict(id=13,name='Fixed mount with connected raised keys and rear tool parking',width=1.60,depth=.90,base=[0,.70,1.30],angle=90,rail=0,old=False,cup_shift=-.14,work_z=.85,front_y=.29,rear_y=.62,pitch=.36,station_x=.47,correct_plate=True,connected_handles=True),
14:dict(id=14,name='Outboard key bridge clears lid sweep; integral pan lid drive',width=1.60,depth=.90,base=[0,.70,1.30],angle=90,rail=0,old=False,cup_shift=-.14,work_z=.85,front_y=.29,rear_y=.62,pitch=.36,station_x=.47,correct_plate=True,connected_handles=True,outboard_handles=True,integral_lid=True),
}
CONFIGS[15]=dict(CONFIGS[14],id=15,name='Rear-offset geared lid shaft outside full lid sweep',offset_lid_drive=True)
CONFIGS[16]=dict(CONFIGS[15],id=16,name='Full blade parks laterally outside vertical pan corridor',blade_lateral_park=True)
CONFIGS[17]=dict(CONFIGS[16],id=17,name='Full cup raised80mm to clear returned bowls at both stations',cup_z_shift=-.08)
def box(parent,name,pos,size,rgba='.60 .64 .67 1',**kw):
 attrs=dict(name=name,type='box',pos=fmt(pos),size=fmt(np.array(size)/2),rgba=rgba,contype='1',conaffinity='2');attrs.update(kw)
 return E.SubElement(parent,'geom',**attrs)
def body(parent,name,pos=(0,0,0)):
 return E.SubElement(parent,'body',name=name,pos=fmt(pos))
def config(v):
 if v not in CONFIGS:
  f=H/f'v2/config_{v}.json'
  if not f.exists():raise KeyError(v)
  CONFIGS[v]=json.loads(f.read_text())
 return copy.deepcopy(CONFIGS[v])
def initial_locations(cfg):
 if cfg.get('old'):
  return {b['id']:list(b['pose']['position_m']) for b in SPEC['bodies'] if b['parent']=='world' and b['id'].startswith('output_')}
 return {'output_'+p:[(i-1.5)*cfg['pitch'],cfg['front_y'],cfg['work_z']+(.012 if cfg['id']>=10 else .014)] for i,p in enumerate(PRODUCTS)}
def seats(cfg):
 if cfg.get('old'):return dict(wash_basin=[-.49,.49,1.073],process_cell=[.45,.505,.984])
 return dict(wash_basin=[-cfg['station_x'],cfg['rear_y'],cfg['work_z']+(.012 if cfg['id']>=10 else .014)],process_cell=[cfg['station_x'],cfg['rear_y'],cfg['work_z']+(.012 if cfg['id']>=10 else .014)])
def key_position(origin,cfg=None):return np.array(origin)+[0,-.155 if cfg and cfg.get('outboard_handles') else -.121,.150]
def scene(v,held=None,container_poses=None):
 cfg=config(v);loc=initial_locations(cfg);loc.update(container_poses or {})
 text,com=OLD_SCENE(7,held,container_poses=loc);root=E.fromstring(text);world=root.find('worldbody')
 tool=root.find(".//body[@name='R_tool']")
 for n in ('R_eoat_cup_floor','R_eoat_cup_back'):
  g=tool.find(f"geom[@name='{n}']");p=np.fromstring(g.get('pos'),sep=' ');p[1]+=cfg['cup_shift'];p[2]+=cfg.get('cup_z_shift',0);g.set('pos',fmt(p))
 # 0.10 kg cup allowance relocated rigidly; retain the complete 1.2 kg EOAT.
 tool.find('inertial').set('pos',fmt([0,.1*cfg['cup_shift'],.08+.1*cfg.get('cup_z_shift',0)]))
 if v>=10:
  for n in ('minus','plus'):tool.find(f"body[@name='R_jaw_{n}']/joint").set('range','-.02 .04')
 if cfg.get('connected_handles'):
  outboard=cfg.get('outboard_handles',False);extra_mass=.40 if outboard else .15
  drive_y=.115 if cfg.get('offset_lid_drive') else .0815
  extra_com=(.15*np.array([0,-.129,.120])+.20*np.array([.153,drive_y,.115])+.05*np.array([0,-.095,.078]))/.40 if outboard else np.array([0,-.095,.120])
  for p in PRODUCTS:
   prefix='R_held_' if held=='output_'+p else '';pan=root.find(f".//body[@name='{prefix}output_{p}']")
   g=pan.find(f"geom[@name='{prefix}key_backer_{p}']");gp=np.fromstring(g.get('pos'),sep=' ');gp[1]=-.110 if outboard else -.085;g.set('pos',fmt(gp))
   if outboard:
    g=pan.find(f"geom[@name='{prefix}key_{p}']");gp=np.fromstring(g.get('pos'),sep=' ');gp[1]=-.155;g.set('pos',fmt(gp))
   box(pan,prefix+'key_neck_'+p,[0,-.129 if outboard else -.095,.140],[.020,.058 if outboard else .040,.016],contype='2' if prefix else '1',conaffinity='3' if prefix else '2')
   for sx in (-1,1):E.SubElement(pan,'geom',name=prefix+'key_bolt_'+p+str(sx),type='cylinder',pos=fmt([sx*.025,-.083,.078 if outboard else .110]),quat=quat(Rotation.from_euler('x',90,degrees=True)),size='.004 .005',contype='2' if prefix else '1',conaffinity='3' if prefix else '2')
   if outboard:
    box(pan,prefix+'key_lower_bridge_'+p,[0,-.095,.078],[.090,.032,.010],contype='2' if prefix else '1',conaffinity='3' if prefix else '2')
    box(pan,prefix+'lid_drive_'+p,[.153,.09825 if cfg.get('offset_lid_drive') else .0815,.115],[.041,.060 if cfg.get('offset_lid_drive') else .024,.048],contype='2' if prefix else '1',conaffinity='3' if prefix else '2')
    E.SubElement(pan,'geom',name=prefix+'lid_drive_shaft_'+p,type='cylinder',pos=fmt([.075,drive_y,.104]),quat=quat(Rotation.from_euler('y',90,degrees=True)),size='.003 .075',contype='2' if prefix else '1',conaffinity='3' if prefix else '2')
   if not prefix:
    ine=pan.find('inertial');oldmass=float(ine.get('mass'));oldcom=np.fromstring(ine.get('pos'),sep=' ');ine.set('mass',str(oldmass+extra_mass));ine.set('pos',fmt((oldmass*oldcom+extra_mass*extra_com)/(oldmass+extra_mass)))
  if held:
   mass=next(g['combined_mass_kg'] for g in SPEC['grasp_handles'] if g['object_id']==held);grip=np.array([0,-.155 if outboard else -.121,.15]);tr=Rotation.from_euler('z',180,degrees=True)*WORLD_TOOL*PREP_LOCAL
   if outboard:
    pan=root.find(f".//body[@name='R_held_{held}']");pan.set('pos',fmt(np.array([0,0,.09])-(Rotation.from_euler('z',180,degrees=True)*WORLD_TOOL).inv().apply(grip)));com=np.array(com)+tr.inv().apply([0,.034,0])
   offset=tr.inv().apply(extra_com-grip);com=(mass*np.array(com)+extra_mass*offset)/(mass+extra_mass)
   tool.find("site[@name='R_mass']").set('pos',fmt(np.array([0,0,.09])+PREP_LOCAL.apply(com)))
 if cfg.get('old'):return E.tostring(root,encoding='unicode'),com
 mount=world.find("body[@name='rail_structure']")
 for x in list(mount):
  if x.tag=='body' and x.get('name')!='R_arm_base':mount.remove(x)
 keep={'rail_structure'}|{'output_'+p for p in PRODUCTS}
 for x in list(world):
  if x.get('name') not in keep:world.remove(x)
 mount.set('pos',fmt(cfg['base']));mount.set('quat',quat(Rotation.from_euler('x',cfg['angle'],degrees=True)))
 mount.find('joint').set('range',fmt([-cfg['rail'],cfg['rail']]) if cfg['rail'] else '-1e-12 1e-12')
 width,depth,z=cfg['width'],cfg['depth'],cfg['work_z'];bx,by,bz=cfg['base']
 # Weld only fixed base/mating members to the actual fixed mount. The moving
 # carriage carries its own plate when a rail is selected; beam stays world.
 if not cfg['rail']:
  stand=body(mount,'R_fixed_base_support');rt=Rotation.from_euler('x',cfg['angle'],degrees=True)
  stand.set('quat',quat(rt.inv()));stand.set('pos',fmt(rt.inv().apply(np.array([bx,by,bz]) - np.array(cfg['base']))))
  if cfg['angle']==155:
   if cfg.get('correct_plate'):
    box(mount,'mount_plate',[0,0,-.014],[.20,.20,.028])
    for sx in (-1,1):E.SubElement(mount,'geom',name='mount_brace_'+str(sx),type='capsule',fromto=fmt([sx*.065,0,-.029,*rt.inv().apply([sx*.065,.13,.045])]),size='.016',contype='1',conaffinity='2',rgba='.4 .45 .5 1')
   else:box(stand,'mount_plate',[0,.028,.016],[.20,.020,.20])
   box(stand,'mount_crossbeam',[0,.13,.095],[width-.08,.10,.10])
   for sx in (-1,1):box(stand,'fixed_column_'+str(sx),[sx*(width/2-.06),.13,-.36],[.080,.080,.81])
  else:
   # Retain a full plate but recess it30mm from the OEM base plane. Four
   # integral base fastener/standoff solids transmit the load. Those are
   # robot-base hardware (same audited adjacent-link self policy); the plate,
   # bracket and post remain environment and keep10mm to moving robot links.
   box(mount,'mount_plate',[0,0,-.044],[.20,.20,.028]);box(stand,'fixed_pedestal',[0,.095,-.25],[.12,.12,.60])
   box(stand,'base_support_bracket',[0,.10,0],[.18,.11,.18])
   for sx in (-1,1):
    for sy in (-1,1):E.SubElement(mount,'geom',name=f'R_base_fastener_{sx}_{sy}',type='cylinder',pos=fmt([sx*.0389,sy*.0389,-.015]),size='.006 .015',rgba='.4 .43 .47 1',contype='2',conaffinity='3')
 else:
  box(mount,'R_carriage_plate',[0,0,-.018],[.22,.22,.036])
  box(world,'rear_rail_full_beam',[0,by+.125,bz],[1.04,.12,.15])
  box(world,'rail_brake_motor',[.64,by+.115,bz],[.16,.14,.16])
  box(world,'rail_cable_chain',[0,by+.11,bz+.14],[1.12,.08,.08])
  for sx in (-1,1):box(world,'rear_rail_column_'+str(sx),[sx*.58,by+.115,(bz+.45)/2],[.08,.10,bz-.45])
 box(world,'floor',[0,depth/2,-.026],[width+.2,depth+.2,.05],'.3 .33 .35 1')
 box(world,'worktop_full',[0,depth/2,z-.022],[width,depth,.024])
 box(world,'frame_lower',[0,depth/2,.09],[width-.08,depth-.08,.06])
 for sx in (-1,1):
  for sy in (.06,depth-.06):box(world,f'frame_leg_{sx}_{sy}',[sx*(width/2-.06),sy,z/2],[.08,.08,z])
 for sx in (-1,1):box(world,'guard_side_'+str(sx),[sx*(width/2),depth/2,(z+1.97)/2],[.006,depth,1.97-z],'.44 .70 .80 .18')
 box(world,'guard_back',[0,depth,(z+1.97)/2],[width,.006,1.97-z],'.44 .70 .80 .18')
 box(world,'guard_roof',[0,depth/2,1.97],[width,depth,.006],'.44 .70 .80 .18')
 door=body(world,'access_door',[-width/2,0,(z+1.95)/2]);E.SubElement(door,'joint',name='access_door_joint',type='hinge',axis='0 0 1',range='-1.58 0')
 E.SubElement(door,'inertial',pos=fmt([width/2,0,0]),mass='8',diaginertia='.8 1.8 1.0')
 box(door,'access_door_panel',[width/2,0,0],[width-.025,.006,1.95-z],'.44 .70 .80 .12')
 # Wide surface lands; no pocket walls or pins in the robot insertion route.
 for p in PRODUCTS:
  xyz=initial_locations(cfg)['output_'+p];b=body(world,'dock_'+p,[xyz[0],xyz[1],z])
  box(b,'dock_'+p+'_land',[0,0,0],[.29,.21,.024],'.45 .48 .51 1')
 for station,xyz in seats(cfg).items():
  x,y,_=xyz;b=body(world,station,[x,y,z]);prefix='wash' if station=='wash_basin' else 'process'
  box(b,prefix+'_open_land',[0,0,0],[.33,.245,.024],'.48 .54 .59 1')
  # Utilities and drive remain below the pan. Whole lateral utility head parks
  # behind it; an overhead gantry/cage is unnecessary for loading.
  box(b,prefix+'_drive_enclosure',[0,.04,-.28 if v>=10 else -.20],[.34,.26,.30],'.55 .60 .64 1')
  head=body(b,prefix+'_utility_head',[0,.205,.10]);E.SubElement(head,'joint',name=prefix+'_head_y',type='slide',axis='0 1 0',range='0 .15')
  E.SubElement(head,'inertial',pos='0 0 0',mass='2',diaginertia='.01 .015 .02')
  box(head,prefix+'_head_full',[0,0,0],[.31,.065,.08],'.50 .57 .63 1')
  # Remote lid platen picks the existing lid at its rear tab; actuator, link,
  # full opening motion, and retention shoe are explicitly modelled.
  lift=body(b,prefix+'_lid_lift',[.19,0,.16]);E.SubElement(lift,'joint',name=prefix+'_lid_lift_z',type='slide',axis='0 0 1',range='0 .22')
  E.SubElement(lift,'inertial',pos='0 0 0',mass='.6',diaginertia='.002 .002 .002')
  box(lift,prefix+'_lid_lift_shoe',[0,.072,0],[.018,.05,.03])
  if cfg.get('integral_lid'):b.remove(lift)
  clamp=body(b,prefix+'_retainer',[.177,0,.04]);E.SubElement(clamp,'joint',name=prefix+'_retention_x',type='slide',axis='-1 0 0',range='0 .04')
  E.SubElement(clamp,'inertial',pos='0 0 0',mass='.3',diaginertia='.001 .001 .001');box(clamp,prefix+'_retention_shoe',[0,0,0],[.02,.14,.035])
  if prefix=='wash':
   box(b,'wash_catch_basin_floor',[0,0,-.10],[.36,.28,.006],'.5 .62 .66 1')
   for side in (-1,1):box(b,'wash_basin_side_'+str(side),[side*.177,0,-.047],[.006,.28,.10])
   box(b,'wash_spray_manifold',[0,.185,.05],[.28,.025,.025],'.35 .5 .6 1')
  else:
   # A supported feed/pusher and guarded side cutting module, with full drive,
   # blade, opening and catch geometry. This is an explicit custom interface,
   # not an OEM appliance certification or a food-transformation oracle.
   f=body(b,'process_pusher',[.21,.055,.065]);E.SubElement(f,'joint',name='process_pusher_x',type='slide',axis='-1 0 0',range='0 .20');E.SubElement(f,'inertial',pos='0 0 0',mass='.5',diaginertia='.002 .002 .002')
   box(f,'process_pusher_plate',[0,0,0],[.02 if v>=10 else .012,.08,.09])
   parent=b
   if cfg.get('blade_lateral_park'):
    parent=body(b,'process_blade_lateral',[-.25,0,0]);E.SubElement(parent,'joint',name='process_blade_park_x',type='slide',axis='1 0 0',range='0 .25');E.SubElement(parent,'inertial',pos='0 0 0',mass='.8',diaginertia='.01 .01 .01')
    box(b,'process_full_lateral_rail',[-.125,.165,.43],[.33,.06,.04]);box(b,'process_lateral_motor',[-.29,.165,.43],[.10,.08,.08])
   if cfg.get('connected_handles'):
    parent=body(parent,'process_blade_park',[0,.10,0]);E.SubElement(parent,'joint',name='process_blade_park_y',type='slide',axis='0 -1 0',range='0 .10');E.SubElement(parent,'inertial',pos='0 0 0',mass='1',diaginertia='.01 .01 .01')
   blade=body(parent,'process_blade',[0,.065,.30]);E.SubElement(blade,'joint',name='process_blade_z',type='slide',axis='0 0 -1',range='0 .275' if v>=10 else '0 .22');E.SubElement(blade,'inertial',pos='0 0 0',mass='2' if v>=10 else '.5',diaginertia='.02 .02 .02' if v>=10 else '.002 .002 .002');box(blade,'process_blade_full',[0,0,0],[.003,.14,.11] if v>=10 else [.003,.12,.08],'.75 .77 .79 1')
   if v>=10:box(blade,'process_carriage_plate',[0,0,.065],[.04,.18,.03])
   box(b,'process_guard_back',[0,.225,.20],[.37,.008,.41],'.45 .7 .8 .22')
   box(b,'process_waste_chute',[.10,.095,-.18],[.065,.11,.30])
 box(world,'controller_box',[0,depth-.20,.38],[.460,.254,.449],'.23 .28 .33 1')
 box(world,'controller_dry_partition',[0,depth-.37,.43],[.54,.008,.57])
 box(world,'controller_drip_shield',[0,depth-.20,.64],[.54,.32,.008])
 binbody=body(world,'waste_bin',[.47,depth-.28,.24]);box(binbody,'waste_floor',[0,0,-.12],[.28,.28,.008])
 for sx in (-1,1):box(binbody,'waste_wall_x'+str(sx),[sx*.136,0,0],[.008,.28,.25])
 for sy in (-1,1):box(binbody,'waste_wall_y'+str(sy),[0,sy*.136,0],[.28,.008,.25])
 box(world,'water_drain_hookups',[-.62,depth-.02,.30],[.10,.04,.12],'.25 .43 .62 1');box(world,'one_household_inlet',[.1,depth-.018,.23],[.06,.036,.08],'.15 .18 .21 1')
 return E.tostring(root,encoding='unicode'),com
class Workcell(c.Cell):
 def __init__(self,v,held=None,locations=None):
  cfg=config(v);old=c.make_scene;c.make_scene=lambda *a,**k:scene(v,held,locations)
  try:super().__init__(7 if cfg.get('old') else 2,held,locations)
  finally:c.make_scene=old
  self.cfg=cfg;self.variant=v
  rating=H/f'v2/ratings{cfg["angle"]}'
  c.ENV['HERE']=rating if (rating/'results/torque_envelope.json').exists() else H
  for n in ('R_jaw_minus','R_jaw_plus'):self.q0[self.qa[n]]=.005 if held else (-.02 if v>=10 else -.01)
  self.d.qpos[:]=self.q0;mujoco.mj_forward(self.m,self.d)
  self.support_registry={**{'dock_'+p:dict(faces=['dock_'+p+'_land'],objects=['output_'+p]) for p in PRODUCTS},'wash_basin':dict(faces=['wash_lift_left','wash_lift_right'] if cfg.get('old') else ['wash_open_land'],objects=['output_'+p for p in PRODUCTS]),'process_cell':dict(faces=['cell_land_a','cell_land_b'] if cfg.get('old') else ['process_open_land'],objects=['output_'+p for p in PRODUCTS])}
  self.part_registry={n.removeprefix('R_held_'):self.m.body(self.m.geom_bodyid[i]).name.removeprefix('R_held_') for i,n in enumerate(self.gnames)}
  self.ix=[self.qa[n] for n in ARM]+([self.qa['R_carriage_x']] if cfg['rail'] else [])
  self.variables=ARM+(['R_carriage_x'] if cfg['rail'] else [])
 def window(self,obj,station,origin):
  parts=['pan_'+obj.removeprefix('output_')+'_'+n for n in ('floor','left','right','front','rear')]
  return [dict(kind='grasp_release_support',object_id=obj,support_id=station,side='R',face=f,held_parts=parts,tcp_origin_m=key_position(origin,self.cfg).tolist(),tcp_rotation=self.rot.tolist(),normal=[0,0,1],reason='Owned pan underside / registered top land, straight 50mm normal, ends at5mm') for f in self.support_registry[station]['faces']]
 def capture(self,obj,origin):
  self.capture_window=dict(kind='grasp_release_support',object_id=obj,support_id='eoat_key_capture',pairs=[['key_'+obj.removeprefix('output_'),n] for n in ('R_eoat_key_left','R_eoat_key_right')],tcp_origin_m=key_position(origin,self.cfg).tolist(),tcp_rotation=self.rot.tolist(),normal=[0,0,1])
 def collision_solve(self,target,rot,seed,seconds=20,aim_reserve=.010):
  """Pose solve + active collision constraints + restarts inside each seed.
  A full20s rescue budget is available when branches need it. Fixed tool/goal
  obstruction is a geometric impossibility certificate, not a solver timeout.
  """
  q=np.array(seed).copy();ix=self.ix;lim=np.array([self.m.jnt_range[self.jid[n]] for n in self.variables]).T;start=time.monotonic();deadline=start+max(20,seconds);rng=np.random.default_rng(int(abs(np.sum(q[ix])*1e7))%2**32)
  best=None;active=[];evaluations=0;attempt=0;reason=None
  def pose_res(x):
   nonlocal evaluations
   evaluations+=1
   if time.monotonic()>deadline:raise TimeoutError
   q[ix]=x;p,r=self.pose(q)
   out=list((p-target)*20)+list(Rotation.from_matrix(rot.T@r).as_rotvec()*3)
   for a,b,need in active:
    dist=mujoco.mj_geomDistance(self.m,self.d,a,b,.10,None)
    out.append(max(0,need-dist)*25)
   return out
  while time.monotonic()<deadline:
   attempt+=1
   try:
    ls=least_squares(pose_res,np.clip(q[ix],lim[0]+1e-9,lim[1]-1e-9),bounds=lim,max_nfev=160,ftol=1e-8,xtol=1e-8,gtol=1e-8);q[ix]=ls.x
   except TimeoutError:reason='20s collision-aware per-start rescue exhausted';break
   p,r=self.pose(q);err=dict(position_mm=float(np.linalg.norm(p-target)*1000),orientation_deg=float(np.linalg.norm(Rotation.from_matrix(rot.T@r).as_rotvec())*180/math.pi))
   hits,mins,proof=contacts(self,q);reserve=min((v['reserve_mm'] for cat,v in mins.items() if cat!='self'),default=0);score=err['position_mm']+err['orientation_deg']+max(0,aim_reserve*1000-reserve)*3+len(hits)*100
   row=dict(q=q.tolist(),errors=err,hits=hits[:5],mins=mins,reserve_mm=reserve,score=score,okay=err['position_mm']<=5 and err['orientation_deg']<=3 and not hits)
   if best is None or score<best['score']:best=copy.deepcopy(row)
   if row['okay'] and reserve>=aim_reserve*1000-1e-5:reason='Pose and generous-clearance target reached';break
   if row['okay'] and attempt>=2:reason='Reference gates passed; extra reserve target remains a design score';break
   # At an exact full6D tool goal, a tool or rigid held/environment gap cannot
   # change under an arm null-space motion. Report it instead of spending20s
   # on an impossible local branch. Other arm collisions get the full budget.
   fixed=[h for h in hits if any(n.startswith(('R_eoat_','R_held_')) for n in h['pair']) and any(not n.startswith('R_') for n in h['pair'])]
   if fixed and err['position_mm']<.001 and err['orientation_deg']<.001:
    reason='Task-fixed held/EOAT versus environment obstruction; layout change required';best['invariant_blocker']=fixed[0];break
   basefixed=[h for h in hits if set(h['pair'])=={'R_geom_5','mount_plate'}]
   if basefixed:
    # OEM first shoulder collision capsule is coaxial with its only ancestor
    # hinge; rotating about that axis preserves the entire capsule, not just
    # its AABB. All other arm joints are downstream. A fixed plate relative to
    # that hinge therefore has exactly the same gap for every arm solution.
    g=self.gnames.index('R_geom_5');b=int(self.m.geom_bodyid[g]);j=int(self.m.body_jntadr[b])
    coaxial=(int(self.m.geom_type[g])==3 and np.allclose(self.m.geom_quat[g],[1,0,0,0]) and np.allclose(self.m.geom_pos[g,:2],0) and np.allclose(self.m.jnt_axis[j],[0,0,1]) and np.allclose(self.m.jnt_pos[j],0))
    if coaxial:reason='Analytic branch-invariant coaxial shoulder capsule / base plate obstruction';best['invariant_blocker']=basefixed[0];best['invariant_shape_proof']='Only influencing relative joint is rotation about capsule symmetry axis; distance is constant';break
   allow=permitted(self);active=[]
   self.d.qpos[:]=q;mujoco.mj_forward(self.m,self.d)
   for a,b,need,cat in self.bounds.pairs:
    if frozenset((self.gnames[a],self.gnames[b])) in allow:continue
    if np.linalg.norm(self.d.geom_xpos[a]-self.d.geom_xpos[b])-self.m.geom_rbound[a]-self.m.geom_rbound[b]>.065:continue
    distance=mujoco.mj_geomDistance(self.m,self.d,a,b,.075,None)
    goal=need+(.010 if cat!='self' else .002)
    if distance<goal+.015:active.append((a,b,goal))
   if attempt%3==0:
    q[ix]=np.clip(np.array(best['q'])[ix]+rng.normal(0,.45,len(ix)),lim[0]+1e-8,lim[1]-1e-8);active=[]
  if best is None:
   p,r=self.pose(q);hits,mins,proof=contacts(self,q);best=dict(q=q.tolist(),errors=dict(position_mm=float(np.linalg.norm(p-target)*1000),orientation_deg=float(np.linalg.norm(Rotation.from_matrix(rot.T@r).as_rotvec())*180/math.pi)),hits=hits[:5],mins=mins,reserve_mm=min((v['reserve_mm'] for k,v in mins.items() if k!='self'),default=-1e6),score=1e9,okay=False)
  best.update(elapsed_s=time.monotonic()-start,allocated_per_start_s=max(20,seconds),collision_aware=True,active_collision_constraints=len(active),evaluations=evaluations,restarts=attempt,reason=reason)
  return best
def names_to_q(dst,src,q):
 z=dst.q0.copy()
 for n,j in dst.jid.items():
  if n in src.jid:
   count=7 if dst.m.jnt_type[j]==0 else 1;z[dst.qa[n]:dst.qa[n]+count]=q[src.qa[n]:src.qa[n]+count]
 return z
def hand(ch,pos,load='carry'):
 h=c.hand(ch,pos,load)
 if ch.held_id and ch.cfg.get('connected_handles'):h['R']['held_kg']+=.40 if ch.cfg.get('outboard_handles') else .15
 return h
