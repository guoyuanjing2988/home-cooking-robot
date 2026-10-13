"""R19 seasoning-station options: recipe coverage and seasoning-related arm moves per meal/dish.
Uses the event lists of r19seas_usage.py (home-style hand-coded; Wang Gang from the JSON).
All move counts are a bookkeeping MODEL (est.), not checked paths:
  cup      = empty cup to the port, filled cup to staging, pour at the wok + return  -> 3 moves, ~22 s
             (R14 timeline14 rates: 6 + 8 s staging, 8 s pour)
  drum     = drum to the port, drum to the wok holder, drum back                     -> 3 moves, ~22 s, <= 4 compartments
  vessel   = the dish's own bowl/plate carried to the port and back                  -> 2 moves, ~14 s
  squeeze  = arm fetches a squeeze bottle, squeezes over a cup on the port scale, returns it -> +2 moves, ~15 s
  nozzle / wok-side portioner / sachet dropper                                       -> 0 moves
Usage: python r19seas_options.py -> results/r19seas/options.json + markdown on stdout"""
import json, os, statistics as st, collections
from r19seas_usage import HS, wg_events

S_CUP, S_DRUM, S_VESSEL, S_SQUEEZE = 22, 22, 14, 15
WOKBOUND = {'wok', 'finish', 'bowl_prep', 'blanch', 'boil', 'fryer'}       # dose ends up in the wok (or wok water)
OFF_SAUCE = {'sauce', 'plate'}                                            # sauces over steamed/blanched dishes (home-style)
OFF_VESSEL = {'marinade', 'coat', 'dressing', 'bowl', 'cups'}             # dose goes into the dish's own bowl/cups
OFF_POT = {'pot'}                                                         # soup pot on zone 2 / stew pot

LIQ_CORE = {'oil', '盐', '白糖', '冰糖', '糖色', '生抽', '老抽', '料酒', '醋(白)', '醋(深色)', '醋(未注明)', '蚝油', '淀粉', '蒸鱼豉油', '鱼酱油', '葱油', '猪油'}
# 葱油/猪油 -> cooking oil, 鱼酱油 -> 生抽, 冰糖/糖色 -> syrup: substitutions (est.)
CONFIGS = {
 # today's R14 station: 12 liquid + oil, 4 augers, 2 syringes (1 fixed 豆瓣 + 1 swap cartridge), 花椒 feeder; rest = user kit cups
 'a_today': dict(liquid=LIQ_CORE - {'蒸鱼豉油'} | {'味精', '香油', '红油', '花椒油'},
                 subs={'蒸鱼豉油': 'liquid'},
                 auger={'鸡精', '胡椒粉', '花椒面'}, paste={'豆瓣酱', '甜面酱'}, feeder={'花椒'},
                 swap_paste={'番茄酱', '黄豆酱'}, kit=None, delivery='cup+drum'),
 # right-sized, still cup/drum delivery: 11 liquids, 2 whole-spice portioners, pepper grinder, sachet magazine, squeeze bottles
 'b_rightsized': dict(liquid=LIQ_CORE, subs={'鸡精': None, '味精': None}, auger=set(), grinder={'胡椒粉', '花椒面'},
                      feeder={'花椒', '干辣椒'}, sachet={'八角', '桂皮', '香叶', '草果', '小茴香'},
                      squeeze={'豆瓣酱', '甜面酱', '番茄酱', '黄豆酱', '芝麻酱', '糖桂花酱', '泡椒'}, delivery='cup+drum'),
 # b + MSG solution + 香油 + 红油 channels (Wang Gang set)
 'b_plus_wg': dict(liquid=LIQ_CORE | {'味精', '鸡精', '香油', '红油', '花椒油'}, subs={}, grinder={'胡椒粉', '花椒面'},
                   feeder={'花椒', '干辣椒'}, sachet={'八角', '桂皮', '香叶', '草果', '小茴香'},
                   squeeze={'豆瓣酱', '甜面酱', '番茄酱', '黄豆酱', '芝麻酱', '糖桂花酱', '泡椒'}, delivery='cup+drum'),
 # d: same hardware as b, but liquids through a nozzle cluster over the wok, chili/花椒 portioners and sachet dropper at the wok,
 #    home-style plate sauces made in the wok and tipped over the dish (the existing hot-oil pour), off-wok doses via the port
 'd_direct': dict(liquid=LIQ_CORE, subs={}, grinder={'胡椒粉', '花椒面'}, feeder={'花椒', '干辣椒'},
                  sachet={'八角', '桂皮', '香叶', '草果', '小茴香'},
                  squeeze={'豆瓣酱', '甜面酱', '番茄酱', '黄豆酱', '芝麻酱', '糖桂花酱', '泡椒'}, delivery='direct'),
 'd_direct_wg': dict(liquid=LIQ_CORE | {'味精', '鸡精', '香油', '红油', '花椒油'}, subs={}, grinder={'胡椒粉', '花椒面'},
                     feeder={'花椒', '干辣椒'}, sachet={'八角', '桂皮', '香叶', '草果', '小茴香'},
                     squeeze={'豆瓣酱', '甜面酱', '番茄酱', '黄豆酱', '芝麻酱', '糖桂花酱', '泡椒'}, delivery='direct'),
}

