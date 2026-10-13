# Per-dish routine sequences. Each call: (phase, routine, params, covered, why_not). phase -1 = before phase 0 (prep).
M = {}
HOME = {}


def c(ph, r, **p):
    return (ph, r, p, True, '')


def x(ph, r, why, **p):
    return (ph, r, p, False, why)


# ===== 1. 西红柿炒蛋 — in full detail, in demo routines (matches build_day runs/run05, which executed it) =====
M['xihongshichaodan'] = [
    c(-1, 'mise_en_place', tomatoes=2,
      cups=[dict(what='oil', grams=40), dict(what='oil', grams=25), dict(what='salt', grams=1), dict(what='sugar', grams=1)],
      drum=[dict(what='ketchup', grams=5), dict(what='water', grams=60), dict(what='starch_water', grams=25), dict(what='finishing_oil', grams=5)],
      note='eggs: 3 beaten by the user (cup in the cold box); tomatoes cut into 8 wedges each'),
    # Same granularity as the other dishes (plan-level routines). run05 executed the finer 21-call version,
    # because the demo then had only 9 routines (no wok_grease / egg_set_and_hold / season_and_toss).
    # phase 0 预热/润锅 (heat the wok, oil it, pour the oil out, fresh oil)
    c(0, 'wok_grease', oil_g=40, pour_out=True, target_C=150, fresh_oil_g=25),
    # phase 1 煎 eggs: oil to 120 °C, egg in, low heat until set, flip, out (returned at the end)
    c(1, 'egg_set_and_hold', target_C=120, level=0.3, still_s=50, flip_s=30),
    # phase 2 炒 tomato + ketchup on low heat
    c(2, 'add_stir_fry', what='tomato', level=0.3, seconds=45, stroke='dice'),
    c(2, 'drum_add_stir', what='ketchup', grams=5, seconds=20),
    # phase 3 煮/焖: water, salt + sugar, simmer 1 min
    c(3, 'drum_add_stir', what='water', grams=60, seconds=15),
    c(3, 'season_and_toss', cups=['salt 1 g', 'sugar 1 g'], level=0.5, seconds=50),
    # phase 4 勾芡 + 明油
    c(4, 'thicken', sauce='starch_water', grams=25, level=0.5, max_s=20),
    c(4, 'drum_add_stir', what='finishing_oil', grams=5, seconds=4),
    # phase 5 eggs back, mix a few times, plate
    c(5, 'return_and_toss', level=0.5, seconds=8),
    c(5, 'take_out', into='plate'),
]

# ===== 2. other egg / tomato dishes =====
M['jiucaichaodan'] = [
    c(-1, 'mise_en_place', cups=[dict(what='oil', grams=40), dict(what='oil', grams=25), dict(what='韭菜 chopped', grams=150)],
      drum=[dict(what='salt water', grams=5)], note='eggs beaten by the user (prep_egg_beat is two_hands)'),
    c(0, 'wok_grease', oil_g=40, pour_out=True, target_C=180, fresh_oil_g=25),
    c(1, 'add_stir_fry', what='韭菜', level=0.7, seconds=20, stroke='shreds_leafy'),
    c(2, 'add_off_heat', source='egg (poured over the chives)', level=0.3),
    c(2, 'fry_still', seconds=60),
    c(3, 'stir_fry', level=0.5, seconds=20, note='break the patty up, 锅气'),
    c(3, 'take_out', into='plate'),
]
M['danchaofan'] = [
    x(-1, 'prep_egg_beat', 'separating whites and yolks: one gripper cannot; user separates them (as the demo eggs)', eggs=3),
    c(-1, 'mise_en_place', cups=[dict(what='oil', grams=40), dict(what='oil', grams=20), dict(what='egg white', grams=90),
                                 dict(what='egg yolk + oil', grams=60), dict(what='bacon/sausage/corn', grams=120), dict(what='cooked rice', grams=400)],
      drum=[dict(what='soy sauce', grams=3), dict(what='scallion', grams=10)]),
    c(0, 'wok_grease', oil_g=40, pour_out=True, target_C=180, fresh_oil_g=20),
    c(1, 'add_stir_fry', what='egg white', level=0.5, seconds=30),
    c(1, 'take_out', into='holding_bowl'),
    c(2, 'add_stir_fry', what='egg yolk + a little oil', level=0.3, seconds=20),
    c(3, 'add_stir_fry', what='bacon, sausage, corn', level=0.4, seconds=30),
    c(4, 'return_and_toss', level=0.4, seconds=10, note='颠锅 → scrape strokes'),
    c(5, 'add_stir_fry', what='rice', level=0.2, seconds=300, note='颠锅 → scrape strokes; 5 min very low'),
    c(6, 'drum_add_stir', what='soy sauce (from the edge)', grams=3, seconds=4, level=1.0),
    c(6, 'drum_add_stir', what='scallion', grams=10, seconds=4),
    c(6, 'take_out', into='plate'),
]
M['qiezhilizhi'] = [
    x(-1, 'prep_marinate', 'battering the pork (挂糊) has no design (R19_PREP_AUDIT [missing])', what='里脊 in batter'),
    c(0, 'deep_fry', vessel='fryer', target_C=150, seconds=120, **{'pass': 1}, note='5成热, add, do not stir, 中小火; spider separates then lifts'),
    c(1, 'deep_fry', vessel='fryer', target_C=200, seconds=90, **{'pass': 2}, note='复炸 to golden, into the holding bowl'),
    c(2, 'add_off_heat', source='cup (oil 10 g)', level=0.4, note='wok is clean: frying was in the fryer'),
    c(2, 'drum_add_stir', what='茄汁 (ketchup + sugar + vinegar)', grams=40, seconds=8),
    c(2, 'simmer_open', liquid='water', grams=60, level=0.4, seconds=20),
    c(2, 'thicken', sauce='starch_water', grams=20, level=0.4, max_s=15),
    c(2, 'drum_add_stir', what='finishing_oil', grams=5, seconds=3),
    c(3, 'return_and_toss', level=0.4, seconds=10),
    c(3, 'take_out', into='plate'),
]

