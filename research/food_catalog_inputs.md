# Food catalog inputs: ingredient sizes, damage thresholds, friction and stiffness

Compiled 2026-10-11 by read-only web research for the robot_rail food-prep gripper (UR5e + 2-jaw parallel gripper, soft pads ~20 × 40 mm). Companion machine-readable file: `food_catalog_inputs.json` (same data, SI units, one object per ingredient, every number paired with a source key or `estimate`/`derived`).

**Tags.** [M] = the number was measured in the cited source. [O] = other: cited second-hand, a review, a standard's class limit, a retailer page, or an abstract seen only via a search snippet. `derived` = my arithmetic from a sourced number (method stated). `estimate` = my judgement (method stated). `not found` = searched, nothing usable.

**How to read the damage column.**
- In a two-plate (or plate-and-probe) compression test, each plate pushes on the sample with the full measured force F. A two-finger pinch is the same load case, so **per-finger squeeze = test force F** (not F/2). I use this conversion throughout.
- A "damage threshold" here is the lowest sourced force at which the source reports damage onset: bio-yield, bruise, crack, rupture, or loss of shelf life. Where only rupture/failure is known, that is an **upper bound**, not a safe value, and is marked as such.
- Where only a stress (kPa) is available, I multiply by the contact area: the full pad (20 × 40 mm = 800 mm²) for flat-faced items such as tofu, meat and fillets, and an assumed **200 mm²** (a 10 × 20 mm patch) for curved produce, unless a row says otherwise. These are marked `derived`. The 200 mm² is my estimate; a stiffer pad or smaller item gives less area and a lower force.
- Each ingredient gets one settled **Limit** (per-finger N) and, where known, a **Failure** force. The Limit is, in order of preference: (1) a measured onset or safe value; (2) a value derived from a measured stress as above; (3) an `estimate` by one of two stated rules: for soft fleshy produce, 0.13 × failure (0.13 = tomato non-destructive limit / rupture force, 11.13 / 83.5 N, the only rig in this catalog that measured both); for firm, robust items, failure / 2; (4) a labelled proxy or judgement. The basis is written next to every Limit.
- Most onset criteria in the literature are cosmetic or shelf-life based (bruise volume, 9-day shelf life). This robot washes and cuts the food within minutes, so those limits are conservative; the Failure column is the hard limit (crack, rupture, crush).
- Plate/probe forces were measured at quasi-static speeds (typically 10–60 mm/min). Fast closing adds an impact component that the thresholds do not include. Strawberry bruising also grows with hold time (2 s vs 5 s).
- For simulation pass/fail, apply your own safety factor to these thresholds; I have not built one in.
- Context: the current gripper (DECISIONS.md R12) is a PGC-140-50 whose force mode cannot go below 40 N per jaw. Every Limit below 40 N needs position-limited closing or compliant fingers, as R12 already does for tomato.

**How to read the friction column.** Values are static coefficients unless marked kinetic. The counter-material is stated per row because it matters as much as the food; several values (Qiu 2023, Q23) come from a commercial tester whose contact material is not stated. "Wet" means the source tested a wet or mucus-covered surface. Only three wet values exist in this catalog (potato on rubber belting, raw chicken fillet on steel, fish with mucus on polypropylene); everything else is dry or as-received. **No source measured any food against wet silicone or TPU.** Where nothing was measured, the JSON gives a labelled `sim_estimate` (0.5 for produce skin and leaves, 0.1 for mucilaginous or slimy surfaces such as peeled yam/taro, tofu, fish and shrimp).

**Hold force** (`hold_force_per_finger_N` in the JSON) = m_max·g / (2·μ). It is the per-finger squeeze needed to keep the heaviest unit from sliding out vertically under gravity alone, using the lowest measured μ (wet or dry), else the sim estimate. m_max is the larger of the sourced and the Chinese-retail-estimate maximum. It is a derived floor: multiply by your dynamic factor (acceleration, tilt, off-centre grasp) and compare it with the Limit to see the grip window.

**Units.** The markdown uses mm, kg, N and Pa. The JSON uses SI throughout (sizes in m).

## 1. Grasp summary (all ingredients)

Limit = the per-finger force I settled on as the damage criterion (type and basis in section 3). Failure = sourced or derived rupture/crush force (upper bound). μ = the lowest measured value available (wet preferred if measured; see section 3 for the counter-material), else my estimate (*est*). Hold = derived per-finger squeeze to hold the heaviest unit by friction alone (SF = 1). Limit/Hold < 2 means a friction pinch has little or no margin.

| Ingredient | Max unit mass kg | Limit N/finger | Failure N | μ (state, src) | Hold N | Limit/Hold |
|---|---|---|---|---|---|---|
| Carrot 胡萝卜 | 0.3 | 56.7 (C1) | 71.9 (C1) | 0.5 (*est*) | 2.94 | 19.3 |
| Potato 马铃薯/土豆 | 0.4 | 40 (derived) | – | 0.35 (dry, P1) | 5.61 | 7.1 |
| Daikon (white radish) 白萝卜 | 2 | 40 (estimate) | – | 0.5 (*est*) | 19.62 | 2.0 |
| Ginger 生姜 | 0.4 | 55 (estimate) | 110.1 (Gi1) | 0.31 (dry, Gi1) | 6.33 | 8.7 |
| Garlic head + clove 大蒜（蒜头/蒜瓣） | 0.08 | 20 (estimate) | 40 (G1) | 0.33 (dry, G1) | 1.19 | 16.8 |
| Onion 洋葱 | 0.4 | 170 (estimate) | 341 (O1) | 0.67 (dry, O1) | 2.93 | 58.0 |
| Lotus root (segment) 莲藕 | 0.88 | 64 (estimate) | 128 (derived) | 0.5 (*est*) | 8.63 | 7.4 |
| Chinese yam 山药（铁棍山药/菜山药） | 1.5 | 40 (estimate) | – | 0.1 (*est*) | 73.57 | 0.5 |
| Taro (small corm) [added] 芋头（毛芋头） | 0.12 | 140 (estimate) | 1121 (TA1) | 0.2 (dry, TA1) | 2.94 | 47.6 |
| Corn cob (fresh, husked) 鲜玉米 | 0.45 | 50 (estimate) | – | 0.5 (*est*) | 4.41 | 11.3 |
| Apple 苹果 | 0.35 | 112.5 (A1) | – | 0.85 (dry, APL15) | 2.02 | 55.7 |
| Pumpkin / winter melon piece 南瓜/冬瓜（切块） | 2 | 50 (estimate) | – | 0.5 (*est*) | 19.62 | 2.5 |
| Tomato 番茄/西红柿 | 0.3 | 11.13 (T1) | 83.5 (T1) | 1.41 (dry, T1) | 1.04 | 10.7 |
| Cherry tomato 樱桃番茄/圣女果 | 0.025 | 1.5 (estimate) | – | 0.44 (dry, Q23) | 0.28 | 5.4 |
| Cucumber 黄瓜 | 0.4 | 19 (estimate) | 148 (derived) | 1.02 (dry, Q23) | 1.92 | 9.9 |
| Chinese long eggplant 长茄子 | 0.4 | 10 (estimate) | – | 0.5 (*est*) | 3.92 | 2.6 |
| Bell / green pepper 青椒/甜椒 | 0.25 | 3 (estimate) | – | 1.35 (dry, Q23) | 0.91 | 3.3 |
| Chili (jianjiao / xiaomila) 尖椒/线椒/小米辣 | 0.06 | 3 (estimate) | 24 (derived) | 0.5 (*est*) | 0.59 | 5.1 |
| Zucchini 西葫芦 | 0.8 | 22 (estimate) | 167 (ZU1) | 0.5 (*est*) | 7.85 | 2.8 |
| Strawberry 草莓 | 0.05 | 0.6 (S3) | 9.8 (S1) | 0.57 (dry, Q23) | 0.43 | 1.4 |
| Green beans / long beans 四季豆/豇豆 | 0.03 | – | – | 0.5 (*est*) | 0.29 | – |
| Bean sprouts 绿豆芽/黄豆芽 | 0.5 | – | – | 0.5 (*est*) | 4.91 | – |
| Bok choy (Shanghai qing) 上海青/小油菜 | 0.118 | 12.2 (BC2) | – | 0.65 (dry, BC1) | 0.89 | 13.7 |
| Cabbage (head) 卷心菜/结球甘蓝 | 2.27 | – | 1198 (CB1) | 0.5 (*est*) | 22.27 | – |
| Napa cabbage 大白菜 | 5 | – | 820.3 (NC1) | 0.5 (*est*) | 49.05 | – |
| Broccoli 西兰花 | 0.6 | 175 (estimate) | 350 (BR3) | 0.5 (*est*) | 5.89 | 29.7 |
| Celery 芹菜/西芹 | 2.094 | 12 (estimate) | – | 0.5 (*est*) | 20.54 | 0.6 |
| Scallion (xiaocong) / Welsh onion (dacong) 小葱/大葱 | 0.5 | 16.5 (estimate) | 33 (derived) | 0.5 (*est*) | 4.91 | 3.4 |
| Chinese chives 韭菜 | 0.5 | 140 (CV1) | – | 0.5 (*est*) | 4.91 | 28.5 |
| Spinach 菠菜 | 0.08 | 2.2 (LE1) | – | 0.5 (*est*) | 0.78 | 2.8 |
| Lettuce 生菜 | 0.6 | 2.2 (LE1) | – | 0.5 (*est*) | 5.89 | 0.4 |
| Shiitake 香菇 | 0.04 | 42 (derived) | – | 0.5 (*est*) | 0.39 | 107.7 |
| Enoki 金针菇 | 0.2 | – | – | 0.5 (*est*) | 1.96 | – |
| King oyster mushroom 杏鲍菇 | 0.15 | 84 (estimate) | – | 0.5 (*est*) | 1.47 | 57.1 |
| Chicken egg (in shell) 鸡蛋 | 0.065 | 10 (EGG2) | 38 (EGG3) | 0.47 (dry, EGG6) | 0.68 | 14.7 |
| Tofu, silken 嫩豆腐/内酯豆腐 | 0.5 | 3 (derived) | – | 0.1 (*est*) | 24.52 | 0.1 |
| Tofu, firm 老豆腐/北豆腐 | 0.5 | 15 (derived) | – | 0.1 (*est*) | 24.52 | 0.6 |
| Chicken breast (raw) 鸡胸肉 | 0.35 | 56 (derived) | – | 0.5 (wet, CK1) | 3.43 | 16.3 |
| Pork (lean chunk / belly) 猪肉（瘦肉块/五花肉） | 1 | 56 (estimate) | – | 0.5 (*est*) | 9.81 | 5.7 |
| Whole fish (sea bass) 鲈鱼（整条） | 1 | – | – | 0.12 (wet, FI1) | 40.88 | – |
| Fish fillet 鱼片/鱼柳 | 0.3 | – | – | 0.1 (*est*) | 14.71 | – |
| Shrimp (shell-on, raw) 虾（带壳，白虾/基围虾） | 0.033 | – | – | 0.1 (*est*) | 1.62 | – |

