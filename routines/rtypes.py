# Routine type catalogue. Status vocabulary: demo | demo_ready | sim_motion_checked | needs_check | needs_hardware | two_hands
# Movement-set statuses come from sim/r10/claude/results/r19/prim/library_size.json (R19_MOTION_LIBRARY §9):
#   verified: CARRIER_IN/OUT, FAUCET_OPEN/CLOSE, LID_OFF_pot, LID_ON_pot, SPATULA_FETCH/STOW, SPIDER_FETCH,
#             SPIDER_SCOOP_pot, SPIDER_DUMP_plate, SPIDER_STOW, WOK_PLATE_RINSE
#   composed_from_verified: WOK_DUMP_RINSE, WOK_FILL      partially_verified: STIR_CYCLE_dice
#   everything else (CUP_*, DRUM_LOAD, LID_*_wok, LID_*_stew, SPIDER_SCOOP_wok/fryer, WOK_OIL_POUR, ARRANGE, ...) not verified.

def P(name, unit, rng):
    return dict(name=name, unit=unit, typical=rng)

T = []

def t(id, zh, en, cat, purpose, params, steps, stop, sensors, msets, hw, status, notes=''):
    T.append(dict(id=id, name_zh=zh, name_en=en, category=cat, purpose=purpose, parameters=params, steps=steps,
                  stop_condition=stop, sensors_needed=sensors, movement_sets=msets, hardware_needed=hw,
                  status=status, notes=notes))

LV = P('level', '0–1 knob', '0.3 low · 0.5 medium · 0.7 med-high · 1.0 full')
SEC = lambda r: P('seconds', 's', r)
CUPSETS = ['CUP_FETCH', 'CUP_POUR_wok', 'CUP_RETURN']
STIR = ['SPATULA_FETCH', 'STIR_CYCLE_dice']

# ---------------- the 9 executable demo routines (build_day/cook_api.py ROUTINES) ----------------
t('mise_en_place', '备料', 'Mise en place', 'prep',
  'Everything before the heat goes on: cold box out, tomatoes cut, seasonings dosed into cups, pour drum loaded.',
  [P('tomatoes', 'count', '0–2'), P('cups', 'list of {what, grams}', '≤ 6'), P('drum', 'list of {what, grams}', '≤ 4, release order')],
  ['fridge_fetch', 'prep_tomato × n', 'dose_cup × n', 'load_drum'], 'all listed steps done', ['scale (station)'],
  ['new (fridge box transfer)', 'CUP_FETCH', 'DRUM_LOAD'], 'fridge cold box, lever cutter, seasoning station, pour drum',
  'demo', 'In the demo only tomato is cut by the robot; eggs come pre-beaten. Other ingredients need the prep_* types below.')
t('heat_to', '烧到油温', 'Heat to temperature', 'wok',
  'Heat the wok (with oil or food) at a power level until the thermometer reads the target (油温 N 成热).',
  [LV, P('target_C', '°C', '120 (4成) · 150 (5成) · 180 (6成) · 210 (7–8成)')],
  ['set_heat(level)', 'wait 3 s steps'], 'thermometer ≥ target_C, or 120 s, or > 200 °C', ['IR thermometer', 'clock'],
  [], 'induction + knob servo', 'demo', 'No arm motion.')
t('add_off_heat', '离火下料', 'Add off heat', 'wok',
  'Heat off (plume rule), arm pours a cup / bowl into the wok, heat back to level.',
  [P('source', 'cup id | egg | tomato | holding_bowl', '—'), LV], ['set_heat(0)', 'pour_into_wok(source)', 'set_heat(level)'],
  'pour done', ['clock'], CUPSETS, 'UR5e + PGC, robot cups', 'demo')
t('fry_still', '静煎', 'Fry undisturbed', 'wok', 'Leave the food to fry without stirring (煎 / 定型).',
  [SEC('3–120')], ['wait(seconds)'], 'clock (heat must be ≤ 0.5)', ['clock'], [], 'induction', 'demo')
t('flip_and_fry', '翻面再煎', 'Flip and fry', 'wok', 'Turn the piece over with the spatula, fry the other side.',
  [SEC('0–120')], ['flip_egg', 'wait(seconds)'], 'clock', ['clock'], ['SPATULA_FETCH', 'new (flip stroke)'],
  'UR5e + spatula', 'demo', 'Flipping a single piece is not simulated (uses the scrape stroke).')
t('stir_fry', '翻炒', 'Stir-fry', 'wok', 'Set the heat and stir with the spatula for a time.',
  [LV, SEC('3.6–90')], ['set_heat(level)', 'stir(seconds)'], 'clock', ['clock'], STIR, 'UR5e + keyed spatula', 'demo')
