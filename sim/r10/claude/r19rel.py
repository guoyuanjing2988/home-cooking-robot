"""R19 reliability model (issue #27): failure-prone events per meal x per-event success -> meal success,
user interventions and the meal-time spread, with and without recovery; per-type success targets; design levers.

Bookkeeping + Monte Carlo only: no physics, no path checks. Every rate is labelled in TYPES (sourced range or
assumption, see R19_RELIABILITY.md section 3 for the citations S1..S18).

Inputs (all read-only):
  results/r19/prim/library_size.json  cooking set instances per meal (R19 motion library, mapping of meal16 SET=stew ARM=r18)
  results/r19/prep/prep_demand.json   prep set instances per meal (R19 prep audit section 6.2)
  results/r19seas/cups.json           seasoning containers per meal (2026-10-13 cup rule; plan P2 = caddy + cups + drums, as recommended
                                      in research/r19_seasoning_cups.md) if present
  meal16.py                           exec'd only up to its run() definition (SET=stew ARM=r18 USERRICE=1); nothing is written
Outputs: results/r19/rel/{inventory,rates,mc,targets,levers,exposure}.json and markdown tables on stdout.

python r19rel.py [N=20000] [SEED=1]
"""
import json, os, sys, math, copy, collections
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
KV = dict(a.split('=', 1) for a in sys.argv[1:]); NMC = int(KV.get('N', 20000)); SEED = int(KV.get('SEED', 1))
OUT = os.path.join('results', 'r19', 'rel'); os.makedirs(OUT, exist_ok=True)
LIB = json.load(open('results/r19/prim/library_size.json', encoding='utf-8'))
PREP = json.load(open('results/r19/prep/prep_demand.json', encoding='utf-8'))
CUPS_F = 'results/r19seas/cups.json'
CUPS = json.load(open(CUPS_F, encoding='utf-8')) if os.path.exists(CUPS_F) else None
MEALS3 = 'ABC'

# ------------------------------------------------------------------------------------------------ event types
# p = first-attempt failure probability per event at three levels (lo / mid / hi).
# d = share of failures the robot detects itself; r = share of detected failures it can retry along stored paths;
# q_floor / m: a retry fails with q = min(1, max(m*p, q_floor)) (failures are correlated: the item that slipped once
# often slips again); t = seconds per retry. Undetected failures are silent defects (a wrong or spoiled result).
# cat = the issue's category; regime = structured (keyed, fixtured, repeated: near-industrial) or unstructured (food).
T = lambda cat, regime, lo, mid, hi, d, r, m, qf, t, basis: dict(cat=cat, regime=regime, p=dict(lo=lo, mid=mid, hi=hi),
                                                                  d=d, r=r, m=m, q_floor=qf, t=t, basis=basis)
TYPES = {
 'g_rigid':      T('grasp/release', 'structured', 1e-4, 5e-4, 2e-3, .95, .9, 3, .05, 10,
                   'ASSUMED. Keyed handle in a keyed dock, taught pose. Between known-part bin picking 96-99 % (S2: pose error dominates) '
                   'and wafer handlers ~1e-6-1e-7 per handoff (S1: hardware only, ideal objects).'),
 'r_rigid':      T('grasp/release', 'structured', 2e-5, 1e-4, 5e-4, .8, .5, 3, .05, 8, 'ASSUMED. Opening the jaws over a seated keyed object.'),
 'g_food_rigid': T('grasp/release', 'unstructured', 1e-3, 5e-3, 3e-2, .9, .9, 2, .2, 15,
                   'SOURCED range: novel-object grasping 95-96 % (S3 Dex-Net 4.0, S4 QT-Opt), known parts 96-99 % (S2). Mid assumes a '
                   'known firm item (potato, carrot, ginger) on a tray: 99.5 %.'),
 'g_food_soft':  T('grasp/release', 'unstructured', 3e-3, 1.5e-2, 8e-2, .9, .9, 2, .2, 15,
                   'SOURCED range: food acquisition 83-91 % on plates (S8 SPANet), human teleop demos of lettuce 94.7 % (S7). Mid 98.5 %.'),
 'g_food_wet':   T('grasp/release', 'unstructured', 5e-3, 2e-2, 1e-1, .9, .9, 2, .2, 15,
                   'SOURCED range: autonomous lettuce grasp 75 % (S7), slippery items the worst class in S8; wet pad friction unmeasured (#10). Mid 98 %.'),
 'g_food_small': T('grasp/release', 'unstructured', 5e-3, 2e-2, 1e-1, .9, .9, 2, .2, 15,
                   'ASSUMED (+S8). Rib pieces, clams, cloves, okra, whole spices, one at a time.'),
 'r_food':       T('grasp/release', 'unstructured', 5e-4, 3e-3, 1e-2, .7, .6, 2, .2, 10,
                   'ASSUMED. Food let go into a chute, cradle, cup or plate: sticks to wet fingers, bounces out.'),
 'seat':         T('insertion/seating', 'structured', 2e-4, 1e-3, 5e-3, .9, .8, 3, .05, 12,
                   'ASSUMED. Keyed seat with lead-in. Learned precise insertion reaches 100/100 (S5 HIL-SERL; one-sided 95 % bound >= 97 %). '
                   'Tight reserves here: lid rack 0.3 mm, wok grasp 2.4 mm (R19_MOTION_LIBRARY 5).'),
 'contact_mech': T('contact', 'structured', 2e-4, 1e-3, 5e-3, .9, .7, 3, .05, 10,
                   'ASSUMED. Faucet lever, fridge door, drawer, lever-cutter stroke, cracker press. Learned-policy floor: cabinet 85 %, '
                   'faucet rinse 80 % (S9).'),
 'stir_dice':    T('contact', 'semi', 2e-4, 1e-3, 5e-3, .7, .6, 3, .1, 15,
                   'ASSUMED per 13.15 s cycle (5 strokes): jam, spatula turned in the grip, food thrown out. R15 rigid dice only.'),
 'stir_shred':   T('contact', 'unstructured', 1e-3, 5e-3, 2e-2, .6, .5, 3, .2, 15,
                   'ASSUMED per cycle. README_R10:544: shreds and leaves "not credible" with rigid pieces.'),
 'food_contact': T('contact', 'unstructured', 2e-3, 1e-2, 5e-2, .8, .8, 2, .2, 15,
                   'ASSUMED. Spider scoop, re-push of an item under the lever blade, eggs out of the wok. Learned-policy floor: '
                   '"cook shrimp" 60 % whole task (S9).'),
 'pour_liquid':  T('pour/tip', 'structured', 1e-4, 5e-4, 3e-3, .6, .7, 2, .1, 8,
                   'ASSUMED. Keyed cup tipped into a large target (wok, pot). Level accuracy 13-31 ml (S18) is dose error, not failure.'),
 'pour_food':    T('pour/tip', 'unstructured', 1e-3, 5e-3, 2e-2, .8, .7, 2, .2, 15,
                   'ASSUMED. Tip of food or paste: wok to plate, basket, spider dump, chopper bowl. Sim: 81-91 % of rigid dice on the '
                   'plate, 98 % at half load (README_R10:561).'),
 'tool_change':  T('tool change', 'structured', 1e-4, 1e-3, 5e-3, .95, .8, 3, .05, 15,
                   'ASSUMED. Finger-set swap on a dovetail + spring pin, never simulated (R19_PREP_AUDIT 6.2).'),
 'appl_cmd':     T('appliance', 'structured', 1e-5, 1e-4, 1e-2, .95, .95, 1, .05, 5,
                   'ASSUMED. lo/mid: wired control with state read-back. hi: consumer smart plug, no read-back; forum reports of "a few '
                   'percent" lost Zigbee commands (S17, anecdotal).'),
 'appl_proc':    T('appliance', 'unstructured', 2e-3, 1e-2, 5e-2, .7, .5, 2, .3, 60,
                   'ASSUMED. Outcome of a food-processing run: peel incomplete, slicer jam, piece stuck in the lever cutter, dry doser caked.'),
 'perc_struct':  T('perception', 'structured', 1e-4, 5e-4, 3e-3, .5, .8, 2, .05, 5,
                   'ASSUMED. Presence / seated / flow / cup-ID check in a fixed scene; ~99.5 % detection on food lines (S14, vendor).'),
 'perc_food':    T('perception', 'unstructured', 1e-3, 5e-3, 3e-2, .4, .7, 2, .2, 10,
                   'ASSUMED. Food localisation and food-state judgement (all out, peel done, shell-free).'),
 'transit':      T('free move', 'structured', 1e-5, 1e-4, 1e-3, 1., .5, 1, .5, 20,
                   'ASSUMED. Protective stop on a hub transit (object left in the corridor, contact).'),
 'hw':           T('hardware', 'structured', 1e-4, 1e-3, 1e-2, 1., 0., 1, 1., 0,
                   'ASSUMED per meal: a fault of the arm, gripper, PC or station that needs the user (MTBF ~1,000 h of a home system).'),
}
LEVELS = ('lo', 'mid', 'hi')

