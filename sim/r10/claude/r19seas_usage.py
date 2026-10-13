"""R19 seasoning-station sizing: seasoning usage, forms, burst behaviour and top-N coverage.
Inputs (read only):
  research/homestyle_meals.json   (main reference: the user's 3 home-style meals, 15 dishes)
  research/wanggang_recipes.json  (wider check: 42 Wang Gang recipes, structured seasoning events)
The home-style JSON has no structured seasoning events, so its events are hand-coded below from the
step text of homestyle_meals.json (quoted in 'src'). Doses there are only what he says ('1 spoon',
'a little'); grams are ND. Wang Gang grams are his own (g_basis in the JSON).
Usage: python r19seas_usage.py  -> results/r19seas/usage.json + markdown on stdout"""
import json, os, collections, statistics as st

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..')
WG = json.load(open(os.path.join(ROOT, 'research', 'wanggang_recipes.json'), encoding='utf-8'))
HSJ = json.load(open(os.path.join(ROOT, 'research', 'homestyle_meals.json'), encoding='utf-8'))

# ---------------------------------------------------------------- canonical names and forms
CANON = {'酱油': '生抽', '植物油': 'oil', '菜籽油': 'oil', '明油': 'oil', '黑胡椒': '胡椒粉', '白胡椒粒': '胡椒粉',
         '水淀粉': '淀粉', '泡椒末': '泡椒', '红泡椒': '泡椒'}
FORM = {  # form as stored/handled; 'how' = what a station would have to do
 'oil': ('oil', 'pump'), '盐': ('granular, soluble', 'dissolve -> brine'), '白糖': ('granular, soluble', 'syrup'),
 '冰糖': ('lumps, soluble', 'syrup (sub)'), '味精': ('granular, soluble', 'solution'), '鸡精': ('powder, mostly soluble', '鸡汁 liquid (sub) or solution'),
 '生抽': ('thin liquid', 'pump'), '老抽': ('thin liquid (dark)', 'pump'), '蒸鱼豉油': ('thin liquid', 'pump'),
 '料酒': ('thin liquid', 'pump'), '醋(白)': ('thin liquid', 'pump'), '醋(深色)': ('thin liquid', 'pump'), '醋(未注明)': ('thin liquid', 'pump'),
 '蚝油': ('viscous liquid', 'pump, wide bore'), '淀粉': ('powder, insoluble', 'stirred slurry'),
 '胡椒粉': ('powder, insoluble', 'auger or grinder'), '花椒面': ('powder', 'auger or grinder'), '辣椒面': ('powder', 'auger'),
 '十三香': ('powder blend', 'auger'), '五香粉': ('powder blend', 'auger'),
 '花椒': ('whole spice', 'vibratory feeder'), '干辣椒': ('whole spice (light, bulky)', 'vibratory feeder'),
 '八角': ('whole spice (pieces)', 'count / sachet'), '桂皮': ('whole spice (pieces)', 'count / sachet'), '香叶': ('whole spice (leaves)', 'count / sachet'),
 '草果': ('whole spice (pieces)', 'count / sachet'), '小茴香': ('whole spice (seeds)', 'sachet'),
 '豆瓣酱': ('chunky paste', 'extruder'), '甜面酱': ('paste', 'extruder'), '黄豆酱': ('paste', 'extruder'), '芝麻酱': ('paste', 'extruder'),
 '番茄酱': ('paste, pumpable', 'pump wide bore / extruder'), '糖桂花酱': ('syrup with flowers', 'pump wide bore / extruder'),
 '豆豉': ('wet granular', 'feeder / cup'), '泡椒': ('wet pickled solids', 'cup'), '泡姜': ('wet pickled solids', 'cup'), '芽菜': ('wet pickled solids', 'cup'),
 '火锅底料': ('solid fat block', 'cup / portion pack'), '香油': ('oil', 'pump'), '红油': ('oil with sediment', 'pump (settles)'),
 '花椒油': ('oil', 'pump'), '葱油': ('oil (homemade)', 'pump'), '猪油': ('semi-solid fat', 'heated pump / cup'),
 '糖色': ('intermediate (from sugar)', 'made in the wok from sugar'), '椒盐粉': ('homemade powder', 'made from salt + 花椒'),
 '刀口辣椒': ('homemade (chili + 花椒)', 'made from 干辣椒 + 花椒'), '鱼酱油': ('homemade liquid', 'pump'),
 '啤酒': ('bulk liquid', 'ingredient'), '可乐': ('bulk liquid', 'ingredient'), '浓缩橙汁': ('liquid', 'ingredient'), '小苏打': ('powder', 'prep'),
}
AROMATIC = {'蒜', '姜', '葱', '大葱', '香葱', '小米辣', '二荆条/小米辣', '香菜', '香菜/香葱', '葱头', '蒜苗', '红椒', '青红椒', '胡萝卜/红椒', '辣椒籽'}
WATERISH = {'清水', '清汤', '清汤/清水', '清水/清汤', '鸡汤', '鲜汤', '热水', '开水', '清水(开水)', '水'}
INGREDIENT = {'蛋清', '蛋黄', '花生', '花生碎', '熟芝麻', '香菇', '肉末', '面粉'}
COMPOSITE = {'碗汁', '料汁', '鱼香汁', '碗芡', '茄汁', '甜面酱+老抽 bowl'}  # references to premixes listed elsewhere
BULK = {'啤酒', '可乐', '浓缩橙汁', '小苏打'}

