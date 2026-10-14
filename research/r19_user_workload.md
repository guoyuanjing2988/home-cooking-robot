# R19: user workload ledger and 5-year cost vs a helper, tingkat/delivery and auto-cookers (GitHub #28)

Date: 2026-10-14. Desk study, read-only. Inputs: project files and public web pages (WebSearch/WebFetch; no logins, forms, purchases or contact). No other file was changed.

**Tags**
- **[S]**: sourced. Repo `file:line`, or a URL with its date.
- **[E]**: my estimate, with the reasoning given. Nothing in this file is **[M]** (measured). The robot-free trial (#29) is the first chance to measure the minutes.
- Exchange rate: **S$0.19 per ¥1** [S: clock7 1 CNY = S$0.1905 on 2026-07-11, https://www.clock7.com/currency/cny-to-sgd/ ; OFX 1 SGD = ¥5.219 on 2026-08-05, https://www.ofx.com/en-au/exchange-rates/sgd-to-cny]. I found no October 2026 spot rate.
- Household: **4 people**, the reference cook's family size used in the prep audit [S: `sim/r10/claude/R19_PREP_AUDIT.md:32,92`]. Meals: **one 四菜一汤 dinner per cooking day**. The default case is 5 robot meals per week, or 1,300 meals in 5 years [E: the user has not said].

---

## Answer first

1. **User time.** With the current design, the user spends about **38–87 min per meal on robot-only tasks** [E]. Cooking the same meal by hand takes about **62–104 min of hands-on work** [E]. Both figures leave out the tasks that stay the same either way: shopping, rice, serving and clearing the table (18–33 min).
   - **Net saving: −25 to +66 min per meal, about 20 min at the midpoints.** The low end is a loss of time.
   - **With dishwasher automation (#31): 30–74 min, so the net saving is −12 to +74 min, about 31 min at the midpoints.**
   - The user also has to stay at home for the 46–103 min the robot runs, to take plates off the plating spots and because it is not safe to leave cooking unattended.
2. **5-year cost in cash (FR5 path, 1,300 meals): about S$37–55k, or S$28–42 per meal**, groceries excluded [E built on S]. The UR5e path costs S$65–92k (S$50–71 per meal).
   - If the software, integration and validation work is paid for at market rates, add **S$100–300k** [E]. The robot then costs S$105–270 per meal.
3. **Cost per user-hour saved.** For the robot (FR5, cash only) it is **about S$54–126 per hour** at the midpoint savings. For comparison [E built on S]:
   - a live-in helper: S$6–22 per hour, counting only the cooking share of the helper's cost;
   - tingkat: S$0–21 per hour;
   - a part-time cook: S$20–68 per hour;
   - an auto-cooker: S$1–17 per hour.
4. **Verdict.** On money and on time saved, the robot loses to every alternative at today's design and meal count. It wins only on things money comparisons do not capture:
   - the creator's own dishes, freshly cooked at home;
   - no live-in stranger and no spare room needed;
   - control over ingredients;
   - the value of the project itself.
   - It would get closer if it cooks 2 meals a day, saves ≥ 30 min per meal at ≥ 90 % meal success (the #28 gate), and #31 takes over the dishwasher loading.

---

## 1. Per-meal user-minute ledger (robot design as of 2026-10-14)

### 1.1 Tasks that are the same with or without the robot ("common")

| Task | min / meal, low–high | Basis |
|---|---|---|
| Shopping (wet market + supermarket), amortised | 8–17 [E] | 2–3 trips a week × 25–40 min ÷ 7 meals. The as-bought rule (`DECISIONS.md:495-499`) means the robot does not change what is bought. Slot-tray sizes might narrow choices a little. |
| Rice: rinse, load and start the cooker | 3–5 | ≈ 5 min [S: `research/r19_system_cost.md:216`]. The user's job [S: `DECISIONS.md:491-492`]. |
| Serving, soup included | 2–3 [E] | The user serves [S: `DECISIONS.md:421`]. |
| Clearing the table, eating plates into the dishwasher and out again | 5–8 [E] | The user clears; there is a dishwasher [S: `DECISIONS.md:540`]. |
| **Subtotal (common)** | **18–33** | |

### 1.2 Robot-only tasks

| # | Task | Now: low–high | With future automation | Basis |
|---|---|---|---|---|
| R1 | Put groceries into slot trays and baskets, one item per slot for the fork items (about 12–14 prep items per meal) | 5–10 [E] | same | Interface accepted by the user [S: `DECISIONS.md:200`, `:211`]. 38 prep items over 3 meals [S: `R19_PREP_AUDIT.md:32`]. Minutes as in the reviewer ledger [S: `home-cooking-robot/feasibility/gaps_process.md:50`]. |
| R2 | Cold box into the fridge door bin; move frozen meat to it the evening before | 1–2 [E] | same | [S: `DECISIONS.md:270`, `:281`; `R19_PREP_AUDIT.md:388`] |
| R3 | Water: fill and boil the kettle, put steaming water in the pot, top up the Xiaomi dispenser tank | 1–3 [E] | 0–1 if the arm fills the kettle or jug at the dispenser | 4–8 L per meal [S: `DECISIONS.md:387-390`]; dispenser [S: `DECISIONS.md:541`] |
| R4 | Start and pre-check: menu, tools on their rests, finger sets, seasoning levels | 2–4 [E] | 1–2 with self-checks | [S: `gaps_process.md:54`] |
| R5 | Cups and seasoning restock (per meal) | 0 | 0 | The station fills the cups. Nobody doses by hand [S: `DECISIONS.md:542`; `research/r19_seasoning_cups.md:66-76`]. Bulk restock is in R9. Putting the caddies back is in R6. |
| R6 | Robot items through the dishwasher: 24 cups, 6 caddies, 3 drums [S: `r19_seasoning_cups.md:371`], plus baskets, slot trays, lever plates, chopper bowl, soak tub, spider, lid, carrier and plate guards. Load, unload and put each back on its keyed dock. | 8–16 [E] | **0–3 with #31** (exceptions only) | Caddies back on the dock ≈ 1 min [S: `r19_seasoning_cups.md:376`]. A second cup set is needed if 2 meals share one wash [S: `:372`]. |
| R7 | Hand cleaning: deep scrub and oil the wok (the robot only rinses it, [S: `DECISIONS.md:392`]); steamer and stew pot; the 3D-printed PETG finger pads, which are not dishwasher-safe (Tg 80 °C) [S: `research/finger_design_inputs.md:96`; `r19_seasoning_cups.md:346`]; slicer body; peel and waste bins; wipe grease off the counter, hood and arm | 12–24 [E] | 10–20 | No cleaning SOP exists yet (#23). Reviewer ledger 7–13 for the wok, bins and spills, excluding the robot parts [S: `gaps_process.md:57`] |
| R8 | Plates off the 2 plating spots during the run (4–5 dishes) | 2–4 active [E] | same | [S: `DECISIONS.md:425`]. **Presence:** the meal runs A 45–56, B 82–86 and C 41–48 min, plus a 5–17 min prep-first block [S: `R19_PREP_AUDIT.md:65-66`]. |
| R9 | Weekly upkeep, amortised: refill 9 liquid bottles, salt and sugar dosers, spice tray, squeeze bottles; flush the lines; check the pads and tubing; filter the fryer oil | 4–9 [E] (30–60 min/wk ÷ 7) | same | [S: `DECISIONS.md:542`; `r19_seasoning_sizing.md:265`; `gaps_process.md:34`, `:58`] |
| R10 | Failure rescue: a dropped item, a jam, a cup not placed, the dock | 3–15 [E] (0.5–1 per meal × 5–15 min) | lower with maturity | [S: `gaps_process.md:59`]. At today's estimated 22–78 % meal success [S: `gaps_process.md:64`], the high end may be optimistic. |
| | **Subtotal, robot-only** | **38–87** | **30–74** with #31 (29–72 with a dispenser-filled kettle too) | |
| | **User total per meal** (common + robot-only) | **56–120** | **48–107** | |
| | **Presence required, not hands-on** | 46–103 min per meal | same | Plate clearing and fire risk. Unattended cooking caused 318 of 1,051 home fires in Singapore in 2025 [S: `research/r15_cooking_market.md:38`]. Whether the user must be at home is still undecided [S: `gaps_process.md:45`]. |

### 1.3 Human baseline: the same meal cooked by hand

No measured figure exists. The creator's videos are edited and give only cooking durations (braise 40 min, soup 60 min, steaming 6–30 min) [S: `research/homestyle_meals.md:48-56`], not hands-on time. I found no published minutes for food preparation from Singapore or China time-use surveys. The nearest figure is Beijing residents' housework, including shopping, cooking and tidying: **1 h 47 min per day** [S: China Daily, 2017-07-20, https://www.chinadaily.com.cn/china/2017-07/20/content_30180557.htm]. That is a broad sanity check only. **The #29 trial must measure this.**

| Task (hands-on, by hand) | min / meal | Reasoning [E] |
|---|---|---|
| Groceries into the fridge | 2–4 | Simpler than loading slot trays |
| Prep: wash, peel, cut, mince, marinate, soak; 12–14 items | 25–40 | About 2–3 min per item for a practised cook. Shreds, florets, mincing, the fish back-split and squid scoring stay as listed in [S: `r19_asbought.md:26-50`]. |
| Cooking at the hob: on average 2–3 short wok dishes per meal (7 of 15 dishes), plus steaming, a soup and sometimes deep-frying | 20–35 | Most of this time is hands-on, but a person does other tasks during braises and steaming |
| Plating | 3–5 | |
| Cleaning the cooking gear: wok, pots, boards, knives, prep bowls, stove | 12–20 | |
| **By-hand subtotal** (comparable to the robot-only subtotal) | **62–104** | Close to the issue's unmeasured "75–120" [S: issue #28 body], which included the common tasks |
| **User total by hand** (+ common 18–33) | **80–137** | |

### 1.4 Net time saved per meal

| Case | Robot-only | By hand | Saved: worst / midpoint / best |
|---|---|---|---|
| Design today | 38–87 | 62–104 | **−25 / ≈ 20 / +66 min** |
| With #31 (dishwasher automation) | 30–74 | 62–104 | **−12 / ≈ 31 / +74 min** |

**What drives the result.** Three items carry most of the uncertainty:
- R7, hand cleaning: no SOP exists (#23);
- R10, failure rescue: reliability is unknown;
- the by-hand prep time: unmeasured.

Loading the trays (R1) is the largest fixed cost that the design itself adds.

---

## 2. Five-year cost in SGD

### 2.1 Robot

| Line | FR5 path | UR5e path | Basis |
|---|---|---|---|
| Everything except the arm and gripper, incl. 15 % reserve | ¥111–138k | ¥111–138k | [S: `research/r19_system_cost.md:90`]. The seasoning station was re-sized to cups (¥4.9–16.2k, [S: `r19_seasoning_cups.md:66`]), close to the BOM rows it replaces, and the rice module is gone (−¥1–3k [S: `r19_system_cost.md:216`]). Net change ≈ 0 [E]. |
| Arm | ¥23.8k (2023 guide price) | ¥150–180k | [S: `research/r19_arm_hand_cost.md:157-161`]. The FR5 J6 ±360° option is not priced. Industrial-robot prices were reported up 5–15 % in 2026 [S: `:173`]. |
| Gripper PGC-140-50 | ¥12k | ¥12k | [S: `r19_system_cost.md:50`] |
| **Hardware, CNY** | **¥147–174k** | **¥273–330k** | sum |
| Hardware, SGD at 0.19 | S$28–33k | S$52–63k | |
| + 9 % GST on import | S$30.5–36k (round up to 38k for the FR5 price drift) | S$57–69k | 9 % GST [S: Select Catering grid ×1.09, https://www.misslobang.com/article/best-tingkat-delivery-singapore-2026 ; SP tariff "with 9 % GST", https://www.thestar.com.my/aseanplus/aseanplus-news/2026/09/30/electricity-tariff-for-singapore-households-to-fall-by-104-in-fourth-quarter-of-2026] |
| Freight, insurance and broker, CN → SG | S$1–3k [E] | S$1–3k [E] | not researched |
| Not priced in the repo [S: `r19_system_cost.md:106`]: LEW work and a 20 A point for the 3.5 kW cooker, fire items (stove guard, suppression canister, heat detector), wok, DIY parts, build materials | S$1.6–5k [E] | S$1.6–5k [E] | LEW S$0.3–1k; fire items S$0.3–1k; the rest S$1–3k |
| Service and spares over 5 years | S$3–7k [E] | S$5–13k [E] | 10–20 % of hardware |
| Consumables: tubing, pads, filters, extra detergent | S$0.6–1.8k [E] | same | S$10–30 per month. Interval study pending (#28 study 3). |
| Electricity for the arm and PC | ≈ S$0.1–0.3k | same | 0.3–0.6 kWh per meal [E] × 31.16 ¢/kWh incl. GST, Q4 2026 [S: The Star, URL above]. Appliance energy is the same as cooking by hand. |
| **5-year cash total** | **≈ S$37–55k** | **≈ S$65–92k** | Residual value assumed 0 [E] |
| Software, integration and validation, if paid | +S$100–300k [E] | same | No line exists in the repo; `r19_system_cost.md:60` holds only ¥8k for "Industrial PC, vision, network". Bottom-up [E]: perception and runtime state machine 3–6 engineer-months; about 20 prep families tuned on real food 3–6; taste tuning with 45–75 real cooks [S: #29 body] 1–2; FMEA, recovery and safety 2–4; install and commissioning 1. That is 10–19 engineer-months at S$120–180k per year loaded [E]. If the user and AI agents do it unpaid, the cost becomes about 1,500–3,000 hours of the user's time instead [E]. |

**Per meal, cash only, groceries excluded:**

| Meals in 5 years | FR5 | UR5e |
|---|---|---|
| 5 per week (1,300) | **S$28–42** | S$50–71 |
| 7 per week (1,820) | S$20–30 | S$36–51 |
| 14 per week, lunch and dinner (3,640) | S$10–15 | S$18–25 |

With paid software, the FR5 path at 1,300 meals costs **S$105–273 per meal**.

### 2.2 Live-in migrant domestic worker (MDW)

| Item | Amount | Source |
|---|---|---|
| Levy | S$300 per month standard (first helper); S$60 concessionary (household with a child, a senior or a person with a disability) | [S: MOM, https://www.mom.gov.sg/passes-and-permits/work-permit-for-foreign-domestic-worker/foreign-domestic-worker-levy/paying-levy , read 2026-10-14] |
| Recurring per year: salary S$480–700 per month; medical about S$70; insurance S$425; food, utilities and transport S$300 per month; concessionary levy | **S$10,575–13,215 per year** | [S: DBS, 2024-05-14, https://www.dbs.com.sg/personal/articles/nav/financial-planning/cost-of-hiring-domestic-helper] |
| Same with the standard levy (+S$240 per month) | S$13,455–16,095 per year | calc |
| One-off: agency, placement, permit and courses (no bond with insurance) | S$3,930–5,955 per hire | [S: DBS, same] |
| Hires in 5 years | 1–2 [E] (a 2-year contract, renewal or replacement) | |
| **5-year total** | **S$57–78k** with the concession; **S$71–93k** standard | calc |

**Per meal.** Allocated entirely to 1,300 dinners, an MDW costs S$44–72 per meal. But the helper also cleans, does the laundry and helps with childcare. Allocating 25–40 % of the helper's cost to cooking [E] gives **S$11–29 per meal**. The helper needs a room, and the user must want someone living in the home.

### 2.3 Part-time helper who cooks

- S$18–30 per hour [S: Expat Living City Guide 2024, via the search snippet; library mirror https://db.westchesterlibraries.org:2090/singapore/expat-living-city-guide-singapore/20240801/281844353897162].
- Cleaners about S$20 per hour, in 4-hour blocks of S$80–90 [S: MoneySmart 2022, https://blog.moneysmart.sg/family/part-time-maids-singapore/].
- About 2–3 h per meal for prep, cooking and cleanup [E] → **S$40–90 per meal**, or **S$52–117k over 5 years** at 1,300 meals, plus groceries.
- Whether someone can cook the creator's 四菜一汤 reliably is unverified.

### 2.4 Tingkat and delivery apps (food included)

- **Tingkat:** S$6.54–10.91 per person per meal across 7 caterers, typically 3 dishes + soup or 4 dishes; rice +S$0.80–1.09 per person [S: Miss Lobang 2026, URL above]. For 4 people that is **S$30–48 per meal**.
  - The menu is the caterer's, not the creator's.
  - Most plans run 20–22 weekdays.
  - Groceries avoided: S$20–35 per meal [E: 4 dishes + soup for 4 with fish or ribs, not researched]. The premium over cooking at home is therefore **S$0–28 per meal**.
  - 5 years × 1,300: S$39–62k including food.
- **Delivery apps (GrabFood, foodpanda):** "a family dinner for 3 to 4 costs about $50 to $80", or S$15–25+ per person [S: FoodLine.sg, 2026-07-21, https://www.foodline.sg/Discover/Tingkat-vs-Food-Delivery-Apps-Which-Is-Better-for-Daily-Family-Dinners-in-SG/].
  - Premium over groceries: S$15–60 per meal.
  - 5 years: S$65–104k including food.

### 2.5 Auto-cook machine plus the user

- **Thermomix TM7:** S$2,980 at the Singapore flagship store [S: press release, 2025-07-09, https://www.taiwannews.com.tw/en/news/6151900].
- **Home pot-type 炒菜机:** ¥530–4,890 [S: `r19_system_cost.md:180`], about S$100–930 before shipping and GST. The broader market range is ¥500–9,000, with Thermomix-class from ¥5,999 [S: `research/r19_autostir_market.md:20-23`].
- I found no Singapore retail price for a Chinese 炒菜机.
- **5 years:** S$0.4–3.8k including repairs [E], about **S$0.3–2.9 per meal**.
- **What it saves:** stirring and watching one dish at a time while the user preps the next, about **10–25 min per meal** [E]. The user still preps, loads, plates and cleans.
- **Quality:** it covers about 4 of the 7 wok dishes well. The lid stays shut, it cooks at ≤ 230 °C, and there is "no 锅气" [S: `r19_system_cost.md:180`, `:200-203`].

### 2.6 Side by side (5 dinners a week, 5 years, 4 people)

| Option | 5-year cost (S$) | Per meal (S$) | User minutes saved per meal vs by hand | S$ per saved user-hour |
|---|---|---|---|---|
| Cook by hand | groceries only | 0 extra | 0 | — |
| **Robot, FR5, cash** | 37–55k | 28–42 | −25 / **≈ 20** / +66 (≈ 31 with #31) | **≈ 84–126** at 20 min; **54–81** at 31 min; no saving at ≤ 0 min |
| Robot, UR5e, cash | 65–92k | 50–71 | same | ≈ 150–213 at 20 min |
| Robot, FR5 + paid software | 137–355k | 105–273 | same | ≈ 315–820 at 20 min |
| Live-in MDW (cooking share 25–40 %) | 57–93k in total | 11–29 (cooking share) | ≈ 80–120 [E] (all hands-on cooking plus rice) | **≈ 6–22** |
| Part-time cook | 52–117k | 40–90 | ≈ 80–120 [E] | ≈ 20–68 |
| Tingkat | 39–62k incl. food | premium 0–28 | ≈ 90–130 [E] (shopping too) | **≈ 0–21** |
| Delivery app | 65–104k incl. food | premium 15–60 | ≈ 90–130 [E] | ≈ 8–45 |
| Auto-cooker + user | 0.4–3.8k | 0.3–2.9 | ≈ 10–25 [E] | ≈ 1–17 |

---

## 3. Conclusion: where the robot wins, where it loses, and what would change that

**It loses on:**
- **Cost per saved hour.** Even with the cheap arm and no paid software, each saved hour costs more than a part-time cook's wage. Tingkat and a live-in helper cost several times less.
- **Time.** The robot moves work to the user rather than removing it: slot trays, dishwasher loads of about 35 robot items, hand-washing the pads, rescues and weekly upkeep. The worst case is a net loss of time. The user must also stay at home for the whole 46–103 min run.
- **Risk.** Every one of these numbers assumes a meal that works. Today's estimated meal success is 22–78 % [S: `gaps_process.md:64`].

**It wins, or could win, on:**
- **The exact dishes.** The creator's 四菜一汤 cooked fresh at home with the user's own ingredients. Tingkat and delivery give a caterer's menu; an auto-cooker gives no 锅气 and covers about 4 of the 7 wok dishes.
- **No helper.** No live-in person, no spare room, no employer duties.
- **Scale.** At 14 meals a week, the cash cost falls to S$10–15 per meal with the FR5. That is about part-time-cook money per saved hour if the saving reaches 30–60 min.
- **The project itself.** If the user values building it, the cost works out as a hobby budget rather than a value case.

**What would change the verdict:**
1. **Measured minutes from #29.** A by-hand baseline at the high end (≥ 100 min) together with robot-only work at the low end would put the saving at ≥ 45 min.
2. **#31 (robot loads the dishwasher)** removes 8–16 min. Self-checks and a dispenser-filled kettle remove 2–4 min more.
3. **Removing the tray loading.** Bulk bins with a vision pick instead of one item per slot would remove most of R1's 5–10 min.
4. **Reliability.** ≥ 90 % meal success with ≤ 1 rescue per week would bring R10 to ≤ 2 min.
5. **More meals per week, and a cheaper arm.** The Dobot Nova 5 at ¥20.4k average [S: `r19_arm_hand_cost.md:165`] costs about the same as the FR5 but is slower. The arm is not the big lever on the FR5 path.
6. **Counting the user's own build hours** (1,500–3,000 h [E]): the robot cannot win on cost at any meal count.

**Suggested go/no-go gate** (from the #28 issue, for the user to accept or change): **net saving ≥ 30 min per meal at ≥ 90 % meal success, measured over 10 consecutive meals, with cash cost ≤ S$30 per meal.** On the midpoint figures, today's design does not meet this.

---

## 4. Decisions and inputs needed from the user

1. **Meals per week, and which meals** (dinner only, or lunch too). This is the biggest lever on cost per meal.
2. **Household size.** I assumed 4, the reference cook's family.
3. **Does the levy concession apply** (a child under 16, a senior aged 67+, or a disabled person at home)? And is a live-in helper acceptable at all (room, privacy)?
4. **Is tingkat or delivery acceptable for some days?** That is, is "the creator's dishes" a must every day?
5. **How do you value your own time** (S$ per hour)? Do your build and supervision hours count in the value case?
6. **Must someone be at home while the robot cooks?** Plate clearing already requires it today.
7. **Your grocery cost per meal and shopping routine.** This replaces my S$20–35 and 8–17 min estimates.
8. **Accept or change the go/no-go gate** in §3.

## 5. Next steps

1. **#29 trial:** stopwatch every task in §1.2 and §1.3. Replace each [E] with [M]. The by-hand prep and cleanup minutes matter most.
2. **#23:** write the cleaning SOP with minutes per item and a dishwasher-safe check. This replaces R6/R7.
3. **#28 study 3:** consumables and refill schedule in S$ per month, plus noise from product specs.
4. **#28 study 2:** turn §2 into `feasibility/value_case.md`:
   - an FR5 quote and Singapore import costs. Contacting a supplier is the user's decision;
   - an LEW quote for the 20 A point;
   - Singapore prices for fire items.
5. **#31:** once the dishwasher model is known, re-cost R6.
6. **Re-run this ledger** after the user answers §4.