# ===== 3. the rest of Wang Gang's 42 =====
PL = lambda ph: c(ph, 'take_out', into='plate')
POFF = lambda ph: c(ph, 'pour_off_excess_oil', keep_oil_g=20)
M['huiguorou'] = [
    c(0, 'sear_skin_dry', what='后腿肉 500 g', level=0.7, seconds=120),
    c(1, 'blanch_lift', vessel='pot', start='cold', seconds=1800, what='pork', chill=True),
    x(1, 'prep_mince_meat_cut', 'slicing cooked pork 2 mm: no meat slicer (R19_PREP_AUDIT [missing])', what='cooked pork slices 2 mm'),
    c(2, 'wok_grease', oil_g=40, pour_out=True, target_C=180, fresh_oil_g=15),
    c(3, 'render_fat', what='pork slices', level=0.4, seconds=60),
    c(4, 'bloom_aromatics', what='豆豉', target_C=150, level=0.4, seconds=20),
    c(5, 'fry_paste_red_oil', what='豆瓣', grams=5, level=0, seconds=20, off_heat_first=True),
    c(6, 'stir_fry', level=0.4, seconds=20),
    c(7, 'drum_add_stir', what='sauce (酱油/糖/料酒)', grams=15, seconds=10),
    c(8, 'add_stir_fry', what='蒜苗', level=0.5, seconds=15, stroke='shreds_leafy'), PL(8),
]
M['yuxiangrousi'] = [
    c(0, 'wok_grease', oil_g=40, pour_out=True, target_C=180, fresh_oil_g=30),
    c(1, 'slide_oil_meat', target_C=180, level=0.6, set_s=8, separate_s=30, take_out=False, note='肉丝 + 豆瓣'),
    c(2, 'bloom_aromatics', what='姜蒜末', target_C=160, level=0.6, seconds=10),
    c(3, 'add_stir_fry', what='葱粒', level=0.6, seconds=60),
    c(4, 'thicken', sauce='碗汁 (鱼香汁 with starch)', grams=60, level=0.7, max_s=10), PL(4),
]
M['gongbaojiding'] = [
    c(0, 'deep_fry', vessel='fryer', target_C=160, seconds=60, **{'pass': 1}, note='滑油 chicken in 750 g oil → fryer'),
    c(1, 'bloom_aromatics', what='干辣椒 + 花椒', target_C=150, level=0.4, seconds=23),
    c(2, 'return_and_toss', level=0.8, seconds=15),
    c(3, 'thicken', sauce='碗汁', grams=50, level=1.0, max_s=10),
    c(4, 'drum_add_stir', what='花生 + 葱 + 红油', grams=40, seconds=3, note='peanuts in the drum (granules release 100 %, R14)'), PL(4),
]
M['mapodoufu'] = [
    c(0, 'soak_bowl', water_C=90, seconds=300, what='tofu in salted water'),
    c(1, 'wok_grease', oil_g=40, pour_out=True, target_C=180, fresh_oil_g=30),
    c(2, 'render_fat', what='牛肉粒', level=0.3, seconds=60),
    c(3, 'add_stir_fry', what='花椒', level=1.0, seconds=60),
    c(4, 'fry_paste_red_oil', what='豆瓣 + 豆豉', grams=25, level=0.3, seconds=20),
    c(5, 'bloom_aromatics', what='姜蒜葱 + 辣椒面', target_C=130, level=0.3, seconds=3),
    c(6, 'simmer_open', liquid='water + seasoning', grams=300, level=1.0, seconds=30, note='300 g > one drum compartment: wok_fill_water or 2 compartments'),
    c(7, 'add_off_heat', source='tofu (drained)', level=0.3),
    c(7, 'fry_still', seconds=120, note='tofu simmered on low; no stirring'),
    c(8, 'thicken_multi_off_heat', passes=3, grams_each=15, level=0.3, interval_s=60, note='phases 8–10 are one routine'),
    c(9, 'thicken_multi_off_heat', passes=0, note='(pass 2 of the routine above)'),
    c(10, 'thicken_multi_off_heat', passes=0, note='(pass 3 of the routine above)'),
    c(11, 'drum_add_stir', what='花椒油', grams=5, seconds=3), PL(11),
]
M['hongshaorou'] = [
    c(0, 'sear_skin_dry', what='五花 slab', level=0.7, seconds=120),
    c(1, 'caramelize_sugar', sugar_g=20, level=0.3, max_s=120, then='water'),
    c(2, 'simmer_open', liquid='boiling water', grams=150, level=1.0, seconds=60),
    c(2, 'take_out', into='holding_bowl', note='糖色 kept aside'),
    c(3, 'blanch_lift', vessel='pot', start='cold', additive='料酒 15 g', seconds=300, skim=True),
    c(4, 'wok_grease', oil_g=40, pour_out=True, target_C=180, fresh_oil_g=30),
    c(5, 'render_fat', what='五花 cubes', level=0.5, seconds=120), POFF(5),
    c(6, 'bloom_aromatics', what='葱姜 + 香料', target_C=150, level=0.3, seconds=20),
    c(7, 'drum_add_stir', what='酱油 (from the side)', grams=5, seconds=10),
    c(8, 'wok_fill_water', water_g=600, note='water to 1 cm over the pork'),
    c(8, 'add_off_heat', source='holding_bowl (糖色)', level=1.0),
    c(8, 'simmer_open', liquid='water + 糖色', grams=600, level=0.3, seconds=3600),
    c(8, 'fish_out_item', what='葱姜 + 香料', into='discard'),
    c(9, 'reduce_sauce', level=0.5, max_s=600, stir_every_s=30), PL(9),
]
M['tangcupaigu'] = [
    c(0, 'blanch_lift', vessel='pot', start='cold', additive='料酒/干辣椒/花椒', seconds=300),
    c(1, 'steam_plate', seconds=9000, level=0.5, note='ribs in a 盆 with seasoned water; broth kept'),
    c(2, 'deep_fry', vessel='fryer', target_C=190, seconds=90, **{'pass': 1}),
    c(3, 'add_off_heat', source='cup (steaming broth + 糖醋)', level=0.4),
    c(3, 'return_and_toss', level=0.4, seconds=10),
    c(3, 'reduce_sauce', level=0.3, max_s=300, stir_every_s=15, note='炸收: until the sauce is dry, never high heat'), PL(3),
]
M['qingjiaorousi'] = [
    c(0, 'wok_grease', oil_g=40, pour_out=True, target_C=180, fresh_oil_g=30),
    c(1, 'slide_oil_meat', target_C=120, level=0.4, set_s=5, separate_s=30, take_out=True),
    c(2, 'bloom_aromatics', what='姜蒜 in lard', target_C=150, level=0.4, seconds=20),
    c(3, 'add_stir_fry', what='青椒丝', level=0.5, seconds=30, stroke='shreds_leafy'),
    c(4, 'return_and_toss', level=0.5, seconds=10),
    c(4, 'drum_add_stir', what='seasoning sauce', grams=15, seconds=5),
    c(5, 'drum_add_stir', what='finishing_oil', grams=5, seconds=3), PL(5),
]
M['tudousi'] = [
    c(0, 'blanch_lift', vessel='pot', start='boiling', additive='white vinegar', seconds=20),
    c(1, 'bloom_aromatics', what='干辣椒 + 蒜片', target_C=180, level=0.6, seconds=20),
    c(2, 'add_stir_fry', what='potato shreds', level=1.0, seconds=40, stroke='shreds_leafy'),
    c(3, 'drum_add_stir', what='生抽 + 醋 (from the edge)', grams=6, seconds=5),
    c(3, 'drum_add_stir', what='scallion', grams=10, seconds=5), PL(3),
]
M['ganbiansijidou'] = [
    c(0, 'dry_stir', what='四季豆', level=0.4, seconds=183), POFF(0), c(0, 'take_out', into='holding_bowl'),
    c(1, 'render_fat', what='肉末', level=0.3, seconds=36),
    c(2, 'bloom_aromatics', what='花椒 + 干辣椒', target_C=170, level=1.0, seconds=44),
    c(3, 'add_stir_fry', what='蒜 (cools the wok)', level=1.0, seconds=3),
    c(4, 'return_and_toss', level=1.0, seconds=30),
    c(4, 'drum_add_stir', what='salt + 花椒油', grams=5, seconds=5), PL(4),
]
M['shuizhuroupian'] = [
    c(0, 'wok_grease', oil_g=40, pour_out=True, target_C=180, fresh_oil_g=40),
    c(1, 'add_stir_fry', what='干辣椒 + 花椒', level=0.3, seconds=20), c(1, 'take_out', into='holding_bowl'),
    x(1, 'prep_mince_meat_cut', 'mincing the fried chilies (刀口辣椒) on a board: no chopper', what='刀口辣椒'),
    c(2, 'bloom_aromatics', what='干辣椒 + 花椒', target_C=170, level=0.6, seconds=20),
    c(3, 'add_stir_fry', what='vegetable bed', level=1.0, seconds=20, stroke='shreds_leafy'),
    c(3, 'take_out', into='serving bowl (veg bed)', note='tip into a bowl: not simulated'),
    c(4, 'bloom_aromatics', what='姜蒜泡椒', target_C=170, level=0.6, seconds=20),
    c(5, 'fry_paste_red_oil', what='豆瓣', grams=10, level=0.3, seconds=20),
    c(6, 'simmer_open', liquid='water', grams=600, level=1.0, seconds=60),
    c(7, 'thicken', sauce='starch_water', grams=20, level=0.3, max_s=10),
    c(8, 'poach_slices', what='肉片 (上浆)', level=0.5, seconds=60),
    c(8, 'serve_soup', mass_g=600, note='some soup ladled over the pork'),
    c(9, 'pour_cup_over_plate', what='刀口辣椒 + 蒜末'),
    c(9, 'hot_oil_pour_over', oil_g=60, target_C=210, onto='bowl'),
]
M['kelejichi'] = [
    c(0, 'bloom_aromatics', what='姜片', target_C=150, level=0.5, seconds=20),
    c(1, 'add_off_heat', source='wings', level=0.3, note='he lays wings one by one on the ginger bed; here poured off heat (plume rule)'), c(1, 'fry_still', seconds=180), c(1, 'flip_and_fry', seconds=180),
    c(2, 'simmer_open', liquid='cola', grams=500, level=1.0, seconds=60, skim=True),
    c(3, 'braise_lid', liquid_g=0, level=0.3, seconds=900),
    c(3, 'fish_out_item', what='葱姜', into='discard'),
    c(4, 'reduce_sauce', level=0.5, max_s=300, stir_every_s=30), PL(4),
]
M['xilanhua'] = [
    c(0, 'blanch_lift', vessel='pot', start='boiling', additive='salt + oil', seconds=60, note='spider out to arrange'),
    c(1, 'bowl_pack_invert', note='two_hands: replaced by arrange_on_plate (no dome)'),
    c(1, 'arrange_on_plate', pieces=12, note='workaround for the dome'),
    c(2, 'hot_oil_pour_over', oil_g=40, target_C=180, onto='bowl (蒜蓉)'),
    c(2, 'pour_cup_over_plate', what='蒜蓉 oil sauce'),
    c(3, 'simmer_open', liquid='water + salt + oil + 土豆淀粉 (拉丝芡)', grams=600, level=0.3, seconds=60),
    c(3, 'blanch_lift', vessel='wok', start='boiling', seconds=60, note='florets in the thickened water'),
    c(4, 'take_out', into='oil_cup', note='pour most of the liquid out (留下少部分): a full tip loses it all; use the drum for fresh 蚝油汁 instead'),
    c(4, 'drum_add_stir', what='蚝油', grams=20, seconds=5),
    c(4, 'thicken', sauce='starch_water', grams=15, level=0.5, max_s=15),
    c(4, 'take_out', into='plate', note='sauce over the plated broccoli'),
    c(5, 'blanch_lift', vessel='pot', start='boiling', additive='salt + oil', seconds=60),
    c(6, 'bloom_aromatics', what='胡萝卜 + 红椒 + 蒜蓉', target_C=150, level=0.4, seconds=20),
    c(7, 'simmer_open', liquid='water', grams=60, level=1.0, seconds=20),
    c(7, 'thicken', sauce='starch_water', grams=15, level=0.5, max_s=10),
    c(8, 'add_stir_fry', what='broccoli (blanched)', level=0.6, seconds=10),
    c(8, 'drum_add_stir', what='finishing_oil', grams=5, seconds=3), PL(8),
]
M['disanxian'] = [
    c(0, 'blanch_lift', vessel='pot', start='boiling', seconds=300, what='potato cubes'),
    c(1, 'deep_fry', vessel='fryer', target_C=180, seconds=80, **{'pass': 1}),
    c(2, 'bloom_aromatics', what='蒜 + 葱', target_C=150, level=0.5, seconds=20),
    c(3, 'drum_add_stir', what='生抽 (from the edge)', grams=3, seconds=3),
    c(3, 'thicken', sauce='water + starch sauce', grams=60, level=0.5, max_s=10),
    c(4, 'return_and_toss', level=0.6, seconds=10), PL(4),
]
M['xiaochaorou'] = [
    c(0, 'slide_oil_meat', target_C=120, level=0, set_s=5, separate_s=30, take_out=True, note='wok off the fire for 滑油'),
    c(1, 'wash_wok'),
    c(2, 'wok_grease', oil_g=40, pour_out=True, target_C=180, fresh_oil_g=0),
    c(3, 'render_fat', what='五花', level=0.3, seconds=60),
    c(4, 'bloom_aromatics', what='姜蒜末 + 辣椒', target_C=160, level=0.6, seconds=20),
    c(4, 'return_and_toss', level=0.6, seconds=20, note='里脊 back half-way'),
    c(5, 'stir_fry', level=0.8, seconds=30),
    c(6, 'drum_add_stir', what='生抽 (from the edge)', grams=2, seconds=5),
    c(6, 'add_stir_fry', what='蒜苗叶', level=0.8, seconds=25, stroke='shreds_leafy'), PL(6),
]
M['fengweiqiezi'] = [
    c(0, 'deep_fry', vessel='fryer', target_C=180, seconds=60, **{'pass': 1}, note='small batches'),
    c(1, 'bloom_aromatics', what='蒜 + 葱 + 花椒 + 辣椒', target_C=160, level=0.5, seconds=20),
    c(2, 'thicken', sauce='碗汁', grams=60, level=0.3, max_s=10),
    c(3, 'drum_add_stir', what='finishing_oil', grams=5, seconds=2),
    c(3, 'return_and_toss', level=0.4, seconds=5), PL(3),
]
M['yuxiangqiezi'] = [
    c(0, 'steam_plate', seconds=900, level=0.5),
    c(1, 'wok_grease', oil_g=40, pour_out=True, target_C=180, fresh_oil_g=20),
    c(2, 'render_fat', what='肉末', level=0.4, seconds=20),
    c(3, 'bloom_aromatics', what='姜蒜葱 + 泡椒', target_C=140, level=0.3, seconds=20),
    c(4, 'thicken', sauce='鱼香汁 (with starch)', grams=60, level=0.3, max_s=10),
    c(5, 'add_stir_fry', what='steamed eggplant', level=0.3, seconds=30), PL(5),
]
M['mayishangshu'] = [
    c(0, 'soak_bowl', water_C=80, seconds=900, what='粉丝'),
    c(1, 'wok_grease', oil_g=40, pour_out=True, target_C=180, fresh_oil_g=20),
    c(2, 'render_fat', what='肉末 + 花椒', level=0.3, seconds=40),
    c(3, 'fry_paste_red_oil', what='豆瓣 + 姜蒜', grams=3, level=0.2, seconds=20),
    c(4, 'add_stir_fry', what='noodles', level=0.4, seconds=30, stroke='shreds_leafy'),
    c(5, 'drum_add_stir', what='生抽 (from the edge)', grams=2, seconds=10),
    c(6, 'drum_add_stir', what='蒜苗 + 葱 + 葱油', grams=30, seconds=3), PL(6),
]
M['laziji'] = [
    c(0, 'deep_fry', vessel='fryer', target_C=210, seconds=60, **{'pass': 1}),
    c(1, 'deep_fry', vessel='fryer', target_C=240, seconds=20, **{'pass': 2}, note='fryer max is usually ~190 °C: 240 °C needs a check'),
    c(2, 'bloom_aromatics', what='干辣椒 + 花椒', target_C=180, level=0.5, seconds=30),
    c(3, 'return_and_toss', level=0.3, seconds=120),
    c(4, 'drum_add_stir', what='醋 (edge) + 花生 + 油', grams=30, seconds=10), PL(4),
]
M['suancaiyu'] = [
    c(0, 'blanch_lift', vessel='pot', start='boiling', seconds=120, what='酸菜'),
    c(1, 'wash_wok'),
    c(2, 'dry_stir', what='酸菜', level=0.5, seconds=120), c(2, 'take_out', into='holding_bowl'),
    c(3, 'add_stir_fry', what='泡萝卜 + 泡姜 + 野山椒', level=0.5, seconds=60), c(3, 'take_out', into='holding_bowl'),
    c(4, 'wash_wok'),
    c(5, 'wok_grease', oil_g=40, pour_out=True, target_C=180, fresh_oil_g=20),
    c(6, 'add_off_heat', source='fish bones + head', level=0.5), c(6, 'fry_still', seconds=120),
    c(7, 'return_and_toss', level=1.0, seconds=10),
    c(8, 'wok_fill_water', water_g=1000, note='he uses hot water'),
    c(8, 'simmer_open', liquid='water', grams=1000, level=0.6, seconds=180, skim=True),
    c(8, 'fish_out_item', what='bones + 酸菜', into='serving_bowl'),
    c(9, 'poach_slices', what='鱼片', level=0.3, seconds=15),
    c(10, 'serve_soup', mass_g=1200, note='dregs held back'),
    c(11, 'hot_oil_pour_over', oil_g=60, target_C=230, onto='bowl'),
]
M['jingjiangrousi'] = [
    c(0, 'wok_grease', oil_g=40, pour_out=True, target_C=180, fresh_oil_g=40),
    c(1, 'slide_oil_meat', target_C=60, level=0.4, set_s=10, separate_s=30, take_out=False, note='cold oil start'), POFF(1),
    c(2, 'bloom_aromatics', what='蒜蓉', target_C=150, level=0.5, seconds=15),
    c(2, 'drum_add_stir', what='料酒 (from the edge)', grams=4, seconds=5),
    c(3, 'add_stir_fry', what='甜面酱', level=0.4, seconds=3),
    c(4, 'drum_add_stir', what='water (from the edge)', grams=30, seconds=10),
    c(4, 'add_off_heat', source='cup (sugar 5 g)', level=0.4),
    c(4, 'reduce_sauce', level=0.4, max_s=30, stir_every_s=5), PL(4),
]
M['congbaoyangrou'] = [
    c(0, 'wok_grease', oil_g=40, pour_out=True, target_C=180, fresh_oil_g=60),
    c(1, 'deep_fry', vessel='wok', target_C=150, seconds=60, **{'pass': 1}, note='葱心 in shallow oil, spider out'),
    c(2, 'slide_oil_meat', target_C=160, level=0.5, set_s=5, separate_s=28, take_out=True),
    c(3, 'bloom_aromatics', what='姜蒜末 + 小米辣', target_C=160, level=0.5, seconds=20),
    c(4, 'add_stir_fry', what='大葱', level=0.8, seconds=20),
    c(4, 'drum_add_stir', what='oil on the wall', grams=10, seconds=3),
    c(5, 'return_and_toss', level=0.8, seconds=3),
    c(5, 'thicken', sauce='料汁 (10 g 玉米淀粉)', grams=40, level=0.8, max_s=5), PL(5),
]
M['dandanmian'] = [
    c(0, 'render_fat', what='肉末 to crisp', level=0.5, seconds=180), c(0, 'take_out', into='holding_bowl'),
    c(1, 'add_stir_fry', what='芽菜', level=0.5, seconds=20), c(1, 'take_out', into='serving bowl', note='to the sauce bowl'),
    c(2, 'blanch_lift', vessel='pot', start='boiling', seconds=180, chill=True, what='noodles'),
    c(3, 'cold_mix_bowl', items=['noodles', '肉末', '花生碎', '葱花', '香油']),
]
M['suanlatang'] = [
    c(0, 'blanch_lift', vessel='pot', start='boiling', additive='salt', seconds=20, what='猪血 + 豆腐'),
    c(1, 'wok_fill_water', water_g=1000),
    c(1, 'simmer_open', liquid='water', grams=1000, level=1.0, seconds=30),
    c(1, 'add_off_heat', source='cup (salt 7 g)', level=1.0),
    c(2, 'thicken_multi_off_heat', passes=1, grams_each=40, level=0.3, interval_s=10, note='off heat, 拉丝 soup'),
    c(3, 'add_off_heat', source='木耳/火腿/姜/虾米', level=0.8), c(3, 'simmer_open', liquid='—', grams=0, level=0.8, seconds=60),
    c(3, 'drum_add_stir', what='香醋', grams=10, seconds=4),
    c(4, 'drum_add_stir', what='egg (drizzled)', grams=50, seconds=4, note='egg drizzle from the drum while stirring'),
    c(4, 'add_off_heat', source='猪血 + 豆腐 + 青菜丝', level=1.0), c(4, 'simmer_open', liquid='—', grams=0, level=1.0, seconds=30),
    c(4, 'serve_soup', mass_g=1200),
]
M['paihuanggua'] = [
    c(0, 'cold_mix_bowl', items=['红油 20 g', '酱油', '醋', '糖', '蒜']),
    c(1, 'arrange_on_plate', pieces=1, note='cucumber core on the plate'),
    c(1, 'pour_cup_over_plate', what='mixed cucumber + sauce'),
]
M['baiqieji_koushuiji'] = [
    c(0, 'simmer_open', liquid='water + salt 100–150 g + 姜葱 (pot)', grams=4000, level=1.0, seconds=60, note='pot, 4 kg water: no fill set for the pot'),
    c(1, 'steep_off_heat', seconds=0, note='dip-lift-drain 3×'),
    c(2, 'steep_off_heat', seconds=2400),
    c(3, 'cold_water_chill', seconds=600),
    x(3, 'prep_mince_meat_cut', 'chopping a whole cooked chicken: no chopper', what='chicken'),
    c(4, 'cold_mix_bowl', items=['酱油', 'chicken stock', '红油', '糖', '醋']),
    c(5, 'hot_oil_pour_over', oil_g=40, target_C=200, onto='bowl (姜葱蓉)'),
]
M['hongshaoliyu'] = [
    c(0, 'add_off_heat', source='whole carp', level=0.4), c(0, 'fry_still', seconds=150), c(0, 'flip_and_fry', seconds=150),
    x(0, 'take_out', 'whole fish out of the wok and back later without breaking it: needs a fish turner + ladle (two hands); workaround: leave the fish in and cook the sauce around it', into='holding_bowl'),
    c(1, 'render_fat', what='五花粒', level=0.5, seconds=60),
    c(2, 'bloom_aromatics', what='姜蒜粒', target_C=150, level=0.5, seconds=20),
    c(3, 'add_stir_fry', what='香菇 + 葱', level=0.5, seconds=10),
    c(4, 'drum_add_stir', what='生抽 (from the edge)', grams=6, seconds=3),
    c(4, 'simmer_open', liquid='beer', grams=500, level=1.0, seconds=30),
    c(5, 'braise_lid', liquid_g=0, level=0.5, seconds=360, note='workaround for 舀汤浇 (ladle_baste needs a ladle)'),
    x(5, 'take_out', 'lift the whole fish onto the plate and keep the sauce: two hands (turner + ladle); workaround: thicken first, then tip fish + sauce together', into='plate'),
    c(6, 'thicken', sauce='starch_water', grams=20, level=0.6, max_s=10),
    c(6, 'drum_add_stir', what='finishing_oil', grams=5, seconds=2), PL(6),
]
M['shousibaocai'] = [
    c(0, 'blanch_lift', vessel='pot', start='boiling', additive='salt + oil', seconds=13),
    c(1, 'wash_wok'),
    c(2, 'add_stir_fry', what='cabbage', level=1.0, seconds=18, stroke='shreds_leafy'), c(2, 'take_out', into='holding_bowl'),
    c(3, 'wash_wok'),
    c(4, 'bloom_aromatics', what='猪油 + 辣椒 + 辣椒籽 + 蒜', target_C=170, level=0.7, seconds=12),
    c(5, 'return_and_toss', level=1.0, seconds=20),
    c(5, 'drum_add_stir', what='酱油 + 醋 (from the edge)', grams=8, seconds=10), PL(5),
]
M['xiaochaoqiezi'] = [
    c(0, 'wok_grease', oil_g=30, pour_out=False, target_C=220, fresh_oil_g=0),
    c(1, 'render_fat', what='五花', level=0.4, seconds=60),
    c(2, 'bloom_aromatics', what='大蒜 + 辣椒', target_C=160, level=0.5, seconds=20),
    c(3, 'add_stir_fry', what='茄子', level=0.5, seconds=240),
    c(4, 'drum_add_stir', what='生抽 + 老抽 (from the edge)', grams=5, seconds=10), PL(4),
]
M['huangmenji'] = [
    c(0, 'soak_bowl', water_C=40, seconds=2400, what='dried 香菇'),
    c(1, 'blanch_lift', vessel='pot', start='cold', seconds=300, what='chicken'),
    c(2, 'deep_fry', vessel='wok', target_C=170, seconds=120, **{'pass': 1}, note='potatoes in 底油, spider out'),
    c(3, 'caramelize_sugar', sugar_g=20, level=0.3, max_s=120, then='meat'),
    c(4, 'add_stir_fry', what='chicken', level=0.4, seconds=120),
    c(5, 'bloom_aromatics', what='香菇 + 姜蒜粒', target_C=150, level=0.4, seconds=20),
    c(6, 'add_stir_fry', what='蚝油 + 黄豆酱 + 老抽', level=0.4, seconds=60),
    c(7, 'drum_add_stir', what='黄酒 (from the edge)', grams=15, seconds=3),
    c(8, 'wok_fill_water', water_g=600), c(8, 'braise_lid', liquid_g=600, level=0.5, seconds=900),
    c(9, 'add_off_heat', source='fried potatoes', level=0.3), c(9, 'simmer_open', liquid='—', grams=0, level=0.3, seconds=600),
    c(10, 'add_off_heat', source='青红椒', level=0.5), c(10, 'reduce_sauce', level=0.5, max_s=30, stir_every_s=10),
    c(10, 'drum_add_stir', what='生抽 + 明油', grams=10, seconds=3), PL(10),
]
M['zhengluyu'] = [
    c(0, 'steam_plate', seconds=480, level=0.5),
    c(1, 'drain_plate_juice'), c(1, 'arrange_on_plate', pieces=1), c(1, 'pour_cup_over_plate', what='葱姜丝 + 辣椒丝'),
    c(2, 'hot_oil_pour_over', oil_g=40, target_C=200, onto='plate'), c(2, 'pour_cup_over_plate', what='鱼酱油'),
    x(3, 'reboil_plate_juices', 'optional 进阶 step: chopsticks + plate + strainer at once'),
]
M['qingchao_qiangchao'] = [
    c(0, 'add_stir_fry', what='蒜末 + 菠菜', level=0.5, seconds=30, stroke='shreds_leafy'),
    c(1, 'drum_add_stir', what='salt + sugar dissolved in hot water', grams=20, seconds=3, note='replaces dissolving in the wok spoon'), PL(1),
    c(2, 'bloom_aromatics', what='蒜 + 干辣椒', target_C=160, level=0.5, seconds=20),
    c(3, 'add_stir_fry', what='油麦菜', level=0.4, seconds=30, stroke='shreds_leafy'),
    c(4, 'drum_add_stir', what='salt + sugar water', grams=20, seconds=3), PL(4),
]
M['yutoudoufutang'] = [
    c(0, 'deep_fry', vessel='wok', target_C=150, seconds=120, **{'pass': 1}, note='fish head, then 姜葱 in the same oil'),
    c(0, 'take_out', into='oil_cup', note='oil poured out, fish stays: spider the head out first (see pour_off_excess_oil)'),
    c(1, 'wok_fill_water', water_g=1000, note='he adds 2 kg (四斤): > 1 L not checked'),
    c(1, 'simmer_open', liquid='water', grams=2000, level=0.3, seconds=900),
    c(2, 'add_off_heat', source='tofu', level=1.0), c(2, 'simmer_open', liquid='—', grams=0, level=0.3, seconds=120),
    c(2, 'fish_out_item', what='葱', into='discard'),
    c(2, 'serve_soup', mass_g=2000, season_in_bowl='盐 3 g'),
    c(3, 'serve_soup', mass_g=0, note='(salt in the bowl and stir: covered by the call above)'),
]
M['jiaoyanpaigu'] = [
    c(0, 'add_stir_fry', what='椒盐 dry-roast, no oil', level=0.3, seconds=300), c(0, 'take_out', into='holding_bowl'),
    c(0, 'grind_spice'),
    c(1, 'deep_fry', vessel='fryer', target_C=180, seconds=60, **{'pass': 1}),
    c(2, 'deep_fry', vessel='fryer', target_C=150, seconds=40, **{'pass': 1}, note='蒜蓉 in a fine basket'),
    c(3, 'deep_fry', vessel='fryer', target_C=210, seconds=180, **{'pass': 2}),
    c(4, 'bloom_aromatics', what='葱椒粒 in 猪油', target_C=180, level=0.5, seconds=20),
    c(5, 'return_and_toss', level=0.6, seconds=20),
    c(5, 'drum_add_stir', what='蒜末 + 椒盐粉 3 g', grams=20, seconds=8), PL(5),
]
M['jiaoliuroduan'] = [
    c(0, 'deep_fry', vessel='fryer', target_C=160, seconds=180, **{'pass': 1}),
    c(1, 'deep_fry', vessel='fryer', target_C=200, seconds=20, **{'pass': 2}),
    c(2, 'bloom_aromatics', what='葱姜蒜 + 辅料', target_C=170, level=0.6, seconds=20),
    c(3, 'return_and_toss', level=1.0, seconds=3),
    c(3, 'thicken', sauce='碗汁', grams=60, level=1.0, max_s=8),
    c(3, 'drum_add_stir', what='芝麻油', grams=5, seconds=3), PL(3),
]
M['tudoushaoniunan'] = [
    c(0, 'blanch_lift', vessel='pot', start='cold', additive='料酒 + 姜 + 花椒 + 小茴香', seconds=3600, skim=True, note='lid on: LID_ON_pot'),
    x(0, 'prep_mince_meat_cut', 'cubing the cooked brisket: no meat cutter', what='牛腩 cubes'),
    c(1, 'fry_paste_red_oil', what='草果/葱/姜/花椒 → 豆瓣 → 甜面酱', grams=40, level=0, seconds=60, off_heat_first=True),
    c(2, 'add_stir_fry', what='beef cubes', level=0.5, seconds=30),
    c(2, 'drum_add_stir', what='料酒 (from the edge) + 泡椒', grams=20, seconds=5),
    c(3, 'wok_fill_water', water_g=800), c(3, 'add_off_heat', source='potato', level=0.4),
    c(3, 'braise_lid', liquid_g=800, level=0.4, seconds=900),
    c(4, 'add_off_heat', source='tomato', level=0.4), c(4, 'braise_lid', liquid_g=0, level=0.4, seconds=900),
    c(5, 'reduce_sauce', level=0.7, max_s=120, stir_every_s=20),
    c(5, 'drum_add_stir', what='葱油', grams=5, seconds=3), PL(5),
]
M['chaomian'] = [
    c(0, 'egg_set_and_hold', target_C=120, level=0.3, still_s=40, flip_s=40, note='荷包蛋 a bit firm'),
    x(0, 'prep_mince_meat_cut', 'cutting the fried egg into strips: no cutter for it', what='egg strips'),
    c(1, 'soak_bowl', water_C=90, seconds=420, what='instant noodles'), c(1, 'cold_water_chill', seconds=60),
    c(2, 'wok_grease', oil_g=40, pour_out=True, target_C=180, fresh_oil_g=20),
    c(3, 'slide_oil_meat', target_C=150, level=0.5, set_s=5, separate_s=25, take_out=False),
    c(3, 'add_stir_fry', what='noodles', level=0.5, seconds=5, stroke='shreds_leafy'),
    c(4, 'drum_add_stir', what='生抽 + 老抽 (from the edge)', grams=5, seconds=10),
    c(5, 'add_stir_fry', what='辅料 (veg)', level=1.0, seconds=3, stroke='shreds_leafy'),
    c(5, 'drum_add_stir', what='oil from the edge', grams=10, seconds=3),
    c(6, 'return_and_toss', level=1.0, seconds=5), PL(6),
]
M['jiangyouchaofan'] = [
    c(0, 'soak_bowl', water_C=20, seconds=600, what='dried radish'),
    x(-1, 'prep_egg_beat', 'separating whites and yolks: user does it', eggs=2),
    c(1, 'wok_grease', oil_g=40, pour_out=True, target_C=180, fresh_oil_g=20),
    c(2, 'egg_set_and_hold', target_C=120, level=0.3, still_s=30, flip_s=20, note='egg white'),
    c(3, 'add_off_heat', source='yolk', level=0.3), c(3, 'fry_still', seconds=30, note='40% oil, slow'),
    c(4, 'add_stir_fry', what='radish', level=0.4, seconds=10),
    c(5, 'return_and_toss', level=0.4, seconds=20),
    c(6, 'drum_add_stir', what='oil from the edge', grams=10, seconds=3),
    c(6, 'add_stir_fry', what='rice', level=0.4, seconds=60),
    c(7, 'drum_add_stir', what='oil + soy sauce (from the edge)', grams=12, seconds=63, level=0.7), PL(7),
]
M['naohuadoufu'] = [
    c(0, 'soak_bowl', water_C=95, seconds=300, what='tofu + 脑花'),
    c(1, 'bloom_aromatics', what='葱头 → 火锅底料', target_C=120, level=0.3, seconds=20),
    c(2, 'fry_paste_red_oil', what='豆瓣', grams=15, level=0.3, seconds=20),
    c(3, 'simmer_open', liquid='water + seasoning', grams=400, level=1.0, seconds=30),
    c(4, 'add_off_heat', source='tofu + 脑花 (slowly)', level=0.3), c(4, 'simmer_open', liquid='—', grams=0, level=0.3, seconds=600),
    c(5, 'thicken_multi_off_heat', passes=4, grams_each=10, level=0.8, interval_s=10, note='少量多次 until the oil turns glossy (亮油)'),
    c(5, 'take_out', into='plate', note='he serves in a clay pot on a burner'),
]

