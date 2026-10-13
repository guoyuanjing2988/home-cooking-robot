"""R19 power budget per meal (GitHub #17): can the R18 meals (meal16.py SET=stew ARM=r18 USERRICE=1) be powered from a
Singapore flat's kitchen circuits, and what does a power cap cost in meal time?
Inputs: results/r16/meal_stew_r18_userrice.json (the schedule) and meal16's own step lists and list scheduler. meal16.py is
executed only up to its output section ('out={k:run(v)...'), so it is not modified and none of its outputs are rewritten.
Every step gets a power profile (segments relative to its start; preheats sit before it). Each appliance has a rated draw
(LOADS, tagged [M] maker/listing, [O] secondary or search-snippet source, [E] estimate) and a duty pattern (all [E]).
Two views of every load:
 avg = mean over about a minute: what heats a breaker; low induction settings counted at their average;
 pk  = worst instant: pulsed settings at their pulse power, all pulses aligned (conservative upper bound).
Plans P0/P1/P2 put the loads on circuits; MAIN (the flat's main switch, 40 or 63 A) carries every load plus BG W for the
rest of the flat. Reported per meal and circuit: the 1 s peak and the 15 min max (kW and A at 230 V).
Capped re-schedule: meal16's forward list scheduler and right-shift pass with one change: a step (with its preheat) is placed
only where every circuit stays <= its rating in the chosen view. With no cap it reproduces meal16 exactly (asserted).
Time cost = capped total - meal16 total.
python r19power.py [BG=1500] -> results/r19/power[/bg<BG>]/r19power.json, timeline_<A|B|C>.csv, timeline.png"""
import sys,os,json,math
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
os.chdir(os.path.dirname(os.path.abspath(__file__)))
KV=dict(a.split('=',1) for a in sys.argv[1:]);BG=float(KV.get('BG',1500))
OUT='results/r19/power'+('' if BG==1500 else f'/bg{BG:.0f}');os.makedirs(OUT,exist_ok=True)   # BG sensitivity runs go to a subfolder

# ---- meal16 logic (executed, not copied) ----
src=open('meal16.py',encoding='utf-8').read();cut=src.index('\nout={k:run(v)')
_argv=sys.argv;sys.argv=['meal16.py','SET=stew','ARM=r18','USERRICE=1'];M16={'__name__':'meal16_lib'}
exec(compile(src[:cut],'meal16.py','exec'),M16);sys.argv=_argv
MEALS,A,run16=M16['MEALS'],M16['A'],M16['run']
BASE=json.load(open('results/r16/meal_stew_r18_userrice.json',encoding='utf-8'))

