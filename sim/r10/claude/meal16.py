"""R16 one-arm meal scheduler for the user's reference creator's 四菜一汤 menus
(research/homestyle_meals.json): can one arm plus a few appliances get a 4-dish + soup + rice
meal on the table, everything hot at the same time, and how long does it take?
Each dish is a chain of steps. A step occupies the ARM for arm_s, then (optionally) holds a heat
RESOURCE unattended for wait_s; the dish's next step starts only after that. The arm runs a list
scheduler: at each moment it does the first step (in the creator's own cooking order) whose
predecessor is done and whose resource is free; it never waits while another step is ready.
Cooking times are his (homestyle_meals.json); arm handling times are ASSUMPTIONS (ARM below),
the stir-fry arm time includes the one-arm pauses (R15: about 2.6 s per stroke, half power when
the spatula stops). Knife work is NOT scheduled here (counted separately: done by the R11 prep
machines or by the user beforehand); seasoning cups come from the R14 station in advance.
Resources: wok (R15 concave induction), zone2 (a second, flat induction zone: steamer pot or
clay pot), stew (an electric stew pot, option), rice (rice cooker), fryer (R14).
python meal16.py [SET=base|stew] [ARM=checked|r17] -> results/r16/meal_<SET>[_checked|_r17].json, renders/r16/meal_<SET>[_checked|_r17].png
ARM=r17 (R17, after the user's decisions of 2026-10-12): as checked, plus results/r17/arm17.json (r17seq.py):
the wok is rinsed at the sink on the plating trip (faucet opened before, closed after), so a dish's
'rinse' after a plating takes no arm time; after blanching or a soup in the wok the wok goes to the
sink to be emptied and rinsed ('dump'); a litre of water for the wok is taken at the running tap
('fill', the same trip); small amounts (<= 300 ml) still come in a cup like a seasoning; the spider
from its rest (checked whole path). Serving is the user's (2026-10-12: "做完上菜人类来就行"): no ladling;
soups stay in their pot and the user serves them (meal C's soup moves from the wok to the electric stew
pot: a soup bowl at the plating spot was in the arm's way when it picked the wok up).
ARM=checked: lid, plate_in / plate_out, ladle, spider, wok_plate and rinse from results/r16/arm_checked.json
(r16seq.py: checked whole-action paths for the lid, the dish carrier and the ladle; estimates for the
spider and the wok, see its status field). The R16 steamer is a pot with one steaming rack (a stacked
tier failed under the hood), so it holds ONE dish carrier: in meal A the stew cups go to an electric
water-bath stew pot ('stew', handling and its lid assumed like the pot's) and the taro takes the rack."""
import sys,os,json
KV=dict(a.split('=',1) for a in sys.argv[1:]);SET=KV.get('SET','stew')
ARM=dict(pour=8,lid=8,plate_in=20,plate_out=20,wok_plate=30,ladle=35,rinse=75,spider=20,sauce_oil=30,cup=8,rice=180,arrange=30)
SOUP_RES='stew' if SET=='stew' else 'zone2'
def S(dish,label,res,arm,wait=0,after=None,nb=None):return dict(dish=dish,label=label,res=res,arm=arm,wait=wait,after=after,nb=nb)   # nb=(step, lead_s): not before that step's finish minus lead (quick dishes go last, like he does)
R17=KV.get('ARM') in ('r17','r18');CHECKED=KV.get('ARM')=='checked' or R17
if CHECKED:ARM.update(json.load(open('results/r16/arm_checked.json'))['arm_s'])
if R17:ARM.update(json.load(open('results/r18/arm18.json' if KV.get('ARM')=='r18' else 'results/r17/arm17.json'))['arm_s'])   # R18: ARM=r18, the spatula on the counter left of the sink   # wok_plate (with the sink rinse), rinse=0, dump, fill, spider
A=ARM
MEALS={
 'A 干锅土豆/桂花芋头/西兰花/蒜蓉丝瓜/蛤蜊排骨盅':[
  S('蛤蜊排骨盅','cups + taro plate into steamer, lid, steam 30 min','zone2',4*A['plate_in']/2+A['plate_in']+A['lid'],1800),
  S('桂花糖芋头','(steams with the cups)',None,0,0,after=0),
  S('米饭','rice: dose, wash, cooker','rice',A['rice'],2100),
  S('干锅土豆','fry potato 3 min (fryer), lift out','fryer',A['pour']+A['spider'],180,nb=(0,780)),
  S('干锅土豆','wok: pork, 豆瓣, chili, potato, sauce; stir 90 s; plate','wok',90*1.3+3*A['pour']+A['wok_plate'],0,after=3),
  S('蚝油西兰花','rinse wok; oil, broccoli, sauce; lid 30 s; stir; plate','wok',A['rinse']+2*A['pour']+A['lid']*2+30+20*1.3+A['wok_plate'],nb=(0,600)),
  S('蒜蓉蒸丝瓜','steamer: cups + taro out (lid), luffa in, 3 min','zone2',A['lid']+3*A['plate_out']+A['plate_in']+A['lid'],180,after=0),
  S('桂花糖芋头','drizzle osmanthus syrup',None,A['pour'],after=6),
  S('蒜蓉蒸丝瓜','rinse wok; heat 40 g oil 60 s; pour over garlic bowl','wok',A['rinse']+A['pour']+A['sauce_oil'],60),
  S('蒜蓉蒸丝瓜','luffa out (lid), pour sauce over','zone2',A['lid']+A['plate_out']+A['pour'],0),
 ],
 'B 红烧肉/番茄炒蛋/白灼秋葵娃娃菜/清蒸鲈鱼/鲜笋排骨汤':[
  S('鲜笋排骨汤','scalded ribs, shoots, scallops, hot water into the pot; lid; 60 min',SOUP_RES,4*A['pour']+A['lid'],3600),
  S('红烧肉','blanch pork belly (cold water start) 5 min; lift out','wok',2*A['pour']+A['spider'],300),
  S('红烧肉','(cut cubes: prep machine / user)',None,0,0,after=1),
  S('红烧肉','fry cubes, aromatics, 糖色, sauce, water; lid; braise 40 min','wok',A['rinse']+150*1.3+5*A['pour']+A['lid'],2400,after=2),
  S('米饭','rice: dose, wash, cooker','rice',A['rice'],2100),
  S('清蒸鲈鱼','fish plate into steamer, lid, 6 min','zone2' if SET=='stew' else 'wok',A['plate_in']+A['lid'],360,nb=(0,900)),
  S('红烧肉','lid off, reduce 3 min stirring, plate','wok',A['lid']+180*1.0+A['wok_plate'],0,after=3),
  S('清蒸鲈鱼','fish out, pour off water, soy, shreds','zone2' if SET=='stew' else 'wok',A['lid']+A['plate_out']+3*A['pour'],0,after=5),
  S('白灼汁','rinse wok; heat oil 60 s; over fish + over garlic bowl; mix sauce','wok',A['rinse']+A['pour']+2*A['sauce_oil']+3*A['pour'],60,after=7),
  S('番茄炒蛋','oil, eggs set, out; tomato, lid 30 s, eggs back; plate','wok',A['rinse']+5*A['pour']+2*A['lid']+30+60*1.3+A['wok_plate'],nb=(0,720)),
  S('白灼秋葵娃娃菜','water+oil+salt to boil 3 min; cabbage 1 min, okra 30 s; spider out; arrange; sauce','wok',A['rinse']+A['pour'],180,nb=(0,600)),
  S('白灼秋葵娃娃菜','blanch and lift out, arrange, sauce','wok',2*A['pour']+90+2*A['spider']+A['arrange']+A['pour'],0,after=10),
  S('鲜笋排骨汤','salt, celery; ladle into bowl',SOUP_RES,A['pour']+A['ladle'],0,after=0),
 ],
 'C 芋头蒸排骨/酸辣土豆丝/青椒炒鱿鱼/清炒荷兰豆/青瓜肉片汤':[
  S('芋头蒸排骨','taro+rib plate into steamer, lid, 30 min','zone2',A['plate_in']+A['lid'],1800),
  S('米饭','rice: dose, wash, cooker','rice',A['rice'],2100),
  S('酸辣土豆丝','water to boil 3 min; shreds in, back to boil, spider out','wok',2*A['pour'],180,nb=(0,900)),
  S('酸辣土豆丝','blanch 30 s, lift out; rinse; stir-fry 45 s with 调味水; plate','wok',A['pour']+30+A['spider']+A['rinse']+3*A['pour']+45*1.3+A['wok_plate'],0,after=2),
  S('青瓜肉片汤','water to boil 3 min, ginger, cucumber','wok',A['rinse']+2*A['pour'],180),
  S('青瓜肉片汤','pork slices into the boil 2 min; salt; ladle into bowl','wok',2*A['pour']+120+A['ladle'],0,after=4),
  S('青椒炒鱿鱼','rinse; aromatics, pepper, wine, squid, sauce; stir 60 s; plate','wok',A['rinse']+5*A['pour']+60*1.3+A['wok_plate']),
  S('清炒荷兰豆','oil, garlic, peas, salt, water; stir 45 s; plate','wok',A['rinse']+3*A['pour']+45*1.3+A['wok_plate']),
  S('芋头蒸排骨','out (lid), chili, scallion, hot oil from the wok','zone2',A['lid']+A['plate_out']+2*A['pour']+A['sauce_oil'],0,after=0),
 ]}