# ===== 4. homestyle meals A/B/C (homestyle_meals.json; phase = step index of the dish) =====
HOME['home_A_gelipaigu'] = ('蛤蜊排骨盅 (A)', [
    c(0, 'portion_into_cups', pieces=8), x(0, 'steam_cups', 'cling film needs two hands; workaround: lidded cups', cups=4),
    c(1, 'steam_cups', cups=4, seconds=1800, note='with lidded cups'), c(2, 'steam_cups', cups=4, note='cups out = STEW_CUP_OUT')])
HOME['home_A_guihuayutou'] = ('桂花糖芋头 (A)', [
    c(0, 'prep_peel', what='taro'), c(0, 'prep_cut', what='taro', cut='dice'), c(0, 'arrange_on_plate', pieces=12),
    c(1, 'steam_plate', seconds=1800, level=0.6), c(2, 'steam_plate', seconds=0, note='chopstick probe → time only'),
    c(3, 'pour_cup_over_plate', what='糖桂花酱')])
HOME['home_A_ganguotudou'] = ('干锅土豆 (A)', [
    c(0, 'deep_fry', vessel='fryer', target_C=180, seconds=180, **{'pass': 1}),
    c(1, 'render_fat', what='五花片 + 姜', level=0.5, seconds=30), c(1, 'fry_paste_red_oil', what='豆瓣', grams=5, level=0.3, seconds=15),
    c(1, 'bloom_aromatics', what='干辣椒 + 花椒', target_C=150, level=0.5, seconds=10), c(1, 'return_and_toss', level=0.8, seconds=15),
    c(1, 'drum_add_stir', what='生抽 + 十三香', grams=8, seconds=5), c(1, 'add_stir_fry', what='红椒 + 蒜苗', level=0.8, seconds=15),
    c(2, 'take_out', into='plate')])
