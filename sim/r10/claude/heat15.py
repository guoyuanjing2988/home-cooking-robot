"""R15 wok heat budget: a lumped (0-D) model to compare heat sources and to size the heat
policy for one-arm cooking. It is an estimate, not a heat-transfer simulation.
Nodes: the wok (steel + oil in it) and the food. Values and their basis:
 - power into the wok = rated power x transfer efficiency from water-boiling tests
   (r15_cooking_market.md 1.4): induction 3.5 kW x 0.85 (Frontier 2019 / EPRI 2014: 83-86 %);
   the user's gas wok burner 5.0 kW LPG or 3.8 kW town gas (Fujioh SG manual) x 0.32. The
   lower pan-test efficiencies (48-54 % / 23 %) include losses that are modelled here explicitly.
 - wok: 34 cm carbon steel 1.5 kg (r15 market 4.1: 1.47-2.2 kg), cp 490 J/kgK; oil 30 g,
   cp 2000; inner surface 0.119 m^2 (spherical cap); losses = convection 10 W/m^2K + radiation
   (emissivity 0.8, seasoned steel, market 4.4) from the inner surface to 30 °C air.
 - food: 355 g (median stated wok load in wanggang_cooking.md), cp 3500 J/kgK, from the fridge
   at 5 °C or the counter at 25 °C. Heat into the food = h_c x contact area x (T_wok - T_food)
   with h_c = 300 W/m^2K (ASSUMED; run with 150 and 600) and contact area = 0.6 (the stir
   bench's hot-contact share for dice) x 101 dice faces of 2.25 cm^2. The food node is held
   at 100 °C while it loses its first 8 % of mass as steam (latent heat 2.26 MJ/kg) - the
   evaporation plateau of stir-frying (ASSUMED share).
Outputs (results/r15/heat.json):
 1. heat-up of the empty wok + oil from 30 °C to 180 °C (Wang Gang's 6成热);
 2. drop and recovery after the food goes in at a 200 °C wok, and time for the food node
    to pass 75 °C (a doneness proxy), per heat source;
 3. cooling with the heat off (离火: induction to 0 or the wok lifted off a gas flame are
    the same case - in both the wok only loses heat);
 4. wok temperature change over a 6 s arm-busy stir pause at 100 / 50 / 0 % power."""
import json,os,numpy as np
SIG=5.67e-8;TA=30.
SRC={'induction 3.5 kW':3.5e3*.85,'gas LPG 5.0 kW':5.0e3*.32,'gas town 3.8 kW':3.8e3*.32}
CW=1.5*490+.03*2000;AW=2*np.pi*.20*(.20-np.sqrt(.20**2-.17**2))
def loss(T):return AW*(10*(T-TA)+.8*SIG*((T+273.15)**4-(TA+273.15)**4))
def run(P,Tw0,food=None,hc=300.,t_end=600.,dt=.05,stop=None,power_fn=None):
 Tw=Tw0;mf=.355;Tf=None if food is None else food;evap=0.;A=.6*101*2.25e-4;t=0.;hist=[]
 while t<t_end:
  p=P if power_fn is None else power_fn(t)*P
  q=0.
  if Tf is not None:
   q=hc*A*(Tw-Tf)
   if Tf<100:Tf+=q*dt/(mf*3500)
   elif evap<.08*mf:evap+=q*dt/2.26e6
   else:Tf+=q*dt/(mf*(1-.08)*3500)
  Tw+=(p-loss(Tw)-q)*dt/CW;t+=dt;hist.append((t,Tw,Tf))
  if stop and stop(t,Tw,Tf):break
 return hist
out={}
for name,P in SRC.items():
 r=dict(power_into_wok_W=round(P))
 h=run(P,TA,stop=lambda t,Tw,Tf:Tw>=180);r['heatup_30_to_180C_s']=round(h[-1][0],1) if h[-1][1]>=180 else None
 h=run(P,TA,t_end=1800,stop=lambda t,Tw,Tf:t>1200);r['steady_empty_wok_C']=round(h[-1][1])   # where losses = input (cut-offs ignored)
 for Tf0 in (5.,25.):
  for hc in (150.,300.,600.):
   h=run(P,200.,food=Tf0,hc=hc,t_end=900)
   T=np.array([x[1] for x in h]);ts=np.array([x[0] for x in h]);F=np.array([x[2] for x in h])
   i_min=int(np.argmin(T));rec=next((ts[i] for i in range(i_min,len(T)) if T[i]>=180),None)
   r[f'food{Tf0:g}C_hc{hc:g}']=dict(wok_min_C=round(float(T.min())),t_min_s=round(float(ts[i_min]),1),back_to_180C_s=None if rec is None else round(float(rec),1),
    food_75C_s=round(float(next((ts[i] for i in range(len(F)) if F[i]>=75),np.nan)),1),wok_at_120s_C=round(float(T[min(len(T)-1,int(120/.05))])))
 out[name]=r
# 3. heat off with the food in (same physics whatever the source)
h=run(0.,200.,food=60.,t_end=60);T=np.array([x[1] for x in h]);out['heat_off_from_200C']=dict(after_5s_C=round(float(T[int(5/.05)]),1),after_10s_C=round(float(T[int(10/.05)]),1),after_30s_C=round(float(T[int(30/.05)]),1),
 note='food at 60 °C in the wok; induction set to 0 and a wok lifted off a gas flame both follow this curve')
h=run(0.,200.,t_end=60);T=np.array([x[1] for x in h]);out['heat_off_empty_200C']=dict(after_5s_C=round(float(T[int(5/.05)]),1),after_10s_C=round(float(T[int(10/.05)]),1),after_30s_C=round(float(T[int(30/.05)]),1))
# 4. a 6 s stir pause at 200 °C with the food at 80 °C: heat into the food halves (fewer pieces on the hot zone, none turned)
for frac in (1.,.5,0.):
 h=run(SRC['induction 3.5 kW'],200.,food=80.,hc=150.,t_end=6,power_fn=lambda t:frac)
 out.setdefault('pause_6s_induction',{})[f'power_{int(frac*100)}pct']=dict(wok_end_C=round(h[-1][1],1),change_C=round(h[-1][1]-200,1))
os.makedirs('results/r15',exist_ok=True);json.dump(out,open('results/r15/heat.json','w'),indent=1,ensure_ascii=False);print(json.dumps(out,indent=1,ensure_ascii=False))