t('drum_add_stir', '鼓仓加料翻炒', 'Drum add + stir', 'wok',
  'Release the next drum compartment (liquid / sauce / oil from the edge) and stir straight after it, no pause.',
  [P('what', 'compartment content', 'water, ketchup, soy, vinegar, wine, finishing oil, sauce'), P('grams', 'g', '2–60'), SEC('3.6–90')],
  ['drum_release(stir_seconds)'], 'clock', ['clock'], STIR + ['servo drum (no arm)'], 'pour drum + spatula', 'demo',
  'Covers 锅边淋 soy / vinegar / wine, 明油, dissolved seasoning water. Ingredients other than the model\'s are not simulated.')
t('take_out', '出锅', 'Take out', 'plating', 'Heat off and tip the whole wok into the plate (serve + rinse), the holding bowl, or the oil cup.',
  [P('into', 'enum', 'plate | holding_bowl | oil_cup')], ['set_heat(0)', 'tip_wok(into)'], 'tip done', ['clock'],
  ['FAUCET_OPEN', 'WOK_PLATE_RINSE', 'FAUCET_CLOSE', 'WOK_OIL_POUR (oil_cup, not verified)'],
  'keyed wok grip, faucet lever block', 'demo', 'Plate tip ≤ 1150 g food (PGC 6.47 of 7 N·m). holding_bowl / oil_cup return path not re-run.')
t('return_and_toss', '回锅翻匀', 'Return and toss', 'wok', 'Heat off, pour the holding bowl back, heat on and stir.',
  [LV, SEC('3.6–60')], ['set_heat(0)', 'pour_into_wok(holding_bowl)', 'set_heat(level)', 'stir(seconds)'], 'clock', ['clock'],
  ['new (holding-bowl pour)', 'STIR_CYCLE_dice'], 'holding bowl', 'demo')

t('season_and_toss', '调味翻匀', 'Season and toss', 'wok',
  'Heat off, pour the seasoning cups in (salt, sugar, ...), heat on and stir so they dissolve evenly.',
  [P('cups', 'cup ids', '1–6'), LV, SEC('3.6–60')], ['set_heat(0)', 'pour_into_wok(cup) × n', 'set_heat(level)', 'stir(seconds)'],
  'clock', ['clock'], CUPSETS + STIR, 'seasoning cups', 'demo',
  'Added to the demo after run05 (run05 poured salt and sugar as two add_off_heat calls).')

# ---------------- wok composites ----------------
t('wok_grease', '润锅/滑锅', 'Season the wok (热锅冷油)', 'wok',
  'Heat the empty wok, add oil, heat it, pour the hot oil out, add fresh cold oil (热锅冷油, non-stick film).',
  [P('oil_g', 'g', '30–60'), P('pour_out', 'bool', 'true (false = oil stays)'), P('target_C', '°C', '150–200'), P('fresh_oil_g', 'g', '10–30')],
  ['add_off_heat(cup oil, 1.0)', 'heat_to(1.0, target_C)', 'take_out(oil_cup)', 'add_off_heat(cup fresh oil)'],
  'thermometer ≥ target_C (or 120 s)', ['IR thermometer', 'clock'], CUPSETS + ['WOK_OIL_POUR'], 'oil cup', 'demo_ready',
  'Exactly what run05 did (pour cup1 → heat_to 150 → take_out oil_cup → add cup2). His 晃锅 (swirl) is replaced by the tip to the oil cup, which wets the wall.')
t('egg_set_and_hold', '滑蛋盛出', 'Set eggs and hold', 'wok',
  'Pour beaten egg into oil at temperature, fry still until the underside sets, flip, fry, tip into the holding bowl.',
  [P('target_C', '°C', '120–150'), LV, P('still_s', 's', '20–60'), P('flip_s', 's', '0–30')],
  ['heat_to(level, target_C)', 'add_off_heat(egg, level)', 'fry_still(still_s)', 'flip_and_fry(flip_s)', 'take_out(holding_bowl)'],
  'clock (camera rule optional: no liquid sheen on top)', ['IR thermometer', 'clock', 'camera (optional)'],
  CUPSETS + ['new (flip)', 'new (tip to holding bowl)'], 'holding bowl', 'demo_ready', 'The demo did these 5 calls one by one; as one routine there is no gap between pour and still-fry.')
t('add_stir_fry', '下料翻炒', 'Add and stir-fry', 'wok',
  'Add an ingredient off heat, then stir at a level for a time (炒 / 炒至断生 / 炒匀).',
  [P('what', 'ingredient', '—'), LV, SEC('3–300'), P('stroke', 'enum', 'dice | shreds_leafy')],
  ['add_off_heat(cup, level)', 'stir_fry(level, seconds)'], 'clock; optional camera rule (colour change / wilt area)', ['clock', 'camera (optional)'],
  CUPSETS + STIR + ['STIR_CYCLE_shreds_leafy (shreds / leafy)'], 'spatula', 'demo_ready',
  'Runs in the demo with tomato (add_off_heat + stir_fry). Other ingredients: same calls, not in the wok model; shreds / leafy need the unverified stroke set.')
