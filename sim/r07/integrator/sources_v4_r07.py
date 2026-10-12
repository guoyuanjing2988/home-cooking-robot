"""Public appliance evidence, no supplier contact or procurement."""
import urllib.request,json,hashlib,time
from pathlib import Path
H=Path(__file__).resolve().parent;D=H/'sources/appliances_v4';D.mkdir(exist_ok=True)
sources=[
 ('sammic_m5','https://sammic.com/en/product/m-5','html'),
 ('sammic_m5_spec','https://www.sammic.com.au/wp-content/uploads/2023/SPECSHEET/M-5.pdf','pdf'),
 ('sammic_manual','https://www.sammic.com.au/wp-content/uploads/2023/INSTRUCTIONS/PI-30.pdf','pdf'),
 ('rotato_manual','https://www.starfrit.com/media/pdf/instrbooklet--User-manual-093209002BLCK-en2.pdf','pdf'),
 ('rotato_buyable','https://www.starfrit.com/en/starfrit-electric-rotato-express','html'),
 ('nemco_manual','https://nemco.com/wp-content/uploads/2025/07/55550_Easy_Wedger_4-2012.pdf','pdf'),
 ('nemco_dimensions','https://nemco.com/wp-content/uploads/2025/06/c9bb50b8-9645-4786-b5ff-fd07fe8a7881.pdf','pdf'),
]
rows=[]
for name,url,ext in sources:
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=20) as response:content=response.read();status=response.status
  valid=ext!='pdf' or content.startswith(b'%PDF')
  path=D/(name+'.'+(ext if valid else 'blocked.html'));path.write_bytes(content)
  rows.append(dict(id=name,url=url,path=str(path.relative_to(H)),sha256=hashlib.sha256(content).hexdigest(),valid_document=valid,status=status))
 except Exception as e:rows.append(dict(id=name,url=url,error=str(e),valid_document=False))
 print(name,rows[-1].get('valid_document'),flush=True)
 (D/'manifest.json').write_text(json.dumps(rows,indent=2))
facts=dict(schema='r07.v4.commodity-screen',source_manifest='sources/appliances_v4/manifest.json',models=[
 dict(model='Sammic M-5',dimensions_mm=[333,367,490],W=300,kg=15.5,capacity_kg=5,timer_s=[0,360],source=sources[0][1],buyable='https://www.sammicspares.com/buy-machines/buy-dynamic-preparation',benefit='OEM explicitly supports carrots as well as potatoes; removes repeated hand peel/index cycles.',blockers=['490mm closed height leaves10mm below cabinet','full exterior cover overlaps cable band in left bay; this is a conservative cover rejection, not an exact casting impossibility','far-right333mm counter bay has poor long-reach access','lid/interior and single-small-vegetable peel loss/depth not qualified']),
 dict(model='Starfrit Rotato Express093209',manufacturer=sources[4][1],manual=sources[3][1],dimension_listing='https://www.odpbusiness.com/a/products/983762/Starfrit-Rotato-Express/',listing_dimensions_in=[6,6,10.5],dimension_status='First-party distributor product entry; axis ordering ambiguous, matched Canada/US suffix not certified. No exact OEM CAD claim.',guard_design_reservation_mm=[300,300,350],guard_status='New full enclosure reservation exceeds every supplier dimension in any ordering; includes motor and moving holder reservation but no invented robot-access opening.',source_power='6V adapter, OEM; nameplate input W not established',benefit='Lower guarded reservation clears fixed chain vertically.',blockers=['OEM maximum140mm food requires pre-halving160mm carrot','carrot suitability/depth/loss not demonstrated','manual lowering holder and rocking extraction still need robot interfaces','prototype guard/interlock and stops not qualified']),
 dict(model='Nemco55550-8 Easy Wedger',dimensions_mm=[203.2,203.2,482.6],source=sources[6][1],manual=sources[5][1],benefit='Real eight-section tomato blade/pusher mechanism.',selection='Screened, not installed: manual exposed sharp blades need extra guard and powered pusher. Full19inch height plus guard/loading competes with band. Existing full guarded auxiliary cutter retained for tomato and greens.',process_force_N=636.365,force_basis='Inherited sourced tomato wedge design load unchanged; OEM marketing does not establish drive force.'),
 dict(model='Breville BFP610',source='https://www.breville.com/en-nz/product/bfp610',manual='https://assets.breville.com/BFP610/BFP610_ANZ_WEB_IB_A23_LR.pdf',full_retained_cover_mm=[395,295,395],selection='Retain batch household processor, shift whole unit back55mm from prior near-edge layout.',blockers=['matched chute/lid/pusher/disc geometry remains unresolved','stopped disc removal and separate batch unloading cannot be replaced by R211 continuous-ejection events','feed force and power nameplate unqualified']),
 dict(model='Robot-Coupe R211 XL',dimensions_mm=[245,385,510],W=550,source='https://www.robot-coupe.com/australia/en_AU/p/food-processors-r-211-xl/18401',selection='Screened, not installed. All cabinet-free X strips coincide with sink or protected stove; existing kitchen/exclusion kept.'),
 dict(model='HENDI229200',dimensions_mm=[620,525,787],source='https://www.hendi.eu/en/potato-peeler-5-kg-103894.html',selection='Rejected countertop candidate on closed height alone; larger revision802mm also fails.')],
 finished_product_acceptance='Unchanged JSON inherited from cook_ref. No appliance gets quality credit from marketing.',arms=dict(selected='UR5e principal + xArm6 helper comparison; full OEM meshes/inertias unchanged',principal_service_kg=3,principal_EOAT_kg=1.2,compact_comparison='L41 xArm6 principal;5kg nominal but long-offset curve prevents claiming3+1.2kg capability',xarm_source='https://www.ufactory.cc/wp-content/uploads/2023/05/xArm-User-Manual-V2.0.0.pdf',UR3e='3kg nominal excludes3kg plus any positive EOAT; helper-only candidate',UR3e_source='https://www.universal-robots.com/products/ur3e/',other_candidates='Prior research.json includes JAKA Zu5, EliteCS66, DobotCR5, AUBOi5 with public models. No matched mounted envelope added for these unselected alternatives.'))
(H/'results/research_v4.json').write_text(json.dumps(facts,indent=2))
