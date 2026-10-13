"""R19 seasoning in containers (user decision 2026-10-13: "不能用容器装好然后拿起来这种吗。或者是每道菜提前准备好料汁之类的").
During prep the station doses each dish's seasonings, weighed, into cups in a dry place; the arm stages the cups at
the heat zone and pours each at its moment; the 4-compartment pour drum takes stir-fry bursts.

What this script does (bookkeeping only, no physics, no path checks):
  1. MOMENTS: every seasoning / aromatics addition moment of the 3 reference meals, as the cook does it, with the
     container type, dose (his words where he gives one; grams are est.), and the evidence (seen in the 2 s frames /
     stated in his speech). Every 'src' phrase is checked against homestyle_meals.json and, if present, the session
     transcripts (home3/v1-3.txt).
  2. Container, cup-size, caddy and drum counts per meal.
  3. Arm moves and arm time per meal for four plans:
       P0 cups only (R19 accounting: stage, pick-pour, return = 3 moves per cup)
       P1 caddy + cups (a 2x3 caddy per dish group is staged in one move; 2 moves per cup)
       P2 P1 + drums in the servo rim holder for stir bursts (load + unload = 2 moves per drum, the servo pours)
       P2h P2 with the drum arm-held (3 moves per drum, the spatula is parked while the arm rolls it)
     with and without the taste-neutral merges (MERGE, est.), seasoning-only and including aromatics.
  4. Per-meal bulk use per ingredient (restock sizing) and the station parts total (PARTS, prices unconfirmed).
Usage: python r19seas_cups.py  -> results/r19seas/cups.json + markdown on stdout"""
import json, os, sys, math, collections
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..', '..')
HSJ = json.load(open(os.path.join(ROOT, 'research', 'homestyle_meals.json'), encoding='utf-8'))
TX_DIR = os.environ.get('HOME3', r'C:\Users\admin\AppData\Local\Temp\claude\C--Users-admin-Documents-YJGames'
                        r'\86718cbb-b411-47ad-a94e-23d66b0c6309\scratchpad\home3')

AROMATIC = {'姜', '葱', '蒜', '蒜苗+红椒', '蒜末+红椒', '蒜末+葱白', '芹菜', '葱姜胡萝卜丝', '葱段', '葱叶', '红椒末+葱花', '葱姜蒜'}
DOSER = {'oil': 'pump', 'water': 'pump', '生抽': 'pump', '老抽': 'pump', '蚝油': 'pump', '蒸鱼豉油': 'pump', '料酒': 'pump',
         '陈醋': 'pump', '白醋': 'pump', '盐': 'dry doser', '白糖': 'dry doser', '淀粉': 'dry doser',
         '干辣椒段': 'portioner', '花椒': 'portioner', '八角': 'arm pick', '桂皮': 'arm pick', '干辣椒(整)': 'arm pick',
         '十三香': 'shaker', '胡椒粉': 'shaker', '豆瓣酱': 'squeeze', '糖桂花酱': 'squeeze'}
# bulk density g/ml (est.): liquids ~1, oil .92, salt 1.2, sugar .85, starch .6, cut aromatics .35, dry spices .25
RHO = {'oil': .92, '盐': 1.2, '白糖': .85, '淀粉': .6, '干辣椒段': .25, '花椒': .35, '八角': .25, '桂皮': .3, '干辣椒(整)': .15,
       '十三香': .5, '胡椒粉': .5, '豆瓣酱': 1.1, '糖桂花酱': 1.3, '蚝油': 1.2}
LIQ = {'oil', 'water', '生抽', '老抽', '蚝油', '蒸鱼豉油', '料酒', '陈醋', '白醋'}

def M(id, dish, cont, items, t, ev, src, stir=False, target='wok', caddy=None, drum=None, merge=None, note='', extra_moves=0, optional=False):
    """items: (name, qty g or ml, dose basis). cont: L 料汁 cup | S single-moment cup | D dry-spice cup | A aromatics cup
    (may carry a dose on top) | V vessel dose at the station (no cup) | X skipped. ev: evidence for the moment."""
    return dict(id=id, dish=dish, cont=cont, items=items, t=t, ev=ev, src=src, stir=stir, target=target, caddy=caddy,
                drum=drum, merge=merge, note=note, extra_moves=extra_moves, optional=optional)

