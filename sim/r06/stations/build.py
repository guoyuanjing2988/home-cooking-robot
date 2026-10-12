"""R06 station research artifacts. No IK, dynamics, path search or food qualification.
Run through bounded_run.py; all outputs are confined to this role directory.
"""
from __future__ import annotations
import csv, hashlib, json, math, copy, time
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RESULTS = HERE / 'results'
DATE = '2026-10-08'

def dump(name, value):
    (RESULTS / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')

SOURCES = {
 'fotile': ('https://www.fotile.com/product/4444.html', 'OEM China product page', 'Q5AL dimensions, electrical rating and basin volume; no measured basal-crease cleaning'),
 'midea_catalog': ('https://detail.zol.com.cn/fruitwasher/midea/pic.html', 'secondary China price catalog', 'Price observation only; technical fields unverified against OEM; not selected'),
 'wash_line': ('https://www.21food.cn/productshow/4216261.html', 'China manufacturer advertisement', 'QX4000 dimensions and power; advertised CNY46800 refers to larger QX6m, not the QX4000'),
 'tp350': ('https://www.21food.cn/productshow/1575484.html', 'China manufacturer advertisement updated 2024-03-26', 'Matched TP350 CNY1500, dimensions, load and approximately two-minute cycle; advertisement not quotation'),
 'mg800': ('https://wap.21food.cn/product/detail7416565.html', 'China manufacturer advertisement', 'MG800 dimensions and power; no matched MG800 price'),
 'brush_price': ('https://price.21food.cn/quote/1790041.html', 'China manufacturer advertisement dated 2026-08-20', 'MQT family CNY8800-15000; not a matched MG800 quote'),
 'hento': ('https://hentomachine.cn/product/Carrot-Peeling-Machine.html', 'China OEM product advertisement', 'HT-HLQP01 dimensions, power, throughput and broad CNY9000-42000 range'),
 'rotato': ('https://www.starfrit.com/en/starfrit-electric-rotato-express-0932110060red', 'OEM product page, red SKU', 'Six-volt adaptor, advertised ten seconds, automatic stop and non-immersible body; no peel-depth data'),
 'rotato_manual': ('https://www.starfrit.com/media/pdf/instrbooklet--User-manual-093209002BLCK-en2.pdf', 'OEM manual, older black SKU', 'Four AA or six-volt adaptor; maximum 140mm food length without halving; end/eye finishing; SKU difference retained'),
 'rotato_dims': ('https://www.rakuten.com.tw/shop/tw1111/product/7uga4d67o/', 'seller listing, Taiwan, older black SKU', '165x160mm footprint; third dimension absent; no mainland-CNY quote; reserve 310mm height as assumption'),
 'rotato_price': ('https://cn.ebay.com/b/Starfrit-Peelers-Slicers/20641/bn_99094882', 'cross-border marketplace CNY display', 'CNY128.60 plus CNY361.42 shipping; not China domestic retail or guaranteed matched SKU'),
 'sammic': ('https://www.sammic.com.au/wp-content/uploads/2023/SPECSHEET/M-5.pdf', 'OEM datasheet', 'M5 333x367x490mm, 300W, 5kg, 0-6min, 80-100kg/h; minimum load not established'),
 'oxo': ('https://www.oxo.com/shop/kitchenware/utensils/y-peeler.html', 'OEM product page', '21081 152.4x76.2x25.4mm, dishwasher safe, built-in eyer; depth and force not specified'),
 'huller': ('https://triangle-tools.de/en/Tomato-and-fruit-huller-Professional/10-004-25-00', 'OEM product page', '145x20x13mm, 34g, dishwasher safe; huller diameter/depth unknown'),
 'cl20': ('https://www.robot-coupe.com/france/fr/p/coupe-legumes-cl-20/18232', 'OEM product page, current French SKU', '325x310x570mm, 400W, 11kg, 104cm2 large hopper, 58mm tube and 18289 five-mm disc'),
 'cl20_manual': ('https://www.caterkwik.co.uk/shop/downloads/CL20_Robotcoupe-CL20-Manual.pdf', 'OEM 2009 D-version manual hosted by dealer', 'Magnetic lid stop, motor braking, green-button restart and unplug before cleaning; exact generation unresolved'),
 'r211': ('https://www.robot-coupe.com/australia/en_AU/p/food-processors-r-211-xl/18401', 'OEM product page', 'R211XL continuous discharge, 550W, 58mm and 87cm2 inlets; historical R04 envelope retained separately'),
 'rc_catalog': ('https://www.robot-coupe.com/robot-coupe-global/Page%20Documentation/Catalogues/Export/Robot-Coupe_2024_Catalogue_Export_Interactive.pdf', 'OEM catalog 2024', 'Discs and regional dimensions; generations must not be mixed'),
 'cl50': ('https://www.robot-coupe.com/cn/zh/p/vegetable-preparation-machines-cl-50/20672', 'OEM China product page', 'Current 380x305x595mm, 550W, 18kg, five-mm disc, 2.2L hopper and 58mm tube'),
 'cl50_price': ('https://www.21food.cn/productshow/3244917.html', 'historical China seller listing in R02, not freshly retrievable', 'CNY10500 base, different 350x320x590mm/25kg generation; do not transfer price as a current matched quotation'),
 'blaupunkt': ('https://www.blaupunkt.com/zh-cn/product/bp-qc02%E7%94%B5%E5%8A%A8%E5%88%87%E8%8F%9C%E6%9C%BA', 'OEM China product page', '179x287x148mm, 60W, 1.5kg, 70x90mm inlet, 110mm outlet, one-minute duty/five-minute rest'),
 'blaupunkt_price': ('https://www.smzdm.com/p/118488221/', 'historical 2024-07-07 secondary China promotion retained in R02', 'CNY399 before coupon; current availability/price unverified'),
 'breville': ('https://www.breville.com/en-au/product/bfp610', 'OEM Australian product page', '120mm feed chute and adjustable slicing; no China matched price'),
 'breville_manual': ('https://assets.breville.com/BFP610/BFP610_ANZ_WEB_IB_A23_LR.pdf', 'OEM manual', 'Bowl/lid/pusher interlocks, stop and unplug, disc removal for unloading, unattended-use restriction'),
 'yqc': ('https://www.topfoodmachinery.com/product/fruit-and-vegetable-processing-equipment/multi-function-cutting-machine/multifunctional-vegetable-cutter/', 'China OEM product page', 'Jiaruichang YQC660 930x440x785mm, 750W, 217mm belt, 1-30mm; cannot give nominal 40mm'),
 'yqc_price': ('https://www.lnvcm.edu.cn/__local/D/C1/78/13B20A737D75B8D91CB3D076BEE_3E413E03_E75D4C.pdf?e=.pdf', 'China institutional procurement detail', 'CNY5950 for different Meiying YQC660/1.87kW; comparator not matched OEM machine'),
 'nemco': ('https://nemco.com/wp-content/uploads/2025/06/c9bb50b8-9645-4786-b5ff-fd07fe8a7881.pdf', 'OEM sell sheet', '55550-8 203.2x203.2x482.6mm, 2.04kg; 428-8 blade; tomato use; 8C apple corer is unsuitable'),
 'nemco_parts': ('https://nemco.com/catalog/easy-wedger/', 'OEM product page', 'Eight-section blade/pusher family; fitting dimensions and forces not published'),
 'ikea_spinner': ('https://www.ikea.cn/cn/zh/p/uppfylld-wu-pu-fei-er-de-sha-la-shuai-gan-ji-bai-se-40521951/', 'OEM China retail page', 'CNY19.99, diameter230 height165mm, PP, hand wash; local stock page shows unavailable'),
 'oxo_spinner': ('https://www.oxouk.com/products/salad-spinner/', 'OEM UK product page', '1351580 pump and brake; conservative 266x266x152mm envelope inherited cook_ref; no pump-force rating'),
 'hendi_spinner': ('https://www.hendi.eu/en/salad-spinner-4548.html', 'OEM product page', '222553 diameter335 height430mm, 12L, 2.26kg, removable basket, drain; food-contact declaration link'),
 'gn': ('https://www.hendi.eu/de/gastronorm-behlter-14-4046.html', 'OEM product page', '801628 GN1/4 265x162x100mm, 2.8L, 0.46kg, 0.7mm 18/8 stainless, stackable'),
 'gn_drain': ('https://www.hendi.eu/ro/tava-gastronorm-perforata-4071.html', 'OEM product page', '806593 perforated GN1/4 265x163mm; one-mm dimensional difference retained'),
 'ur5': ('https://www.universal-robots.com/manuals/EN/PDF/SW5_25_1/user-manual-UR5e-PDF_online/710-965-00_UR5e_User_Manual_en_Global.pdf', 'OEM manual', 'UR5e 5kg/850mm/20.7kg, mounting and power-loss holding; use correct payload CoM and gravity orientation'),
 'xarm': ('https://docs.xarm.ufactory.cc/8.technical_specifications.html', 'OEM technical data', 'xArm6 5kg/700mm/12.5kg; 3kg external payload plus EOAT needs actual CoM curve'),
 'xarm_model': ('https://github.com/xArm-Developer/xarm_ros2', 'OEM public model repository', 'Model/inertia revision must match purchased hardware'),
 'xarm_brake': ('https://docs.xarm.ufactory.cc/1.safety.html', 'OEM safety documentation', 'Power-loss pose holding with possible slight movement; home brake basis'),
 'cut_paper': ('https://iseki-food-ejournal.com/article/69/pdf', 'primary paper Singh Das Das 2016', 'Root cutting averages at 20-40mm/min; not a powered-slicer feed-load bound'),
 'peel_paper': ('https://www.qikan.com.cn/article/5dd020251220.html', 'primary journal abstract via indexed publisher, inherited R02', 'Carrot peel resistance 1.68N/mm; full paper inaccessible; potato transfer a proxy'),
 'pom': ('https://www.ensingerplastics.com/en-us/shapes/acetal-tecaform-ah-natural', 'material manufacturer', 'Grade-specific food-contact POM; require compliance document for actual stock'),
 'local': ('../../../../DECISIONS.md', 'binding local decisions', '2026-10-08 workstation, rated envelope, brakes, intended contacts and planning budgets')
}

def survey_row(id, step, device, dims, power, capacity, cycle, opening, controls, relay, cleaning, quality, gaps, price=None, price_kind='ND; China matched price unavailable', allowance=None, sources=(), status='survey_only'):
    return dict(id=id, step=step, device=device, dimensions_mm=dims, dimension_basis='OEM unless explicitly marked otherwise', loading_geometry=opening, power_W=power, capacity=capacity, cycle_time=cycle, controls_and_robot_operation=controls, relay_or_smart_plug=relay, cleanability=cleaning, spec_fit=quality, weak_evidence=gaps, china_price_cny=price, china_price_basis=price_kind, china_planning_allowance_cny=allowance, source_ids=';'.join(sources), urls=' | '.join(SOURCES[s][0] for s in sources), checked_date=DATE, disposition=status)

SURVEY = [
 survey_row('W01','wash','FOTILE JBSD2F-Q5AL','895x490x610',1850,'31L sink; five place settings','Produce cycle duration ND','Top lid; 855x460 worktop cutout; own fruit basket, opening profile ND','Electronic program/start; lid and basket handling; mains water/drain','Isolation only; mains restoration not documented to start produce program','Accessible basket/filter; dishwasher program is not the produce program','Physical wash option; no complete leaf-crease proof','Too wide for three stations; cycle/China matched price ND',allowance=10000,sources=('fotile',),status='reject_recommended_footprint'),
 survey_row('W02','wash','Midea FY08PB-B(RZ), catalog lead','420x350x320 [secondary, unverified]',60,'8L [unverified]','ND','Top lid and internal basket dimensions ND','Catalog says membrane timer and auto drain; OEM manual missing','Unknown; no automatic restart credit','Basket removal/drain unverified','Do not rely on purification claim for soil removal','Technical fields are research leads only; current OEM SKU/stock missing',728,'2026-08-30 ZOL catalog observation, not OEM quotation',sources=('midea_catalog',),status='lead_only'),
 survey_row('W03','wash','Huikang QX4000 bubble/spray line','4130x1010x1550',3500,'1000-1500kg/h','Continuous','Open conveyor; commercial pump/spray/brush','Switches, conveyor; add guard on drives','Industrial starter unknown; no smart-plug adaptation','304 claim; screens and conveyors need access','Washes soil; still requires exposed leaf bases','Far outside module; CNY46800 is larger QX6m advertisement',sources=('wash_line',),status='reject_size_and_power'),
 survey_row('W04','wash / basket rinse','Custom GN basket rinse cradle in own basin','360x320x220 [design]',120,'One reference carrier; 6L working water; 40mm freeboard','60s coarse/root rinse; 30s final; inspection extends','336x296 clear mouth; 285x223 carrier incl key; top entry','24V valves, 24V lift cradle, soft brush; level/overflow/drain feedback','Yes, isolated OEM-rated pump plus low-voltage valves; no blind restart','Lift-out screen and smooth basin; no peel into drain','Fresh-water lift-out, basal rub and visual inspection retained','Designed plumbing and brush coverage, not a sold complete washer',allowance=3500,sources=('gn','local'),status='selected_A_and_B'),
 survey_row('P01','abrasive peel','Aoge/Huiyou TP350','780x510x1000',1100,'Recommended batch5-8kg;240kg/h','About2min advertised','350mm rotating plate; top lid/chute mouth actual size ND','Clipped lid, water valve, start, discharge door; powered discharge','Starter circuit needs inspection; no relay-autostart assumption','Remove plate/cover and flush; IPX1','Peels potatoes; no 0.2-0.8mm depth/eyes or one-potato performance','Oversize and batch mismatch; stated380V0.75kW and220V1.1kW variants',1500,'Matched China manufacturer ad updated2024-03-26; not a current quote',sources=('tp350',),status='reject_size_minimum_batch'),
 survey_row('P02','roller wash / peel','Jiapin MG800','1500x850x900','1200-1500','200-500kg/h','ND','Nine diameter120x800mm rollers; loading mouth ND','Switch/start/discharge; add guarded cover','Unknown; machine schematic needed','Nylon rollers removable in principle; method ND','Root wash/peel claimed; quantitative losses absent','Depth exceeds module alone; MQT price8800-15000 is unmatched family',allowance=15000,sources=('mg800','brush_price'),status='reject_size'),
 survey_row('P03','carrot peel','Hento HT-HLQP01','1980x450x1050',500,'100kg/h','Continuous; individual cycle ND','Industrial long roller/feed geometry ND','220V; local switches; robot loader adaptation ND','Unknown','Stainless claim; dismantling instructions ND','Carrot-specific peeling, no depth/yield distribution','Much too wide; broad advertised price range only','9000-42000','China OEM advertised range, SKU configuration unresolved',sources=('hento',),status='reject_size'),
 survey_row('P04','household electric peel','Starfrit Rotato Express','165x160x310 [footprint seller; height reserve assumption]','ND;6V OEM;3W older-adapter allowance unverified','One symmetric firm item, <=140mm food length','10s OEM claim plus loading/end/eye finishing','Bottom spike/top pin, cutter-arm height lever; no lid','Push red start while stabilizing top pin; unload by rocking; guard retrofit','6V DC controlled power can isolate; pressing start still needed; no smart-plug start credit','Remove blade head; body wipe only; do not immerse','Potato plausible; whole160mm carrot conflicts140mm food limit','No OEM overall 3-axis dimensions or matched red-SKU wattage; no peel depth, tapered-carrot or restart guarantee',128.60,'Cross-border CNY display plus361.42 shipping; not mainland retail; SKU unresolved',600,('rotato','rotato_manual','rotato_dims','rotato_price'),status='B_candidate_with_carrot_halving_and_touchup'),
 survey_row('P05','small-commercial abrasive peel','Sammic M-5','333x367x490',300,'5kg/cycle;80-100kg/h','0-6min timer','Top lid, lateral discharge; aperture profile ND','On/off buttons and timer; own water inlet with air break','Isolation only until exact starter behavior known','Stainless body; abrasive plate; removable filter/stand','OEM includes carrots; no depth/uniformity or eyes proof','Minimum0.12/0.2kg load behavior and China price unknown',allowance=16000,sources=('sammic',),status='reject_recommended_small_batch_uncertainty'),
 survey_row('P06','peel / potato eyes','OXO Good Grips21081 Y-peeler','152.4x76.2x25.4',0,'One root','Manual/operator dependent','Swivel blade and built-in eyer; no appliance lid','Clamp purchased peeler in compliant fixed stage; root stays in keyed cradle','Passive blade; drive belongs to custom cell','Dishwasher-safe; removable food-contact mount','Actual peel blade and eyer; depth stop must be engineered','Peel depth/eyering force ND; Chinese matched SKU price ND',allowance=180,sources=('oxo',),status='selected_A_blade_and_eye_tool'),
 survey_row('P07','peel / inspect / finish','Custom supported root rotary cradle with purchased swivel blade','450x350x520 [shared cell]',120,'One carrot or potato;35-80mm diameter;180mm length','120s carrot;180s potato inc three eyes [estimate]','Cartridge retains food on rollers; end trimming releases spindle/contact scars','Motor indexes; depth skid0.5mm nominal; cell-driven eyer; guarded end cutter','24V drive enable and encoder; brake/catch, no automatic resume','Food roller and peeler modules lift out; motor outside food tray','Inspect every surface/eyes and rework; 0.2-0.8mm still unqualified','Irregular/tapered roots and peel scars are highest risks',allowance=9000,sources=('oxo','peel_paper','local'),status='selected_A_shared_cell'),
 survey_row('E01','tomato core','triangle huller10 00425 00','145x20x13',0,'One core','ND','Hand scoop/huller; working tip dimensions ND','Fixed keyed tool in depth-limited cell stage; tomato supported','Passive, custom drive if automated','Dishwasher safe;34g','Removes stem tissue; avoid full seed cavity scoop','Tip force/depth and China price ND',allowance=250,sources=('huller',),status='selected_A_tool_candidate'),
 survey_row('E02','eyes / core inspection','Custom camera plus rotary nest and depth-limited eyer/huller','Uses shared450x350cell',30,'Every visible eye;reference three eyes','20-30s/eye [estimate]','Supported root/tomato; end-stop and guarded tool; reject green/sprouted/rotten','Cell actuates; arm detached; motor tracks each index/tool stroke','DC controls, sensor-gated enable','Removable scoop, silicone lands and accessible waste tray','Must expose and inspect all surfaces; count is not a maximum','Visual classification/core depth still unqualified',allowance=0,sources=('oxo','huller','local'),status='included_shared_cell_not_additive'),
 survey_row('S01','5mm root slice','Robot-Coupe CL20 +18289disc','325x310x570',400,'OEM50kg/h [France];UK40kg/h operating /2kg/min processing','Reference roots <1min nominal; adaptation not measured','104cm2 half-moon, diameter58mm tube; large profile ND','OEM lid/motor brake; green-button start; original pusher retained in actuator cradle','Isolation only; closing lid requires green-button on documented D version','Detach lid/bowl/disc; unplug before cleaning','Real nominal5mm disc; no within-slice<=1mm or final-stub guarantee','65x70 potato cannot use58mm tube; area is not a verified mouth shape',allowance=16000,sources=('cl20','cl20_manual'),status='B_candidate_conditioned_on_hopper_geometry'),
 survey_row('S02','5mm root slice','Robot-Coupe R211XL +5mm disc','245x385x510 [R04 regional envelope; current generation must match]',550,'Continuous slicer;2.9L cutter bowl','Nominal throughput not a complete cycle','87cm2 half-moon;58mm tube; 18289disc on selected regional generation','Lid/pusher/buttons, supplied pusher only','Isolation only; starter/revision unresolved','Detach accessories; motor not immersed','Nominal five-mm slices, not final-yield proof','Smaller chute; exact current drawing missing',allowance=15000,sources=('r211','rc_catalog'),status='survey_alternative'),
 survey_row('S03','slice / dice','Robot-Coupe CL50 China +5mm disc','380x305x595',550,'150kg/h nominal','ND','2.2L half-moon;58mm tube; optional39mm pusher','Lid and pusher; auto restart feature advertised; keep interlock','Mains enable alone not safe start; monitored cut enable and restart inhibit needed','Metal lid/bowl; detach discs; dry motor','5mm slicing available; dice cannot replace slices','Current OEM18kg vs historical seller25kg generation',10500,'R02 historical seller base price, unavailable fresh; discs extra; unmatched current SKU',18000,('cl50','cl50_price'),status='survey_alternative'),
 survey_row('S04','electric household slice/dice','Blaupunkt BP-QC02','179x287x148',60,'One-minute continuous maximum;>=5min rest','1min on /5min off','70x90mm feed;110mm outlet; five blade groups','One start/stop; pusher/guard geometry from exact manual needed','Restart memory ND; smart plug isolation only','Detach wet parts; motor stays dry','No specified flat5mm thickness; wave/strip/pulp modes not baseline','Cannot credit5mm or section/wedge quality',399,'R02 retained2024-07-07 China promotion, not current stock/price',500,('blaupunkt','blaupunkt_price'),status='reject_cut_spec'),
 survey_row('S05','household adjustable slicing','Breville BFP610','395x240x290 [largest395 axis reserved; ordering uncertain]',1000,'2.5L batch bowl;120mm feed','ND; unloading requires disc removal','120mm feed, lid, large pusher, batch bowl','Multiple bowl/lid/pusher interlocks; stop/unplug and remove disc before unload','Isolation only; OEM unattended restriction conflicts automation without qualified adaptation','Detachable bowl/disc; prescribed disassembly each batch','Nominal5mm setting; no tolerance or recovery data','No China matched quote; requires many bowl/lid/disc handoffs',allowance=4500,sources=('breville','breville_manual'),status='reject_recommended_robot_unloading'),
 survey_row('S06','5mm slice / terminal recovery','Custom guarded indexed guillotine with follower','450x350x520 [shared cell]',200,'One root in removable cassette','~45s carrot /30s potato [estimate at qualified future rate]','330x260mm loading portal; feed slot100x90; full-profile food guides','Own encoder5mm feed; final10mm stub then two5mm cuts; blade park catch','DC control; loadcell abort; motor brake and mechanical park catch','Tool lifts out for cleaning; no blind bearing in food path','Feed4-6mm; last interval redistributed to avoid edible<3mm waste','Faster-than-paper cutting rate unqualified; internal drive sized>=1000N',allowance=8000,sources=('cut_paper','local'),status='selected_A_shared_drive'),
 survey_row('B01','bok choy section comparator','Jiaruichang YQC660 belt cutter','930x440x785',750,'150-660kg/h;217mm belt','Continuous','Belt feed, knife enclosure, outlet; root and stalk arrangements manual','Start/length adjustment; interlock details ND','Unknown; cannot use smart plug to defeat guard','Belt/blade removal method must be checked','1-30mm advertised; nominal40mm unavailable; basal cleaning/splitting absent','CNY5950 procurement is different1.87kW Meiying generation',5950,'China institutional comparator for different MeiyingYQC660; not matched price',sources=('yqc','yqc_price'),status='reject_length_and_footprint'),
 survey_row('B02','bok root trim / split /40mm','Custom low-bundle guide +split blade +shared guillotine','Cassette285x223x125 [design]',200,'Six reference stalks, two wide;bundle<=30mm','~90s splitting/sectioning plus individual crease work [estimate]','Root disk5-10mm; adjustable strip guide<=15mm; length-balanced30-50mm cuts','Cell actuates; leaf grasp/cup is outside powered blade window','Shared guarded DC drive','Lift-out comb, slotted supports; every fiber inspected','Width<=15; n nearest L/40 within30-50; no ignored terminal leaf remnant','Leaf positioning/fiber release variable; reference counts may grow',allowance=0,sources=('local','cut_paper'),status='selected_A_and_B_shared_cell'),
 survey_row('T01','tomato eight wedges','Nemco55550-8 whole wedger','203.2x203.2x482.6',0,'One tomato','One stroke; time/force ND','Vertical manual pusher, centering rods; blade throat size ND','Robot direct press would react full force; retrofit actuator guard','Passive unit; motor conversion is custom appliance','Simple disassembly; blades extremely sharp','OEM tomato use; eight sectors; 8C apple corer not appropriate','No wedge mass, angle,compression or pulp-retention test;China matched price ND',allowance=2200,sources=('nemco',),status='component_option_not_robot_press'),
 survey_row('T02','guarded tomato wedger','Nemco428-8 blade +matching pusher in fixed guarded press','450x350x520 [shared cell]',200,'One cored70mm tomato','~10s stroke plus core/inspect [estimate]','90mm clear food throat [custom]; support cup transfers continuously to receiving petals','Actuator pushes; arm withdraws; inlet/outlet shutters closed','Shared DC drive with interlock and park catch','Matched removable blade/pusher; tray collects juice','Eight45deg sectors nominal;>=98% retained edible incl pulp','636N structural proxy is not measured cutting force; softer fruit may crush',allowance=1800,sources=('nemco','nemco_parts','local'),status='selected_A_candidate_with_sequential_draw_fallback'),
 survey_row('T03','tomato fallback','Two supported half-cradles and sequential radial draw blade','Same shared cell',200,'One tomato; halves cut then3radial cuts per half','~60-90s [estimate]','Cut-face-supported halves;45/90/135deg planes;40mm draw','Automated indexed cradle; arm detached; low-force controlled draw','Shared DC drive','Removable half-cradles and blade','Preserves seed cavity better in principle; no measured result','Extra mechanism; force/quality trials required; contingency allowance only',allowance=2000,sources=('local',),status='fallback_not_baseline_cost'),
 survey_row('D01','drain / spin','IKEA UPPFYLLD40521951','diameter230x165',0,'OEM usable food capacity ND;7.1L is package volume','Manual,cycle time ND','Removable basket; whole lid and crank','Crank and lid; no powered blade hazard; would need coupler','Passive; no smart plug','PP/rubber, handwash only','Drains/spins; cannot replace wash or basal inspection','China page shows local unavailability;crank force/rpm ND',19.99,'Current OEM China displayed price; stock not guaranteed',sources=('ikea_spinner',),status='reject_recommended_extra_lid_crank'),
 survey_row('D02','drain / pump spin','OXO1351580 spinner','266x266x152 [cook_ref conservative envelope]',0,'Salad basket,actual usable volume ND','ND','Pump lid, lock and brake; basket/bowl','Pump requires hold reaction and lid control; force ND','Passive; custom pump actuator needed','Detach lid/basket; inspect food traps','Optional spinner, gentle drainage sufficient for reference','No China matched price or pump force bound',allowance=400,sources=('oxo_spinner',),status='survey_alternative'),
 survey_row('D03','small-commercial spin','HENDI222553','diameter335x430',0,'12L;2.26kg empty','ND','Removable basket, drain; crank/lid geometry ND','Crank, lid, drain hose; bulky and heavy','Passive; motor adaptation custom','Dishwasher-suitable parts; food-contact document linked','Batch spin available, no no-tear guarantee','Overkill for0.1kg greens;China matched price ND',allowance=1800,sources=('hendi_spinner',),status='reject_recommended_size_payload'),
 survey_row('C01','standard bowl / basket','HENDI801628 GN1/4 +806593 perforated insert','265x162x100 outer;265x163 insert outline',0,'2.8L outer,food<=0.2kg reference','30s drain,measured end criterion','Keyed collar285x223x145 total [custom]; insert lift station-operated','Latch retains pan+insert as one carried assembly; built-in wet-food cup used only for leaves','Passive; washer lift/drain hardware DC','18/8 stainless, stackable;0.46kg outer; grade-specific food-contact POM collar','Separate labeled bowl per ingredient;2mm mesh plus solid outerpan retains pulp and seeds','Perforated SKU depth/mass ND;custom65mm basket;China matched retail ND',allowance=650,sources=('gn','gn_drain','pom'),status='selected_container_system')
]

PRODUCTS = {
 'carrot': dict(input_dimensions_mm=[160,35,35], input_mass_kg=.12, wash='All surfaces and ends clean; no visible soil or peel fragments; fresh final rinse; no soap', peel_depth_mm=[.2,.8], max_gouge_mm=2, ends_trim_mm=[3,5], facet_mm=[2,3], cut='Transverse slices; half-rounds accepted', thickness_mm=[4,6], within_slice_variation_max_mm=1, terminal='Explicit10mm stub, final5mm slice; only<3mm final sliver may join trim', transfer_fraction_min=.98, bowl='output_carrot'),
 'potato': dict(input_dimensions_mm=[90,65,70], input_mass_kg=.20, wash='All surface/eyes clean before peel; remove peel fragments afterward', peel_depth_mm=[.2,.8], max_gouge_mm=2, eyes='Inspect all sides; remove every dark eye; reject green/heavily sprouted/rotten/deep damage', facet_mm=[2,3], cut='5mm transverse slices; longitudinal halves/half-rounds accepted; quarters not assumed acceptable', thickness_mm=[4,6], within_slice_variation_max_mm=1, terminal='Explicit10mm stub and final5mm slice; no unexplained discarded remnant', post_cut='2-3 fresh-water changes until no visible white swirl against dark backing; separated pieces;20-30s drain; no free puddle', transfer_fraction_min=.98, bowl='output_potato', optional_julienne='Deferred; if added each axis2-3mm,length30-80mm,>=90% intact strands'),
 'bok_choy': dict(input_dimensions_mm=[170,100,70], input_mass_kg=.10, coarse_rinse='External/root soil removed before root trim; discard yellow/rotten leaves', root_trim_mm=[5,10], wash='Detach every stalk, expose/rub/inspect every basal crease;600s cold soak; lift leaves before dirty water disposal; fresh rinse until no grit', rubbing_command_N=[2,5], bundle_height_max_mm=30, stalk_width_max_mm=15, section_length_mm=[30,50], nominal_length_mm=40, drain='30s and no continuous drip; no wringing, tearing, uncut fibers or macerated edges', transfer_fraction_min=.98, bowl='output_bok_choy', reference_stalks=6, reference_wide_stalks=2),
 'tomato': dict(input_dimensions_mm=[70,70,60], input_mass_kg=.15, wash='All surface/stem recess clean; cold rinse; retain skin, no blanch', core='Remove hard stem tissue without seed-cavity removal', wedges=8, sector_degrees=[35,55], nominal_sector_degrees=45, relative_piece_mass=[.65,1.35], max_compression_fraction_exclusive=.10, quality='No visible bruise/collapse, all skin cut through; attached pulp/seeds retained', transfer_fraction_min=.98, bowl='output_tomato', hand_scoop_max_g=25)
}

# Physics bounds for arm actions. Machine reactions are separately transmitted to the frame.
FORCES = [
 dict(id='carry', recipient='arm', frame='world', force_N=[0,0,1.89], moment_Nm=[0,0,0], gravity_separate=True, application='carried assembly CoM', derivation='m_max4.2kg x a0.3m/s2 x1.5=1.89N acceleration;reference pan+insert+lid+food<=1.63kg;3kg task plus1.2kg EOAT uses combined4.2kg', margin=1.5, evidence='physics; motion acceleration requirement, not measured'),
 dict(id='load_insert', recipient='arm', frame='world', force_N=[0,-20,0], moment_Nm=[0,0,2], application='carrier key on portal approach', derivation='1.5 x (0.5 x1.63kg x9.81 +1.63kg x0.3 +4N latch)=18.73N;rounded20N;0.1m lever gives2Nm.Lift-and-lower intended route;bound does not permit unintended sliding contacts.', margin=1.5, evidence='physics/design; latch spring2N/mm at2mm compression'),
 dict(id='key_latch', recipient='arm', frame='object', force_N=[0,0,-7.5], moment_Nm=[0,0,0], application='key latch tab', derivation='2N/mm spring x2.5mm x1.5', margin=1.5, evidence='specified custom spring; calibrated force required'),
 dict(id='leaf_brush', recipient='arm', frame='world', force_N=[0,7.5,0], moment_Nm=[.375,0,0], application='leaf cup basal support', derivation='400N/m spring at5-12.5mm gives2-5N command;upper5N x1.5=7.5N;50mm lever0.375Nm;opposite reaction on fixed brush frame', margin=1.5, evidence='R02 spring model extended to entire cook_ref2-5N command band;calibrate actual spring'),
 dict(id='root_brush', recipient='fixture', frame='world', force_N=[0,9,0], moment_Nm=[0,0,0], application='roller-supported root', derivation='1000N/m x0.006m x1.5', margin=1.5, evidence='R02 physics model; detached arm, force closes through cradle'),
 dict(id='tomato_wipe', recipient='fixture', frame='world', force_N=[0,1.5,0], moment_Nm=[0,0,0], application='cup-supported tomato', derivation='200N/m x0.005m x1.5', margin=1.5, evidence='R02 physics model; detached arm'),
 dict(id='jet', recipient='fixture', frame='world', force_N=[0,.382,0], moment_Nm=[0,0,0], application='wash basket', derivation='rho Q2/A=1000*(1e-4m3/s)^2/(pi*(.005m)^2)=.1273N;3x momentum reserve=.382N', margin=3, evidence='physics;6L/min and10mm outlet specified; not a high-pressure jet'),
 dict(id='peel_drag', recipient='fixture', frame='world', force_N=[-63,0,0], moment_Nm=[0,0,0], application='blade/root point in rotary cell', derivation='1.68N/mm x25mm x1.5;potato transfer proxy', margin=1.5, source_ids=['peel_paper'], evidence='indexed primary abstract +R02; not independently measured here'),
 dict(id='eye_core', recipient='fixture', frame='world', force_N=[0,0,52.328], moment_Nm=[0,.52328,0], application='depth-limited eyer/huller working edge', derivation='2 x(67.59N/31mm)x12mm=52.328N;10mm moment arm', margin=2, source_ids=['cut_paper'], evidence='root-cut proxy,not a measured scoop/core force'),
 dict(id='carrot_cut', recipient='fixture', frame='world', force_N=[0,0,-152.623], moment_Nm=[0,0,0], application='cell blade plane', derivation='2 x(67.59/31)x35mm', margin=2, source_ids=['cut_paper'], evidence='slow transverse-cut paper; future speed qualification required'),
 dict(id='potato_cut', recipient='fixture', frame='world', force_N=[0,0,-183.162], moment_Nm=[0,0,0], application='cell blade plane', derivation='2 x(61.49/47)x70mm', margin=2, source_ids=['cut_paper'], evidence='slow transverse-cut paper; not rotating-disc feed load'),
 dict(id='greens_cut', recipient='fixture', frame='world', force_N=[0,0,-348.852], moment_Nm=[0,0,0], application='shared blade plane', derivation='2 x(67.59/31)x80mm total engaged width', margin=2, source_ids=['cut_paper'], evidence='root-tissue proxy,not a validated bok-choy bound'),
 dict(id='wedger', recipient='fixture', frame='world', force_N=[0,0,-636.365], moment_Nm=[0,0,0], application='wedger blade/pusher', derivation='Inherited R02 effective-stress proxy15N/(pi*2mm^2) x280mm x.952mm x2', margin=2, evidence='structural proxy only; actual tomato damage/force unknown; never apply via robot'),
 dict(id='press_capacity', recipient='fixture', frame='world', force_N=[0,0,-1000], moment_Nm=[0,0,0], application='ball screw blade carriage', derivation='Drive and frame design rating1000N >=1.5 x636.365=954.55N; pitch5mm,eta.85 require.936Nm,select>=1.5Nm continuous motor', margin=1.5, evidence='specified capability,not expected process force; braked drive plus mechanical catch'),
 dict(id='B_feed', recipient='fixture', frame='world', force_N=[0,0,-75], moment_Nm=[0,0,0], application='OEM slicer pusher via fixed actuator', derivation='Candidate compliant force limit:10N/mm spring at5mm x1.5 reserve=75N;no OEM feed-force proof', margin=1.5, evidence='design bound,not a demonstrated effective feed load;if required feed exceeds bound B fails')
]

IDENTITY = [1,0,0,0]
def box(id, size, pos=(0,0,0), rgba=(.65,.7,.74,1), quat=IDENTITY):
    return dict(id=id,type='box',size_m=list(size),pose=dict(position_m=list(pos),quaternion_wxyz=list(quat)),rgba=list(rgba))
def cyl(id, radius, height, pos=(0,0,0), rgba=(.65,.7,.74,1), quat=IDENTITY):
    return dict(id=id,type='cylinder',radius_m=radius,height_m=height,pose=dict(position_m=list(pos),quaternion_wxyz=list(quat)),rgba=list(rgba))

BODIES=[]
def body(id, pos, mass, geoms, parent='world', joint=None, category='environment', quat=IDENTITY, evidence='specified custom concept geometry', com=(0,0,0), inertia=None):
    # Explicit conservative inertial budgets are independent of geom volume; no vendor inertia changes.
    if inertia is None:
        inertia=[max(.00005,mass*.01)]*3
    b=dict(id=id,parent=parent,pose=dict(position_m=list(pos),quaternion_wxyz=list(quat)),mass_kg=mass,com_local_m=list(com),inertia_kg_m2=list(inertia),inertia_basis='concept lumped budget,not released CAD' if evidence.startswith('specified') else 'conservative budget',geometry=geoms,category=category,evidence=evidence)
    if joint: b['joint']=joint
    BODIES.append(b)
    return b
def pan_geoms(prefix, length=.265,width=.163,height=.1,thick=.0007,color=(.55,.64,.7,1)):
    # Open vessels: real floors/walls, not solid boxes that fill their usable interior.
    return [box(prefix+'_floor',[length,width,thick],[0,0,thick/2],color),box(prefix+'_left',[thick,width,height],[-length/2+thick/2,0,height/2],color),box(prefix+'_right',[thick,width,height],[length/2-thick/2,0,height/2],color),box(prefix+'_front',[length-2*thick,thick,height],[0,-width/2+thick/2,height/2],color),box(prefix+'_rear',[length-2*thick,thick,height],[0,width/2-thick/2,height/2],color)]

def geometry():
    BODIES.clear()
    legs=[box(f'frame_leg{i}',[.04,.04,.86],[x,y,0]) for i,(x,y) in enumerate([(-.695,-.34),(.695,-.34),(-.695,.34),(.695,.34)])]
    body('frame',[0,.375,.46],40,[box('frame_bottom',[1.41,.71,.04],[0,0,-.40])]+legs+[box('front_beam',[1.43,.04,.05],[0,-.34,.39]),box('rear_beam',[1.43,.04,.05],[0,.34,.39])])
    body('worktop',[0,.375,.91],15,[box('worktop_full',[1.258,.75,.02],[-.096,0,0]),box('worktop_right',[.138,.75,.02],[.656,0,0]),box('worktop_port_front',[.054,.45,.02],[.56,-.15,0]),box('worktop_port_rear',[.054,.14,.02],[.56,.305,0])],evidence='specified worktop tiles preserve1450x750 outline with54x160mm physical waste aperture atworld(.56,.53);not a collision exemption')
    # Washer sits on its own cutout-independent worktop cradle; bottom remains above worktop.
    body('wash_basin',[-.49,.49,.93],5,pan_geoms('basin',.36,.32,.22,.012),evidence='specified360x320x220mm custom basin; clear mouth336x296mm')
    body('wash_lift',[-.49,.49,.946],1,[box('wash_lift_left',[.015,.20,.014],[-.115,0,0]),box('wash_lift_right',[.015,.20,.014],[.115,0,0])],joint=dict(type='slide',axis=[0,0,1],range=[0,.12],initial=0,drive='24V braked lift;holding pawl',brake='de_energize_to_apply'),category='appliance_moving')
    body('wash_brush',[-.49,.49,1.12],.15,[cyl('wash_brush_cylinder',.025,.12,quat=[.7071067812,.7071067812,0,0])],category='appliance_tool')
    body('wash_spout',[-.49,.655,1.26],.25,[box('wash_spout_box',[.09,.025,.025])])
    body('wash_lid',[-.49,.65,1.35],.6,[box('wash_lid_panel',[.36,.32,.008],[0,-.16,0],(.5,.8,.9,.25))],joint=dict(type='hinge',axis=[1,0,0],range=[-1.7,0],initial=-1.7,drive='DC lid actuator',brake='counterbalanced and restrained'),category='appliance_moving')
    body('inspection_dock',[0,.475,.96],1.1,[box('inspection_land',[.295,.235,.025])])
    body('clean_leaf_basket',[0,.475,.974],.55,pan_geoms('clean_leaf',.255,.153,.065,.001)+[box('clean_leaf_key',[.06,.028,.016],[.085,-.121,.105])],category='movable_container',joint=dict(type='free',initial='pose'),evidence='specified custom255x153x65 inner basket;same insert dimensions as other kits;offset key avoids the outer-pan key when nested')
    body('tool_dock',[-.20,.48,1.04],.65,[box('tool_land',[.09,.14,.018])])
    body('leaf_cup_tool',[-.20,.48,1.06],.18,[box('leaf_cup_floor',[.07,.05,.004]),box('leaf_cup_back',[.07,.004,.025],[0,.025,.014]),box('leaf_cup_key',[.05,.022,.016],[0,-.05,0])],category='movable_tool',joint=dict(type='free',initial='pose'))
    # Shared process cell: a large portal and an actual hollow enclosure, no whole-fixture exception.
    cp=[.45,.505,.93]
    body('process_cell',cp,20,[box('cell_floor',[.308,.35,.03],[-.071,0,.015]),box('cell_floor_right',[.088,.35,.03],[.181,0,.015]),box('cell_floor_port_front',[.054,.12,.03],[.11,-.115,.015]),box('cell_floor_port_rear',[.054,.07,.03],[.11,.14,.015]),box('cell_left_wall',[.012,.35,.52],[-.219,0,.26]),box('cell_right_wall',[.012,.35,.52],[.219,0,.26]),box('cell_rear_wall',[.426,.012,.52],[0,.169,.26]),box('cell_roof',[.45,.35,.012],[0,0,.514]),box('cell_front_left',[.06,.012,.52],[-.195,-.169,.26]),box('cell_front_right',[.06,.012,.52],[.195,-.169,.26]),box('cell_front_header',[.33,.012,.21],[0,-.169,.415]),box('cell_front_sill',[.33,.012,.05],[0,-.169,.025]),box('cell_land_a',[.03,.25,.012],[-.115,0,.036]),box('cell_land_b',[.03,.25,.012],[.115,0,.036])])
    body('cell_door',[.45,.330,1.115],.8,[box('cell_door_panel',[.33,.008,.29],[0,0,0],(.4,.8,.85,.3))],joint=dict(type='slide',axis=[0,0,1],range=[0,.29],initial=.29,drive='guarded24V shutter',brake='de_energize_to_apply'),category='appliance_moving')
    body('blade_carriage',[.45,.505,1.38],2,[box('carriage_plate',[.04,.18,.03]),box('guillotine_blade',[.001,.14,.11],[0,0,-.065])],joint=dict(type='slide',axis=[0,0,-1],range=[0,.275],initial=0,drive='5mm-pitch ballscrew>=1.5Nm continuous',brake='de_energize_to_apply+mechanical park catch'),category='appliance_tool')
    body('follower',[.575,.515,1.04],.25,[box('follower_pad',[.02,.08,.07])],joint=dict(type='slide',axis=[-1,0,0],range=[0,.18],initial=0,drive='encoded feed;5mm nominal along-X',brake='low force horizontal,retain food on loss'),category='appliance_moving')
    body('root_roller',[.45,.54,1.045],.35,[cyl('root_roller_geom',.025,.16,quat=[.7071067812,0,.7071067812,0])],joint=dict(type='hinge',axis=[1,0,0],range=[-6.283,6.283],initial=0,drive='rotary DC encoder',brake='mechanical food retention'),category='appliance_moving')
    body('cell_peeler',[.45,.54,1.26],.15,[box('peeler_edge',[.06,.003,.014]),box('peeler_depth_skid',[.07,.012,.012],[0,.01,0])],joint=dict(type='slide',axis=[0,0,-1],range=[0,.18],initial=0,drive='spring compliant peeler stage;follower provides longitudinal sweep',brake='spring return'),category='appliance_tool')
    body('eye_core_stage',[.53,.53,1.30],.25,[box('core_x_adapter',[.03,.04,.02])],joint=dict(type='slide',axis=[-1,0,0],range=[0,.12],initial=0,drive='depth-limited service stage',brake='spring return'),category='appliance_moving')
    body('eye_core_z',[0,0,0],.12,[box('eye_core_neck',[.015,.012,.06],[0,0,-.025]),cyl('eye_core_edge',.006,.004,[0,0,-.057])],parent='eye_core_stage',joint=dict(type='slide',axis=[0,0,-1],range=[0,.21],initial=0,drive='DC',brake='de_energize_to_apply'),category='appliance_tool')
    body('wedger_module',[.36,.62,1.05],.3,[box('wedger_module_adapter',[.11,.012,.02],[0,.06,0])],joint=dict(type='slide',axis=[0,-1,0],range=[0,.15],initial=0,drive='mode selector,park behind own shutter',brake='latched at selected position'),category='appliance_moving')
    body('wedger_blade',[0,0,0],.2,[box(f'wedger_edge{i}',[.09,.001,.012],[0,0,0],quat=[math.cos(i*math.pi/8),0,0,math.sin(i*math.pi/8)]) for i in range(4)],parent='wedger_module',joint=dict(type='slide',axis=[0,0,1],range=[0,.15],initial=.15,drive='vertical blade parking above entering basket',brake='de_energize_to_apply+park catch'),category='appliance_tool',evidence='custom90mm throat proxy for Nemco428-8 component;actual OEM fitting dimensions unverified')
    teeth=[box('wedger_tooth'+str(i),[.014,.008,.03],[.029*math.cos((i+.5)*math.pi/4),.029*math.sin((i+.5)*math.pi/4),-.04],quat=[math.cos((i+.5)*math.pi/8),0,0,math.sin((i+.5)*math.pi/8)]) for i in range(8)]
    body('wedger_pusher',[0,0,.26],.4,[cyl('wedger_pusher_plate',.041,.015)]+teeth,parent='wedger_module',joint=dict(type='slide',axis=[0,0,-1],range=[0,.23],initial=0,drive='shared>=1000N drive mode',brake='de_energize_to_apply+catch'),category='appliance_tool',evidence='specified slotted tooth proxy;not measured OEM pusher geometry;replacement union must not shrink to pass')
    body('cell_clamp_left',[.35,.56,1.05],.2,[box('cell_clamp_pad_left',[.018,.07,.04])],joint=dict(type='slide',axis=[1,0,0],range=[0,.04],initial=0,drive='spring compliant clamp',brake='retaining latch'),category='appliance_moving')
    body('cell_clamp_right',[.55,.56,1.05],.2,[box('cell_clamp_pad_right',[.018,.07,.04])],joint=dict(type='slide',axis=[-1,0,0],range=[0,.04],initial=0,drive='spring compliant clamp',brake='retaining latch'),category='appliance_moving')
    body('waste_bin',[.46,.50,.30],1.2,pan_geoms('waste',.30,.25,.27,.003),category='removable_bin')
    body('waste_chute',[.56,.53,.7075],.6,[box('waste_chute_front',[.054,.002,.445],[0,-.079,0]),box('waste_chute_back',[.054,.002,.445],[0,.079,0]),box('waste_chute_side_a',[.002,.156,.445],[-.026,0,0]),box('waste_chute_side_b',[.002,.156,.445],[.026,0,0])],evidence='specified open-bottom tube50x156mm internal;bottomz.485 insidebin;real cutouts in cell floor/worktop')
    body('waste_drop_gate',[.56,.53,.935],.15,[box('waste_gate_panel',[.054,.16,.003])],joint=dict(type='slide',axis=[1,0,0],range=[0,.07],initial=0,drive='low-voltage scrap gate;opens only own waste-drop operation',brake='spring return closed'),category='appliance_moving')
    body('dry_controller',[0,.64,.45],8,[box('controller_box',[.32,.18,.35])])
    body('robot_pedestal',[0,.70,1.20],12,[box('pedestal_post',[.10,.06,.54]),box('arm_mount_plate',[.18,.016,.18],[0,-.044,.14])])
    body('power_track',[0,.719,1.72],.8,[box('dry_track',[.60,.035,.05])])
    # Glass/polycarbonate only outside food paths. Service door is hinged around Z at left front.
    body('enclosure',[0,.375,1.43],9,[box('guard_left_lower',[.008,.75,.07],[-.721,0,-.485],(.6,.8,.9,.18)),box('guard_left_upper',[.008,.75,.67],[-.721,0,.185],(.6,.8,.9,.18)),box('guard_left_front_strip',[.008,.325,.30],[-.721,-.2125,-.30],(.6,.8,.9,.18)),box('guard_left_rear_strip',[.008,.095,.30],[-.721,.3275,-.30],(.6,.8,.9,.18)),box('guard_right',[.008,.75,1.04],[.721,0,0],(.6,.8,.9,.18)),box('guard_rear',[1.45,.008,1.04],[0,.371,0],(.6,.8,.9,.18)),box('guard_roof',[1.45,.75,.008],[0,0,.516],(.6,.8,.9,.18))])
    body('greens_output_gate',[-.721,.49,1.13],.7,[box('greens_gate',[.008,.33,.30])],joint=dict(type='hinge',axis=[0,0,1],range=[0,1.6],initial=0,drive='human output only',brake='interlocked lock,tools isolated'),category='guard')
    body('access_door',[-.713,.004,1.43],5,[box('access_door_panel',[1.426,.008,1.02],[.713,0,0],(.65,.85,.95,.18))],joint=dict(type='hinge',axis=[0,0,1],range=[0,1.6],initial=0,drive='human service only,dual channel monitored latch',brake='locked while active;start inhibited'),category='guard')
    for product,x in zip(['carrot','potato','bok_choy','tomato'],[-.525,-.175,.175,.525]):
        body('dock_'+product,[x,.20,.942],.4,[box('dock_'+product+'_land',[.285,.235,.024])])
        body('output_'+product,[x,.20,.954],.60,pan_geoms('pan_'+product)+[box('key_'+product,[.06,.028,.016],[0,-.121,.13]),box('key_backer_'+product,[.09,.006,.065],[0,-.092,.091])],category='movable_container',joint=dict(type='free',initial='pose'),evidence='GN265x163x100mm conservative full outline;OEM0.46kg pan+0.14kg keyed collar budget')
        body('carrier_'+product,[0,0,.008],.65,pan_geoms('basket_'+product,.255,.153,.065,.001, color=(.6,.72,.7,1))+[box('carrier_latch_'+product,[.018,.01,.012],[.12,0,.069])],parent='output_'+product,category='removable_insert',joint=dict(type='slide',axis=[0,0,1],range=[0,.12],initial=0,drive='wash dock lifts insert;pan latched before carry',brake='retaining clip'),evidence='specified custom65mm mesh basket inside GN outline;2mm mesh conservative sheet envelope;not holes omitted for robot clearance')
        body('lid_'+product,[0,.0815,.104],.18,[box('lid_panel_'+product,[.265,.163,.003],[0,-.0815,0],(.7,.72,.74,1))],parent='output_'+product,category='movable_container_lid',joint=dict(type='hinge',axis=[1,0,0],range=[-1.8,0],initial=0,drive='station lid finger actuator',brake='detent holds open or closed'))
        dim=PRODUCTS[product]['input_dimensions_mm']
        food_geoms=[box('food_'+product,[d/1000 for d in dim],[0,0,dim[2]/2000+.002],(.95,.43,.14,1) if product=='carrot' else ((.8,.7,.48,1) if product=='potato' else ((.2,.65,.23,1) if product=='bok_choy' else (.9,.18,.16,1))))]
        body('food_'+product,[0,0,.002],PRODUCTS[product]['input_mass_kg'],food_geoms,parent='carrier_'+product,category='food',evidence='cook_ref full-size input envelopes,not shrunken for collision')
    return copy.deepcopy(BODIES)

def bom_A():
    lines=[('A01','UR5e arm +controller +teach pendant',1,150000,'China engineering allowance;no current matched China quote'),('A02','1.2kg keyed/soft-cup EOAT,150N/15Nm direct metal key path',1,12000,'Fabrication/integration allowance;proof unqualified'),('A03','Stand-alone frame,worktop,wall-mount pedestal',1,6500,'China fabrication allowance'),('A04','Own basin,water inlet/filter/air break/drain/pump/brush/lift',1,3500,'Allowance;includes W04'),('A05','Bought peeler/huller/knife/wedger blade+pusher components',1,1800,'China import/component allowance,not a supplier quote'),('A06','Press/feed/rotary/core actuators and spring brakes/catches',1,8000,'Continuous capability must be verified;includes S06'),('A07','Shared processing frame,cartridges,rollers,eye/core stage',1,9000,'One-off fabrication allowance;includes P07'),('A08','Four keyed GN pan+insert kits and clean basket',1,3100,'4x650+500;China allowance,not HENDI quotation'),('A09','Vision,lighting,scales,controller and process sensing',1,6500,'Allowance'),('A10','Dry household power track,LV supplies,protected wiring',1,1600,'Allowance;RCD/PE hardware in safety package only'),('A11','Cleaning accessories,removable screens,seals',1,1500,'Allowance'),('A12','Assembly and commissioning engineering labor',1,12000,'Allowance;does not fund a product certification program'),('A13','ONE home safety package incl all guards and door interlocks',1,16000,'Enclosure/all blade covers,E-stop,dual-channel interlocks,relay/contactor,RCD/PE,presence sensor,no-restart;drive brakes A06 not duplicated'),('A14','Consumable blades/brushes and retention spares',1,2400,'Allowance')]
    return [dict(id=i,item=t,quantity=q,unit_cny=p,line_cny=q*p,basis=b) for i,t,q,p,b in lines]

def events_A():
    ev=[]
    def e(action,object,station,seconds=0,kind='appliance',details='',substeps=None):
        ev.append(dict(id=f'A{len(ev)+1:02}',action=action,object_id=object,station=station,estimated_s=seconds,kind=kind,details=details,substeps=substeps or [],motion_status='not_simulated',container_lid_contract='Every transported GN kit has its own lid closed;station finger opens only after seating and closes before transport.Pan opening/closing is an internal mechanism step and must be expanded.'))
    def transfer(product, dest, seconds=15, obj=None):
        obj=obj or 'output_'+product
        e('grasp',obj,'current_support',2,'grasp','Close jaw on named key;confirm retention;food and carrier keep unique identities')
        e('release',obj,dest,seconds+2,'release','Plan the loaded move between these endpoints;seat before open jaw;all subordinate containers/lids retain state')
    e('lock_guard_and_selfcheck','access_door','enclosure',20,details='Person outside;check water/drain,power,brakes,catch,bin and container IDs;reset does not restart')
    for p in ['carrot','potato']:
        transfer(p,'wash_basin')
        e('coarse_wash_and_all_surface_inspect','food_'+p,'wash_basin',60,details='Basket remains supported;rotate/rub all sides;fresh water;extend or reject if soil remains',substeps=['close_wash_lid','fill6L','index_and_rub_all_surfaces','lift_insert120mm','drain_dirty_pan','fresh_spray_pan_and_food','lower_insert','open_lid'])
        transfer(p,'process_cell')
        e('peel_trim_and_eye_inspect','food_'+p,'process_cell',120 if p=='carrot' else 180,details='Detach arm before power;peel depth0.2-0.8mm/gouge<=2;ends3-5mm carrot;all eyes scanned;reference3potato eyes',substeps=['close_cell_door','latch_pan','close_clamps','rotary_peel','index_all_surface_inspection']+(['eyer_work_and_retract_1','eyer_work_and_retract_2','eyer_work_and_retract_3'] if p=='potato' else [])+['end_trim_and_facet','park_all_tools','open_clamps','unlatch_pan','open_cell_door'])
        transfer(p,'wash_basin')
        e('fresh_post_peel_rinse','food_'+p,'wash_basin',30,details='Remove peel fragments;pan and basket also cleaned;peel scraps remain in waste bin',substeps=['close_lid','fresh_rinse','lift_insert','drain','lower_insert','open_lid'])
        transfer(p,'process_cell')
        e('slice5mm_and_recover_last_stub','food_'+p,'process_cell',45 if p=='carrot' else 30,details='Food captured by own cassette/follower;cuts fall into same mesh insert;last10mm stub receives two5mm cuts;all cut pieces inspected',substeps=['close_door','latch_pan','close_clamps','feed_cut_repeats','last10mm_stub_two_cuts','contained_piece_recovery','blade_park','open_clamps','unlatch_pan','open_door'])
        if p=='potato':
            transfer(p,'wash_basin')
            e('starch_rinse_and_drain','food_potato','wash_basin',100,details='Three fresh changes planned;lift slices before drain,never decant dirty water through food;extend until nearly clear;30s drain',substeps=['close_lid','fresh_fill_lift_drain_repeat3','spray_pan','lower_insert','drain30s','open_lid'])
        transfer(p,'dock_'+p)
        e('measure_and_close_output_lid','output_'+p,'dock_'+p,25,details='Distributed10cuts or all if fewer;weigh edible+captured residue;>=98% cut edible transfer;close lid only after pass')
    # Tomato wash before its cell cycle; skin/pulp retained, core waste explicit.
    transfer('tomato','wash_basin')
    e('wash_tomato_and_drain','food_tomato','wash_basin',50,details='Gentle supported rotation/wipe;all surfaces/stem recess;no blanch;10s drain',substeps=['close_lid','gentle_supported_rinse_wipe','lift_and_fresh_rinse','drain10s','open_lid'])
    transfer('tomato','process_cell')
    e('core_and_eight_wedges','food_tomato','process_cell',70,details='Core depth limited;seed cavity retained;arm detached;wedge cradle catches every piece/pulp;grid failure routes to draw-cut fallback,never acceptable crushing',substeps=['close_door','latch_pan','gentle_support_clamp','inspect_core','core_work_then_park','support_handoff_to_wedger','pusher_work_then_park','petal_catch_recover','unclamp','unlatch_pan','open_door'])
    transfer('tomato','dock_tomato')
    e('measure_and_close_output_lid','output_tomato','dock_tomato',45,details='Count8;all35-55deg,0.65-1.35mean mass;skin fully separated,pulp retained,<10% compression,no bruise;>=98% transfer')
    transfer('bok_choy','wash_basin')
    e('coarse_rinse_root','food_bok_choy','wash_basin',30,details='Remove exterior mud;discard yellow/rotten leaves with explicit waste identities',substeps=['close_lid','coarse_rinse','drain','open_lid'])
    transfer('bok_choy','process_cell')
    e('root_trim_and_stalk_release','food_bok_choy','process_cell',30,details='5-10mm disk;release all6reference stalks without tearing;inspect every separation;additional attached stalks extend cycle',substeps=['close_door','latch_pan','root_disk_cut','guarded_spreader_release6','blade_park','unlatch_pan','open_door'])
    transfer('bok_choy','wash_basin')
    e('soak600s','carrier_bok_choy','wash_basin',600,details='Full600s cold soak;overlap150s guarded empty-cell rinse/cleanup using separate fresh spray branch,all cell tools parked;no shared basin volume',substeps=['fill_cold','start_timer600','parallel_empty_cell_clean150s','timer_complete','lift_stalk_source_basket_before_drain','fresh_water_rinse'])
    for k in range(1,7):
        e('grasp_leaf',f'leaf_{k}','carrier_bok_choy',5,'grasp','Spring-limited bottom-supported food cup;powered blades parked;leaf identity leaves source basket')
        e('work_basal_crease',f'leaf_{k}','wash_brush',25,'working_stroke','Expose/rub every basal crease at2-5N;screen7.5N reaction including1.5margin;inspect and fresh rinse;not just soak',substeps=['straight_work_approach<=50mm','brush_work_line','inspect_basal_crease','fresh_rinse','straight_work_retreat_until5mm_gap'])
        e('release_leaf',f'leaf_{k}','clean_leaf_basket',5,'release','Named clean receiver floor;other dirty leaves remain in source;cup cleaned between contaminated grasps')
    e('drain_clean_greens','clean_leaf_basket','inspection_dock',30,details='No continuous dripping,no squeeze;source empty pan washed before clean food returns')
    e('grasp','clean_leaf_basket','inspection_dock',2,'grasp','Pick own handle;all6leaf identities enclosed')
    e('release','clean_leaf_basket','process_cell',17,'release','Seat clean basket on cell support;source pan/insert remain washed and stationary in basin')
    e('split_and_section40mm','clean_leaf_basket','process_cell',90,details='Two wide reference stalks split<=15mm;width/bundle<=30mm;redistribute every edible terminal section into30-50mm;contained catch back to basket',substeps=['close_door','latch_clean_basket','split_wide_stalks2','arrange_low_bundle','length_balanced_section_repeats','recover_fibers_and_pieces','blade_park','unlatch_basket','open_door'])
    e('grasp','clean_leaf_basket','process_cell',2,'grasp','Same retained clean basket and section identities')
    e('release','clean_leaf_basket','output_bok_choy_at_wash',17,'release','Clean basket nests in washed dedicated bok-choy outer bowl;the original empty dirty insert remains basin supported')
    e('measure_and_close_output_lid','output_bok_choy','wash_basin',30,details='Inspect every basal crease,all fibers,width/length;>=98%transfer;thenclose lid;this bowl is collected through dedicated left-side output port after safe stop',substeps=['verify_wash_pan_clean','weigh_and_inspect','close_lid','enable_left_output_port_only_after_safe_stop'])
    e('clean_and_safe_park','process_cell','all_stations',150,details='Total cleaning300s:150s empty-cell rinse already overlapped A52 plus150s final drain/screen/food-path/park;release only with all-tools-retained and no blade access',substeps=['cell_tool_park','wash_scrap_screen','basin_flush','food_path_rinse','drain_all','close_water','arm_safe_park'])
    e('publish_and_unlock','access_door','enclosure',10,details='All four labeled bowls supported,accepted or explicitly rejected;stop/isolate tools before unlock;human removes bin and food')
    return ev

def main():
    RESULTS.mkdir(exist_ok=True)
    with (RESULTS/'survey.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(SURVEY[0]));w.writeheader();w.writerows(SURVEY)
    dump('sources.json', [dict(id=k,url=v[0],kind=v[1],limits=v[2],retrieved_or_rechecked=DATE) for k,v in SOURCES.items()])
    dump('products.json',PRODUCTS)
    # The event ledger deliberately distinguishes high-level cycles from expanded appliance strokes.
    events=events_A()
    write_process_and_concepts(events)
    write_stations(events)
    drawings()
    audit()

def food_catalog():
    """Nominal conserved mass parcels, not food measurements or topology qualification."""
    table={}
    def split(p, waste, n, dims):
        m=PRODUCTS[p]['input_mass_kg'];edible=m-sum(waste.values())
        table[p]=dict(initial_token='food_'+p,initial_mass_kg=m,waste=[dict(id=p+'_'+k,mass_kg=v,owner='waste_bin') for k,v in waste.items()],pieces=[dict(id=p+'_piece_'+str(i+1),mass_kg=edible/n,geometry=[box(p+'_piece_geom_'+str(i+1),dims)],final_owner='carrier_'+p) for i in range(n)],edible_nominal_kg=edible,allocation_status='illustrative design bookkeeping;actual measured waste/edible masses replace values without changing conservation')
    split('carrot',{'peel':.0068,'end_trim':.0071,'facet':.0011},30,[.005,.034,.034])
    split('potato',{'peel':.012,'eyes':.0015,'facet':.003},18,[.005,.064,.069])
    split('tomato',{'core':.003},8,[.07,.07,.06])
    # Tomato piece boxes retain whole fruit envelope conservatively: no fabricated smaller wedge geometry admission.
    table['tomato']['geometry_limit']='Whole70x70x60mm box per piece is intentionally conservative until actual wedge solids are supplied;not an eight-wedge collision/packing witness'
    m=.10;w=.004;leaf=(m-w)/6
    pieces=[]
    for leaf_id in range(1,7):
        width_splits=2 if leaf_id<=2 else 1
        for strip in range(width_splits):
            for section in range(4):
                pid=f'greens_leaf{leaf_id}_strip{strip+1}_section{section+1}'
                pieces.append(dict(id=pid,mass_kg=leaf/(width_splits*4),geometry=[box(pid+'_geom',[.0405,.015,.02])],final_owner='clean_leaf_basket'))
    table['bok_choy']=dict(initial_token='food_bok_choy',initial_mass_kg=m,waste=[dict(id='bok_choy_root_disk',mass_kg=w,owner='waste_bin')],leaves=[dict(id=f'leaf_{i}',mass_kg=leaf,geometry=[box(f'leaf_{i}_geom',[.17,.10,.07])],geometry_limit='Whole-head envelope retained for each separated leaf until measured segmented leaf solids exist;not a leaf grasp or packing admission',owner_before_wash='carrier_bok_choy',owner_after_wash='clean_leaf_basket') for i in range(1,7)],pieces=pieces,edible_nominal_kg=.096,allocation_status='illustrative mass balance,not weighed yield;leaf section boxes are design proxies,not deformable-food validation')
    return table

def event_state_ledger(events, catalog):
    s=dict(arm=dict(jaw='open',held=None,builtin_leaf_cup='empty'),containers={f'output_{p}':{'location':'dock_'+p,'lid':'closed','insert':'carrier_'+p,'water_kg':0,'pan_hygiene':'raw_requires_wash'} for p in PRODUCTS},inserts={f'carrier_{p}':{'parent':'output_'+p,'latched':True} for p in PRODUCTS},clean_leaf_basket=dict(location='inspection_dock',parent=None,contents=[]),appliances=dict(wash_lid='open',wash_lift_m=0,water_supply='off',process_door='open',blade='parked_caught',pusher='parked_caught',follower_mm=0,root_roller='stopped',peeler='parked',eyer='parked',clamps=['open','open'],waste_bin_lid='closed_except_scrap_drop'),guard='unlocked_stopped',food={f'food_{p}':{'mass_kg':PRODUCTS[p]['input_mass_kg'],'owner':'carrier_'+p} for p in PRODUCTS},accepted_bowls=[],status='design_intent_no_motion')
    states=[copy.deepcopy(s)]
    for e in events:
        action,obj=e['action'],e['object_id']
        if action=='lock_guard_and_selfcheck':s['guard']='locked'
        elif action=='grasp_OEM_pusher':
            assert s['arm']['held'] is None
            s['arm'].update(jaw='closed_key',held=obj)
            s['appliances']['B_pusher_owner']='arm'
        elif action=='release_OEM_pusher':
            assert s['arm']['held']==obj
            s['arm'].update(jaw='open',held=None)
            s['appliances']['B_pusher_owner']=e['station']
        elif action=='start_green_button':s['appliances']['B_slicer']='running_after_button_only'
        elif action=='stop_isolate_and_clean_disc':s['appliances']['B_slicer']='isolated_clean_reassembled_at_event_end'
        elif action=='grasp':
            assert s['arm']['held'] is None
            s['arm'].update(jaw='closed_key',held=obj)
        elif action=='release':
            assert s['arm']['held']==obj,(e,s['arm'])
            s['arm'].update(jaw='open',held=None)
            if obj in s['containers']:s['containers'][obj]['location']=e['station']
            else:s['clean_leaf_basket']['location']=e['station']
            if obj=='clean_leaf_basket' and e['station']=='output_bok_choy_at_wash':
                s['clean_leaf_basket']['parent']='output_bok_choy'
                s['containers']['output_bok_choy']['insert']='clean_leaf_basket'
                s['inserts']['carrier_bok_choy'].update(parent=None,location='wash_basin',latched=False)
        elif action=='grasp_leaf':
            assert s['arm']['held'] is None
            s['arm'].update(jaw='food_cup_retained',held=obj,builtin_leaf_cup=obj)
            s['food'][obj]['owner']='arm_food_cup'
        elif action=='work_basal_crease':
            s['food'][obj]['basal_crease']='inspection_pending'
            s['appliances']['water_supply']='off_at_event_end'
        elif action=='release_leaf':
            assert s['arm']['held']==obj
            s['arm'].update(jaw='open',held=None,builtin_leaf_cup='empty')
            s['food'][obj]['owner']='clean_leaf_basket';s['clean_leaf_basket']['contents'].append(obj)
        elif action=='root_trim_and_stalk_release':
            old=s['food'].pop('food_bok_choy');c=catalog['bok_choy']
            for x in c['leaves']:s['food'][x['id']]={'mass_kg':x['mass_kg'],'owner':'carrier_bok_choy'}
            for x in c['waste']:s['food'][x['id']]={'mass_kg':x['mass_kg'],'owner':'waste_bin'}
        elif action=='soak600s':
            s['containers']['output_bok_choy']['lid']='open_for_leaf_access'
            s['appliances']['wash_lift_m']=.12
        elif action=='peel_trim_and_eye_inspect':
            p=obj.removeprefix('food_');c=catalog[p]
            s['food'][obj]['mass_kg']=c['edible_nominal_kg']
            for x in c['waste']:s['food'][x['id']]={'mass_kg':x['mass_kg'],'owner':'waste_bin'}
        elif action in ('slice5mm_and_recover_last_stub','core_and_eight_wedges','split_and_section40mm'):
            p='bok_choy' if action=='split_and_section40mm' else obj.removeprefix('food_');c=catalog[p]
            if p=='bok_choy':
                for i in range(1,7):s['food'].pop(f'leaf_{i}')
                s['clean_leaf_basket']['contents']=[]
            else:s['food'].pop('food_'+p)
            if p=='tomato':
                for x in c['waste']:s['food'][x['id']]={'mass_kg':x['mass_kg'],'owner':'waste_bin'}
            for x in c['pieces']:s['food'][x['id']]={'mass_kg':x['mass_kg'],'owner':x['final_owner']}
        elif action=='measure_and_close_output_lid':
            s['containers'][obj].update(lid='closed',pan_hygiene='clean_required_to_pass')
            s['accepted_bowls'].append(dict(id=obj,status='quality_acceptance_required_not_observed'))
        elif action=='publish_and_unlock':
            assert s['arm']['held'] is None
            s['guard']='unlocked_after_stop';s['appliances']['water_supply']='off'
        if 'wash' in action or 'rinse' in action:
            for pan in s['containers'].values():
                if pan['location']=='wash_basin':pan.update(pan_hygiene='clean_required_to_pass',water_kg=0)
        state=copy.deepcopy(s)
        state['after_event']=e['id']
        state['total_food_mass_kg']=sum(x['mass_kg'] for x in s['food'].values())
        assert abs(state['total_food_mass_kg']-.57)<1e-10,(e,state['total_food_mass_kg'])
        state['interpretation']='Proposed event-boundary ownership only;physical trajectories,measured food conservation and intermediate mechanism states are unverified'
        states.append(state)
    return states

def make_B_events(a):
    b=[]
    def extra(action,obj,station,seconds,kind,details):
        b.append(dict(action=action,object_id=obj,station=station,estimated_s=seconds,kind=kind,details=details,substeps=[],motion_status='not_simulated'))
    for source in a:
        e=copy.deepcopy(source);e['reference_template_event_id']=source['id']
        if source['id']=='A07':
            extra('halve_long_carrot_before_Rotato','food_carrot','B_finish_cell',30,'appliance','Two80mm portions stay one conserved carrot lot;new cut faces are edible,not unexplained scraps')
        if source['id'] in ('A12','A27'):e['station']='B_slicer'
        if source['id'] in ('A13','A28'):
            extra('grasp_OEM_pusher','B_pusher','B_pusher_dock',3,'grasp','Slicer stopped;original supplied pusher')
            extra('release_OEM_pusher','B_pusher','B_feed_actuator',17,'release','Fixed actuator retains pusher;arm withdraws')
            extra('start_green_button','B_start_button','B_slicer',4,'appliance','Physical button poker after every lid/restart transaction;smart plug only isolates')
            e['station']='B_slicer'
            e['details']='ONE5mm disc-cut cycle replaces A guillotine cycle;all cut food returns to own pan through enclosed catch adapter.No second cut cycle.No terminal-stub/yield credit without validation.'
            e['substeps']=['confirm_OEM_lid_locked','retain_food_in_own_feed_adapter','transfer_food_to_OEM_hopper_support','fixed_OEM_pusher_feed','continuous_discharge_into_same_food_lot_basket','terminal_piece_recovery','motor_stop_and_brake']
        if source['id']=='A52':
            e['substeps']=['fill_cold','timer600','parallel_finish_cell_rinse150s','lift_insert_before_drain','fresh_rinse']
        b.append(e)
        if source['id']=='A07':
            extra('Rotato_second_load_and_touchup','food_carrot','B_peeler',90,'appliance','Second half:top pin,height lever,start,rocking unload,end/scar finishing;both halves conserved')
        if source['id'] in ('A13','A28'):
            extra('grasp_OEM_pusher','B_pusher','B_feed_actuator',3,'grasp','Stopped appliance;remove retained pusher')
            extra('release_OEM_pusher','B_pusher','B_pusher_dock',17,'release','Park on its own named dock')
            extra('stop_isolate_and_clean_disc','B_disc','B_slicer',100,'appliance','Lockable stop/isolation;retained disc/lid cleaning and reassembly subpaths required,all food already in its own pan')
    for i,e in enumerate(b):e['id']=f'B{i+1:02}'
    return b

def write_process_and_concepts(events):
    catalog=food_catalog();states=event_state_ledger(events,catalog)
    dump('food_catalog.json',catalog)
    dump('events_A.json',events)
    b_events=make_B_events(events)
    dump('events_B.json',b_events)
    dump('state_ledger_A.json',states)
    dump('state_ledger_B.json',event_state_ledger(b_events,catalog))
    # Dependency/resource schedule in seconds, explicitly a timing estimate.
    # Soak can run while arm inspects finished outputs/cleans detached root inserts.
    active=sum(e['estimated_s'] for e in events)
    base_bom=bom_A();subtotal=sum(l['line_cny'] for l in base_bom)
    b_bom=copy.deepcopy(base_bom)
    for l in b_bom:
        if l['id']=='A07':l['item']='Compact finish cell and guarded Rotato adapters';l['line_cny']=l['unit_cny']=5000
    b_bom += [dict(id='B15',item='CL20+5mmdisc and guarded fixed OEM-pusher adapter',quantity=1,unit_cny=18000,line_cny=18000,basis='China engineering import allowance;matched CNY quote ND'),dict(id='B16',item='Two Rotato units and food handoff nests',quantity=1,unit_cny=2000,line_cny=2000,basis='China landed/adaptation allowance;two food halves modeled'),dict(id='B17',item='Short850mm horizontal rail,drive,brake,cable chain',quantity=1,unit_cny=6000,line_cny=6000,basis='China fabrication allowance;de-energize-to-apply brake,not duplicated in safety line')]
    bb=sum(l['line_cny'] for l in b_bom)
    write_bom_csv(base_bom,b_bom)
    common=dict(acceptance=dict(pose_translation_m=.005,pose_rotation_degrees=3,robot_environment_gap_m=.010,arm_arm_gap_m=.010,gripper_held_environment_gap_m=.005,PAD=0,mu=.5,SF=1.5,key_force_N=150,key_moment_Nm=15,planner_seconds_per_connection_min=60,point_displacement_m_max=.004),event_count_basis='Supervisory task events;grasp and release counted separately;motion between them is a separate planner edge.Appliance batches include enumerated internal strokes;expanded mechanism ledger is larger than79/93 and earns no motion credit.',status='research_design_only;no_motion_simulation;no_food_quality_qualification',power_feed='One220-240V household feed,dry household power track,RCD andPE;no gas/air/battery',water='Cold mains inlet,backflow air break,screened gravity drain,overflow/leak tray and shutoff;no peels down drain',food_products=PRODUCTS)
    common['expanded_named_substeps_minimum']={name:len(es)+sum(max(0,len(e['substeps'])-1) for e in es) for name,es in [('cassette_fixed',events),('appliance_hybrid',b_events)]}
    common['expanded_count_limit']='216/223 minimum named operations exclude extra pan-lid actions,repeated blade/feed/peel strokes and sample checks;neither is a <=80 atomic-operation demonstration.'
    A=dict(id='cassette_fixed',name='One fixed arm,GN cassettes,shared guarded process cell',recommended=True,footprint_m=[1.45,.75],height_m=1.95,worktop_m=.92,arms=1,arm_model='UR5e',arm_mount=dict(position_m=[0,.674,1.34],quaternion_wxyz=[math.sqrt(.5),math.sqrt(.5),0,0],description='Fixed inward-facing wall mount on stand-alone rear pedestal;local+Z points world-Y;actual mount envelope/brakes recomputed by integrator'),rail=None,station_layout=[dict(id='wash_basin',center_m=[-.49,.49],size_m=[.36,.32],top_m=1.15),dict(id='process_cell',center_m=[.45,.505],size_m=[.45,.35],top_m=1.45),dict(id='inspection_dock',center_m=[0,.475],size_m=[.295,.235],top_m=.974),dict(id='input_output_ports',centers_m=[[-.525,.165],[-.175,.165],[.175,.165],[.525,.165]],size_each_m=[.285,.235],pan_bottom_m=.955),dict(id='greens_side_output',side='left',y_center_m=.49,clear_m=[.33,.30],description='After safe stop,remove bok-choy bowl from basin through side port;three other bowls at front')],events=events,event_count=len(events),minimum_arm_connections=len(events)-1,estimated_minutes=38.0,estimated_timing=dict(serial_nominal_event_seconds=active,nominal_seconds_plus_20percent=round(active*1.2,1),estimated_overlap_s=150,overlap_work='During600s soak,inspect/wipe retained root output kits and cell surfaces with basin reserved;no simultaneous-moving second arm',planning_minutes=38,measured_minutes=None,allowance='38min includes untimed IK travel variability,rework up to~4min and product inspections;extra leaves/eyes/dirty produce may exceed45min',resource_calendar='A01-A51 serial;A52 soak600s overlaps150s of detached output inspection/cleaning rescheduled from A16/A34/A43/A78;A53-A79 sequential,same state identities.No basin use in overlap.'),bom=base_bom,subtotal_cny=subtotal,contingency_fraction=.15,estimated_cny=round(subtotal*1.15,2),safety_package_cny=16000,price_status='All selected hardware figures are China planning allowances;no complete matched-price quotation exists',risks=['Peel coverage/depth and eyes/core perception unqualified','Wedger pulp/bruising risk;fallback adds time andmechanism','One arm leaf handling and cup sanitation still need paths','79 counts supervisory cycles,not every internal stroke','No arm clearance,IK,payload-CoM or rated-torque admission','Side output is practical only after all robot/tools stop;wash basin/bowl sanitation mandatory'])
    B=dict(id='appliance_hybrid',name='One short-rail arm,Rotato,CL20 and custom greens/core finish cell',recommended=False,footprint_m=[1.50,.75],height_m=1.95,worktop_m=.92,arms=1,arm_model='UR5e',arm_mount=dict(position_m=[0,.675,1.64],quaternion_wxyz=[math.sqrt(.5),math.sqrt(.5),0,0],description='Horizontal rail center850mm stroke;higher mount clears CL20;actual arm envelope unverified'),rail=dict(axis=[1,0,0],range_m=[-.425,.425],beam_length_m=1.20,beam_section_m=[.10,.08],brake='de_energize_to_apply'),station_layout=[dict(id='wash_basin',center_m=[-.53,.475],size_m=[.36,.31],top_m=1.15),dict(id='B_finish_cell',center_m=[-.08,.475],size_m=[.42,.31],top_m=1.42),dict(id='B_slicer',center_m=[.50,.475],size_m=[.325,.31],top_m=1.49),dict(id='B_peeler',center_m=[-.08,.17],size_m=[.165,.16],top_m=1.23,description='Two peeler units use two undercounter latching cradles brought up individually;full conversion mechanism still unqualified'),dict(id='input_output_ports',description='Four front GN ports;peeler temporarily occupies dedicated service dock,never a finished bowl dock')],events=make_B_events(events),event_count=93,estimated_minutes=42.0,estimated_timing=dict(measured_minutes=None,planning_minutes=42,overlap_s=160,description='Greens600s soak overlaps detached CL20 cutting/pusher work and output inspections;starch rinse and tomato wash wait for basin;nominal cutter throughput is not used as meal time',margin='Higher uncertainty than A;OEM disassembly and two Rotato carrot halves can exceed45min'),bom=b_bom,subtotal_cny=bb,contingency_fraction=.15,estimated_cny=round(bb*1.15,2),safety_package_cny=16000,risks=['93 supervisory events exceeds80 goal','Exact CL20 hopper/pusher geometry unknown;65x70potato must use verified large inlet','Rotato food140mm limit requires carrot halves,end and eye touchup','Commodity nominal cuts do not certify4-6mm/within-slice1mm or98%transfer','Rail adds braking/chain/shielding and1.64m mount reach uncertainties','Temporary peeler dock and OEM cleaning must be mechanically completed;no hidden tool or bowl occupancy admitted'],selection='Reserve as appliance-integration alternative;not recommended to freeze')
    # Correct B geometry: a front peeler must not overlap four bowl positions. Store it at own rear-cell cradle.
    for l in B['station_layout']:
        if l['id']=='B_peeler':l.update(center_m=[-.08,.475],description='Guarded rotary peelers dock inside finish-cell volume as mutually-exclusive inserts;not simultaneous separate overlapping boxes')
    A['estimated_minutes']=45.0
    A['estimated_timing']=dict(serial_nominal_event_seconds=active+150,parallel_cell_clean_s=150,resource_scheduled_nominal_seconds=active,nominal_minutes=round(active/60,3),planning_minutes=45,planning_allowance_s=269,measured_minutes=None,resource_calendar='A01-A51 serial;A52 includes600s soak concurrently with150s guarded empty-cell rinse,using separate fresh spray branch and common screened drain.A53-A77 sequential;A78 includes only remaining150s of300s total cleanup;A79 stopped output release.',limitation='40.52min nominal plus4.48min contingency=45min.The margin is modest;extra eyes/leaves,dirt,slow accepted paths or draw-cut fallback can exceed45min.No speed or force qualification is claimed.')
    A['station_layout'][3]['centers_m']=[[x,.20] for x in [-.525,-.175,.175,.525]]
    A['station_layout'][3]['pan_bottom_m']=.954
    A['arm_mount']['position_m']=[0,.648,1.34]
    B['events']=b_events
    B['estimated_minutes']=56.0
    bseconds=sum(e['estimated_s'] for e in b_events)
    B['estimated_timing']=dict(resource_scheduled_nominal_seconds=bseconds,nominal_minutes=round(bseconds/60,3),planning_allowance_s=56*60-bseconds,planning_minutes=56,measured_minutes=None,description='Same150s empty-cell cleanup overlap during greens600s soak;additional OEM pusher/button/disc handling and second Rotato half add408s (6.8min).No extra processing of duplicated food.',limitation='Fails45min and80-supervisory-event targets;fine hopper/food quality geometry still unqualified')
    B['selection']='Complete candidate recipe concept with explicit ordered extra transactions;exceeds event/time goals and has unresolved OEM fitting geometry,so not recommended.'
    dump('concepts.json',dict(schema_version='r06.stations.concepts.1',date=DATE,recommendation=A['id'],common=common,concepts=[A,B]))

def write_bom_csv(a,b):
    rows=[]
    for c,ls in [('cassette_fixed',a),('appliance_hybrid',b)]:
        for l in ls:rows.append(dict(concept=c,**l))
    with (RESULTS/'bom.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def write_stations(events):
    bs=geometry()
    supports=[dict(id='worktop_top',body='worktop',geom='worktop_full',point_local_m=[-.096,0,.01],normal_local=[0,0,1],polygon_local_m=[[-.725,-.375,.01],[.533,-.375,.01],[.533,.375,.01],[-.725,.375,.01]])]
    for gid,point,rect in [('worktop_right',[.656,0,.01],[.138,.75]),('worktop_port_front',[.56,-.15,.01],[.054,.45]),('worktop_port_rear',[.56,.305,.01],[.054,.14])]:
        supports.append(dict(id=gid+'_face',body='worktop',geom=gid,point_local_m=point,normal_local=[0,0,1],rectangle_m=rect))
    for p in PRODUCTS:
        supports += [dict(id='dock_face_'+p,body='dock_'+p,geom='dock_'+p+'_land',point_local_m=[0,0,.012],normal_local=[0,0,1],rectangle_m=[.285,.235]),dict(id='pan_floor_face_'+p,body='output_'+p,geom='pan_'+p+'_floor',point_local_m=[0,0,.0007],normal_local=[0,0,1],rectangle_m=[.2636,.1616]),dict(id='basket_floor_face_'+p,body='carrier_'+p,geom='basket_'+p+'_floor',point_local_m=[0,0,.001],normal_local=[0,0,1],rectangle_m=[.253,.151])]
    supports += [dict(id='wash_lift_face_a',body='wash_lift',geom='wash_lift_left',point_local_m=[-.115,0,.007],normal_local=[0,0,1],rectangle_m=[.015,.20]),dict(id='wash_lift_face_b',body='wash_lift',geom='wash_lift_right',point_local_m=[.115,0,.007],normal_local=[0,0,1],rectangle_m=[.015,.20]),dict(id='cell_land_face_a',body='process_cell',geom='cell_land_a',point_local_m=[-.115,0,.042],normal_local=[0,0,1],rectangle_m=[.03,.25]),dict(id='cell_land_face_b',body='process_cell',geom='cell_land_b',point_local_m=[.115,0,.042],normal_local=[0,0,1],rectangle_m=[.03,.25]),dict(id='inspection_face',body='inspection_dock',geom='inspection_land',point_local_m=[0,0,.0125],normal_local=[0,0,1],rectangle_m=[.295,.235]),dict(id='clean_basket_face',body='clean_leaf_basket',geom='clean_leaf_floor',point_local_m=[0,0,.001],normal_local=[0,0,1],rectangle_m=[.253,.151])]
    handles=[];contacts=[]
    for p in PRODUCTS:
        obj='output_'+p
        handles.append(dict(id='handle_'+p,object_id=obj,geom='key_'+p,pose_local=dict(position_m=[0,-.121,.13],quaternion_wxyz=IDENTITY),jaw_axis_local=[1,0,0],approach_axis_local=[0,0,-1],retreat_axis_local=[0,0,1],grasp_land_m=[.06,.028,.016],key_design_force_N=150,key_design_moment_Nm=15,key_status='proof_required',combined_mass_kg=.60+.65+.18+PRODUCTS[p]['input_mass_kg'],com_limit_from_flange_m=.18))
        contacts.append(dict(id='grasp_key_'+p,kind='grasp_release_support',object_id=obj,support_id='eoat_key_capture',object_geoms=['key_'+p],support_geoms=['eoat_key_left','eoat_key_right'],activation='only matching key capture,pose/key proof valid;retain while this object is held',window=dict(max_length_m=.05,axis_local=[0,0,-1],straight=True,ends_at_gap_m=.005),non_working_paths_may_use=True,scope='own grasp only;no food/tool permission inherited'))
        for dest,faces in [('dock_'+p,['dock_face_'+p]),('wash_lift',['wash_lift_face_a','wash_lift_face_b']),('process_cell',['cell_land_face_a','cell_land_face_b'])]:
            contacts.append(dict(id='support_'+p+'_'+dest,kind='grasp_release_support',object_id=obj,support_id=dest,object_geoms=['pan_'+p+'_floor'],support_faces=faces,activation='named own support at declared grasp/release;lift/lower<=50mm along+Z until5mm gap',window=dict(max_length_m=.05,axis_world=[0,0,1],straight=True,orientation_constant=True,ends_at_gap_m=.005),non_working_paths_may_use=True,scope='Only this pan floor against these exact support lands;guard/walls/sides excluded'))
        contacts.append(dict(id='cargo_'+p,kind='grasp_release_support',object_id='food_'+p,support_id='carrier_'+p,object_geoms=['food_'+p],support_faces=['basket_floor_face_'+p],activation='Own retained cargo support;food stays in same carrier until an explicit process transition;not an appliance or arm exemption',window=dict(max_length_m=.05,axis_world=[0,0,1],straight=True,ends_at_gap_m=.005),non_working_paths_may_use=True))
    for i in range(1,7):
        for kind,support,face in [('grasp_release_support','carrier_bok_choy','basket_floor_face_bok_choy'),('grasp_release_support','clean_leaf_basket','clean_basket_face')]:
            contacts.append(dict(id=f'leaf_{i}_{support}',kind=kind,object_id=f'leaf_{i}',support_id=support,object_geoms=[f'leaf_{i}_geom'],support_faces=[face],activation='Only this leaf own pickup/release support and straight<=50mm normal window',window=dict(max_length_m=.05,axis_world=[0,0,1],straight=True,ends_at_gap_m=.005),non_working_paths_may_use=True))
        contacts.append(dict(id=f'leaf_{i}_brush_work',kind='working_stroke',object_id=f'leaf_{i}',support_id='wash_brush',object_geoms=[f'leaf_{i}_geom'],support_geoms=['wash_brush_cylinder'],force_id='leaf_brush',activation=f'Only A{54+(i-1)*3:02} declared work stroke and its straight<=50mm work approach/retreat;remove on every connection',window=dict(max_length_m=.05,axis_world=[0,1,0],straight=True,ends_at_gap_m=.005),non_working_paths_may_use=False))
    for p in ['carrot','potato']:
        for tool,geom,force in [('cell_peeler','peeler_edge','peel_drag'),('eye_core_z','eye_core_edge','eye_core'),('blade_carriage','guillotine_blade',p+'_cut')]:
            contacts.append(dict(id=p+'_'+tool+'_work',kind='working_stroke',object_id='food_'+p,support_id=tool,object_geoms=['food_'+p],support_geoms=[geom],force_id=force,activation='Only named appliance operation substroke;arm detached;never allow this pair on loading/unloading/connection paths',window=dict(max_length_m=.05,axis_world=[0,0,1],straight=True,ends_at_gap_m=.005),non_working_paths_may_use=False))
    contacts += [dict(id='tomato_wedge_work',kind='working_stroke',object_id='food_tomato',support_id='wedger_blade',object_geoms=['food_tomato'],support_geoms=['wedger_edge'+str(i) for i in range(4)],force_id='wedger',activation='Only pusher_work_then_park inside A40;arm detached;no blade/food permission on loading or other paths',window=dict(max_length_m=.05,axis_world=[0,0,1],straight=True,ends_at_gap_m=.005),non_working_paths_may_use=False),dict(id='tomato_core_work',kind='working_stroke',object_id='food_tomato',support_id='eye_core_z',object_geoms=['food_tomato'],support_geoms=['eye_core_edge'],force_id='eye_core',activation='Only core_work_then_park inside A40',window=dict(max_length_m=.05,axis_world=[0,0,1],straight=True,ends_at_gap_m=.005),non_working_paths_may_use=False)]
    # Additional exact declarations for separate clean-basket transfers and whole-bundle work.
    for sup,faces in [('inspection_dock',['inspection_face']),('process_cell',['cell_land_face_a','cell_land_face_b']),('output_bok_choy',['pan_floor_face_bok_choy'])]:
        contacts.append(dict(id='clean_basket_'+sup,kind='grasp_release_support',object_id='clean_leaf_basket',support_id=sup,object_geoms=['clean_leaf_floor'],support_faces=faces,activation='Own basket grasp/release support only',window=dict(max_length_m=.05,axis_world=[0,0,1],straight=True,ends_at_gap_m=.005),non_working_paths_may_use=True))
    contacts.append(dict(id='greens_root_work',kind='working_stroke',object_id='food_bok_choy',support_id='blade_carriage',object_geoms=['food_bok_choy'],support_geoms=['guillotine_blade'],force_id='greens_cut',activation='Only root_disk_cut in A49;remove for all connections',window=dict(max_length_m=.05,axis_world=[0,0,1],straight=True,ends_at_gap_m=.005),non_working_paths_may_use=False))
    for i in range(1,7):
        contacts.append(dict(id=f'greens_leaf{i}_section_work',kind='working_stroke',object_id=f'leaf_{i}',support_id='blade_carriage',object_geoms=[f'leaf_{i}_geom'],support_geoms=['guillotine_blade'],force_id='greens_cut',activation='Only split and section substrokes in A74;own leaf only',window=dict(max_length_m=.05,axis_world=[0,0,1],straight=True,ends_at_gap_m=.005),non_working_paths_may_use=False))
    geom_ids=[g['id'] for b in bs for g in b['geometry']]
    d=dict(schema_version='r06.stations.scene.1',date=DATE,concept='cassette_fixed',units=dict(length='m',mass='kg',force='N',moment='Nm',angles='radians',quaternion='wxyz'),coordinates='World+X right,+Y back,+Z up;floor0;modulex[-.725,.725],y[0,.75]',geometry_schema=dict(box='Full edge lengths in size_m;MuJoCo half-size=size_m/2',cylinder='radius_m,height_m;MuJoCo size=[radius,height/2],axis localZ',pose='Local relative to named parent;quaternionwxyz',joints='Hinge radians,slide metres;free joint initial world transform composed from parent',inertias='Concept budgets for station parts only;never replace OEM arm inertias',food='Whole input proxies plus explicitly declared nominal processing topology;not proof of actual cuts or conservation',collision='Every supplied geom collision-enabled;PAD0;no global appliance/guard exclusions;static mounts only named mating faces;own articulated neighbors require factual OEM/fixture adjacency audit'),module=dict(footprint_m=[1.45,.75],height_m=1.95,worktop_m=.92,primary_arm_required_workpiece_kg=3,EOAT_budget_kg=1.2),status=dict(geometry='primitive research model',motion='not_simulated',clearance='analytical opening design only,all-arm/path minima null',food_quality='not_qualified',physical_trials='not_run_user_decision'),robot=dict(model='UR5e',payload_rating_kg=5,reach_m=.85,body_mass_kg=20.7,mount_world=dict(position_m=[0,.674,1.34],quaternion_wxyz=[math.sqrt(.5),math.sqrt(.5),0,0]),mount_axis_world=[0,-1,0],gravity_world_m_s2=[0,0,-9.81],OEM_model_ref='sim/r04/integrator/sources/menagerie/universal_robots_ur5e/ur5e.xml',accepted_geometry_context='Use R04/R05 audited full arm geometry including restored base hull;do not interpret Menagerie simplified collision shapes as a new exemption',rated_envelope='Recompute each joint maximum static torque with OEM rated payload and allowed CoM in this new wall mount;R04 numeric denominators not transferable',brakes='OEM power-loss holding in this mounting sufficient documentary basis;actual controller gravity settings and slight settling still assessed',payload_status='3kg external+1.2kg EOAT=4.2kg proposed;actual CoM and inertias must pass chart and mounted envelope;not a task payload witness'),bodies=bs,support_faces=supports,grasp_handles=handles,appliance_openings=[dict(id='wash_opening',body='wash_basin',center_world_m=[-.49,.49,1.15],shape='rectangle',clear_size_m=[.336,.296],approach_axis_world=[0,0,-1],lid='wash_lid',measurement_status='specified custom geometry'),dict(id='cell_portal',body='process_cell',center_world_m=[.45,.330,1.11],shape='rectangle',clear_size_m=[.33,.26],approach_axis_world=[0,1,0],support_seating_axis_world=[0,0,-1],shutter='cell_door',measurement_status='specified custom geometry;powered actions only afterarmwithdrawal'),dict(id='greens_output',body='enclosure',center_world_m=[-.721,.49,1.13],shape='rectangle',clear_size_m=[.33,.30],approach_axis_world=[1,0,0],gate='greens_output_gate',measurement_status='human output after stop only')],approach_poses=[dict(id='wash_stage',position_m=[-.49,.32,1.31],quaternion_wxyz=IDENTITY,clearance_verdict=None),dict(id='cell_stage',position_m=[.45,.235,1.10],quaternion_wxyz=IDENTITY,clearance_verdict=None),dict(id='central_stage',position_m=[0,.28,1.28],quaternion_wxyz=IDENTITY,clearance_verdict=None)],intended_contacts=contacts,force_cases=FORCES,products=PRODUCTS,container_system=dict(outer='GN1/4',outer_outline_m=[.265,.163,.1],basket_custom_m=[.255,.153,.065],keyed_total_outline_m=[.285,.223,.145],mesh_aperture_m=.002,lid='captively hinged,detent,water ingress tolerable but no raw contamination retained after final rinse',latch='positive metal pan/insert capture;proof150N/15Nm;no food squeeze to increase grip',stacking='Plain GN pans nest for cleaning only;key collars andlids prevent loaded nesting;no stacking inside active meal',drainage='Station lift leaves food above dirty water,suction drain from solid outerpan,fresh wash pan;do not carry accumulated wash water',materials='Grade-documented304/316 stainless,food-contact POM andapproved silicone;no food-pathFDM',reference_loaded_assembly_max_kg=1.63),event_file='events_A.json',persistent_boundary_state_file='state_ledger_A.json',food_topology_file='food_catalog.json',planned_meal_events=len(events),full_scene_checks=dict(accepted_paths=0,actual_verified_time_min=None,robot_gap_min_m=None,held_gap_min_m=None),contact_policy=dict(window_kinds=['grasp_release_support','working_stroke'],support_window_max_m=.05,stop_permission_at_gap_m=.005,straight_axis_and_constant_orientation=True,working_permission_on_nonworking_paths=False,work_window_object_support_must_match=True,no_entire_fixture_exemption=True,wall_mount_exception='only explicit mating faces;if no wall rail in this concept do not invent wall wildcard'),integrator_obligations=['Bind every planned ownership endpoint to continuous object poses;no teleportation','Expand every machine substep,including jaw,lid,clamp,lift,pusher,food splitting andscrap drop','Instantiate full OEM arm and actual EOAT,geometry/inertias preserved','Use<=4mm all-point displacement bound,jaw/held parts included;normal10/5mm gaps;PAD0','>=60s per connection with restarts,staging,shortcutting;failed budgets remain failures','Replace unresolved Nemco/pusher fitting geometry with matched full union;current proxies earn no interface clearance admission','Inspect food and measure edible output/residue;nominal mass parcels do not qualify98%','Every contact is own named face;internal mechanism adjacency is not a whole-appliance exemption'])
    # Explicit EOAT geometry for integration; station-only XML does not install this without the OEM wrist.
    d['EOAT']=dict(mass_kg=1.2,com_local_m=[0,0,.08],inertia_kg_m2=[.005,.005,.002],parent='OEM_tool_flange',jaw_initial_gap_m=.07,jaw_travel_each_m=.04,geometry=[box('eoat_palm',[.10,.07,.065],[0,0,.0325]),box('eoat_key_left',[.012,.028,.035],[-.041,0,.09]),box('eoat_key_right',[.012,.028,.035],[.041,0,.09]),box('eoat_cup_floor',[.07,.05,.004],[0,.055,.11]),box('eoat_cup_back',[.07,.004,.025],[0,.080,.12])],food_cup='Built into sameEOAT,not a picked tool;passive2-5N pads and bottom/back support;wet retention/creaserub proof required',key_load_path='Metal wrist bridge bypasses low-moment OEM finger attachments;150N/15Nm proof required,not inferred from gripper advertisement')
    d['clearance_reserves']=[dict(id='cell_portal_lateral',minimum_nominal_gap_mm=22.5,gate_mm=5,reserve_mm=17.5,basis='(330-285)/2;centered carrier,nominal design only'),dict(id='cell_portal_vertical',minimum_nominal_gap_mm=57.5,gate_mm=5,reserve_mm=52.5,basis='(260-145)/2'),dict(id='wash_pan_side',minimum_nominal_gap_mm=35.5,gate_mm=5,reserve_mm=30.5,basis='(336-265)/2'),dict(id='wash_pan_foreaft',minimum_nominal_gap_mm=36.5,gate_mm=5,reserve_mm=31.5,basis='(296-223)/2'),dict(id='front_carrier_neighbor',minimum_nominal_gap_mm=65,gate_mm=5,reserve_mm=60,basis='350mm dock pitch minus285mm carrier/key collar width'),dict(id='right_cell_to_guard',minimum_nominal_gap_mm=38,gate_mm=10,reserve_mm=28,basis='guardinside x.717 minuscellright x.675 gives42mm;4mm installation tolerance deducted'),dict(id='arm_all_poses',minimum_nominal_gap_mm=None,gate_mm=10,reserve_mm=None,basis='No IK/path simulation;target>=20mm gap,>=10mm reserve for most poses')]
    d['robot']['mount_world']['position_m']=[0,.648,1.34]
    d['container_system']['reference_loaded_assembly_max_kg']=1.63
    d['grasp_handles'].append(dict(id='handle_clean_leaf_basket',object_id='clean_leaf_basket',geom='clean_leaf_key',pose_local=dict(position_m=[.085,-.121,.105],quaternion_wxyz=IDENTITY),jaw_axis_local=[1,0,0],approach_axis_local=[0,0,-1],retreat_axis_local=[0,0,1],grasp_land_m=[.06,.028,.016],key_design_force_N=150,key_design_moment_Nm=15,key_status='proof_required',combined_mass_kg=.646))
    d['intended_contacts'].append(dict(id='grasp_clean_leaf_key',kind='grasp_release_support',object_id='clean_leaf_basket',support_id='eoat_key_capture',object_geoms=['clean_leaf_key'],support_geoms=['eoat_key_left','eoat_key_right'],activation='Only own clean-basket key capture and retained grasp',window=dict(max_length_m=.05,axis_local=[0,0,-1],straight=True,ends_at_gap_m=.005),non_working_paths_may_use=True))
    d['intended_contacts'].append(dict(id='arm_mount_mating',kind='grasp_release_support',object_id='UR5e_base',support_id='robot_pedestal',object_geoms=['OEM_base_mating_face_only'],support_geoms=['arm_mount_plate'],activation='Permanent structural mating faces only,world plane y=.648,opposite normals;no whole wall/base/plate exception',window=dict(max_length_m=0,axis_world=[0,-1,0],straight=True,ends_at_gap_m=.005),non_working_paths_may_use=False))
    for i in range(1,7):
        d['intended_contacts'].append(dict(id=f'leaf_{i}_cup_capture',kind='grasp_release_support',object_id=f'leaf_{i}',support_id='arm_food_cup',object_geoms=[f'leaf_{i}_geom'],support_geoms=['eoat_cup_floor','eoat_cup_back'],activation='Own retained bottom/back support while this leaf is held;low-force pads;not permission for brush/tool contact on transit',window=dict(max_length_m=.05,axis_world=[0,0,1],straight=True,ends_at_gap_m=.005),non_working_paths_may_use=True))
    d['interface_limits']=['Food group initial geometries and cut-piece boxes are explicit conservative proxies.Continuous topology transitions and material distribution have no execution witness.','Front door is a single interlocked output/access guard;person remains outside during active operation.','Shared cell purchased wedger fittings remain conservative proxy geometry;cutter modes must be physically registered before carrying food into the cell.']
    d['utilities']=dict(power=dict(feed_voltage_V=[220,240],household_feed_A=13,planned_connected_W=1100,arm_and_controller_allowance_W=500,process_drives_allowance_W=350,wash_allowance_W=120,control_vision_allowance_W=80,lighting_misc_allowance_W=50,pf_assumed=.8,current_A_at230V=round(1100/(230*.8),2),status='Load allowance,inrush/leakage/cable ratings require integrator calculation',track_location='power_track;dry splash shielded,PE,RCD',restart='Manual reset then distinctstart;no automatic resume after power,data or guard event'),water=dict(cold_inlet_thread='G3/4 dishwasher-style adapter',regulated_flow_L_min=6,basin_working_volume_L=6,minimum_freeboard_m=.04,air_break='Above basin flood rim1.15m,backflow prevention selection by installer',drain='40mm trapped gravity household hookup;lift-out2mm scrap screen,no peel to drain',basin_suction='Remove dirty water from outerpan after120mm insertlift;rinse pan before lowering clean food',leak='tray,level,overflow sensor and normally-closed inlet valve'))
    d['mechanism_substeps']=dict(reference_event_expansion='events_A.json substeps;each is a required mechanism state/motion obligation,not a verified path',state_machine=dict(loading='Blade/pusher caught,clamps open,shutter open,food supported,arm carries pan then lowers20mm on own lands;no sliding guide contacts',start='Pan/insert retained,lid/doorclosed,arm withdrawn into checked stagingpose,all inactive tools parked;then drives enable',work='Only named food/tool work pair active;reaction transmitted through fixed support andframe',unload='Every drive stopped and caught;tools clear food,clamps open,shutter open;grasp key,straight lift<=50mm until5mm gap;then general checked transport',wash='Lift own insert before removing dirtywater;do not carry6L water;all lid and lift strokes checked',failure='Stop and retain;food remains in current unique owner;partial meal flagged,never clone food to retry'))
    # The complete registry resolves named future food and wrist geometries without pretending they exist simultaneously.
    catalog=food_catalog()
    d['food_catalog']=catalog
    d['runtime_object_registry']={b['id']:dict(kind=b['category'],body_ref=b['id'],geometry_ids=[g['id'] for g in b['geometry']]) for b in bs}
    for name,geoms in [('eoat_key_capture',['eoat_key_left','eoat_key_right']),('arm_food_cup',['eoat_cup_floor','eoat_cup_back']),('UR5e_base',['OEM_base_mating_face_only'])]:
        d['runtime_object_registry'][name]=dict(kind='external_OEM_or_EOAT_binding',geometry_ids=geoms)
    for p,c in catalog.items():
        for part in c.get('leaves',[])+c['pieces']:
            d['runtime_object_registry'][part['id']]=dict(kind='food_after_explicit_split',mass_kg=part['mass_kg'],geometry_ids=[g['id'] for g in part['geometry']],geometry=part['geometry'],activation='Only after corresponding source token is retired;conserve measured mass;no concurrent duplicate source/part')
        for part in c['pieces']:
            carrier='clean_leaf_basket' if p=='bok_choy' else 'carrier_'+p
            face='clean_basket_face' if p=='bok_choy' else 'basket_floor_face_'+p
            d['intended_contacts'].append(dict(id=part['id']+'_own_receiver',kind='grasp_release_support',object_id=part['id'],support_id=carrier,object_geoms=[g['id'] for g in part['geometry']],support_faces=[face],activation='Only this conserved child piece on its own receiver floor;piece pose must be continuous from its cut,not spawned in bowl',window=dict(max_length_m=.05,axis_world=[0,0,1],straight=True,ends_at_gap_m=.005),non_working_paths_may_use=True))
        for w in c['waste']:
            d['runtime_object_registry'][w['id']]=dict(kind='captured_waste_mass_token',mass_kg=w['mass_kg'],geometry_ids=[],physical_geometry='Unresolved measured scraps;capture/bin trajectories still required')
    d['mechanism_state_contract']=dict(state_variables=['arm_joint_q','jaw_q','held_object_id','container_world_poses','insert_latch_and_lift','each_pan_lid_q','wash_lid_q','water_volume_and_valves','cell_door_q','mode_selector_q','blade_q_and_catch','wedger_pusher_q_and_catch','eyer_X_Z_q','root_rotation_q','clamp_q','food_token_owner_and_mass','waste_token_owner_and_mass','guard_locks','drive_enable_and_brake'],initial_values='body joint initial fields plus state_ledger_A[0];no unstated reset',event_boundary_states='state_ledger_A.json;macro internal states are enumerated obligations,not a witnessed trajectory',new_food_body_spawn='Source geometry retired only as conserved child pieces and scraps gain continuous poses at actual cutting plane;no remote spawn in output bowl',whole_food_contact_limit='Every declared50mm window must be checked against real work/approach travel;full60mm tomato/70mm potato work may require a different tool sequence.No permission by splitting a long generic transit into artificial work windows.')
    d['EOAT']['jaw_joints']=[dict(id='eoat_left_jaw',geometry_ids=['eoat_key_left'],axis_local=[1,0,0],range_m=[0,.04],initial_m=0),dict(id='eoat_right_jaw',geometry_ids=['eoat_key_right'],axis_local=[-1,0,0],range_m=[0,.04],initial_m=0)]
    d['EOAT']['capture_command_m_each']=.005
    d['EOAT']['key_capture_frame_tool']=dict(position_m=[0,0,.09],quaternion_wxyz=[0,1,0,0],instruction='Tool+Z points downward for top key approach;solve world_tool=world_handle*inverse(tool_capture).Do not equate handle frame with flange pose.')
    d['EOAT']['leaf_support_frame_tool']=dict(position_m=[0,.055,.112],quaternion_wxyz=IDENTITY,normal_local=[0,0,1],instruction='Bottom support must face upward under gravity;leaf-to-cup pose measured,not inherited from key-capture orientation.')
    d['acceptance']=dict(pose_translation_m=.005,pose_rotation_degrees=3,robot_environment_gap_m=.01,arm_arm_gap_m=.01,gripper_held_environment_gap_m=.005,PAD=0,mu=.5,SF=1.5,key_force_N=150,key_moment_Nm=15,point_displacement_m_max=.004,planner_budget_s_per_connection_min=60,planner_restarts=True,shortcutting=True,staging=True)
    d['station_seating_poses_world']=[dict(object_id='output_'+p,support='wash_lift',position_m=[-.49,.49,.953],quaternion_wxyz=IDENTITY,placement_status='Design endpoint only;lid/cargo clearances unverified') for p in PRODUCTS]+[dict(object_id='output_'+p,support='process_cell',position_m=[.45,.505,.972],quaternion_wxyz=IDENTITY,placement_status='Design endpoint only;mode tools parked;all internal loading paths unresolved') for p in PRODUCTS]+[dict(object_id='clean_leaf_basket',support='process_cell',position_m=[.45,.505,.972],quaternion_wxyz=IDENTITY,placement_status='Design endpoint only;food arrangement unverified')]
    d['container_system']['lid_transport']='All transported kits closed:145mm declared travel outline.Station-open lids can reach~263mm abovepan bottom;their entire hinge sweep must be checked and is not covered by closed-outline portal reserve.'
    d['container_system']['clean_basket_key_offset_m']=[.085,-.121,.105]
    d['container_system']['clean_basket_nesting']='Clean inner basket255x153x65 replaces original empty insert in bok outerpan;original insert remains basin-supported as a separate conserved object;offset key avoids coincident front keys.'
    d['waste_interface']=dict(port_center_world_m=[.56,.53,.93],cutout_full_m=[.054,.16],chute_internal_m=[.05,.156],chute_top_z_m=.93,chute_bottom_z_m=.485,receiver='waste_bin',gate='waste_drop_gate',ledger_name='appliances.waste_bin_lid refers to this scrap-drop gate,not an unmodelled rotating bin lid',limitations='Cell support lands partly cover aperture;actual retained scraps must use the remaining measured passage or a redesigned support.Never teleport root disk/facet into bin;exact scrap solids/paths unresolved.')
    for p in ['carrot','potato','tomato']:
        force='tomato_wipe' if p=='tomato' else 'root_brush'
        d['intended_contacts'].append(dict(id=p+'_wash_work',kind='working_stroke',object_id='food_'+p,support_id='wash_brush',object_geoms=['food_'+p],support_geoms=['wash_brush_cylinder'],force_id=force,activation='Only supported all-surface wash substroke of this named food;water controls/appliance fixture act while arm detached;not during transport',window=dict(max_length_m=.05,axis_world=[0,1,0],straight=True,ends_at_gap_m=.005),non_working_paths_may_use=False))
    for p in ['carrot','potato']:
        d['intended_contacts'].append(dict(id=p+'_rotary_support',kind='grasp_release_support',object_id='food_'+p,support_id='root_roller',object_geoms=['food_'+p],support_geoms=['root_roller_geom'],activation='Own supported root in selected peeling mode only;support acquired/released through straight<=50mm normal window;not on arm transport',window=dict(max_length_m=.05,axis_world=[0,0,1],straight=True,ends_at_gap_m=.005),non_working_paths_may_use=True))
    for food in ['food_'+p for p in PRODUCTS]+[f'leaf_{i}' for i in range(1,7)]:
        geom=food if food.startswith('food_') else food+'_geom'
        for side,axis in [('left',[1,0,0]),('right',[-1,0,0])]:
            d['intended_contacts'].append(dict(id=food+'_own_'+side+'_clamp',kind='grasp_release_support',object_id=food,support_id='cell_clamp_'+side,object_geoms=[geom],support_geoms=['cell_clamp_pad_'+side],activation='Only own appliance-supported food and actual clamp retention in named mode;inactive clamp contacts forbidden;never inherited by arm-held transit',window=dict(max_length_m=.05,axis_world=axis,straight=True,ends_at_gap_m=.005),non_working_paths_may_use=True))
    dump('stations.json',d)
    export_station_xml(d)

def export_station_xml(d):
    """Direct primitive-to-MuJoCo export, initialization only; not a simulated acceptance."""
    r=Element('mujoco',model='r06_station_primitives')
    SubElement(r,'compiler',angle='radian',autolimits='true')
    SubElement(r,'option',gravity='0 0 -9.81',timestep='.002')
    defaults=SubElement(r,'default');SubElement(defaults,'geom',margin='0',friction='.5 .005 .0001')
    world=SubElement(r,'worldbody');SubElement(world,'geom',name='floor',type='box',pos='0 .375 -.025',size='1 1 .025',rgba='.25 .28 .30 1')
    nodes={'world':world};qinit={};worldposes={}
    def fmt(x):return ' '.join(f'{v:.10g}' for v in x)
    # Free objects cannot have a non-world parent in MuJoCo. Their initial transform is composed explicitly.
    for b in d['bodies']:
        parent=b['parent'];pos=b['pose']['position_m'];q=b['pose']['quaternion_wxyz'];j=b.get('joint')
        if j and j['type']=='free':
            assert parent=='world'
        node=SubElement(nodes[parent],'body',name=b['id'],pos=fmt(pos),quat=fmt(q));nodes[b['id']]=node
        SubElement(node,'inertial',pos=fmt(b['com_local_m']),mass=str(b['mass_kg']),diaginertia=fmt(b['inertia_kg_m2']))
        if j:
            if j['type']=='free':SubElement(node,'freejoint',name=b['id']+'_joint')
            else:
                SubElement(node,'joint',name=b['id']+'_joint',type=j['type'],axis=fmt(j['axis']),range=fmt(j['range']),damping='1')
                qinit[b['id']+'_joint']=j['initial']
        for g in b['geometry']:
            args=dict(name=g['id'],type=g['type'],pos=fmt(g['pose']['position_m']),quat=fmt(g['pose']['quaternion_wxyz']),rgba=fmt(g['rgba']))
            args['size']=fmt([v/2 for v in g['size_m']]) if g['type']=='box' else fmt([g['radius_m'],g['height_m']/2])
            SubElement(node,'geom',**args)
    SubElement(world,'site',name='arm_mount',pos=fmt(d['robot']['mount_world']['position_m']),quat=fmt(d['robot']['mount_world']['quaternion_wxyz']),size='.01',rgba='1 0 1 1')
    ElementTree(r).write(RESULTS/'station_primitives.xml',encoding='utf-8',xml_declaration=True)
    dump('initial_joints.json',qinit)

def font(size=21):
    for path in ['C:/Windows/Fonts/arial.ttf','C:/Windows/Fonts/segoeui.ttf']:
        if Path(path).exists():return ImageFont.truetype(path,size)
    return ImageFont.load_default()

def drawings():
    concepts=json.loads((RESULTS/'concepts.json').read_text(encoding='utf-8'))['concepts']
    for c in concepts:
        im=Image.new('RGB',(1500,1080),'#f9fafb');dr=ImageDraw.Draw(im)
        dr.text((45,25),c['id']+' | DIMENSIONED CONCEPT PLAN',font=font(29),fill='#123149')
        dr.text((45,65),'Research design. All dimensions mm. No IK/path/food-quality pass.',font=font(20),fill='#495a68')
        scale=780;ox=740;oy=730
        def xy(x,y):return (ox+x*scale,oy-y*scale)
        def rect(x,y,w,h,color,label):
            x1,y1=xy(x-w/2,y+h/2);x2,y2=xy(x+w/2,y-h/2)
            dr.rectangle([x1,y1,x2,y2],fill=color,outline='#34485c',width=3)
            dr.text((x1+8,y1+8),label,font=font(17),fill='#17334b')
        wid=c['footprint_m'][0];rect(0,.375,wid,.75,'#edf1f3','')
        for l in c['station_layout']:
            if 'center_m' in l and 'size_m' in l:
                label=l['id']+'\n'+str(round(l['size_m'][0]*1000))+' x '+str(round(l['size_m'][1]*1000))
                rect(*l['center_m'],*l['size_m'],'#b8e0de' if 'wash' in l['id'] else '#d6ddec',label)
        if c['id']=='cassette_fixed':
            rect(-.20,.48,.09,.14,'#ffe5aa','Tool\nnest')
            for p,x in zip(['CARROT','POTATO','BOK INPUT','TOMATO'],[-.525,-.175,.175,.525]):rect(x,.20,.285,.235,'#fae7c6',p+'\n285 x 235 dock')
            dr.line([xy(-.721,.325),xy(-.721,.655)],fill='#e87928',width=10)
            dr.text((30,340),'Greens outlet\nleft side\n330x300 clear\nstopped only',font=font(18),fill='#9d4914')
            dr.text((290,823),'Ports: whole GN assemblies are loaded raw, washed, then delivered.\nGreens finish in the basin pan; its empty source insert stays supported.',font=font(19),fill='#34485c')
        else:
            for p,x in zip(['C','P','G','T'],[-.525,-.175,.175,.525]):rect(x,.13,.285,.20,'#fae7c6',p+' GN port')
            dr.text((285,823),'Rotato fits INSIDE the finish-cell volume as a mutually exclusive insert.\nLarge-hopper/pusher profiles remain unresolved; no passed loading route.',font=font(19),fill='#34485c')
        bx,by=xy(0,c['arm_mount']['position_m'][1]);dr.ellipse([bx-65,by-45,bx+65,by+45],fill='#5d84a5',outline='#163d5a',width=3)
        dr.text((bx-65,by-30),'ARM\nMOUNT',font=font(16),fill='white')
        if c['rail']:
            a=xy(-.425,.675);b=xy(.425,.675);dr.line([a,b],fill='#277ab5',width=8)
            dr.text((435,112),'850mm rail stroke;1200mm beam;spring brake',font=font(19),fill='#175b83')
        else:dr.text((435,112),'Fixed UR5e wall mount z=1340;no rail',font=font(20),fill='#175b83')
        # Overall dimension arrows.
        x1,y=xy(-wid/2,-.05);x2,_=xy(wid/2,-.05)
        dr.line([(x1,y),(x2,y)],fill='#273d4e',width=2)
        for x in [x1,x2]:dr.line([(x,y-7),(x,y+7)],fill='#273d4e',width=2)
        dr.text(((x1+x2)/2-100,y+8),f'{round(wid*1000)} overall width',font=font(21),fill='#17334b')
        dr.text((1350,395),'750\ndepth',font=font(21),fill='#17334b')
        dr.text((590,745),'FRONT / HUMAN OUTSIDE DURING RUN',font=font(19),fill='#5a4535')
        dr.text((290,903),f"Arm count {c['arms']} | supervisory events {c['event_count']} | plan {c['estimated_minutes']:.0f}min | CNY{c['estimated_cny']:,.0f} incl15%reserve",font=font(20),fill='#16334b')
        dr.text((290,942),'Worktop920;enclosure1950 high. Water/drain and one household feed at rear.\n20mm target robot gap;15mm target held gap. Opening reserves are not arm clearances.',font=font(19),fill='#34485c')
        im.save(HERE/'plans'/f"{c['id']}_plan.png")
    # Elevation for selected concept adds actual depth/height information.
    im=Image.new('RGB',(1500,950),'#f9fafb');dr=ImageDraw.Draw(im)
    dr.text((50,30),'cassette_fixed | FRONT ELEVATION + INTERFACES',font=font(29),fill='#123149')
    sx=700;ox=720;floor=820
    def pt(x,z):return (ox+x*sx,floor-z*330)
    def r(x,z,w,h,col,label):
        a=pt(x-w/2,z+h/2);b=pt(x+w/2,z-h/2);dr.rectangle([a,b],fill=col,outline='#34485c',width=3);dr.text((a[0]+8,a[1]+8),label,font=font(18),fill='#16334b')
    r(0,.91,1.45,.02,'#a3acb2','');r(-.49,1.04,.36,.22,'#a8d4d1','Wash basin\n360x320x220');r(.45,1.19,.45,.52,'#c8d0e4','Shared guarded cell\n450x350x520');r(0,1.34,.18,.18,'#79a0bc','Mount')
    for p,x in zip(['C','P','G','T'],[-.525,-.175,.175,.525]):r(x,1.005,.265,.1,'#f6dfb2',p)
    r(.46,.435,.30,.27,'#ceb6a9','Waste bin');r(0,.45,.32,.35,'#c6ced3','Dry control')
    for x in [-.72,.72]:dr.line([pt(x,.04),pt(x,1.95)],fill='#9aafb9',width=4)
    dr.line([pt(-.725,1.95),pt(.725,1.95)],fill='#9aafb9',width=4)
    dr.text((1250,390),'1950\nmax height',font=font(23),fill='#16334b')
    dr.text((50,140),'Arm not drawn.\nFull OEM model\nrequired; reach\nand swept volume\nunverified.',font=font(18),fill='#596c79')
    dr.text((225,845),'Floor z0 | Worktop top920 | Bowl bottom954 | Washer rim1150 | Cell top1450 | Fixed mount1340',font=font(20),fill='#34485c')
    im.save(HERE/'plans'/'cassette_fixed_elevation.png')

def audit():
    d=json.loads((RESULTS/'stations.json').read_text(encoding='utf-8'));c=json.loads((RESULTS/'concepts.json').read_text(encoding='utf-8'));e=json.loads((RESULTS/'events_A.json').read_text(encoding='utf-8'));states=json.loads((RESULTS/'state_ledger_A.json').read_text(encoding='utf-8'))
    checks=[]
    def ok(name,test,detail=''):
        checks.append(dict(check=name,pass_=bool(test),detail=detail))
        if not test:raise AssertionError(name+':'+str(detail))
    ok('A event count',len(e)==79,str(len(e)))
    ok('A boundary state count',len(states)==80)
    ok('Nominal food mass at every boundary',all(abs(s.get('total_food_mass_kg',.57)-.57)<1e-9 for s in states))
    ok('No arm-held object at output unlock',states[-1]['arm']['held'] is None)
    ok('Four output bowls',len(states[-1]['accepted_bowls'])==4)
    ids={b['id'] for b in d['bodies']};gids={g['id'] for b in d['bodies'] for g in b['geometry']}
    ok('Unique body IDs',len(ids)==len(d['bodies']))
    ok('Unique geom IDs',len(gids)==sum(len(b['geometry']) for b in d['bodies']))
    ok('Parents resolve',all(b['parent']=='world' or b['parent'] in ids for b in d['bodies']))
    ok('Primitives dimensioned',all((g['type']=='box' and all(x>0 for x in g['size_m'])) or (g['type']=='cylinder' and g['radius_m']>0 and g['height_m']>0) for b in d['bodies'] for g in b['geometry']))
    ok('PAD0 unchanged',c['common']['acceptance']['PAD']==0)
    ok('Contact kinds explicit',all(x['kind'] in ['grasp_release_support','working_stroke'] for x in d['intended_contacts']))
    ok('Own contact identities explicit',all(x['object_id'] and x['support_id'] for x in d['intended_contacts']))
    registry=d['runtime_object_registry'];known_geoms={g for x in registry.values() for g in x['geometry_ids']}
    ok('Contact object/support IDs resolve',all(x['object_id'] in registry and x['support_id'] in registry for x in d['intended_contacts']))
    ok('Contact geometry IDs resolve',all(g in known_geoms for x in d['intended_contacts'] for g in x.get('object_geoms',[])+x.get('support_geoms',[])))
    face_ids={s['id'] for s in d['support_faces']}
    ok('Support face IDs resolve',all(f in face_ids for x in d['intended_contacts'] for f in x.get('support_faces',[])))
    eb=json.loads((RESULTS/'events_B.json').read_text(encoding='utf-8'));sb=json.loads((RESULTS/'state_ledger_B.json').read_text(encoding='utf-8'))
    ok('B ordered event count',len(eb)==93)
    ok('B unique ownership boundary count',len(sb)==94 and sb[-1]['arm']['held'] is None)
    ok('B nominal mass at every boundary',all(abs(s.get('total_food_mass_kg',.57)-.57)<1e-9 for s in sb))
    ok('Time estimate matches event sum',c['concepts'][0]['estimated_timing']['resource_scheduled_nominal_seconds']==sum(x['estimated_s'] for x in e))
    ok('No working permission on transit',all(x['non_working_paths_may_use'] is False for x in d['intended_contacts'] if x['kind']=='working_stroke'))
    ok('Windows <=50mm',all(x['window']['max_length_m']<=.05 for x in d['intended_contacts']))
    ok('No claimed paths',d['full_scene_checks']['accepted_paths']==0)
    for concept in c['concepts']:
        ok('BOM '+concept['id'],abs(sum(x['line_cny'] for x in concept['bom'])-concept['subtotal_cny'])<1e-8)
        ok('One home safety package '+concept['id'],sum(1 for x in concept['bom'] if 'ONE home safety' in x['item'])==1)
        ok('Fits module '+concept['id'],1.2<=concept['footprint_m'][0]<=1.5 and .6<=concept['footprint_m'][1]<=.75 and concept['height_m']<=2)
    for path in (HERE/'plans').glob('*.png'):
        with Image.open(path) as im:ok('Image<=1600 '+path.name,max(im.size)<=1600,str(im.size))
    import mujoco
    model=mujoco.MjModel.from_xml_path(str(RESULTS/'station_primitives.xml'))
    data=mujoco.MjData(model)
    qs=json.loads((RESULTS/'initial_joints.json').read_text(encoding='utf-8'))
    for name,value in qs.items():
        ji=mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_JOINT,name)
        data.qpos[model.jnt_qposadr[ji]]=value
    # mj_forward only constructs kinematic transforms; no integration,collision acceptance or planner run.
    mujoco.mj_forward(model,data)
    ok('Direct station XML compiles',model.ngeom==len(gids)+1,str(model.ngeom)+'geoms,arm deliberately external')
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'DECISIONS.md',ROOT/'inputs/cook_ref.md',ROOT/'inputs/keypose_cook.md',ROOT/'posts/r05/reviewer.md',ROOT/'posts/r04/reviewer.md',ROOT/'posts/r02/tools.md',ROOT/'inputs/prep_checker.py',ROOT/'sim/r04/integrator/reference.py']}
    out=dict(date=DATE,checks=checks,passed=len(checks),scope='Artifact/nominal ownership/arithmetical audit and station XML compilation only;no path,food quality or safety pass',input_sha256=hashes,model_counts=dict(bodies=model.nbody,geoms=model.ngeom,joints=model.njnt),bytes_under_role=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file()),exceptions='ConceptB hopper geometry and transaction insertion unresolved,clearly marked;neither concept admitted')
    (HERE/'audit'/'validation.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
    print(json.dumps(dict(artifact_checks=len(checks),events_A=len(e),events_B=93,est_min=c['concepts'][0]['estimated_minutes'],est_cny=c['concepts'][0]['estimated_cny'],xml_geoms=model.ngeom,role_bytes=out['bytes_under_role'])))

if __name__=='__main__':main()