t('bloom_aromatics', '爆香', 'Bloom aromatics', 'wok',
  'Oil at temperature, aromatics (姜蒜葱 / 干辣椒 / 花椒) in, short stir until fragrant, then the next ingredient goes in at once.',
  [P('what', 'aromatics', '姜蒜葱, 干辣椒, 花椒, 泡椒'), P('target_C', '°C', '150–180'), LV, SEC('10–40')],
  ['heat_to(level, target_C)', 'add_off_heat(aromatics cup, level)', 'stir_fry(level, seconds)'],
  'clock 10–30 s; abort early if thermometer > 200 °C (smell has no sensor: time + temperature proxy)', ['IR thermometer', 'clock'],
  CUPSETS + STIR, 'spatula', 'needs_check', 'Aromatics are not in the wok model; CUP_POUR_wok not verified, stir set partially verified.')
t('fry_paste_red_oil', '炒出红油', 'Fry paste to red oil', 'wok',
  'Paste (豆瓣 / 火锅底料 / 甜面酱) into low-heat oil, often with the wok off heat first, stir until the oil turns red.',
  [P('what', 'paste', '豆瓣, 豆豉, 火锅底料, 甜面酱'), P('grams', 'g', '3–30'), LV, SEC('10–60'), P('off_heat_first', 'bool', '—')],
  ['set_heat(0) (if off_heat_first)', 'add_off_heat(paste cup, level)', 'stir_fry(level, seconds)'],
  'camera rule: oil hue red (a* threshold) or clock; cap thermometer ≤ 140 °C', ['camera', 'IR thermometer', 'clock'],
  CUPSETS + STIR, 'spatula', 'needs_check', 'Paste from a cup: sticky; scraping the cup is not designed.')
t('render_fat', '煸', 'Render / dry-fry meat', 'wok',
  'Meat (五花 / 肉末 / 腊肉) in a little oil, medium-low, stirred until the fat runs and it curls or crisps.',
  [P('what', 'meat', '五花片/粒, 肉末, 牛肉粒'), LV, SEC('20–120')],
  ['add_off_heat(meat cup, level)', 'stir_fry(level, seconds)'], 'clock; camera: pieces curl / colour (golden)', ['clock', 'camera'],
  CUPSETS + STIR, 'spatula', 'needs_check')
t('dry_stir', '干煸', 'Dry-stir until wrinkled/dry', 'wok',
  'Long low-medium stir until surface water is gone (酸菜) or skins wrinkle (四季豆); pour excess oil off mid-way.',
  [P('what', 'veg', '四季豆, 酸菜'), LV, SEC('60–200')],
  ['add_off_heat(cup, level)', 'stir_fry(level, seconds)', '(pour_off_excess_oil)'],
  'clock; thermometer rise (> 120 °C = water gone); camera wrinkle texture', ['clock', 'IR thermometer', 'camera'],
  CUPSETS + STIR, 'spatula', 'needs_check')
t('slide_oil_meat', '滑油/滑炒', 'Slide-cook marinated meat', 'wok',
  'Marinated meat into warm oil (120 °C), do not move until the bottom sets, break apart with gentle strokes until colour changes, optionally take out.',
  [P('target_C', '°C', '100–150'), LV, P('set_s', 's', '5–15'), P('separate_s', 's', '15–40'), P('take_out', 'bool', '—')],
  ['heat_to(level, target_C)', 'add_off_heat(meat cup, level)', 'fry_still(set_s)', 'stir_fry(level, separate_s) (gentle strokes)', 'take_out(holding_bowl) (optional)'],
  'clock; camera: no pink area', ['IR thermometer', 'clock', 'camera'],
  CUPSETS + ['STIR_CYCLE_shreds_leafy', 'new (gentle separate stroke)'], 'spatula', 'needs_check',
  'Shreds need the unverified shreds stroke. Batter-coated pieces for deep-frying use deep_fry instead.')
t('caramelize_sugar', '炒糖色', 'Caramelize sugar', 'sauce',
  'Rock sugar with a little oil/water on low heat until amber, then boiling water or the meat goes in at once.',
  [P('sugar_g', 'g', '15–30'), LV, P('max_s', 's', '60–180'), P('then', 'enum', 'water | meat')],
  ['add_off_heat(sugar cup, 0.3)', 'stir_fry(0.3, until rule)', 'drum_add_stir(boiling water) or add_off_heat(meat)'],
  'camera: amber hue reached, or thermometer ≥ 165 °C, or max_s', ['camera', 'IR thermometer', 'clock'],
  CUPSETS + STIR, 'spatula, drum', 'needs_check', 'Timing-critical (burns in seconds): this is the case routines are for. Caramel is not in the wok model.')
