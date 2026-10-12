"""Validate delivered engineering records and reference integrity, CPU only."""
import json,csv,re,hashlib
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];R=HERE/'results'
D=json.loads((R/'transport_options.json').read_text());G=json.loads((R/'geometry_check.json').read_text());S=json.loads((R/'sources.json').read_text())
post=ROOT/'posts/r02/transport.md';P=post.read_text(encoding='utf-8')
assert P.startswith('推荐采用') and '## Decision and scope' in P
assert not re.search(r'SOURCE_[A-Z]+|(?:COST|RANK|CHECK|SERVICE)_TABLE|MOUNT_TWO|MOUNT_THREE',P)
ids={a['id'] for a in S}
with (R/'costs.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
assert len(rows)==39 and len(D['options'])==13
for a in D['options']:
    for k in ['capacity_note','accuracy_evidence','stiffness','power_loss_braking','power_data','splash_grease_cleanability','noise','mounting','scores_1_to_5']:assert a[k],(a['id'],k)
    assert set(a['source_ids'])<=ids
    for n in [2,3,4]:
        row=next(z for z in rows if z['option_id']==a['id'] and int(z['carriages'])==n)
        assert int(row['cost_base_cny'])==a['cost_cny'][str(n)]
        assert float(row['run_m'])==2.4 and int(row['cost_low_cny'])<=a['cost_cny'][str(n)]<=int(row['cost_high_cny'])
assert next(a for a in D['options'] if a['id']==D['recommendation']['primary'])['cost_cny']['3']==D['recommendation']['cost_3arm_cny']==99000
assert len(G)==4 and all(a['screen_pass'] and a['minimum_robot_environment_gap_lower_bound_m']>=.01-1e-9 and a['minimum_different_lane_robot_gap_lower_bound_m']>=.01-1e-9 for a in G)
geometry_variants={v['id']:v for v in D['geometry']['variants']}
for g in G:
    draw=json.loads((R/(g['variant']+'_draw.json')).read_text())
    assert draw['variant']==geometry_variants[g['variant']],g['variant']
    assert (R/(g['variant']+'.xml')).is_file()
diagrams=[]
for name in ['passing_rails_cable_2','passing_xz_cable_2','passing_rails_cable_3','passing_xz_cable_3']:
    with Image.open(HERE/'renders'/(name+'.png')) as im:
        assert im.size==(1600,1000);im.verify();diagrams.append(dict(file=name+'.png',size=[1600,1000]))
local_links=[]
for target in re.findall(r'\]\(([^)]+)\)',P):
    if not target.startswith(('https://','http://')):
        path=(post.parent/target).resolve();assert path.is_file(),str(path);local_links.append(target)
for path,sha in D['reference_hashes'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha,path
assert D['binding_acceptance']['friction_mu']==.5 and D['binding_acceptance']['pose_angle_deg']==3
assert D['sizing']['selected_service_moment_each_axis_Nm']>=D['sizing']['gravity_plus_process_design_Nm']
assert abs(D['sizing']['guide']['rail_pair_spacing_m']-D['geometry']['variants'][0]['rails'][0]['guide_pair_spacing_m'])<1e-9
power=D.get('power_options')
if power:
    assert P.count('## Power track addendum')==1
    assert power==json.loads((R/'power_options.json').read_text(encoding='utf-8'))
    assert power['recommendation']['arm_power']=='dedicated_cable_chains'
    assert power['recommendation']['appliance_power']=='stationary_household_power_track'
    assert power['no_new_contact_exemptions'] and not power['mechanical_collision_screen_for_added_power_hardware']
    ps=json.loads((R/'power_sources.json').read_text(encoding='utf-8'))
    pids={z['id'] for z in ps};assert set(power['source_ids'])==pids
    for opt in power['options']:assert set(opt.get('source_ids',opt.get('sources',[])))<=pids
    with (R/'power_costs.csv').open(encoding='utf-8-sig',newline='') as f:pcost=list(csv.DictReader(f))
    assert len(pcost)==12
    for row in pcost:
        opt=next(a for a in power['options'] if a['id']==row['option_id'])
        assert opt['cost']['packages_cny'][row['carriages']]==int(row['base_cny'])
    ur=power['arm_budgets'][1];xa=power['arm_budgets'][2]
    assert ur['catalog_max_inrush_A']==400 and ur['instantaneous_operating_peak_W'] is None
    assert abs(ur['carriage_total_input_design_A_42V']-1045/.9/42)<1e-5
    assert abs(xa['carriage_total_input_design_A_48V']-862/.9/48)<1e-5
    b=power['options'][1];buf=power['options'][2]['buffer']
    assert ur['carriage_total_input_design_A_42V']<b['minimum_derated_continuous_A']
    required=1045*20*1.5/.9
    available=.5*buf['selected_minimum_initial_capacitance_F']*.8*(47.5**2-36**2)
    assert available>=required and abs(buf['required_energy_with_margin_J']-required)<1e-4
    assert b['PSU_example']['overvoltage_trip_range_V'][1]>60 and not b['PSU_example']['installed_SELV_proof']
    assert not re.search(r'POWER_[A-Z]+',P)
files=list(HERE.rglob('*'));total=sum(p.stat().st_size for p in files if p.is_file())+post.stat().st_size
assert total<2*1024**3
result=dict(status='PASS',files=sum(p.is_file() for p in files),output_bytes=total,cost_rows=len(rows),survey_options=len(D['options']),local_post_links=len(local_links),reference_hashes_verified=len(D['reference_hashes']),diagrams=diagrams,geometry_checks=len(G),scope='Artifact consistency and sampled transport evidence only, not hardware certification or prep-task pass.')
if power:result.update(power_options=len(power['options']),power_sources=len(ps),power_cost_rows=len(pcost),power_buffer_energy_arithmetic_verified=True)
(HERE/'audit/delivery_check.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