# ---- loads: rated W at 230 V, power factor, source ----
V=230.;R220=(230/220)**2   # China-rated resistive heaters draw (230/220)^2 more at Singapore's 230 V
LOADS={
 'wok':   dict(W=3500,pf=.97,src='[M] 美的 MC-E35D2 concave induction 3500 W (research/r15_cooking_market.md); pf [E]'),
 'zone2': dict(W=2100,pf=.97,src='[M] 米家电磁炉2 2100 W, MIoT (r15); BOM pick 米家电磁炉 N1 also 2100 W [O] ithome 0/788/518; pf [E]'),
 'stew':  dict(W=round(600*R220),pf=1.,src='[E] 4-cup water-bath stew pot, 600 W at 220 V (a 1.2 L Tonze unit is 300 W [O]); x(230/220)^2'),
 'rice':  dict(W=round(650*R220),pf=1.,src='[O] 米家电饭煲 C1 3 L (MDFBZ02ACM) 650 W at 220 V (listing snippet); x(230/220)^2'),
 'fryer': dict(W=2300,pf=1.,src='[O] Tefal Oleoclean Pro FR8040 2300 W, 3.5 L (galaxus / mediamarkt / mydealz listings)'),
 'kettle':dict(W=2200,pf=1.,src='[O] 1.7 L kettle, Philips HD9350 class 2200 W at 220-240 V (retail listings)'),
 'robot': dict(W=984,pf=.95,src='UR5e 200 W typical / 570 W max [M datasheet]; IPC+sensors 60 W, gripper 24 W, drive supply 270 W [hardware.py allowances]; '
                                 'brake coils 40 W + safety sensors 20 W [E]; controller off-board on the same feed; pf [E]'),
 'station':dict(W=150,pf=.9,src='[E] seasoning station 24 V PSU: dosing peak 150 W (doses during prep), 15 W idle'),
 'fridge':dict(W=150,pf=.7,src='[E] single-door fridge, 150 W running, ~40 % duty; compressor start 5-8x for <1 s'),
 'hood':  dict(W=160,pf=.9,src='[O] slim hood class Fujioh FR-SC2090 85/125/160 W (hkele listing); run on high all meal [E]'),
 'misc':  dict(W=30,pf=.9,src='[E] knob servo, stove guard, smart plugs, kitchen light'),
}
# duty patterns (avg W, pk W), all [E] unless noted. Heat policy (DECISIONS 10-12): half power whenever the spatula stops;
# the spatula is idle a median 36 % of the stir window -> 0.64*3500+0.36*1750 = 2870 W.
WOK_FULL=(3500,3500);WOK_STIR=(2900,3500);WOK_BOIL=(2000,3500);WOK_BLANCH=(2500,3500);WOK_SIMMER=(800,2000)
Z2_FULL=(2100,2100);Z2_STEAM=(1200,2100);Z2_SWAP=(1500,2100)
STEW_FULL=(LOADS['stew']['W'],)*2;STEW_HOLD=(LOADS['stew']['W']*.5,LOADS['stew']['W'])
FRY=(2300,2300);KETTLE=(2200,2200)
ROBOT_IDLE=(180,300);ROBOT_INC=(370-180,984-300)   # arm busy: 200 W arm + 60 IPC + 10 grip + 40 drives + 40 brakes + 20 safety
CONT={'robot':ROBOT_IDLE,'station':(15,150),'fridge':(50,150),'hood':(160,160),'misc':(30,30)}
PRE={'zone2':360,'fryer':600,'stew_bath':960,'stew_soup':900,'kettle':270}   # preheats [E], derivation in research/r19_power_budget.md
def rice(D):
 R=LOADS['rice']['W'];f=[0,.29,.63,.8,1.];d=[.35,1.,.25,.1]   # soak, boil, simmer, rest (fractions of the 35 min cycle) [E]
 return [(f[k]*D,f[k+1]*D,'rice',d[k]*R,R) for k in range(4)]
