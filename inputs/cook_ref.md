# T03 cook_ref — grounded food-preparation task specification

The baseline produces peeled carrot and potato slices at **5 ±1 mm**, cleaned bok choy sections at **40 ±10 mm**, and **eight unpeeled tomato wedges**. Potato shreds are an optional, separately defined **2–3 mm × 2–3 mm** branch. This is the task definition for both kitchens before key-pose hardware analysis. Stove operation, stir-frying, plating and r09 grasps are outside this reference.

Research used written recipes, creator descriptions, chapters, uploaded YouTube subtitles and a small comment sample. **No video frames were watched.** YouTube subtitles were retrieved for S08 and S09. Bilibili returned HTTP 412; S10/S11 support only their indexed creator titles/descriptions. Meishij/meishi.cc was searched and an original article requested, but usable original prep instructions were unavailable; it is not counted. No knife speed or detailed technique is attributed to inaccessible video content.

There are **25 distinct evidence URLs**, four ingredients and **59 step definitions** (7 common, 52 ingredient records, including two optional julienne records). Shared calls are expanded at every physical use by the next analyst, rather than counted again as definitions. The machine-readable specification is [prep_spec.json](../../sim/t03/cook_ref/prep_spec.json).

## Cooking evidence and decisions

Potato prep has a real sequence: wash before peeling, make a flat side, cut evenly, then remove starch and drain. [S01: 万万：酸辣土豆丝（下厨房）](https://www.xiachufang.com/recipe/37746/) supports the flat-side and slice-to-strip order; [S02: 酸辣青椒土豆丝（下厨房）](https://m.xiachufang.com/recipe/107119914/) specifies about 2 × 2 mm strips; [S03: 诗韵美食：湘味土豆片（下厨房）](https://m.xiachufang.com/recipe/104471919/) uses roughly 4 mm slices. The user’s requested 5 mm slices remain the baseline. A home cook’s preference for crisp strips is also evident in the small S08 comment sample, which is context rather than a quantitative acceptance standard.

Carrot washing, peeling and slicing are common preparation steps in [S04: 东北家常菜：熘肉段（豆果）](https://m.douguo.com/recipe/imgs/3303138?step=8); [S06: Made With Lau：牛肉炒白菜](https://www.madewithlau.com/recipes/bok-choy-recipe) uses approximately 6.35 mm carrot slices. These support a sliced home-cooking ingredient while the user’s 5 mm target determines this round’s thickness.

Bok choy needs access to the creases nearest the root. [S05: Made With Lau：蒜蓉炒白菜](https://www.madewithlau.com/recipes/stir-fried-bok-choy) separates stems and rubs those areas; [S06: Made With Lau：牛肉炒白菜](https://www.madewithlau.com/recipes/bok-choy-recipe) uses soaking, agitation and draining. Whole/halved heads are legitimate alternatives in those recipes, but this round explicitly requests sections. We therefore trim the root disk, separate stems, clean each base, drain and cut short sections.

Tomato peeling is optional in [S07: Made With Lau：番茄炒蛋](https://www.madewithlau.com/recipes/tomato-and-eggs); that recipe halves tomatoes and divides each half into four wedges. The [S09: Made With Lau：Tomato + Egg](https://www.youtube.com/watch?v=Wn8ox93Qhus) cutting chapter begins at 01:24, and its Chinese captions discuss angled cuts to preserve the pulp. We retain the skin, remove hard stem tissue and preserve pulp/seeds. No blanching or boiling-water task is needed. The caption and current recipe give different blanching durations, which do not affect the chosen baseline.

Quality bands, food sizes, no-crush limits, stroke lengths and robot speeds below are **engineering assumptions**, except where a recipe measurement is identified. They make the task reviewable without claiming a universal culinary standard.

## Numbered ingredient processes

### 胡萝卜 / carrot

Reference input: [160, 35, 35] mm, 0.12 kg. Sources: [S04: 东北家常菜：熘肉段（豆果）](https://m.douguo.com/recipe/imgs/3303138?step=8), [S06: Made With Lau：牛肉炒白菜](https://www.madewithlau.com/recipes/bok-choy-recipe), [S12: Victorinox：Sharpen your knife skills](https://www.victorinox.com/en-GB/Sharpen-your-Knife-Skills/cms/sharpen-your-knife-skills/).

1. **Take vegetable from basket** (food gripper). Approach accessible sides; pinch gently; lift 120 mm clear of basket rim. Quality: One vegetable, no collisions with neighbours; soft produce must not be squeezed to increase friction.

2. **Start cold water with vegetable parked** (faucet + wash_bowl). Place vegetable in supported wash bowl, release; operate faucet; reacquire vegetable. Quality: No lever operation while pretending the same hand still holds produce.

3. **Rinse and rub every surface** (faucet + soft food pads). R holds food; L gently rubs; present near/far side and rotate food 180 deg, using bowl-supported regrasp as needed. Rinse about 15–30 s, extending until visible dirt is gone. Quality: Inspect all surface, including ends/eyes/stem recess; no soil or attached peel debris; no soap; durations are estimates, not timed video observations.

4. **Peel the washed root** (peeler). Park root and close water before peeling (C03). Place washed root on peel-side of board. R grips peeler, L holds food against board; sweep swivel blade along exposed surface, park food before rolling/regrasping; no in-hand finger rolling assumed. About 30–60 mm/s, 60–120 mm carrot stroke or 30–60 mm potato stroke. Quality: Peel removal is required for this baseline; carrot skin could be scrubbed and retained in other recipes. No visible root peel patches; nominal peel depth 0.2–0.8 mm, maximum gouge 2 mm, engineering targets.

5. **Rinse away peel fragments; close water** (wash_bowl + faucet). With root parked, reopen water (C02); re-rinse peeled surfaces; park root in clean colander, release; faucet off (C03). Clear peels from board and clean its cutting area before food returns. Quality: No peel fragments/dirt transferred to clean cutting area.

6. **Move clean vegetable to cutting board** (food gripper). Grasp from supported colander; place in clean cutting zone; release. Quality: Object rests stably; knife not used to carry whole food.

7. **Pick up knife** (knife). Use C04; other hand free before food stabilisation. Quality: Knife handle grip resists process wrench.

8. **Trim ends and create a flat support face** (knife). Cut 3–5 mm off top and dry tip; cut a 2–3 mm longitudinal facet, then put facet down. Quality: All unwanted end tissue removed; flat face down; supported reorientation with knife lifted >80 mm.

9. **Stabilise, feed and cut 5 mm slices** (knife + food gripper). L supports behind cutting plane; R push-cuts down with up to 20 mm forward component; feed 5 mm after clearing edge. About 20–60 mm/s through food, 0.3–0.7 cuts/s overall; no impact chopping. Keep each cut perpendicular to feed. Quality: 5 +/-1 mm slices; last edible end slice must also pass, including held stub 10 mm long. No omitted final-cut pose or unexplained discarded remainder; final sliver may join trim only if <3 mm.

10. **Push/scoop pieces into the ingredient bowl** (knife flat + output_bowl). Release food on board; L steadies empty bowl rim; R gathers with flat/spine, lifts a small batch over the 90 mm rim and tilts into bowl. Scraping alone at board height cannot cross a bowl rim; no teleporting pieces. Quality: At least 98% of cut edible mass reaches bowl; no spill; no sharp-edge dragging; tomato batches <=25 g.

11. **Return knife between batches** (knife). Set knife on valid dock; clean/rinse between dirty/clean work and after tomato; full final clean uses C06. Quality: Blade supported before releasing handle.

12. **Park finished bowl and reset the active station** (output_bowl). After the knife is parked and all final rinsing is complete, take the filled bowl with both hands on opposite rim points; lift, set in its labelled counter parking location, release; install next clean bowl at active station. Quality: Ingredient bowls remain separate and fully supported; no overlap with blade sweep, basket or draining station.

### 土豆 / potato

Reference input: [90, 65, 70] mm, 0.20 kg. Sources: [S01: 万万：酸辣土豆丝（下厨房）](https://www.xiachufang.com/recipe/37746/), [S02: 酸辣青椒土豆丝（下厨房）](https://m.xiachufang.com/recipe/107119914/), [S03: 诗韵美食：湘味土豆片（下厨房）](https://m.xiachufang.com/recipe/104471919/), [S08: 小高姐：酸辣土豆丝，烹饪基础系列（3）](https://www.youtube.com/watch?v=DwlD6gdXrF8).

1. **Take vegetable from basket** (food gripper). Approach accessible sides; pinch gently; lift 120 mm clear of basket rim. Quality: One vegetable, no collisions with neighbours; soft produce must not be squeezed to increase friction.

2. **Start cold water with vegetable parked** (faucet + wash_bowl). Place vegetable in supported wash bowl, release; operate faucet; reacquire vegetable. Quality: No lever operation while pretending the same hand still holds produce.

3. **Rinse and rub every surface** (faucet + soft food pads). R holds food; L gently rubs; present near/far side and rotate food 180 deg, using bowl-supported regrasp as needed. Rinse about 15–30 s, extending until visible dirt is gone. Quality: Inspect all surface, including ends/eyes/stem recess; no soil or attached peel debris; no soap; durations are estimates, not timed video observations.

4. **Peel the washed root** (peeler). Park root and close water before peeling (C03). Place washed root on peel-side of board. R grips peeler, L holds food against board; sweep swivel blade along exposed surface, park food before rolling/regrasping; no in-hand finger rolling assumed. About 30–60 mm/s, 60–120 mm carrot stroke or 30–60 mm potato stroke. Quality: Peel removal is required for this baseline; carrot skin could be scrubbed and retained in other recipes. No visible root peel patches; nominal peel depth 0.2–0.8 mm, maximum gouge 2 mm, engineering targets.

5. **Remove shallow eyes/blemishes on supported potato** (peeler eye scoop). Hold supported potato; approach eyer, turn/scoop up to 30 deg, lift removed tissue. Reject green, heavily sprouted, rotten or deeply damaged input. Quality: No dark eye tissue left; shallow localized recess only; rotate supported potato to check every side.

6. **Rinse away peel fragments; close water** (wash_bowl + faucet). With root parked, reopen water (C02); re-rinse peeled surfaces; park root in clean colander, release; faucet off (C03). Clear peels from board and clean its cutting area before food returns. Quality: No peel fragments/dirt transferred to clean cutting area.

7. **Move clean vegetable to cutting board** (food gripper). Grasp from supported colander; place in clean cutting zone; release. Quality: Object rests stably; knife not used to carry whole food.

8. **Pick up knife** (knife). Use C04; other hand free before food stabilisation. Quality: Knife handle grip resists process wrench.

9. **Trim ends and create a flat support face** (knife). Trim localized blemish if needed; cut a 2–3 mm longitudinal facet and put it down. Half potato longitudinally if a facet cannot stabilize it; half-round slices are accepted. Quality: All unwanted end tissue removed; flat face down; supported reorientation with knife lifted >80 mm.

10. **Stabilise, feed and cut 5 mm slices** (knife + food gripper). L supports behind cutting plane; R push-cuts down with up to 20 mm forward component; feed 5 mm after clearing edge. About 20–60 mm/s through food, 0.3–0.7 cuts/s overall; no impact chopping. Keep each cut perpendicular to feed. Quality: 5 +/-1 mm slices; last edible end slice must also pass, including held stub 10 mm long. No omitted final-cut pose or unexplained discarded remainder; final sliver may join trim only if <3 mm.

11. **Push/scoop pieces into the ingredient bowl** (knife flat + output_bowl). Release food on board; L steadies empty bowl rim; R gathers with flat/spine, lifts a small batch over the 90 mm rim and tilts into bowl. Scraping alone at board height cannot cross a bowl rim; no teleporting pieces. Quality: At least 98% of cut edible mass reaches bowl; no spill; no sharp-edge dragging; tomato batches <=25 g.

12. **Return knife between batches** (knife). Set knife on valid dock; clean/rinse between dirty/clean work and after tomato; full final clean uses C06. Quality: Blade supported before releasing handle.

13. **Optional 土豆丝: slice 2–3 mm planks instead of 5 mm slices** (knife + food gripper). **Optional julienne branch.** After P09 replace baseline P10: put flat face down; slice at 2.5 mm nominal feed. Quality: Plank thickness 2–3 mm; target 2.5 +/-0.5 mm; no uncut bridges.

14. **Optional 土豆丝: arrange a low stack and cut strips** (knife + food gripper). **Optional julienne branch.** Park knife on dock to free R; arrange 2–3 planks in a stable stack (<=9 mm high), cut faces down; reacquire knife and cut strips at 2.5 mm feed. Use overlapping planks rather than a tall slippery stack. Quality: Both cross-section dimensions 2–3 mm; useful strand length 30–80 mm; at least 90% by mass intact strands, tolerance chosen by team.

15. **Rinse starch from slices or optional shreds and drain** (wash_bowl + colander + faucet). **After piece collection, for all potato cuts.** After scooping, rinse potato pieces in a supported wash bowl; gently agitate 20 mm, lift food out in colander leaving settled residue behind; change water 2–3 times until nearly clear; drain 20–30 s. Optional shreds may soak 5–10 min in cold water; vinegar belongs to recipe choice and is not a required additional ingredient task. Quality: Last rinse nearly clear: visual target no visible white swirl against dark backing; no free puddle after drain; pieces remain separated.

16. **Park finished bowl and reset the active station** (output_bowl). After the knife is parked and all final rinsing is complete, take the filled bowl with both hands on opposite rim points; lift, set in its labelled counter parking location, release; install next clean bowl at active station. Quality: Ingredient bowls remain separate and fully supported; no overlap with blade sweep, basket or draining station.

Baseline order: 01,02,03,04,05,06,07,08,09,10,11,12,J03,13. Julienne replaces 10 with J01,J02 before 11; J03 remains required. After drain/decant park the filled bowl with 13.

### 上海青 / 小白菜 / bok choy

Reference input: [170, 100, 70] mm, 0.10 kg. Sources: [S05: Made With Lau：蒜蓉炒白菜](https://www.madewithlau.com/recipes/stir-fried-bok-choy), [S06: Made With Lau：牛肉炒白菜](https://www.madewithlau.com/recipes/bok-choy-recipe), [S12: Victorinox：Sharpen your knife skills](https://www.victorinox.com/en-GB/Sharpen-your-Knife-Skills/cms/sharpen-your-knife-skills/).

1. **Take the head from basket** (food gripper). Grasp broad stalk area, not fragile leaf tips; lift clear. Quality: No crushed leaf tissue.

2. **Open cold water; park greens before operating control** (faucet + wash_bowl). Place greens in supported bowl; free hand for faucet. Quality: No unsupported head while control hand is busy.

3. **Coarse rinse the head and root base** (faucet + soft pads). Rinse external soil before root trimming; turn basal end toward water stream; discard yellow/rotten outer leaves. Quality: No mud spread onto clean cutting zone.

4. **Trim root disk on dirty-prep area; park knife** (knife). On board cut 5–10 mm basal disk, enough to release stems; park knife, clear dirty trim and clean board before section cuts. Quality: Basal root tissue discarded, edible stalk retained.

5. **Separate every stalk/leaf for access to basal creases** (food grippers). Both hands pinch thick stalk portions; pull separated leaves 20–50 mm apart; release into bowl. If still attached, repeat localized root trim with knife parked between separation attempts. Quality: Every inner leaf/stalk crease exposed; tearing a whole bunch or shaking alone does not meet cleaning quality.

6. **Soak, rub basal creases, lift and rinse in fresh water** (wash_bowl + faucet). Ten-minute cold-water soak as reference; L holds one stalk, R soft pad rubs its basal crease at 2–5 N; agitate gently; lift leaves out before emptying dirty water. Repeat fresh water rinse until grit gone; no squeeze wringing. Quality: Inspect every basal crease and final rinse; no grit or dirt. Source soak durations vary 10–30 min; timing alone is not the acceptance test.

7. **Drain in handled colander, with gentle optional shake** (colander). Hold both handles level; tilt +/-10 deg, translate +/-20 mm at an estimated 0.5–1 Hz for 3–5 cycles; replace on flat tray; drain 30 s; optional blot with supported cloth. Quality: No torn leaves, no spills, no continuous dripping stream after drain; single shake cannot replace basal cleaning.

8. **Stop water and transfer drained greens to clean board** (food grippers + faucet). Park colander before faucet-off; move loose small bundles from supported colander to board. Quality: All leaves clean; bundle <=30 mm high.

9. **Split thick stalks and arrange a low bundle** (knife + food gripper). Cut stalks wider than 15 mm lengthwise; stack 2–3 stalks parallel, bundle height <=30 mm; leaves may be cut separately. Park knife if both hands are needed to arrange the bundle. Quality: Stalk width <=15 mm; no tall compressed bunch.

10. **Cut 40 mm sections** (knife + food gripper). L pins stalks behind blade; R push/slice completely through bundle with 10–20 mm forward component. Feed 40 mm; 30–80 mm/s and 0.4–0.8 cuts/s are engineering starting speeds, not measured human observations. Quality: Sections 30–50 mm; no attached fibres or macerated leaf edges.

11. **Scoop stalk and leaf sections into bowl** (knife flat + output_bowl). Release bundle; L steadies bowl; lift over rim with small knife-flat batches as in transfer poses. Quality: At least 98% of cut edible mass in bowl; stalks/leaves can be separate batches.

12. **Return knife** (knife). Use supported dock; final rinse/dry is C06. Quality: Knife supported before release.

13. **Park finished bowl and reset the active station** (output_bowl). After the knife is parked and all final rinsing is complete, take the filled bowl with both hands on opposite rim points; lift, set in its labelled counter parking location, release; install next clean bowl at active station. Quality: Ingredient bowls remain separate and fully supported; no overlap with blade sweep, basket or draining station.

### 番茄 / tomato

Reference input: [70, 70, 60] mm, 0.15 kg. Sources: [S07: Made With Lau：番茄炒蛋](https://www.madewithlau.com/recipes/tomato-and-eggs), [S09: Made With Lau：Tomato + Egg](https://www.youtube.com/watch?v=Wn8ox93Qhus), [S11: 小高姐：番茄炒蛋，要做到漂亮好吃](https://www.bilibili.com/video/BV1PW411T7YB/), [S12: Victorinox：Sharpen your knife skills](https://www.victorinox.com/en-GB/Sharpen-your-Knife-Skills/cms/sharpen-your-knife-skills/).

1. **Take vegetable from basket** (food gripper). Approach accessible sides; pinch gently; lift 120 mm clear of basket rim. Quality: One vegetable, no collisions with neighbours; soft produce must not be squeezed to increase friction.

2. **Start cold water with vegetable parked** (faucet + wash_bowl). Place vegetable in supported wash bowl, release; operate faucet; reacquire vegetable. Quality: No lever operation while pretending the same hand still holds produce.

3. **Rinse and rub every surface** (faucet + soft food pads). R holds food; L gently rubs; present near/far side and rotate food 180 deg, using bowl-supported regrasp as needed. Rinse about 15–30 s, extending until visible dirt is gone. Quality: Inspect all surface, including ends/eyes/stem recess; no soil or attached peel debris; no soap; durations are estimates, not timed video observations.

4. **Drain and stop water; keep skin** (colander + faucet). Park tomato in supported colander; release; close water; drain about 10 s. Do not blanch or peel. Quality: Surface clean; skin intentionally retained; no hot-water step.

5. **Move clean vegetable to cutting board** (food gripper). Grasp from supported colander; place in clean cutting zone; release. Quality: Object rests stably; knife not used to carry whole food.

6. **Pick up knife** (knife). Use C04; other hand free before food stabilisation. Quality: Knife handle grip resists process wrench.

7. **Halve tomato and remove hard stem core** (knife + food gripper). L cups tomato on board gently; R draw-slices through centre. Lay each half cut-face down for stable support, then make two small angled V-cuts around hard stem tissue; park knife during supported reorientation if both hands are needed. Quality: Remove hard stem tissue; do not remove seed cavities; no need for a separate paring-knife grasp.

8. **Cut each half into four attached-pulp wedges** (knife + food gripper). Three dividing cuts per half with radial planes at 45/90/135 deg relative to its cut face; arrange/rotate each half on a stable cut face between cuts. Draw 40 mm while descending; 10–40 mm/s, 0.2–0.5 cuts/s; use angled cuts to retain pulp rather than squeezing. Quality: Eight completely separated wedges; 35–55 deg each, mass 0.65–1.35 times mean; seeds/pulp attached; do not use a crushing vertical chop.

9. **Push/scoop pieces into the ingredient bowl** (knife flat + output_bowl). Release food on board; L steadies empty bowl rim; R gathers with flat/spine, lifts a small batch over the 90 mm rim and tilts into bowl. Scraping alone at board height cannot cross a bowl rim; no teleporting pieces. Quality: At least 98% of cut edible mass reaches bowl; no spill; no sharp-edge dragging; tomato batches <=25 g.

10. **Return knife between batches** (knife). Set knife on valid dock; clean/rinse between dirty/clean work and after tomato; full final clean uses C06. Quality: Blade supported before releasing handle.

11. **Park finished bowl and reset the active station** (output_bowl). After the knife is parked and all final rinsing is complete, take the filled bowl with both hands on opposite rim points; lift, set in its labelled counter parking location, release; install next clean bowl at active station. Quality: Ingredient bowls remain separate and fully supported; no overlap with blade sweep, basket or draining station.

## Tools, geometry, mass and storage

The light Chinese vegetable cleaver is the reference, since it performs the requested cuts and offers a broad scooping flat. A western chef knife is a credible alternative for tomato draw-slicing and tip-pivot rocking. A bone chopper is unnecessary. Market dimensions are overall envelopes; handle zones and tool-contact offsets must still be modelled. Package masses are conservative upper bounds, never labelled net measurements.

| Tool | Geometry (mm) | Mass | Basis / role |

|---|---|---|---|

| Reference light Chinese vegetable cleaver / 菜刀 | 309 × 85 × 18 | 0.198 kg | manufacturer net; [S16: Victorinox Chinese Style Chef knife 6.8561.18G](https://www.victorinox.com/en-TW/Products/Cutlery/Chef%27s-Knives/Swiss-Classic-Chinese-Style-Chef%E2%80%99s-Knife/p/6.8561.18G) |

| Alternative 200 mm western chef knife | 344 × 54 × 19 | 0.179 kg | manufacturer net; [S17: Victorinox wooden cook/carving knife 5.2060.20G](https://victorinox.com.au/products/cooks-carving-knife-1) |

| Reference thick-grip swivel Y-peeler, OXO 21081 | 152.4 × 76.2 × 25.4 | 0.100 kg | engineering upper budget; OXO net mass absent; [S22: OXO Good Grips Y-Peeler 21081](https://www.oxo.com/shop/kitchenware/utensils/y-peeler.html), [S15: Victorinox REX Peeler 6.0900.1](https://www.victorinox.com/en/Products/Cutlery/Graters-and-Peelers/REX-Peeler/p/6.0900.1) |

| Existing T02 400x300x25 mm board | 400 × 300 × 25 | 1.950 kg | engineering estimate: 0.4*0.3*0.025 m^3 * 650 kg/m^3 hardwood; board/sim/t02/cook_chain/scenes/kitchen_galley.json |

| Passive anti-slip silicone mat under board | 400 × 300 × 2 | 0.264 kg | engineering estimate: 0.4*0.3*0.002 m^3 *1100 kg/m^3 assumed silicone density; Engineering estimate |

| Handled stable-bottom KLOCKREN 5 L | 300 × 240 × 200 | 0.410 kg | package upper bound; [S19: IKEA KLOCKREN 504.491.77, 5 L](https://www.ikea.com/gb/en/p/klockren-colander-50449177/) |

| BLANDA BLANK 28 cm | 280 × 280 × 130 | 0.570 kg | package upper bound; [S21: IKEA BLANDA BLANK 401.796.99, 28 cm](https://www.ikea.com/sg/en/p/blanda-blank-serving-bowl-stainless-steel-40179699/) |

| BLANDA BLANK 20 cm; one bowl per ingredient | 200 × 200 × 90 | 0.220 kg | package upper bound; [S20: IKEA BLANDA BLANK 200.572.55, 20 cm](https://www.ikea.com/gb/en/p/blanda-blank-serving-bowl-stainless-steel-20057255/) |

| T02 produce basket | 420 × 340 × 160 | 0.500 kg | engineering estimate, not carried as a loaded batch; board/sim/t02/cook_chain/scenes/kitchen_galley.json |

| Existing T02 horizontal supported knife rest | 540 × 145 × 60 | 0.550 kg | T02 fixture ledger; board/sim/t02/cook_chain/README.md |

| Passive washable tool tray | 180 × 90 × 15 | 0.120 kg | engineering estimate, thin stainless tray; Engineering estimate |

| Passive drain tray | 320 × 260 × 15 | 0.200 kg | engineering estimate, thin stainless tray; Engineering estimate |

| Washable absorbent cloth | 200 × 200 × 3 | 0.030 kg | engineering estimate dry; use 0.08 kg wet; Engineering estimate |

| Optional guarded OXO Chef mandoline 2.0 | 406.4 × 177.8 × 158.75 | 1.500 kg | engineering upper budget; not sourced net mass; [S23: OXO Chef mandoline 2.0, 11194500](https://www.oxo.com/chef-s-mandoline-slicer-2-0.html) |

| Optional OXO pump salad spinner | 266 × 266 × 152 | 1.700 kg | manufacturer packaged upper bound; [S24: OXO UK Salad Spinner 1351580](https://www.oxouk.com/products/salad-spinner/) |

The OXO peeler’s official page gives dimensions but no numeric mass: 100 g is a design budget. The REX has a genuine published 14 g mass but a thinner handle. The mandoline’s 1.5 kg is also a budget, not a sourced net mass; its settings do not establish a 2–3 mm julienne blade width. Its food guard, travel endpoints and terminal remnant need separate key poses before it can replace knife tasks.

KLOCKREN’s 240 mm diameter and 410 g package mass are sourced. The reference 300 ×240 ×200 mm working envelope and 120 mm contact base are assumptions because expanded height/base dimensions are not provided. Do not equate the 120 mm package height with the expanded height. Knife contact offset [140,0,-55] mm, handle grip zone [100,28,18] mm and 2 mm blade thickness are nominal reference geometry with 10 mm envelope uncertainty. They are not product CAD measurements.

Knife storage uses the supported T02 horizontal rest. The knife, its rest lands and pickup transform must agree after a market knife substitution. The peeler lies in a shallow tray. The colander rests on a broad flat drain tray. No pedestal, printed part, robot actuator or counterbalance is introduced by this reference. If later hardware needs a sleeve or holder, r05 fabrication rules apply and it needs its own geometry/mass/retention check.

## Hand techniques and operating speeds

The human claw grip curls fingers and uses knuckles to guide the knife; a flat food face prevents rolling. [S12: Victorinox：Sharpen your knife skills](https://www.victorinox.com/en-GB/Sharpen-your-Knife-Skills/cms/sharpen-your-knife-skills/) describes claw, rocking/slicing and strip cuts. Parallel jaws need an equivalent supported-food hold while leaving the blade envelope clear; they cannot assume independent fingertip feeding or safe blade-to-knuckle contact.

Root vegetables use a controlled down-and-forward push cut, with a short sliding component. Greens use a low bundle and a complete push/slice. Tomato uses a draw-slice, then supported reorientation for core and radial wedge cuts. A chef knife can rock around its tip if its tip/heel and handle extremes are added to the model. The broad flat or spine gathers pieces; small scoops lift them over the bowl’s 90 mm rim. A horizontal scrape at board height alone cannot put food into that bowl.

| Operation | Robot starting speed/cadence | Evidence status |

|---|---|---|

| Carrot/potato push-cut | 20–60 mm/s, 0.3–0.7 cuts/s including feed | Engineering starting range |

| Greens sections | 30–80 mm/s, 0.4–0.8 cuts/s | Engineering starting range |

| Tomato draw-slice | 10–40 mm/s, 0.2–0.5 cuts/s | Engineering starting range |

| Y-peeler | 30–60 mm/s; 60–120 mm carrot /30–60 mm potato strokes | Engineering starting range |

| Gentle colander shake | ±20 mm, ±10°, 0.5–1 Hz for 3–5 cycles | Engineering starting range; key-pose screen only |

None is a measured human typical speed. Runtime or chapter length does not establish hand velocity. The study’s 20–40 **mm/min** must not be misread as mm/s or normal home-cooking speed.

## Finished-product acceptance

| Ingredient/cut | Target and tolerance | Rejection examples |

|---|---|---|

| Carrot and potato slices | 5 mm nominal; 4–6 mm; within-slice thickness difference ≤1 mm; half-rounds allowed | Uneven thickness, uncut bridges, crushing/splintering, soil or peel remaining in peeled baseline |

| Optional potato shreds | Each cross-section axis 2–3 mm; 2.5 mm nominal; useful length 30–80 mm; ≥90% intact strands by mass | Fries masquerading as shreds, grated pulp, mashed edges, starch clumps |

| Greens | 30–50 mm sections, nominal 40; stalk width ≤15 mm | Root disk, basal grit, uncut fibres, macerated leaves |

| Tomato | Eight wedges; nominal 45°, 35–55°; piece mass 0.65–1.35× mean | Stem tissue, unsevered skin, squeezing away seed cavity, collapsed wedges |

Inspect ten distributed cuts or every piece if fewer than ten; check all material for uncut bridges and all greens basal creases for dirt. For tomato count all wedges and check each for skin separation and pulp retention. ≥98% of cut edible mass must reach its bowl. The terminal root slice is part of the task: model a 10 mm remaining stub, rather than quietly omitting the hardest final cut. Skin on the selected tomato is intentional and acceptable.

滚刀块 is a different finished product: a useful comparison target would be roughly 20–30 mm chunks made with diagonal cuts and supported 60–90° rolls. Those dimensions/roll angles are engineering examples, not a sourced universal standard. It would need roll-regrasp poses. It is not part of the required slices or an allowed substitute this round.

## Force assumptions and static load contract

[S13: Singh, Das & Das (2016), IJFS 5(1), 22–38](https://iseki-food-ejournal.com/article/69/pdf) reports mean peak forces of **47.90–67.59 N for carrot** and **43.68–61.49 N for potato**. The tests used whole specimens, a straight 0.952 mm blade, 15/20/25° edge angles and 20/30/40 mm/min. These are experimental averages under particular conditions, not upper bounds for arbitrary root size, blade wear or robot speed. [S14: Seattle Ultrasonics：Quantified Knife, Tojiro 8.2 inch](https://seattleultrasonics.com/pages/knife-pages/tojiro-japan-professional-82-chefs-knife) provides useful sharpness/food-test context, but its food labels are graphical; no unlabeled force figure is assigned to an ingredient here.

| Action | Expected / conservative screen | Basis |

|---|---|---|

| Carrot cut | 50–80 N expected design range | Study + widened engineering range |

| Potato cut | 40–70 N expected design range | Study + widened engineering range |

| Low greens bundle | 5–30 N | Estimate for thin water-rich stalks/leaves, ≤30 mm bundle |

| Tomato draw cut | 3–15 N | Estimate for sharp sliding edge; higher force can damage quality |

| Carrot peel | 3–8 N normal, 5–15 N drag; screen 10 N normal +20 N drag | Estimate: 8 N / (25 mm ×0.2 mm ribbon) ≈1.6 MPa effective resistance |

| Potato peel | 2–6 N normal, 3–10 N drag; screen 10 N normal +20 N drag | Estimate: 5 N / same ribbon area ≈1 MPa; enlarge for skin variation |

| Eye scoop | 15 N | Estimate |

| Root /greens /tomato rubbing | Screens 10 /5 /3 N | Estimate, avoid leaf/fruit squeezing |

| Small scoop/scrape | 10 N lateral +5 N vertical | Estimate, second hand steadies bowl |

| Supported knife wipe | 3 N normal +5 N drag | Estimate, both flats, edge away |

The mechanical faucet proxy is **0.20–0.30 Nm**, sourced from [S25: SEDAL SN-35 S/D 08SN35S5001 technical sheet](https://sedal.com/pdfs/ENGLISH/TDS08SN35S5001.pdf). Use **0.60 Nm** as the conservative screen, equivalent to 6 N at a 100 mm lever; model the sheet’s 25° opening endpoints. It is a cartridge-family proxy, not a measurement of the unidentified T02 fixture. The sheet’s **10–12 Nm is assembly nut torque**, not actuation. A sensor faucet can remove lever torque but must have its selected product geometry, mass and detection poses supplied before admission.

**Binding hardware tests:** at every loaded cutting key pose evaluate 30, 50 and 80 N downward, each with ±10 N lateral along both board axes. Do not use the expected tomato/greens range to waive the prescribed high-load screen. These are static capability envelopes, not commands to apply 80 N to a tomato. The wrench acts at the edge/contact point; include the actual lever arm to the handle, gravity, tool/payload and the holding-arm reaction. Continuous torque ratings govern; no transient rating credit.

Use grip SF ≥1.5, wet μ=0.15 as a conservative assumption, and explicitly distinguish per-jaw from total normal force. A symmetric friction hold requires N_per_jaw ≥SF×F_tangent/(2μ). Wet 200 g potato carry needs about 9.81 N per jaw and 150 g tomato about 7.36 N per jaw before moments/rubbing. Knife friction-only resistance to 80 N plus 10 N needs about 202 N per jaw at dry μ=0.30, or **403 N per jaw at wet μ=0.15**, before the edge-offset moment; a retained/form-fit tool grip may be needed. A no-crush upper grip limit must also be checked for tomato (reference compression <10%, no visible bruise), not solved merely by increasing squeeze.

## Scene, key poses and both kitchens

Every ingredient step specifies its tool, motion, force model, key poses and quality targets in JSON. Common faucet, knife acquisition/return and cleanup records expand at every call. Poses specify **tool contact or object centres, not flange coordinates**: compose real grasp/tool transforms for IK. Cutting evaluates first/middle/last feed and stroke-start/peak-depth/cut-through, plus final regrasp; tomato adds angled core/wedge extremes. Held objects and full blade/finger envelopes remain present.

| Station | Galley world origin (m) | L kitchen world origin (m) |

|---|---|---|

| board_origin_world_m | [0.35, 0.2, 0.877] | [-0.3, -1.35, 0.877] |

| basket_origin_world_m | [-1.3, 0.24, 0.865] | [0.55, 0.25, 0.865] |

| wash_origin_world_m | [-0.4, 0.3, 0.9] | [-0.3, -0.8, 0.9] |

| wash_bowl_bottom_world_m | [-0.4, 0.3, 0.65] | [-0.3, -0.8, 0.65] |

| colander_bottom_world_m | [-0.92, 0.3, 0.865] | [1.02, 0.3, 0.865] |

| output_bowl_bottom_world_m | [0.03, 0.2, 0.85] | [-0.3, -1.67, 0.85] |

| knife_dock_bottom_world_m | [0.4, 0.46, 0.85] | [-0.29, 0.46, 0.85] |

| peeler_tray_bottom_world_m | [0, 0.46, 0.85] | [-0.3, -1.88, 0.85] |

| faucet_pivot_world_m | [-0.41, 0.547, 1.019] | [-0.547, -0.81, 1.019] |

Galley free floor is x=[−1.8,1.8], y=[−1.2,0] m. L floor is x=[0,1.5], y=[−1.5,0] m. All countertop stations are outside the floor polygon; base and lift are searched over their legal ranges. Board u/v are +x/+y in the galley and +y/−x in the L kitchen. The L board is moved onto the fully supported west-counter-high region, clear of the sink opening. The L basket/draining station use the real north counter. These are recorded scene changes to be analysed, not claimed reachability results.

Counter height is 850 mm; reference board surface is **877 mm** including a 2 mm anti-slip mat. The sink bowl rests on the real sink bottom at 650 mm, and the colander on a drain tray at 865 mm. One output bowl and one ingredient occupy the active cutting station at a time; filled bowls need distinct supported parking. Move incompatible old objects/knife adapters to valid supports rather than leaving duplicate masses or overlapping parked tools in the scene.

The JSON includes proposed support polygons and COM eccentricity bounds. With assumed contact diameters of 120/80/120 mm, colander/output-bowl/wash-bowl rest margins are 40/25/45 mm respectively. Those are **reference calculations on assumed base geometry**, not a certificate for an unmeasured market product. The next role checks actual contact polygons. The empty small bowl needs the free hand at its rim during transfer to resist tipping. No pedestal is used.

At each pose search whole-body base x/y/yaw and lift with mink, solving both arms together when needed. Use a copy of the repaired T02 toolkit/ACM with ≥10 mm real forbidden gap at the pose and ±20 mm /±5° neighbourhood; only intended food/tool/support contacts are allowed. Record continuous torque ratio and worst joint, grip margin, signed support margin, all joint-limit distances and manipulability with stated Jacobian frame/scaling. Suggested robustness targets are ≥10° revolute-limit and ≥20 mm lift-end margin; they are advisory design targets, not extra binding pass thresholds.

A later hardware phase receives its explicit local supported/held setup even when an earlier phase fails. Its verdict is OK only if every expanded key pose passes; otherwise FAIL with the numerical blocker. **This reference itself does not run IK, assign hardware verdicts, or require a continuous collision-free chain.**

## Minimum viable execution and difficult steps

Prepare supported stations; then run carrot slices, potato slices, greens sections and tomato wedges in separate bowls. Each batch follows take →park →faucet on →wash/peel or expose basal creases →rinse/drain →faucet off →clean board →knife pickup →trim/stabilise/cut →small scoops over bowl rim →knife return. Potato pieces always receive a post-cut starch rinse and drain; optional shreds replace only the cut geometry. Finish with knife rinse, supported cloth drying and storage.

The hardest parallel-gripper actions are curved peeling/regrasp, spreading thin greens and cleaning inner bases, holding the tiny last root remainder, arranging 2–3 mm plank stacks, and gently stabilising tomato while cutting angled wedges. Piece transfer frees the food-holding hand to steady the bowl; cleaning frees a hand by parking food/tools. There is no hidden third hand.

Robot-friendly market options are a thick-handle swivel peeler, handled stable-bottom colander, guarded mandoline, pump spinner and sensor/long-lever faucet. Mandoline/spinner substitutions add their own setup, guard/lid/pump, stroke-end and release poses. A grid chopper’s cubes and crushed tomato do not meet slices/wedges; a rasp’s ragged pulp is not automatically acceptable 土豆丝. Tools can reduce dexterity demands, but quality and terminal-remnant handling must still be checked.

## Evidence source list

- **S01** [万万：酸辣土豆丝（下厨房）](https://www.xiachufang.com/recipe/37746/) — Wash and peel; make a flat face; slice evenly then cut strips; change soaking water and drain. Access: indexed primary recipe text; direct desktop page presented CAPTCHA.

- **S02** [酸辣青椒土豆丝（下厨房）](https://m.xiachufang.com/recipe/107119914/) — Wash before peeling; approximately 2 by 2 mm strips; repeated rubbing/rinsing to remove starch. Access: indexed primary recipe step text. Limit: The numerical robot tolerances are ours.

- **S03** [诗韵美食：湘味土豆片（下厨房）](https://m.xiachufang.com/recipe/104471919/) — Peel and cut approximately 4 mm slices; rinse away starch and drain. Access: page text.

- **S04** [东北家常菜：熘肉段（豆果）](https://m.douguo.com/recipe/imgs/3303138?step=8) — The vegetable preparation step washes, peels and slices carrot. Access: indexed primary recipe steps; direct request failed.

- **S05** [Made With Lau：蒜蓉炒白菜](https://www.madewithlau.com/recipes/stir-fried-bok-choy) — Separate stems, rub root-side creases, rinse, drain; optional soaking and separating stalks/leaves. Access: indexed primary full recipe text. Limit: Long soaking is an option, not proof that rinsing is unnecessary.

- **S06** [Made With Lau：牛肉炒白菜](https://www.madewithlau.com/recipes/bok-choy-recipe) — Ten-minute soak, remove outer leaves, agitate stem-up and drain; halve/quarter; carrot slices about 6.35 mm. Access: page text.

- **S07** [Made With Lau：番茄炒蛋](https://www.madewithlau.com/recipes/tomato-and-eggs) — Peeling is optional; remove hard stem tissue; halve then make four wedges per half; retain seeds/pulp. Access: page text.

- **S08** [小高姐：酸辣土豆丝，烹饪基础系列（3）](https://www.youtube.com/watch?v=DwlD6gdXrF8) — Text captions specify peeling, water/vinegar soaking and draining; a sampled viewer prioritises crisp texture. Access: description + uploaded English subtitles + five comments; no frames. Limit: Captions say to cut, but do not establish the plank-stack technique or a measured cutting speed.

- **S09** [Made With Lau：Tomato + Egg](https://www.youtube.com/watch?v=Wn8ox93Qhus) — Chapters 00:42 and 01:24 discuss optional peeling and cutting; Chinese captions describe angled cuts preserving pulp. Access: description + chapters + uploaded zh-Hans subtitles + five comments; no frames. Limit: Caption blanching time differs from current written recipe; blanching is excluded from the baseline.

- **S10** [王刚：土豆切片切丝不均匀，切刀的类型](https://www.bilibili.com/video/BV1Gb411H7uz/) — Creator title identifies slice/strip uniformity and knife selection as the instructional problem. Access: indexed primary title/description only; direct page and yt-dlp returned HTTP 412. Limit: No transcript or comments obtained; no unseen technique, timing or tool dimensions attributed to this video.

- **S11** [小高姐：番茄炒蛋，要做到漂亮好吃](https://www.bilibili.com/video/BV1PW411T7YB/) — Creator title/description identifies tomato-and-egg as a home dish and emphasises appearance and avoiding errors. Access: indexed primary title/description only; no frames. Limit: Detailed tomato preparation comes from S07/S09, not unseen Bilibili frames.

- **S12** [Victorinox：Sharpen your knife skills](https://www.victorinox.com/en-GB/Sharpen-your-Knife-Skills/cms/sharpen-your-knife-skills/) — Claw stabilisation, guided rocking/slicing, and even slices/strips are described. Access: manufacturer written technique guide. Limit: No quantitative hand speed is reported.

- **S13** [Singh, Das & Das (2016), IJFS 5(1), 22–38](https://iseki-food-ejournal.com/article/69/pdf) — Table 2: potato mean peaks 43.68–61.49 N; carrot 47.90–67.59 N; speeds 20/30/40 mm per minute. Access: primary paper PDF text, pp.24–28 and Table 2 p.32. Limit: Straight 0.952 mm experimental blade, edge angles 15/20/25 degrees and whole specimens; not human kitchen speeds or universal force maxima.

- **S14** [Seattle Ultrasonics：Quantified Knife, Tojiro 8.2 inch](https://seattleultrasonics.com/pages/knife-pages/tojiro-japan-professional-82-chefs-knife) — Five food-cutting trials per knife; sharpness and food resistance are distinct measures. Access: primary experiment page text. Limit: Food labels are graphical and absent from accessible text; do not map unlabelled gram-force numbers to ingredients or use BESS as food-cutting force.

- **S15** [Victorinox REX Peeler 6.0900.1](https://www.victorinox.com/en/Products/Cutlery/Graters-and-Peelers/REX-Peeler/p/6.0900.1) — 110 by 65 by 12 mm, 14 g; straight swivel peeling blade. Access: page text.

- **S16** [Victorinox Chinese Style Chef knife 6.8561.18G](https://www.victorinox.com/en-TW/Products/Cutlery/Chef%27s-Knives/Swiss-Classic-Chinese-Style-Chef%E2%80%99s-Knife/p/6.8561.18G) — 180 mm blade; overall 309 by 85 by 18 mm; net 198 g; straight-edge vegetable slicing knife. Access: page text.

- **S17** [Victorinox wooden cook/carving knife 5.2060.20G](https://victorinox.com.au/products/cooks-carving-knife-1) — 200 mm chef blade; overall 344 by 54 by 19 mm; net 179 g. Access: page text.

- **S18** [IKEA LEGITIM 902.022.68](https://www.ikea.com/ae/en/p/legitim-chopping-board-white-90202268/) — 340 by 240 by 8 mm polyethylene board; packaged mass 0.58 kg. Access: page text.

- **S19** [IKEA KLOCKREN 504.491.77, 5 L](https://www.ikea.com/gb/en/p/klockren-colander-50449177/) — Diameter 240 mm, stable bottom edge, collapsible; package 300 by 230 by 120 mm and 0.41 kg. Access: manufacturer page text. Limit: Expanded height, handle span and base contact diameter are not specified; analysis envelopes below are engineering assumptions.

- **S20** [IKEA BLANDA BLANK 200.572.55, 20 cm](https://www.ikea.com/gb/en/p/blanda-blank-serving-bowl-stainless-steel-20057255/) — Diameter 200 mm, height 90 mm, capacity 1.6 L; packaged mass 0.22 kg. Access: page text.

- **S21** [IKEA BLANDA BLANK 401.796.99, 28 cm](https://www.ikea.com/sg/en/p/blanda-blank-serving-bowl-stainless-steel-40179699/) — Diameter 280 mm, height 130 mm, capacity 5.4 L; packaged mass 0.57 kg. Access: page text.

- **S22** [OXO Good Grips Y-Peeler 21081](https://www.oxo.com/shop/kitchenware/utensils/y-peeler.html) — 152.4 by 76.2 by 25.4 mm; wet non-slip handle and potato-eye scoop. Access: manufacturer page text. Limit: The displayed weight field has no number; 0.10 kg below is our conservative budget, not a published net mass.

- **S23** [OXO Chef mandoline 2.0, 11194500](https://www.oxo.com/chef-s-mandoline-slicer-2-0.html) — 406.4 by 177.8 by 158.75 mm; settings in 0.5 mm increments; straight and julienne blades. Access: manufacturer page text. Limit: No numeric weight or guaranteed 2–3 mm julienne width in accessible text; budget and sample verification are required.

- **S24** [OXO UK Salad Spinner 1351580](https://www.oxouk.com/products/salad-spinner/) — 266 by 266 by 152 mm, packaged 1.7 kg, 6.2 L bowl/4.2 L basket; push pump, brake and non-slip base. Access: page text.

- **S25** [SEDAL SN-35 S/D 08SN35S5001 technical sheet](https://sedal.com/pdfs/ENGLISH/TDS08SN35S5001.pdf) — Open/close and left/right operating torque 0.20–0.30 Nm; opening angle 25 degrees; separate assembly tightening torque 10–12 Nm. Access: indexed primary manufacturer PDF text, revision 5 dated 2024-05-24; direct PDF open unavailable. Limit: A sourced cartridge-family proxy, not a measured rating for the unidentified T02 faucet.

All sources accessed 2026-10-05. Reference measurements are paraphrased; raw video subtitles, comments and full page captures are not republished. Local T02 scene/fixture records are additional provenance and are not counted among the 25 evidence URLs.