## 2. Size, shape and how it arrives

Sourced sizes are often from non-Chinese cultivars (noted). The last column is my estimate of a typical Chinese retail unit, used only where the sourced unit is missing or clearly unrepresentative. All "arrives as" entries are my estimate (common knowledge), not sourced.

| Ingredient | Shape | Arrives as | Sourced size, mm (min–typ–max) | Sourced mass, kg | CN retail estimate, kg (size) |
|---|---|---|---|---|---|
| Carrot | tapered cylinder (cone) | loose, or 0.5-1 kg plastic bag; washed | length 121–155–185 (C1); max diameter 23–29–34 (C1) | 0.045–0.073–0.115 (C1) | 0.1–0.15–0.3 (L 150-250 mm, D 30-50 mm) |
| Potato | ellipsoid | loose (often soil-dusted) or net bag | length 50–70–87 (P1); width 46–62–69 (P1); thickness 40–52–58 (P1) | 0.068–0.132–0.221 (P1) | 0.1–0.2–0.4 (L 70-140 mm) |
| Daikon (white radish) | long cylinder | loose, sometimes halved and cling-wrapped | not found | not found | 0.5–1–2 (L 200-450 mm, D 60-100 mm) |
| Ginger | branched rhizome ('hand') | loose, irregular pieces | piece size classes 35–50 (Gi1) | not found | 0.05–0.15–0.4 (hand 80-200 mm long) |
| Garlic head + clove | head: oblate sphere of cloves; clove: crescent wedge | loose heads, or net bag of 3-5 heads | not found | not found | 0.03–0.05–0.08 (head D 45-65 mm; clove 3-10 g, 25-35 mm long) |
| Onion | oblate sphere | loose or net bag | diameter (equatorial/polar) 51–57–62 (O1) | 0.079–0.097–0.115 (O1) | 0.15–0.25–0.4 (D 70-100 mm) |
| Lotus root (segment) | sausage-shaped segment with axial air channels | loose segments, often mud-coated, or cling-wrapped washed pieces | segment length 98–160–239 (L1); width 63–75–91 (L1); height 58–70–86 (L1) | 0.17–0.4–0.88 (derived) | – |
| Chinese yam | long thin cylinder, slightly club-shaped | loose, often in a long box or cut to length; hairy skin | not found | not found | 0.15–0.4–1.5 (tie-gun type L 500-1000 mm, D 20-40 mm; cai-shanyao L 400-900 mm, D 40-80 mm) |
| Taro (small corm) [added] | ovoid, hairy fibrous skin | loose, soil-coated | length 52–85–118 (TA1); width 32–35–39 (TA1) | ~0.076 (TA1) | 0.03–0.06–0.12 (mao-yutou cormels; Lipu taro 1-2 kg is a different product) |
| Corn cob (fresh, husked) | tapered cylinder | loose, husk-on or husked in a 2-3 ear tray | length 189–260–280 (CN1); base diameter 43–55–66 (CN1) | not found | 0.2–0.3–0.45 (husked ear) |
| Apple | sphere | loose, or foam-net sleeve in tray | equatorial diameter 75–78–80 (A1) | not found | 0.18–0.25–0.35 (D 75-90 mm (Fuji)) |
| Pumpkin / winter melon piece | wedge or block cut from a large fruit, rind on one face | cling-wrapped cut piece on a foam tray, sold by weight | not found | not found | 0.5–1–2 (piece 100-250 mm; whole pumpkin 1-3 kg) |
| Tomato | oblate sphere | loose, or 4-6 in a tray | equatorial diameter 64–75–90 (T1) | not found | 0.12–0.18–0.3 (D 60-90 mm) |
| Cherry tomato | sphere / short ellipsoid | loose in a clamshell box or bag (~300-500 g) | diameter 24–26–28 (Q23) | 0.012–0.0125–0.013 (Q23) | 0.01–0.015–0.025 (D 20-35 mm) |
| Cucumber | long cylinder, bumpy/spiny skin (mici type) | loose, or 2-3 in a cling-wrapped tray | length class (S/M/L) 110–220–280 (CU1); diameter 20–24–28 (Q23) | 0.089–0.11–0.129 (Q23) | 0.15–0.25–0.4 (L 200-350 mm, D 30-45 mm) |
| Chinese long eggplant | long curved cylinder, glossy skin, spongy flesh, prickly calyx | loose | length (Japanese mid-size) 125–155–185 (EG1) | not found | 0.15–0.25–0.4 (L 250-400 mm, D 40-65 mm) |
| Bell / green pepper | hollow blocky or conical shell, 3-4 lobes | loose | size 46–50–54 (Q23) | 0.033–0.035–0.038 (Q23) | 0.08–0.15–0.25 (D 60-90 mm) |
| Chili (jianjiao / xiaomila) | long thin cone, hollow | loose, or small bag/tray (xiaomila) | length 172–178–185 (CH1); diameter (mid) 12–16–20 (CH1) | 0.012–0.023–0.034 (CH1) | 0.002–0.03–0.06 (xiaomila 2-8 g, L 30-70 mm; jianjiao 20-60 g) |
| Zucchini | cylinder | loose | length ~112 (ZU1); diameter ~34 (ZU1) | ~0.081 (ZU1) | 0.3–0.5–0.8 (L 180-350 mm, D 50-80 mm) |
| Strawberry | cone/heart, seeds on surface, calyx on top | single layer in a plastic clamshell box (250-500 g) | size 25–26–28 (Q23) | 0.014–0.016–0.02 (Q23) | 0.015–0.025–0.05 (D 25-45 mm) |
| Green beans / long beans | thin pods; long beans 300-700 mm, flexible | loose heap or banded bundle | not found | not found | 0.005–0.01–0.03 (sijidou pod L 100-200 mm, 5-12 g; jiangdou L 300-700 mm, 10-30 g; bunch 0.25-0.5 kg) |
| Bean sprouts | thin brittle hypocotyls with bean heads, bulk | loose bulk or 250-500 g bag | hypocotyl length (soybean sprout) 86–90–99 (BS1); hypocotyl thickness 2.1–2.3–2.5 (BS1) | not found | 0.25–0.4–0.5 (bag mass) |
| Bok choy (Shanghai qing) | vase-shaped rosette, thick spoon-shaped petioles at the base | loose heads or 3-5 in a bag | plant length 160–177–185 (BC1); root diameter 7.9–9–10.8 (BC1) | 0.073–0.09–0.118 (BC1) | – |
| Cabbage (head) | sphere / flattened sphere | loose heads, sometimes halved and cling-wrapped | vertical diameter 135–162–190 (CB1); transverse diameter 140–164–185 (CB1) | 1.24–1.91–2.27 (CB1) | – |
| Napa cabbage | elongated head | loose heads; halves/quarters cling-wrapped | diameter 148–155–162 (NC1); height 138–164–190 (NC1) | 2.35–2.77–3.18 (NC1) | 1.5–3–5 (winter napa 300-450 mm tall) |
| Broccoli | dome of florets on a thick stem | loose head, often cling-wrapped; wholesale in foam box with ice | curd diameter grade 120–150–170 (BR1); stem diameter ≤42 (BR2) | not found | 0.25–0.4–0.6 (head) |
| Celery | bunch of long petioles | banded bunch or whole plant | plant length 476–740–819 (CE1) | 0.309–1.5–2.094 (CE1) | 0.3–0.5–1 (local qincai bunch) |
| Scallion (xiaocong) / Welsh onion (dacong) | hollow tubular leaves on a white shaft | banded bunch (xiaocong) or single long stalks (dacong) | not found | not found | 0.1–0.2–0.5 (xiaocong bunch 0.1-0.25 kg (single stalk 5-20 g); dacong single stalk 0.15-0.5 kg, L 500-700 mm) |
| Chinese chives | flat narrow leaves, banded bunch | banded bunch (ba) | bundle diameter (harvester feed) 5–15–25 (CV1) | not found | 0.25–0.4–0.5 (retail bunch, leaves 250-400 mm) |
| Spinach | rosette with red crown and taproot | banded bunch | not found | not found | 0.02–0.04–0.08 (single plant; bunch 0.25-0.5 kg) |
| Lettuce | loose-leaf rosette or head | loose plant, often in a bag | height / leaf spread 86.5–195.3 (LE1) | not found | 0.2–0.4–0.6 (plant/head) |
| Shiitake | cap (umbrella) on short stipe | loose, or 150-300 g foam tray, cling-wrapped | cap diameter 50–62–74 (SH1); cap height 17–21–25 (SH1); stipe diameter 10.6–13.2–15.8 (SH1); stipe height 27–33–38 (SH1) | not found | 0.015–0.025–0.04 () |
| Enoki | cluster of thin long stems joined at a base block | sealed plastic bag (~100-200 g) | not found | not found | 0.1–0.15–0.2 (bag, L 120-150 mm) |
| King oyster mushroom | thick cylindrical stem, small cap | 2-4 in a cling-wrapped tray or bag | not found | not found | 0.04–0.08–0.15 (L 100-200 mm, D 30-60 mm) |
| Chicken egg (in shell) | ovoid | pulp or plastic egg tray (6/10/30) | length ~58 (EGG2); width ~45.5 (EGG2) | 0.044–0.055–0.065 (EGG1) | – |
| Tofu, silken | rectangular block in water-filled sealed box | sealed plastic box (often with water) | not found | not found | 0.3–0.4–0.5 (box ~ 100 x 100 x 50-60 mm) |
| Tofu, firm | rectangular block | box with water, or loose block on a tray at wet markets | not found | ~0.4 (TF3) | 0.25–0.4–0.5 (block ~ 100 x 80 x 40-60 mm) |
| Chicken breast (raw) | flattened teardrop fillet | chilled tray, 2-3 pieces, cling-wrapped | length 144–172–176 (CK1); width ~72 (CK1); thickness 32–40–40 (CK1) | not found | 0.15–0.25–0.35 (single fillet) |
| Pork (lean chunk / belly) | irregular block / slab (belly layered fat-lean-skin) | chilled tray or loose at the butcher | not found | not found | 0.2–0.5–1 (chunk or belly strip) |
| Whole fish (sea bass) | fusiform body, scales, mucus | live from tank or chilled on ice; scaled/gutted at the stall | body length 336–352–367 (FI3); body height 93–96–100 (FI3) | not found | 0.4–0.6–1 (whole fish) |
| Fish fillet | flat slab, skin-on or skinless | chilled tray | not found | not found | 0.1–0.2–0.3 (fillet) |
| Shrimp (shell-on, raw) | curved segmented body, antennae, legs | live in water, chilled on ice, or frozen block | length 70–75–80 (SR1) | 0.011–0.012–0.033 (SR1) | – |