t('thicken', '勾芡/收汁(碗汁)', 'Thicken with starch', 'sauce',
  'Release starch water or a starch-containing bowl sauce (碗汁/料汁) from the drum and stir until the sauce coats.',
  [P('sauce', 'what', 'starch_water | 碗汁 | 茄汁 | 料汁'), P('grams', 'g', '15–80'), LV, P('max_s', 's', '10–30')],
  ['set_heat(level)', 'drum_release(stir_seconds = until rule)'], 'camera gloss rule (specular area on sauce > threshold, no free liquid at the wok bottom) or max_s',
  ['camera', 'clock'], STIR + ['servo drum (no arm)'], 'pour drum', 'demo_ready',
  'The brief\'s example: the LLM pause between release and stir made the sauce lumpy. starch_water is in the wok model; the gloss rule is not in the camera model yet (time cap only).')
t('thicken_multi_off_heat', '少量多次勾芡', 'Thicken in passes off heat', 'sauce',
  'Heat off, starch water to the centre, gentle push strokes, heat back to low; repeat 2–4 times (麻婆豆腐 / 脑花豆腐).',
  [P('passes', 'count', '2–4'), P('grams_each', 'g', '10–20'), LV, P('interval_s', 's', '30–60')],
  ['repeat: set_heat(0), drum_release, stir(push strokes), set_heat(level), wait(interval_s)'],
  'passes done; camera gloss rule on the last pass', ['camera', 'clock'], STIR + ['new (push stroke for soft tofu)'],
  'pour drum (all 4 compartments)', 'needs_check', 'Soft tofu needs a push stroke, not the scrape stroke.')
t('simmer_open', '煮/烧(敞口)', 'Simmer uncovered', 'wok',
  'Liquid in (drum / WOK_FILL), bring to the boil, hold at a level for a time; optional skim and basting.',
  [P('liquid', 'what', 'water, stock, cola, beer, 糖色'), P('grams', 'g', '60–1000'), P('boil_level', '0–1', '1.0'), LV, SEC('60–1800'), P('skim', 'bool', '—')],
  ['drum_add_stir(liquid) or wok_fill_water', 'heat_to(1.0, 98)', 'set_heat(level)', 'wait(seconds)'],
  'clock after the thermometer reads ≥ 98 °C; boil-dry guard: > 110 °C stops', ['IR thermometer', 'clock'],
  ['servo drum (no arm)', 'WOK_FILL (large volumes)'], 'pour drum', 'demo_ready',
  'Water is in the wok model (run05 simmered 50 s). Skimming (撇浮沫) has no tool: skipped or spider (SPIDER_SCOOP_wok, not verified). > 1 L needs WOK_FILL.')
t('braise_lid', '焖(盖盖)', 'Braise with lid', 'wok',
  'Liquid in, boil, lid on, hold at a level for a time (30 s 焖 on high up to 60 min braise), lid off.',
  [P('liquid_g', 'g', '0–1000'), LV, SEC('30–3600')],
  ['drum_add_stir(water) or wok_fill_water', 'heat_to(1.0, 98)', 'set_heat(level)', 'lid on', 'wait(seconds)', 'lid off'],
  'clock; boil-dry guard on the thermometer', ['IR thermometer', 'clock'], ['LID_ON_wok', 'LID_OFF_wok'],
  'wok lid + lid rack', 'needs_check', 'Wok lid sets are not verified (meal A 西兰花, meal B 红烧肉 / 番茄炒蛋 need them).')
t('reduce_sauce', '收汁(无芡)', 'Reduce sauce', 'sauce',
  'Uncovered, medium-high, stir now and then until the liquid is thick and glossy (no starch).',
  [LV, P('max_s', 's', '30–600'), P('stir_every_s', 's', '20–60')],
  ['set_heat(level)', 'repeat: wait, stir(4 s)'], 'thermometer of the bottom rises above ~105 °C (water gone) or camera gloss, or max_s',
  ['IR thermometer', 'camera', 'clock'], STIR, 'spatula', 'needs_check')
t('sear_skin_dry', '烙皮', 'Sear pork skin', 'wok',
  'Dry wok very hot, slab of pork skin-down, sear until the skin is golden and blistered, lift it out.',
  [P('what', 'slab', '五花 / 后腿 500–600 g'), LV, SEC('60–240')],
  ['heat_to(1.0, 220)', 'place slab skin-down (gripper)', 'fry_still(seconds)', 'lift slab to the sink tray'],
  'camera: skin colour; clock', ['IR thermometer', 'camera', 'clock'], ['new (place / lift slab)'],
  'gripper finger set for raw meat', 'needs_check', 'He moves the slab around to sear evenly; one arm can do it but the grip on a hot slab is not designed.')
