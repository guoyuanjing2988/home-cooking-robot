"""Consolidate evidence without changing submitted artifacts."""
from pathlib import Path
import json,hashlib,ast,math
H=Path(__file__).resolve().parent;ROOT=H.parents[2];I=H.parent/'integrator';O=H/'results';A=H/'audit'
def dump(n,v):(O/n).write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
before=json.loads((A/'source_hashes_before.json').read_text());changed=[]
for n,h in before.items():
 now=hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
 if now!=h:changed.append(n)
replay=json.loads((O/'reverify_all.json').read_text());convex=json.loads((O/'convex_geometry_crosscheck.json').read_text());parts=[p for ph in replay['phases'] for p in ph['parts']]
restored=[];unresolved=[]
for ph in replay['phases']:
 for p in ph['parts']:
  for row in p['rejected_claims']:
   proof=next((r for r in convex['clearance_discrepancies'] if r['stroke']==ph['phase']+'__'+p['stroke'] and r['k']==row['k']),None)
   if proof and proof['clearance_10mm_certified']:restored.append(dict(phase=ph['phase'],stroke=p['stroke'],k=row['k'],projection_lower_bound_mm=proof['separating_projection_lower_bound_mm']))
   else:unresolved.append(dict(phase=ph['phase'],stroke=p['stroke'],k=row['k']))
logical=[]
for i in range(1,28):
 q=f'Q{i:02d}';phs=[x for x in replay['phases'] if x['phase'].split('.')[0]==q];logical.append(dict(phase=q,ok=all(x['ok'] for x in phs)))
dump('review_summary.json',dict(logical_passed=sum(p['ok'] for p in logical),logical_total=27,instances_passed=sum(p['ok'] for p in replay['phases']),instances_total=len(replay['phases']),strokes_passed=sum(p['claimed']>0 for p in parts),strokes_total=len(parts),solver_starts=sum(p['starts'] for p in parts),solver_solutions=sum(p['claimed'] for p in parts),independently_verified_witnesses=sum(p['independently_verified'] for p in parts)+len(restored),poses_recomputed=sum(p['poses_recomputed'] for p in parts),restored_after_independent_convex_proof=restored,unresolved_witnesses=unresolved,logical=logical,motion='fail',cost_cny=467129.95,serial_planning_min=99.86,proceed=False,findings=12,numerical_caveat='Two positive-distmax libccd query false alarms were resolved using unchanged original vertex hulls and independent separating-projection certificates. Submitted20mm absence-of-contact lower bounds are nevertheless disproved. Static counts remain19/27, not a rigorous continuous-motion certificate.'))
force=[
 ('carrot_cut',2*67.59/31*35,'Primary slow transverse carrot data plus width scaling and2x margin'),
 ('potato_cut',2*61.49/47*70,'Primary slow transverse potato data plus width scaling and2x margin'),
 ('greens_cut',2*67.59/31*80,'Retained carrot-tissue proxy, unqualified for bok choy'),
 ('tomato_wedge',2*15/(math.pi*2**2)*4*70*.952,'Retained4mm probe-stress/blade-area proxy; unqualified wedger force'),
 ('peel_drag',1.5*1.68*25,'Carrot abstract resistance; potato transfer remains proxy'),
 ('peel_normal',1.5*1000*.005,'Design spring, requires calibration'),
 ('eye_core',2*67.59/31*12,'Retained carrot-width proxy; scoop free moment times10mm lever'),
 ('root_rub',1.5*1000*.006,'Design spring, requires calibration'),
 ('leaf_rub',1.5*400*.005,'Design spring, requires calibration'),
 ('tomato_rub',1.5*200*.005,'Design spring, requires calibration'),
 ('water_jet',1.5*1000*(.006/60)**2/(math.pi*.010**2/4),'rho Q squared/A;6L/min and10mm outlet assumptions'),
 ('drawer_insert',1.5*(.5*1.1*9.81+1.1*.3+2),'Coulomb/inertia/latch design assumptions'),
 ('handle_carry',.45,'Check acceleration N/kg; actual gravity separate'),
 ('leaf_separate',.1*.45,'Already detached leaf carry; no tearing force qualified'),
 ('cleanup_wipe',1.5*500*.005,'Design spring, requires calibration'),
 ('end_cup_preload',1.5*1000*.010,'Design spring, positive endstop reacts peeling'),
 ('machine_index',1.5*(.5*1.1*9.81+1.1*.3),'Coulomb/inertia design assumptions')]