## 3. Evidence per ingredient

Each block: the settled limit with its basis, friction, stiffness, then the sourced evidence rows. Tags: [M] measured in source, [O] other.

### Carrot (胡萝卜)
- **Limit:** 56.7 N per finger — bruise (min of n=100) [C1]. lowest bruising force; round probe, 20 mm/min; occurs at 17-22 mm deformation so it is near failure, not a cosmetic onset
- **Failure:** 71.9 N [C1] — mean bruising force, same test
- **Friction:** no measured value; sim estimate 0.5 (estimate: middle of the measured dry produce values in this catalog on rubber/TPU/silicone/steel (0.33-1.41); no wet data)
- **Stiffness:** 38 kPa — apparent whole-root modulus (bruising test) - far below typical fresh-tissue values, use with care [C1]
- **Handling:** Robust. Grasp mid-length across the diameter; tapered shape slides toward the tip under squeeze, so use a V or concave pad. Thin tip snaps in bending (48.6 N 3-point).

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| bruising force | 56.7-92.3 N, mean 71.90 N; deformation 17.4-21.7 mm | round pressure probe, 20 mm/min | [M] | C1 |
| bending / shear force | 48.6 N (3-point) / 41.1 N | 20 mm/min | [M] | C1 |
| density, moisture | 1.04 g/cm3, 87.2 % |  | [M] | C1 |
| friction | not found |  |  |  |

### Potato (马铃薯/土豆)
- **Limit:** 40 N per finger — derived [derived]. 0.20 MPa critical contact stress (P2, drop impact, pressure film) x assumed 200 mm2 effective contact on a curved tuber; full-pad 800 mm2 would give 160 N
- **Friction:** wet 0.65 — kinetic, rubber belting, clean-wet tuber (Cara) [F2]; dry 0.35 — static, rubber, unpeeled (min of Marfona/Sante classes) [P1]
- **Stiffness:** 1.9 MPa — flesh, 10 mm probe punch on peeled halves (1.81-2.11 MPa) [P1]
- **Handling:** Robust. Peeled potato: surface starch/water film; sources say friction rises after peeling (dry test) - wet peeled friction not measured.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| critical damage contact stress | 0.20 MPa | drop impact, pressure-sensitive film | [M] | P2 |
| drop damage onset | 300 mm onto 65Mn steel; 400 mm onto ABS/rubber/soil |  | [M] | P2 |
| static mu | rubber 0.35-0.53; galvanized iron 0.31-0.34; aluminium 0.37-0.42; glass 0.35-0.45 | tilting plate, dry, unpeeled | [M] | P1 |
| kinetic mu (rubber belting) | ~0.66 clean-dry, ~0.65 clean-wet, ~0.62 wet-dirty | Cara 50-64 mm, read from bar chart | [M] | F2 |
| peeled vs unpeeled | peeled tubers have higher sliding friction | cited Dalvand 2011 | [O] | P1 |

### Daikon (white radish) (白萝卜)
- **Limit:** 40 N per finger — estimate [estimate]. no data; set below carrot (56.7 N) because daikon flesh is softer and juicier
- **Friction:** no measured value; sim estimate 0.5 (estimate: middle of the measured dry produce values in this catalog on rubber/TPU/silicone/steel (0.33-1.41); no wet data)
- **Stiffness:** not found
- **Handling:** Too wide for most 2-jaw strokes when whole (60-100 mm); usually bought or handled as a cut section. Long whole root needs a 2-point or cradle grasp.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| compression, modulus, friction, size | not found (Koide 2005 Biosyst Eng 92:335 abstract has no numbers) |  |  |  |

### Ginger (生姜)
- **Limit:** 55 N per finger — estimate [estimate]. failure/2: compression 110.06 N (lowest, Gi1, geometry not stated) / 2
- **Failure:** 110.1 N [Gi1] — compression 110.06-154.25 N, geometry not stated
- **Friction:** dry 0.31 — static, stainless steel (lowest surface) [Gi1]
- **Stiffness:** not found
- **Handling:** Irregular branched shape: grasp the thickest lobe. Peel tears at very low force (0.45 N penetration) - cosmetic only, since it is peeled.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| compression | 110.06-154.25 N | geometry not in abstract | [M] | Gi1 |
| penetration / cutting | 12.70-15.06 N / 218.5-252.7 N |  | [M] | Gi1 |
| peel penetration | 0.45-0.52 N | fresh fingers | [M] | Gi2 |
| peel rupture under compression | 17.56-20.12 N | seen only in a search snippet - unverified | [O] | Gi2 |

### Garlic head + clove (大蒜（蒜头/蒜瓣）)
- **Limit:** 20 N per finger — estimate [estimate]. head: failure/2 = 40 N/2 (G1 horizontal peak, lowest); clove: 28 N/2 = 14 N
- **Failure:** 40 N [G1] — head horizontal peak 40-65 N; vertical 80-110 N; clove ~28 N (P/75 platen, 0.5 mm/s)
- **Friction:** dry 0.33 — static, stainless steel, head (clove 0.35) [G1]
- **Stiffness:** not found
- **Handling:** Clove is small (3-10 g) and smooth; papery skin flakes. Loose cloves are better handled in a container/tray than pinched one by one.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| head compression peak | vertical 80-110 N (~93.5 N); horizontal 40-65 N (~52 N) | 75 mm platen (P/75), 0.5 mm/s | [M] | G1 |
| clove compression peak | ~28.05 N | same | [M] | G1 |
| clove crushing load (other study) | 55.6-155.0 N | cited Bahnasawy 2007 | [O] | G1 |
| static mu head / clove | stainless 0.33/0.35; mild steel 0.43/0.46; glass 0.24/0.27; wood 0.51/0.54 | tilting table, dry | [M] | G1 |

### Onion (洋葱)
- **Limit:** 170 N per finger — estimate [estimate]. failure/2 = 341 N/2; above the 140 N max of a PGC-140, so not limiting
- **Failure:** 341 N [O1] — crushing load 341-981 N (small red bulbs lowest), dead weights on flat plate until permanent destruction
- **Friction:** dry 0.67 — static, galvanized steel (rubber 0.69-1.30, bulk test) [O1]
- **Stiffness:** not found
- **Handling:** Robust. Dry outer skin flakes and can slip off the bulb - grip through the flesh layers, not loose skin.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| crushing load | white 443/677/820 N; red 341/803/981 N; yellow 400/679/780 N (S/M/L) | flat plate, dead weights | [M] | O1 |
| penetration | 26.1-45.5 N | 3 mm flat probe | [M] | O1 |
| static mu | rubber 0.69-1.30; galvanized steel 0.67-1.01; plywood 0.71-1.34 | tilting frame filled with bulbs; text vs table ranking inconsistent | [M] | O1 |

### Lotus root (segment) (莲藕)
- **Limit:** 64 N per finger — estimate [estimate]. failure/2: flesh compressive strength 0.64 MPa (L2 min) x 200 mm2 = 128 N (derived) / 2
- **Failure:** 128 N [derived] — 0.64 MPa (L2 outer flesh, 15 mm flat indenter) x 200 mm2 assumed contact
- **Friction:** no measured value; sim estimate 0.5 (estimate: middle of the measured dry produce values in this catalog on rubber/TPU/silicone/steel (0.33-1.41); no wet data)
- **Stiffness:** not found
- **Handling:** Width 60-90 mm exceeds a 50 mm stroke; grasp along the narrow neck or handle in a cradle. Brittle: cracks diagonally rather than bruising.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| whole-section indentation | max 58.6-89.3 N (2.98-4.54 MPa) | 5 mm cylindrical indenter, 10 mm/min | [M] | L2 |
| flesh compressive strength | 0.64-1.20 MPa (axial) | 15 mm flat indenter, 4 mm, 10 mm/min; brittle diagonal cracks | [M] | L2 |
| bending / tensile | min 97 N / min 182.7 N | 10 mm/min | [M] | L2 |
| skin peeling cutting force | 9.13-12.88 N | texture analyser | [M] | L1 |
| segment size (other cvs) | 87x50x44 mm to 132x64x55 mm (first section) |  | [M] | L2 |

### Chinese yam (山药（铁棍山药/菜山药）)
- **Limit:** 40 N per finger — estimate [estimate]. no data for Dioscorea opposita; judgement. Main risk is snapping in bending, not crushing
- **Friction:** no measured value; sim estimate 0.1 (estimate: between fish-mucus values on polypropylene (snakehead 0.04, carp 0.12-0.14, FI1); mucilage/slime acts as a lubricant)
- **Stiffness:** not found
- **Handling:** Do NOT pinch peeled yam: mucilage makes it near-frictionless (estimate mu ~0.1) and the long thin tuber snaps. Grasp unpeeled (hairy skin), cut to length first, or carry peeled pieces in a tray/chute. Mucilage also irritates skin and fouls pads - wash pads.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| mechanics of D. opposita | not found |  |  |  |
| proxy: Nigerian yams/cocoyam | compressive 0.609-2.354 kN, tensile 0.091-0.822 kN; unit 41-1170 g | different species, geometry not stated | [M] | Y1 |
| peeled mucilage friction | not found; mucilage is a mannan-protein complex (viscosity source) - qualitative |  |  |  |