# ------------------------------------------------------------------------------------------------ set templates
COOK_T = {
 'FAUCET_OPEN': dict(g_rigid=1, contact_mech=1, r_rigid=1, perc_struct=1), 'FAUCET_CLOSE': dict(g_rigid=1, contact_mech=1, r_rigid=1, perc_struct=1),
 'WOK_PLATE_RINSE': dict(g_rigid=1, pour_food=1, pour_liquid=1, seat=1, r_rigid=1, perc_struct=2, perc_food=1),
 'WOK_DUMP_RINSE': dict(g_rigid=1, pour_food=1, seat=1, r_rigid=1, perc_struct=1, perc_food=1),
 'WOK_FILL': dict(g_rigid=1, seat=1, r_rigid=1, perc_struct=1),
 'WOK_OIL_POUR': dict(g_rigid=1, pour_liquid=1, seat=1, r_rigid=1, perc_struct=1),
 'SPATULA_FETCH': dict(g_rigid=1, perc_struct=1), 'SPATULA_STOW': dict(seat=1, r_rigid=1),
 'STIR_CYCLE_dice': dict(stir_dice=1), 'STIR_CYCLE_shreds_leafy': dict(stir_shred=1),
 'SPIDER_FETCH': dict(g_rigid=1, perc_struct=1), 'SPIDER_SCOOP': dict(food_contact=1, perc_food=1),
 'SPIDER_DUMP_plate': dict(pour_food=1), 'SPIDER_STOW': dict(seat=1, r_rigid=1),
 'LID': dict(g_rigid=1, seat=1, r_rigid=1, perc_struct=1), 'CARRIER_IN': dict(g_rigid=1, seat=1, r_rigid=1, perc_struct=1),
 'CARRIER_OUT': dict(g_rigid=1, seat=1, r_rigid=1, perc_struct=1), 'CARRIER_DRAIN': dict(pour_liquid=1),
 'STEW_CUP_IN': dict(g_rigid=1, seat=1, r_rigid=1), 'ARRANGE': dict(pour_food=1, perc_food=1),
}
HOT = ('STIR_CYCLE', 'SPIDER_SCOOP', 'LID_ON_wok', 'LID_OFF_wok', 'WOK_OIL_POUR')   # sets done with the heat on
PREP_T = {
 'PIECE': dict(perc_food=1, G=1, r_food=1, appl_proc=.5), 'PIECE_SHORT': dict(perc_food=1, G=1, r_food=1),
 'BASKET': dict(g_rigid=1, pour_food=1, seat=1, r_rigid=1, perc_food=1),
 'SOAK': dict(g_rigid=2, seat=2, r_rigid=2, pour_liquid=1, perc_struct=1),
 'PEEL_BATCH': dict(g_rigid=2, seat=2, r_rigid=2, pour_food=2, contact_mech=1, appl_cmd=2, appl_proc=1, perc_food=1),
 'TOOL': dict(g_rigid=2, seat=2, r_rigid=2, contact_mech=2, perc_struct=1), 'PLATE': dict(g_rigid=2, seat=2, r_rigid=2, perc_struct=1),
 'FINGER': dict(tool_change=1, perc_struct=1), 'XFER': dict(g_rigid=1, pour_food=1, seat=1, r_rigid=1, perc_food=1),
 'PRESS': dict(g_rigid=1, contact_mech=1, r_rigid=1, food_contact=1, appl_proc=1),
 'MINCE': dict(g_rigid=2, seat=2, r_rigid=2, pour_food=2, contact_mech=1, appl_cmd=2, appl_proc=1, perc_food=1),
 'MEAT': dict(G=1, r_food=1, contact_mech=1, appl_cmd=2, appl_proc=1, g_rigid=1, pour_food=1, seat=1, r_rigid=1, perc_food=1),
 'EGG': dict(g_food_soft=1, r_food=1, contact_mech=1, pour_food=1, perc_food=1),
 'BEAT': dict(g_rigid=1, seat=1, r_rigid=1, appl_cmd=2, appl_proc=1),
 'MIX': dict(g_rigid=2, seat=2, r_rigid=2, contact_mech=1, pour_liquid=1, perc_food=1),
 'SCALD': dict(g_rigid=1, pour_liquid=1, seat=1, r_rigid=1, appl_cmd=1, perc_struct=1),
 'PLACE': dict(perc_food=1, G=1, r_food=1), 'ARRANGE': dict(g_rigid=1, pour_food=1, seat=1, r_rigid=1, perc_food=1),
 'FAUCET': dict(g_rigid=2, contact_mech=2, r_rigid=2, perc_struct=2),
 'FRIDGE': dict(contact_mech=2, g_rigid=2, seat=2, r_rigid=2, perc_struct=1),
}
def food_cls(ing, fam):
    """grasp class of the food in a prep item (est. from the ingredient; R13 bench notes in R19_PREP_AUDIT 3)"""
    if fam == 'PLACE': return 'g_food_small'
    if fam == 'EGG': return 'g_food_soft'
    s = ing.lower()
    if any(k in s for k in ('squid', '鱿鱼', 'fish', '鲈鱼')): return 'g_food_wet'
    if fam == 'PIECE_SHORT' and any(k in s for k in ('taro', '芋头', 'potato', '土豆')): return 'g_food_wet'   # peeled: slimy / wet
    if any(k in s for k in ('丝 fine', 'shreds')): return 'g_food_small'
    if any(k in s for k in ('tomato', '番茄', 'luffa', '丝瓜', 'pork', '肉')): return 'g_food_soft'
    return 'g_food_rigid'