HOME['home_A_haoyouxilanhua'] = ('蚝油西兰花 (A)', [
    c(0, 'prep_cut', what='broccoli florets', cut='section'), c(0, 'soak_bowl', water_C=20, seconds=600, what='salted water'),
    c(1, 'cold_mix_bowl', items=['water', '蚝油'], note='or premix into a drum compartment'),
    c(2, 'add_stir_fry', what='broccoli + salt', level=1.0, seconds=10), c(2, 'drum_add_stir', what='蚝油 water', grams=60, seconds=3),
    c(2, 'braise_lid', liquid_g=0, level=1.0, seconds=30), c(2, 'stir_fry', level=1.0, seconds=5), c(2, 'take_out', into='plate')])
HOME['home_A_suanrongsigua'] = ('蒜蓉蒸丝瓜 (A)', [
    x(0, 'prep_peel', 'luffa peeling: [missing] in R19_PREP_AUDIT', what='luffa'), c(0, 'prep_cut', what='luffa', cut='section'),
    c(0, 'arrange_on_plate', pieces=10), c(1, 'steam_plate', seconds=180, level=1.0),
    x(2, 'prep_mince_meat_cut', 'garlic mince: no chopper (buy minced garlic)', what='蒜蓉'),
    c(2, 'hot_oil_pour_over', oil_g=40, target_C=200, onto='bowl'), c(2, 'cold_mix_bowl', items=['蒸鱼豉油', '陈醋']),
    c(3, 'pour_cup_over_plate', what='garlic sauce')])