WP,F,DU,SP=A['wok_plate'],A['fill'],A['dump'],A['spider']
def profile(m,i,s):
 """power segments (r0,r1,load,avg,pk) relative to the step start, for step i of meal m (A/B/C)"""
 a,D=s['arm'],s['arm']+s['wait'];stir=[(0,a-WP,'wok',*WOK_STIR)]
 P={('A',0):[(-PRE['stew_bath'],900,'stew',*STEW_FULL),(900,D,'stew',*STEW_HOLD)],
    ('A',1):[(-PRE['zone2'],120,'zone2',*Z2_FULL),(120,D,'zone2',*Z2_STEAM)],('A',2):rice(D),
    ('A',3):[(-PRE['fryer'],D,'fryer',*FRY)],('A',4):stir,('A',5):stir,('A',6):[(0,D,'zone2',*Z2_SWAP)],('A',7):[],
    ('A',8):[(0,D,'wok',*WOK_FULL)],('A',9):[],('A',10):[],
    ('B',0):[(-PRE['kettle'],0,'kettle',*KETTLE),(0,600,'stew',*STEW_FULL),(600,D,'stew',*STEW_HOLD)],
    ('B',1):[(F,F+120,'wok',*WOK_FULL),(F+120,D,'wok',*WOK_BOIL)],('B',2):[],
    ('B',3):[(DU,a,'wok',*WOK_STIR),(a,a+120,'wok',*WOK_FULL),(a+120,D,'wok',*WOK_SIMMER)],('B',4):rice(D),
    ('B',5):[(-PRE['zone2'],120,'zone2',*Z2_FULL),(120,D,'zone2',*Z2_STEAM)],('B',6):stir,('B',7):[],
    ('B',8):[(0,D,'wok',*WOK_FULL)],('B',9):stir,('B',10):[(F,F+120,'wok',*WOK_FULL),(F+120,D,'wok',*WOK_BOIL)],
    ('B',11):[(0,2*A['pour']+90+SP,'wok',*WOK_BLANCH)],('B',12):[],
    ('C',0):[(-PRE['zone2'],120,'zone2',*Z2_FULL),(120,D,'zone2',*Z2_STEAM)],('C',1):rice(D),
    ('C',2):[(F,F+120,'wok',*WOK_FULL),(F+120,D,'wok',*WOK_BOIL)],
    ('C',3):[(0,30,'wok',*WOK_BOIL),(30+SP+DU,a-WP,'wok',*WOK_STIR)],
    ('C',4):[(-PRE['stew_soup'],D,'stew',*STEW_FULL)],('C',5):[(0,D,'stew',*STEW_FULL)],('C',6):stir,('C',7):stir,
    ('C',8):[(0,60,'wok',*WOK_FULL)]}[(m,i)]   # C8: hot oil heated in the wok for the ribs
 return P+([(0,a,'robot',*ROBOT_INC)] if a>0 else [])
LABEL={('A',0):'4 cups into',('A',3):'fry potato',('A',8):'rinse wok; heat 40 g oil',('B',0):'scalded ribs',
 ('B',3):'wok emptied',('B',11):'blanch and lift',('C',3):'blanch 30 s',('C',4):'stew pot (water in',('C',8):'out (lid), chili'}

# ---- circuit plans ----
SMALL=['robot','station','fridge','hood','misc']
PLANS={
 'P0':dict(desc='repo today: new 20 A wok point; every other load on the existing kitchen socket circuit (2 outlets)',
           circ={'WOK':(20,['wok']),'KIT':(20,['zone2','fryer','stew','rice','kettle']+SMALL)}),
 'P1':dict(desc='+1 new 20 A radial for the two big plug-in heaters (zone 2, fryer)',
           circ={'WOK':(20,['wok']),'NEW1':(20,['zone2','fryer']),'KIT':(20,['stew','rice','kettle']+SMALL)}),
 'P2':dict(desc='+2 new 20 A radials: heaters split three ways',
           circ={'WOK':(20,['wok']),'NEW1':(20,['zone2','stew']),'NEW2':(20,['fryer','kettle']),'KIT':(20,['rice']+SMALL)})}
MAINS={'40A':40,'63A':63}
def circuits(plan,main_A):
 c=dict(PLANS[plan]['circ']);c['MAIN']=(main_A,list(LOADS)+['bg']);return c
AMP={k:1/(V*v['pf']) for k,v in LOADS.items()};AMP['bg']=1/(V*.95)
FL=lambda t:math.floor(t+1e-9)
T0,N=-3600,4*3600   # 1 s grid from t=-1 h (setup window before the meal clock) to +3 h

def rel_arrays(segs):
 """per load: (rmin, avg array, pk array) on the 1 s grid"""
 segs=[(math.ceil(r0-1e-9),math.floor(r1+1e-9),ld,av,pk) for r0,r1,ld,av,pk in segs]   # floor/ceil: back-to-back steps never overlap
 segs=[g for g in segs if g[1]>g[0]]
 if not segs:return 0,{}
 lo=min(s[0] for s in segs);hi=max(s[1] for s in segs);out={}
 for r0,r1,ld,av,pk in segs:
  a=out.setdefault(ld,(np.zeros(hi-lo),np.zeros(hi-lo)));a[0][r0-lo:r1-lo]+=av;a[1][r0-lo:r1-lo]+=pk
 return lo,out