E = 'est.'
MOMENTS = [
 # ---------------- meal A (v1): 干锅土豆, 桂花糖芋头, 蚝油西兰花, 蒜蓉蒸丝瓜, 蛤蜊排骨盅
 M('A01', '蛤蜊排骨盅', 'V', [('盐', 2, 'stated "就一点盐就行了"; est. 0.5 g x 4 stew cups')], '[0:12]', 'stated',
   '文革本身很咸,就一点盐就行了', target='4 stew cups, dosed while they are assembled'),
 M('A02', '蚝油西兰花', 'V', [('盐', 5, 'stated "一勺盐"; est.')], '[1:34]', 'stated', '加一勺盐', target='soak water (wash)',
   note='optional: a wash step, not taste; not in the counts', optional=True),
 M('A03', '干锅土豆', 'S', [('oil', 10, E)], '[2:12]', 'seen (little oil left from frying)', 'pork belly slices',
   caddy='A1', note='robot fries in the fryer, so the wok needs its own oil (est.)'),
 M('A04', '干锅土豆', 'A', [('姜', 5, E), ('豆瓣酱', 10, 'seen: one heaped spoon; est. g')], '[2:14-2:16]', 'seen',
   '来点生姜,少许豆瓣酱', stir=True, caddy='A1', drum='Ad1', note='paste sticks: residue to bench-test'),
 M('A05', '干锅土豆', 'D', [('干辣椒段', 8, E), ('花椒', 3, E)], '[2:17-2:18]', 'seen (one plate, segments)',
   '干辣椒、干花椒,下', stir=True, caddy='A1', drum='Ad1'),
 M('A06', '干锅土豆', 'S', [('生抽', 10, E), ('十三香', .5, 'seen: a pinch; est.')], '[2:23-2:26]', 'stated + seen',
   '来点生抽,少许十三香', stir=True, caddy='A1', drum='Ad1'),
 M('A07', '干锅土豆', 'A', [('蒜苗+红椒', 60, E)], '[2:27-2:28]', 'seen', 'red pepper, garlic sprouts', stir=True, caddy='A1',
   note='~170 ml bulk: too big for a drum compartment'),
 M('A08', '蚝油西兰花', 'S', [('oil', 15, E)], '[2:46]', 'seen', '干净的锅里面下油', caddy='A2'),
 M('A09', '蚝油西兰花', 'S', [('盐', 2, E)], '[2:49-2:50]', 'seen', '来点盐,杀出水分', stir=True, caddy='A2', merge='A10'),
 M('A10', '蚝油西兰花', 'L', [('water', 120, 'stated "半碗水"; est. ml'), ('蚝油', 12, 'stated + seen "一勺"; est. g')],
   '[2:39-2:52]', 'seen', '碗中准备半碗水,加一勺蚝油,把它搅拌均匀', stir=True, caddy='A2'),
 M('A11', '桂花糖芋头', 'S', [('糖桂花酱', 20, 'seen 1-2 spoons; est.')], '[3:12-3:14]', 'seen', '最后淋上糖桂花酱',
   target='taro plate', caddy='A3', note='viscous: residue to bench-test'),
 M('A12', '蒜蓉蒸丝瓜', 'S', [('oil', 30, E)], '[3:33-3:36]', 'seen', '继续用热油炝香', target='wok, then tipped over the bowl',
   caddy='A3'),
 M('A13', '蒜蓉蒸丝瓜', 'A', [('蒜末+红椒', 25, E)], '[3:34]', 'seen', '碗中准备蒜末,红椒', target='sauce bowl at the plating spot',
   caddy='A3', extra_moves=1, note='sauce bowl: +1 move to the plating spot for the hot-oil tip, then poured over the luffa'),
 M('A14', '蒜蓉蒸丝瓜', 'L', [('蒸鱼豉油', 20, E), ('陈醋', 8, E)], '[3:38-3:40]', 'seen', '加蒸鱼豉油,陈醋',
   target='into the sauce bowl', caddy='A3'),
 # ---------------- meal B (v2): 红烧肉, 番茄炒蛋, 白灼秋葵娃娃菜, 清蒸鲈鱼, 鲜笋排骨汤
 M('B01', '鲜笋排骨汤', 'S', [('盐', 6, E)], '[4:20]', 'stated', '最后加盐', target='soup pot', caddy='B4', merge='B02'),
 M('B02', '鲜笋排骨汤', 'A', [('芹菜', 15, E)], '[4:23-4:24]', 'seen', '撒点芹菜', target='soup pot', caddy='B4'),
 M('B03', '红烧肉', 'A', [('葱', 10, E), ('姜', 10, E), ('料酒', 15, E)], '[0:38-0:40]', 'stated + seen',
   '五花肉冷水下锅,加去腥三件耗,葱姜料酒', target='blanch water', caddy='B1'),
 M('B04', '红烧肉', 'S', [('oil', 15, E)], '[1:01]', 'stated', '锅中下油,五花肉下锅', caddy='B1'),
 M('B05', '红烧肉', 'A', [('葱', 10, E), ('姜', 10, E)], '[1:14]', 'seen (own spoon)', '加葱姜', stir=True, caddy='B1',
   drum='Bd1', merge='B06'),
 M('B06', '红烧肉', 'D', [('八角', 2, 'seen 1-2 pieces; est. g'), ('桂皮', 3, E), ('干辣椒(整)', 2, 'seen 3-4 whole; est.')],
   '[1:16]', 'seen (own spoon)', '酱料有八角桂皮,干辣椒', stir=True, caddy='B1', drum='Bd1'),
 M('B07', '红烧肉', 'S', [('白糖', 20, 'est.; seen: he pours ready 糖色 from a small bowl (made beforehand)')], '[1:18]',
   'seen', '红烧肉少不了糖色', stir=True, caddy='B1', drum='Bd1', note='糖色 method for the robot is open (sugar in the fat, est.)'),
 M('B08', '红烧肉', 'L', [('料酒', 20, E), ('盐', 4, 'stated "一勺盐", seen small spoon; est. g'), ('生抽', 8, 'stated "少许"; est.')],
   '[1:23-1:26]', 'stated + seen (dark liquid poured from a bowl)', '加料酒,一勺盐,少许生抽', stir=True, caddy='B1', drum='Bd1'),
 M('B09', '清蒸海鲈鱼', 'S', [('蒸鱼豉油', 25, E)], '[2:18]', 'seen', '淋上蒸鱼豉油', target='fish plate', caddy='B2'),
 M('B10', '清蒸海鲈鱼', 'A', [('葱姜胡萝卜丝', 20, E)], '[2:20]', 'seen', '撒上蒸鱼三丝', target='fish plate', caddy='B2',
   note='soaked in water: drained (perforated) cup'),
 M('B11', '清蒸海鲈鱼', 'S', [('oil', 60, 'est.: one heating for the fish and the 白灼汁 bowl')], '[2:21-2:28]', 'seen',
   '高油温炝香', target='wok, tipped over the fish, rest over the 白灼 bowl', caddy='B2'),
 M('B12', '白灼汁', 'A', [('蒜末+葱白', 25, E), ('干辣椒段', 3, E)], '[2:24]', 'seen', '准备蒜末葱白,干辣椒',
   target='sauce bowl at the plating spot', caddy='B2', extra_moves=1, note='sauce bowl: +1 move to the plating spot'),
 M('B13', '白灼汁', 'L', [('蒸鱼豉油', 25, E), ('陈醋', 10, 'seen bottle; est.'), ('白糖', 5, 'seen spoon; est.')],
   '[2:30-2:34]', 'seen', '往这里面下蒸鱼豉油,陈醋,白糖', target='into the sauce bowl', caddy='B2'),
 M('B14', '番茄炒蛋', 'S', [('oil', 20, E)], '[3:26]', 'stated', '锅中下油,煎鸡蛋', caddy='B3'),
 M('B15', '番茄炒蛋', 'S', [('oil', 10, E)], '[3:32]', 'stated + seen', '锅中下油,把葱段炒香', caddy='B3'),
 M('B16', '番茄炒蛋', 'A', [('葱段', 10, E)], '[3:32]', 'seen', '把葱段炒香', stir=True, caddy='B3', drum='Bd2'),
 M('B17', '番茄炒蛋', 'S', [('盐', 3, E), ('白糖', 6, E)], '[3:35]', 'stated', '下西红柿,加盐,来点白糖', stir=True, caddy='B3',
   drum='Bd2', merge='B18'),
 M('B18', '番茄炒蛋', 'S', [('water', 60, 'seen small bowl; est. ml')], '[3:36]', 'seen', 'a little water', stir=True,
   caddy='B3', note='60 ml: over the drum liquid limit'),
 M('B19', '番茄炒蛋', 'A', [('葱叶', 8, E)], '[3:46]', 'seen', '来点葱叶子点缀', stir=True, caddy='B3', drum='Bd2'),
 M('B20', '白灼秋葵娃娃菜', 'S', [('oil', 10, E), ('盐', 6, 'stated "一勺盐"; est.')], '[3:52-3:54]', 'stated + seen',
   '锅中烧水,来点油,加一勺盐', target='blanch water', caddy='B4'),
 # ---------------- meal C (v3): 芋头蒸排骨, 酸辣土豆丝, 青椒炒鱿鱼, 清炒荷兰豆, 青瓜肉片汤
 M('C01', '芋头蒸排骨', 'V', [('生抽', 10, E), ('老抽', 4, E), ('蚝油', 10, E), ('胡椒粉', .5, 'seen shaker; est.'),
   ('淀粉', 15, 'stated "两勺"; est. g'), ('oil', 10, 'stated "一勺"; est. g')], '[0:19-0:28]', 'stated + seen',
   '两勺土豆淀粉', target='rib bowl, dosed at the station', note='mixing (抓拌, gloved hand) has no robot motion yet'),
 M('C02', '芋头蒸排骨', 'X', [('白醋', 5, E)], '[0:30-0:32]', 'stated', '你可以在它表面淋点白醋', target='taro',
   note='against itchy hands; a robot does not need it (est.)'),
 M('C03', '芋头蒸排骨', 'A', [('红椒末+葱花', 10, E)], '[3:56]', 'seen', '撒点红椒末,葱花', target='rib plate', caddy='C3'),
 M('C04', '芋头蒸排骨', 'S', [('oil', 15, 'stated "一勺热油"; est. g')], '[3:58]', 'seen', '一勺热油',
   target='wok, then tipped over the plate', caddy='C3'),
 M('C05', '酸辣土豆丝', 'S', [('oil', 5, E), ('盐', 3, E)], '[2:08-2:10]', 'stated + seen', '过水的时候,来点油',
   target='blanch water', caddy='C1'),
 M('C06', '酸辣土豆丝', 'S', [('oil', 20, E)], '[2:18]', 'seen', 'oil coats the wok', caddy='C1'),
 M('C07', '酸辣土豆丝', 'A', [('蒜末+红椒', 25, E), ('干辣椒段', 3, E)], '[2:22]', 'seen (one bowl)', 'garlic, red pepper, dried chili',
   stir=True, caddy='C1', drum='Cd1'),
 M('C08', '酸辣土豆丝', 'L', [('water', 40, 'seen; est. ml'), ('盐', 3, E), ('白醋', 10, E), ('陈醋', 10, 'seen spoon; est.'),
   ('生抽', 5, E)], '[2:26-2:34]', 'seen', '这就是调味水', stir=True, caddy='C1'),
 M('C09', '酸辣土豆丝', 'A', [('葱', 8, E)], '[2:36]', 'seen', '倒入葱叶', stir=True, caddy='C1', drum='Cd1'),
 M('C10', '青瓜肉片汤', 'V', [('盐', 1.5, E), ('淀粉', 12, 'stated "多一点"; est.')], '[2:00-2:02]', 'stated',
   '肉片里面加点盐,多一点的土豆淀粉', target='pork bowl, dosed at the station', note='上浆 mixing: no robot motion yet'),
 M('C11', '青瓜肉片汤', 'S', [('盐', 3, E)], '[2:56]', 'seen', '煮汤来点盐', target='stew pot', caddy='C2'),
 M('C12', '青瓜肉片汤', 'A', [('芹菜', 10, E), ('胡椒粉', .3, 'seen shaker; est.')], '[3:04]', 'seen (in the serving bowl)',
   '锅中下芹菜,来点胡椒粉', target='stew pot (the user serves from it)', caddy='C2'),
 M('C13', '青椒炒鱿鱼', 'S', [('oil', 15, E)], '[3:12]', 'seen', '锅中下油。', caddy='C2'),
 M('C14', '青椒炒鱿鱼', 'A', [('葱姜蒜', 15, E)], '[3:12-3:14]', 'seen', '先下葱姜蒜', stir=True, caddy='C2', drum='Cd2'),
 M('C15', '青椒炒鱿鱼', 'S', [('料酒', 10, E)], '[3:16]', 'seen', '倒入点料酒', stir=True, caddy='C2', drum='Cd2'),
 M('C16', '青椒炒鱿鱼', 'L', [('water', 60, 'seen; est. ml'), ('生抽', 10, E), ('盐', 1.5, E), ('蚝油', 10, 'seen spoon; est.'),
   ('淀粉', 5, 'seen spoon; est.')], '[3:20-3:26]', 'seen', '水中下生抽', stir=True, caddy='C2',
   note='starch settles: re-suspend just before the pour'),
 M('C17', '清炒荷兰豆', 'S', [('oil', 15, E)], '[3:36]', 'seen', '下油入锅', caddy='C3'),
 M('C18', '清炒荷兰豆', 'A', [('蒜', 8, E)], '[3:38]', 'seen', '来点蒜比较香', stir=True, caddy='C3', drum='Cd3'),
 M('C19', '清炒荷兰豆', 'S', [('盐', 2.5, E), ('water', 30, E)], '[3:40]', 'stated + seen', '来点盐,加点水', stir=True,
   caddy='C3', drum='Cd3'),
]

