"""R19 #36 / #42: the PGC-140 cable on the m2 wedge mount (new file). Report: R19_M2CABLE.md.
arms.py calls register(ARMS) after the mount options, which adds the cable options of the two m2 bases in the style of the
existing ones (arms.py, R19 #36): <base>c_<routing> = the base option (gripper on the m2 wedge, r19mount.py) plus the cable
shapes of r19cable.ROUTINGS[<routing>] on R_tool. arms.swap applies the mount first and then r19cable.add, so the shapes
sit on the re-posed gripper and a '_tc' run ends on the arm's tool connector as seen from the m2 pose (r19cable2_tc.port_H).
Registered per m2 base:
 - every first-section routing of r19cable.py (no run to the tool connector; the run of the old mount, '<r>_tc*', is NOT
   registered: its corner points belong to the old gripper pose);
 - the m2 runs of ROUTES_M2 below (added to r19cable2_tc.ROUTES / r19cable.ROUTINGS as '<routing>_m2tc*');
 - the screening models: r19cable.SCREENS of first-section routings, and 'M2TC' (the m2 runs marked _screen).
Nothing that existed before changes: the new routings are added after r19cable's SCREENS were built and after arms.py made
the cable options of the old bases (r19m2cable_md5.py checks every option that existed before).
ROUTES_M2 follows r19cable2_tc.ROUTES: per port key ('ur5e' / 'fr5'), lead = mm along the first-section direction from the
first tie to the first corner, mid = corner points in the housing frame H (mm), exit = the plug's cable-exit direction in H,
tail = mm straight out of the plug's cable exit to the last corner, junction=False = one flexible cable from the boot to the
plug (no M12 junction on the run). The corners were found by a search (R19_M2CABLE.md 3) and screened / certified with
r19cable_check.py."""
import r19cable as CAB,r19cable2_tc as TC
M2_BASES=('ur5e_enc2_pgc_m2','fr5_j6_pgc_m2')
# Other tool connectors than r19cable2_tc.PORTS: a route that names '_port': <key> ends on PORTS_M2[key] instead of the arm's
# default port (r19cable2_tc.build is wrapped below for those routes only; every other route builds exactly as before).
PORTS_M2={
 'fr5io':dict(frame='fr5_w3',p=[-.0400,0.,.0790],axis=[-1.,0.,0.],plug='m12ra',model='fr5',
  what='Fairino FR5 end I/O connector, M12 8-pin female (AI0, AO0, DI0, DI1, 24 V, DO0, DO1, GND): NO RS485, so the PGC runs in '
       "DH's I/O mode and DH pins 1/2 (RS485) must stay unconnected (R19_CABLE2.md 3: a straight M12-M12 cable would put the "
       'RS485 lines on AI0 / AO0)',
  src='M: Fairino FR5 wrist3_link.STL (frcobot_ros2 fairino5_v6): the 8-contact face at 180 deg from DH frame 6 x, centre z 79.0 mm '
      '(21 mm behind the flange at 100), flush with the dia 80 housing (R19_CABLE2.md 3); S: pinout, Fairino Cobots manual 3.5.4, '
      'https://fairino-doc-en.readthedocs.io/latest/CobotsManual/installation.html'),
 'fr5c':dict(r19cable2_port='fr5',plug='m8ra',model='fr5',
  what='Fairino FR5 end RS485 connector, 5-pin, as r19cable2_tc.PORTS["fr5"], but with a COMPACT right-angle plug: the M8-size '
       'envelope of r19cable2_tc.PLUGS["m8ra"] (18 mm mating face to top) instead of the M12 one (26.6 mm), which meets the FR5 '
       "forearm's wrist-1 housing on the spatula chain at every plug clocking (R19_M2CABLE.md 2)",
  src='E: the FR5 5-pin connector type and size are not published (R19_CABLE2.md 3); this option holds only if a right-angle plug '
      'no taller than the m8ra envelope mates with it')}
PORTS_M2['fr5c'].update({k:v for k,v in TC.PORTS['fr5'].items() if k not in ('plug','what','src')})
_build=TC.build
def build(key,arm,tree,r=TC.R_CAB):
 po=TC.ROUTES[key].get('_port')
 if not po:return _build(key,arm,tree,r)
 spec=PORTS_M2[po];k=spec['model'];sv=TC.PORTS[k];TC.PORTS[k]=spec
 try:S,info=_build(key,arm,tree,r)
 finally:TC.PORTS[k]=sv
 if str(arm).startswith(k):info['port']=po   # only the arm whose port is replaced (a route can carry runs for both arms)
 return S,info
TC.build=build
ROUTES_M2={
 'yp_a-45_m2tc':{'_base':'yp_a-45','_screen':True,'_note':'m2 run (R19_M2CABLE.md): UR5e = search candidate yp_a-45_m2u0 (opt_ur_m2_a.json #0), FR5 = yp_a-45_m2c0 (opt_frc_map5_a45.json #0)',
  'ur5e':{'lead':25.496,'mid':[[-255.8,63.37,-83.74],[-256.03,-3.4,-62.89]],'exit':[0.31834,0.0,-0.94798],'tail':47.82,'junction':False},
  '_port':'fr5c',   # FR5: compact right-angle plug on the RS485 port (PORTS_M2['fr5c']); the UR5e uses its own port (ur5e key)
  'fr5':{'lead':20.699,'mid':[[-283.88,38.65,-104.67],[-180.16,-49.89,-40.68]],'exit':[0.75469,-0.53606,-0.37825],'tail':62.78,'junction':False}}}
for _k,_s in ROUTES_M2.items():
 TC.ROUTES[_k]=_s;CAB.ROUTINGS[_k]=dict(CAB.ROUTINGS[_s['_base']],tc=_k)
CAB.SCREENS['M2TC']=[k for k in ROUTES_M2 if ROUTES_M2[k].get('_screen')]
def routings():
 """the routings registered for the m2 bases: first sections, m2 runs, screens (no old-mount runs)."""
 first=[r for r in CAB.ROUTINGS if not CAB.ROUTINGS[r].get('tc')]
 screens=[s for s in CAB.SCREENS if s=='M2TC' or all(not CAB.ROUTINGS[r].get('tc') for r in CAB.SCREENS[s])]
 return first+list(ROUTES_M2)+screens
def register(ARMS):
 for b in M2_BASES:
  ARMS[b+'c']=dict(ARMS[b],name=ARMS[b]['name']+' + cable outlet and first cable section (both jaw sides, R50 bend down)',cable='both_dn',cable_source='R19_CABLE.md section 1; m2: R19_M2CABLE.md')
  for r in routings():ARMS[b+'c_'+r]=dict(ARMS[b],name=ARMS[b]['name']+' + cable, routing '+r,cable=r,cable_source='R19_CABLE.md section 1; m2 runs: R19_M2CABLE.md')