# main-ingredient bowls poured during cooking (cut food in staging bowls; the seasoning cups are separate). Hand count
# from the meal16 step labels [est.]: (count, phase)
MAIN_BOWLS = {'A': [(1, 'hot'), (1, 'hot'), (1, 'hot'), (1, 'hot')],          # potato -> fryer, pork belly, fried potato -> wok, broccoli
              'B': [(1, 'hot'), (1, 'hot'), (4, 'cook'), (1, 'hot'), (1, 'hot'), (1, 'hot'), (1, 'hot'), (1, 'hot')],
              # pork strip -> blanch, cubes -> wok, ribs/shoots/scallops/hot water -> stew pot, eggs, eggs back, tomato, cabbage, okra
              'C': [(1, 'hot'), (1, 'hot'), (1, 'cook'), (1, 'cook'), (1, 'hot'), (1, 'hot'), (1, 'hot')]}
              # shreds -> water, shreds -> wok, cucumber+ginger -> stew pot, pork slices -> stew pot, squid, pepper, peas
EXTRA_COOK = {'B': {'food_contact': 1}}   # eggs set and taken out of the wok (no library set exists for it)
# operations of the as-bought rule with NO designed robot method today (r19_asbought.md 4, R19_PREP_AUDIT 3/5.7):
STRUCTURAL = {
 'A': ['luffa peel', 'broccoli florets + stem peel', 'garlic clove peel', 'ginger knob peel'],
 'B': ['bamboo shoot husk', 'sea bass back-split', 'tomato peel after scald', 'fine scallion shreds (comb concept only)',
       'okra cap trim + halve (~15 pods)', 'garlic clove peel', 'ginger knob peel', 'dried-chili snipping'],
 'C': ['squid open + cross-score', 'garlic clove peel', 'ginger knob peel', 'dried-chili snipping']}
ESCAPE = {'broccoli florets + stem peel', 'garlic clove peel', 'bamboo shoot husk', 'sea bass back-split', 'squid open + cross-score',
          'dried-chili snipping'}   # closed by the 10-13 as-bought rule; would reopen only by a user decision (stall cuts, 净菜, peeled garlic, 辣椒段)
DRY = {'盐', '白糖', '淀粉', '干辣椒段', '花椒', '胡椒粉', '十三香', '八角', '桂皮', '干辣椒(整)'}
PASTE = {'豆瓣酱', '糖桂花酱', '蚝油'}
AROM = {'姜', '葱', '蒜', '蒜苗+红椒', '蒜末+红椒', '蒜末+葱白', '芹菜', '葱姜胡萝卜丝', '葱段', '葱叶', '红椒末+葱花', '葱姜蒜'}
FALLBACK_CUPS = {'A': dict(cont=12, caddies=3, extra=1), 'B': dict(cont=20, caddies=4, extra=1), 'C': dict(cont=16, caddies=3, extra=0)}

def add(inv, fam, phase, tmpl, n, G=None):
    for k, v in tmpl.items():
        if v * n == 0: continue
        typ = G if k == 'G' else k
        inv[(fam, phase, typ)] += v * n