### Taro (small corm) [added] (芋头（毛芋头）)
- **Limit:** 140 N per finger — estimate [estimate]. failure 1121 N (TA1) far above gripper max - not limiting
- **Failure:** 1121 N [TA1] — average compressive force, geometry not stated
- **Friction:** dry 0.2 — static, stainless steel (wood/glass/galvanized 0.21) [TA1]
- **Stiffness:** 11.98 MPa — Young's modulus as reported (N/mm2) [TA1]
- **Handling:** Like yam: peeled taro is slimy and irritant - do not pinch peeled; dry unpeeled is already low-friction (0.20).

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| compressive force / toughness | 1121.08 N / 6.89 N m |  | [M] | TA1 |
| static mu | stainless 0.20; wood, glass, galvanized 0.21 | dry, unpeeled | [M] | TA1 |

### Corn cob (fresh, husked) (鲜玉米)
- **Limit:** 50 N per finger — estimate [estimate]. no data; judgement (kernels burst under concentrated load)
- **Friction:** no measured value; sim estimate 0.5 (estimate: middle of the measured dry produce values in this catalog on rubber/TPU/silicone/steel (0.33-1.41); no wet data)
- **Stiffness:** not found
- **Handling:** Bumpy kernel surface gives good mechanical interlock; grasp near the butt end.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| ear size | L 260-280 mm, D 64-66 mm, moisture 66.5-69 % | husk-on, peeling-machine test material | [M] | CN1 |
| ear size | L 189 mm, base D 45 mm, kernel moisture 70 % |  | [M] | CN2 |
| compression, friction, mass | not found |  |  |  |

### Apple (苹果)
- **Limit:** 112.5 N per finger — internal damage onset [A1]. Red Fuji whole fruit, 65 mm flat cylindrical indenter, 2 mm/s; damage after ~100 N mm absorbed energy
- **Friction:** dry 0.85 — static, silica gel (TPU rubber 0.88 +/- 0.03, A2) [APL15]
- **Stiffness:** 5 MPa — flesh (Fuji min 5.0 MPa, A2; 3-5 MPa A3) [A2]
- **Handling:** Robust to squeeze; bruises from impact/drop rather than slow grip.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| internal damage onset | 112.5 N; elastic below 2.3 mm | 65 mm flat indenter, 0.1-8 mm/s | [M] | A1 |
| flesh E / yield / compressive strength | 5.0 / 2.2 / 2.4 MPa (min) | Fuji | [M] | A2 |
| flesh failure stress / strain | ~0.40-0.47 MPa / ~0.15 | 20x20 mm cylinders | [M] | A3 |
| static mu | TPU rubber 0.88 +/- 0.03; aluminium 0.14 | Fuji, dry | [M] | A2 |
| static mu | 0.848 vs silica gel | push-pull gauge tester; table has odd negative entries - low quality | [M] | APL15 |

### Pumpkin / winter melon piece (南瓜/冬瓜（切块）)
- **Limit:** 50 N per finger — estimate [estimate]. no data; firm flesh, judgement
- **Friction:** no measured value; sim estimate 0.5 (estimate: middle of the measured dry produce values in this catalog on rubber/TPU/silicone/steel (0.33-1.41); no wet data)
- **Stiffness:** not found
- **Handling:** Grip rind-to-cut-face across the thinnest dimension; winter melon cut face is wet and slippery, rind is waxy.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| anything | not found |  |  |  |

### Tomato (番茄/西红柿)
- **Limit:** 11.13 N per finger — non-destructive clamp limit [T1]. shelf life >= 9 days; Dia 50 mm flat probe faced with 3 mm Dragon Skin 30 on a 3 mm DS30 pad, 30 mm/min; reached at ~4 % compression
- **Failure:** 83.5 N [T1] — rupture 83.5-147.9 N, same rig
- **Friction:** dry 1.41 — static, Dragon Skin 30 silicone, moisture not stated [T1]
- **Stiffness:** not found
- **Handling:** Grip at the equator with a concave soft pad; already covered in finger_design_inputs.md (R12: ~5 N position-mode grasp).

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| compression force | 1 %: 3.0-4.0 N; 4 %: 8.3-11.1 N; 6 %: 10.2-19.5 N; 15 %: 34-48 N | same rig | [M] | T1 |
| design guideline | < 10 N per finger, 30 mm wide finger | FEA, cites deformation < 1.5 mm elastic | [M] | T2 |
| working grasp force | 0.20-0.50 N (set 0.30 N) | TPU 95A auxetic fingers, tomatoes 43-57 mm, 40-81 g | [M] | T6 |
| static mu | 1.41 (1.15-1.79) vs Dragon Skin 30 | pull test 30 mm/min | [M] | T1 |

### Cherry tomato (樱桃番茄/圣女果)
- **Limit:** 1.5 N per finger — estimate [estimate]. Hertz scaling of the tomato limit (11.13 N at 4 % compression, Dia 75 mm) to Dia 28 mm at equal strain and modulus gives ~1.6 N; a UR5e harvesting study started at 1.2 N (+0.3 N steps) without bruising (CT1)
- **Friction:** dry 0.44 — static, counter-surface not stated (range 0.44-0.65) [Q23]
- **Stiffness:** 0.41 MPa — single measurement, curve-fit [Q23]
- **Handling:** Small and light (12-13 g): bulk-handle in a basket/colander; if picked singly, use position-limited closing.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| working grip force | start 1.2 N, +0.3 N per retry; success = detached without bruising | gel-pad tactile gripper on UR5e | [M] | CT1 |
| rupture trend | green > ripe; axial > radial; no numbers in abstract |  | [M] | CT2 |
| static mu | 0.44-0.65 | TL201Tt tester | [M] | Q23 |

### Cucumber (黄瓜)
- **Limit:** 19 N per finger — estimate [estimate]. 0.13 x derived failure 148 N (0.13 = tomato onset/rupture ratio 11.13/83.5)
- **Failure:** 148 N [derived] — slice fracture stress near skin > 0.74 MPa (CU2) x 200 mm2 assumed contact
- **Friction:** dry 1.02 — static, counter-surface not stated (1.02-1.23) [Q23]
- **Stiffness:** 0.987 MPa — single measurement, curve-fit [Q23]
- **Handling:** Grasp mid-length; spines (mici type) aid grip but break off. Long thin fruit bends - keep grasp near the centre of mass.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| slice fracture | fracture at ~0.3 strain; stress > 0.74 MPa near skin, 0-0.39 MPa in seed cavity | 10 mm slices, Instron 1 mm/s | [M] | CU2 |
| storage | firmness/E/failure stress/energy fall 49/39/38/33 % | Viola | [M] | CU3 |
| static mu | 1.02-1.23 | TL201Tt tester | [M] | Q23 |

### Chinese long eggplant (长茄子)
- **Limit:** 10 N per finger — estimate [estimate]. no compression data; set like tomato (11 N) because both are soft-skinned and dent visibly
- **Friction:** no measured value; sim estimate 0.5 (estimate: middle of the measured dry produce values in this catalog on rubber/TPU/silicone/steel (0.33-1.41); no wet data)
- **Stiffness:** not found
- **Handling:** Spongy flesh dents permanently; calyx has prickles. Grasp mid-body with wide pads; very long fruit needs grasp near centre of mass.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| penetration hardness | 1644 g (16.1 N) fresh -> 1433 g after 10 days | round eggplant, CT3 texture analyser, probe not stated, n=2/day | [M] | EG3 |
| gripper damage | 10 'Negra alargada' fruits held by a parallel pneumatic gripper: 1 slightly damaged, no skin cuts (force not given) |  | [M] | EG2 |
| flesh modulus, friction | not found |  |  |  |

### Bell / green pepper (青椒/甜椒)
- **Limit:** 3 N per finger — estimate [estimate]. no data; proxy = chili 'Round pepper' wall failure 24 N (derived) x 0.13. Likely conservative for thick-walled bell peppers
- **Friction:** dry 1.35 — static, counter-surface not stated (1.35-1.53) [Q23]
- **Stiffness:** 0.166 MPa — single measurement, curve-fit [Q23]
- **Handling:** Hollow shell: walls buckle and crack; grasp across the shoulders near the stem, not mid-wall. MAJOR GAP - measure.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| compression / damage | not found |  |  |  |
| static mu | 1.35-1.53 | TL201Tt tester | [M] | Q23 |

### Chili (jianjiao / xiaomila) (尖椒/线椒/小米辣)
- **Limit:** 3 N per finger — estimate [estimate]. 0.13 x derived failure 24 N
- **Failure:** 24 N [derived] — radial compressive strength 0.1216 MPa (Round, CH1) x 200 mm2; Bo 15 0.2507 MPa -> 50 N
- **Friction:** no measured value; sim estimate 0.5 (estimate: middle of the measured dry produce values in this catalog on rubber/TPU/silicone/steel (0.33-1.41); no wet data)
- **Stiffness:** 0.36 MPa — Round pepper 0.3628 MPa; Bo 15 1.028 MPa [CH1]
- **Handling:** Xiaomila (2-8 g) should be handled in bulk (container). Long chilies: grasp mid-length. Capsaicin contaminates pads - wash.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| radial compressive strength | 0.1216 (Round) / 0.2507 (Bo 15) MPa | segments laid flat, plate 10 mm/min | [M] | CH1 |
| tensile / bending / shear strength | 0.65/0.83; 0.24/0.58; 0.099/0.282 MPa | same | [M] | CH1 |
| grade size (Huaiji pepper) | length >= 8 cm (grade 3: >= 6 cm), width >= 3 cm | group standard | [O] | CH2 |