dump('force_arithmetic.json',dict(models=[dict(id=n,check_value=v,basis=b) for n,v,b in force],note='Rounded hand force vectors retain the source magnitudes; this arithmetic is not a qualification of proxy force bounds. Tomato blade area uses the stated0.952mm assumption, not an independently measured Nemco cutting edge.'))
urls=[
 ('Robot-Coupe R211XL','https://www.robot-coupe.com/export/en/p/food-processors-r-211-xl/18401','OEM550W/1500rpm/13kg/245x385x510mm;87cm2 halfmoon and58mm inlet; lever-operated restart; continuous output'),
 ('Robot-Coupe5mm accessory','https://www.robot-coupe.com/nl/nl/p/schijvenverzameling-snijschijven-5-mm/18289','R211XL-compatible5mm Essential disc; current page references27087'),
 ('Nemco','https://nemco.com/catalog/easy-wedger/','55550-8,428-8 blade and55434 pusher; tomato use; no quantitative quality guarantee'),
 ('xArm specifications','https://docs.xarm.ufactory.cc/8.technical_specifications.html','5kg, public ranges, any-direction mount,500W supply provision; native84mm/30N gripper'),
 ('xArm safety','https://docs.xarm.ufactory.cc/1.safety.html','Internal brakes retain power-loss pose; warns of slight fall and integration responsibility'),
 ('xArm payload PDF','https://www.ufactory.cc/wp-content/uploads/2023/05/xArm-User-Manual-V2.0.0.pdf','Printedp237 chart visually inspected locally, fetched by web too'),
 ('UR5e manual','https://www.universal-robots.com/manuals/EN/PDF/SW5_21/user-manual-UR5e-PDF_online/710-965-00_UR5e_User_Manual_en_Global.pdf','Web fetch size-limit; supplied PDF visually/text inspected: arbitrary tilt, payload curve, powered-off brakes; not publicly fetched anew by reviewer'),
 ('UR cable','https://www.universal-robots.com/manuals/EN/HTML/SW10_14/Content/prod-cable/cable-product-description.htm','Cable-specific dimensions/bend guidance, assembly routing still open'),
 ('Miki brake','https://www.mikipulley.co.jp/en/electromagnetic-clutches-brakes/offbrakes/holding/bxr-le','Spring-applied3.20Nm; hold-in/release values60/20ms are not measured integration timing'),
 ('Eubiq track','https://eubiq.com/product/e-track/','13A/IP40; exact modeled70x28mm section and installed adapter SKU not established'),
 ('Slow cut primary study','https://iseki-food-ejournal.com/article/69/pdf','20-40mm/min,0.952mm blade,carrot67.59N,potato61.49N data; not high-speed food-force'),
 ('Carrot peel abstract','https://www.qikan.com.cn/article/5dd020251220.html','Direct page unavailable; publisher-indexed abstract found via search:1.68N/mm,16-32N,90.72percent peeling; not complete potato validation'),
 ('Tomato firmness primary record','https://www.sciencedirect.com/science/article/pii/S0925521401001338','Publisher-indexed2-15N firmness data; not wedger-force bound'),
 ('MuJoCo3.2.5 distance API','https://mujoco.readthedocs.io/en/3.2.5/APIreference/APIfunctions.html#mj-geomdistance','Documents inaccurate general-convex positive-distmax queries'),
 ('MuJoCo collision filters','https://mujoco.readthedocs.io/en/3.2.5/computation/index.html#collision-detection','Parent/weld/mask filtering; meshes convexified')]
dump('public_sources.json',dict(date='2026-10-08',sources=[dict(name=n,url=u,observation=v) for n,u,v in urls],no_purchasing_or_supplier_contact=True))
parsed=[]
for f in I.glob('*.py'):ast.parse(f.read_text(encoding='utf-8-sig'));parsed.append(f.name)
resources=[json.loads(f.read_text()) for f in A.glob('*.resource.json')]
dump('delivery_audit.json',dict(unchanged_submitted_and_binding_files=not changed,changed=changed,submitted_scripts_AST_parsed=parsed,resources=resources,max_worker_MiB=max(x['peak_MiB'] for x in resources),max_worker_elapsed_s=max(x['elapsed_s'] for x in resources),reviewer_output_bytes=sum(f.stat().st_size for f in H.rglob('*') if f.is_file()),r03_total_bytes=sum(f.stat().st_size for f in H.parent.rglob('*') if f.is_file()),process_limit='At most2 numerical worker processes simultaneously; each bounded foreground run<=900s timeout and1900MiB tree cap;CPU only',work_scope='Only sim/r03/reviewer and posts/r03/reviewer.md written;originals read only'))
assert not changed and not unresolved and sum(p['ok'] for p in logical)==19
print('19/27;2134 verified;motion fail;source hashes unchanged')
