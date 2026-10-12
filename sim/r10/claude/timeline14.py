"""R14 seasoning timeline for Wang Gang's 42 recipes (research/wanggang_recipes.json).
For every recipe: which station channel doses each seasoning, how long the station needs
to fill the dish's cups (料碗), and whether the arm can deliver the wok additions at his
timing — by single cups (pick, pour by wrist roll, return) or by the 4-compartment pour
box (one pick; compartments empty in order as the box rolls).
All rates are design assumptions (labelled RATE below), not measurements.
Usage: python timeline14.py  -> results/r14/timeline.json + markdown on stdout"""
import json,os,collections,numpy as np
D=json.load(open('../../../research/wanggang_recipes.json',encoding='utf-8'))
# channel kinds and dose-time models t = settle + m / rate (s), m in g of dispensed fluid
RATE={'thin':(1.5,3.0),'syrup':(1.5,1.0),'viscous':(2.0,.5),'oil':(1.5,2.0),'slurry':(4.5,2.0),'powder':(3.0,1.0),'paste':(3.0,1.0),'spice':(3.0,.5),'water':(1.5,5.0)}
CH={# name: (kind, channel, dispensed mass factor) ; salt / sugar / MSG are pumped as solutions
 '盐':('thin','brine 26%',1/.264),'白糖':('syrup','syrup 66%',1/.66),'味精':('thin','MSG 30%',1/.30),
 '生抽':('thin','light soy',1),'酱油':('thin','light soy',1),'老抽':('thin','dark soy',1),'料酒':('thin','cooking wine',1),
 '醋':('thin','vinegar (white/dark: 2 ch)',1),'蚝油':('viscous','oyster sauce',1),'香油':('oil','sesame oil',1),
 '红油':('oil','chili oil',1),'花椒油':('oil','Sichuan pepper oil',1),'植物油':('oil','cooking oil',1),'明油':('oil','cooking oil',1),'菜籽油':('oil','cooking oil',1),
 '水淀粉':('slurry','starch slurry (stirred)',1),'清水':('water','water',1),'清汤':('water','water',1),'清汤/清水':('water','water',1),'清水/清汤':('water','water',1),
 '鸡汤':('water','water',1),'鲜汤':('water','water',1),'热水':('water','water',1),'开水':('water','water',1),'清水(开水)':('water','water',1),
 '鸡精':('powder','chicken powder auger',1),'胡椒粉':('powder','white pepper auger',1),'黑胡椒':('powder','white pepper auger',1),
 '花椒面':('powder','ground Sichuan pepper auger',1),'淀粉':('powder','corn starch auger',1),
 '豆瓣酱':('paste','doubanjiang syringe',1),'甜面酱':('paste','sweet bean paste syringe',1),'番茄酱':('paste','sweet bean paste syringe (swap)',1),
 '花椒':('spice','Sichuan pepper feeder',1)}
KIT={'干辣椒','八角','桂皮','香叶','草果','小茴香','冰糖','豆豉','泡椒','泡姜','芽菜','泡椒末','红泡椒','花生','花生碎','熟芝麻','火锅底料','糖色','刀口辣椒','椒盐粉','葱油',
 '可乐','啤酒','浓缩橙汁','小苏打','五香粉','辣椒面','白胡椒粒','辣椒籽','黄豆酱','芝麻酱','鱼酱油','猪油','茄汁','碗汁','料汁','鱼香汁','碗芡','甜面酱+老抽 bowl'}
# defaults for unstated amounts (median of his stated doses where available) — 'assumed'
DEF={'植物油':30,'明油':5,'水淀粉':15,'清水':50,'清汤':50,'盐':2,'白糖':5,'味精':1,'鸡精':1,'生抽':4,'酱油':4,'老抽':2,'料酒':10,'醋':3,'蚝油':5,'胡椒粉':1,
 '花椒面':1,'淀粉':4,'豆瓣酱':5,'甜面酱':5,'番茄酱':10,'花椒':3,'香油':5,'红油':10,'花椒油':5,'鸡汤':200,'鲜汤':200,'热水':100,'开水':100}
ARM=dict(cup_to_platform=6.,cup_to_staging=8.,kit_cup=10.,tare=.5)   # s, arm handling estimates (RATE)
POUR={'conservative':8.,'fast':4.};BOX_STEP=1.5;BOX_MAX=4                 # pour cycle per single cup; box compartment interval
def dose_time(name,g):
 k,ch,f=CH[name];s,r=RATE[k];return s+g*f/r