def seasoning(meal, opt):
    """seasoning containers per the 10-13 cup rule (results/r19seas/cups.json, 'as he does'), plan P2 (caddy + cups + drums) or P1 (no drums)"""
    inv = collections.Counter()
    if CUPS is None:
        f = FALLBACK_CUPS[meal]
        add(inv, 'SEAS_CUP', 'hot', dict(g_rigid=1, pour_liquid=1, seat=1, r_rigid=1, perc_struct=1), f['cont'])
        add(inv, 'SEAS_CADDY', 'cook', dict(g_rigid=2, seat=2, r_rigid=2), f['caddies']); return inv, 'fallback constants'
    ms = [m for m in CUPS['moments'] if m['id'][0] == meal and m['cont'] != 'X' and not m['optional']]
    V = [m for m in ms if m['cont'] == 'V']; C = [m for m in ms if m['cont'] != 'V']
    drums = sorted({m['drum'] for m in C if m['drum']}) if opt.get('drums', 1) else []   # P2 (recommended in r19_seasoning_cups.md) by default
    for m in C:
        names = [i[0] for i in m['items']]
        phase = 'hot' if ('wok' in m['target'] and m['stir']) else 'cook'
        dosed = [n for n in names if n not in AROM]
        add(inv, 'SEAS_DOSE', 'prep', dict(appl_cmd=sum(n not in DRY for n in dosed), appl_proc=sum(n in DRY for n in dosed)), 1)
        if m['cont'] == 'A': add(inv, 'SEAS_AROM_FILL', 'prep', dict(pour_food=1, perc_food=1), 1)
        if m['drum'] in drums: continue
        pt = 'pour_food' if (m['cont'] in ('A', 'D') or any(n in PASTE for n in names)) else 'pour_liquid'
        add(inv, 'SEAS_CUP', phase, {'g_rigid': 1, pt: 1 + m['extra_moves'], 'seat': 1, 'r_rigid': 1, 'perc_struct': 1}, 1)
    for dr in drums:  # servo rim holder pours the compartments: load + unload by the arm, one servo pour per compartment
        ncomp = sum(1 for m in C if m['drum'] == dr)
        add(inv, 'SEAS_DRUM', 'hot', dict(g_rigid=2, seat=2, r_rigid=2, appl_cmd=ncomp, pour_food=1, perc_struct=1), 1)
    for m in V: add(inv, 'SEAS_DOSE', 'prep', dict(appl_cmd=sum(i[0] not in DRY for i in m['items']), appl_proc=sum(i[0] in DRY for i in m['items'])), 1)
    caddies = len({m['caddy'] for m in ms if m['caddy']})
    add(inv, 'SEAS_CADDY', 'cook', dict(g_rigid=2, seat=2, r_rigid=2), caddies)
    pp = CUPS['meals'][meal]['prep_phase']
    add(inv, 'SEAS_PICK', 'prep', dict(g_food_small=1, r_food=1, perc_food=1), pp['spice_picks'])
    add(inv, 'SEAS_SHAKE_SQUEEZE', 'prep', dict(g_rigid=1, contact_mech=1, seat=1, r_rigid=1), pp['shakes_if_arm'] + pp['squeezes'])
    return inv, f'{CUPS_F} ({"P2 drums" if drums else "P1 caddy + cups"})'

def meal_appliance_cmds(meal):
    inv = collections.Counter()
    for s in MEALS16[MEAL_KEY[meal]]:
        if not s['res'] or s['res'] == 'rice' or s['arm'] == 0: continue
        hot = s['res'] in ('wok', 'fryer'); stir = s['res'] == 'wok' and any(w in s['label'] for w in ('stir', 'reduce'))
        inv[('APPL_COOK', 'hot' if hot else 'cook', 'appl_cmd')] += 2 + 2 * stir   # on/off (+ 2 power changes when stirring)
    return inv

def inventory(meal, opt=None):
    """event counts per (set family, phase, event type) for one meal; opt switches the design levers"""
    opt = opt or {}; inv = collections.Counter(); note = {}
    for s, n in LIB['meals'][meal]['counts'].items():
        if s.startswith('CUP_') or s.startswith('RICE_'): continue      # cups: re-counted below; rice: the user's (10-13)
        if opt.get('auto_stirrer') and s.startswith(('STIR_CYCLE', 'SPATULA_')): continue
        fam = 'LID' if s.startswith('LID_') else 'SPIDER_SCOOP' if s.startswith('SPIDER_SCOOP') else s
        phase = 'hot' if any(s.startswith(h) for h in HOT) else 'cook'
        add(inv, fam, phase, COOK_T[fam], n)
    if opt.get('auto_stirrer'):   # a stirring appliance in the wok zone: + start/stop per stirred dish, no arm strokes
        nd = sum(1 for s, n in LIB['meals'][meal]['counts'].items() if s.startswith('SPATULA_FETCH') for _ in range(n))
        add(inv, 'AUTO_STIR', 'hot', dict(appl_cmd=2, appl_proc=1), nd)
    for n, ph in MAIN_BOWLS[meal]: add(inv, 'MAIN_BOWL', ph, dict(g_rigid=1, pour_food=1, seat=1, r_rigid=1, perc_food=1), n)
    for k, v in EXTRA_COOK.get(meal, {}).items(): inv[('EGGS_OUT', 'hot', k)] += v
    si, note['seasoning'] = seasoning(meal, opt); inv.update(si)
    inv.update(meal_appliance_cmds(meal))
    for it in PREP['meals'][meal]['items']:
        for fam, n in it['sets'].items():
            if fam == 'PLACE' and opt.get('pour_portion') and n >= 8:   # 4 partial pours per ingredient, scale under the cup
                add(inv, 'PLACE->POUR', 'prep', dict(pour_food=1, perc_food=1), 4 if n >= 12 else 2); continue
            if fam == 'PRESS' and opt.get('powered_cutter'):           # belt / section cutter: one feed + one run per item
                continue
            if fam == 'FINGER' and opt.get('one_finger_set'): n = 1
            if fam == 'FAUCET' and opt.get('batch_wash'): n = 1
            add(inv, fam, 'prep', PREP_T[fam], n, G=food_cls(it['ingredient'], fam))
        if opt.get('powered_cutter') and it['sets'].get('PRESS'):
            add(inv, 'POWERED_CUT', 'prep', dict(r_food=1, appl_cmd=2, appl_proc=1, perc_food=1), 1)
    if meal == 'B':   # as-bought corrections with a method: 4 tomatoes (not 3), tomato scald (r19_asbought 3.4)
        add(inv, 'PIECE', 'prep', PREP_T['PIECE'], 1, G='g_food_soft'); add(inv, 'SCALD', 'prep', PREP_T['SCALD'], 1)
    nsets = sum(n for s, n in LIB['meals'][meal]['counts'].items() if not s.startswith(('CUP_', 'RICE_', 'STIR')))
    nmoves = sum(v for (f, ph, t), v in inv.items() if t in ('g_rigid',) and f.startswith(('SEAS', 'MAIN')))
    nprep = sum(sum(it['sets'].values()) for it in PREP['meals'][meal]['items'])
    inv[('TRANSIT', 'cook', 'transit')] = round(0.7 * (nsets + nmoves + nprep))   # ASSUMED: 0.7 hub transits per set instance
    inv[('HW', 'cook', 'hw')] = 1
    return inv, note