class Grid:
 """per-circuit current on the 1 s grid for one view (avg / pk), with placement and feasibility checks"""
 def __init__(s,rels,circ,view):
  s.cap={c:v[0] for c,v in circ.items()};s.k=1 if view=='pk' else 0;s.rel={}
  s.tot={c:np.full(N,sum(CONT[l][s.k]*AMP[l] for l in v[1] if l in CONT)+(BG*AMP['bg'] if 'bg' in v[1] else 0.)) for c,v in circ.items()}
  for i,(lo,arr) in rels.items():
   s.rel[i]=(lo,{c:sum(arr[l][s.k]*AMP[l] for l in v[1] if l in arr) for c,v in circ.items() if any(l in arr for l in v[1])})
 def put(s,i,t,sg):
  lo,cs=s.rel[i];k=FL(t)+lo-T0
  for c,a in cs.items():s.tot[c][k:k+len(a)]+=sg*a
 def ok(s,i,t):
  lo,cs=s.rel[i];k=FL(t)+lo-T0
  return all(np.max(s.tot[c][k:k+len(a)]+a)<=s.cap[c]+1e-9 for c,a in cs.items())
 def okmany(s,i,t0,K):   # integer starts t0..t0+K-1
  lo,cs=s.rel[i];k=t0+lo-T0;m=np.ones(K,bool)
  for c,a in cs.items():m&=(sliding_window_view(s.tot[c][k:k+K+len(a)-1],len(a))+a).max(1)<=s.cap[c]+1e-9
  return m
 def earliest(s,i,t0):
  if s.ok(i,t0):return t0
  c0=math.floor(t0)+1
  while c0<N+T0-4600:   # the longest profile (meal B soup + kettle) is < 4000 s
   m=s.okmany(i,c0,600)
   if m.any():return float(c0+np.argmax(m))
   c0+=600
  raise RuntimeError('no feasible start')
 def latest(s,i,t,lo_t,placed,arm):
  ts=np.arange(math.ceil(lo_t),math.floor(t)+1)
  if not len(ts):return lo_t
  bad=np.zeros(len(ts),bool)
  for a0,a1 in placed:bad|=(ts+arm>a0+1e-9)&(ts<a1-1e-9)
  okp=np.concatenate([s.okmany(i,int(ts[j]),min(600,len(ts)-j)) for j in range(0,len(ts),600)])
  good=np.where(~bad&okp)[0]
  return float(ts[good[-1]]) if len(good) else lo_t

def sched(steps,rels=None,circ=None,view='avg'):
 """meal16.run() (forward list scheduler + right-shift pass) with an optional per-circuit current cap"""
 n=len(steps);done=[None]*n;start=[None]*n;arm_t=0.;res_free={};arm_busy=0.;prev={};last={}
 G=Grid(rels,circ,view) if circ else None
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
   if G:t0=G.earliest(i,t0)
   if best is None or t0<best[0]-1e-9:best=(t0,i)
  t0,i=best;s=steps[i];start[i]=t0;arm_t=t0+s['arm'];arm_busy+=s['arm'];done[i]=arm_t+s['wait']
  if G:G.put(i,t0,1)
  if s['res']:res_free[s['res']]=done[i]
  todo.remove(i)
 end=max(done);succ={i:[j for j in range(n) if prev[j]==i] for i in range(n)};placed=[];resv={}
 for i in sorted(range(n),key=lambda k:-start[k]):
  s_=steps[i];lim=end-s_['wait']-s_['arm']
  for j in succ[i]:lim=min(lim,start[j]-s_['wait']-s_['arm'])
  if s_['res']:
   for (a0,a1) in resv.get(s_['res'],[]):
    if a0>=start[i]-1e-6:lim=min(lim,a0-s_['wait']-s_['arm'])
  t=lim
  for (a0,a1) in sorted(placed,key=lambda x:-x[0]):
   if t+s_['arm']>a0+1e-9 and t<a1-1e-9:t=a0-s_['arm']
  if G and t>start[i]+1e-9:
   G.put(i,start[i],-1)
   if not G.ok(i,t):t=G.latest(i,t,start[i],placed,s_['arm'])
   G.put(i,max(t,start[i]),1)
  t=max(t,start[i]);start[i]=t;done[i]=t+s_['arm']+s_['wait'];placed.append((t,t+s_['arm']))
  if s_['res']:resv.setdefault(s_['res'],[]).append((t,done[i]))
 return start,done,end,arm_busy