t('poach_slices', '滑片', 'Poach slices in soup', 'wok',
  'Heat off, coated slices in one by one, low heat ~15 s, gentle push, lift into the serving bowl with the spider.',
  [P('what', 'slices', '鱼片, 肉片'), LV, SEC('15–90')],
  ['set_heat(0)', 'add_off_heat(slice cup, level)', 'wait(seconds)', 'spider scoop wok → serving bowl'],
  'clock; camera: slices opaque', ['clock', 'camera'], CUPSETS + ['SPIDER_FETCH', 'SPIDER_SCOOP_wok', 'SPIDER_DUMP_plate', 'SPIDER_STOW'],
  'spider strainer', 'needs_check', 'SPIDER_SCOOP_wok not verified (only the pot scoop is).')
t('fish_out_item', '捞出(单件/料头)', 'Fish out an item', 'wok',
  'Lift a named item (葱段, 姜, bones + 酸菜, a piece) out of the liquid with the spider.',
  [P('what', 'item', '—'), P('into', 'enum', 'discard | serving_bowl | holding_bowl')],
  ['SPIDER fetch', 'scoop wok', 'dump', 'stow'], 'scoop done', ['camera (locate)'],
  ['SPIDER_FETCH', 'SPIDER_SCOOP_wok', 'SPIDER_DUMP_plate', 'SPIDER_STOW'], 'spider strainer', 'needs_check')
t('pour_off_excess_oil', '倒出多余油', 'Pour off excess oil, keep food', 'wok',
  'Tip the wok so the excess oil runs out while the food stays in.',
  [P('keep_oil_g', 'g', '10–30')], ['(he holds the food back with the ladle while tipping)'], 'oil out', ['camera'],
  ['WOK_OIL_POUR', 'new'], 'oil cup', 'two_hands',
  'One arm cannot hold the food back and tip at once. Workaround: spider the food into the holding bowl, take_out(oil_cup), add back (3 sets, +~40 s); or use less oil so no pour-off is needed.')
t('ladle_baste', '舀汤浇', 'Baste with a ladle', 'wok', 'Ladle sauce over a whole fish / piece without turning it.',
  [P('times', 'count', '3–6'), SEC('60–360')], ['fetch ladle', 'repeat: scoop sauce, pour over', 'stow ladle'], 'clock',
  ['clock'], ['new'], 'ladle (not designed)', 'needs_hardware', 'Workaround: lid on (braise_lid) instead of basting.')
t('hot_oil_pour_over', '泼油/浇热油', 'Pour hot oil over', 'sauce',
  'Heat oil in the wok to 180–240 °C, heat off, tip the wok so the oil runs over the food / aromatics in a bowl or plate.',
  [P('oil_g', 'g', '20–80'), P('target_C', '°C', '180–240'), P('onto', 'enum', 'plate | bowl')],
  ['add_off_heat(cup oil, 1.0)', 'heat_to(1.0, target_C)', 'set_heat(0)', 'tip wok over the bowl/plate', 'wok back'],
  'thermometer ≥ target_C', ['IR thermometer'], CUPSETS + ['WOK_OIL_POUR'], 'keyed wok grip', 'needs_check',
  'R17: a 6–8 cm bowl at the plating spot was hit by the forearm during the wok pick; hot-oil pour not verified.')
t('deep_fry', '炸/复炸', 'Deep-fry (and re-fry)', 'fry',
  'Oil (fryer or wide oil in the wok) to temperature, food in, do not stir until set, separate, fry for a time, lift out with the spider; pass 2 = hotter, shorter.',
  [P('vessel', 'enum', 'fryer | wok'), P('target_C', '°C', '150–240'), SEC('20–360'), P('pass', 'count', '1 | 2')],
  ['heat oil (fryer thermostat or heat_to)', 'pour food from cup', 'wait(set) + gentle separate', 'wait(rest of seconds)', 'spider scoop → tray/holding bowl'],
  'clock; oil thermometer held at target; camera: golden colour', ['oil thermometer', 'clock', 'camera'],
  ['CUP_FETCH', 'CUP_POUR_fryer', 'CUP_RETURN', 'SPIDER_FETCH', 'SPIDER_SCOOP_fryer', 'SPIDER_DUMP_plate', 'SPIDER_STOW'],
  'fryer, spider', 'needs_check',
  'Use the fryer, not 750 g of oil in the wok. Pieces added one by one (逐步下入) become one pour; battering (挂糊) is prep [missing].')