def by_type(inv):
    c = collections.Counter()
    for (f, ph, t), v in inv.items(): c[t] += v
    return c

# ------------------------------------------------------------------------------------------------ meal16 schedule (read-only exec)
src = open('meal16.py', encoding='utf-8').read(); src = src[:src.index('out={k:run(v)')]
_argv = sys.argv; sys.argv = ['meal16.py', 'SET=stew', 'ARM=r18', 'USERRICE=1']; NS = {}
exec(compile(src, 'meal16.py', 'exec'), NS); sys.argv = _argv
MEALS16 = NS['MEALS']; RUN16 = NS['run']; MEAL_KEY = {k[0]: k for k in MEALS16}
PREP_BLOCK = {'A': (6.9, 17.4), 'B': (6.0, 10.4), 'C': (5.3, 12.7)}   # min, R19_PREP_AUDIT 6.3 (a lower bound per r19_asbought 3.3)

def schedule_samples(meal, n, rng):
    steps = MEALS16[MEAL_KEY[meal]]; out = np.empty(n)
    base = RUN16(copy.deepcopy(steps))['total_min']
    for i in range(n):
        st = copy.deepcopy(steps)
        for s in st:
            s['arm'] *= rng.uniform(0.7, 1.3)          # issue #27: arm durations +-30 %
            s['wait'] *= rng.uniform(0.9, 1.1)         # ASSUMED: heating / cooking times +-10 %
        out[i] = RUN16(st)['total_min']
    return base, out

# ------------------------------------------------------------------------------------------------ reliability
def rates(level='mid', scale=None, over=None):
    """per-type parameters at a level; scale: {type: factor} on p; over: {type: {field: value}}"""
    R = {}
    for t, v in TYPES.items():
        p = v['p'][level] * (scale or {}).get(t, 1.)
        R[t] = dict(p=min(p, 1.), d=v['d'], r=v['r'], m=v['m'], q_floor=v['q_floor'], t=v['t'], k=1)
        R[t].update((over or {}).get(t, {}))
    return R

def q_retry(x): return min(1., max(x['m'] * x['p'], x['q_floor']))

def lam(inv, R, policy='retry', s=1., only=None):
    """expected interventions and silent defects per meal (Poisson; exact enough for small p)"""
    li = ls = 0.; contrib = collections.Counter()
    for (f, ph, t), n in inv.items():
        x = dict(R[t]); x['p'] = min(1., x['p'] * (s if (only is None or t in only) else 1.))
        if policy == 'none': a, b = n * x['p'], 0.
        elif policy == 'user': a, b = n * x['p'] * x['d'], n * x['p'] * (1 - x['d'])
        else:
            a = n * x['p'] * x['d'] * (x['r'] * q_retry(x) ** x['k'] + (1 - x['r'])); b = n * x['p'] * (1 - x['d'])
        if t == 'hw': a, b = n * x['p'], 0.
        li += a; ls += b; contrib[(f, t)] += a + b
    return li, ls, contrib

def simulate(inv, R, policy, n, rng, sched=None, count_sd=0.25):
    """Monte Carlo of one meal: interventions, silent defects, hot-phase interventions and the meal time (min)"""
    u = rng.uniform(1 - count_sd, 1 + count_sd, n) if count_sd else np.ones(n)   # ASSUMED: event counts +-25 %
    K_int = np.zeros(n, int); K_sil = np.zeros(n, int); K_hot = np.zeros(n, int); t_retry = np.zeros(n)
    for (f, ph, t), N in inv.items():
        x = R[t]; Ns = np.round(N * u).astype(int) if t != 'hw' else np.full(n, int(N))
        F = rng.binomial(Ns, x['p'])
        if t == 'hw': K_int += F; continue
        if policy == 'none': K_int += F; K_hot += F * (ph == 'hot'); continue
        D = rng.binomial(F, x['d']); K_sil += F - D
        if policy == 'user': K_int += D; K_hot += D * (ph == 'hot'); continue
        Rr = rng.binomial(D, x['r']); q = q_retry(x)
        fail = rng.binomial(Rr, q ** x['k']); extra = rng.binomial(Rr, q) if x['k'] >= 2 else 0
        Ki = (D - Rr) + fail; K_int += Ki; K_hot += Ki * (ph == 'hot'); t_retry += (Rr + extra) * x['t']
    kmax = int(K_int.max()) if K_int.max() > 0 else 1
    lat = rng.lognormal(math.log(90), 0.8, (n, kmax)); fix = rng.lognormal(math.log(60), 0.6, (n, kmax))   # ASSUMED user response
    mask = np.arange(kmax)[None, :] < K_int[:, None]
    t_int = ((lat + fix) * mask).sum(1)
    hot_late = np.zeros(n, bool)
    if K_hot.max() > 0:   # a hot-phase intervention answered after > 60 s puts the dish at risk (heat to the safe state meanwhile)
        mh = np.arange(kmax)[None, :] < np.minimum(K_hot, K_int)[:, None]; hot_late = ((lat > 60) & mh).any(1)
    res = dict(K_int=K_int, K_sil=K_sil, K=K_int + K_sil, hot_late=hot_late)
    if sched is not None:
        nsets = sum(v for (f, ph, t), v in inv.items() if t == 'transit') / 0.7
        pres = rng.poisson(2.0, n) * rng.uniform(10, 60, n)        # ASSUMED: 2 person-in-reach pauses per meal, 10-60 s
        dec = 0.3 * nsets                                           # ASSUMED: 0.3 s decision latency per set
        res['T'] = sched + (t_retry + t_int + pres + dec) / 60.
    return res

def summ(r):
    K = r['K']; o = dict(p_clean=float((K == 0).mean()), p_le1=float((K <= 1).mean()), E_int=float(r['K_int'].mean()),
                          E_sil=float(r['K_sil'].mean()), p_dish_at_risk=float(r['hot_late'].mean()))
    if 'T' in r: o.update(T_p50=float(np.percentile(r['T'], 50)), T_p90=float(np.percentile(r['T'], 90)), T_mean=float(r['T'].mean()))
    return o

