import json, sys, collections, datetime
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rtypes import T
from maps import M, HOME

OUT = os.path.dirname(os.path.abspath(__file__)) + '/'
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'research') + '/'
W = json.load(open(RES + 'wanggang_cooking.json'))
H = json.load(open(RES + 'homestyle_meals.json'))
TYPES = {t['id']: t for t in T}
recipes = {r['id']: r for r in W['recipes']}

dishes, problems = {}, []
nphase_total = nphase_cov = 0
for rid, calls in M.items():
    r = recipes[rid]
    out = []
    for (ph, rt, params, cov, why) in calls:
        if rt not in TYPES:
            problems.append(f'{rid}: unknown {rt}')
        out.append(dict(routine=rt, params=params, phase=ph, covered=cov, why_not=why))
    phases = set(range(len(r['phases'])))
    mapped = {c['phase'] for c in out}
    for ph in sorted(phases - mapped):
        problems.append(f'{rid}: phase {ph} unmapped')
    pc = {}
    for c in out:
        if c['phase'] is None or c['phase'] < 0:
            continue
        pc.setdefault(c['phase'], []).append(c['covered'])
    ncov = sum(1 for ph in phases if ph in pc and all(pc[ph]))
    nphase_total += len(phases); nphase_cov += ncov
    dishes[rid] = dict(dish=r['dish'], source='wanggang', n_phases=len(phases), phases_covered=ncov, calls=out)

home_total = home_cov = 0
for hid, (name, calls) in HOME.items():
    out = [dict(routine=rt, params=params, phase=ph, covered=cov, why_not=why) for (ph, rt, params, cov, why) in calls]
    for c in out:
        if c['routine'] not in TYPES:
            problems.append(f'{hid}: unknown {c["routine"]}')
    phs = sorted({c['phase'] for c in out if c['phase'] is not None and c['phase'] >= 0})
    pc = {}
    for c in out:
        if c['phase'] is not None and c['phase'] >= 0:
            pc.setdefault(c['phase'], []).append(c['covered'])
    ncov = sum(1 for ph in phs if all(pc[ph]))
    home_total += len(phs); home_cov += ncov
    dishes[hid] = dict(dish=name, source='homestyle', n_phases=len(phs), phases_covered=ncov, calls=out)

# per-type usage
inst = collections.Counter(); dset = collections.defaultdict(set); quote = {}
for did, d in dishes.items():
    for c in d['calls']:
        inst[c['routine']] += 1; dset[c['routine']].add(did)
        if c['routine'] not in quote and d['source'] == 'wanggang' and c['phase'] is not None and c['phase'] >= 0:
            q = recipes[did]['phases'][c['phase']]['quote']
            if any('一' <= ch <= '鿿' for ch in q):
                quote[c['routine']] = q.split(' / ')[0][:20]
for did, d in dishes.items():   # fallback: any quote (english) or the phase action
    for c in d['calls']:
        if c['routine'] not in quote and d['source'] == 'wanggang' and c['phase'] is not None and c['phase'] >= 0:
            quote[c['routine']] = recipes[did]['phases'][c['phase']]['action'][:20]
types = []
for t in T:
    t = dict(t)
    t['dishes'] = sorted(dset[t['id']]); t['instances'] = inst[t['id']]
    t['example_quote'] = quote.get(t['id'], '')
    types.append(t)

def all_dishes_full():
    return [k for k, d in dishes.items() if d['n_phases'] and d['phases_covered'] == d['n_phases']]

st = TYPES
calls_all = [c for d in dishes.values() for c in d['calls']]
by_status_inst = collections.Counter(st[c['routine']]['status'] for c in calls_all if c['routine'] in st)
phase_calls = [c for c in calls_all if c['phase'] is not None and c['phase'] >= 0]
# a dish is "runnable in the demo today" if every call is demo/demo_ready
runnable = [k for k, d in dishes.items() if all(st[c['routine']]['status'] in ('demo', 'demo_ready') for c in d['calls'])]
RANK = ['demo', 'demo_ready', 'sim_motion_checked', 'needs_check', 'needs_hardware', 'two_hands']
phase_worst = collections.Counter(); dish_worst = collections.Counter()
for did, d in dishes.items():
    byph = collections.defaultdict(list)
    for cl in d['calls']:
        byph[cl['phase']].append(RANK.index(st[cl['routine']]['status']))
    for ph, v in byph.items():
        if ph is not None and ph >= 0:
            phase_worst[RANK[max(v)]] += 1
    dish_worst[RANK[max(max(v) for v in byph.values())]] += 1