### Zucchini (西葫芦)
- **Limit:** 22 N per finger — estimate [estimate]. 0.13 x whole-fruit max force 167 N
- **Failure:** 167 N [ZU1] — max compressive force at 8.81 mm deformation; plate/probe not in abstract
- **Friction:** no measured value; sim estimate 0.5 (estimate: middle of the measured dry produce values in this catalog on rubber/TPU/silicone/steel (0.33-1.41); no wet data)
- **Stiffness:** not found
- **Handling:** Chinese xihulu is 4-10x heavier than the tested fruit - re-measure.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| whole fruit compression | max 167 N at 8.81 mm; work 762.8 N mm; penetration 1.26 N |  | [M] | ZU1 |
| modulus | 0.73 GPa as printed - implausible for fresh tissue, not used |  | [M] | ZU1 |

### Strawberry (草莓)
- **Limit:** 0.6 N per finger — demonstrated safe [S3]. stable, damage-free grasp at 0.3-0.6 N (visuotactile silicone finger); true onset lies between 0.6 N and 9.8 N
- **Failure:** 9.8 N [S1] — 9.8 N for 2 s with a 15 mm convex probe already gives a 197 mm3 bruise (301 mm3 at 5 s)
- **Friction:** dry 0.57 — static, counter-surface not stated (0.57-0.95) [Q23]
- **Stiffness:** 29.55 kPa — whole-fruit curve fit (Q23); inner tissue 0.53 MPa per S5 (snippet) [Q23]
- **Handling:** Do not pinch the body above ~0.6 N; bruising grows with hold time. Prefer handling in the clamshell / a scoop, or grip the calyx/peduncle (2 N per finger used in S2).

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| static bruise | 9.8 N, 2 s -> 197 mm3; 5 s -> 301 mm3 | 15 mm convex probe, Oso Grande | [M] | S1 |
| impact bruise | 0.040 J -> 13 mm3; 0.083 J -> 91 mm3 | pendulum | [M] | S1 |
| inner tissue failure | 0.093 MPa, strain 17.7 %, E 0.53 MPa | search snippet only | [O] | S5 |
| peduncle crush | min peak 22.5-26.8 N; recommended limit 10 N | UTM 1.5 mm/min | [M] | S4 |
| assumed mu | 0.5 for silicone ('closer to 1') | design assumption | [O] | S2 |
| static mu | 0.57-0.95 | TL201Tt tester | [M] | Q23 |

### Green beans / long beans (四季豆/豇豆)
- **Limit:** not settled (no usable data) — see handling
- **Friction:** no measured value; sim estimate 0.5 (estimate: middle of the measured dry produce values in this catalog on rubber/TPU/silicone/steel (0.33-1.41); no wet data)
- **Stiffness:** not found
- **Handling:** Handle as a bundle or in a container; single pods are thin and flexible (long beans drape). No pinch threshold found.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| pod detachment force | 6.57 N (Bronco), 12.68 N (Contender) | snap bean, detachment not crushing; snippet only | [O] | GB1 |
| size, compression, friction | not found |  |  |  |

### Bean sprouts (绿豆芽/黄豆芽)
- **Limit:** not settled (no usable data) — see handling
- **Friction:** no measured value; sim estimate 0.5 (estimate: middle of the measured dry produce values in this catalog on rubber/TPU/silicone/steel (0.33-1.41); no wet data)
- **Stiffness:** not found
- **Handling:** Bulk only: scoop or tip from a container; never pinch.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| hypocotyl hardness | 4414-5157 g/cm2 (0.43-0.51 MPa) | 15 mm plunger, 15 mm depth | [M] | BS1 |
| pack | 50 g in PE bag (test pack) |  | [M] | BS2 |

### Bok choy (Shanghai qing) (上海青/小油菜)
- **Limit:** 12.2 N per finger — clamping damage critical force (lowest) [BC2]. range 12.2-26.4 N across clamp conditions; best case 16.95 N at 18.03 mm (sponge belt, 15 deg, 2 cm clamp height)
- **Friction:** dry 0.65 — static, stem on steel (rubber timing belt 0.69, BC2) [BC1]
- **Stiffness:** 0.916 MPa — petiole/stem; root 0.602 MPa [BC1]
- **Handling:** Grasp at the stem base (lowest clamp height had least damage). Leaves tear; never grip the blades.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| clamp damage critical force | 12.2-26.4 N; 16.95 N at 18.03 mm best case | cloth-sponge belt; plant 176 mm, 79.7 g | [M] | BC2 |
| mu vs belts | rubber timing belt 0.69; patterned belt 0.79; sponge belt 0.73 | static/dynamic not stated | [M] | BC2 |
| mu (static/dynamic) | stem-steel 0.65/0.32; root-steel 0.89/0.36; stem-stem 1.25/0.54 | n=30 | [M] | BC1 |
| leaf creep spring k1 | whole plant 12.7-26.9 N/mm; single leaf ~23-24 N/mm | 1-inch sphere, 6-10 N for 60 s | [M] | BC1 |
| baby-pakchoi stalk E (proxy) | axial 3.15-3.91 MPa; radial 20.2-21.0 MPa |  | [M] | BC3 |

### Cabbage (head) (卷心菜/结球甘蓝)
- **Limit:** not settled (no usable data) — see handling
- **Failure:** 1198 N [CB1] — max compressive force; ambiguous whether stem extrusion or whole head
- **Friction:** no measured value; sim estimate 0.5 (estimate: bok choy stem on steel 0.65 / rubber belt 0.69 (BC1, BC2) rounded down for wet leaf blades)
- **Stiffness:** not found
- **Handling:** Whole head (140-190 mm, ~2 kg) is beyond a 50 mm-stroke 2-jaw gripper - handle halved/quartered or as separated leaves.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| grade masses | loose head 1.5-2.5/1-1.5/<1 kg; tight head 2.5-3/1.5-2.5/<1.5 kg | draft group standard | [O] | CB2 |
| root cutting force | 137.1 N |  | [M] | CB1 |
| leaves | inner leaves high-moisture and brittle |  | [M] | CB1 |

### Napa cabbage (大白菜)
- **Limit:** not settled (no usable data) — see handling
- **Failure:** 820.3 N [NC1] — whole head radial crush at 27.86 mm, 10 mm/min; internal damage may start earlier
- **Friction:** no measured value; sim estimate 0.5 (estimate: bok choy stem on steel 0.65 / rubber belt 0.69 (BC1, BC2) rounded down for wet leaf blades)
- **Stiffness:** not found
- **Handling:** Whole head not graspable by a 2-jaw gripper; handle cut pieces or single leaves (grip the thick white midrib).

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| radial crush | 820.34 N at 27.86 mm | 10 mm/min | [M] | NC1 |
| pull-out force | 222-354 N |  | [M] | NC1 |

### Broccoli (西兰花)
- **Limit:** 175 N per finger — estimate [estimate]. stem grasp only: failure/2 = petiole crush 350 N/2; curd threshold not found - do not pinch the curd
- **Failure:** 350 N [BR3] — petiole radial compression peak 350-400 N (P/36R, 0.2 mm/s)
- **Friction:** no measured value; sim estimate 0.5 (estimate: middle of the measured dry produce values in this catalog on rubber/TPU/silicone/steel (0.33-1.41); no wet data)
- **Stiffness:** 1.6 MPa — whole-stem compressive E 1.3-2 MPa [BR2]
- **Handling:** Grasp the stem only; florets break off. Head (120-170 mm) exceeds the stroke - present stem-first.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| stem moduli | rind 27-48 MPa; xylem 19-111 MPa; pith 6.5-7.5 MPa; whole-stem compressive E 1.3-2 MPa |  | [M] | BR2 |
| stem radial compressive strength | 0.59 MPa | FEA result | [O] | BR2 |
| petiole bending peak | 15-20 N | 80 mm petiole, 2 mm/s | [M] | BR3 |

### Celery (芹菜/西芹)
- **Limit:** 12 N per finger — estimate [estimate]. no data; proxy = bok choy petiole clamp damage 12.2 N
- **Friction:** no measured value; sim estimate 0.5 (estimate: bok choy stem on steel 0.65 / rubber belt 0.69 (BC1, BC2) rounded down for wet leaf blades)
- **Stiffness:** not found
- **Handling:** Long (0.5-0.8 m): grasp the bunch at the base; single petioles are crisp and snap.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| petiole cutting force | figure only | Warner-Bratzler, 0.4 mm/s | [M] | CE1 |
| compression, friction, modulus | not found |  |  |  |

### Scallion (xiaocong) / Welsh onion (dacong) (小葱/大葱)
- **Limit:** 16.5 N per finger — estimate (white shaft only) [estimate]. failure/2 = 33 N/2 for the white shaft; the green tubular leaves permanently deform at ~1 N (SC2, chive proxy) - never grip the leaves
- **Failure:** 33 N [derived] — dacong white shaft compressive strength 0.33 MPa (SC1, upper part) x assumed 100 mm2 contact
- **Friction:** no measured value; sim estimate 0.5 (estimate: bok choy stem on steel 0.65 / rubber belt 0.69 (BC1, BC2) rounded down for wet leaf blades)
- **Stiffness:** 2.44 MPa — dacong white shaft, upper (2.44-2.76 MPa) [SC1]
- **Handling:** Grasp the bunch at the white base (SC1: clamp upper/lower parts of the white). Green tubes crush at ~1 N.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| white-shaft compressive strength | upper 0.33 / middle 0.37 / lower 0.39 MPa | 4-factor test | [M] | SC1 |
| white-shaft shear strength | 0.19-0.21 MPa |  | [M] | SC1 |
| chive damage onset | ~1 N; leaf diameter 2-3 mm | bunch compression | [M] | SC2 |

### Chinese chives (韭菜)
- **Limit:** 140 N per finger — not limiting at the banded base [CV1]. bundle compressed 13 mm at 40 mm/min showed no visible breakage up to 225 N (above a 140 N gripper max); leaf blades permanently deform at ~1 N (SC2, chive proxy), so grip only the base
- **Friction:** no measured value; sim estimate 0.5 (estimate: bok choy stem on steel 0.65 / rubber belt 0.69 (BC1, BC2) rounded down for wet leaf blades)
- **Stiffness:** not found
- **Handling:** Grasp the whole bunch near the white base (where it is banded). Treat 1 N vs 225 N as the bruise vs breakage bounds.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| bundle compression | no visible damage up to 225 N | TMS-Pro 40 mm/min, 13 mm | [M] | CV1 |
| max shear force | 129 N |  | [M] | CV1 |