if CHECKED:   # meal A with a one-carrier pot steamer: cups in the electric stew pot (隔水炖), taro on the rack
 MEALS['A 干锅土豆/桂花芋头/西兰花/蒜蓉丝瓜/蛤蜊排骨盅']=[
  S('蛤蜊排骨盅','4 cups into the electric stew pot (water bath), lid, 30 min','stew',4*A['cup']+A['lid'],1800),
  S('桂花糖芋头','taro plate into the pot steamer, lid, 30 min','zone2',A['plate_in']+A['lid'],1800),
  S('米饭','rice: dose, wash, cooker','rice',A['rice'],2100),
  S('干锅土豆','fry potato 3 min (fryer), lift out','fryer',A['pour']+A['spider'],180,nb=(1,780)),
  S('干锅土豆','wok: pork, 豆瓣, chili, potato, sauce; stir 90 s; plate','wok',90*1.3+3*A['pour']+A['wok_plate'],0,after=3),
  S('蚝油西兰花','rinse wok; oil, broccoli, sauce; lid 30 s; stir; plate','wok',A['rinse']+2*A['pour']+A['lid']*2+30+20*1.3+A['wok_plate'],nb=(1,600)),
  S('蒜蓉蒸丝瓜','steamer: taro out (lid), luffa in, lid, 3 min','zone2',A['lid']+A['plate_out']+A['plate_in']+A['lid'],180,after=1),
  S('桂花糖芋头','drizzle osmanthus syrup',None,A['pour'],after=6),
  S('蒜蓉蒸丝瓜','rinse wok; heat 40 g oil 60 s; pour over garlic bowl','wok',A['rinse']+A['pour']+A['sauce_oil'],60),
  S('蒜蓉蒸丝瓜','luffa out (lid), pour sauce over','zone2',A['lid']+A['plate_out']+A['pour'],0),
  S('蛤蜊排骨盅','cups out of the stew pot (lid)','stew',A['lid']+4*A['cup'],0,after=0)]