HOME['home_B_xiansunpaigutang'] = ('鲜笋排骨汤 (B)', [
    c(0, 'prep_cut', what='bamboo shoot', cut='slice'), c(0, 'blanch_lift', vessel='pot', start='boiling', seconds=60, what='ribs (scald)'),
    c(1, 'stew_pot', seconds=3600, water_g=1500),
    c(2, 'serve_soup', mass_g=2000, season_in_bowl='salt + celery')])
HOME['home_B_hongshaorou'] = ('红烧肉 (B)', [
    c(0, 'blanch_lift', vessel='pot', start='cold', additive='葱姜 + 料酒', seconds=300),
    x(1, 'prep_mince_meat_cut', 'scraping the skin + cubing cooked belly: no tool', what='五花 cubes'),
    c(2, 'render_fat', what='五花 cubes', level=0.5, seconds=90), c(2, 'bloom_aromatics', what='葱姜 + 八角 + 桂皮 + 干辣椒', target_C=150, level=0.4, seconds=20),
    c(2, 'caramelize_sugar', sugar_g=20, level=0.3, max_s=90, then='meat'), c(2, 'drum_add_stir', what='料酒 + 盐 + 生抽', grams=20, seconds=10),
    c(2, 'wok_fill_water', water_g=800, note='he uses boiling water'),
    c(3, 'braise_lid', liquid_g=800, level=0.5, seconds=2400), c(4, 'reduce_sauce', level=0.7, max_s=300, stir_every_s=20), c(4, 'take_out', into='plate')])
