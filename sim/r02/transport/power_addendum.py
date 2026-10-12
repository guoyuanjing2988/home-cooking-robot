"""Public-source power comparison and reproducible sizing; no procurement/contact.

Run through bounded.py. Regenerates the separate power record, embeds it in the
transport JSON, and appends the same Markdown section exactly once.
"""
import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
R = HERE / 'results'
POST = ROOT / 'posts/r02/transport.md'
DATE = '2026-10-07'

SOURCES = [
    ('P01', 'Bull official household power-track page', 'https://www.gongniu.cn/show-209-438-1.html', 'Manufacturer product-family evidence; maximum current 10 A on page is not a matched GQ1 backbone/IP certificate.'),
    ('P02', 'Quanxingtai Bull GQ1 China retail listing', 'https://www.quanxingtai.com/goods.php?id=13131', '500 mm + 3 adapters: headline 367.08 CNY, variant table 305.90 CNY; 750 mm 431.85; 1000 mm 559.53. Advertised backbone 32 A/250 V. Price discrepancy unresolved; technical ratings require OEM SKU confirmation.'),
    ('P03', 'Consumer commission 2023 comparative track-socket test', 'https://www.hn315.net.cn/newones.asp?id=13340', 'Published 2024-02-26, 12 products, 200-500 CNY; tested samples lacked aggregate overload and leakage protection. Does not certify continuous powered sliding duty or current model IP.'),
    ('P04', 'Xiaomi official Mijia power-track product', 'https://www.mi.com/shop/buy/detail?product_id=19055', 'Product exists; dynamic page did not expose verifiable current price, matched IP or continuous sliding-contact rating. No launch/subsidy price substituted.'),
    ('P05', 'UF ACTORY arm and controller specifications', 'https://docs.xarm.ufactory.cc/8.technical_specifications.html', 'Arm minimum 8.4 W, typical 200 W, recommended 500 W supply; DC controller input 24-72 V, output 24 V/672 W max; xArm6 5 kg payload, 12.5 kg arm, 700 mm reach.'),
    ('P06', 'UF ACTORY xArm user manual v2.0.0', 'https://www.ufactory.cc/wp-content/uploads/2023/05/xArm-User-Manual-V2.0.0.pdf', 'PDF page 217 lists min/typical/max consumption 8.4/200/500 W. Max 500 W is a catalog maximum, not a measured instantaneous waveform; input-current entries differ between revisions.'),
    ('P07', 'UF ACTORY DC controller electrical interface', 'https://docs.xarm.ufactory.cc/3.controller_electrical_interface.html', 'DC1300: input 24-72 VDC, output 24 VDC/672 W maximum; OEM controller used intact. Protective/functonal-earth implications remain a whole-system qualification issue.'),
    ('P08', 'Universal Robots UR5e manufacturer specification sheet', 'https://www.universal-robots.com/media/1819032/ur5e-tech-spec_tcn_202105.pdf', 'Typical average about 250 W; maximum average 570 W. The latter is not instantaneous peak or startup current. Historical sheet used for power evidence, not to overwrite current reused arm geometry.'),
    ('P09', 'Universal Robots OEM AC/DC controller specifications', 'https://www.universal-robots.com/manuals/EN/HTML/SW5_25/Content/prod_oem_cb_all/oem_cb_all_specs_root.htm', 'OEM DC input 19-72 V, typical 24-48 V; 4.3 kg, 451x150x168 mm; inrush up to 400 A, external fuse max 100 A, UR5e controller heat dissipation max 100 W. Standard AC controller cannot simply take DC.'),
    ('P10', 'Universal Robots mains connection requirements', 'https://www.universal-robots.com/manuals/EN/HTML/SW10_12_1/Content/prod-usr-man/complianceUR5e/H_g5_sections/installation/mains_connection.htm', 'Protective earth, correct fuses and RCD; use original/OEM interfaces and isolate all sources. No Type B mandate inferred for every controller.'),
    ('P11', 'Conductix-Wampfler 0811 manufacturer Chinese catalog', 'https://cdn.conductix.com.cn/cdn/ff/19EmMw97qmKO53e4ZdeTTQlzXvn-F2gwMQyq7ULb3kY/1753690205/public/downloads/KAT0811-0002I-CN%20%E5%8D%95%E6%9E%81%E7%BB%84%E5%90%88%E5%BC%8F%E6%BB%91%E8%A7%A6%E7%BA%BFSingleFlexLine0811.pdf', 'SingleFlexLine 0811 conductor-rail family, IP23 installed system; not washdown/grease protection. Matched 48 VDC low-voltage contact material and derating must be established.'),
    ('P12', 'Conductix-Wampfler 0811 German manufacturer catalog', 'https://www.conductix.com/sites/default/files/downloads/KAT0811-0002-D_Isolierte_Schleifleitung_SingleFlexLine_Programm_0811_1.pdf', 'Page 24: short 40 mm shoe, copper-graphite 40 A vs pure carbon 16 A; normal force 3 N each, mass 0.09 kg; use high-flex double-insulated leads. Catalogue normal force is not drag friction.'),
    ('P13', 'VAHLE KBHF/KBHS manufacturer catalog', 'https://www.vahle.com/fileadmin/cavok_upload/US%20Catalogs/vPOWER%2004b%20KBHF%20KBHS%20Enclosed%20Conductor%20System.pdf', 'Enclosed sliding conductor rails, 4/5 poles, family 63-200 A, IP23/IP24 with sealing strips. Not an arm support or an automatically splash-proof food-prep component.'),
    ('P14', 'Mean Well RSP-1500 manufacturer specification', 'https://www.meanwell.com/Upload/PDF/RSP-1500/RSP-1500-SPEC-CN.PDF', '48 V variant 32 A/1536 W, 91% typical efficiency, PF 0.95 at 230 V, typical AC input 8 A at 230 V, inrush 60 A at 230 V, overvoltage trip 57.6-67.2 V. 278x127x83.5 mm, 3 kg, fan cooled, noncondensing. Component certificate is not installed SELV proof.'),
    ('P15', 'Weimro RSP-1500-48 China price', 'https://www.weimro.com/product/detail/91575844', '1868.80 CNY per unit displayed, tax basis not explicit. Use only price, not retailer technical summary.'),
    ('P16', 'Oneyac RSP-1500-48 China price', 'https://www.oneyac.com/product/34972221.html', '2793 CNY quantity one, tax-inclusive displayed price; used as the conservative PSU price anchor.'),
    ('P17', 'Mean Well RSP-3000 manufacturer specification', 'https://www.meanwell.com/Upload/PDF/RSP-3000/RSP-3000-SPEC-CN.PDF', '48 V 62.5 A/3000 W; use manufacturer input range, not conflicting merchant summary.'),
    ('P18', 'DigiKey China RSP-3000-48 price', 'https://www.digikey.cn/zh/products/detail/mean-well-usa-inc/RSP-3000-48/7706324', '4792.19 CNY quantity one including 13% VAT; price anchor for 3 kW docking supply.'),
    ('P19', 'Schneider Type B RCCB applicability', 'https://www.se.com/th/en/faqs/FA339268/', 'Type B RCCB detects DC residual leakage while supplied from AC; this product is not for a DC distribution circuit. Updated 2026-04-15.'),
    ('P20', 'Schneider RCD coordination with DC leakage', 'https://www.electrical-installation.org/enwiki/RCDs_selection_in_presence_of_DC_earth_leakage_currents', 'Type A 6 mA / Type F 10 mA smooth DC tolerance; drives/converters can blind upstream devices; select and coordinate protection for the actual converter. Updated 2026-08-05.'),
    ('P21', 'IEC-authored control-equipment standard preview', 'https://www.iteh.us/catalog/standards/clc/6caddc76-f5f1-4ede-a4a8-aa90a4c53602/en-iec-61010-2-201-2024', 'IEC 61010-2-201:2024 definitions 3.109/3.110: 60 VDC dry vs 35 VDC wet under normal/single-fault conditions. Authorized-distributor preview of primary standards text; applicability to the complete kitchen cell not asserted.'),
    ('P22', 'Eaton XLR-48 manufacturer datasheet', 'https://www.eaton.com/content/dam/eaton/products/electronic-components/resources/data-sheet/eaton-xlr-48-supercapacitor-module-data-sheet.pdf', 'XLR-48R6167-R: 166 F, 48.6 V, initial ESR max 5 mOhm, approximately 419.5x194.5x177 mm, conservative mass 14.7 kg. Module voltage must not be exceeded; not a small 100 ms capacitor.'),
    ('P23', 'Eaton XLR-48 manufacturer SKU', 'https://www.eaton.com/ca/en-gb/skuPage.XLR-48R6167-R.html', '86 A continuous at 15 C rise, capacitance end of life 80%, ESR end of life 200%. SKU mass 14.197 kg differs from datasheet 14.7 kg: size using larger datasheet mass.'),
    ('P24', 'DigiKey China XLR-48 price', 'https://www.digikey.cn/zh/products/detail/eaton-electronics-division/XLR-48R6167-R/5956249', '11163.85 CNY quantity one including 13% VAT; displayed stock/lead time can change. Price is module only.'),
    ('P25', 'Staubli CombiTac direqt manufacturer catalog', 'https://www.staubli.com/content/dam/ecs/catalogs-brochures/IND/CT-Direqt-11014015-en.pdf', 'Pages 16-17: 4 mm up to 80 A class; /10 contacts with 10 mm2 wires 81 A catalogue rating, average sliding force 9.5 N/contact, 10000 cycles, IP2X. Page 74 plugging force 1.5 times sliding force; page 79 no mating under load. Current derating and enclosing system remain required.'),
    ('P26', 'Staubli CombiTac uniq manufacturer catalog', 'https://www.staubli.com/content/dam/ecs/catalogs-brochures/IND/CT-Main-11014009-en.pdf', 'Uniq up to 100000 cycles, rather than direqt 10000; matched contact/enclosure selection needed. Do not transfer direqt insertion-force numbers or housing IP to unspecified uniq modules.'),
    ('P27', 'Molicel P28A manufacturer cell datasheet', 'https://www.molicel.com/wp-content/uploads/INR18650P28A-V2-80093.pdf', '3.6 V nominal, 2.8 Ah typical, 35 A maximum discharge, 46 g typical, 4.2 V charged. Cell ratings do not certify any assembled pack, BMS or IP; high-current thermal behavior must be qualified.'),
    ('P28', 'LYBATT Chinese manufacturer 48 V pack', 'https://cn.lybatt.com/products/48v-20ah-lifepo4-battery', '48 V/20 Ah/960 Wh, 25 A continuous/30 A peak, 37.5-54.75 V range, 445x97x212 mm, IP64 advertised; matched public price unavailable. Oversized energy but not enough UR worst-case current at minimum voltage.'),
]
S = [dict(id=i, title=t, url=u, evidence=e, accessed=DATE,
          source_kind='primary_manufacturer_or_retailer_or_primary_test',
          access_note='Public page/PDF or indexed primary content; no login, purchase or supplier contact. Prices are displayed snapshots, not confirmed quotes.')
     for i, t, u, e in SOURCES]