def canon(name, variant=None):
    if name == '醋':
        if variant in ('白醋', '米醋'): return '醋(白)'
        if variant in ('陈醋', '香醋', '保宁醋', '镇江醋'): return '醋(深色)'
        return '醋(未注明)'
    return CANON.get(name, name)

def kind(n):
    if n in AROMATIC: return 'aromatic'
    if n in WATERISH: return 'water'
    if n in INGREDIENT or n in BULK: return 'ingredient'
    if n in COMPOSITE: return 'composite'
    return 'seasoning'

# ---------------------------------------------------------------- home-style events (hand-coded)
# stage: wok | blanch (salted/oiled water in the wok) | marinade | sauce (bowl/plate, off-wok) | plate | pot | cups | wash | fryer
HS = [
 ('A', '蛤蜊排骨盅', [('cups', ['盐'], [], {'盐': 'a little per cup'}, 'per cup: 4 rib pieces, 1 ginger slice, 3 clams, a little salt')]),
 ('A', '桂花糖芋头', [('plate', ['糖桂花酱'], [], {'糖桂花酱': 'drizzle'}, 'drizzle 糖桂花酱')]),
 ('A', '干锅土豆', [('fryer', ['oil'], [], {'oil': 'wide oil (deep-fry, 六成)'}, 'fry about 3 min'),
                 ('wok', ['豆瓣酱'], ['姜'], {'豆瓣酱': 'a little'}, 'pork belly slices, ginger, a little 豆瓣酱 -> red oil'),
                 ('wok', ['干辣椒', '花椒'], [], 'ND', 'dried chili + Sichuan pepper'),
                 ('wok', ['生抽', '十三香'], [], {'十三香': 'a little'}, '生抽, a little 十三香')]),
 ('A', '蚝油西兰花', [('wok', ['oil'], [], 'ND', 'oil, broccoli'), ('wok', ['盐'], [], 'ND', 'salt'),
                  ('wok', ['蚝油'], [], {'蚝油': '1 spoon (in half a bowl of water)'}, 'sauce bowl: half bowl water + 1 spoon oyster sauce')]),
 ('A', '蒜蓉蒸丝瓜', [('wok', ['oil'], [], 'ND', 'hot oil poured over (炝香)'),
                  ('sauce', ['蒸鱼豉油', '醋(深色)'], ['蒜'], 'ND', 'bowl of minced garlic + red chili, hot oil, 蒸鱼豉油 + 陈醋')]),
 ('B', '鲜笋排骨汤', [('pot', ['盐'], [], 'ND', 'salt, celery; ladle out')]),
 ('B', '红烧肉', [('blanch', ['料酒'], ['葱', '姜'], 'ND', 'cold water with scallion, ginger, wine'),
               ('wok', ['oil'], [], 'ND', 'oil, pork fried to render'),
               ('wok', ['八角', '桂皮', '干辣椒'], ['葱', '姜'], 'ND', 'scallion, ginger, star anise, cinnamon, dried chili'),
               ('wok', ['白糖'], [], {'白糖': 'ND (糖色; sugar type not stated)'}, '糖色'),
               ('wok', ['料酒', '盐', '生抽'], [], {'盐': '1 spoon', '生抽': 'a little'}, 'wine, 1 spoon salt, a little 生抽')]),
 ('B', '清蒸海鲈鱼', [('plate', ['蒸鱼豉油'], [], 'ND', 'pour off the fishy water, 蒸鱼豉油'),
                  ('wok', ['oil'], [], 'ND', 'very hot oil over')]),
 ('B', '番茄炒蛋', [('wok', ['oil'], [], 'ND', 'oil, eggs set'), ('wok', ['oil'], ['葱'], 'ND', 'oil, scallion'),
                ('wok', ['盐', '白糖'], [], 'ND', 'tomato, salt, sugar, a little water')]),
 ('B', '白灼秋葵娃娃菜', [('blanch', ['oil', '盐'], [], 'ND', 'wok of water + oil + salt'),
                    ('sauce', ['干辣椒'], ['蒜', '葱'], 'ND', 'bowl of garlic, scallion white, dried chili'),
                    ('wok', ['oil'], [], 'ND', 'the remaining hot oil poured in'),
                    ('sauce', ['蒸鱼豉油', '醋(深色)', '白糖'], [], 'ND', '蒸鱼豉油, 陈醋, sugar')]),
 ('C', '芋头蒸排骨', [('marinade', ['生抽', '老抽', '蚝油', '胡椒粉', '淀粉', 'oil'], [], {'淀粉': '2 spoons (potato starch)', 'oil': '1 spoon'},
                    'ribs marinated: 生抽, 老抽, 蚝油, pepper, 2 spoons potato starch, 1 spoon oil'),
                  ('wash', ['醋(白)'], [], 'ND', 'taro (white vinegar against itching)'),
                  ('wok', ['oil'], ['葱'], {'oil': '1 spoon'}, 'red chili, scallion, 1 spoon hot oil')]),
 ('C', '青椒炒鱿鱼', [('wok', ['oil'], ['葱', '姜', '蒜'], 'ND', 'oil, scallion/ginger/garlic, green pepper'),
                  ('wok', ['料酒'], [], 'ND', 'wine'),
                  ('wok', ['生抽', '盐', '蚝油', '淀粉'], [], 'ND', 'sauce (water, 生抽, salt, 蚝油, potato starch)')]),
 ('C', '酸辣土豆丝', [('blanch', ['oil', '盐'], [], 'ND', 'into boiling water with oil and salt'),
                  ('wok', ['oil'], [], 'ND', 'oil coats the wok'),
                  ('wok', ['干辣椒'], ['蒜'], 'ND', 'garlic, red pepper, dried chili'),
                  ('wok', ['盐', '醋(白)', '醋(深色)', '生抽'], [], 'ND', '调味水 (salt, white vinegar, 陈醋, 生抽)')]),
 ('C', '青瓜肉片汤', [('marinade', ['盐', '淀粉'], [], {'淀粉': 'plenty'}, 'salt + plenty of potato starch (上浆)'),
                  ('wok', ['盐'], ['姜'], 'ND', 'ginger, cucumber, pork slices into rolling boil; salt'),
                  ('bowl', ['胡椒粉'], [], 'ND', 'celery and white pepper in the serving bowl')]),
 ('C', '清炒荷兰豆', [('wok', ['oil'], ['蒜'], 'ND', 'oil, garlic, snow peas'), ('wok', ['盐'], [], 'ND', 'salt, a little water')]),
]