def load_arrays(rels,start):
 """per load (avg, pk) W on the grid for a placed schedule, continuous loads and BG included"""
 L={l:(np.full(N,float(CONT[l][0])),np.full(N,float(CONT[l][1]))) if l in CONT else (np.zeros(N),np.zeros(N)) for l in LOADS}
 L['bg']=(np.full(N,BG),np.full(N,BG))
 for i,(lo,arr) in rels.items():
  k=FL(start[i])+lo-T0
  for l,(av,pk) in arr.items():L[l][0][k:k+len(av)]+=av;L[l][1][k:k+len(pk)]+=pk
 return L
def window(rels,start,end):
 lo=min([FL(start[i])+r[0] for i,r in rels.items() if r[1]]+[0]);return lo-T0,int(math.ceil(end))-T0
def circuit_report(L,circ,w,bg=None):
 rep={};a,b=w
 for c,(lim,lds) in circ.items():
  av=sum(L[l][0][a:b]*AMP[l] for l in lds if l!='bg');pk=sum(L[l][1][a:b]*AMP[l] for l in lds if l!='bg')
  avW=sum(L[l][0][a:b] for l in lds if l!='bg');pkW=sum(L[l][1][a:b] for l in lds if l!='bg')
  if 'bg' in lds:b_=BG if bg is None else bg;av=av+b_*AMP['bg'];pk=pk+b_*AMP['bg'];avW=avW+b_;pkW=pkW+b_
  k=min(900,len(av));r15=np.convolve(av,np.ones(k)/k,'valid');r15W=np.convolve(avW,np.ones(k)/k,'valid')
  rep[c]=dict(limit_A=lim,peak_A=round(float(pk.max()),1),peak_kW=round(float(pkW.max())/1e3,2),avg1min_max_A=round(float(av.max()),1),
   max15_A=round(float(r15.max()),1),max15_kW=round(float(r15W.max())/1e3,2),s_over_avg=int((av>lim+1e-9).sum()),s_over_pk=int((pk>lim+1e-9).sum()),
   verdict='ok' if pk.max()<=lim+1e-9 else 'peak over (pulses aligned), 1-min mean ok' if av.max()<=lim+1e-9 else
           'over for minutes, 15-min mean ok' if r15.max()<=lim+1e-9 else 'over: 15-min mean above rating')
 return rep
def summary(steps,start,done,end):
 ready={}
 for i,s in enumerate(steps):ready[s['dish']]=max(ready.get(s['dish'],0),done[i])
 return dict(total_min=round(end/60,1),wait_before_serving_min={k:round((end-v)/60,1) for k,v in ready.items()})

res=dict(note=__doc__.split('\n')[0],bg_W=BG,volt=V,loads=LOADS,duty=dict(WOK_FULL=WOK_FULL,WOK_STIR=WOK_STIR,WOK_BOIL=WOK_BOIL,
 WOK_BLANCH=WOK_BLANCH,WOK_SIMMER=WOK_SIMMER,Z2_FULL=Z2_FULL,Z2_STEAM=Z2_STEAM,Z2_SWAP=Z2_SWAP,STEW_FULL=STEW_FULL,STEW_HOLD=STEW_HOLD,
 FRY=FRY,KETTLE=KETTLE,ROBOT_IDLE=ROBOT_IDLE,ROBOT_INC=ROBOT_INC,CONT=CONT,preheat_s=PRE),plans={k:v['desc'] for k,v in PLANS.items()},meals={})