phase_worst = {k: phase_worst[k] for k in RANK}; dish_worst = {k: dish_worst[k] for k in RANK}
stats = dict(
    n_types=len(types),
    types_by_category=dict(collections.Counter(t['category'] for t in types)),
    types_by_status=dict(collections.Counter(t['status'] for t in types)),
    wanggang=dict(recipes_mapped=sum(1 for d in dishes.values() if d['source'] == 'wanggang'), recipes_total=len(recipes),
                  phases_total=nphase_total, phases_covered=nphase_cov),
    homestyle=dict(dishes_mapped=sum(1 for d in dishes.values() if d['source'] == 'homestyle'), steps_total=home_total, steps_covered=home_cov),
    routine_calls_total=len(calls_all), routine_calls_on_phases=len(phase_calls),
    calls_by_type_status=dict(by_status_inst),
    dishes_fully_covered=sorted(all_dishes_full()), n_dishes_fully_covered=len(all_dishes_full()),
    dishes_all_calls_demo_or_demo_ready=sorted(runnable),
    covered_definition='A phase is covered when every routine call mapped to it has covered=true: a library routine runs it with one arm as written or with a stated workaround that keeps the dish. covered=false = one arm cannot do it as written (two_hands) or mid-cook knife work with no tool (cooked meat slicing, mincing). Covered does not mean executable today: see phase_worst_status.',
    phase_worst_status=phase_worst, dishes_worst_status=dish_worst,
    problems=problems,
)
lib = dict(generated=str(datetime.date.today()),
           sources=['home-cooking-robot/research/wanggang_cooking.json (42 recipes, 258 phases)',
                    'home-cooking-robot/research/homestyle_meals.json + .md (meals A/B/C, 15 dishes + rice)',
                    'home-cooking-robot/sim/r10/claude/R19_MOTION_LIBRARY.md + results/r19/prim/library_size.json (movement-set statuses)',
                    'home-cooking-robot/sim/r10/claude/R19_PREP_AUDIT.md (prep coverage)',
                    'build_day/cook_api.py ROUTINES + runs/run05/run.json (demo routines and the executed 西红柿炒蛋 sequence)'],
           types=types, dishes=dishes, stats=stats)