def solve_scale(inv, R, policy, target_lam, only=None):
    lo, hi = 1e-6, 1e3
    for _ in range(200):
        mid = math.sqrt(lo * hi); a, b, _ = lam(inv, R, policy, mid, only)
        if a + b > target_lam: hi = mid
        else: lo = mid
    return lo

def lam_le1(P):   # e^-l (1 + l) = P
    lo, hi = 0., 10.
    for _ in range(200):
        m = (lo + hi) / 2
        if math.exp(-m) * (1 + m) > P: lo = m
        else: hi = m
    return lo

# ------------------------------------------------------------------------------------------------ main
if __name__ == '__main__':
    rng = np.random.default_rng(SEED)
    INV = {m: inventory(m) for m in MEALS3}
    # ---- 1. inventory
    CATS = ['grasp/release', 'insertion/seating', 'contact', 'pour/tip', 'tool change', 'appliance', 'perception', 'free move', 'hardware']
    inv_out = {}
    print('## 1. Inventory per meal (events, est.)\n')
    print('| Type | Category | Regime | A | B | C |\n|---|---|---|---|---|---|')
    bt = {m: by_type(INV[m][0]) for m in MEALS3}
    for t, v in TYPES.items():
        print(f"| {t} | {v['cat']} | {v['regime']} | " + ' | '.join(f"{bt[m][t]:.0f}" for m in MEALS3) + ' |')
    for m in MEALS3:
        inv, note = INV[m]
        ph = collections.Counter(); cat = collections.Counter(); reg = collections.Counter()
        for (f, p, t), v in inv.items(): ph[p] += v; cat[TYPES[t]['cat']] += v; reg[TYPES[t]['regime']] += v
        grasp_rel = sum(v for t, v in bt[m].items() if t.startswith(('g_', 'r_')))
        inv_out[m] = dict(total=sum(inv.values()), by_type=dict(bt[m]), by_category=dict(cat), by_phase=dict(ph), by_regime=dict(reg),
                          grasp_release=grasp_rel, structural_no_method=STRUCTURAL[m], seasoning_source=note['seasoning'],
                          by_family_type={f'{f}|{p}|{t}': v for (f, p, t), v in sorted(inv.items())})
    print('\n| Meal | events | grasp+release | prep share | hot-phase | structured / semi / unstructured | no-method ops |\n|---|---|---|---|---|---|---|')
    for m in MEALS3:
        o = inv_out[m]
        print(f"| {m} | {o['total']:.0f} | {o['grasp_release']:.0f} | {o['by_phase'].get('prep', 0) / o['total']:.0%} | {o['by_phase'].get('hot', 0):.0f} | "
              f"{o['by_regime'].get('structured', 0):.0f} / {o['by_regime'].get('semi', 0):.0f} / {o['by_regime'].get('unstructured', 0):.0f} | {len(STRUCTURAL[m])} |")
    print('\nby category:', {m: {c: round(inv_out[m]['by_category'].get(c, 0)) for c in CATS} for m in MEALS3})
    json.dump(inv_out, open(os.path.join(OUT, 'inventory.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    json.dump(TYPES, open(os.path.join(OUT, 'rates.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

    # ---- 2. Monte Carlo: policies x rate levels, with the schedule spread
    SCH = {}
    for m in MEALS3:
        base, s = schedule_samples(m, NMC, rng); lo_, hi_ = PREP_BLOCK[m]
        SCH[m] = dict(base_cook_min=base, sample=s + rng.uniform(lo_, hi_, NMC))
    mc = {}
    print('\n## 2. Monte Carlo (N=%d per cell). K = interventions + silent defects; clean meal = K 0\n' % NMC)
    print('| Meal | Rates | Policy | P(clean) | P(K<=1) | E[interventions] | E[silent] | P(hot dish at risk) | T p50 / p90 min |\n|---|---|---|---|---|---|---|---|---|')
    for m in MEALS3:
        for lev in LEVELS:
            for pol in ('none', 'user', 'retry'):
                r = summ(simulate(INV[m][0], rates(lev), pol, NMC, rng, SCH[m]['sample']))
                mc[f'{m}|{lev}|{pol}'] = r
                print(f"| {m} | {lev} | {pol} | {r['p_clean']:.3f} | {r['p_le1']:.3f} | {r['E_int']:.2f} | {r['E_sil']:.2f} | {r['p_dish_at_risk']:.3f} | "
                      f"{r['T_p50']:.1f} / {r['T_p90']:.1f} |")
    sched_only = {m: dict(base_cook_min=SCH[m]['base_cook_min'], p50=float(np.percentile(SCH[m]['sample'], 50)),
                          p90=float(np.percentile(SCH[m]['sample'], 90))) for m in MEALS3}
    print('\nschedule + prep block only (no failures):', {m: {k: round(v, 1) for k, v in d.items()} for m, d in sched_only.items()})
    json.dump(dict(N=NMC, seed=SEED, results=mc, schedule_only=sched_only), open(os.path.join(OUT, 'mc.json'), 'w'), indent=1)

    # ---- 3. exposure: what drives E[K] at mid rates with retry
    expo = {}
    print('\n## 3. Exposure at mid rates, retry policy: top contributors to E[K]\n')
    for m in MEALS3:
        a, b, c = lam(INV[m][0], rates('mid'), 'retry'); tot = a + b
        byt = collections.Counter(); byf = collections.Counter()
        for (f, t), v in c.items(): byt[t] += v; byf[f] += v
        expo[m] = dict(E_K=tot, E_int=a, E_sil=b, by_type={k: v / tot for k, v in byt.most_common()}, by_family={k: v / tot for k, v in byf.most_common()})
        print(f"{m}: E[K] {tot:.2f} (int {a:.2f} + silent {b:.2f}); types: " + ', '.join(f'{k} {v / tot:.0%}' for k, v in byt.most_common(6))
              + '; families: ' + ', '.join(f'{k} {v / tot:.0%}' for k, v in byf.most_common(6)))
    json.dump(expo, open(os.path.join(OUT, 'exposure.json'), 'w'), indent=1)

    # ---- 4. targets
    TG = [('P(K=0)>=0.90', -math.log(.90)), ('P(K=0)>=0.95', -math.log(.95)), ('P(K=0)>=0.99', -math.log(.99)),
          ('P(K<=1)>=0.90', lam_le1(.90)), ('P(K<=1)>=0.95', lam_le1(.95)), ('P(K<=1)>=0.99', lam_le1(.99)),
          ('E[K]<=1/week (7 meals)', 1 / 7)]
    tg = {}
    print('\n## 4. Targets. Scale s on all mid first-attempt failure rates (relative difficulty kept), and the equal allocation\n')
    print('| Meal | Target | lambda | equal alloc: residual per-event success | s (no recovery) | s (retry) | g_rigid | seat | g_food_rigid | g_food_soft/wet | pour_food | appl_proc | perc_food |')
    print('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    R0 = rates('mid')
    for m in MEALS3:
        inv = INV[m][0]; Nev = sum(inv.values())
        for name, L in TG:
            s_none = solve_scale(inv, R0, 'none', L); s_ret = solve_scale(inv, R0, 'retry', L)
            req = {t: 1 - min(1, R0[t]['p'] * s_ret) for t in TYPES}
            tg[f'{m}|{name}'] = dict(lam=L, events=Nev, equal_alloc_success=1 - L / Nev, s_none=s_none, s_retry=s_ret,
                                     required_first_attempt_success_retry=req,
                                     required_success_no_recovery={t: 1 - min(1, R0[t]['p'] * s_none) for t in TYPES})
            f = lambda t: f'{req[t] * 100:.3f}'
            print(f"| {m} | {name} | {L:.3f} | {(1 - L / Nev) * 100:.3f} % | {s_none:.3f} | {s_ret:.3f} | {f('g_rigid')} | {f('seat')} | "
                  f"{f('g_food_rigid')} | {f('g_food_soft')} / {f('g_food_wet')} | {f('pour_food')} | {f('appl_proc')} | {f('perc_food')} |")
    json.dump(tg, open(os.path.join(OUT, 'targets.json'), 'w'), indent=1)

    print('\nPer-type first-attempt success needed (retry policy as designed; worst of A/B/C; all mid rates scaled by one factor s):\n')
    keys = [k for k, _ in TG]
    print('| Type | regime | mid assumption | ' + ' | '.join(keys) + ' |\n|---|---|---|' + '---|' * len(keys))
    smin = {k: min(tg[f'{m}|{k}']['s_retry'] for m in MEALS3) for k in keys}
    for t in TYPES:
        print(f"| {t} | {TYPES[t]['regime']} | {(1 - R0[t]['p']) * 100:.3f} | " + ' | '.join(f"{(1 - min(1, R0[t]['p'] * smin[k])) * 100:.3f}" for k in keys) + ' |')
    print('| (scale s) | | 1 | ' + ' | '.join(f'{smin[k]:.3f}' for k in keys) + ' |')
    smin_n = {k: min(tg[f'{m}|{k}']['s_none'] for m in MEALS3) for k in keys}
    tg['_worst_meal_scale_retry'] = smin; tg['_worst_meal_scale_none'] = smin_n
    # allocation 2: the keyed / structured events stay at their mid rates; only the food-handling events improve
    UNS = {t for t, v in TYPES.items() if v['regime'] != 'structured'}
    alloc2 = {}
    for m in MEALS3:
        a, b, _ = lam(INV[m][0], R0, 'retry', 0., UNS); alloc2[m] = dict(structured_floor=a + b)
    print('\nAllocation 2 (structured types kept at mid, only semi/unstructured scaled). Structured floor E[K]: '
          + ', '.join(f"{m} {alloc2[m]['structured_floor']:.3f}" for m in MEALS3))
    for k, L in TG:
        row = []
        for m in MEALS3:
            fl = alloc2[m]['structured_floor']
            su = solve_scale(INV[m][0], R0, 'retry', L, UNS) if fl < L else None
            alloc2[m][k] = su; row.append(f"{m} " + (f's_u={su:.3f}' if su is not None else 'infeasible'))
        print(f'  {k}: ' + ', '.join(row))
    tg['_alloc2_structured_at_mid'] = alloc2
    print('\nwithout recovery the same targets need s =', {k: round(v, 3) for k, v in smin_n.items()})
    sens = {}   # sensitivity of E[K] (mid, retry) to the model's own recovery assumptions
    for name, ov in [('baseline', {}), ('independent retries (q_floor 0)', {t: dict(q_floor=0.) for t in TYPES}),
                     ('strongly correlated retries (q_floor 0.5)', {t: dict(q_floor=.5) for t in TYPES}),
                     ('detection -0.2 on every type', {t: dict(d=max(0., TYPES[t]['d'] - .2)) for t in TYPES if t != 'hw'}),
                     ('detection 0.95 on every type', {t: dict(d=.95) for t in TYPES if t != 'hw'})]:
        E = {m: sum(lam(INV[m][0], rates('mid', None, ov), 'retry')[:2]) for m in MEALS3}
        Ei = {m: lam(INV[m][0], rates('mid', None, ov), 'retry')[0] for m in MEALS3}
        sens[name] = dict(E_K=E, E_int=Ei)
        print(f"sensitivity {name}: E[K] " + ', '.join(f'{m} {E[m]:.2f}' for m in MEALS3) + '; E[interventions] ' + ', '.join(f'{m} {Ei[m]:.2f}' for m in MEALS3))
    tg['_sensitivity'] = sens
    json.dump(tg, open(os.path.join(OUT, 'targets.json'), 'w'), indent=1)

    # ---- 5. levers (analytic E[K] with retry, averaged over A/B/C, at mid and hi rates; P(clean) = exp(-E[K]))
    LEV = [
     ('baseline (retry k=1)', {}, {}, {}),
     ('recovery off: every failure goes to the user (p^n)', {}, {}, {'policy': 'none'}),
     ('retry twice (k=2)', {}, {t: dict(k=2) for t in TYPES}, {}),
     ('grasp / pour / placement sensing (d -> 0.98, food release 0.9)', {},
      {**{t: dict(d=.98) for t in TYPES if t.startswith('g_') or t in ('pour_food', 'pour_liquid', 'seat')}, 'r_food': dict(d=.9)}, {}),
     ('process verification: scale + camera after each prep output (appl_proc, perc_food d -> 0.9)', {},
      {'appl_proc': dict(d=.9), 'perc_food': dict(d=.9)}, {}),
     ('food on keyed slot trays (food grasp p x0.3, locate x0.5)', {'g_food_rigid': .3, 'g_food_soft': .3, 'g_food_wet': .3, 'g_food_small': .3, 'perc_food': .5}, {}, {}),
     ('better food-state perception (perc_food p x0.3)', {'perc_food': .3}, {}, {}),
     ('keyed lead-ins + force-monitored contact (rigid/seat/contact p x0.3)', {'g_rigid': .3, 'seat': .3, 'contact_mech': .3, 'r_rigid': .3}, {}, {}),
     ('bench-proven prep appliances (process outcome p x0.3)', {'appl_proc': .3}, {}, {}),
     ('pour-portion the stew cups (A: 32 placements -> 8 pours)', {}, {}, {'opt': dict(pour_portion=1)}),
     ('powered section/belt cutter instead of 45 lever presses', {}, {}, {'opt': dict(powered_cutter=1)}),
     ('one finger set for most items (5 -> 1 swap per meal)', {}, {}, {'opt': dict(one_finger_set=1)}),
     ('no drum rim holder found: plan P1 (cups for the stir bursts too)', {}, {}, {'opt': dict(drums=0)}),
     ('stirring appliance at the wok (not adopted; market survey)', {}, {}, {'opt': dict(auto_stirrer=1)}),
     ('one prep faucet session instead of 2', {}, {}, {'opt': dict(batch_wash=1)}),
     ('consumer smart plugs without read-back (appl_cmd p = 1e-2)', {'appl_cmd': 100.}, {}, {}),
    ]
    lv = {}; base = {}
    print('\n## 5. Levers: E[K] per meal (interventions + silent defects), retry policy. P(clean) ~ exp(-E[K])\n')
    print('| Lever | mid: A | B | C | mean | change | P(clean) | hi: mean | change |\n|---|---|---|---|---|---|---|---|---|')
    def lever_row(sc, ov, extra):
        row = {}
        for lev in ('mid', 'hi'):
            R = rates(lev, sc, ov); pol = extra.get('policy', 'retry'); E = {}
            if 'appl_cmd' in sc: R['appl_cmd']['p'] = 1e-2   # smart plugs: the same absolute rate at both levels
            for m in MEALS3:
                inv = inventory(m, extra.get('opt'))[0] if extra.get('opt') else INV[m][0]
                a, b, _ = lam(inv, R, pol); E[m] = a + b
            mean = sum(E.values()) / 3; base.setdefault(lev, mean)
            row[lev] = dict(E_K=E, mean=mean, delta=mean - base[lev], p_clean_mean=sum(math.exp(-E[m]) for m in MEALS3) / 3)
        return row
    def pr(name, row, bold=False):
        r0, r1 = row['mid'], row['hi']; nm = f'**{name}**' if bold else name
        print(f"| {nm} | {r0['E_K']['A']:.2f} | {r0['E_K']['B']:.2f} | {r0['E_K']['C']:.2f} | {r0['mean']:.2f} | {r0['delta']:+.2f} | "
              f"{r0['p_clean_mean']:.2f} | {r1['mean']:.2f} | {r1['delta']:+.2f} |")
    for name, sc, ov, extra in LEV:
        lv[name] = lever_row(sc, ov, extra); pr(name, lv[name])
    # combined package of the design levers (no user decision needed; no stirrer, no smart plugs)
    pkg_sc = {'g_food_rigid': .3, 'g_food_soft': .3, 'g_food_wet': .3, 'g_food_small': .3, 'perc_food': .15, 'g_rigid': .3, 'seat': .3,
              'contact_mech': .3, 'r_rigid': .3, 'appl_proc': .3}
    pkg_ov = {t: dict(k=2) for t in TYPES}
    for t in TYPES:
        if t.startswith('g_') or t in ('pour_food', 'pour_liquid', 'seat'): pkg_ov[t]['d'] = .98
    pkg_ov['r_food']['d'] = .9; pkg_ov['appl_proc']['d'] = .9; pkg_ov['perc_food']['d'] = .9
    pkg_opt = dict(pour_portion=1, powered_cutter=1, one_finger_set=1, drums=1, batch_wash=1)
    lv['PACKAGE: all design levers above'] = lever_row(pkg_sc, pkg_ov, dict(opt=pkg_opt)); pr('package of the design levers', lv['PACKAGE: all design levers above'], True)
    # package MC (with time) at mid and hi
    pk = {}
    for m in MEALS3:
        for lev in ('mid', 'hi'):
            pk[f'{m}|{lev}'] = summ(simulate(inventory(m, pkg_opt)[0], rates(lev, pkg_sc, pkg_ov), 'retry', NMC, rng, SCH[m]['sample']))
    print('\npackage MC:', {k: {kk: round(vv, 3) for kk, vv in v.items()} for k, v in pk.items()})
    lv['_package_mc'] = pk
    st = {m: dict(no_method=len(STRUCTURAL[m]), after_escape_routes=len([s for s in STRUCTURAL[m] if s not in ESCAPE]),
                  ops=STRUCTURAL[m]) for m in MEALS3}
    lv['_structural'] = st
    print('\nstructural (no designed method, a certain user step each until designed):', {m: (v['no_method'], v['after_escape_routes']) for m, v in st.items()})
    json.dump(lv, open(os.path.join(OUT, 'levers.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

    # ---- 6. evidence: failure-free trials to show a rate at 95 % confidence (rule of three)
    print('\n## 6. Failure-free trials needed at 95 % confidence: n = ln(0.05)/ln(1-p)')
    for p in (1e-1, 5e-2, 1e-2, 1e-3, 1e-4):
        print(f'  per-event failure <= {p:g}: {math.ceil(math.log(.05) / math.log(1 - p)):,} clean events')
    for P in (.9, .95, .99):
        print(f'  clean-meal rate >= {P}: {math.ceil(math.log(.05) / math.log(P))} clean meals in a row')