t('wok_fill_water', '锅中加水(龙头)', 'Fill wok at the tap', 'wok',
  'Carry the wok to the faucet, fill ~1 L, set it back (for soups, blanching water, 煮).',
  [P('water_g', 'g', '300–1000')], ['FAUCET_OPEN', 'WOK_FILL', 'FAUCET_CLOSE'], 'fill time (flow-calibrated)', ['clock'],
  ['FAUCET_OPEN', 'WOK_FILL', 'FAUCET_CLOSE'], 'faucet lever block', 'sim_motion_checked',
  'WOK_FILL is composed from the verified wok chain (micro-joins checked in R19, 1 L load PGC 5.88 N·m). Flow volume not calibrated; > 1 L not checked.')
t('wash_wok', '洗锅', 'Rinse the wok', 'cleanup', 'Wok to the sink, rinse under the running tap, dump, back on the cooker.',
  [], ['set_heat(0)', 'FAUCET_OPEN', 'WOK_DUMP_RINSE', 'FAUCET_CLOSE'], 'sequence done', ['clock'],
  ['FAUCET_OPEN', 'WOK_DUMP_RINSE', 'FAUCET_CLOSE'], 'faucet lever block', 'sim_motion_checked',
  'Composed from verified sets. Rinse only (no scrubbing). The spatula rest ↔ faucet transits are not verified (R19 §1).')

# ---------------- pot / steam / stew ----------------
t('blanch_lift', '焯水/煮后捞出', 'Blanch or boil, then lift out', 'pot_steam',
  'Pot (zone 2) or wok water to the boil (or cold start for meat), food in, time, optional skim, lift out with the spider (optional cold-water dip).',
  [P('vessel', 'enum', 'pot | wok'), P('start', 'enum', 'boiling | cold'), P('additive', 'what', 'salt, oil, vinegar, 料酒'), SEC('10–3600'), P('chill', 'bool', '—')],
  ['(water already in the pot / wok_fill_water)', 'heat_to(1.0, 98)', 'pour food cup into the pot', 'wait(seconds)', 'SPIDER_FETCH', 'SPIDER_SCOOP_pot', 'SPIDER_DUMP_plate (or holding bowl)', 'SPIDER_STOW'],
  'clock after boil (thermometer ≥ 98 °C)', ['IR thermometer', 'clock'],
  ['new (cup pour into the pot)', 'SPIDER_FETCH', 'SPIDER_SCOOP_pot', 'SPIDER_DUMP_plate', 'SPIDER_STOW'],
  'zone-2 pot, spider', 'needs_check',
  'The spider chain from the pot is verified; pouring food into the pot and filling the pot are not designed. Skimming foam: no tool.')
t('steam_plate', '蒸', 'Steam a plate', 'pot_steam',
  'Plate on the dish carrier into the steaming pot, lid on, steam for a time from full steam, lid off, carrier out.',
  [P('seconds', 's', '180–10800'), P('level', '0–1', '0.5–1.0')],
  ['heat_to(1.0, 98) (pot)', 'CARRIER_IN', 'LID_ON_pot', 'wait(seconds)', 'LID_OFF_pot', 'CARRIER_OUT'],
  'clock from boil (pot water thermometer ≥ 98 °C)', ['thermometer (pot)', 'clock'],
  ['CARRIER_IN', 'LID_ON_pot', 'LID_OFF_pot', 'CARRIER_OUT'], 'zone-2 pot + steaming rack + lid rack + dish carrier', 'sim_motion_checked',
  'All four sets verified. Loading the food onto the dish is arrange_on_plate (not verified); pot water filled by the user.')
t('stew_pot', '炖/煲汤', 'Stew pot soup', 'stew',
  'Ingredients and water into the electric stew pot, lid on, program for a time, lid off, season.',
  [SEC('1800–7200'), P('water_g', 'g', '1000–2000')], ['CUP_POUR_stew × n', 'water in', 'LID_ON_stew', 'wait', 'LID_OFF_stew', 'CUP_POUR_stew (salt)'],
  'clock (pot program)', ['clock'], ['CUP_FETCH', 'CUP_POUR_stew', 'CUP_RETURN', 'LID_ON_stew', 'LID_OFF_stew'], 'electric stew pot', 'needs_check',
  'Water fill of the stew pot has no set.')
t('steam_cups', '炖盅蒸', 'Steam stew cups', 'pot_steam',
  'Fill 4 炖盅 (pieces + water to 90 %), cover with cling film, steam 30 min, take out.',
  [P('cups', 'count', '4'), SEC('1800')], ['STEW_CUP_IN × 4', 'LID_ON_pot', 'wait', 'LID_OFF_pot', 'STEW_CUP_OUT × 4'],
  'clock', ['clock'], ['STEW_CUP_IN', 'STEW_CUP_OUT', 'LID_ON_pot', 'LID_OFF_pot'], 'stew cups', 'two_hands',
  'Cling film needs two hands. Workaround: cups with ceramic lids; then needs_check (STEW_CUP_IN not verified).')