SM = {s['id']: s for s in S}
def cite(*ids):
    return ', '.join('[' + SM[i]['title'] + '](' + SM[i]['url'] + ')' for i in ids)
def dump(name, obj):
    (R / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')

ETA = .90  # Conservative combined conversion/provisioning assumption, not OEM efficiency.
RAIL_W, AUX_W = 150, 40  # Electrical allowances, motor selection pending, NOT process forces.
UR_DESIGN_W = 570 * 1.5 + RAIL_W + AUX_W
XA_DESIGN_W = 672 + RAIL_W + AUX_W
def bus_current(power, v):
    return round(power / (ETA * v), 5)
T, MARGIN, RETENTION = 20, 1.5, .8
VHI, VLO = 47.5, 36
E = UR_DESIGN_W * T * MARGIN / ETA
CAP = 2 * E / ((VHI ** 2 - VLO ** 2) * RETENTION)
EXAMPLE_F = 166
BUFFER = dict(
    sizing_basis='Worst UR steady provision 1.5 x 570 W + 150 W rail + 40 W auxiliaries. Not a measured cooking cycle or true instantaneous robot peak.',
    uninterrupted_transit_and_enabled_hold_s=T, conversion_efficiency_assumption=ETA,
    energy_margin=MARGIN, capacitance_end_of_life_retention=RETENTION,
    charge_voltage_V=VHI, bus_low_cutoff_V=VLO,
    energy_equation='E=P_downstream*t*margin/eta; C_initial_min=2*E/((Vhi^2-Vlo^2)*EOL_retention)',
    required_energy_with_margin_J=round(E, 5), required_energy_with_margin_Wh=round(E / 3600, 5),
    required_initial_capacitance_F=round(CAP, 5), selected_minimum_initial_capacitance_F=100,
    xarm_required_initial_capacitance_F=round(2 * XA_DESIGN_W * T * MARGIN / ETA / ((VHI**2 - VLO**2) * RETENTION), 5),
    worst_input_current_at_36V_A=bus_current(UR_DESIGN_W, VLO),
    example=dict(model='Eaton XLR-48R6167-R', capacitance_F=EXAMPLE_F, maximum_V=48.6,
                 initial_ESR_max_ohm=.005, EOL_ESR_max_ohm=.010, continuous_A_at_15C_rise=86,
                 mass_design_kg=14.7, size_xyz_m=[.4195, .1945, .177],
                 usable_energy_EOL_47p5_to_36_Wh=round(.5 * EXAMPLE_F * RETENTION * (VHI**2 - VLO**2) / 3600, 5),
                 voltage_drop_EOL_at_worst_A_V=round(bus_current(UR_DESIGN_W, VLO) * .010, 5),
                 price_module_cny=11163.85, price_tax='13% VAT included',
                 source_ids=['P22', 'P23', 'P24'],
                 eligibility='Energy/current example only; size and mass outside baseline moving envelope. New inertia, stiffness, passing, thermal and braking checks required.'),
    startup_surge_handled='OEM DC energization/precharge while docked, with validated OEM-compatible current-limiting interface; do not debit 400 A inrush against this steady-transit calculation.',
    docking_supply=dict(nominal_output_V=48, reserved_power_W=2500,
                        package_example_W=3000, maximum_load_at_42V_A=round(2500 / 42, 5),
                        selected_contact_class_A=80, net_recharge_target_W=1000,
                        ideal_min_refill_s=round(UR_DESIGN_W * T / ETA / 1000, 5),
                        note='About 23.22 s ideal refill for the actual un-margined 20 s energy consumption; CC/CV limits, conversion and balancing lengthen this. Dock pack is 3 kW per lane, not the 1.536 kW sliding-bus PSU.'),
    battery=dict(architecture_status='Compared because the addendum explicitly requests it; not adopted. Original no-battery architecture otherwise retained.',
                 minimum_usable_energy_Wh=round(E / 3600, 5), minimum_output_power_W=round(UR_DESIGN_W / ETA, 5),
                 minimum_discharge_A_at_36V=bus_current(UR_DESIGN_W, 36),
                 high_rate_cell_example='13-series P28A-type pack: approximately 46.8 V nominal, 54.6 V full, 131 Wh and 0.598 kg cells only. Not a selected/built/certified pack; manufacturer supplies a cell maximum, not pack continuous rating.',
                 planning_complete_pack_allowance_cny=[800, 2000], matched_pack_public_price_cny=None,
                 rejected_catalog_example='LYBATT 960 Wh:25 A continuous <30.96 A provision at37.5 V; 30 A unspecified-duration peak also insufficient. IP64 claim does not cure current/geometry mismatch.',
                 source_ids=['P27', 'P28']),
    stop_energy_status='Reserve for declared 20 s window is calculated; actual SS1 deceleration energy and regenerative absorption are not measured. Before acceptance, prove both positive load and braking energy paths, UV reserve and spring-brake operation.'
)

BUDGETS = dict(
    A_stationary_household_track=dict(fixed_cny=2500, per_carriage_cny=0, range_multiplier=[.8, 1.4]),
    B_48v_sliding_conductor=dict(fixed_cny=8000, per_carriage_cny=12000, range_multiplier=[.65, 1.6]),
    C_supercap_docks=dict(fixed_cny=12000, per_carriage_cny=32000, range_multiplier=[.7, 1.6]),
    C_battery_docks=dict(fixed_cny=12000, per_carriage_cny=14000, range_multiplier=[.6, 1.8]),
)
COST_ROWS = []
for name, b in BUDGETS.items():
    for n in (2, 3, 4):
        c = b['fixed_cny'] + n * b['per_carriage_cny']
        b.setdefault('packages_cny', {})[str(n)] = c
        COST_ROWS.append(dict(option_id=name, carriages=n, transport_run_m=2.4,
                              low_cny=round(c * b['range_multiplier'][0]), base_cny=c,
                              high_cny=round(c * b['range_multiplier'][1]),
                              basis='gross_power_package_planning_not_quote', date=DATE,
                              includes='power_hardware_guards_protection_local_interface_installation_allowance',
                              excludes='OEM_arm_controller_or_replacement_guide_redesign_building_circuit_rebuild_certified_cell_NRE',
                              baseline_overlap='Do not add blindly to99000:existing chain/electrical allowance overlaps; power-package saving cannot be separated from existing lump-sum BOM.'))
with (R / 'power_costs.csv').open('w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(COST_ROWS[0])); w.writeheader(); w.writerows(COST_ROWS)

POWER = dict(
    schema_version='r02.transport.power.1', date=DATE,
    scope='Power-track addendum only; baseline mechanical recommendation and39transport cost rows unchanged.',
    recommendation=dict(arm_power='dedicated_cable_chains',
                        appliance_power='stationary_household_power_track',
                        conditional_free_switching_upgrade='48v_dc_sliding_conductor_with_oem_dc_controller',
                        rationale='Passing lanes already permit overtaking and stopping anywhere without disconnecting power/data. Keep fixed standard UR controllers and approved flex arm cables. Industrial DC sliding pickup is technically credible if lane changes become necessary; household clips cannot be used as moving collectors. Dock buffers are lower-ranked due to finite autonomy, docking schedule, added mass and contacts.',
                        baseline_3arm_transport_cny=99000,
                        baseline_status='Same previously screened cable geometry; no source model/input/checker modifications.'),
    no_new_contact_exemptions=True, mechanical_collision_screen_for_added_power_hardware=False,
    arm_budgets=[
        dict(arm='UR5e standard controller', average_typical_W=250, catalog_maximum_average_W=570,
             instantaneous_peak_W=None, input='100-240 VAC OEM standard controller; 220 VAC China comparison',
             current_typical_220VAC_unity_PF_A=round(250 / 220, 5), current_max_average_220VAC_unity_PF_A=round(570 / 220, 5),
             caveat='P/V is ideal real-power current, not nameplate/fuse/inrush; 570 W is a maximum AVERAGE. No artificial measured peak substituted.',
             source_ids=['P08', 'P10']),
        dict(arm='UR5e OEM DC controller, conditional carriage-mounted upgrade', average_typical_W=250,
             catalog_maximum_average_W=570, instantaneous_operating_peak_W=None,
             native_input_V=[19, 72], typical_native_input_V=[24, 48],
             controller_mass_kg=4.3, controller_size_whd_m=[.451, .150, .168],
             catalog_max_inrush_A=400, inrush_duration_verified_s=None, external_fuse_max_A=100,
             average_arm_current_48V_conservative_A=bus_current(250, 48),
             maximum_average_arm_current_48V_conservative_A=bus_current(570, 48),
             arm_steady_provision_W=855, margin_on_max_average=1.5,
             carriage_total_downstream_design_W=UR_DESIGN_W, carriage_total_input_design_W=round(UR_DESIGN_W / ETA, 5),
             carriage_total_input_design_A_48V=bus_current(UR_DESIGN_W, 48),
             carriage_total_input_design_A_42V=bus_current(UR_DESIGN_W, 42),
             startup_gate='Controlled energization validated against OEM DC installation requirements; 40 A collectors do not acquire400 A surge capability. Inrush duration/soft-start compatibility unverified.',
             source_ids=['P08', 'P09']),
        dict(arm='UF ACTORY xArm6 with DC1300', average_typical_W=200, minimum_catalog_W=8.4,
             catalog_maximum_W=500, instantaneous_operating_peak_W=None,
             max_controller_output_W=672, native_controller_input_V=[24, 72], internal_arm_voltage_V=24,
             input_current_datasheet_conflict='Different manual/HTML revisions list16.5 or20.8 A at24V; use explicit power limits/controller rating and do not silently mix them.',
             mass_kg=12.5, flange_payload_kg=5, reach_m=.7,
             payload_note='5 kg flange permits3 kg food+1.2 kg gripper on mass alone; xArm7 3.5 kg does not. xArm6 reach/model/spring brakes not approved by existing UR geometry screen.',
             average_arm_current_48V_conservative_A=bus_current(200, 48),
             max_arm_current_48V_conservative_A=bus_current(500, 48),
             controller_output_envelope_current_48V_conservative_A=bus_current(672, 48),
             carriage_total_downstream_design_W=XA_DESIGN_W,
             carriage_total_input_design_A_48V=bus_current(XA_DESIGN_W, 48),
             carriage_total_input_design_A_42V=bus_current(XA_DESIGN_W, 42),
             startup_inrush_A=None, source_ids=['P05', 'P06', 'P07']),
    ],
    shared_electrical_assumptions=dict(combined_efficiency=.9, rail_servo_allowance_W=RAIL_W,
                                     auxiliaries_allowance_W=AUX_W, source_type='engineering electrical provisioning; not sourced motor peak or food-process load',
                                     dynamic_food_loads_unchanged=True, arm_peak_waveforms_need_measurement=True),
    options=[
        dict(id='A_stationary_household_track', recommended=True,
             application='220 VAC fixed appliance/tool power in verified dry positions, clips manually repositioned with power off and stationary in operation',
             moving_arm_eligibility='Rejected as sliding collector; no matched continuous powered-sliding rating.',
             sources=['P01', 'P02', 'P03', 'P04'],
             current_limit='At220V10A adapter=2200W;10A/16A feed=2200/3520W at unityPF. Installed circuit, adapter, feed, conductor and protective-device lowest rating governs;32A marketing backbone does not raise a wall-outlet circuit rating.',
             appliance_provisioning_example=dict(dicer_W=300, washer_pump_W=100, spinner_W=150,
                                                total_W=550, total_current_220V_unity_PF_A=2.5,
                                                status='Electrical allowances only; actual appliance datasheet watts/locked-rotor current must replace them. No new cutting/pressing force claim.'),
             household_IP_rating_verified=None,
             environmental_rule='Treat matched SKU as dry-only until its installed, adapter-mated IP rating is proven. Covers are not an IP certificate. No track across sink, exposed underside slots or direct spray; isolated damp wiping only.',
             wear_arcing='Stationary mating only; power off before relocation. No continuous wear/sliding lifetime data; contact bounce, scraping plated copper, deposits, PE interruption and load arcing are foreseeable engineering concerns.',
             protection='PE for Class I appliances/aluminium as OEM requires; upstream30mA RCBO design baseline and correct overload protection. Choose RCD type from actual load leakage. Fixed, accessible isolator; appliance restart inhibited after trip.',
             data='No power-bus Ethernet/EtherCAT; wired station I/O. Xiaomi smart/WLAN control only supervisory, never safety credited.',
             passing_rails='Independent static utility for fixtures; no arm-carriage contact or cable drag.',
             switches='Same static utility; does not solve arm switching power.',
             cost=BUDGETS['A_stationary_household_track']),
        dict(id='B_48v_sliding_conductor', recommended=False, conditional_preference_for_switches=True,
             application='Dedicated insulated industrial copper busbars and copper-graphite collectors, OEM DC controller onboard, separate structural arm guides',
             nominal_VDC=48, minimum_bus_design_VDC=42,
             selected_continuous_collector_class_A=40, selected_continuous_derating_factor=.8,
             minimum_derated_continuous_A=32,
             topology='Independent48V32A-class PSU/feed per lane; + and0V each two suitably separated40A shoes for continuity, each shoe rated for whole carriage steady current. Bond/PE path separate where Class I/PELV requires it. Do not add collector ratings without OEM load-sharing approval.',
             collector_example=dict(model='Conductix081101-0011 copper-graphite40mm', nominal_A=40,
                                    normal_force_each_N=3, mass_each_kg=.09, shoe_length_m=.04,
                                    collector_count_power_shoes_per_carriage=4, total_normal_force_N=12,
                                    tangential_drag_force_N=None,
                                    drag_note='Measure after running-in/contamination; mu=0.5 is the unchanged food gripper coefficient, not carbon brush friction.'),
             dc_low_voltage_contact_grade_approved=False,
             vendor_installed_IP='Conductix0811 IP23;VAHLE KBH IP23/IP24 variants',
             environmental_rule='Dry protected conduit with downward/lateral guarded openings, removable catch tray for carbon/copper debris, accessible isolated maintenance. No washdown, grease-on-contact or particles above open food. Final sealed assembly water/food-cleaning test required.',
             wear_arcing='Wear is expected maintenance; no kitchen duty life number invented. Log distance and contact voltage/temperature, inspect brushes/rail joints. DC interruption may sustain arc; precharge controller and prohibit energized pickup through open joints.',
             safety_class='Nominal48V ELV only. SELV requires protective separation, fault voltage and floating output proof; earthed0V gives PELV.48V is above35VDC wet-control-equipment preview limit; enclose and relocate out of wet access.',
             PSU_example=dict(model='RSP-1500-48', output_A=32, output_W=1536,
                              price_anchor_cny=2793, lower_merchant_price_cny=1868.8,
                              current_budget_headroom=round(1536 / (UR_DESIGN_W / ETA), 5),
                              overvoltage_trip_range_V=[57.6, 67.2], installed_SELV_proof=False,
                              gate='Independent validated voltage limiting/fault protection and system certificates, or choose a suitably certified supply. Current-limit and startup compatibility still needed.'),
             data='OEM Ethernet local to carriage gateway; WLAN for supervisory traffic with local execution/watchdog and a separately certified safe stop channel, or industrial contactless Ethernet guide. Raw Ethernet/EtherCAT across carbon brush poles is unqualified.',
             passing_rails='One continuous protected bus per straight lane. Controller/guard geometry must be rebuilt; existing cable-model PASS does not extend to this option.',
             switches='Collector-compatible pickup guides, electrically isolated/latching transfer deck, DC backfeed blocking, buffer/UV-stop reserve for measured gap. No shoe bridging unequal live supplies or traversing unprotected live gaps.',
             source_ids=['P07', 'P09', 'P11', 'P12', 'P13', 'P14', 'P15', 'P16', 'P19', 'P20', 'P21'],
             cost=BUDGETS['B_48v_sliding_conductor']),
        dict(id='C_supercap_docks', recommended=False, nominal_buffer_VDC=48,
             application='Carriage buffer powered from the mains at fixed industrial docking connectors; no household track auto-clipping and no chemical battery adopted.',
             buffer=BUFFER, dock_count_per_lane_cost_assumption=4,
             collector_example=dict(family='CombiTac direqt4mm /10 reference; final automated dock contact family must be selected', contact_class_A=80,
                                    source_rated_A_with_10mm2=81, installed_derating_required=True,
                                    power_contact_count=2, average_sliding_force_per_contact_N=9.5,
                                    vendor_plug_to_slide_factor=1.5, extra_engineering_margin=1.5,
                                    power_contacts_only_design_insertion_N=round(2 * 9.5 * 1.5 * 1.5, 5),
                                    power_plus_PE_contacts_only_design_insertion_N=round(3 * 9.5 * 1.5 * 1.5, 5),
                                    actual_full_dock_insertion_force_N=None,
                                    force_note='Known two-power-contact lower-bound design provision42.75N,64.125N if same-class PE added. Add measured guide/seal/interlock/data forces; average catalog value is not guaranteed contaminated peak. Force borne by carriage dock actuator, not an invented arm cutting force.'),
             wear_arcing='Direqt10000 vs uniq up to100000 cycles; select exact product before life credit. Zero-current mating/unmating, contactor+precharge/backfeed blocking and last-mate-first-break interlock. Need enclosure protection in both mated and open states.',
             IP='Bare contact frontIP2X: touch protection only, not water. HousingIP65/67 catalogue is conditional on actual matched housing/closed state; dock open state needs separately tested cover.',
             protection='AC-side coordinatedRCD/overload; DC-rated protection close to both buffer and charger; voltage/cap-balance monitoring, energy discharge isolation, UVSS1 reserve, spring brakes. Buffer must not defeatSTO or automatically restart.',
             data='WLAN+onboard controller in motion, matched Ethernet docking module for stationary use; certified safe-stop link and local fail-safe watchdog. Do not require fieldbus reconnection to be the sole stop channel.',
             passing_rails='Can pass with finite20s energy window; long food-prep holds require task-station docks. Stops anywhere remain mechanically possible, indefinite powered work anywhere does not.',
             switches='Bridges electrically dead switches/transfer gaps while charged; latch/geometry/structural safety remain independent. Schedule energy return before undertaking route.',
             process_phases='AddD00 controlled precharge, D01 zero-current undock, D02 energy-bounded transit, D03 dock/latch verify, D04 zero-current mate/precharge/power transfer. Keep everyP01-P16 product requirement; no new contact exemptions or food-force assumptions. Dock scenes not yet checker-approved.',
             source_ids=['P09', 'P17', 'P18', 'P22', 'P23', 'P24', 'P25', 'P26'],
             cost=BUDGETS['C_supercap_docks']),
        dict(id='C_battery_docks', recommended=False,
             architecture_status='Evaluation requested by addendum; conflicts with original no-battery default, so not adopted.',
             sizing=BUFFER['battery'],
             interfaces='Same interlocked zero-current industrial DC dock asC_supercap; chemistry-specific charger, qualifiedBMS, temperature/current protection, isolated output, state-of-health reserve. Never charge by directly clipping pack onto household230V track.',
             wear_arcing_IP_data_and_movement='Dock mating/data/arc controls asC_supercap; packIP and thermal/BMS certification independent. Switched rails supported while energy lasts; unknown pack life must not become a promised replacement interval.',
             source_ids=['P27', 'P28'], cost=BUDGETS['C_battery_docks']),
    ],
    price_anchors=[
        dict(item='BullGQ1 recessed500mm+3adapters', low_cny=305.90, high_cny=367.08, source_ids=['P02'], limitation='Headline/table discrepancy; recessed hardware price is not a quote for a different surface/dry-panel SKU.'),
        dict(item='BullGQ1 750mm /1000mm variants', prices_cny=[431.85, 559.53], source_ids=['P02'], limitation='No price for a custom2.4m unbroken household rail. Use separate OEM modules, not field-cut/spliced live track.'),
        dict(item='RSP1500-48 unit', low_cny=1868.8, high_cny=2793, source_ids=['P15', 'P16'], limitation='Supplier tax basis differs; select2793taxinclusive budget. Not a completeSELV source assembly.'),
        dict(item='RSP3000-48 unit', price_cny=4792.19, source_ids=['P18'], limitation='3kW supply only, protective enclosure/SELV proof/current control not included.'),
        dict(item='EatonXLR48R6167-R unit', price_cny=11163.85, source_ids=['P24'], limitation='Module only; China price incl13%VAT.14.7kg design mass.'),
        dict(item='Exact48VDC industrial sliding rail with protected collector set', price_cny=None,
             planning_line_hardware_and_debris_guard_cny=4000, source_ids=['P11', 'P12', 'P13'],
             limitation='Numeric matched China OEM kit quote not publicly found; this4000 is an engineering allowance, not a fabricated vendor price. PSU anchor is public.'),
        dict(item='Matched80A industrial automatic dock set', price_cny=None, planning_per_dock_cny=1500, source_ids=['P25', 'P26'], limitation='Engineering allowance; exact manufacturer China price and chosen full-dock force unavailable.'),
        dict(item='Certified high-rate small buffer battery pack', price_cny=None, planning_pack_cny=[800, 2000], source_ids=['P27', 'P28'], limitation='No matched public price/current/geometry-certified pack; not selected.'),
    ],
    installation_geometry=dict(
        status='Added hardware placement constraints only, NOT instantiated/clearance-proved geometry. Preserve main geometry and original acceptance rules.',
        household_track=dict(continuous_sink_back_track_allowed=False, nominal_lengths_m=[.5, .75, 1.0],
                             position_rule='Short separate dry-zone segments beside stations, away from faucet movement/outlets/cabinet doors. Survey splash reach before assigning coordinates; no speculative wet-zone safety distance substituted.',
                             requested_counter_service_length_m=2.4, illustrative_purchased_modules_m=[1, 1, .5],
                             note='2.5m bought as3independentOEMsegments to serve2.4m counter; unused end length/dry gaps allowed, not a2.4m continuous-cut kit.500mmpricedGQ1 proxy, exact adapted dry-panel product pending.',
                             mount_wall_nonmount_gap_min_m=.01),
        industrial_bus=dict(one_bus_per_passing_lane=True, follow_original_rail_x_m=[-1.5, .9],
                            conductor_poles=['+48V', '0V', 'separate_bond_or_PE_if_required'],
                            controller_center_local_m=None,
                            controller_local_size_with_enclosure_m=None,
                            pose_note='Do not insert a451x150x168mmURDCbox into the existing360mmwide/108mmhighcarriage envelope. Rebuildpassing/door/faucet/outletclearance for enclosure, collectors, debris trays and wiring.'),
        docks=dict(count_per_lane_budget=4, docking_x_m=None,
                   location_rule='At actualprocessstations rather than arbitraryequallyspacedstops; endpoint-onlydocks cannot supplyindefinitewash/cutoperationsawayfromends.',
                   note='No switch or dock contact exemptions added. Validate contacts with existing internal-robot kinematic/contact semantics and unchangedchecker before adopting. Dock insertion/guarding and mounting exceptions need fullphysicalgeometry.'),
        min_robot_environment_gap_m=.01, min_gripper_and_held_tool_gap_m=.005,
        phase_pose_acceptance_m=.005, phase_pose_acceptance_deg=3, unchanged_grip_mu=.5,
        sources_reused_read_only=True),
    source_ids=[s['id'] for s in S], source_registry_file='power_sources.json', cost_file='power_costs.csv',
    open_engineering_gates=['Matched controller input peak/inrush waveform and precharge behavior.',
                            'Actual chosen rail drive watts, brake coil/auxiliary demand and regenerating power.',
                            '48VDC low-voltage contact grade, duty wear/drop/bounce and full guards/IP/food cleanability.',
                            'Protective separation/fault voltage andSELV vsPELV proof, wet-zone exclusion, coordinatedAC/DC protection.',
                            'OEM controller enclosure heat dissipation, mass, geometry, force, stiffness andspring-on-loss arm brakes.',
                            'Certified stop/data-link behavior andpower-loss energy path. No wireless safety credit invented.',
                            'Four-lane budget remains mechanically nonintegrable in this kitchen; power costs do not change that.']
)
dump('power_sources.json', S)
dump('power_options.json', POWER)
D = json.loads((R / 'transport_options.json').read_text(encoding='utf-8'))
D['power_options'] = POWER
dump('transport_options.json', D)

TEXT = r'''
## Power track addendum

补充结论：家用轨道插座适合给固定电器和工装供电，放在经过确认的干燥位置。现有方案的机械臂仍采用各轨独立拖链；这样已经能错车、任意位置停靠，也能保留固定控制箱和有线通信。如果以后确实需要换轨，优先研究 **48 V 工业滑触线＋原厂直流控制箱**。家用旋转适配器不能充当带载滑动集电器。停靠充电只列为备选：按保持机械臂通电的保守工况计算，需要约100 F的电容储能；公开规格完整的166 F模块重14.7 kg，控制箱和护罩还会增加重量。电池方案按本次补充要求比较，但不纳入原来的无电池架构。

### Decision, evidence and power budgets

Use **A for fixed appliances**, retain **dedicated cable chains for the screened passing-arm layout**, and reserve **B for a future lane-changing design**. C is feasible as an electrical topology but is less simple for this kitchen. All comparisons use public data, with no purchase, account creation or supplier contact. Unknown ratings and prices remain explicitly unknown. Displayed China prices were inspected on 2026-10-07; indexed pages can be older snapshots, and none is a confirmed installation quote.

The UR5e power sheet gives about250 W typical average and570 W maximum average. **570 W is not a true instantaneous peak.** The ordinary UR controller takes AC. A genuine OEM DC variant accepts19–72 V, typically24–48 V, and is a credible48 V option without modifying arm electronics. Its startup inrush can reach400 A; the duration and operating transient waveform were not established. Its100 A maximum external-fuse specification is not a400 A continuous operating load. POWER_UR.

UF ACTORY gives200 W typical and its PDF labels500 W maximum, whereas the HTML recommends a500 W supply. DC1300 accepts24–72 V and provides24 V/672 W maximum to the arm. Use the intact OEM DC box; do not feed48 V into the24 V arm connector. xArm6's5 kg flange rating accommodates3 kg food plus1.2 kg gripper on mass alone; its700 mm reach and brake/geometry approval still need separate checking. The3.5 kg xArm7 would not satisfy that combined payload. POWER_XA.

| Arm/controller | Datasheet average / maximum | Instantaneous peak / startup | Current at chosen input | Status |
|---|---|---|---|---|
| UR5e, existing standard AC controller | ~250 W typical;570 W maximum average | Operating peak not published in inspected sheet | At220 VAC:1.14 /2.59 A **ideal at unityPF** | Keep fixed controller and approved arm cable in each chain; fuse/nameplate/inrush require OEM limits |
| UR5e OEM DC,48 V carriage option | Same arm average evidence; direct DC efficiency not separately published | Up to400 A controller inrush; operating waveform unknown | Conservative conversion allowance gives5.79 /13.19 A for250 /570 W at48 V | Continuous pickup provision below is not a startup-surge qualification |
| xArm6+DC1300 at48 V |200 W typical;500 W catalog max;672 W controller-output limit | Startup/instantaneous waveform unknown |4.63 /11.57 A for200 /500 W;15.56 A at672 W output | Different24 V input-current numbers across manual/HTML revisions are not silently combined |

The DC currents include an engineering90% combined conversion/provisioning assumption. This is conservative arithmetic, not a measured OEM efficiency. Reserve150 W for a carriage drive and40 W for logic/brake/gateway auxiliaries; these are electrical allowances pending motor selection, **not new food-process forces**. For UR size steady provision at1.5×570+150+40=1045 W downstream, or1161 W on the assumed DC input:24.19 A at48 V,27.65 A at42 V. For xArm size from the larger672 W controller output:862 W downstream,19.95 A at48 V,22.80 A at42 V. The1.5 UR provision is explicitly a design margin on maximum average, not a claim that the true peak has been measured.

One independent48 V/32 A/1536 W source per lane provides about32% headroom above the UR steady input provision. Do not parallel supplies or add tandem collector current ratings without approved current sharing. Three such sources can draw24 A at230 V at their manufacturer-rated load; they require an assessed dedicated building circuit, not an ordinary16 A socket feed. The quoted source has fan cooling,3 kg mass and278×127×83.5 mm dimensions; keep it stationary in a dry, ventilated electrical cabinet. POWER_PSU.

The100 W UR OEM controller heat-dissipation limit is heat to reject, **not an extra100 W to add a second time to arm consumption**. A carriage enclosure must remove this heat without pulling grease/steam into electronics. Its451×150×168 mm,4.3 kg OEM DC box is outside the existing360 mm wide/108 mm high moving-carriage proxy. No B/C installation inherits the previous cable-layout collision PASS. POWER_URDC.

### A — household appliance/tool power track

A static aluminium/copper household track is useful for a stationary dicer, washer pump, spinner or tool charger. The adapter can be relocated between setups, then remains fixed while supplying power. Retain the OEM matching adapter/track/feed combination and certification; do not combine brands, field-cut or electrically splice a household track. The track carries electricity, **not the arm's15–25 kg structural load or650 N·m mounting moment**. Bull and Mijia have public product pages; a matched TOP track manual/IP/current price was not found, so an ordinary TOP extension-strip price is not substituted. POWER_BRANDS.

China price anchor: Bull GQ1 recessed500 mm+three silver4046 adapters is367.08 CNY in the headline and305.90 in its variant table. The discrepancy is unresolved. The table lists750 mm431.85 and1000 mm559.53 CNY. It advertises32 A/250 V/8000 W on the backbone. This retailer rating is not an OEM adapter or installed-IP certificate. A2×1000 mm+500 mm buying example costs1486.14 CNY using the1000 mm table and500 mm headline; it is **2.5 m purchased in separate modules serving about2.4 m of counter**, not a cut-to-length continuous track. GQ1's recessed price is a budget anchor; a different surface/dry-panel SKU needs its own price. POWER_BULLPRICE.

Apply the **lowest** track, adapter, feed, wire and protective-device rating. With a verified10 A adapter at220 V, its limit is2200 W at unityPF; a10 A feed supplies2200 W total, and a16 A feed3520 W total. A32 A backbone label does not upgrade the household circuit. For sizing illustration only, a300 W dicer+100 W washer pump+150 W spinner totals550 W/2.5 A at220 V; replace these allowances with selected appliance running and starting-current datasheets. Cooking appliances remain outside this food-prep scope.

No matched GQ1/Mijia installed water-IP certificate was obtained: mark it **dry-only/IP unknown**, not IP44/IP65 by assumption. Site it in short dry segments beside stations with drip-protected entry, an accessible isolator, unobstructed wall outlets and cabinet doors, and no direct faucet/washer splash path. Do not prescribe a made-up universal sink setback; survey actual spray/reach. A canopy does not certify the track. Disconnect before cleaning; damp wipe accessible exteriors and avoid spraying into the slot. Aluminium coatings/contact surfaces need detergent compatibility; food-contact guards/trays use appropriate stainless steel or food-safe polymer. Electrical contacts are not food-contact components.

A2023 consumer-commission test of12 products found no aggregate overload/leakage protection in those tested units. Therefore do not assume an adapter's individual switch or a smart function provides upstream protection. Use a30 mA RCBO as the design baseline for the AC appliance branch, verified protective earth for Class I appliances and metal housings, correct cable/overcurrent protection, and load-appropriate RCD type; the installation's earthing/certification still determines the final arrangement. POWER_CONSUMER.

**Why it must not slide under load:** household twist/clip mating lacks an established continuous powered-sliding qualification, specified normal-force tolerance under rail misalignment, debris-management system and wear-distance rating. Engineering failure modes include contact bounce, scraped/oxidized copper, pitting, localI²R heating, broken PE sequencing and load arcing. DC interruptions are especially troublesome because there is no AC current zero. Manually de-energize, reposition and lock the adapter according to its OEM instructions; do not attach it to a motor-driven arm carriage. The household product's convenient repositioning is not evidence that energized scraping is rated. This is an engineering rejection from missing duty evidence, not a claim of a verified manufacturer ban for every household SKU.

Appliance station control uses fixed wired I/O; WLAN/smart adapters may offer supervisory switching but receive no safety credit and must not auto-restart a cutter after power restoration. A neither obstructs arm passing nor supplies arms through switches: it is stationary utility infrastructure. It has no sliding noise; no matched dBA measurement was found.

### B — industrial48 V DC sliding conductor rail / 滑触线

Use separate structural guides and insulated industrial copper conductors, with copper-graphite sliding shoes appropriate for the chosen **48 VDC** current and low-voltage contact behavior. Conductix0811's short40 mm copper-graphite collector is rated40 A, versus16 A for the pure-carbon version; each has3 N normal preload and0.09 kg mass. Four power shoes per carriage—tandem on+48 V and tandem onreturn—have12 N total normal force and0.36 kg shoe mass before mounts/leads. Tandem shoes improve continuity; **each remains capable of the whole27.65 A steady budget** rather than assuming doubled capacity. Use an80% continuous derating provision:40 A→32 A. Catalog rating alone does not prove every brush grade at48 VDC, temperature, condensation or startup duty. POWER_COLLECTOR.

The3 N is a sourced normal contact force. Tangential drag must be measured or supported by a matched carbon/copper friction source; the unchangedμ=0.5 gripper coefficient does not apply to it. No fabricated collector friction force, cooking force or contact exemption was inserted into the simulation.

Conductix0811 is anIP23 installed-system family; VAHLE KBH listsIP23/IP24 variants with seals. These do not establish washdown, grease exclusion or food-safe wear debris. Use a guarded dry channel with accessible isolated maintenance, down/lateral protected pickup opening and a removable carbon/copper-dust catch tray separated from produce and bowls. No lubrication on electrical contact surfaces. Inspect brush length, joint alignment, dust, contact voltage drop and heating; log travel distance. No unsupported kitchen replacement-km, arc-energy or service-year guarantee is given. Scraping/contact-bounce noise and PSU fans remain; no installed dBA estimate is asserted. POWER_CONDUCTOR.

Size a separate+48 V/0 V branch per lane; add a separately reliable PE/bonding path when the OEM/Class I arrangement requires it. The mechanical guide is not an acceptable unverified PE conductor. Keep polarity correct, guard all live pickup faces, and prevent collector backfeed between supplies. A limited ride-through capacitor can suppress **measured** bounce or switch gaps; its required duration must include the verified stop-energy path. DC-rated local fuses/breakers and an actual OEM-compatible startup/precharge interface are required.40 A collector ratings do not cover UR's up-to400 A energization surge. Do not keep re-energizing its controller at every seam.

**48 V is only the nominal voltage, not an established SELV system.** Establish protective separation, insulation, normal/single-fault voltage limits and the OEM controller's earth relationships. Floating protected output may qualify as SELV; earth-referenced0 V is PELV. IEC61010-2-201's control-equipment preview gives60 VDC dry and35 VDC wet definitions; this illustrates why accessible wet48 V contacts should not be called touch-safe. The exact GB/IEC classification for the completed cell must be established. Put the protected48 V path outside wet access, use enclosed contacts, and use24 V or a suitably qualified lower-voltage interface where accessible wet contacts are unavoidable. POWER_WET.

The pricedRSP-1500-48 has an overvoltage-trip range57.6–67.2 V; that upper value prevents claiming a≤60 V single-fault limit from its48 V label alone. It is a **price/capacity anchor, not a selected certified SELV assembly**. Select a suitable certified source, or validate an independent protective voltage-limit/disconnection system with the complete controller circuit. Thermal/current/short-circuit energy protections still matter at low voltage. POWER_PSUFAULT.

Install a coordinated AC-side RCD and overload protection for the source/drive circuit. Type A is a candidate only where the actual converter leakage permits it; use suitable Type B/other approved detection where smooth DC leakage could blind upstream protection. Type A's published smooth-DC tolerance is6 mA. **Do not place an ordinary AC Type B RCCB on the48 V distribution bus:** its DC-leakage sensing capability does not make it a DC-network breaker. Protect DC branches with DC-rated devices; floating-output insulation monitoring and earth relationships must follow the selected safety design. POWER_RCD.

Use a local OEM controller and wired Ethernet to a carriage gateway; supervisory WLAN is possible with local execution/watchdogs and a separately certified safe-stop path. Safety functions must lead to Category1/SS1 thenSTO on a commanded stop, followed by the specified spring-applied rail/arm/Z brakes. Abrupt power loss needs the brakes and a validated energy/UV strategy; sufficient SS1-on-blackout hold-up is not established merely by a capacitor label. Ordinary Wi-Fi, household power-line networking or bare carbon brush poles do not qualify as a deterministic EtherCAT/safety channel. An industrial contactless Ethernet guide is another option, as discussed in the original report.

For passing rails, a continuous bus on each lane works but adds wear and controller packaging to a problem the present chains already solve. For a transfer shuttle, interlock rail locks and use manufacturer-compatible pickup guides, independently protected transfer-deck power, backfeed blocking and an energy reserve across its measured dead section. Never drag a live shoe through an open track joint or bridge unlike supplies. Parallel structural rails retain their original passing clearances; added bus/box/dust-guard geometry must be rebuilt and rerun with the same10 mm/5 mm gap rules. There is no new faucet/outlet/cabinet-door exemption.

### C — dock-and-charge buffer carriage

C can cross dead switches without a running collector. Use industrial DC mating contacts and a mains-fed charger at stops; do not automate plugging a household230 V twist adapter. Comparison includes a supercap and a battery because the addendum asks for both; the battery remains outside the adopted no-battery architecture.

Keep the onboard controller energized while traveling, rather than assuming the arm is an unpowered dead load. A20 s travel/hold window is an engineering scenario, longer than the9.5 s empty1.9 m traverse at0.2 m/s; it is not a measured washing-cycle duration. Using the UR steady provision1045 W,90% conversion,1.5 energy margin and80% end-of-life capacitance:

```text
E_required = 1045 W × 20 s × 1.5 / 0.90 = 34,833 J = 9.68 Wh
C_initial ≥ 2E / [(47.5² − 36²) × 0.80] = 90.69 F
Select at least 100 F initial guaranteed capacitance; measure real duty before shrinking.
```

47.5 V charging target gives headroom below a48.6 V rated example; charger tolerance, transients and protective cutoff must remain within the module rating.36 V is the assumed cutoff for this buffer scenario, within the cited OEM controller input ranges. At36 V the provision demands32.25 A. For xArm's862 W provision, the same calculation needs74.81 F. A tiny capacitor sized for contact bounce cannot be presented as a20 s autonomous buffer.

Real buyable reference: EatonXLR-48R6167-R has166 F,48.6 V rating,5 mΩ maximum initial ESR,86 A continuous at15°C rise, and80% end-of-life capacitance/200% ESR. Size using the larger datasheet14.7 kg mass and approximately419.5×194.5×177 mm envelope; the SKU's14.197 kg differs. It provides17.71 Wh from47.5→36 V at end of life, before conversion/stop reserve; end-of-life ESR gives about0.323 V drop at32.25 A. This is a credible energy/current example but a poor fit for the small-carriage goal. Controller+module alone add19 kg, and require new mass/inertia, moment, braking, stiffness and collision checks. Neither arm gravity brakes nor rail brakes may be bypassed because a buffer remains charged. POWER_CAP.

Price:11,163.85 CNY per module on DigiKey China, including13% VAT. The dock supply must support operating load **plus recharge**: reserve2.5 kW output per lane, use a3 kW supply example, not the1.536 kW B supply. At42 V,2.5 kW is59.52 A. A nominal80 A contact class needs wire/bundling/temperature derating. With1 kW net recharge, refilling the actual un-margined20 s energy use takes at least23.22 s ideally; regulation, balancing, conversion and taper increase that. Long washing/cutting holds require powered **task-station** docks, not just chargers at rail ends. POWER_CAPPRICE.

CombiTac direqt's4 mm family offers an80 A class reference; its/10 power contacts are catalogued81 A with10 mm² conductors, with derating conditions. Bare fronts areIP2X, which is touch protection, not water protection. Its catalogue gives9.5 N average sliding force per contact and plugging force1.5×sliding. Two power contacts therefore imply28.5 N reference insertion; adding a separate1.5 engineering margin gives42.75 N. With an additional same-class PE contact the provision becomes64.125 N. **These are not complete-dock peak-force ratings**: guide/seal, interlock and data-module forces and contaminated/end-of-life insertion still need sourced values or measurement. Have the carriage docking actuator bear the force, not the food-handling arm. POWER_DOCKFORCE.

The direqt family is rated up to10,000 mating cycles; uniq offers up to100,000 under its matched conditions. Do not transfer direqt force/current ratings to an unspecified uniq assembly. As an illustrative duty of20 connections/day,10,000 cycles is about500 operating days versus5000 days for100,000, before environmental derating; these are arithmetic comparisons, not promised service lives. Matched housing ratingsIP65/67 etc apply to specified closed assemblies, not any bare automatic dock while open. Supply a tested cover/drip guard for the open state and food-debris isolation. POWER_DOCKLIFE.

Mate/unmate atzero current; the manufacturer explicitly rejects mating under load. Use a keyed alignment/lock, last-mate-first-break verification, contactor/precharge and blocking of buffer backfeed, with protective earth first/last if required by the Class I design. Verify latched contacts before transferring load; isolate the buffer during maintenance and prevent automatic cutter/arm restart. DC-side short-circuit protection belongs close to **both** energy sources, along with balance/overvoltage/thermal monitoring. Commanded safety stops still require validated SS1/STO and spring brakes, even if electronics stay powered. Regenerative braking energy cannot be pushed into a fully charged supercap or nonsinking source without a qualified absorption path. POWER_DOCKMATE.

The battery comparison illustrates the power constraint:9.68 Wh usable energy is small, but32.25 A at36 V is not. A conceptual13-series high-rate P28A-type cell basis is46.8 V nominal/54.6 V full, about131 Wh and0.598 kg cells only;35 A is the published **cell maximum**, not certified pack continuous capability. It needs a qualified pack/BMS/charger/enclosure and thermal/current proof. This is not a pack build instruction or selected product. LYBATT's public960 Wh,25 A continuous/30 A peak,37.5–54.75 V,445×97×212 mm/IP64 pack has ample energy but the UR provision needs30.96 A at37.5 V, above both ratings. Its public matched price is unavailable. Smaller certified high-rate pack allowance800–2000 CNY is a planning estimate, not a merchant quote. POWER_BATTERY.

C data uses local execution/WLAN during transit, with an optional matched Ethernet docking module at rest and a separately validated safety link. Avoid making reacquisition of WLAN or Ethernet the sole stopping mechanism. Proposed transport-only subphases areD00 controlled energization/precharge;D01 zero-current undock;D02 energy-bounded transit;D03 dock/latch verification;D04 zero-current connection/precharge/power transfer. They supplement allP01–P16 finished-product requirements. They are not accepted task phases until docking forces/geometry and the unchanged checker pass; no new contacts/ACM exceptions were authorized. C permits mechanical stops anywhere for limited energized time; it does **not** provide indefinite powered work anywhere. Supercaps avoid sliding debris but add docking clicks, cooling and duty delays; no dBA measurements were found.

### China cost comparison and integration decision

All installed numbers below are **gross power-package engineering budgets**, separate from the original39 transport quotes/allowances. They exclude the OEM arm/controller price or retrofit, additional guide/frame redesign, building-circuit reconstruction and certified-cell NRE. The99,000 CNY baseline already contains a lumped chain/electrical allowance, so B/C cannot simply be added as a net delta without subtracting a now-unitemized overlap. Four-carriage prices remain comparison budgets; they do not make four lanes fit this kitchen.

POWER_COST_TABLE

A's fixed2500 CNY allowance covers short compatible dry modules, wiring/protection and installation; the indicative range is2000–3500. B uses8000 fixed+12,000 per lane/carriage, with4000 per protected2.4 m conductor/collector/debris-guard assembly as an **allowance**,2793 public-price PSU, and remaining branch/current-control/data/enclosure integration allowances. A matched China OEM48 V kit quote was not public, so no fabricated VAHLE/Conductix price is given. RSP-1500 China listings are1868.80 (tax basis unspecified) and2793 CNY (tax-inclusive); use the latter. POWER_SUPPLYPRICE.

C-supercap uses12,000 fixed+32,000/carriage, including the11,163.85 module, a3 kW charger/source anchored at4792.19 CNY, four task docks/lane at1500 CNY each as an allowance, and remaining power/enclosure/interface integration. C-battery uses12,000 fixed+14,000/carriage, with the unverified800–2000 pack allowance and chemistry-specific charging/interface provisions; exact matching pack price is unknown. No China price was found for the selected full80 A automatic connector set:1500/dock is an engineering allowance. These budgets are useful comparisons, not claims of complete buyable certified kits. POWER_DOCKSUPPLYPRICE.

**Adopt static household track for fixtures; retain cable chains for arms.** B is the preferred power topology if genuine free lane shuttling later becomes a requirement. Public OEM DC controllers make it credible, but startup current, enclosure heat/geometry, contact wear, SELV/PELV proof and safe data still cost engineering work. C's task-station docks and energy scheduling make it less attractive than B for indefinite washing/cutting. A household track never earns moving-arm approval by being cheaper.

Updated machine-readable evidence is in[transport_options.json](../../sim/r02/transport/results/transport_options.json) under`power_options`, with a standalone[power record](../../sim/r02/transport/results/power_options.json),[28 power sources](../../sim/r02/transport/results/power_sources.json), and[12 power budget rows](../../sim/r02/transport/results/power_costs.csv). Main rail coordinates/clearance witnesses, process-force references and39 transport-cost rows are preserved. Additional power hardware has **no claimed collision-screen PASS**. Reproduce by running`power_addendum.py` through`bounded.py` with a120 s timeout; the base generators preserve/reappend this record when present. No new robot contacts, pose tolerances or grip semantics were introduced.
'''
# Normalize engineering-number typography while preserving model identifiers,
# local link targets and literal code/paths.
def typography(text):
    protected = re.split(r'(```[\s\S]*?```|`[^`]*`|\]\([^)]*\))', text)
    model_prefixes = {'UR', 'xArm', 'DC', 'GQ', 'GN', 'IP', 'IEC', 'RSP', 'P', 'D', 'R', 'XLR'}
    for i in range(0, len(protected), 2):
        z = protected[i]
        z = re.sub(r"(?<![\w./])([A-Za-z]+(?:['’]s)?)(?=\d)",
                   lambda m: m.group(1) + ('' if m.group(1) in model_prefixes else ' '), z)
        z = z.replace('UF ACTORY', 'UFACTORY').replace('EatonXLR', 'Eaton XLR')
        z = z.replace('RSP3000', 'RSP-3000').replace('RSP-1500 China', 'RSP-1500 China')
        z = z.replace('Category1/', 'Category 1 /').replace('D00 ', 'D00 ').replace('0.90 =34', '0.90 = 34')
        z = re.sub(r'(?<=[,;:])(?=\d)', ' ', z)
        z = re.sub(r'(?<=[A-Za-z])\.(?=\d)', '. ', z)
        # Thousands separators are numeric punctuation, not prose commas.
        z = re.sub(r'(?<=\d), (?=\d{3}\b)', ',', z)
        z = z.replace('=2200', '= 2200').replace('=1045', '= 1045')
        z = z.replace('a≤', 'a ≤').replace('supports24', 'supports 24')
        protected[i] = z
    return ''.join(protected)

TEXT = typography(TEXT)
REPLACEMENTS = {
    'POWER_UR': ['P08', 'P09'], 'POWER_XA': ['P05', 'P06', 'P07'],
    'POWER_PSU': ['P14'], 'POWER_URDC': ['P09'], 'POWER_BRANDS': ['P01', 'P04'],
    'POWER_BULLPRICE': ['P02'], 'POWER_CONSUMER': ['P03'],
    'POWER_COLLECTOR': ['P12'], 'POWER_CONDUCTOR': ['P11', 'P13'],
    'POWER_WET': ['P21'], 'POWER_PSUFAULT': ['P14'], 'POWER_RCD': ['P19', 'P20'],
    'POWER_CAP': ['P22', 'P23'], 'POWER_CAPPRICE': ['P24'],
    'POWER_DOCKFORCE': ['P25'], 'POWER_DOCKLIFE': ['P26'], 'POWER_DOCKMATE': ['P25'],
    'POWER_BATTERY': ['P27', 'P28'], 'POWER_SUPPLYPRICE': ['P15', 'P16'],
    'POWER_DOCKSUPPLYPRICE': ['P18'],
}
for token in sorted(REPLACEMENTS, key=len, reverse=True):
    TEXT = TEXT.replace(token, cite(*REPLACEMENTS[token]))
table = ['| Power option |2 carriages |3 carriages |4 carriages |3-carriage range CNY |Meaning |',
         '|---|---:|---:|---:|---:|---|']
notes = {'A_stationary_household_track': 'Static fixture package; independent of arm count',
         'B_48v_sliding_conductor': '48 V industrial pickup; controller purchase not included',
         'C_supercap_docks': 'Four docks per lane; heavy commercial capacitor example',
         'C_battery_docks': 'Comparison only; original no-battery architecture retained'}
for k, b in BUDGETS.items():
    c = b['packages_cny']['3']
    low = round(c * b['range_multiplier'][0]); high = round(c * b['range_multiplier'][1])
    table.append('|`' + k + '`|' + '|'.join(f"{b['packages_cny'][str(n)]:,}" for n in (2, 3, 4)) +
                 f'|{low:,}–{high:,}|' + notes[k] + '|')
TEXT = TEXT.replace('POWER_COST_TABLE', '\n'.join(table))
(R / 'power_addendum.md').write_text(TEXT.strip() + '\n', encoding='utf-8')
base = POST.read_text(encoding='utf-8').split('\n## Power track addendum')[0].rstrip()
POST.write_text(base + '\n\n' + TEXT.strip() + '\n', encoding='utf-8')
print(json.dumps(dict(embedded_power_options=len(POWER['options']), sources=len(S),
                      power_budget_rows=len(COST_ROWS), min_buffer_F=round(CAP, 3),
                      selected_buffer_F=100, worst48A=bus_current(UR_DESIGN_W, 48),
                      arm_recommendation=POWER['recommendation']['arm_power'],
                      appliance_recommendation=POWER['recommendation']['appliance_power']), indent=2))
