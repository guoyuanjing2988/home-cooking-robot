"""Traceable hardware choices. Prices are CNY allowances unless explicitly sourced."""
import csv
import numpy as np,mujoco
from scene import load,save,build,H
S={
 'UR_SPEC':'https://www.universal-robots.com/media/1807465/ur5e_e-series_datasheets_web.pdf',
 'UR_PRICE':'https://czzx.csu.edu.cn/csustatic/zbgshwfwl/20221213/3497.html',
 'UR_BRAKE':'https://docs.universal-robots.com/tutorials/controlling-robot-externally/stop-recovery.html',
 'FR_PRICE':'https://fairino.com/Companynews/37.html',
 'FR_SPEC':'https://www.fairino.us/collaborative-robot/fairino/fr5',
 'CR_SPEC':'https://www.dobot.cn/products/cr-series/dobot-cr-series.html?lang=cn',
 'WHEEL':'https://www.zlingkj.com/Data/zlingkj/upload/file/20240102/ZLLG65ASM500%20V2.0%E5%8D%95%E5%87%BA%E8%BD%B4.pdf',
 'DRIVER':'https://www.zlingkj.com/Data/zlingkj/upload/file/20231229/ZLAC8015%E4%BC%BA%E6%9C%8D%E8%BD%AE%E6%AF%82%E9%A9%B1%E5%8A%A8%E5%99%A8%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8CVersion%201.02-20230627.pdf',
 'GRIP':'https://www.dh-robotics.com/wp-content/uploads/2022/03/DH-Robotics-Servo-Electric-Grippers-Product-Gallery-202203D.pdf',
 'REEL':'https://www.brennenstuhl.com/en-DE/products/cable-reels/automatic-cable-reel-ip44-16-2m-h07rn-f-3g1-5',
 'REEL_MANUAL':'https://www.brennenstuhl.com/index.php?index%5Bexplorer%5D%5Baction%5D=download&index%5Bexplorer%5D%5Bfile%5D=shop_articles%2Fen-DE%2Fpdf%2F4007123616657_1241020300_2_xx_data_sheet.pdf&module=explorer',
 'BRAKE':'https://www.mayr.com/en/products/safety-brakes/industrial-brakes/roba-stop-m~55',
 'SPOUT':'https://www.grohe-mena.com/en_cy/eurocube-bath-spout-13303000.html',
 'P16':'https://www.actuonix.com/assets/images/datasheets/ActuonixP16Datasheet.pdf',
 'CUT':'https://iseki-food-ejournal.com/article/69/pdf'}