if R17:   # water and rinses (see the docstring); the rest as checked
 MB,MC='B 红烧肉/番茄炒蛋/白灼秋葵娃娃菜/清蒸鲈鱼/鲜笋排骨汤','C 芋头蒸排骨/酸辣土豆丝/青椒炒鱿鱼/清炒荷兰豆/青瓜肉片汤'
 MEALS[MB][1]=S('红烧肉','wok to the tap: 1 L cold water; pork belly in; blanch 5 min; lift out','wok',A['fill']+A['pour']+A['spider'],300)
 MEALS[MB][3]=S('红烧肉','wok emptied at the sink; fry cubes, aromatics, 糖色, sauce, water (cup); lid; braise 40 min','wok',A['dump']+150*1.3+5*A['pour']+A['lid'],2400,after=2)
 MEALS[MB][10]=S('白灼秋葵娃娃菜','wok to the tap: 1 L water; oil, salt; to boil 3 min','wok',A['fill']+2*A['pour'],180,nb=(0,600))
 MEALS[MC][2]=S('酸辣土豆丝','wok to the tap: 1 L water; to boil 3 min; shreds in, back to boil','wok',A['fill']+A['pour'],180,nb=(0,900))
 MEALS[MC][3]=S('酸辣土豆丝','blanch 30 s, lift out; wok emptied at the sink; stir-fry 45 s with 调味水; plate','wok',30+A['spider']+A['dump']+3*A['pour']+45*1.3+A['wok_plate'],0,after=2)
 # soups stay in a pot the user serves from: a soup bowl at the plating spot (6-8 cm) met the arm's
 # forearm when it picked the wok up (r17chain wok PH=.06/.08, also moved 8-10 cm left), so meal C's
 # quick soup moves from the wok to the electric stew pot (idle in this meal; water put in at setup)
 MEALS[MC][4]=S('青瓜肉片汤','stew pot (water in at setup, heating): ginger, cucumber','stew',2*A['pour'],300)
 MEALS[MC][5]=S('青瓜肉片汤','pork slices 3 min; salt (the user serves it from the pot)','stew',2*A['pour'],180,after=4)
 MEALS[MC][6]=S('青椒炒鱿鱼','aromatics, pepper, wine, squid, sauce; stir 60 s; plate','wok',5*A['pour']+60*1.3+A['wok_plate'])
 MEALS[MB][12]=S('鲜笋排骨汤','salt, celery (the user serves it from the pot)',SOUP_RES,A['pour'],0,after=0)
 MEALS['A 干锅土豆/桂花芋头/西兰花/蒜蓉丝瓜/蛤蜊排骨盅'][10]=S('蛤蜊排骨盅','(the cups stay in the stew pot; the user serves them)','stew',0,0,after=0)