# ---------------------------------------------------------------- model constants (seconds; basis in the comment)
T = dict(pour=8,          # pick-pour at the wok/plate: meal16 ARM['pour'] = 8 s, an ASSUMPTION (pour pose checked 23/72 in R14, never chained)
         ret=4,           # empty cup back into its caddy slot (est.)
         cup0=22,         # P0 cup-only cycle: R14 timeline14 rates 6 + 8 s staging + 8 s pour (R19 S_CUP)
         caddy_in=12,     # caddy from the station dock to the staging spot: hub corridor H_SINK-H_WOK 4.0 s (checked, empty tuck) + 2 spurs ~4 s (est.)
         caddy_out=8,     # used caddy to the wash basket (est.)
         drum_in=12, drum_out=8,   # drum into / out of the servo rim holder (est.)
         drum_roll=10,    # arm-held drum: roll through 2-4 compartments, >= 1.3-2.0 s apart (R14 pourbox) + spatula park (est.)
         vessel=14,       # prep bowl to the station and back, 2 moves (R19 S_VESSEL)
         pick=6, shake=15, squeeze=15)   # prep-phase station work by the arm (est.; R19 S_SQUEEZE = 15)
DRUM_LIQ_ML, DRUM_BULK_ML = 35, 100   # per compartment, est. (R14 drum Ø80x140, 4 compartments; liquids never simulated)
CUP_S_ML, CUP_L_ML, CUP_L_BULK = 50, 160, 220   # S cup ~100 ml brimful, L cup ~300 ml brimful: liquids <= ~50-55 %, loose aromatics <= ~75 % (est.)

