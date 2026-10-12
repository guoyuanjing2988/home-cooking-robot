"""Explicit like-scope budget reconciliation and source revision inventory."""
import json,subprocess,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];CONCEPT=HERE.parent/'concept'
market=json.loads((HERE.parent/'market/results/costs.json').read_text())
arm_allowance=77000
items=[]
for original in market['items']:
    row=dict(original)
    if row['id']=='arms_controllers':
        row.update(item='xArm6 arm/controller planning allowance',unit_cost_cny=arm_allowance,two_arm_cny=2*arm_allowance,three_arm_cny=3*arm_allowance,
          price_basis='Reviewer estimate 77,000/complete arm/controller, not quotation. Market records a 76,900 tender reproduction, not independently retrievable by reviewer. Dated official EXW comparator is USD8,399; inclusions/revision/import costs differ.')
    if row['id'] in ('rail','covers'):
        row.update(quantity_2=4.6,quantity_3=4.6,two_arm_cny=4.6*row['unit_cost_cny'],three_arm_cny=4.6*row['unit_cost_cny'])
    items.append(row)
totals={}
for n,k in [(2,'two_arm_cny'),(3,'three_arm_cny')]:
    sub=sum(row[k] for row in items)
    totals[str(n)]=dict(subtotal_cny=sub,contingency_cny=round(sub*.15,2),installed_estimate_cny=round(sub*1.15,2))
result=dict(date='2026-10-07',currency='CNY',rail_length_m=4.6,arm='xArm6',arm_unit_allowance_cny=77000,
    official_dated_exw_comparator=dict(date='2024-08-09',usd=8399,planning_cny_per_usd=7,planning_cny=8399*7,not_current_domestic_quote=True),
    items=items,totals=totals,incremental_third_arm_cny=round(totals['3']['installed_estimate_cny']-totals['2']['installed_estimate_cny'],2),
    inherited_market_2_4m_Zu7_totals=market['totals'],limitations=market['exclusions']+['Qualified gripper/brakes/support redesign and complete 4.6m moving-chain routing are unresolved; longer carrier cost held at inherited allowance and may increase.','No complete autonomy development cost, lifecycle support, matched certified stop integration quotation or hardware validation procurement.','These are arithmetic planning estimates, not order-ready installed prices.'])
(HERE/'audit/cost_reconciliation.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
manifest=json.loads((CONCEPT/'sources/sources.json').read_text());commits={}
for key,folder in [('menagerie','menagerie'),('aubo','aubo_description'),('xArm6','xarm_ros')]:
    head=subprocess.check_output(['git','-C',str(CONCEPT/'sources'/folder),'rev-parse','HEAD'],timeout=15,text=True).strip()
    commits[key]=dict(expected=manifest[key]['commit'],actual=head,matches=head==manifest[key]['commit'])
sources=[
 ('torques','https://docs.supportarticle.ufactory.cc/support_articles/hardware/ufactory-joint-parameters.html','Motor rated torque, gearing and separate versions; continuous joint-output rating not established'),
 ('specs','https://docs.xarm.ufactory.cc/8.technical_specifications.html','Any direction; xArm6 5kg and 12.5kg; narrower J2/J3 table; native gripper 30N'),
 ('legacy_specs','https://docs.supportarticle.ufactory.cc/support_articles/hardware/the-difference-between-ufactory-xarm5-xarm6-and-xarm7.html','Alternative official 12.2kg and broader J2/J3 ranges match legacy source more closely'),
 ('safety','https://docs.xarm.ufactory.cc/1.safety.html','Internal joint brakes; power-off holding; construction and individual holding torques not specified'),
 ('stop_environment','https://docs.xarm.ufactory.cc/7.production_information.html','EI Category1 versus SI Category2; no oil mist; stopping data; payload versus TCP offset'),
 ('mount','https://docs.xarm.ufactory.cc/2.hardware_installation.html','Direct open failed 503; official search-index extraction available: strong mount, ten times full base torsion and five times arm weight; no liquid contact'),
 ('cable','https://docs.supportarticle.ufactory.cc/support_articles/hardware/bend-radius-for-communication-and-power-cable.html','Power cable 10.4mm / radius78mm, communication6mm / radius45mm'),
 ('price','https://assets.zyrosite.com/m6Lb1n8yxOiXQr53/ufactory-product-list-dOqDEyxRogfNgOKP.pdf','Dated 2024-08-09, xArm6 USD8,399 EXW and 5kg half reach; not current China complete-cell quote'),
 ('manual','https://www.ufactory.cc/wp-content/uploads/2023/04/xArm-User-Manual-V1.11.0.pdf','Manufacturer archive illustrating XI1300 12.2kg and revision identity'),
 ('unretrieved_price','https://www.bidcenter.com.cn/newscontent-444145466-4.html','Reviewer open failed cache miss; only inherited market evidence, not independently verified')]
(HERE/'audit/source_verification.json').write_text(json.dumps(dict(date='2026-10-07',commits=commits,sources=[dict(id=k,url=u,observation=o) for k,u,o in sources]),indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(dict(totals=totals,third_arm_increment=result['incremental_third_arm_cny'],commits=commits),indent=2))