json.dump(lib, open(OUT + 'routines.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in stats.items() if k not in ('dishes_fully_covered',)}, ensure_ascii=False, indent=0)[:3000])

# ---------------- routines.md ----------------
L = []
A = L.append
A('# Cooking routine library (one-arm robot)\n')
A(f'Generated {lib["generated"]} from Wang Gang\'s 42 recipes (258 phases) and the three home-style 四菜一汤 meals (17 dishes incl. rice and 白灼汁). Data: `routines.json`.\n')
A('A routine is a predefined sequence that runs straight through, with parameters and a stop condition that uses only the thermometer, the clock and simple camera rules. The planner (LLM) picks the routine and its parameters; it never decides between the steps inside one.\n')
A('## Counts\n')
wg = stats['wanggang']; hs = stats['homestyle']
A(f'- **{stats["n_types"]} routine types**, {stats["routine_calls_total"]} routine calls across {len(dishes)} dishes.')
A(f'- Wang Gang: **{wg["phases_covered"]} / {wg["phases_total"]} phases covered**; all 42 recipes mapped. Home-style: {hs["steps_covered"]} / {hs["steps_total"]} steps covered.')
A(f'- Dishes fully covered (every phase): **{stats["n_dishes_fully_covered"]} / {len(dishes)}**.')
A(f'- Dishes where every call is `demo` or `demo_ready` (runnable in the build_day demo with its wok model): {", ".join(stats["dishes_all_calls_demo_or_demo_ready"])}.')
A('- "Covered" = a library routine does the phase with one arm (as written or with a workaround that keeps the dish). It does **not** mean the motions are checked: see the worst-status rows below.\n')
A('| Category | Types |\n|---|---|')
for k, v in sorted(stats['types_by_category'].items(), key=lambda kv: -kv[1]):
    A(f'| {k} | {v} |')
A('')
A('| Status | Types | Calls | Phases whose worst call has this status | Dishes whose worst call has this status |\n|---|---|---|---|---|')
for k in RANK:
    A(f'| `{k}` | {stats["types_by_status"].get(k, 0)} | {stats["calls_by_type_status"].get(k, 0)} | {phase_worst.get(k, 0)} | {dish_worst.get(k, 0)} |')
A('\nStatus meaning: `demo` = one of the 9 executable build_day routines; `demo_ready` = expressible with the demo\'s skills and wok-model ingredients; `sim_motion_checked` = every arm movement set it uses is verified (or composed from verified sets) in R19; `needs_check` = the motions exist in the design but are not verified; `needs_hardware` = equipment not designed yet; `two_hands` = one arm cannot do it as written.\n')
A('Only 3 types are `sim_motion_checked`: **steam_plate** (CARRIER_IN, LID_ON_pot, LID_OFF_pot, CARRIER_OUT, all verified), **wash_wok** and **wok_fill_water** (FAUCET_OPEN/CLOSE verified; WOK_DUMP_RINSE / WOK_FILL composed from the verified wok chain). The demo routines themselves rely on CUP_POUR_wok (not verified) and STIR_CYCLE_dice (partially verified).\n')
A('## Top 20 types by instances\n')
A('| # | Type | 中文 | Category | Status | Calls | Dishes |\n|---|---|---|---|---|---|---|')
for i, t in enumerate(sorted(types, key=lambda t: -t['instances'])[:20], 1):
    A(f'| {i} | `{t["id"]}` | {t["name_zh"]} | {t["category"]} | {t["status"]} | {t["instances"]} | {len(t["dishes"])} |')
A('\n## What blocks coverage\n')
A('**Not covered (covered=false):**\n')
for did, d in dishes.items():
    for cl in d['calls']:
        if not cl['covered'] and cl['phase'] is not None and cl['phase'] >= 0:
            A(f'- {d["dish"]} phase {cl["phase"]} — `{cl["routine"]}`: {cl["why_not"]}')
A('\n**two_hands types** (workaround in brackets):\n')
for t in types:
    if t['status'] == 'two_hands':
        A(f'- `{t["id"]}` ({t["instances"]} calls): {t["notes"]}')
A('\n**needs_hardware types:**\n')
for t in types:
    if t['status'] == 'needs_hardware':
        A(f'- `{t["id"]}` ({t["instances"]} calls) — {t["hardware_needed"]}. {t["notes"]}')
A('\n**Biggest needs_check families** (design exists, motions not verified): cup pour into the wok (every add_off_heat-based routine), the shreds/leafy stir stroke, wok lid on/off (braise_lid), spider scoop from the wok and the fryer (deep_fry, poach_slices, fish_out_item), hot-oil pour over a bowl (forearm hit the bowl in R17), drum loading.\n')
A('## 西红柿炒蛋 (xihongshichaodan) sequence\n')
A('Same calls as the executed build_day run05, regrouped by Wang Gang\'s 6 phases. Phase 4 uses the new `thicken` routine (drum release + stir with the gloss stop) where run05 used `drum_add_stir`.\n')
A('| Phase | Routine | Params |\n|---|---|---|')
for cl in dishes['xihongshichaodan']['calls']:
    p = {k: v for k, v in cl['params'].items() if k != 'note'}
    ps = json.dumps(p, ensure_ascii=False)
    if len(ps) > 140: ps = ps[:137] + '…'
    A(f'| {"prep" if cl["phase"] < 0 else cl["phase"]} | `{cl["routine"]}` | {ps} |')
A('\nOther egg / tomato dishes: 韭菜炒鸡蛋 (all demo / demo_ready), 蛋炒饭 (demo_ready except whites/yolks separated by the user), 茄汁糖醋里脊 (deep_fry in the fryer is needs_check; the sauce part is demo_ready).\n')
A('## Notes\n')
A(f'- {sum(1 for t in types if t["instances"])} of the {len(types)} types are used by at least one dish; the unused ones are `ladle_baste` and `wok_toss` (mapped to lid / stirring instead) and `prep_wash` (washing is not a phase in either source).')
A('- `mise_en_place` is written out only for the egg dishes; the other dishes assume their cups and drum are loaded the same way, and their knife work is in the prep_* types (most are [missing] in R19_PREP_AUDIT).')
A('- Every 颠锅 is mapped to scrape-stroke stirring; deep oil in the wok is moved to the fryer.')
A('- Long simmer / braise phases use the half-power rule only when food is unstirred at > 0.5 heat; the boil-dry guard is a thermometer rise above ~110 °C.')
A('- Statuses come from `results/r19/prim/library_size.json`; the per-dish mapping is a proposal and has not been run.')
open(OUT + 'routines.md', 'w').write('\n'.join(L) + '\n')