def vol(items):
    return sum(q / RHO.get(n, .35 if (n in AROMATIC or n not in LIQ) else 1.) for n, q, _ in items)
def liq(items): return sum(q for n, q, _ in items if n in LIQ)
def seasoned(m): return any(n not in AROMATIC for n, _, _ in m['items'])

def check_src():
    blob = json.dumps(HSJ, ensure_ascii=False)
    tx = ''
    for k in (1, 2, 3):
        p = os.path.join(TX_DIR, f'v{k}.txt')
        if os.path.exists(p): tx += open(p, encoding='utf-8').read()
    miss = [m['id'] for m in MOMENTS if m['src'] not in blob and m['src'] not in tx]
    return miss, bool(tx)

def apply_merges(moms):
    """Taste-neutral merges (est.): the merged moment's items go into its partner's container."""
    by = {m['id']: dict(m, items=list(m['items'])) for m in moms}
    for m in moms:
        if m['merge'] and m['merge'] in by:
            p = by[m['merge']]; p['items'] = p['items'] + m['items']; p['stir'] = p['stir'] or m['stir']
            if p['cont'] == 'A' and m['cont'] == 'D': p['cont'] = 'A'
            del by[m['id']]
    out = list(by.values())
    for m in out:   # a drum compartment must still fit after a merge
        if m['drum'] and not drum_ok(m): m['drum'] = None
    return out