def route(item, cfg):
    """which mechanism serves this seasoning, or 'uncovered'."""
    if item in cfg['liquid']: return 'liquid'
    if item in cfg.get('subs', {}) and cfg['subs'][item] == 'liquid': return 'liquid'
    for k in ('auger', 'grinder', 'paste', 'feeder', 'sachet', 'squeeze'):
        if item in cfg.get(k, set()): return k
    if item in cfg.get('swap_paste', set()): return 'swap'
    return 'uncovered'

def dish_moves(events, cfg):
    """events: list of (stage, seasonings, aromatics). Returns dict of counts for one dish."""
    direct = cfg['delivery'] == 'direct'
    wok_containers = 0; moves = 0; secs = 0; uncovered = set(); swaps = 0; squeezes = 0; nozzle_doses = 0
    off_cups = 0; vessels = 0
    for stg, seas, arom in events:
        if stg == 'wash' or not seas: continue
        routes = {s: route(s, cfg) for s in seas}
        uncovered |= {s for s, r in routes.items() if r == 'uncovered'}
        swaps += sum(1 for r in routes.values() if r == 'swap')
        sq = sum(1 for r in routes.values() if r == 'squeeze'); squeezes += sq
        if not direct:
            if stg in WOKBOUND: wok_containers += 1
            elif stg in OFF_SAUCE | OFF_POT | OFF_VESSEL: off_cups += 1
            continue
        # direct delivery
        if stg in WOKBOUND:
            need_cup = any(r in ('grinder', 'auger', 'paste', 'squeeze', 'swap', 'uncovered') for r in routes.values())
            nozzle_doses += sum(1 for r in routes.values() if r in ('liquid', 'feeder', 'sachet'))
            if need_cup: wok_containers += 1
        elif stg in OFF_SAUCE:
            # made in the wok with the nozzle, then tipped over the dish together with the hot oil (already an R16 motion)
            need_cup = any(r in ('grinder', 'auger', 'paste', 'squeeze', 'swap', 'uncovered') for r in routes.values())
            nozzle_doses += sum(1 for r in routes.values() if r in ('liquid', 'feeder', 'sachet'))
            if need_cup: off_cups += 1
        elif stg in OFF_VESSEL: vessels += 1
        elif stg in OFF_POT: off_cups += 1
    # wok-bound containers: one cup, or one drum per <= 4 compartments when there are >= 2
    if wok_containers == 1: moves += 3; secs += S_CUP
    elif wok_containers >= 2:
        nd = -(-wok_containers // 4); moves += 3 * nd; secs += S_DRUM * nd
    moves += 3 * off_cups + 2 * vessels + 2 * squeezes
    secs += S_CUP * off_cups + S_VESSEL * vessels + S_SQUEEZE * squeezes
    return dict(moves=moves, secs=secs, wok_containers=wok_containers, off_cups=off_cups, vessels=vessels, squeezes=squeezes,
                nozzle_doses=nozzle_doses, uncovered=sorted(uncovered), swaps=swaps)

def cup_only_moves(events):
    """R19 baseline accounting: every seasoning event = one station cup (no drum)."""
    n = sum(1 for stg, seas, arom in events if stg != 'wash' and seas)
    return 3 * n, S_CUP * n

if __name__ == '__main__':
    hs = [(m, d, [(a, b, c) for a, b, c, *_ in ev]) for m, d, ev in HS]
    wg = [(rid, d, [(e['stage'], e['seas'], e['arom']) for e in ev]) for rid, d, ev in wg_events()]
    out = {}
    print('| config | HS meal A moves (s) | meal B | meal C | HS dishes fully automatic /15 | HS uncovered items | WG moves per dish median / p90 | WG dishes fully automatic /42 | WG top uncovered |')
    print('|---|---|---|---|---|---|---|---|---|')
    base = collections.defaultdict(lambda: [0, 0])
    for m, d, ev in hs:
        mv, s = cup_only_moves(ev); base[m][0] += mv; base[m][1] += s
    wgb = [cup_only_moves(ev)[0] for _, _, ev in wg]
    print(f"| cups only (R19 accounting) | {base['A'][0]} ({base['A'][1]}) | {base['B'][0]} ({base['B'][1]}) | {base['C'][0]} ({base['C'][1]}) | — | — | {st.median(wgb):g} / {sorted(wgb)[int(.9*len(wgb))]} | — | — |")
    for name, cfg in CONFIGS.items():
        per_meal = collections.defaultdict(lambda: dict(moves=0, secs=0, nozzle=0))
        hs_ok = 0; hs_unc = collections.Counter()
        for m, d, ev in hs:
            r = dish_moves(ev, cfg)
            per_meal[m]['moves'] += r['moves']; per_meal[m]['secs'] += r['secs']; per_meal[m]['nozzle'] += r['nozzle_doses']
            if not r['uncovered'] and not r['swaps']: hs_ok += 1
            hs_unc.update(r['uncovered'])
        wg_moves = []; wg_ok = 0; wg_unc = collections.Counter()
        for rid, d, ev in wg:
            r = dish_moves(ev, cfg); wg_moves.append(r['moves'])
            if not r['uncovered'] and not r['swaps']: wg_ok += 1
            wg_unc.update(r['uncovered'])
        p90 = sorted(wg_moves)[int(.9 * len(wg_moves))]
        out[name] = dict(per_meal=dict(per_meal), hs_full=hs_ok, hs_uncovered=dict(hs_unc), wg_moves=wg_moves, wg_full=wg_ok,
                         wg_uncovered=dict(wg_unc.most_common()))
        pm = per_meal
        print(f"| {name} | {pm['A']['moves']} ({pm['A']['secs']}) | {pm['B']['moves']} ({pm['B']['secs']}) | {pm['C']['moves']} ({pm['C']['secs']}) | {hs_ok} | "
              f"{', '.join(f'{k}×{v}' for k, v in hs_unc.most_common()) or '—'} | {st.median(wg_moves):g} / {p90} | {wg_ok} | "
              f"{', '.join(f'{k}×{v}' for k, v in wg_unc.most_common(8))} |")
    # nozzle doses per meal under d (how much the nozzle cluster does)
    print('\nd_direct nozzle/portioner doses per HS meal:', {m: v['nozzle'] for m, v in out['d_direct']['per_meal'].items()})
    os.makedirs('results/r19seas', exist_ok=True)
    json.dump(out, open('results/r19seas/options.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def event_stats(name, dishes, cfg):
    """share of seasoning events/items that are wok-bound and that the liquid bank alone can deliver."""
    ev_total = ev_wok = ev_wok_liq = it_total = it_wok = it_wok_liq = it_wok_liq_or_wokside = 0
    for _, d, ev in dishes:
        for stg, seas, arom in ev:
            if stg == 'wash' or not seas: continue
            ev_total += 1; it_total += len(seas)
            if stg in WOKBOUND:
                ev_wok += 1; it_wok += len(seas)
                r = [route(s, cfg) for s in seas]
                it_wok_liq += sum(x == 'liquid' for x in r)
                it_wok_liq_or_wokside += sum(x in ('liquid', 'feeder', 'sachet') for x in r)
                if all(x == 'liquid' for x in r): ev_wok_liq += 1
    print(f"{name}: events {ev_total}, wok-bound {ev_wok} ({100*ev_wok/ev_total:.0f} %), wok-bound events all-liquid {ev_wok_liq} "
          f"({100*ev_wok_liq/max(ev_wok,1):.0f} % of wok-bound); items {it_total}, wok-bound {it_wok}, of which liquid {it_wok_liq} "
          f"({100*it_wok_liq/max(it_wok,1):.0f} %), liquid+wok-side portioner/sachet {it_wok_liq_or_wokside} ({100*it_wok_liq_or_wokside/max(it_wok,1):.0f} %)")

if __name__ == '__main__':
    print()
    event_stats('home-style (d_direct)', hs, CONFIGS['d_direct'])
    event_stats('Wang Gang (d_direct_wg)', wg, CONFIGS['d_direct_wg'])
