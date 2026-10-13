"""R19 prep audit: prep demand of the reference meals A/B/C and an arm-time ESTIMATE (new file).

Demand: every ingredient of research/homestyle_meals.json (his own steps) with its prep operations.
Masses are ESTIMATES for his family of 4 (he states only: 4 rib pieces + 3 clams per cup, 4 cups,
5 eggs, 400 g rice); 'pcs' are estimated piece counts.
Arm time: each prep item is a list of movement-set instances; the unit times are labelled
  M = derived from checked sim paths (R12 chains SD/WD, R16/R17 actions, R19 hub edges),
  E = estimate by analogy (stated), not checked.
Fit: prep units must finish before the meal step that uses them (meal16 SET=stew ARM=r18 USERRICE=1,
results/r16/meal_stew_r18_userrice.json). They are put into the arm's idle windows, latest deadline
last; what does not fit before its deadline goes into a prep-first block before the meal clock starts.
Appliance dwells (peeler 1-3 min, soaking) are unattended and not arm time. One arm, so this is a
packing estimate only: sink and counter conflicts with the cooking steps are NOT modelled.
python r19prep_demand.py -> results/r19/prep/prep_demand.json"""
import json
from scene import save
# unit movement sets: (low s, high s, basis)
U={
 'PIECE':(30,45,'M: one piece tray -> wash -> station -> drop/press; SD carrot 28.1 s / WD tomato 22.3 s motion + 4 jaw events x 0.8 s + windows at 0.10 m/s; high +30 % for smooth timing at the r17 caps (R19_SMOOTH)'),
 'PIECE_SHORT':(15,25,'E: one piece from a tray or the peeler output to the next station only (one carry leg 3-10 s measured in SD/WD + events)'),
 'BASKET':(40,60,'E: R13 side-handle basket fetch, under the running tap, drain, pour, return; by analogy with the checked spider rest->pot->drain->plate->rest 52.6 s'),
 'FAUCET':(15,20,'M: FAUCET_OPEN + FAUCET_CLOSE 3.5 s each (R17) + 2 hub spurs 3.5-4.2 s (R19 hub edges)'),
 'PEEL_BATCH':(70,100,'E: abrasive drum peeler fetched: fetch 20 s, pour in, clamp, start, pour out, return 20 s (R14/R16 fetch analogies); appliance 1-3 min unattended (market_r10 sec.0)'),
 'TOOL':(40,50,'E: fetch + return of a stored tool (lever base, chopper, cracker); R14 cold box 25 + 20 s estimate, R16/R17 lid 19-20 s checked'),
 'PLATE':(15,20,'E: lever-cutter plate + pusher swap from the plate dock (market_r10 13.5 item 5)'),
 'FINGER':(10,15,'E: finger-set swap in the R13 rack (designed, never simulated)'),
 'XFER':(15,20,'E: output bowl / bin carried and poured into a staging bowl, carrier dish or cup; R16 carrier 17.7 s checked as the analogy'),
 'PRESS':(8,12,'M: lever stroke: WD GT4 pusher grasp, 102 mm press, return, release (0.8 s motion + 2 jaw events) at 0.10 m/s, + a re-push of the item for the next section'),
 'MINCE':(50,80,'E: chopper bowl: load, motor head on, run 5-10 s, head off, pour / scrape'),
 'EGG':(15,25,'E: per egg: pick (R13 egg pinch passes at mu 0.15, ~7 N), place in a lever egg cracker, press, shell to waste'),
 'BEAT':(20,30,'E: eggs beaten in the chopper bowl (pulse) or by a whisk tool'),
 'MIX':(30,45,'E: marinate / 上浆: seasonings into a lidded box, lid on, shake, lid off'),
 'SOAK':(20,30,'E: into a soak basin at the sink and out again (drain)'),
 'SCALD':(25,35,'E: kettle hot water over a bowl/basket (R16 estimate 20-30 s per pour; kettle grasp not checked)'),
 'PLACE':(6,10,'E: one piece placed into a cup or arranged on a dish'),
 'ARRANGE':(20,30,'E: pour pieces onto the steaming dish and spread by tipping'),
 'MEAT':(30,45,'E: meat pinched (R13 pork 40 N passes), dropped into the meat-slicer chute, pusher, output out'),
 'FRIDGE':(45,45,'E: R14 cold box fetch ~25 s + return ~20 s (estimated in R14; door arc checked, transfer not planned)')}