def size(m):
    v, l = vol(m['items']), liq(m['items'])
    return 'S' if v <= CUP_S_ML else 'L' if (l <= CUP_L_ML and v <= CUP_L_BULK) else 'XL'

def drum_ok(m): return liq(m['items']) <= DRUM_LIQ_ML and vol(m['items']) <= DRUM_BULK_ML

def plan(moms, meal, seasoning_only=False):
    ms = [m for m in moms if m['id'][0] == meal and m['cont'] != 'X' and not m['optional']]
    V = [m for m in ms if m['cont'] == 'V']
    C = [m for m in ms if m['cont'] not in ('V',)]
    if seasoning_only: C = [m for m in C if seasoned(m)]
    caddies = sorted({m['caddy'] for m in ms if m['caddy']})
    drums = sorted({m['drum'] for m in ms if m['drum'] and drum_ok(m)})
    in_drum = [m for m in C if m['drum'] in drums]
    cups_p2 = [m for m in C if m not in in_drum]
    xm = sum(m['extra_moves'] for m in C)
    stir_cups_p1 = sum(m['stir'] for m in C); stir_cups_p2 = sum(m['stir'] for m in cups_p2)
    r = {}
    r['P0'] = dict(moves=3 * len(C) + 2 * len(V) + xm, secs=T['cup0'] * len(C) + T['vessel'] * len(V) + 5 * xm, stir_stops=stir_cups_p1)
    base_m = 2 * len(caddies) + 2 * len(V) + xm; base_s = (T['caddy_in'] + T['caddy_out']) * len(caddies) + T['vessel'] * len(V) + 5 * xm
    r['P1'] = dict(moves=base_m + 2 * len(C), secs=base_s + (T['pour'] + T['ret']) * len(C), stir_stops=stir_cups_p1)
    r['P2'] = dict(moves=base_m + 2 * len(cups_p2) + 2 * len(drums),
                   secs=base_s + (T['pour'] + T['ret']) * len(cups_p2) + (T['drum_in'] + T['drum_out']) * len(drums), stir_stops=stir_cups_p2)
    r['P2h'] = dict(moves=base_m + 2 * len(cups_p2) + 3 * len(drums),
                    secs=base_s + (T['pour'] + T['ret']) * len(cups_p2) + (T['drum_in'] + T['drum_roll'] + T['drum_out']) * len(drums),
                    stir_stops=stir_cups_p2 + len(drums))
    for k in r: r[k]['cook_phase_secs'] = r[k]['secs'] - T['vessel'] * len(V)   # vessel doses happen in prep
    sizes = collections.Counter(size(m) for m in cups_p2); sizes_all = collections.Counter(size(m) for m in C)
    return dict(containers=len(C), by_type=dict(collections.Counter(m['cont'] for m in C)), vessel_doses=len(V), caddies=len(caddies),
                drums=len(drums), drum_compartments=len(in_drum), cups_p2=len(cups_p2), cup_sizes_p2=dict(sizes), cup_sizes_p1=dict(sizes_all),
                plans=r)