### Spinach (菠菜)
- **Limit:** 2.2 N per finger — leaf injury observed (proxy) [LE1]. lettuce: 2.2 N per finger on the leaf surface already left 275 mm2 injury
- **Friction:** no measured value; sim estimate 0.5 (estimate: bok choy stem on steel 0.65 / rubber belt 0.69 (BC1, BC2) rounded down for wet leaf blades)
- **Stiffness:** not found
- **Handling:** Grasp the bunch at the crown/roots (113.8 N axial root compression); leaves bruise at ~2 N.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| main root shear / axial compression peak | 31.2 N / 113.8 N | WDW-5E | [M] | SP1 |
| size, leaf compression, friction | not found |  |  |  |

### Lettuce (生菜)
- **Limit:** 2.2 N per finger — leaf injury observed [LE1]. ~2.2 N per finger (1.67-2.33 N), 4 soft fingers: injury 275.5 mm2 on leaf surface, 120.3 mm2 with 2 fingers at leaf junctions
- **Friction:** no measured value; sim estimate 0.5 (estimate: bok choy stem on steel 0.65 / rubber belt 0.69 (BC1, BC2) rounded down for wet leaf blades)
- **Stiffness:** not found
- **Handling:** Grip at leaf junctions / the core, not on blades - halves the injury area.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| grasp injury | 2.2 N -> 275.5 / 206.8 / 120.3 mm2 by finger placement | pneumatic soft fingers | [M] | LE1 |
| pile compression | safe pile height 80 cm; density 0.21 kg/L | packaging study | [M] | LE2 |

### Shiitake (香菇)
- **Limit:** 42 N per finger — derived (stipe only) [derived]. stipe bio-yield stress 0.418 MPa (SH1) x assumed 100 mm2 contact on a 13 mm stipe; cap/gills: not found, do not pinch
- **Friction:** no measured value; sim estimate 0.5 (estimate: middle of the measured dry produce values in this catalog on rubber/TPU/silicone/steel (0.33-1.41); no wet data)
- **Stiffness:** 0.871 MPa — stipe, radial (Poisson 0.322) [SH1]
- **Handling:** Grip the stipe only (SH1 used 1 mm silicone pads); cap and gills are soft and bruise. Grip force decays by relaxation.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| stipe E / bio-yield | 0.871 MPa / 0.418 MPa | 10 mm cubes, 1 mm/s, n=10 | [M] | SH1 |
| stipe stress relaxation | 0.123 -> 0.101 MPa over 60 s | FEA validated within 5 % | [O] | SH1 |
| twist-off torque | 0.092-0.137 N m |  | [M] | SH1 |

### Enoki (金针菇)
- **Limit:** not settled (no usable data) — see handling
- **Friction:** no measured value; sim estimate 0.5 (estimate: middle of the measured dry produce values in this catalog on rubber/TPU/silicone/steel (0.33-1.41); no wet data)
- **Stiffness:** not found
- **Handling:** Handle as one cluster by the root block (cut off before cooking); stems are thin and separate.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| anything | not found |  |  |  |

### King oyster mushroom (杏鲍菇)
- **Limit:** 84 N per finger — estimate (proxy) [estimate]. proxy = shiitake stipe bio-yield 0.418 MPa x 200 mm2 (thicker stem); no data for P. eryngii
- **Friction:** no measured value; sim estimate 0.5 (estimate: middle of the measured dry produce values in this catalog on rubber/TPU/silicone/steel (0.33-1.41); no wet data)
- **Stiffness:** not found
- **Handling:** Firm, dense stem: grasp the stem body.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| anything | not found (hypobaric-storage paper reports texture only qualitatively) |  |  |  |

### Chicken egg (in shell) (鸡蛋)
- **Limit:** 10 N per finger — lowest single-egg rupture [EGG2]. rupture range 10.03-58.96 N (Hisex Brown, cited Nedomova); breed means 38-56 N (EGG3)
- **Failure:** 38 N [EGG3] — lowest breed-mean rupture, equator (short axis) between parallel plates, 0.167 mm/s
- **Friction:** dry 0.47 — static, rubber - QUAIL egg (snippet); chicken egg order only: rubber > plywood > metal > glass [EGG6]
- **Stiffness:** 32 GPa — eggshell, mean of 40 wild bird species (no chicken-specific value) [EGG4]
- **Handling:** Shell cracks with no bruise warning; force-limited grasp across the equator with soft concave pads. Out of shell: never pinch (container only).

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| rupture force by axis | blunt 41.6-53.4; equator 38.0-45.0; sharp 43.8-56.5 N | parallel plates 0.167 mm/s, 4 breeds | [M] | EGG3 |
| rupture (Hisex Brown) | 36.4 N short axis, 34.9 N long axis; range 10.03-58.96 N | cited | [O] | EGG2 |
| puncture force | 26.34 N | 2 mm probe at equator | [M] | EGG2 |
| static stiffness | 145-211 (probably N/mm) | plates | [M] | EGG3 |
| size / shell | L 58.05 mm, W 45.46 mm, 65.89 g, shell 0.48 mm | class L | [M] | EGG2 |
| friction order | rubber > plywood > chipboard > galvanized > glass; mu rises with egg mass | abstract, no numbers | [M] | EGG5 |

### Tofu, silken (嫩豆腐/内酯豆腐)
- **Limit:** 3 N per finger — derived [derived]. peak stress 3.74 kPa at 30 % strain (TF1, confined compression, 8 mm cylinders) x 800 mm2 pad; equilibrium stress 1.26 kPa -> 1.0 N
- **Friction:** no measured value; sim estimate 0.1 (estimate: between fish-mucus values on polypropylene (snakehead 0.04, carp 0.12-0.14, FI1); mucilage/slime acts as a lubricant)
- **Stiffness:** 9 kPa — estimate E = 3G from shear modulus G = 3.0 kPa (TF2, DMA 14 Hz) [estimate]
- **Handling:** Never pinch: move in its box, or slide/tip it out onto a plate or into a tray. Even a full-pad hold is only ~1-3 N before damage.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| peak compressive stress at 30 % strain | silken 3.74 +/- 0.86 kPa | confined compression, 8x10 mm cylinders, 20 %/s | [M] | TF1 |
| equilibrium stress | 1.26 kPa | model fit | [M] | TF1 |
| shear modulus | soft 3.0 +/- 0.40 kPa | poroelastic DMA 14 Hz | [M] | TF2 |
| water fraction | 0.89 | label | [M] | TF1 |

### Tofu, firm (老豆腐/北豆腐)
- **Limit:** 15 N per finger — derived [derived]. peak stress 18.91 kPa at 30 % strain (TF1) x 800 mm2 pad
- **Friction:** no measured value; sim estimate 0.1 (estimate: between fish-mucus values on polypropylene (snakehead 0.04, carp 0.12-0.14, FI1); mucilage/slime acts as a lubricant)
- **Stiffness:** 24 kPa — estimate E = 3G, G = 8.1 kPa (TF2); stiffness 26.4 kPa per St. Pierre 2024 (TF1, cited) [estimate]
- **Handling:** Flat faces: use the full pad area; slippery wet surface (no friction data).

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| peak stress at 30 % strain | firm 18.91 +/- 5.50 kPa; extra-firm 42.84 +/- 16.22 kPa | confined compression | [M] | TF1 |
| shear modulus | firm 8.1 +/- 1.2; extra-firm 15 +/- 2.4 kPa | DMA | [M] | TF2 |

### Chicken breast (raw) (鸡胸肉)
- **Limit:** 56 N per finger — derived (deformation, not damage) [derived]. TPA hardness ~3.5 N on 8 mm cylinders at 50 % strain (CK2) = ~70 kPa x 800 mm2: force that squashes it to half thickness. Raw meat has no bruise criterion for immediate cooking
- **Friction:** wet 0.5 — static, stainless steel SAE304; wetting did not change the sliding angle (tilt test + DEM calibration) [CK1]
- **Stiffness:** 48.6 kPa — raw fillet blocks 35x35x10 mm, < 3 % strain [CK1]
- **Handling:** Floppy and wet; pinch grasps sag. Prefer a scoop/plate or full-length pads; friction on steel 0.5 even when wet.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| Young's modulus | 48.6 +/- 1.64 kPa | 1 mm/min | [M] | CK1 |
| TPA hardness / E | median ~3.5 N / ~40 kPa | 8 mm cylinders, 50 % strain, 3 mm/s; read from box plot | [M] | CK2 |
| cooked comparison | 0.37 MPa | cooked breast (Ko 2023) | [O] | CK1 |

### Pork (lean chunk / belly) (猪肉（瘦肉块/五花肉）)
- **Limit:** 56 N per finger — proxy chicken breast [estimate]. no usable raw-pork compression number; proxy = chicken breast
- **Friction:** no measured value; sim estimate 0.5 (estimate: proxy chicken fillet on steel 0.5 (CK1))
- **Stiffness:** not found
- **Handling:** Belly skin side is the grippiest face; lean chunk is wet and slippery. No sourced friction.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| compression behaviour | ~50 % of stress viscous at 0.5 %/s; stress at 30 % strain x5 from 0.05 to 10 %/s; cross-fibre 1.2x stiffer | fresh porcine muscle cubes, < 2 h post-mortem | [M] | PK1 |
| stress magnitude | order 1 kPa at ~25 % strain, 1 %/s (figure axis, low confidence) |  | [M] | PK1 |

### Whole fish (sea bass) (鲈鱼（整条）)
- **Limit:** not settled (no usable data) — see handling
- **Friction:** wet 0.12 — static, mucus intact, on polypropylene - common carp (0.124-0.141); snakehead 0.037-0.043 [FI1]; dry 0.5 — static, mucus wiped off, carp on polypropylene (0.499-0.550) [FI1]
- **Stiffness:** not found
- **Handling:** Very slippery with mucus (mu ~0.12): a 0.6 kg fish needs ~25 N per finger just to hang - wipe/rinse mucus, grip at the caudal peduncle (tail wrist), or carry on a tray. 350 mm long: centre of mass far from a tail grasp.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| static mu, mucus intact | carp 0.141 fwd / 0.124 back; snakehead 0.037 / 0.043 | freshly euthanised fish towed on a PP table | [M] | FI1 |
| static mu, mucus wiped | carp 0.550 / 0.499; snakehead 1.07 / 1.18 | same | [M] | FI1 |
| max size | 102 cm, 8.7 kg |  | [O] | FI2 |