HOME['home_B_rice'] = ('米饭 (B)', [c(0, 'rice_cooker', rice_g=400)])
HOME['home_B_qingzhengluyu'] = ('清蒸海鲈鱼 (B)', [
    c(0, 'arrange_on_plate', pieces=3, note='fish bought split; ginger + scallion bed'), c(1, 'steam_plate', seconds=360, level=1.0),
    x(2, 'prep_mince_meat_cut', 'fine 葱姜胡萝卜丝 1–2 mm: no tool (slicer shred disc is 4 mm)', what='三丝'),
    c(3, 'drain_plate_juice'), c(3, 'pour_cup_over_plate', what='蒸鱼豉油 + 三丝'), c(3, 'hot_oil_pour_over', oil_g=40, target_C=220, onto='plate')])
HOME['home_B_baizhuozhi'] = ('白灼汁 (B)', [c(0, 'hot_oil_pour_over', oil_g=30, target_C=200, onto='bowl'), c(0, 'cold_mix_bowl', items=['蒸鱼豉油', '陈醋', '糖'])])
HOME['home_B_fanqiechaodan'] = ('番茄炒蛋 (B)', [
    c(0, 'prep_cut', what='tomato', cut='wedge', note='he scalds and peels; skip peeling'), x(0, 'prep_egg_beat', 'crack + beat 5 eggs: user does it', eggs=5),
    c(1, 'egg_set_and_hold', target_C=130, level=0.6, still_s=20, flip_s=10),
    c(2, 'add_stir_fry', what='scallion + tomato + salt + sugar', level=1.0, seconds=20), c(2, 'drum_add_stir', what='water', grams=40, seconds=3),
    c(2, 'braise_lid', liquid_g=0, level=1.0, seconds=30), c(2, 'return_and_toss', level=0.8, seconds=8),
    c(2, 'drum_add_stir', what='葱叶', grams=5, seconds=3), c(2, 'take_out', into='plate')])