rows=[];chan_use=collections.Counter()
for r in D['recipes']:
 cups=[];kit=0;assumed=0;bulk_water=0;unknown=set()
 wok_events=[]
 for e in r['events']:
  st=e['stage'];items=[it for it in e['items'] if 'name' in it]
  doses=[];kits=0
  for it in items:
   n=it['name'];g=it.get('g')
   if n in CH:
    if g is None:g=DEF.get(n,2);assumed+=1
    if CH[n][0]=='water' and g>200:bulk_water+=1;continue
    doses.append((n,g));chan_use[CH[n][1]]+=1
   elif n in KIT:kits+=1
  if st in ('wash','blanch','boil'):continue   # pot work, not seasoning cups
  if doses:cups.append(dict(stage=st,doses=doses,t=sum(dose_time(n,g) for n,g in doses)))
  kit+=kits
  if st in ('wok','finish') and (doses or kits or any('ingredient' in it for it in e['items'])):
   wok_events.append(dict(gap=e.get('gap_s'),basis=e.get('gap_basis'),seasoning=bool(doses or kits)))
 t_station=sum(c['t'] for c in cups)+len(cups)*(ARM['cup_to_platform']+ARM['cup_to_staging']+ARM['tare'])+kit*ARM['kit_cup']
 # pour bursts: consecutive seasoning wok events closer than the single-cup cycle
 res={}
 for lab,T in POUR.items():
  tight=[ev for ev in wok_events[1:] if ev['seasoning'] and ev['gap'] is not None and ev['gap']<T]
  res[lab]=len(tight)
 # with the pour box: runs of tight events (gap < fast cycle) packed into boxes of <= 4 compartments
 boxes=0;run=0;box_fail=0
 for ev in wok_events:
  if ev['seasoning'] and ev['gap'] is not None and ev['gap']<POUR['fast']:
   run+=1
   if ev['gap']<BOX_STEP:box_fail+=1
  else:
   if run:boxes+=1+(run)//BOX_MAX;run=0
 if run:boxes+=1+run//BOX_MAX
 rows.append(dict(id=r['id'],dish=r['dish'],cups=len(cups),kit_cups=kit,assumed_amounts=assumed,bulk_water_jugs=bulk_water,station_s=round(t_station),
  wok_seasoning_events=sum(1 for ev in wok_events if ev['seasoning']),too_tight_single_cup_8s=res['conservative'],too_tight_single_cup_4s=res['fast'],pour_boxes=boxes,too_tight_even_for_box=box_fail))
os.makedirs('results/r14',exist_ok=True)
json.dump(dict(rates=RATE,arm=ARM,pour=POUR,box_step=BOX_STEP,channels_used=dict(chan_use),recipes=rows),open('results/r14/timeline.json','w'),ensure_ascii=False,indent=1)
print('| 菜 | 料碗(站) | 小料杯(备) | 调料站耗时 | 锅中下料次数 | 单杯来不及(8 s/4 s) | 用分格料盒 |\n|---|---|---|---|---|---|---|')
for x in rows:print(f"| {x['dish']} | {x['cups']} | {x['kit_cups']} | {x['station_s']//60} 分 {x['station_s']%60} 秒 | {x['wok_seasoning_events']} | {x['too_tight_single_cup_8s']} / {x['too_tight_single_cup_4s']} | {x['pour_boxes']} 个{'（仍有 '+str(x['too_tight_even_for_box'])+' 处 <1.5 s）' if x['too_tight_even_for_box'] else ''} |")
st=np.array([x['station_s'] for x in rows])
print('\nstation time per dish: median %.0f s, max %.0f s; cups median %d max %d'%(np.median(st),st.max(),np.median([x['cups'] for x in rows]),max(x['cups'] for x in rows)))
print('recipes with any burst too tight for single cups at 8 s / 4 s:',sum(x['too_tight_single_cup_8s']>0 for x in rows),'/',sum(x['too_tight_single_cup_4s']>0 for x in rows),'of',len(rows))
print('recipes needing a pour box:',sum(x['pour_boxes']>0 for x in rows),'; still too tight with the box:',sum(x['too_tight_even_for_box']>0 for x in rows))
print('channel use:',chan_use.most_common())