def check_hs_src():
    """every hand-coded 'src' phrase must be traceable in homestyle_meals.json (loose check: first 12 chars)."""
    blob = json.dumps(HSJ, ensure_ascii=False)
    missing = [s for _, _, evs in HS for *_, s in evs if s[:12] not in blob]
    return missing

# ---------------------------------------------------------------- Wang Gang events
def wg_events():
    out = []
    for r in WG['recipes']:
        evs = []
        prev_wok = None
        for e in r['events']:
            items = [it for it in e['items'] if 'name' in it]
            seas, arom, grams = [], [], {}
            for it in items:
                n = canon(it['name'], it.get('variant'))
                k = kind(it['name'])
                if k == 'aromatic': arom.append(n); continue
                if k != 'seasoning': continue
                if n == '淀粉' and e['stage'] == 'coat' and (it.get('g') or 0) >= 40: continue  # 挂糊 starch = staple
                seas.append(n)
                if it.get('g') is not None and e['stage'] not in ('wash',) and not (n == '盐' and it['g'] > 20):
                    grams.setdefault(n, []).append(it['g'])
            has_ingr = any('ingredient' in it for it in e['items'])
            evs.append(dict(stage=e['stage'], seas=sorted(set(seas)), arom=arom, grams=grams, gap=e.get('gap_s'),
                            gap_basis=e.get('gap_basis'), ingredient=has_ingr))
        out.append((r['id'], r['dish'], evs))
    return out