### Fish fillet (鱼片/鱼柳)
- **Limit:** not settled (no usable data) — see handling
- **Friction:** no measured value; sim estimate 0.1 (estimate: between fish-mucus values on polypropylene (snakehead 0.04, carp 0.12-0.14, FI1); mucilage/slime acts as a lubricant)
- **Stiffness:** not found
- **Handling:** Deformation-limited: keep pad indentation < 5 mm (FI4). Flaky and slippery - support from below (spatula/tray) rather than pinch.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| fibre damage onset | fibres break at 6-8 mm penetration; no yield at 5 mm (25.4 mm sphere) | raw salmon fillet, 20 mm flat cylinder, 2 mm/s; forces only in figures | [M] | FI4 |

### Shrimp (shell-on, raw) (虾（带壳，白虾/基围虾）)
- **Limit:** not settled (no usable data) — see handling
- **Friction:** no measured value; sim estimate 0.1 (estimate: between fish-mucus values on polypropylene (snakehead 0.04, carp 0.12-0.14, FI1); mucilage/slime acts as a lubricant)
- **Stiffness:** not found
- **Handling:** Bulk-handle in a colander/basket (washing step). Single-shrimp pinch not characterised.

| Quantity | Value | Conditions | Tag | Src |
|---|---|---|---|---|
| TPA hardness | 6900.8 +/- 484.9 g (~67.7 N) | 36 mm probe, 6 mm, beheaded/peeled, possibly cooked - not raw shell-on | [M] | SR1 |
| count | 30-35 per kg | farm harvest, India | [M] | SR2 |

## 4. What this means for the finger design

All points below are derived from the tables above.

- **Pinch is not feasible (Limit/Hold < 1) for:**
  - **Silken tofu** (0.1): handle it in its box or slide it out.
  - **Firm tofu** (0.6, with the slime μ estimate).
  - **Peeled Chinese yam** (0.5).
  - **Whole lettuce head by its leaves** (0.4): grip the core instead.
  - **Whole western celery plant** (0.6).
- **Margin of 2 or less:** strawberry (1.4), daikon (2.0).
- **Too large for a 2-jaw grasp:** whole cabbage and napa cabbage. Whole fish has a large hold requirement (≈41 N per finger at μ = 0.12) and no damage limit. These need cutting, a tray, or a different end-effector.
- **Bulk items:** cherry tomato (if many), xiaomila, garlic cloves, bean sprouts, green beans, shrimp and enoki. These are better handled in a container or colander than one piece at a time.
- **Limits below 40 N per finger:** carried over from the PGC-140-50 force-mode floor, these need position-limited or compliant closing. This applies to tomato, cherry tomato, cucumber, eggplant, peppers, zucchini, strawberry, bok choy, celery, scallion, spinach, lettuce, egg, both tofus and garlic.
- **Mucus and mucilage are the dominant slip risk.** Carp with mucus measured μ = 0.12–0.14 on polypropylene (0.50–0.55 once wiped). Peeled yam/taro, tofu and fish fillet are probably similar but unmeasured. Rinsing or wiping before the grasp changes the required force about fourfold.

## 5. Major gaps

- **Wet friction against silicone/TPU:** not found for any food. The only wet data are potato on rubber belting, raw chicken on steel, and fish on polypropylene. This is the biggest gap for slip simulation. A one-afternoon bench test (tilt plate covered with your pad material, wet and dry, about 10 ingredients) would replace every `sim_estimate`.
- **Damage limits with no data**, so the Limit is an estimate or proxy:
  - Daikon, Chinese yam, pumpkin/winter melon, corn, eggplant, bell pepper, celery, king oyster.
  - Green beans, bean sprouts, enoki, whole fish, fish fillet (deformation limit only), shrimp, pork (chicken proxy).
  - Leaf blades: lettuce data reused for spinach.
  - Cherry tomato: the numbers in Kabas 2008 are behind a paywall.
- **Chinese retail sizes and masses:** the NY/T and GB/T grade standards (NY/T 1066, 1983, 1791, 1587, 1894, 944, 1789, 1835, 1729, 941; GB/T 38581, 39438) are paywalled and were not read. Most sourced sizes are Iranian, Egyptian, Indian, Japanese or Serbian cultivars. The CN retail column is my estimate; weigh real samples.
- **Single-measurement or questionable values:**
  - Q23 friction and modulus: the counter-surface is not stated, and E comes from a single measurement.
  - Carrot apparent E: 0.038 MPa.
  - Zucchini E: 0.73 GPa as printed, so not used.
  - Cabbage 1198 N: ambiguous whether this is stem or head.
  - Ginger peel rupture: seen only in a snippet.
  - Egg friction: from a quail-egg snippet.
  - Pork stress magnitude: read from a figure axis.
- **Search budget:** the session's shared web-search budget (200 calls) ran out midway. Several open leads were not followed:
  - MDPI Agriculture 13(5):942, white radish.
  - Tomato-stem friction vs silica gel, 农机化研究 2023.12.022.
  - Kabas 2008, cherry tomato.
  - Altuntas 2010, egg friction numbers.

## Sources

Key — citation — URL. All pages were opened and read by the research agents unless the citation says snippet/abstract.