HOME['home_B_baizhuo'] = ('白灼秋葵娃娃菜 (B)', [
    c(0, 'blanch_lift', vessel='pot', start='boiling', additive='oil + salt', seconds=60, what='baby cabbage'),
    c(0, 'blanch_lift', vessel='pot', start='boiling', additive='oil + salt', seconds=30, what='okra'), c(0, 'arrange_on_plate', pieces=12),
    c(1, 'pour_cup_over_plate', what='白灼汁')])
HOME['home_C_yutouzhengpaigu'] = ('芋头蒸排骨 (C)', [
    c(0, 'prep_marinate', minutes=20), c(1, 'prep_cut', what='taro', cut='dice'), c(1, 'arrange_on_plate', pieces=20),
    c(2, 'steam_plate', seconds=1800, level=0.6), c(3, 'pour_cup_over_plate', what='红椒 + 葱花'), c(3, 'hot_oil_pour_over', oil_g=15, target_C=200, onto='plate')])
HOME['home_C_qingjiaochaoyouyu'] = ('青椒炒鱿鱼 (C)', [
    x(0, 'prep_mince_meat_cut', 'scoring squid 麦穗花刀: buy pre-scored', what='squid'), c(0, 'blanch_lift', vessel='pot', start='boiling', seconds=20, what='squid (scald)'),
    c(1, 'bloom_aromatics', what='葱姜蒜', target_C=160, level=0.7, seconds=10), c(1, 'add_stir_fry', what='青椒 + squid', level=1.0, seconds=30),
    c(1, 'drum_add_stir', what='料酒', grams=5, seconds=3), c(1, 'thicken', sauce='碗汁 (water, 生抽, 蚝油, starch)', grams=50, level=1.0, max_s=10),
    c(1, 'take_out', into='plate')])