t('steep_off_heat', '浸熟(白切)', 'Steep off heat', 'pot_steam',
  'Salted water to the boil, heat off, dip the whole chicken 3× to fill the cavity, then steep 30–40 min, hook out into cold water.',
  [SEC('1800–2400')], ['heat_to(1.0, 98)', 'set_heat(0)', 'dip × 3', 'wait', 'hook out', 'cold_water_chill'], 'clock',
  ['clock'], ['new'], 'whole-bird basket or hook (not designed)', 'needs_hardware', 'Workaround: chicken in a wire basket that the arm lowers and lifts.')
t('cold_water_chill', '过凉', 'Chill in cold water', 'pot_steam',
  'Move cooked food into a bowl of cold water, then drain.', [SEC('30–600')], ['spider dump into the cold-water bowl', 'wait', 'drain'],
  'clock', ['clock'], ['SPIDER_DUMP_plate (to a bowl, new target)', 'new (drain)'], 'cold-water bowl + basket', 'needs_hardware',
  'Soak / drain has no design (R19_PREP_AUDIT [missing]).')
t('serve_soup', '盛汤', 'Serve soup', 'plating',
  'Soup into the serving bowl: tip the wok if ≤ 1150 g, otherwise ladle; optional salt pre-dosed in the bowl.',
  [P('mass_g', 'g', '500–2500'), P('season_in_bowl', 'what', '盐, 芹菜, 白胡椒')], ['set_heat(0)', 'tip_wok(serving bowl) or ladle × n'],
  'done', ['clock'], ['WOK_PLATE_RINSE (tip variant)', 'new (ladle)'], 'serving bowl spot; ladle (not designed)', 'needs_hardware',
  'Tipping into a bowl is not simulated; soups over 1.15 kg exceed the checked wok payload.')
t('rice_cooker', '煮饭', 'Cook rice', 'other', 'Dose rice, wash, into the cooker, water, start.', [P('rice_g', 'g', '200–400')],
  ['RICE_DOSE', 'RICE_WASH', 'RICE_TO_COOKER', 'press start'], 'cooker finishes', ['cooker signal'],
  ['RICE_DOSE', 'RICE_WASH', 'RICE_TO_COOKER'], 'rice cooker', 'needs_check', 'R19_PREP_AUDIT: the user loads the rice cooker (outlet obsolete).')

# ---------------- sauce / cold / plating ----------------
t('cold_mix_bowl', '拌', 'Mix in a bowl', 'sauce', 'Dose sauce items into a bowl and stir; or toss food with sauce in a bowl.',
  [P('items', 'list', '酱油, 醋, 红油, 香油 …')], ['dose_cup × n into the bowl', 'stir with a spoon'], 'clock', ['clock'],
  ['new'], 'bowl fixture + mixing spoon (not designed)', 'needs_hardware')
t('pour_cup_over_plate', '淋汁/撒料', 'Pour a cup over the plate', 'plating',
  'Pour a sauce cup (糖桂花, 白灼汁, 鱼酱油) or sprinkle a garnish cup (葱花, 花生碎) over the plated food.',
  [P('what', 'cup', '—')], ['CUP_FETCH', 'CUP_POUR_plate', 'CUP_RETURN'], 'pour done', ['clock'],
  ['CUP_FETCH', 'CUP_POUR_plate', 'CUP_RETURN'], 'robot cups', 'needs_check')
t('arrange_on_plate', '摆盘', 'Arrange on a plate', 'plating', 'Place pieces on a plate (steaming bed, fish with ginger, re-plating).',
  [P('pieces', 'count', '1–20')], ['ARRANGE'], 'done', ['camera'], ['ARRANGE'], 'plate dock', 'needs_check')
t('drain_plate_juice', '倒掉盘中汤水', 'Drain the plate juices', 'plating', 'Tip the steamed plate to pour off the fishy water.',
  [], ['CARRIER_DRAIN'], 'done', ['clock'], ['CARRIER_DRAIN'], 'dish carrier', 'needs_check')
t('bowl_pack_invert', '码碗扣盘', 'Pack bowl and invert', 'plating', 'Pack florets head-down in a bowl, invert onto a plate, lift the bowl.',
  [], ['place florets', 'plate on bowl', 'invert both'], 'done', ['camera'], ['new'], '—', 'two_hands',
  'Inverting bowl + plate together needs two hands. Workaround: arrange on the plate directly (arrange_on_plate), no dome.')