def prep_phase(meal):
    ms = [m for m in MOMENTS if m['id'][0] == meal]
    picks = sum(1 for m in ms for n, q, _ in m['items'] if DOSER.get(n) == 'arm pick')
    shakes = sum(1 for m in ms for n, q, _ in m['items'] if DOSER.get(n) == 'shaker')
    sq = sum(1 for m in ms for n, q, _ in m['items'] if DOSER.get(n) == 'squeeze')
    # whole spices: about 1 pick per piece; 八角 1-2, 桂皮 1, whole chili 3-4 (seen) -> 6 picks for the 红烧肉 cup (est.)
    npick = 6 if picks else 0
    return dict(spice_picks=npick, shakes_if_arm=shakes, squeezes=sq, secs=npick * T['pick'] + shakes * T['shake'] + sq * T['squeeze'])

def bulk(meal):
    tot = collections.defaultdict(float)
    for m in MOMENTS:
        if m['id'][0] != meal or m['cont'] == 'X' or m['optional']: continue
        for n, q, _ in m['items']:
            if n not in AROMATIC: tot[n] += q
    return dict(sorted(tot.items(), key=lambda kv: -kv[1]))

# ---------------------------------------------------------------- station parts (CNY, unconfirmed; tags as in r19_seasoning_sizing.md)
PARTS = [  # (part, qty, unit lo, unit hi, basis, group)
 ('Peristaltic pumps: oil, water, 生抽, 老抽, 蚝油 (wide bore), 蒸鱼豉油, 料酒, 陈醋, 白醋', 9, 133, 442, '[1688 2026-10-13] via r19', 'core'),
 ('Drivers, food-grade tube (GB 4806.16 silicone / BPT), bottles, fittings', 9, 50, 100, 'est. (r19)', 'core'),
 ('Outlet manifold over the fill point, suck-back, drip tray', 1, 100, 300, 'est. (r19 nozzle-cluster line)', 'core'),
 ('Loss-in-weight load cell + HX711 under each bottle / the oil and water jugs', 9, 10, 55, '[1688] via r19', 'core'),
 ('Sealed dry dosers for real salt, real white sugar, potato starch (agitated auger, or cell wheel at the low end)', 3, 150, 1000,
  'cell wheel est. 150-400 (r19); auger est. 400-1,000 each (r14/r19: 4 augers 1.6-4k)', 'core'),
 ('Whole-spice portioners: 干辣椒段, 花椒 (agitated cell wheel; pet-feeder donor ¥138)', 2, 150, 400, 'est.; [1688] donor via r19', 'core'),
 ('Open spice tray (八角, 桂皮, whole chili) + a station colour camera for arm picks', 1, 120, 550, 'tray est. 20-50; colour cam est. 100-500 (r19 row 11)', 'core'),
 ('Motorised shaker-tappers for 十三香 and 胡椒粉 (inverted sieve-lid jar + vibration motor)', 2, 50, 150, 'est.; 0 if the arm shakes the jars', 'core'),
 ('Squeeze bottles: 豆瓣酱, 糖桂花酱 (+3 for Wang Gang pastes), squeezed by the arm over the cup', 5, 5, 20, 'est. (r19)', 'core'),
 ('Weigh bucket on a 1 kg cell + HX711 + dump servo (all dry doses are weighed here, then dropped into the cup)', 1, 60, 300,
  'cell ¥10-150 [1688] via r19 + servo/bucket est.', 'core'),
 ('Caddy XY indexer under the outlets (fills the 2x3 caddy without the arm)', 1, 300, 600, 'est., no source', 'core'),
 ('Drum fill cradle (turns each drum slot up under the outlet)', 1, 100, 200, 'est.', 'core'),
 ('Sealed dry enclosure: door seal, shutters, silica-gel / sieve cartridges, RH sensor', 1, 100, 400, 'est. (r14 countermeasures)', 'core'),
 ('Magnetic stir pad at the staging slot for starch 料汁 cups + captive stir bars', 1, 50, 150, 'stirrer ¥43-95 [1688] via r19 + est.', 'core'),
 ('Controller (MCU, ~18 stepper/servo channels, 11 HX711), enclosure', 1, 500, 1500, 'est. (r19)', 'core'),
 ('Robot cups: 304 stainless with a keyed 30 mm lug block, 12 S (~100 ml) + 12 L (~300 ml)', 24, 15, 40, 'est., unpriced', 'core'),
 ('Stainless wire caddies 2x3 (also the dishwasher basket)', 6, 30, 80, 'est., unpriced', 'core'),
 ('Pour drums (Ø80x140, 4 compartments) x3 + servo rim holder', 1, 400, 1200, 'r19 row 28 "drum + holder + ~20 cups 400-1,000" (est.), widened for 3 drums', 'core'),
 ('3 spare pump channels (Wang Gang: 香油, 红油, MSG solution or later)', 3, 193, 597, 'pump + tube + cell, as above', 'spare'),
 ('Chilled compartment (Peltier) for 蚝油', 1, 150, 400, 'est. (r19 e4)', 'chill'),
]
def parts_total(groups):
    lo = sum(q * a for _, q, a, b, _, g in PARTS if g in groups); hi = sum(q * b for _, q, a, b, _, g in PARTS if g in groups)
    return lo, hi

