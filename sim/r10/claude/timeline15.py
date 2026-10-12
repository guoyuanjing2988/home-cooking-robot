"""R15 one-arm stir-fry timeline: how long the spatula stops while the single arm fetches and
pours each addition, for Wang Gang's stir-fried dishes (research/wanggang_cooking.json phases +
research/wanggang_recipes.json wok events + R14 timeline drum counts).
Stir window = summed duration of the wok phases where he stirs (翻炒/推炒/划散); a phase with
no stated or estimated time counts as 30 s (ASSUMED, flagged per recipe).
Arm trips inside the window: every main-ingredient addition after the first, plus the
seasoning additions (R14: single cups, or the 4-compartment pour drum where R14 needs one).
Pause per trip (ASSUMED handling times, as in R14): cup 9 s (park the spatula on the rim 1 s,
fetch 3, pour 1.5, return 2.5, re-grasp 1), drum 14 s (+1.5 s per extra compartment),
main-ingredient bowl or tray 10 s.
Policies: A = the arm does every addition; B = a servo pour-drum holder next to the wok
(the arm loads the drums before the stir-fry starts; the servo rolls them on time), so only
main ingredients stop the spatula.
python timeline15.py -> results/r15/timeline.json + table"""
import json,os,numpy as np
R=json.load(open('../../../research/wanggang_recipes.json',encoding='utf-8'))['recipes']
C={r['id']:r for r in json.load(open('../../../research/wanggang_cooking.json',encoding='utf-8'))['recipes']}
T14={r['id']:r for r in json.load(open('results/r14/timeline.json'))['recipes']}
CUP,DRUM,DRUM_EXTRA,MAIN,UNK=9.,14.,1.5,10.,30.
rows=[]
for r in R:
 ph=[p for p in C.get(r['id'],{}).get('phases',[]) if p['vessel'].startswith('wok')]
 stir=[p for p in ph if any(m['code'] in ('翻炒','推炒','划散') for m in p['manipulation'])]
 if not stir:continue
 win=sum(p['duration_s'] if p['duration_s'] is not None else UNK for p in stir);unk=sum(p['duration_s'] is None for p in stir)
 ev=[e for e in r['events'] if e['stage']=='wok'];main=sum(1 for e in ev if any('ingredient' in it for it in e['items']));seas=len(ev)-main
 drums=T14.get(r['id'],{}).get('pour_boxes',0);in_drums=min(seas,4*drums);cups=seas-in_drums
 pauseA=max(main-1,0)*MAIN+cups*CUP+drums*DRUM+max(in_drums-drums,0)*DRUM_EXTRA;tripsA=max(main-1,0)+cups+drums
 pauseB=max(main-1,0)*MAIN;tripsB=max(main-1,0)
 rows.append(dict(id=r['id'],dish=r['dish'],stir_window_s=win,phases_without_time=unk,main_additions=main,seasoning_events=seas,drums=drums,
  A=dict(trips=tripsA,pause_s=pauseA,paused_share=round(pauseA/(win+pauseA),2)),B=dict(trips=tripsB,pause_s=pauseB,paused_share=round(pauseB/(win+pauseB),2))))
agg=lambda k,p:dict(median=float(np.median([x[p][k] for x in rows])),p90=float(np.percentile([x[p][k] for x in rows],90)),max=float(max(x[p][k] for x in rows)))
out=dict(assumptions=dict(cup_s=CUP,drum_s=DRUM,drum_extra_s=DRUM_EXTRA,main_s=MAIN,unknown_phase_s=UNK),n=len(rows),n_all_times_known=sum(x['phases_without_time']==0 for x in rows),
 stir_window_s=dict(median=float(np.median([x['stir_window_s'] for x in rows])),max=float(max(x['stir_window_s'] for x in rows))),
 A={k:agg(k,'A') for k in ('trips','pause_s','paused_share')},B={k:agg(k,'B') for k in ('trips','pause_s','paused_share')},recipes=rows)
os.makedirs('results/r15',exist_ok=True);json.dump(out,open('results/r15/timeline.json','w'),indent=1,ensure_ascii=False)
print(json.dumps({k:v for k,v in out.items() if k!='recipes'},ensure_ascii=False,indent=1))
for x in rows:print(f"{x['dish'][:8]:<9} window {x['stir_window_s']:>5.0f}s{'*' if x['phases_without_time'] else ' '} main {x['main_additions']} seas {x['seasoning_events']:>2} drums {x['drums']} | A trips {x['A']['trips']:>2} pause {x['A']['pause_s']:>5.1f}s ({x['A']['paused_share']:.0%}) | B trips {x['B']['trips']} pause {x['B']['pause_s']:>4.0f}s ({x['B']['paused_share']:.0%})")