def main():
 cfg=load('results/selected.json')['config'];tree,meta=build(cfg)
 from checker import Checker
 ch=Checker(tree,meta);q=ch.m.qpos0.copy();q[:3]=[0,-.4,0];r=ch.check(q,full=False)
 mass=r['stability']['mass_kg']
 hardware=dict(status='FEASIBILITY_DESIGN_NOT_QUALIFIED',selected='UR5e, fixed .85m mount canted20deg, four powered wheels, guarded floor tether, no battery',sources=S,
  combinations=[dict(arm='FAIRINO FR5',payload_kg=5,reach_m=.922,mass_kg=22,arm_system_allowance_cny=45000,public_price_cny=18000,price_scope='2023 FR5-SPARK restricted education offer,1000 units; not current general sale',decision='preferred cost-down candidate; no admitted FR5 geometry, mounting-specific envelope or power-loss evidence in this run; cannot transfer UR witnesses'),dict(arm='DOBOT CR5',payload_kg=5,reach_m=.9,mass_kg=25,arm_system_allowance_cny=90000,public_price_cny=None,decision='plausible longer reach; no primary China price or mounting-specific envelope verified'),dict(arm='UR5e',payload_kg=5,reach_m=.85,mass_kg=20.6,arm_system_allowance_cny=180000,public_price_cny=180000,price_scope='2022 CSU procurement:140000 arm+30000 controller+10000 pendant; historical, not a2026 quote',decision='selected verification baseline: complete inherited geometry and rated-CoM documentation; price premium not justified for manufacture until cheaper arm qualified')],
  cart=dict(footprint_m=[.66,.50],aisle_m=.9,total_model_mass_kg=mass,ballast_kg=46.6,ballast='25mm total steel plate thickness in50mm case;0.54x0.44m plates at7850kg/m3; secured low in chassis',structural_mass_kg=18,controller_mass_kg=13.6,electrics_mass_kg=5,mast_mass_kg=6,support_polygon_m=[[-.215,-.175],[.215,-.175],[.215,.175],[-.215,.175]],mass_note='OEM collision/inertia model arm differs from catalogue20.6kg; actual compiled masses used for statics. Structural18kg budget includes brake carriers; final CAD mass distribution unqualified.'),
  drive=dict(model='4x ZLTECH ZLLG65ASM500 V2.0 + ZLAC8015 drivers',voltage_V=48,wheel_diameter_m=.165,housing_width_m=.088,full_axial_envelope_m=.1295,unit_mass_kg=4.85,rated_torque_Nm=10,rated_phase_current_A=7,load_rating_kg_per_two=200,speed_limit_m_s=.10,acceleration_m_s2=.15,mode='four-wheel skid steer; small yaw range+-0.18rad; body yaw sampled then frozen per stroke',brake='4x Mayr ROBA-stop M spring-applied8Nm through custom1:1 hub-ring/offset brake rotor carrier; de-energize-to-apply',brake_open_issue='OEM hub spindle is stationary. A separate rotating-hub coupling is mandatory. Its CAD/envelope and proof strength are NOT yet qualified; source does not imply integrated hub brake.',floor='level, dry, no thresholds; compliant tyres/equalising chassis must retain four-point contact; statics conditional'),
  mount=dict(height_m=cfg['mount_height'],tilt_deg=20,lift=False,reason='Fixed-height map .70/.80/.85/.95/1.00/1.15m. Repeated failures are station/gripper collisions and upright envelope degeneracy; no evidence that a lift solves them. No lift purchased or credited.',column_height_m=cfg['mount_height']-.553,localization=dict(xy_m=.002,yaw_deg=.2,height_m=.001,mechanism='two hard docking stops and fiducial pose refinement; stationary wheel brakes before every stroke',worst_tcp_from_xy_yaw_m=.002+.85*np.deg2rad(.2),status='engineering accuracy target, not measured; nearly consumes5mm pose gate before calibration')),
  gripper=dict(model='DH PGC-140-50',body_dimensions_m=[.1385,.075,.075],mass_kg=1,custom_fingers_mass_kg=.2,stroke_m=.05,force_per_jaw_N=[40,140],allowable_moment_Nm=7,self_locking=True,checker_total_normal_N=150,key_force_N=150,key_moment_Nm=15,note='Conservative full OEM housing added to inherited80mm-wide palm/fingers.150N/15Nm key rule unchanged; OEM7Nm moment limit is an additional unresolved mechanical interface constraint, not silently upgraded to15Nm. Fingers require commodity-food cushioning and verification.'),
  tether=dict(reel='Brennenstuhl1241000300',retraction='spring rewind with half-turn ratchet; not a continuous-duty robotic reel',cable='16+2m H07RN-F3G1.5',voltage_V=230,coiled_power_W=1000,uncoiled_power_W=3500,coiled_current_A=1000/230,uncoiled_current_A=3500/230,dimensions_m=[.48,.14,.32],mass_kg=6.6,envelope_center_m=[2.52,.15,.45],routing='guarded toe channel x=-1.8..2.8,y=-.04..-.01,z=0...03; short front branch with20mm sag envelope; no loop across standing aisle',tension_cap_N=20,tension_status='design requirement for clutch/tension sensor, not published reel force',pinch_trip='fixed rounded channel cover, inlet shroud, encoder/tension fault stop, presence inhibition; stop and intentional reset before anyone enters front gap',limitation='Manual cautions high tractive forces. Ratchet release/fairlead tracking and continuous automatic retrieval remain unqualified; powered constant-tension reel may be required. No automated retraction success claimed.'),
  power=dict(arm_max_W=570,drive_bus_hard_limit_W=240,drive_supply_input_allowance_W=270,IPC_sensors_W=60,gripper_max_W=24,moving_cart_total_W=924,reel_coiled_limit_W=1000,reel_headroom_W=76,appliances_fixed_track_W=500,appliance_scope='P16+valve+washer pump+greens/wedger allowances; independent dry power track, not reel; no heater',brake_coil_power_open=True,note='924W excludes unverified four brake release coils. 1000W coiled reel has insufficient demonstrated reserve until actual coil/driver losses and limiting behavior are closed; peak rating is not granted from3500W fully unwound figure.',battery=False),
  safety=dict(tier='home',budget_cny=18000,one_package=True,items=['presence camera/ToF and door-open pause','E-stop, RCD30mA and PE','low speeds and arm PFL','lid/door interlocks; NC water valve','retained tools; de-energize drive brakes','cable-tension stop; leak sensor'],restart='manual intentional reset after cleared occupancy/doors/cable fault; no automatic resume',unqualified=['drive brake hub coupling','reel ratchet automation','stop distance on wet floor','guard/drawer ownership transitions']),
  parking=dict(assumed_alcove_m=[[1.8,-.9,0],[2.8,0,2.4]],status='site assumption only; photos do not prove end alcove',door_sweeps='all upper/lower cabinet/oven sweeps remain x<=1.8; parked robot x>=1.81 is separating-axis certificate'),
  no_purchase_or_supplier_contact=True)
 save('results/hardware.json',hardware)
 rows=[]
 def add(item,qty,value,source='',status='China planning allowance; not quoted'):rows.append(dict(item=item,quantity=qty,total_cny=value,source=source,status=status))
 add('UR5e arm+controller+pendant',1,180000,S['UR_PRICE'],'Historical2022 China procurement reference; current price unverified')
 add('Four powered wheels and drivers',4,10000,S['WHEEL']);add('Four spring-applied brakes and custom hub couplings',4,8000,S['BRAKE']);add('Cart frame fixed mast covers and secured steel ballast',1,7000)
 add('PGC140-50 and washable keyed custom fingers',1,12000,S['GRIP']);add('Reel guarded floor guide and tension system',1,4500,S['REEL']);add('AC48V supply current limit and regeneration dump',1,2500)
 add('IPC vision network',1,8000);add('Site installation and docking stops',1,12000);add('Qualification labour',1,20000)
 add('ONE home safety package',1,18000);add('Dry fixed household power track',1,3000)
 add('GROHE13303000 wall spout',1,1500,S['SPOUT']);add('NC valve',1,300);add('P16 guide root holder and guards',1,6400,S['P16']);add('Golden mandoline holder clamps catch tray',1,4500);add('Low greens fixture',1,2800);add('Low tomato fixture',1,3200);add('Basket and physical cradle',1,600);add('Four bowls full bails pins',1,1600);add('Input and scrap containers',1,1200)
 subtotal=sum(r['total_cny'] for r in rows);add('ONE15percent reserve',1,round(subtotal*.15,2),'','Single project reserve');add('TOTAL',1,round(subtotal*1.15,2),'','Feasibility estimate, not passing design')
 with (H/'results/costs.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
 save('results/cost_summary.json',dict(subtotal_cny=subtotal,reserve_cny=subtotal*.15,total_cny=subtotal*1.15,alternative_FR_allowance_total_cny=(subtotal-180000+45000)*1.15,alternative_CR_allowance_total_cny=(subtotal-180000+90000)*1.15,public_current_China_price_coverage='incomplete; no false quotations'))
 print('hardware mass',mass,'cost',subtotal*1.15)
if __name__=='__main__':main()