if __name__ == '__main__':
    miss, have_tx = check_src()
    print('src phrases not found (JSON + transcripts%s):' % ('' if have_tx else ' MISSING, JSON only'), miss)
    merged = apply_merges(MOMENTS)
    out = dict(compare_r19=dict(note='seasoning arm moves (s) per meal A/B/C from results/r19seas/options.json and r19_seasoning_sizing.md',
               a_today_R14_with_drum=[[18, 132], [27, 198], [24, 176]], cups_only_R19=[[33, 242], [45, 330], [42, 308]],
               b_rightsized=[[22, 162], [27, 198], [24, 176]], d_direct=[[12, 88], [3, 22], [6, 42]]),
               moments=MOMENTS, constants=dict(T=T, drum_liq_ml=DRUM_LIQ_ML, drum_bulk_ml=DRUM_BULK_ML, cup_s_ml=CUP_S_ML, cup_l_ml=CUP_L_ML),
               meals={}, parts=PARTS, src_missing=miss)
    print('\n| meal | variant | containers (seasoning / all) | by type (all) | V | caddies | drums (compartments) | cups left with drums (S/L) |'
          ' P0 moves | P1 moves | P2 moves | P2h moves | P2 cook-phase s (seasoning / all) | in-stir cup pours P1 -> P2 |')
    print('|' + '---|' * 14)
    for meal in 'ABC':
        out['meals'][meal] = {}
        for var, moms in (('as he does', MOMENTS), ('merged', merged)):
            a = plan(moms, meal); s = plan(moms, meal, seasoning_only=True)
            out['meals'][meal][var] = dict(all=a, seasoning=s)
            print(f"| {meal} | {var} | {s['containers']} / {a['containers']} | {a['by_type']} | {a['vessel_doses']} | {a['caddies']} | "
                  f"{a['drums']} ({a['drum_compartments']}) | {a['cups_p2']} ({a['cup_sizes_p2'].get('S',0)}/{a['cup_sizes_p2'].get('L',0)}) | "
                  f"{s['plans']['P0']['moves']} / {a['plans']['P0']['moves']} | {s['plans']['P1']['moves']} / {a['plans']['P1']['moves']} | "
                  f"{s['plans']['P2']['moves']} / {a['plans']['P2']['moves']} | {s['plans']['P2h']['moves']} / {a['plans']['P2h']['moves']} | "
                  f"{s['plans']['P2']['cook_phase_secs']} / {a['plans']['P2']['cook_phase_secs']} | {a['plans']['P1']['stir_stops']} -> {a['plans']['P2']['stir_stops']} |")
        out['meals'][meal]['prep_phase'] = prep_phase(meal); out['meals'][meal]['bulk_g'] = bulk(meal)
    print('\nper-moment cup size and drum fit:')
    for m in MOMENTS:
        if m['cont'] in ('V', 'X'): continue
        print(f"  {m['id']} {m['dish']} {m['cont']} vol~{vol(m['items']):.0f} ml liq {liq(m['items']):.0f} ml -> {size(m)}"
              f"{'  drum ' + m['drum'] + (' ok' if drum_ok(m) else ' TOO BIG') if m['drum'] else ''}{'  (in stir)' if m['stir'] else ''}")
    print('\nprep-phase arm work at the station (not in the cooking timeline):', {k: out['meals'][k]['prep_phase'] for k in 'ABC'})
    print('\nbulk use per meal (g or ml):')
    for k in 'ABC': print(' ', k, {n: round(q, 1) for n, q in out['meals'][k]['bulk_g'].items()})
    print('\ntime per plan, all containers, as he does (s): ', {k: {p: v['secs'] for p, v in out['meals'][k]['as he does']['all']['plans'].items()} for k in 'ABC'})
    for grp, lab in ((('core',), '9 channels'), (('core', 'spare'), '9 + 3 spare channels'), (('core', 'spare', 'chill'), '+ chilled 蚝油 box')):
        lo, hi = parts_total(grp); print(f'parts total, {lab}: ¥{lo:,.0f} - ¥{hi:,.0f}'); out.setdefault('parts_total', {})[lab] = [lo, hi]
    os.makedirs(os.path.join(HERE, 'results', 'r19seas'), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, 'results', 'r19seas', 'cups.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