# ---------------------------------------------------------------- analysis
def usage_hs():
    dishes = collections.defaultdict(set); uses = collections.Counter(); multi = collections.Counter(); offwok = collections.Counter()
    wokuses = collections.Counter(); doses = collections.defaultdict(list); witharom = collections.Counter()
    for meal, dish, evs in HS:
        for stg, seas, arom, dose, src in evs:
            if stg == 'wash': continue
            for s in seas:
                dishes[s].add(dish); uses[s] += 1
                if len([x for x in seas if x != 'oil']) >= 2 and s != 'oil': multi[s] += 1
                if stg in ('wok', 'blanch', 'fryer'): wokuses[s] += 1
                else: offwok[s] += 1
                if arom: witharom[s] += 1
                if isinstance(dose, dict) and s in dose: doses[s].append(dose[s])
    return dishes, uses, multi, offwok, wokuses, doses, witharom

def usage_wg(evlist):
    dishes = collections.defaultdict(set); grams = collections.defaultdict(list); wok = collections.Counter(); off = collections.Counter()
    multi = collections.Counter(); burst = collections.Counter(); witharom = collections.Counter(); uses = collections.Counter()
    for rid, dish, evs in evlist:
        wok_idx = [i for i, e in enumerate(evs) if e['stage'] in ('wok', 'finish')]
        for i, e in enumerate(evs):
            if e['stage'] == 'wash': continue
            for s in e['seas']:
                dishes[s].add(dish); uses[s] += 1
                for g in e['grams'].get(s, []): grams[s].append(g)
                if e['stage'] in ('wok', 'finish', 'blanch', 'boil'): wok[s] += 1
                else: off[s] += 1
                if len([x for x in e['seas'] if x != 'oil']) >= 2 and s != 'oil': multi[s] += 1
                if e['arom']: witharom[s] += 1
            if i in wok_idx and e['seas']:
                k = wok_idx.index(i)
                g_this = e['gap'] if k > 0 else None
                g_next = evs[wok_idx[k + 1]]['gap'] if k + 1 < len(wok_idx) else None
                if (g_this is not None and g_this <= 5) or (g_next is not None and g_next <= 5):
                    for s in e['seas']: burst[s] += 1
    return dishes, uses, grams, wok, off, multi, burst, witharom

def coverage(dish_sets, ranking, Ns, subs=None):
    """dish_sets: {dish: set(seasonings)}; a dish is covered when every seasoning is in top-N (after substitution)."""
    res = {}
    total_uses = sum(len(v) for v in dish_sets.values())
    for N in Ns:
        top = set(ranking[:N])
        def ok(s):
            if s in top: return True
            if subs and s in subs: return all(x in top for x in subs[s])
            return False
        full = sum(1 for v in dish_sets.values() if all(ok(s) for s in v))
        used = sum(1 for v in dish_sets.values() for s in v if ok(s))
        res[N] = dict(dishes_full=full, dishes=len(dish_sets), uses_cov=used, uses=total_uses, top=ranking[:N])
    return res

# substitutions judged acceptable for a fully automatic home station (est., my judgement, flagged in the report)
SUBS = {'冰糖': ['白糖'], '糖色': ['白糖'], '鸡精': ['味精'], '蒸鱼豉油': ['生抽', '白糖'], '醋(未注明)': ['醋(深色)'],
        '椒盐粉': ['盐', '花椒'], '刀口辣椒': ['干辣椒', '花椒'], '葱油': ['oil'], '猪油': ['oil'], '鱼酱油': ['生抽'],
        '花椒面': ['花椒'], '五香粉': ['十三香'], '十三香': ['五香粉']}