- **T1** — Zhou K. et al. 2022, Int J Agric Biol Eng 15(2):13-24 (tomato clamping, Dragon Skin 30 pads) — https://ijabe.org/index.php/ijabe/article/view/6672
- **T2** — Zheng Y. et al. 2022, Front. Plant Sci. doi:10.3389/fpls.2022.974456 (tomato gripper FEA) — https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2022.974456/full
- **T6** — Ansari S. et al. 2026, Scientific Reports (TPU auxetic tomato gripper) — https://pmc.ncbi.nlm.nih.gov/articles/PMC13223203/
- **F2** — Bishop C.F.H. et al. 2012, Res. Agr. Eng. 58:114-117 (potato friction, wet/dry belting) — https://rae.agriculturejournals.cz/pdfs/rae/2012/03/05.pdf
- **Q23** — Qiu Z. et al. 2023, Foods 12(22):4062, 'An Evaluation System of Robotic End-Effectors for Food Handling' Table 1 (static mu by TL201Tt tester, counter-surface not stated; E by IMADA stand, single measurement) — https://pmc.ncbi.nlm.nih.gov/articles/PMC10670141/
- **APL15** — 'Design on Tester of Fruit Surface Friction', Proc. KAM 2015, Atlantis Press (Fuji apple vs silica gel) — https://www.atlantis-press.com/article/25445.pdf
- **C1** — Jahanbakhshi A. et al. 2018, Food Sci Nutr 6(7):1898-1903 (carrot) — https://pmc.ncbi.nlm.nih.gov/articles/PMC6189625/
- **P1** — Abedi G. et al. 2019, Res. Agr. Eng. 65(3):77-84 (potato Marfona/Sante) — https://www.agriculturejournals.cz/pdfs/rae/2019/03/01.pdf
- **P2** — Chen Z. et al. 2020, J. South China Agric. Univ. (potato drop-damage contact stress) — https://journal.scau.edu.cn/article/doi/10.7671/j.issn.1001-411X.202001005
- **O1** — Bahnasawy A.H. et al. 2004, J Food Eng 62:255-261 (onion, Egyptian cultivars) — https://bu.edu.eg/portal/uploads/Agriculture/Agricultural%20Engineering/1243/publications/Adel%20hamed_onion-physical.pdf
- **G1** — Jadhav et al. 2026, Plant Archives 26 Suppl 1:2561-2570 (garlic mechanics) — https://plantarchives.org/article/343%20CHARACTERIZATION-OF-THE-MECHANICAL-PROPERTIES-OF-GARLIC-(ALLIUM-SATIVUM-L.)-FOR-PROFICIENT-EQUIPMENT-DESIGN-IN-FOOD-PROCESSING.pdf
- **L1** — Chen Y. et al. 2024, J. Gansu Agric. Univ. (lotus root cv. E-Lian 5) — https://www.aeeisp.com/gsnydxxb/article/doi/10.13432/j.cnki.jgsau.2024.01.034
- **L2** — Teng et al. 2023, Eng. Agric. 43(5) e20230128 (lotus root mechanics) — https://scielo.br/j/eagri/a/SVm7Gv986N4gRQbCMVDDKYx/?lang=en
- **Gi1** — Pandey et al. 2025, J. Agric. Eng. (India) (ginger rhizome) — https://pub.isae.in/index.php/jae/article/view/1233
- **Gi2** — Visvanathan & Jayashree 2011, J. Spices Arom. Crops 20(2):60-65 (ginger) — https://agris.fao.org/search/en/records/670527e2b1dfe472e145aba4
- **CN1** — Chen S. et al., Trans. CSAM (fresh corn peeling machine test material) — https://www.aeeisp.com/nyjxxb/article/id/5f6483ef-3e1d-4c69-9a77-10bf61074feb
- **CN2** — Zhu et al. 2022, J. Jilin Univ. (Eng.) 52(10) (fresh corn ear) — https://xuebao.jlu.edu.cn/gxb/CN/10.13229/j.cnki.jdxbgxb20210308
- **A1** — Liu et al. 2022, Foods (apple compression damage) — https://pmc.ncbi.nlm.nih.gov/articles/PMC9265796/
- **A2** — Zhang X. et al. 2022, Int J Food Prop doi:10.1080/10942912.2022.2107006 (Fuji apple peel/pulp, friction) — https://agris.fao.org/search/en/records/68caca8cf61e5b80b5e91c7e
- **A3** — Stropek & Golacki 2022, Materials (apple flesh compression) — https://pmc.ncbi.nlm.nih.gov/articles/PMC9655156/
- **Y1** — Arisa et al. 2024, J. Food Tech. Res. 11(2) (Nigerian yams/cocoyam - different species, proxy only) — https://archive.conscientiabeam.com/index.php/58/article/view/3741
- **TA1** — Olalusi A.P. 2014, FUTA J. Eng. Eng. Technol. (cocoyam/taro Colocasia esculenta) — https://jeet.futa.edu.ng/jeet/article/view/13
- **S1** — Strawberry bruising under static compression and impact, Scientia Agricola (USP) — https://revistas.usp.br/sa/article/download/22326/24350/25958
- **S2** — Enabling Tactile Feedback for Robotic Strawberry Handling using AST Skin, arXiv 2407.01739 — https://arxiv.org/pdf/2407.01739
- **S3** — Strawberry visuotactile grasping, Trans. CSAE doi:10.11975/j.issn.1002-6819.202411048 — https://www.aeeisp.com/nygcxb/article/doi/10.11975/j.issn.1002-6819.202411048
- **S4** — Strawberry peduncle gripper, arXiv 2207.12552 — https://arxiv.org/abs/2207.12552
- **S5** — Li et al. 2020, J Food Eng doi:10.1016/j.jfoodeng.2020.110016 (strawberry inner tissue; seen via search snippet only) — https://results2021.ref.ac.uk/outputs/0bf8c794-b76c-4c5d-a2c8-7b7d4bd86c06
- **CT1** — Cherry-tomato tactile harvesting on UR5e, arXiv 2602.18991 — https://arxiv.org/pdf/2602.18991
- **CT2** — Cherry tomato axial/radial compression across ripeness (Chinese, abstract) — https://www.aeeisp.com/xdnyzb/cn/article/id/ccd641a3-9bc1-4640-b72a-da69cf956a52
- **CU1** — Group standard T/XMSSAL 0084-2023 (cucumber, cites NY/T 1587) — https://www.ttbz.org.cn/upload/file/20230814/6382760880430589428902716.pdf
- **CU2** — Cucumber slice fracture, JARQ 41(2) — https://www.jircas.go.jp/sites/default/files/publication/jarq/41-02-02_0.pdf
- **CU3** — Cucumber 'Viola' firmness during shelf life, CIGR Journal art. 3615 (abstract) — https://cigrjournal.org/index.php/Ejounral/article/view/3615
- **GB1** — Snap bean pod detachment force, Misr J. Agric. Eng. (search snippet; site did not resolve) — https://mjae.journals.ekb.eg/article_101933_7064e68c411dd6d7294fd8fc403a2bbd.pdf
- **LE2** — Lettuce pile compression / packaging, Ciencia e Agrotecnologia — https://scielo.br/j/cagro/a/QLKFzzjtJQvPw74bMfnbwfk/?lang=en
- **EG1** — Eggplant harvesting robot, JARQ 36(3) — https://www.jircas.go.jp/sites/default/files/publication/jarq/36-03-07_0.pdf
- **EG2** — Long black eggplant handled by pneumatic parallel gripper (Univ. Burgos record) — https://investigacion.ubu.es/documentos/604ac902fcf63c71c571faf7?lang=en
- **EG3** — Mohamad N.S. et al. 2018, J. Eng. Res. Educ. 10 SI:71-78 (round eggplant firmness, CT3 texture analyser) — https://jere.unimap.edu.my/images/Artikel/JERE%20VOL%2010_Special%20Issue%20(2018)/JERE_SI_9_71-78.pdf
- **CH1** — Chili pepper mechanics, Front. Plant Sci. 2025 doi:10.3389/fpls.2025.1542262 — https://www.frontiersin.org/articles/10.3389/fpls.2025.1542262/full
- **CH2** — Group standard, Huaiji pepper quality (Guangdong) — https://www.ttbz.org.cn/upload/file/20250331/6387902756554563032581136.pdf
- **ZU1** — Zucchini physical and mechanical properties, CIGR Journal art. 2068 — https://cigrjournal.org/index.php/Ejounral/article/view/2068
- **BS1** — Soybean sprout quality of commercial brands (Korea) — https://koreascience.kr/article/JAKO200804748553791.pdf
- **BS2** — Mung bean sprout packaging study (Thailand) — https://li01.tci-thaijo.org/index.php/PRRJ_Scitech/article/download/251599/173065
- **BC1** — Pakchoi (Shanghai-qing) physical/mechanical parameters, PMC11218987 — https://pmc.ncbi.nlm.nih.gov/articles/PMC11218987/
- **BC2** — Pakchoi clamping-damage test, J. Agric. Sci. Technol. (China) 2022 24(4):116 doi:10.13304/j.nykjdb.2021.0759 — https://nkdb.magtechjournal.com/CN/Y2022/V24/I4/116
- **BC3** — Baby pakchoi (ji mao cai) stalk compression, J. Agric. Sci. Technol. (China) 2018 20(11):85 — https://nkdb.magtechjournal.com/CN/Y2018/V20/I11/85
- **CB1** — Cabbage harvest mechanics, Agriculture 13(6):1204 (2023) — https://doi.org/10.3390/agriculture13061204
- **CB2** — Group standard draft, cabbage grades (Yu-Sui-Mian) — https://www.ttbz.org.cn/upload/file/20240808/6385872707599460317969759.pdf
- **NC1** — Napa cabbage harvesting mechanics, Agriculture 15(8):831 (2025) — https://doi.org/10.3390/agriculture15080831
- **BR1** — Group standard draft T/NAIA 2023, broccoli grades (Ningxia) — https://www.ttbz.org.cn/upload/file/20230531/6382113090778558988860743.pdf
- **BR2** — Broccoli stem mechanics, Agriculture 12(10):1519 (2022) — https://doi.org/10.3390/agriculture12101519
- **BR3** — Broccoli petiole compression/bending, Agronomy 14(9):1925 (2024) — https://doi.org/10.3390/agronomy14091925
- **CE1** — Celery 'Golden Boy' growth and harvest quality, Hortic. Bras. — https://www.scielo.br/j/hb/a/hNXtzFJPzCjPFS6YTMVxCLx/?lang=en
- **SC1** — Welsh onion (da cong) white-stalk mechanics, J. Agric. Mech. Res. 2023 doi:10.13427/j.cnki.njyi.2023.05.036 — https://www.aeeisp.com/njhyj/article/doi/10.13427/j.cnki.njyi.2023.05.036
- **SC2** — Castillo et al. 2013, Agron. Colomb. (chives Allium schoenoprasum mechanics) — https://revistas.unal.edu.co/index.php/agrocol/article/view/34328
- **CV1** — Chinese chive harvester mechanics, IJABE art. 7067 — https://ijabe.org/index.php/ijabe/article/view/7067
- **SP1** — Spinach root mechanics, J. Agric. Mech. Res. 2021 doi:10.13427/j.cnki.njyi.2021.08.032 — https://www.aeeisp.com/njhyj/article/doi/10.13427/j.cnki.njyi.2021.08.032
- **LE1** — Soft-finger lettuce grasping injury, PMC10346448 — https://pmc.ncbi.nlm.nih.gov/articles/PMC10346448/
- **SH1** — Shiitake picking end-effector, Machines 12(4):241 (2024) — https://doi.org/10.3390/machines12040241
- **EGG1** — Group standard draft T/CAAA, quality classification of shell eggs (cites GB/T 39438-2020) — https://www.ttbz.org.cn/upload/file/20220620/6379132951523607096814028.pdf
- **EGG2** — Egg quality, class L eggs, J. Process. Energy Agric. (Serbia) — https://asistent.ceon.rs/index.php/jpea/article/download/32280/19038
- **EGG3** — Egg rupture force by orientation, Acta Univ. Agric. Silvic. Mendel. Brun. 2016 64(4) — https://acta.mendelu.cz/pdfs/acu/2016/04/11.pdf
- **EGG4** — Eggshell Young's modulus of 40 bird species, PMC5660176 — https://pmc.ncbi.nlm.nih.gov/articles/PMC5660176/
- **EGG5** — Altuntas & Sekeroglu 2010, egg friction on surfaces (abstract) — https://agris.fao.org/search/fr/records/65df1c4e4c5aef494fdfce9f
- **EGG6** — Quail egg friction, J. Soil Sci. Agric. Eng. (search snippet only) — https://jssae.journals.ekb.eg/article_226623.html
- **TF1** — Tofu mechanics (silken/firm/extra-firm), Stanford biomechanics bioRxiv preprint — https://biomechanics.stanford.edu/paper/bioRxiv26.pdf
- **TF2** — Tofu poroelastic DMA, PMC4510837 — https://pmc.ncbi.nlm.nih.gov/articles/PMC4510837/
- **TF3** — Costco Taiwan retail listing, traditional tofu 400 g — https://www.costco.com.tw/Warehouse-Only/Food-Beverages/Chilled/Pure-Chilled-Non-GMO-Traditional-Tofu-400-g-X-3-Pack/p/126249
- **CK1** — Vink et al. 2026, Appl. Food Res. 6:101880 (raw chicken fillet E, friction on steel, DEM) — https://repository.tudelft.nl/file/File_dfebf4e4-3f77-40b9-8e32-e6fbf9116ace
- **CK2** — Meat TPA comparison, Sci. Rep. 2022 doi:10.1038/s41598-022-07785-1 — https://www.nature.com/articles/s41598-022-07785-1
- **PK1** — Van Loocke et al. 2009, viscoelastic passive porcine muscle in compression (UMONS repository) — https://orbi.umons.ac.be/bitstream/20.500.12907/9791/1/viscoelastic%20properties%20of%20passive%20skeletal%20muscle%20in%20compression_cyclic%20behaviour2009.pdf
- **FI1** — Lopez-Chilel & Bressman 2025, Integr. Comp. Biol. 65(1):94 (fish mucus static friction on polypropylene table and turf) — https://academic.oup.com/icb/article/65/1/94/7989456
- **FI2** — Wikipedia, Lateolabrax maculatus — https://en.wikipedia.org/wiki/Lateolabrax_maculatus
- **FI3** — 2025 Progress in Fishery Sciences abstract, commercial Lateolabrax maculatus (search snippet only) — https://yykxjz.ijournals.cn/yykxjz/article/abstract/20251024001
- **FI4** — Matis report AquNut vol. 32 (raw salmon fillet texture) — https://matis.is/media/utgafa/AquNutVol32.pdf
- **SR1** — Foods 14:4041 (2025), L. vannamei from a Fuzhou market — https://mdpi-res.com/d_attachment/foods/foods-14-04041/article_deploy/foods-14-04041.pdf
- **SR2** — Fishery Technology (ICAR), farmed shrimp count — https://epubs.icar.org.in/index.php/FT/article/download/81769/33950/208460