t('reboil_plate_juices', '回锅过滤盘汁', 'Re-boil and strain plate juices', 'sauce',
  'Pick the shreds off the fish, pour the plate juices into the wok, re-boil, strain, pour back.', [],
  ['chopsticks lift shreds', 'pour plate into wok', 'boil', 'strain', 'pour back'], 'done', ['thermometer'], ['new'], 'strainer',
  'two_hands', 'Chopsticks + plate + strainer at once. Optional 进阶 step: skip.')
t('wok_toss', '颠锅', 'Toss the wok', 'wok', 'Lift and flick the wok to toss.', [SEC('3–30')], ['lift wok', 'flick', 'set back'],
  'clock', ['clock'], ['new'], 'keyed wok grip', 'needs_check', 'Not used in the mappings: every 颠锅 is replaced by stir_fry strokes (also what the homestyle cook does).')

# ---------------- prep (from R19_PREP_AUDIT) ----------------
t('prep_wash', '清洗', 'Wash produce', 'prep', 'Hold a firm item under the tap, or a basket of small / leafy items.',
  [P('what', 'item', '—'), P('mode', 'enum', 'held | basket')], ['FAUCET_OPEN', 'hold / basket under the tap', 'FAUCET_CLOSE'],
  'clock', ['clock'], ['FAUCET_OPEN', 'new (wash under R17 outlet)', 'FAUCET_CLOSE'], 'basket, spinner', 'needs_check',
  'R19_PREP_AUDIT: washing chains were checked under the removed R07 spout; must be re-planned under the faucet.')
t('prep_cut', '切配(楔/段/片/丝)', 'Cut with lever cutter / slicer', 'prep',
  'Wedges / sections on the lever cutter; slices / shreds / dice in the 卓晋 slicer.',
  [P('what', 'item', '—'), P('cut', 'enum', 'wedge | section | slice | shred | dice')], ['pick item', 'lever cutter or slicer chute', 'out bowl'],
  'done', ['clock'], ['new (prep chains; tomato WD checked in R11)'], 'lever cutter, slicer', 'needs_check',
  'Tomato wedges are the demo prep_tomato. Slicer stands in the plating area (static overlap 77 mm) until moved.')
t('prep_peel', '去皮', 'Peel', 'prep', 'Roots in the abrasive peeler; tomato skin by scalding.', [P('what', 'item', 'potato, taro, carrot, luffa')],
  ['peeler station'], 'clock', ['clock'], ['new'], 'abrasive peeler', 'needs_check', 'Luffa, bamboo, broccoli stem peeling: [missing].')
t('prep_mince_meat_cut', '剁末/切肉', 'Mince / slice meat', 'prep', 'Garlic / ginger mince, meat slices and shreds, cooked meat cubes, squid scoring.',
  [P('what', 'item', '—')], ['—'], '—', [], ['new'], 'chopper cup / meat slicer (not designed)', 'needs_hardware', 'R19_PREP_AUDIT [missing]. Practical route: buy pre-cut.')
t('prep_egg_beat', '打蛋', 'Crack and beat eggs', 'prep', 'Crack eggs into a cup and beat.', [P('eggs', 'count', '2–5')],
  ['—'], '—', [], ['new'], '—', 'two_hands', 'One gripper cannot crack an egg. Workaround (the demo): the user cracks and beats them, cup in the cold box.')
t('prep_marinate', '腌制/上浆', 'Marinate / coat', 'prep', 'Mix meat with seasoning and starch, rest.', [P('minutes', 'min', '10–30')],
  ['dose_cup × n into the meat bowl', 'mix'], 'clock', ['clock'], ['new'], 'mixing bowl + paddle (not designed)', 'needs_hardware', 'R19_PREP_AUDIT [missing].')
t('soak_bowl', '浸泡', 'Soak in a bowl', 'prep', 'Soak food in hot / warm / salted water for a time, then drain (tofu, noodles, mushrooms).',
  [P('water_C', '°C', '20–95'), SEC('300–2400')], ['food into bowl', 'hot water from kettle', 'wait', 'drain'], 'clock', ['clock'],
  ['new (kettle pour, drain)'], 'kettle, soak basket (not designed)', 'needs_hardware', 'R19_PREP_AUDIT: soak and scald [missing]; kettle grasp unchecked.')
t('portion_into_cups', '分装炖盅', 'Portion into cups', 'prep', 'Put counted pieces (ribs, clams, ginger) into each stew cup with water.',
  [P('pieces', 'count', '8 per cup')], ['ARRANGE × n'], 'done', ['camera'], ['ARRANGE', 'new'], '—', 'needs_check')
t('grind_spice', '研磨', 'Grind spices', 'prep', 'Grind the roasted 椒盐 to powder.', [], ['—'], '—', [], ['new'], 'spice grinder (not designed)',
  'needs_hardware', 'Workaround: buy ground 椒盐.')