if __name__ == '__main__':
    miss = check_hs_src()
    hs_d, hs_u, hs_multi, hs_off, hs_wok, hs_doses, hs_arom = usage_hs()
    wgev = wg_events()
    wg_d, wg_u, wg_g, wg_wok, wg_off, wg_multi, wg_burst, wg_arom = usage_wg(wgev)
    names = sorted(set(hs_d) | set(wg_d), key=lambda s: (-len(hs_d.get(s, ())), -len(wg_d.get(s, ())), s))
    print('hand-coded src phrases not found in homestyle_meals.json:', miss)
    print('\n| seasoning | form | how a station handles it | HS dishes /15 | HS uses: wok / off-wok | HS dose said | WG dishes /42 | WG g min/median/max (n) | WG uses: wok / off-wok | WG wok-or-off uses in a multi-seasoning event | WG wok uses in a <=5 s burst | WG uses with fresh aromatics |')
    print('|' + '---|' * 12)
    rows = []
    for s in names:
        f, how = FORM.get(s, ('?', '?'))
        g = wg_g.get(s, [])
        gtxt = f"{min(g):g}/{st.median(g):g}/{max(g):g} ({len(g)})" if g else 'ND'
        hsd = '; '.join(sorted(set(hs_doses.get(s, [])))) or 'ND'
        row = dict(seasoning=s, form=f, how=how, hs_dishes=len(hs_d.get(s, ())), hs_wok=hs_wok[s], hs_off=hs_off[s], hs_dose=hsd,
                   wg_dishes=len(wg_d.get(s, ())), wg_g=g, wg_wok=wg_wok[s], wg_off=wg_off[s], wg_uses=wg_u[s], wg_multi=wg_multi[s],
                   wg_burst=wg_burst[s], wg_arom=wg_arom[s])
        rows.append(row)
        print(f"| {s} | {f} | {how} | {row['hs_dishes']} | {hs_wok[s]} / {hs_off[s]} | {hsd} | {row['wg_dishes']} | {gtxt} | {wg_wok[s]} / {wg_off[s]} | {wg_multi[s]}/{wg_u[s]} | {wg_burst[s]} | {wg_arom[s]} |")

    # coverage curves
    Ns = [4, 6, 8, 10, 12, 16, 20]
    hs_sets = {}
    for meal, dish, evs in HS:
        hs_sets[dish] = {s for stg, seas, *_ in evs if stg != 'wash' for s in seas}
    wg_sets = {dish: {s for e in evs if e['stage'] != 'wash' for s in e['seas']} for rid, dish, evs in wgev}
    # ranking: HS dish count, ties broken by WG dish count (main reference first)
    rank_hs = sorted(set(hs_d) | set(wg_d), key=lambda s: (-len(hs_d.get(s, ())), -len(wg_d.get(s, ())), s))
    rank_wg = sorted(set(wg_d), key=lambda s: (-len(wg_d.get(s, ())), -len(hs_d.get(s, ())), s))
    cov = {}
    for lab, rk in (('rank_by_homestyle', rank_hs), ('rank_by_wanggang', rank_wg)):
        cov[lab] = {}
        for setlab, sets in (('homestyle', hs_sets), ('wanggang', wg_sets)):
            cov[lab][setlab + '_strict'] = coverage(sets, rk, Ns)
            cov[lab][setlab + '_subs'] = coverage(sets, rk, Ns, SUBS)
    print('\nRanking by home-style count (ties: Wang Gang):', rank_hs[:24])
    print('Ranking by Wang Gang count:', rank_wg[:24])
    for lab in cov:
        print(f'\n{lab}: N | HS dishes fully covered (strict / with subs) | HS uses covered | WG dishes fully covered (strict / subs) | WG uses covered')
        for N in Ns:
            a, b = cov[lab]['homestyle_strict'][N], cov[lab]['homestyle_subs'][N]
            c, d = cov[lab]['wanggang_strict'][N], cov[lab]['wanggang_subs'][N]
            print(f"| {N} | {a['dishes_full']}/{a['dishes']} / {b['dishes_full']}/{b['dishes']} | {a['uses_cov']}/{a['uses']} ({100*a['uses_cov']/a['uses']:.0f} %) "
                  f"| {c['dishes_full']}/{c['dishes']} / {d['dishes_full']}/{d['dishes']} | {c['uses_cov']}/{c['uses']} ({100*c['uses_cov']/c['uses']:.0f} %) | top: {', '.join(a['top'])}")

    os.makedirs('results/r19seas', exist_ok=True)
    json.dump(dict(rows=rows, rank_homestyle=rank_hs, rank_wanggang=rank_wg, coverage=cov, subs=SUBS,
                   hs_events=[dict(meal=m, dish=d, events=[dict(stage=a, seas=b, arom=c, dose=x, src=y) for a, b, c, x, y in ev]) for m, d, ev in HS]),
              open('results/r19seas/usage.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