def run(steps):
 n=len(steps);done=[None]*n;start=[None]*n;arm_t=0.;res_free={};arm_busy=0.;log=[]
 prev={}   # implicit chain: each dish's steps follow each other in list order unless 'after' given
 last={}
 for i,s in enumerate(steps):
  p=s['after'] if s['after'] is not None else last.get(s['dish']);prev[i]=p;last[s['dish']]=i
 todo=list(range(n))
 while todo:
  best=None
  for i in todo:
   p=prev[i];ready=0. if p is None else (done[p] if done[p] is not None else None)
   if ready is None:continue
   r=steps[i]['res'];nb=steps[i]['nb'];rel=0.
   if nb is not None:
    if done[nb[0]] is None:continue
    rel=done[nb[0]]-nb[1]
   t0=max(arm_t,ready,res_free.get(r,0.) if r else 0.,rel)
   if best is None or t0<best[0]-1e-9:best=(t0,i)
  t0,i=best;s=steps[i];start[i]=t0;arm_t=t0+s['arm'];arm_busy+=s['arm'];done[i]=arm_t+s['wait']
  if s['res']:res_free[s['res']]=done[i]
  todo.remove(i);log.append(dict(i=i,dish=s['dish'],label=s['label'],res=s['res'],start_s=round(t0),arm_end_s=round(arm_t),done_s=round(done[i])))
 # right-shift pass (as late as possible, same total time): finished dishes should not sit and cool,
 # so every step is pushed as late as its dish successor, the arm and its heat resource allow
 end=max(done);succ={i:[j for j in range(n) if prev[j]==i] for i in range(n)}
 placed=[];resv={}
 for i in sorted(range(n),key=lambda k:-start[k]):
  s_=steps[i];lim=end-s_['wait']-s_['arm']
  for j in succ[i]:lim=min(lim,start[j]-s_['wait']-s_['arm'])
  if s_['res']:
   for (a0,a1) in resv.get(s_['res'],[]):
    if a0>=start[i]-1e-6:lim=min(lim,a0-s_['wait']-s_['arm'])
  t=lim
  for (a0,a1) in sorted(placed,key=lambda x:-x[0]):   # latest arm slot below lim that is free
   if t+s_['arm']>a0+1e-9 and t<a1-1e-9:t=a0-s_['arm']
  t=max(t,start[i]);start[i]=t;done[i]=t+s_['arm']+s_['wait'];placed.append((t,t+s_['arm']))
  if s_['res']:resv.setdefault(s_['res'],[]).append((t,done[i]))
 for e in log:e['start_s']=round(start[e['i']]);e['arm_end_s']=round(start[e['i']]+steps[e['i']]['arm']);e['done_s']=round(done[e['i']])
 ready={}
 for e in log:ready[e['dish']]=max(ready.get(e['dish'],0),e['done_s'])
 return dict(total_min=round(end/60,1),arm_busy_min=round(arm_busy/60,1),arm_share=round(arm_busy/end,2),
  dish_ready_min={k:round(v/60,1) for k,v in ready.items()},wait_before_serving_min={k:round((end-v)/60,1) for k,v in ready.items()},log=sorted(log,key=lambda e:e['start_s']))