for key,steps in MEALS.items():
 m=key[0]
 for (mm,i),lab in LABEL.items():
  if mm==m:assert steps[i]['label'].startswith(lab),(m,i,steps[i]['label'])   # meal16 step lists changed: re-map profile()
 rels={i:rel_arrays(profile(m,i,s)) for i,s in enumerate(steps)}
 # validation: uncapped sched() == meal16.run() == the saved JSON
 st,dn,end,ab=sched(steps);r16=run16(steps)
 for e in r16['log']:assert abs(round(st[e['i']])-e['start_s'])<=0 and abs(round(dn[e['i']])-e['done_s'])<=0
 for e,f in zip(r16['log'],BASE['meals'][key]['log']):assert (e['i'],e['start_s'],e['done_s'])==(f['i'],f['start_s'],f['done_s'])
 L=load_arrays(rels,st);w=window(rels,st,end)
 out=dict(total_min=round(end/60,1),window_s=[w[0]+T0,w[1]+T0],energy_kWh={l:round(float(L[l][0][w[0]:w[1]].sum())/3.6e6,2) for l in LOADS},
  kitchen_peak_kW=round(float(sum(L[l][1][w[0]:w[1]] for l in LOADS).max())/1e3,2),
  kitchen_avg1min_max_kW=round(float(sum(L[l][0][w[0]:w[1]] for l in LOADS).max())/1e3,2),baseline={},capped={})
 out['kitchen_energy_kWh']=round(sum(out['energy_kWh'].values()),2)
 for p in PLANS:
  out['baseline'][p]=circuit_report(L,circuits(p,40),w)
 out['baseline_main_bg']={f'{bg:.0f}W':{mn:circuit_report(L,{'MAIN':circuits('P1',ma)['MAIN']},w,bg)['MAIN'] for mn,ma in MAINS.items()} for bg in (0,1500,3000)}
 for p in PLANS:
  for mn,ma in MAINS.items():
   for view in ('avg','pk'):
    circ=circuits(p,ma);cs,cd,ce,_=sched(steps,rels,circ,view);Lc=load_arrays(rels,cs);wc=window(rels,cs,ce)
    rep=circuit_report(Lc,circ,wc);assert all(r['s_over_'+view]==0 for r in rep.values()),(m,p,mn,view)
    sm=summary(steps,cs,cd,ce);base=summary(steps,st,dn,end)
    moved=[dict(step=i,dish=steps[i]['dish'],label=steps[i]['label'][:48],start_min=round(st[i]/60,1),capped_start_min=round(cs[i]/60,1))
           for i in range(len(steps)) if abs(cs[i]-st[i])>30]
    out['capped'][f'{p}_{mn}_{view}']=dict(total_min=sm['total_min'],growth_min=round(sm['total_min']-base['total_min'],1),
     max_wait_min=max(sm['wait_before_serving_min'].values()),base_max_wait_min=max(base['wait_before_serving_min'].values()),
     wait_before_serving_min=sm['wait_before_serving_min'],moved=moved,circuits={c:dict(peak_A=r['peak_A'],max15_A=r['max15_A']) for c,r in rep.items()})
 res['meals'][key]=out
 # 1 s timeline of the meal16 schedule
 with open(f'{OUT}/timeline_{m}.csv','w',encoding='utf-8') as f:
  f.write('t_s,'+','.join(f'{l}_avg_W' for l in LOADS)+',kitchen_avg_W,kitchen_pk_W\n')
  for k in range(w[0],w[1]):
   f.write(f'{k+T0},'+','.join(f'{L[l][0][k]:.0f}' for l in LOADS)+f',{sum(L[l][0][k] for l in LOADS):.0f},{sum(L[l][1][k] for l in LOADS):.0f}\n')
 res['meals'][key]['_L']=(L,w)