HOME['home_C_suanlatudousi'] = ('酸辣土豆丝 (C)', [
    c(0, 'prep_cut', what='potato', cut='shred'), c(0, 'soak_bowl', water_C=20, seconds=300, what='shreds (starch rinse)'),
    c(1, 'blanch_lift', vessel='pot', start='boiling', additive='oil + salt', seconds=10),
    c(2, 'bloom_aromatics', what='蒜 + 红椒 + 干辣椒', target_C=170, level=0.8, seconds=10),
    c(2, 'add_stir_fry', what='potato shreds', level=1.0, seconds=30, stroke='shreds_leafy'),
    c(2, 'drum_add_stir', what='调味水 (salt, vinegars, 生抽)', grams=20, seconds=5), c(2, 'drum_add_stir', what='葱叶', grams=5, seconds=3),
    c(2, 'take_out', into='plate')])
HOME['home_C_qinggaroupiantang'] = ('青瓜肉片汤 (C)', [
    x(0, 'prep_mince_meat_cut', 'slicing lean pork: no meat slicer', what='pork slices'), c(0, 'prep_marinate', minutes=10),
    c(1, 'wok_fill_water', water_g=900), c(1, 'simmer_open', liquid='water', grams=900, level=1.0, seconds=60),
    c(1, 'add_off_heat', source='ginger + cucumber', level=1.0), c(1, 'poach_slices', what='肉片', level=1.0, seconds=60),
    c(2, 'serve_soup', mass_g=1100, season_in_bowl='芹菜 + 白胡椒')])
HOME['home_C_qingchaohelandou'] = ('清炒荷兰豆 (C)', [
    c(0, 'bloom_aromatics', what='蒜', target_C=160, level=0.8, seconds=10), c(0, 'add_stir_fry', what='荷兰豆 + salt', level=1.0, seconds=30),
    c(0, 'drum_add_stir', what='water', grams=20, seconds=5), c(0, 'take_out', into='plate')])