out={k:run(v) for k,v in MEALS.items()}
os.makedirs('results/r16',exist_ok=True);TAGF=SET+(('_'+KV['ARM']) if R17 else '_checked' if CHECKED else '');json.dump(dict(set=SET,checked=CHECKED,arm_s=ARM,meals=out),open(f'results/r16/meal_{TAGF}.json','w'),indent=1,ensure_ascii=False)
for k,r in out.items():print(k,'| total',r['total_min'],'min | arm busy',r['arm_busy_min'],'min (',r['arm_share'],') | waits',r['wait_before_serving_min'])
# Gantt
try:
 from PIL import Image,ImageDraw,ImageFont
 F=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',15);FB=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
 W=1500;rowh=22;panels=[]
 for k,r in out.items():
  dishes=list(dict.fromkeys(e['dish'] for e in r['log']));H=40+rowh*(len(dishes)+1)+30;im=Image.new('RGB',(W,H),(255,255,255));d=ImageDraw.Draw(im)
  sc=(W-200)/max(r['total_min']*60,1);d.text((8,6),f"{k}：共 {r['total_min']} 分钟，机械臂忙 {r['arm_busy_min']} 分钟",fill=(0,0,0),font=FB)
  for j,dn in enumerate(['机械臂']+dishes):d.text((8,40+j*rowh),dn,fill=(0,0,0),font=F)
  for e in r['log']:
   y=40+(1+dishes.index(e['dish']))*rowh;x0=190+e['start_s']*sc;x1=190+e['arm_end_s']*sc;x2=190+e['done_s']*sc
   d.rectangle([x0,y+3,max(x1,x0+1),y+rowh-3],fill=(220,80,60));d.rectangle([x1,y+7,max(x2,x1),y+rowh-7],fill=(120,170,230))
   d.rectangle([x0,43,max(x1,x0+1),40+rowh-3],fill=(220,80,60))
  for mnt in range(0,int(r['total_min'])+1,5):x=190+mnt*60*sc;d.line([x,36,x,H-26],fill=(220,220,220));d.text((x-6,H-24),str(mnt),fill=(90,90,90),font=F)
  panels.append(im)
 G=Image.new('RGB',(W,sum(p.height for p in panels)+30),(255,255,255));y=0
 for p in panels:G.paste(p,(0,y));y+=p.height
 ImageDraw.Draw(G).text((8,y+4),'红 = 机械臂在做（含放取、翻炒、出锅、刷锅）；蓝 = 锅具自己在加热（蒸、炖、煮、焖），不占机械臂；横轴分钟。备菜切配不在图里。',fill=(60,60,60),font=F)
 os.makedirs('renders/r16',exist_ok=True);G.save(f'renders/r16/meal_{TAGF}.png');print(f'renders/r16/meal_{TAGF}.png')
except Exception as e:print('gantt failed',e)