json.dump({**res,'meals':{k:{a:b for a,b in v.items() if a!='_L'} for k,v in res['meals'].items()}},open(f'{OUT}/r19power.json','w',encoding='utf-8'),indent=1,ensure_ascii=False)

# ---- console summary ----
for key,o in res['meals'].items():
 print(f"\n{key}: {o['total_min']} min, kitchen energy {o['kitchen_energy_kWh']} kWh, meal-window {o['window_s']} s")
 for p in PLANS:
  print(' ',p,' | '.join(f"{c} pk {r['peak_A']} A / 15min {r['max15_A']} A ({r['verdict']})" for c,r in o['baseline'][p].items()))
 print('  MAIN 40A by BG:',{bg:(r['40A']['peak_A'],r['40A']['max15_A'],r['40A']['verdict']) for bg,r in o['baseline_main_bg'].items()})
 for k,c in o['capped'].items():print(f"  capped {k}: {c['total_min']} min (+{c['growth_min']}), max wait {c['max_wait_min']} (was {c['base_max_wait_min']}), moved {len(c['moved'])}")

# ---- figure: meal16 schedule, mean power by appliance (stacked) and the worst instant (line) ----
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['Microsoft YaHei','DejaVu Sans']
GROUPS=[('wok','wok 3.5 kW',['wok']),('zone2','zone 2',['zone2']),('fryer','fryer',['fryer']),('stew','stew pot',['stew']),
 ('rice','rice cooker',['rice']),('kettle','kettle',['kettle']),('robot','robot + station',['robot','station']),('other','fridge, hood, misc',['fridge','hood','misc'])]
COL=['#2a78d6','#eb6834','#1baf7a','#eda100','#e87ba4','#008300','#4a3aa7','#e34948']   # dataviz reference categorical order
SURF,INK,INK2,GRID='#fcfcfb','#0b0b0b','#52514e','#e4e3df'
fig,axs=plt.subplots(3,1,figsize=(11,9.5),sharex=True,facecolor=SURF)
for ax,(key,o) in zip(axs,res['meals'].items()):
 L,(a,b)=o['_L'];t=(np.arange(a,b)+T0)/60;ys=[sum(L[l][0][a:b] for l in g[2])/1e3 for g in GROUPS]
 ax.set_facecolor(SURF);ax.stackplot(t,ys,colors=COL,labels=[g[1] for g in GROUPS],edgecolor=SURF,linewidth=.6)
 ax.plot(t,sum(L[l][1][a:b] for l in LOADS)/1e3,color=INK,lw=1,label='worst instant (pulses aligned)')
 for lim,ls in ((40,'--'),(63,':')):
  y=(lim*V-BG)/1e3;ax.axhline(y,color=INK2,lw=1,ls=ls);ax.text(-9.5,y+.15,f'{lim} A main minus {BG/1e3:.1f} kW for the rest of the flat',color=INK2,fontsize=8)
 ax.set_title(f"Meal {key}  ({o['total_min']} min, meal16 schedule)",loc='left',fontsize=10,color=INK)
 ax.set_ylabel('kW',color=INK2);ax.set_ylim(0,14);ax.grid(axis='y',color=GRID,lw=.6);ax.tick_params(colors=INK2)
 for sp in ax.spines.values():sp.set_visible(False)
axs[0].legend(loc='upper right',ncol=2,fontsize=8,frameon=False,bbox_to_anchor=(1,.86))
axs[-1].set_xlabel('minutes from the meal start (negative = preheats during setup)',color=INK2);axs[-1].set_xlim(-10,78)
fig.text(.01,.005,'Stacked areas = about-1-min mean draw per appliance; line = worst instant (all pulsed settings at pulse power). Duty patterns estimated; see research/r19_power_budget.md. Data: timeline_<meal>.csv',fontsize=7.5,color=INK2)
fig.tight_layout(rect=(0,.02,1,1));fig.savefig(f'{OUT}/timeline.png',dpi=130,facecolor=SURF);print(f'{OUT}/timeline.png')
