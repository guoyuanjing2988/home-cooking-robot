"""Faucet-enabled evidence aggregation; all prior iteration counts stay literal."""
import sys,json,csv,runpy,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';ID=sys.argv[1]
runpy.run_path(str(H/'deliver_v2_r07.py'))
def read(n):return json.loads((O/n).read_text(encoding='utf-8-sig'))
def write(n,x):(O/n).write_text(json.dumps(x,indent=2,allow_nan=False),encoding='utf-8')
s=read('phase_summary.json');new=[m for m in s['reachability_maps'] if int(m['layout'][1:])>=20 and m['paired_complete']]
assert len(new)>=6,'New user stop condition requires six FURTHER paired-map iterations.'
for m in new:
 for side in ('R','L'):
  rows=read(f'reachability/{m["layout"]}/{side}.json')['rows']
  m['sides'][side]['common_grid_targets']=216;m['sides'][side]['common_grid_passed']=sum(r['pass_'] for r in rows[:216])
  m['sides'][side]['faucet_relative_targets']=len(rows[216:]);m['sides'][side]['faucet_relative_passed']=sum(r['pass_'] for r in rows[216:])
s.update(schema='r07.v3.faucet-enabled-static-evidence',faucet_enabled_paired_maps=new,faucet_enabled_complete_paired_layout_maps=len(new),stopping_basis='Alternative (b) of the faucet-enabled user instruction: at least six FURTHER complete paired reachability studies, with full-size geometry, station/mount iterations and recorded blockers. No global architecture impossibility is inferred from unresolved IK, a conservative obstacle or a finite map.',prior_delivery='history/v2/results/phase_summary.json')
s['new_search_totals']={}
for d in sorted((O/'static_v2').iterdir()):
 if not d.is_dir() or not d.name[1:].isdigit() or int(d.name[1:])<20:continue
 rr=[json.loads(p.read_text()) for p in d.glob('*.json')]
 s['new_search_totals'][d.name]=dict(strokes_attempted=len(rr),starts=sum(r['starts'] for r in rr),strokes_96_or_more=sum(r['starts']>=96 for r in rr),witnesses=sum(bool(r.get('witness')) for r in rr),actual_problem_seconds=sum(x['elapsed_s'] for r in rr for x in r['rows']),newly_executed_starts=sum(r['starts']-r.get('equivalent_scene_reuse',{}).get('starts_reused',0) for r in rr),newly_executed_seconds=sum(x['elapsed_s'] for r in rr for x in r['rows'][r.get('equivalent_scene_reuse',{}).get('starts_reused',0):]))
write('phase_summary.json',s)
f=read('faucet_v3.json');f['valve']=dict(model='DFRobot FIT0498',dimensions_mm=[70,57,45],supply_V=12,current_A=.42,normally_closed=True,IP='IP00',pressure_MPa=[.02,.8],temperature_C=[0,60],manufacturer='https://www.dfrobot.com/product-1530.html',china_direct_buyable='https://www.dfrobot.com.cn/goods-1334.html',observed_CNY=79,installed_service_enclosure_mm=[150,120,110],qualified=False,limitations='Dry enclosure, potable wetted material compatibility, plumbing connections, measured shutoff and fault response remain unqualified; no executed water-event credit.')
f.update(selected_layout=ID,placement=read(f'layouts/{ID}.json')['replacement_faucet'],regional_drawing_note='Japan drawing3328130J has ECN33281003 and G1/2 hoses; global33281003 page specifiesG3/8. Above-deck dimensional drawing is used conservatively;635mm hose cover exceeds595mm global sheet. Exact local connection kit remains qualification work.',design_flow_L_min=6,maximum_published_flow_L_min=11,design_flow_basis='Adjustable flow limiter;6L/min retained design setting, not measured installed flow.')
write('faucet_v3.json',f)
if f['placement'].get('spout_state')=='nominal_fixed_during_operation':
 f['geometry']='Same full exterior profile, body, maximum handle sweep, mounting hardware and hoses at the explicitly recorded nominal spout angle. Full140degree sweep studies remain L20-L31. This state-conditioned model does not claim arbitrary-angle clearance; no physical profile or gap was reduced.'
 write('faucet_v3.json',f)
with (O/'costs.csv').open(newline='',encoding='utf-8') as file:rows=list(csv.DictReader(file))
rows=[r for r in rows if r['item'] not in ('TOTAL','One15percent project reserve')]
for r in rows:
 if 'compact wall rails' in r['item'] or 'compact wall rail,' in r['item']:
  r['item']='One compact wall rail, two carriages, home brakes, chains and brackets'
  r['basis']='43000CNY retained system allowance. One shared lane, carriage order preserved. No portal, legs, elevator, pallet or wall extension.'