# items: meal, dish, ingredient, est mass g, est pieces, ops (prep operations), units {set: count}, deadline (dish, step-label substring), gap note
I=[
 # ---- meal A ----
 ('A','蛤蜊排骨盅','排骨 rib pieces',320,16,['buy chopped','wash','portion into cups'],{'BASKET':1,'PLACE':16},('蛤蜊排骨盅','cups'),'portioning 16 pieces is slow; pour-portion by weight would be ~4 partial pours'),
 ('A','蛤蜊排骨盅','蛤蜊 clams',250,12,['purge-soak','wash','portion into cups'],{'SOAK':1,'BASKET':1,'PLACE':12},('蛤蜊排骨盅','cups'),'purge time unsourced'),
 ('A','蛤蜊排骨盅+干锅土豆','姜 ginger slices',30,1,['wash','slice'],{'PIECE':1,'PLACE':4},('蛤蜊排骨盅','cups'),''),
 ('A','桂花糖芋头','芋头 taro',500,6,['wash','peel','block'],{'BASKET':1,'PEEL_BATCH':1,'PIECE_SHORT':6,'ARRANGE':1},('桂花糖芋头','taro plate'),'taro not in the R13 bench; peeled taro slimy (mu ~0.2 dry, catalog)'),
 ('A','干锅土豆','土豆 potato',500,3,['wash','peel','slice'],{'BASKET':1,'PEEL_BATCH':1,'PIECE_SHORT':3,'XFER':1},('干锅土豆','fry potato'),''),
 ('A','干锅土豆','五花肉 pork belly',150,1,['slice'],{'MEAT':1,'XFER':1},('干锅土豆','wok:'),'meat slicer not designed'),
 ('A','干锅土豆','红椒 red pepper',100,1,['wash','core','pieces'],{'PIECE':1,'XFER':1},('干锅土豆','wok:'),'pepper pinch fails (R13); fork/basket; wedge plate untested on pepper'),
 ('A','干锅土豆','蒜苗 garlic sprouts',80,1,['wash','section'],{'BASKET':1,'PRESS':7,'XFER':1},('干锅土豆','wok:'),'section plate designed only'),
 ('A','蚝油西兰花','西兰花 broccoli',400,1,['florets','salt soak','stem peel+slice'],{'BASKET':1,'SOAK':1,'XFER':1},('蚝油西兰花','broccoli'),'floret cutting: no appliance (gap)'),
 ('A','蚝油西兰花','胡萝卜 carrot garnish',30,1,['wash','peel','slice'],{'PIECE':1},('蚝油西兰花','broccoli'),'= the checked SD chain'),
 ('A','蒜蓉蒸丝瓜','丝瓜 luffa',500,2,['peel','section','arrange'],{'PIECE':2,'PRESS':20,'ARRANGE':1},('蒜蓉蒸丝瓜','luffa in'),'luffa peeling: no appliance (gap)'),
 ('A','蒜蓉蒸丝瓜','蒜 garlic + 红辣椒 chili',50,1,['peel cloves','mince'],{'BASKET':1,'MINCE':1},('蒜蓉蒸丝瓜','pour over garlic'),'clove peeling + mincer missing'),
 ('A','(tools)','lever base, peeler, chopper sessions',0,0,['tool fetch/return','plate swaps','finger swaps','faucet'],{'TOOL':3,'PLATE':2,'FINGER':5,'FAUCET':2,'FRIDGE':1},('蛤蜊排骨盅','cups'),''),
 # ---- meal B ----
 ('B','鲜笋排骨汤','排骨 ribs',500,1,['buy chopped','scald','soak 5 min'],{'SCALD':1,'SOAK':1},('鲜笋排骨汤','scalded ribs'),''),
 ('B','鲜笋排骨汤','鲜笋 bamboo shoot',400,2,['remove sheath','halve','thick slices'],{'PIECE':2,'PRESS':2,'XFER':1},('鲜笋排骨汤','scalded ribs'),'sheath removal: no appliance (gap); buy shelled/boiled shoots'),
 ('B','鲜笋排骨汤','干贝 dried scallops',15,1,['rehydrate soak'],{'SOAK':1},('鲜笋排骨汤','scalded ribs'),'soak time unsourced'),
 ('B','鲜笋排骨汤+红烧肉+鱼','姜 ginger slices',40,1,['wash','slice'],{'PIECE':1,'XFER':1},('鲜笋排骨汤','scalded ribs'),''),
 ('B','鲜笋排骨汤','芹菜 celery',30,1,['wash','chop'],{'BASKET':1,'MINCE':1},('鲜笋排骨汤','salt, celery'),''),
 ('B','红烧肉','五花肉 pork belly (blanched)',600,1,['scrape skin','cubes ~3 cm'],{'PIECE':1,'PRESS':4,'XFER':1},('红烧肉','fry cubes'),'cutting the blanched belly: no checked tool; lever 30 mm grid = concept, force unsourced'),
 ('B','红烧肉+鱼+番茄炒蛋+白灼汁','葱 scallion (段/葱花/葱丝)',60,1,['wash','section','rings','fine shreds'],{'BASKET':1,'PRESS':8,'XFER':2},('红烧肉','blanch'),'fine scallion shreds: no tool (gap)'),
 ('B','清蒸鲈鱼','鲈鱼 sea bass',600,1,['buy cleaned + back-split','rinse','on the dish'],{'PIECE':1,'ARRANGE':1},('清蒸鲈鱼','fish'),'R13 fork holds fish at mu 0.12; back-split by the stall'),
 ('B','清蒸鲈鱼','葱姜胡萝卜丝 fine shreds',40,2,['shred','soak to curl'],{'PIECE':2,'SOAK':1},('清蒸鲈鱼','fish out'),'4 mm shred disc coarser than his'),
 ('B','番茄炒蛋','番茄 tomato',450,3,['wash','(scald+peel: dropped in R16)','8 wedges'],{'PIECE':3,'XFER':1},('番茄炒蛋','oil, eggs'),'= the checked WD chain per tomato'),
 ('B','番茄炒蛋','鸡蛋 eggs',275,5,['crack','beat'],{'EGG':5,'BEAT':1,'TOOL':1},('番茄炒蛋','oil, eggs'),'egg station missing'),
 ('B','白灼秋葵娃娃菜','娃娃菜 baby cabbage',400,2,['wash','quarter lengthwise'],{'BASKET':1,'PRESS':4,'XFER':1},('白灼秋葵娃娃菜','blanch'),'single-blade plate designed only'),
 ('B','白灼秋葵娃娃菜','秋葵 okra',150,10,['wash'],{'BASKET':1},('白灼秋葵娃娃菜','blanch'),''),
 ('B','白灼汁','蒜 garlic + 干辣椒',30,1,['peel cloves','mince'],{'BASKET':1,'MINCE':1},('白灼汁','heat oil'),'clove peeling + mincer missing'),
 ('B','(tools)','lever base, chopper sessions',0,0,['tool fetch/return','plate swaps','finger swaps','faucet'],{'TOOL':2,'PLATE':3,'FINGER':5,'FAUCET':2,'FRIDGE':1},('鲜笋排骨汤','scalded ribs'),''),
 # ---- meal C ----
 ('C','芋头蒸排骨','排骨 ribs (small pieces)',450,1,['buy chopped','rinse','marinate'],{'BASKET':1,'MIX':1},('芋头蒸排骨','taro+rib'),''),
 ('C','芋头蒸排骨','芋头 taro',300,4,['wash','peel','blocks (plate bed)'],{'BASKET':1,'PEEL_BATCH':1,'PIECE_SHORT':4,'ARRANGE':1},('芋头蒸排骨','taro+rib'),'taro not in the R13 bench'),
 ('C','芋头蒸排骨','红椒 chili + 葱花',20,1,['wash','chop'],{'BASKET':1,'MINCE':1},('芋头蒸排骨','out (lid)'),''),
 ('C','青椒炒鱿鱼','鱿鱼 squid',400,1,['buy cleaned','score 麦穗花刀','cut','scald'],{'MEAT':1,'SCALD':1},('青椒炒鱿鱼','aromatics'),'scoring: no tool (gap); rings/strips from the meat slicer instead'),
 ('C','青椒炒鱿鱼','青椒 green pepper',150,1,['wash','core','pieces'],{'PIECE':1,'XFER':1},('青椒炒鱿鱼','aromatics'),'pepper pinch fails (R13)'),
 ('C','青椒炒鱿鱼+清炒荷兰豆+土豆丝','葱姜蒜 aromatics',50,1,['peel garlic','mince/slice'],{'BASKET':1,'MINCE':1},('青椒炒鱿鱼','aromatics'),'clove peeling + mincer missing'),
 ('C','酸辣土豆丝','土豆 potato',400,2,['wash','peel','julienne','rinse starch x2'],{'BASKET':1,'PEEL_BATCH':1,'PIECE_SHORT':2,'SOAK':2},('酸辣土豆丝','wok to the tap'),'4 mm shred disc (sourced) vs his finer hand cut'),
 ('C','酸辣土豆丝','红椒丝 + 干辣椒',30,1,['wash','shred'],{'PIECE':1},('酸辣土豆丝','blanch 30 s'),''),
 ('C','青瓜肉片汤','瘦肉 lean pork',180,1,['thin slices','上浆'],{'MEAT':1,'MIX':1},('青瓜肉片汤','pork slices'),'meat slicer not designed'),
 ('C','青瓜肉片汤','青瓜 cucumber',200,1,['wash','slice'],{'PIECE':1,'XFER':1},('青瓜肉片汤','stew pot'),'cucumber pinch needs mu >= 0.3 (R13); fork ok'),
 ('C','青瓜肉片汤','姜 ginger + 芹菜 celery',40,1,['wash','slice','chop'],{'PIECE':1,'MINCE':1},('青瓜肉片汤','stew pot'),''),
 ('C','清炒荷兰豆','荷兰豆 snow peas',300,40,['wash','string/trim'],{'BASKET':1},('清炒荷兰豆','oil, garlic'),'stringing: no tool (gap)'),
 ('C','(tools)','peeler, lever, meat slicer, chopper sessions',0,0,['tool fetch/return','plate swaps','finger swaps','faucet'],{'TOOL':3,'PLATE':2,'FINGER':5,'FAUCET':2,'FRIDGE':1},('芋头蒸排骨','taro+rib'),'')]
