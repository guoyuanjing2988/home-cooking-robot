"""Independent arithmetic, source-model and submission inventory audit."""
from pathlib import Path
import ast,json,math,xml.etree.ElementTree as ET
H=Path(__file__).resolve().parent;ROOT=H.parents[2];I=H.parent/'integrator';O=H/'results';A=H/'audit'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(n,v):(O/n).write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
force=[('carrot_cut',2*67.59/31*35,'Primary slow transverse carrot data; width scaling and 2x margin'),('potato_cut',2*61.49/47*70,'Primary slow transverse potato data; width scaling and 2x margin'),('greens_cut',2*67.59/31*80,'Retained carrot-tissue proxy'),('tomato_wedge',2*15/(math.pi*2**2)*4*70*.952,'Retained compression-probe stress to blade-area proxy'),('peel_drag',1.5*1.68*25,'Carrot abstract resistance; potato proxy'),('peel_normal',1.5*1000*.005,'Assumed spring and compression'),('eye_core',2*67.59/31*12,'Carrot-width proxy; moment uses 10mm lever'),('root_rub',1.5*1000*.006,'Assumed spring and compression'),('leaf_rub',1.5*400*.005,'Assumed spring and compression'),('tomato_rub',1.5*200*.005,'Assumed spring and compression'),('water_jet',1.5*1000*(.006/60)**2/(math.pi*.010**2/4),'rho Q squared/A, assumed 6L/min and 10mm outlet'),('drawer_insert',1.5*(.5*1.1*9.81+1.1*.3+2),'Friction/inertia/latch assumptions'),('handle_carry',.45,'Check acceleration N/kg, gravity separate'),('leaf_separate',.1*.45,'Detached leaf carry, not tearing'),('cleanup_wipe',1.5*500*.005,'Assumed spring and compression'),('end_cup_preload',1.5*1000*.010,'Assumed spring and compression'),('machine_index',1.5*(.5*1.1*9.81+1.1*.3),'Friction/inertia assumptions')]
dump('force_arithmetic.json',dict(models=[dict(id=n,check_value=v,basis=b) for n,v,b in force],proxy_qualification=False))
raw=read(I/'results/static_all.json');rows=raw['rows'];fresh=[r for r in rows if Path(r['source']).parts[0]=='results']
source_rows=[]
for r in rows:
 p=read(I/r['source']);source_rows.append(dict(stroke=r['stroke'],source=r['source'],starts=p['starts'],solutions=p['solutions_found'],final_witnesses=r['verified_witnesses']))
jaka=[]
for n,kg in [('jaka_zu5',23),('jaka_zu7',22)]:
 p=I/'sources/jaka_description/urdf'/(n+'.urdf');tree=ET.parse(p).getroot();mass=sum(float(x.get('value')) for x in tree.findall('.//link/inertial/mass'));jaka.append(dict(model=n,source_mass_kg=mass,public_mass_kg=kg,match=abs(mass-kg)<.1))
replay=read(O/'reverify_all.json');phase_stats=[]
for p in replay['instances']:
 phase_stats.append(dict(phase=p['phase'],strokes=len(p['strokes']),passed=p['ok'],poses=sum(x['poses'] for x in p['strokes'])))
power=[('UR5e maximum',570),('xArm controller provision',500),('R211XL',550),('guarded auxiliary cutter allowance',150),('rails/EOAT/IPC allowance',200)]
parsed=[];errors=[]
for f in I.glob('*.py'):
 try:ast.parse(f.read_text(encoding='utf-8-sig'));parsed.append(f.name)
 except Exception as e:errors.append(dict(file=f.name,error=str(e)))
json_inventory=[]
for f in (I/'results').glob('*.json'):
 try:
  v=read(f);json_inventory.append(dict(file=f.name,type=type(v).__name__,keys=list(v)[:20] if isinstance(v,dict) else None))
 except Exception as e:errors.append(dict(file=f.name,error=str(e)))
dump('evidence_accounting.json',dict(selected_source_starts=sum(r['starts'] for r in source_rows),selected_source_solutions=sum(r['solutions'] for r in source_rows),historical_scope='These counts include archived geometry; only independently replayed selected witnesses are final passes',fresh_strokes=len(fresh),fresh_starts=sum(r['archived_starts'] for r in fresh),fresh_solutions=sum(r['solver_solutions_found'] for r in fresh),final_witnesses=len(raw['witnesses']),selected_candidates=sum(r['replayed_candidates'] for r in rows),source_rows=source_rows,independently_replayed_phase_stats=phase_stats,jaka_model_mass=jaka,power=dict(components_W=power,total_W=sum(v for _,v in power),current_230V_PF1_A=sum(v for _,v in power)/230,current_230V_PF08_A=sum(v for _,v in power)/230/.8,qualification='Inherited best-candidate steady allowance; no inrush/leakage/coordination proof. Substitutions and lift variants require their own power audit.',r04_power_json_exists=(I/'results/power.json').exists()),submitted_top_level_scripts_AST_parsed=parsed,submitted_top_level_result_inventory=json_inventory,parse_errors=errors))
assert not errors
print('sources',sum(r['starts'] for r in source_rows),sum(r['solutions'] for r in source_rows),'fresh',len(fresh),sum(r['archived_starts'] for r in fresh),'AST',len(parsed),'results',len(json_inventory))