template=dict(rows[0])
for item,value,basis in [('GROHE Eurosmart33281003 replacement faucet',1500,'Real buyable low-spout faucet;1500CNY engineering allowance, not a current China supplier quotation.'),('NC water valve and dry low-voltage plumbing/control',300,'FIT0498 public China direct price79CNY plus221CNY enclosure, driver, adapters and installation allowance; no procurement or supplier contact.')]:
 r=dict(template,item=item,quantity=1,total_cny=value,basis=basis);rows.append(r)
base=round(sum(float(r['total_cny']) for r in rows),2);reserve=round(base*.15,2);total=round(base+reserve,2)
rows +=[dict(template,item='One15percent project reserve',quantity=1,total_cny=reserve,basis='15% of all base items, applied once.'),dict(template,item='TOTAL',quantity=1,total_cny=total,basis='Includes one18000CNY home safety package and one15% reserve.')]
with (O/'costs.csv').open('w',newline='',encoding='utf-8') as file:w=csv.DictWriter(file,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
write('cost_summary.json',dict(base_cny=base,reserve_cny=reserve,total_cny=total,reserve_rate=.15,safety_package_count=1,cheapest_passing_configuration=None,current_supplier_quote=False,faucet_and_control_increment_cny=1800))
motion=read('motion.json');motion['schema']='r07.v3.motion-ledger';foldfile=O/f'layouts/{ID}_fold_map.json'
if foldfile.exists():
 fold=json.loads(foldfile.read_text());motion['auxiliary_fold_unfold']=fold
 idle=read('idle.json');idle['auxiliary_map_folds']=fold;idle['local_map_fold_unfold_pass']=fold['local_fold_unfold_pass'];idle['pass_']=False;idle['meal_end_to_park_verified']=False;idle['status']='MEAL_END_RETURN_UNVERIFIED';write('idle.json',idle);motion['parking']=idle
write('motion.json',motion)
continued=O/f'layouts/{ID}_fold_continuation.json'
if continued.exists():
 foldc=json.loads(continued.read_text());motion['continued_deployment']=foldc;idle=read('idle.json');idle['continued_deployment']=foldc;idle['complete_auxiliary_deployment_pass']=foldc['pass_'];idle['pass_']=False;idle['meal_end_to_park_verified']=False;idle['status']='FULL_WORKING_FOLD_AND_MEAL_END_RETURN_UNVERIFIED';write('idle.json',idle);motion['parking']=idle;write('motion.json',motion)
schedule=read('schedule.json');schedule['schema']='r07.v3.executed-path-schedule';schedule['faucet']=dict(model=f['model'],design_flow_L_min=6,water_execution_verified=False);write('schedule.json',schedule)
# The active ledger is regenerated by rules_v3 before this script.
ledger=read('intended_contacts.json')
with (O/'iterations.csv').open(newline='',encoding='utf-8') as file:iterations=list(csv.DictReader(file));fields=list(iterations[0])
for file in (O/'static_v2'/ID).glob('*.json'):
 r=json.loads(file.read_text());reuse=r.get('equivalent_scene_reuse')
 if not reuse:continue
 for row in iterations:
  if row['kind']=='static_start' and row['layout']==ID and row['id']==r['stroke'] and int(row['seed'])<reuse['starts_reused']:
   row.update(kind='equivalent_scene_reuse',actual_s=0,status='Exact model/task/envelope match; references an already executed '+reuse['source_layout']+' start, zero new CPU time',evidence=reuse['source'])
for routefile in sorted((O/'layouts').glob('*_fold_map.json')):
 mapped=json.loads(routefile.read_text())
 for r in mapped['routes']:
  p=r['planner'];iterations.append(dict(kind='map_guided_fold_unfold',id=r['index'],layout=mapped['layout'],seed=p.get('seed',''),starts=p.get('seeds_tried',0),pass_=r['pass_'],budget_s=65,actual_s=p.get('planner_time_s',0),status='Full populated empty-hand deployment;10mm door gate; no meal-end credit',evidence=str(routefile.relative_to(H)).replace('\\','/')))
for file in sorted((O/'layouts').glob('*_fold_continuation.json')):
 x=json.loads(file.read_text())
 for ai,a in enumerate(x['attempts']):
  for st in a['steps']:
   p=st.get('planner',{});iterations.append(dict(kind='deployment_continuation',id=f'{ai}.{st["step"]}',layout=x['layout'],seed=p.get('seed',''),starts=p.get('seeds_tried',0),pass_=p.get('ok',False),budget_s=p.get('allocated_budget_s',20),actual_s=p.get('planner_time_s',st.get('ik_s',0)),status='Checked segment of deployment attempt; complete attempt pass='+str(a['pass_'])+'; no meal credit',evidence=str(file.relative_to(H)).replace('\\','/')))
with (O/'iterations.csv').open('w',newline='',encoding='utf-8') as file:w=csv.DictWriter(file,fieldnames=fields);w.writeheader();w.writerows(iterations)
print('V3',ID,'new paired maps',len(new),'cost',total,flush=True)