M=json.load(open('results/r16/meal_stew_r18_userrice.json',encoding='utf-8'))['meals']
out=dict(method=__doc__,units={k:dict(low_s=a,high_s=b,basis=c) for k,(a,b,c) in U.items()},meals={})
for mk,r in M.items():
 mid=mk[0];log=sorted(r['log'],key=lambda e:e['start_s']);end=r['total_min']*60
 busy=[(e['start_s'],e['arm_end_s']) for e in log if e['arm_end_s']>e['start_s']];idle=[];t=0
 for a,b in busy:
  if a>t:idle.append([t,a])
  t=max(t,b)
 if end>t:idle.append([t,end])
 items=[x for x in I if x[0]==mid];rows=[];counts={}
 for _,dish,ing,g,pcs,ops,units,(dd,lab),gap in items:
  dl=min((e['start_s'] for e in log if e['dish']==dd and lab in e['label']),default=None)
  if dl is None:raise SystemExit(f'deadline not found: {mid} {dd} {lab}')
  lo=sum(U[k][0]*n for k,n in units.items());hi=sum(U[k][1]*n for k,n in units.items())
  for k,n in units.items():counts[k]=counts.get(k,0)+n
  rows.append(dict(dish=dish,ingredient=ing,mass_g_est=g,pieces_est=pcs,ops=ops,sets=units,arm_s=[lo,hi],deadline_s=dl,gap=gap))
 res={}
 for w,col in (('low',0),('high',1)):   # pack into idle windows before each deadline (earliest deadline first, as early as possible)
  win=[list(x) for x in idle];pre=0.
  for row in sorted(rows,key=lambda x:x['deadline_s']):
   need=row['arm_s'][col]
   for x in win:
    if need<=0:break
    if x[0]>=row['deadline_s']:break
    take=min(need,min(x[1],row['deadline_s'])-x[0])
    if take>0:x[0]+=take;need-=take
   pre+=max(0.,need)
  res[w]=dict(arm_min=round(sum(x['arm_s'][col] for x in rows)/60,1),prep_first_block_min=round(pre/60,1),meal_with_prep_min=round(r['total_min']+pre/60,1),arm_busy_with_prep_min=round(r['arm_busy_min']+sum(x['arm_s'][col] for x in rows)/60,1))
 out['meals'][mid]=dict(meal=mk,cook_total_min=r['total_min'],cook_arm_min=r['arm_busy_min'],idle_windows_min=[[round(a/60,1),round(b/60,1)] for a,b in idle if b-a>=30],
  set_instances=counts,set_instances_total=sum(counts.values()),items=rows,fit=res)
 print(mid,'cook',r['total_min'],'min, arm',r['arm_busy_min'],'| prep arm',res['low']['arm_min'],'-',res['high']['arm_min'],'min | prep-first block',res['low']['prep_first_block_min'],'-',res['high']['prep_first_block_min'],'min | meal incl. prep',res['low']['meal_with_prep_min'],'-',res['high']['meal_with_prep_min'],'| set instances',sum(counts.values()))
tot={}
for v in out['meals'].values():
 for k,n in v['set_instances'].items():tot[k]=tot.get(k,0)+n
out['set_instances_ABC']=dict(sorted(tot.items(),key=lambda kv:-kv[1]));print('set instances A+B+C',out['set_instances_ABC'])
save('results/r19/prep/prep_demand.json',out)
