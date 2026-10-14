# R19 hazard analysis: ISO 12100-style risk assessment and FMEA over the movement library (GitHub #21, 2026-10-14)

Scope: the cart-mounted cobot (UR5e baseline, Fairino FR5 candidate) with a DH PGC-140-50 gripper, cooking meals A/B/C in the user's L-shaped kitchen in Singapore, as designed up to the DECISIONS entries of 2026-10-14. It covers the R19 movement sets, the heaters they serve, and the people and animals who may be in the flat.

Read-only study. This is the only new file. Nothing was bought, no one was contacted, and no git or GitHub action was taken. The issue asks for `feasibility/risk_assessment.md`. This file is the first draft of that document.

**Number tags**
- **[S]**: sourced. A repo `file:line` or a URL is given. Repo paths are relative to `robot_rail/` unless they start with `hcr/`, which means the `home-cooking-robot` repo snapshot.
- **[E]**: estimate or judgement, not measured.
- **[M]**: computed in this study from a repo sim or model. It is not a validated physical measurement.

---

## Answer first

The current "home safety tier" was written for a rail-mounted prep robot whose main hazard was blades (`DECISIONS.md:7-17` [S]). The robot it must now protect is different. It is a 63–67 kg cart (`sim/r10/claude/README_R10.md:8` [S]) whose arm carries a ~180 °C wok with up to 1.15 kg of food, tips hot oil, opens a tap and a fridge, presses blades at ~100 N, and runs a 3.5 kW cooker and four other heaters. The user has to step into its workspace to do the jobs the design leaves to them. No document so far considers children, elderly people, guests or pets.

**Top risks and the design changes they demand** (scale in §4; these are the risks rated High):

| # | Risk | Rating (S×P) | Design change it demands |
|---|---|---|---|
| 1 | **Hot-wok carry, tip and rinse near a person.** The wok is still about **182 °C when it goes under the cold tap** [M, §4.1], about 22 s after the heat goes off. Pressing the E-stop or bumping someone during a 48.9 s chain (`hcr/README.md:66` [S]) can throw hot food, oil or steam. PFL and ISO/TS 15066 limit contact force only. They say nothing about a hot payload. | 4×3 = **12** | Tag every hot-carry set. Allow it only when a **person-free hot zone** is confirmed by a **safety-rated** sensor, not the mmWave/ToF "slow then pause" rule. Rinse only below a temperature threshold, or deglaze on the cooker first. Hand-offs (plates, rice cooker, water) only in declared safe-to-approach states, shown by a lamp. |
| 2 | **Fire from unattended or uncut heat.** The 250 °C limit is application software reading a thermal camera. The knob servo holds its last position if the PC dies. The E-stop scope is undefined. The suppression canister needs 69–89 cm of mounting height, but the hood is only 0.40 m above the cooktop (`research/r15_cooking_market.md:315`, `DECISIONS.md:362` [S]). | 4×3 = **12** | A **fail-off contactor on every heater**, wired to the E-stop, a PC watchdog and a contact-thermocouple high limit. No cloud path to any heater. A written supervision rule: a capable adult at home, and heat off without an acknowledgement. Suppression re-selected for a 40 cm hood. (#19, #22) |
| 3 | **Children and pets are outside every assumption.** A toddler's face at counter height, a cat on the counter, or a child pressing "start". The ISO/TS 15066 limits come from adult subjects. No child limits exist. | 4×3 = **12** | **Exclusion, not limitation.** The robot runs only with the kitchen closed to children and pets (gate or door), a start that needs an adult key or PIN, and presence sensing that also covers the **counter top** and **low zones**, not just the aisle. Blades and tools stay in locked storage. |
| 4 | **Wok drop on E-stop or power loss.** UR tool power drops to 0 V on an E-stop (`research/hand_options.md:93` [S]). The PGC's unpowered hold is undocumented. The jaws run at 6.23–6.47 of 7 N·m (`DECISIONS.md:645`, `hcr/README.md:66` [S]). The fingers are PETG with Tg 80 °C (`research/finger_design_inputs.md:96` [S]). Arm brake data: "ND for all" (`research/r19_arm_hand_cost.md:58` [S]). | 4×2 = **8** | **Palm key plus a mechanical latch**, so the wok cannot fall with the jaws open. Insulating grip block. Written unpowered-hold data from DH and the arm maker. A small UPS so the arm can finish a category-1 stop and set the wok down. (#20, #16, #15) |
| 5 | **Collisions and clamping in shared space.** The arm hangs at 1.12 m (`hcr/README.md:33` [S]), which is head height for children. It sweeps the aisle and is planned only 10 mm from cabinets and doors (`hcr/README.md:53` [S]). The spider grip block sticks out 82 mm past the counter edge at 1.16 m (`DECISIONS.md:567` [S]). Quasi-static clamping has never been assessed. | 3×3 = **9** | Extract **clamp zones** (robot–environment gaps < 50 mm) from the stored swept volumes. In those zones, cap speed and force, or block access. Set UR safety-controller limits (joint, TCP speed, force, safety planes). Pad or park protruding blocks inboard. |
| 6 | **Blades.** The lever cutter is pressed at ~100 N (`DECISIONS.md:136` [S]) with no guard. The 850 W meat-slicer option has "no interlock data" (`sim/r10/claude/R19_PREP_AUDIT.md:320` [S]). Blade plates are stored in drawers. | 3×3 = **9** | Interlocked guard on the lever cutter: the arm cannot press while the cover is open or a hand is detected. Only interlocked powered cutters, switched by the robot's contactor, not a smart plug. Lockable blade storage. |
| 7 | **Water, electricity and floor.** The tap is left running by design (`DECISIONS.md:392` [S]), so a crash or power loss leaves it open next to a tethered cart and a 20 A circuit. A floor datum rail (`sim/r10/claude/R19_DOCK.md:29` [S]) and the tether are trip hazards for elderly people. | 3×3 = **9** | Tap open only while the arm is at the sink, or a leak sensor plus a battery-backed shut-off valve (this conflicts with the "no valve" decision, so the user decides). Flush or covered rail and tether. Splash map. 30 mA RCD per circuit. |
| 8 | **The safety functions are not safety functions.** The presence pause, 250 °C limit, half-power rule and plume rule are all application logic on non-rated sensors (`sim/r10/claude/R19_MOTION_LIBRARY.md:176,188` [S]). There is one E-stop on the unit and none at the plating side. The ¥18k allowance (`research/r19_system_cost.md:62` [S]) is a budget, not an analysis result. | 3×3 = **9** | Map each function to the UR safety controller (PLd Cat 3, `research/r19_arm_hand_cost.md:42` [S]) or to a rated relay or contactor. Keep only comfort functions in app code. Write an **E-stop matrix** (arm, gripper, cart, heaters, tap, pumps). Add a second E-stop at the plating and serving side. If the FR5 is chosen, its safety PL must be documented first. |

**What the user must accept or do** (information for use, §7): keep children and pets out of the kitchen while the robot runs; stay at home and acknowledge prompts; approach only when the green lamp is on; never reach past the plating guard; keep the gate shut. Seven questions for the user are listed at the end.

---

## 1. Method

- **ISO 12100 sequence:** determine the limits of the machine (§2), identify hazards per lifecycle phase (§3.1) and per movement-set family (§3.2), estimate the risk (§4), and reduce it in the 3-step order: inherent design, then safeguarding, then information for use (§5).
- **FMEA** (§6): component and function, failure mode, effect, S / O / D, RPN, action, issue.
- **Task list:** the 34 movement sets of `sim/r10/claude/R19_MOTION_LIBRARY.md:442-463` [S], grouped into 11 families, plus the heaters.
- **Standards used as references, not compliance claims:**
  - ISO 12100 (method);
  - ISO 13482 (personal care robots; the 2026-10-07 basis);
  - ISO/TS 15066 (PFL body limits; now carried into ISO 10218-2:2025 Annex M per [arXiv 2602.17822](https://arxiv.org/pdf/2602.17822) [S]);
  - ISO 13855 (separation distance);
  - ISO 13849 (performance levels);
  - IEC 60335-1 / -2-x (appliances);
  - ISO 13732-1 (contact burns).
- **Not done here:** clause-by-clause applicability (issue step 3), the sim studies (issue step 4) and the hardware tests (issue step 5). §9 lists what to file.

## 2. Limits of the machine

### 2.1 Use limits

| Item | Content |
|---|---|
| Intended use | Cook home-style Chinese meals (four dishes, one soup, rice) end to end. Prep: washing, peeling, appliance cutting, lever pressing, marinating, soaking. Seasoning cups. Wok stir and plating. Wok rinse at the sink. Pot-zone lid, spider and carrier. Fridge cold-box fetch. |
| Left to the user | Loading trays, the cold box, water containers and the rice cooker. Restocking bulk seasonings. Clearing plates from the 2 plating spots (`DECISIONS.md:421-425` [S]). Serving, soups included. Cleaning. |
| Duration | Meals 38.6–75.6 min (`hcr/README.md:81-83` [S]), plus 21–40 arm-min of prep (`hcr/README.md:85` [S]). 1–2 meals a day [E]. Service life 5–10 years [E]. |
| Reasonably foreseeable misuse | Reaching in while it runs (to taste, clear a plate early, rescue dropped food). Leaving the flat while it cooks. A child starting it or playing with the cart. A cat on the counter. Leaning on or riding the cart. Placing objects on hub or plating spots. Cleaning the arm while it is powered. Bypassing a slicer interlock. Starting heat from the MIoT app. |

### 2.2 Space limits

- **Kitchen:** L-shaped. The sink is on the other leg from the hob, so the hot-carry route to the sink is **not yet modelled** (`hcr/README.md:126` [S]). Real dimensions are pending (#11).
- **Hood:** 0.40 m above the cooktop (`DECISIONS.md:362` [S]).
- **Cart:** runs along a floor datum rail with station stops and a 50 N docking pin (`sim/r10/claude/R19_DOCK.md:29,156` [S]). Travel range x −1.48…2.46 m (`R19_DOCK.md:75` [S]). Tethered to an off-board controller (#18).
- **Arm:** mounted at 1.12 m, tilted 20° (`hcr/README.md:33` [S]). Reach 850 mm (UR5e) or 922 mm (FR5) (`research/r19_arm_hand_cost.md:42-43` [S]). Together with the cart, the envelope covers the whole counter front and reaches into the aisle.
- **Heights where people meet the robot [E]:** counter ≈ 0.90 m; arm and wok path ≈ 0.95–1.4 m. That is face and chest height for children aged about 2–8, and hand or chest height for adults.

### 2.3 Who may be present

| Group | Assumed abilities [E] | Why it matters |
|---|---|---|
| User (adult, trained) | Reads the HMI, knows the safe states | Enters the workspace by design |
| Other adults, domestic helper, guests | Untrained. May not read the language of the prompts | No mental model of when the robot moves |
| Elderly | Slower reaction and walking. Reduced sight and hearing. Higher fall risk | Trip hazards (rail, tether, wet floor). Slower avoidance than ISO 13855's K values assume |
| Children 1–3 y | Climb, grab, pull cords. Head at about counter height | Below and inside the presence sensors' "aisle" model. No 15066 limits. Thinner skin burns faster ([PMC11076053](https://pmc.ncbi.nlm.nih.gov/articles/PMC11076053/) [S]: child scald thresholds are not established) |
| Children 4–12 y | Curious. Press buttons. Reach into machines | Start button, slicer chute, lever cutter, open fridge |
| Pets: cats | Jump onto counters [E] | Counter top is unsensed. Hot zone. Blade stations |
| Pets: dogs | Underfoot. Chew cables [E] | Cart wheels, rail, tether |
| Service technician | Trained | Maintenance with the power on, brake release |

## 3. Hazard identification

### 3.1 Per lifecycle phase

| Phase | Main hazards |
|---|---|
| Transport, installation | 63–67 kg cart: tipping and crushing during handling. Drilling for the rail. New 20 A point, which needs a LEW (#24). Electrical installation errors |
| Commissioning | First runs with real heat and food. Teach-pendant work inside the envelope. Untuned monitors (torque thresholds not yet recorded, `R19_MOTION_LIBRARY.md:172` [S]). All sets need re-checking in the real kitchen (`R19_MOTION_LIBRARY.md:252` [S]) |
| Setup before a meal | The user loads trays, the cold box and water containers next to a powered, idle robot. Accidental start |
| Normal operation | All of §3.2 |
| Process interruption and recovery | E-stop with a hot wok in the air. Restart needing a hub match (`R19_MOTION_LIBRARY.md:185` [S]). Manual brake release next to hot items. Tap left open |
| Cleaning | Blades, the hot wok and cooker, the arm still powered, water on electrics. Oil mist on an IP54 arm |
| Maintenance | Finger swaps (pinch), tube replacement, servo knob adjustment, firmware and network changes (cyber) |
| Decommissioning | Oil, batteries (UPS if added), blades |

### 3.2 Per movement-set family

Sets as named in `R19_MOTION_LIBRARY.md` (§3, §8, §9). "Exposed" uses: U = user, A = other adults and elderly, C = children, P = pets.

| Family (sets) | Hazards | Exposed | Notes and evidence |
|---|---|---|---|
| **F1 Wok carry, plate, tip, rinse, dump, fill, oil pour-out** (WOK_PLATE_RINSE, WOK_DUMP_RINSE, WOK_FILL, oil tip) | Burns: contact with a ~180 °C wok [M §4.1], hot food and oil splash, steam burst at the cold tap. Impact from 4.48 kg held at 223 mm (`DECISIONS.md:643` [S]). Drop. Spill beyond the guard (9–19 % of rigid pieces miss the plate, `README_R10.md:561` [S]; sauce not simulated). Oil tipped 90° toward the robot or aisle into a loose cup (`README_R10.md:521` [S]). Cart moving with the wok out (allowed, `DECISIONS.md:385` [S]) | U A C P | ≈22 s from heat-off to "under the tap" [M]. The user's plating spots lie on the tip path |
| **F2 Stir** (SPATULA_FETCH, STIR_CYCLE, SPATULA_STOW) | Oil spatter. Food flung (0 of 8 seeds with the default cycle, `DECISIONS.md:595` [S]). Jam spikes above 7 N·m (`DECISIONS.md:597` [S]) that can make the spatula slip. 0.45 m spatula sweeping. Overheating while the arm is busy (half-power rule in software, `README_R10.md:532` [S]) | U C P | The STIR_CYCLE pre-condition "nobody within reach of the wok" (`R19_MOTION_LIBRARY.md:165` [S]) has no sensor behind it |
| **F3 Seasoning cups, pour drum, 泼油** | Hot-oil pours over food (5 dishes, `README_R10.md:496` [S]). Cup dropped on a hot surface. Liquids not simulated | U C | Cup sets not yet verified (#5, #9) |
| **F4 Pot zone** (LID_OFF_TO_RACK, spider, carrier, kettle pours) | Steam on lid lift and carrier removal. Hot food on the spider. The **2.5 kg kettle of boiling water** has unchecked grasp and pours (`DECISIONS.md:390` [S]). Spider block 82 mm past the counter edge at 1.16 m (`DECISIONS.md:567` [S]) | U A C | Scald: 60 °C water gives a full-thickness burn in about 1–5 s ([raisingchildren.net.au](https://raisingchildren.net.au/babies/safety/burns-scalds-fire/scalds-prevention), [NSW Kids Health](https://kidshealth-old.schn.health.nsw.gov.au/sites/default/files/hot_water_and_scalds_april_2019_final.pdf) [S]). Boiling water is far beyond that |
| **F5 Plating hand-off** | The user reaches into the plating spot next to the wok tip path. Hot plates | U A C | No hand-off protocol exists (#21 problem) |
| **F6 Prep: knife-free appliances** (lever press, slicer chute, meat slicer, chopper, egg cracker, peeler) | Cuts and crush: lever cutter ~100 N with no guard (`DECISIONS.md:136` [S]). Powered slicer 250 W with a lid interlock (`R19_PREP_AUDIT.md:209` [S]). Meat slicer 850 W, interlock unknown (`R19_PREP_AUDIT.md:320` [S]). Chopper on a smart plug (`R19_PREP_AUDIT.md:339` [S]). Blade plates in drawers | U A **C** P | The arm's force is deliberately allowed to reach 100 N here, so PFL does not protect a hand in the cutter |
| **F7 Sink and faucet** (FAUCET_OPEN/CLOSE, washing, basket) | Tap left open on a fault, causing flooding and a wet floor near the tether and power. Hot wok steam at the sink. Splash onto the arm (IP54) and the cart | U A C P | `DECISIONS.md:392` [S]. The route on the real L is unmodelled |
| **F8 Fridge** (door open 35°, cold-box fetch) | Arm pulls against a 100 N seal on a 14 kg door (`hcr/README.md:114` [S]). The door swings into the aisle and can hit or trap a person or pet between door and cabinet | U A C P | The door can be blocked by a person. No force-monitored contact (#26) |
| **F9 Cart travel and docking** | Wheel over a foot or paw. Pinch between the cart and a cabinet or the docking stops. Pin at 50 N (`R19_DOCK.md:156` [S]). Tip-over (no tip in any modelled stop, `sim/r10/claude/R19_CART.md:35` [S]). Trips on the rail and tether. Cart at 0.25 m/s (`README_R10.md:99` [S]) | U A C P | The tip analysis is rigid-body, with 4 constants still estimated (`R19_CART.md:57` [S]) |
| **F10 Transits and free moves** (hub-and-spoke TRANSITs) | Transient impact on a head or chest in the aisle. Quasi-static clamping against the upper cabinets, hood or fridge door. Plans keep only 10 mm to the environment | U A C P | Joint speeds up to 180 °/s (`r19_arm_hand_cost.md:42` [S]). Body limits in §4.2 |
| **F11 Heaters** (not arm sets; served by them) | Fire. Unattended heat (`README_R10.md:617` [S]). Remote cloud start (MIoT zone 2 and rice cooker, `r19_system_cost.md:69,71` [S]). Fryer with 2 L of oil at 150–190 °C (`r14_storage_market.md:281` [S]). Knob servo holding its last position. Dry-burn cut-off only "typical" ≈ 280 °C (`r15_cooking_market.md:77` [S]) | everyone in the flat | 318 of 1,051 SG home fires in 2025 came from unattended cooking (`r15_cooking_market.md:38` [S]) |
| Cross-cutting | Electrical: the 20 A point, water. Cyber: cloud heaters and the cobot TCP interface. Hygiene (see #23). Noise and steam (#15) | | |

## 4. Risk estimation

**Scale** (simple, stated) [E]:
- **Severity S:**
  - 1 = first aid;
  - 2 = medical treatment, minor burn or cut;
  - 3 = serious: deep burn, fracture, finger loss, hospital;
  - 4 = fatal or life-changing, or a house fire.
- **Probability P** combines how often a person is exposed, how often the hazardous event happens, and whether the person can avoid harm:
  - 1 = very unlikely over the service life;
  - 2 = possible;
  - 3 = likely at some point over the service life;
  - 4 = expected repeatedly.
- **Risk R = S × P:**
  - **High ≥ 8**: must reduce before any household use;
  - Medium 4–6: reduce as far as practicable;
  - Low ≤ 3: accept, and inform the user.

### 4.1 Wok temperature at the rinse [M]

`heat15.py`'s lumped model (constants copied unchanged into a scratch script) was run with:
- heat off at the start of WOK_PLATE_RINSE;
- food at 60 °C in the wok for 10 s until it is tipped onto the plate, then an empty wok;
- the set's own step times, which put the wok under the tap at 22.4 s (sum of steps, `R19_MOTION_LIBRARY.md:300-312` [S]).

| Wok at heat-off | At the tap (22.4 s) | 30 s | 49 s | Passive cooling to 100 / 80 / 60 °C, empty wok |
|---|---|---|---|---|
| 200 °C | **182 °C** | 179 °C | 171 °C | 318 / 453 / 664 s |
| 250 °C (the robot's limit) | **225 °C** | 220 °C | 209 °C | 396 / 530 / 742 s |

These numbers come from an unvalidated 0-D model with no water in the wok. The conclusion holds anyway. **The wok meets cold water at 180–225 °C**, which flashes the water to steam and spatters the oil residue. Air cooling to a "touch-safe" level takes 7–11 min. That is too long to wait at every plating, so the rinse needs a design answer. Options:
- deglaze on the cooker under the hood with jug water;
- rinse in a splash-shielded basin;
- rinse after the next dish.

### 4.2 Reference body limits

- **ISO/TS 15066 maximum permissible force** (adult): hand and fingers 140 N, face 65 N, skull and forehead 130 N. Source: secondary reproduction, [arXiv 2311.13814 Table 1](https://arxiv.org/pdf/2311.13814) [S]. Verify against the standard before using these values as settings.
- **Derivation:** the limits come from studies on adult subjects ([DGUV FP-430](https://www.dguv.de/projektdatenbank/0430/ab_18.12.2019_fp430_englisch.pdf), [Control Design](https://www.controldesign.com/articles/2016/robots-allowed-contact-with-humans) [S]). **There are no values for children or animals**, so PFL cannot be claimed as protection for them.
- **Lever press vs body limits:** the ~100 N lever press is within the 140 N hand limit only on paper. The press is a cutting process, so a blade turns that force into a cut.
- **Contact burns:** bare metal at about 70 °C burns in about 1 s, and about 43 °C is the limit for prolonged contact. Source: secondary summary of ISO 13732-1, [inzonex](https://inzonex.co.uk/insulation/safety/hot-surface-standards/) [S, verify]. The wok, its handle, the spider and lids are all far above this.
- **Separation distance, ISO 13855 form:** S = K·T + C, with K = 1600 or 2000 mm/s ([Leuze](https://www.leuze.com/en-us/navigation/0942f478ebd948d9b0b7c4c7734c3714), [Keyence](https://www.keyence.com/ss/products/safetyknowledge/caution/) [S]).
  - T = sensor response + arm stop time. Assume mmWave/ToF response 0.1–0.5 s [E].
  - UR5e J0 deceleration ≈ 19 rad/s² (`R19_CART.md:36` [S]). From 180 °/s (π rad/s) that gives a stop of about 0.17 s [E, derived].
  - T ≈ 0.3–0.7 s therefore gives **S ≈ 0.5–1.1 m + C** [E].
  - The hot zone around a wok carry therefore spans **the whole aisle**. In practice, "nobody in the kitchen during hot-carry sets" is the requirement, not "pause when someone is within reach".

### 4.3 Risk register (before additional measures)

Measures that exist today: PFL cobot, plating guard, slicer lid interlock, software 250 °C limit, mmWave/ToF pause as proposed, one E-stop.

| ID | Family | Hazardous situation | Exposed | S | P | R | Main reduction (step) | Residual R |
|---|---|---|---|---|---|---|---|---|
| H1 | F1 | Person in the aisle or at the plating spot during a hot carry or tip. Protective stop or contact causes hot spill or splash | U A C | 4 | 3 | **12** | Hot-carry tag; rated person-free zone; safe-to-approach states (2) | 4 (S4×P1) |
| H2 | F1 | Steam and oil spatter when a 180–225 °C wok meets the tap | U A C | 3 | 4 | **12** | Rinse threshold or deglaze on the cooker (1); splash shield (2) | 3 |
| H3 | F1 | Wok drops on an E-stop or power loss (gripper unpowered, fingers softened) | U A C P | 4 | 2 | **8** | Palm key + mechanical latch, insulating block (1); UPS for an SS1 set-down (2) | 4 |
| H4 | F1 | Oil pour-out into a loose cup misses, tips or overflows | U C | 3 | 3 | **9** | Fixed funnel-fed container with a level check (1); container-present check (2) | 3 |
| H5 | F2 | Oil spatter or flung food during stir; spatula slips on a jam | U C P | 2 | 4 | **8** | Splash ring (1); force monitor, keyed spatula (2); nobody at the wok (2) | 4 |
| H6 | F4 | Kettle (2.5 kg boiling) or pot pour scalds someone | U C | 3 | 2 | 6 | Verify the set; locking-lid kettle (1); hot-carry tag (2) | 3 |
| H7 | F4/F10 | Head bump on a protruding block (spider 82 mm at 1.16 m) or on the moving arm | A C | 2 | 3 | 6 | Park inboard and pad (1); speed limit (2) | 2 |
| H8 | F5 | User reaches to the plating spot while the wok is tipping | U A | 3 | 3 | **9** | Safe-to-approach lamp; hand-off only at a parked hub (2); second E-stop (2) | 3 |
| H9 | F6 | Hand or finger in the lever cutter during a 100 N press | U C | 3 | 3 | **9** | Interlocked cover (2); presence check at the cutter (2) | 3 |
| H10 | F6 | Child or user uses or cleans a powered slicer or chopper; interlock missing or bypassed | U C | 3 | 2 | 6 | Interlocked models only, powered through the robot's contactor (1, 2); locked blade storage (3) | 3 |
| H11 | F7 | Tap left open: flood, wet floor, water on power | U A C P | 3 | 3 | **9** | Tap opened only at the sink (1) or leak sensor + valve (2) | 3 |
| H12 | F8 | Person or pet between the fridge door and the cabinet; door swings into someone | U A C P | 2 | 2 | 4 | Force-monitored pull, presence check (2) | 2 |
| H13 | F9 | Cart runs over a foot or paw, pinches against a cabinet or docking stop | U A C P | 2 | 3 | 6 | Wheel guards, edge switches (2); low docking speed (1) | 2 |
| H14 | F9 | Trip on the rail or tether, especially elderly people; fall near a hot cooker | A | 3 | 3 | **9** | Flush or covered rail, overhead or covered tether (1) | 3 |
| H15 | F10 | Quasi-static clamping of a hand or head against upper cabinets, hood or fridge door | U A C | 3 | 2 | 6 | Clamp-zone map; reduced speed and force in zones (2) | 3 |
| H16 | F10 | Transient impact on a child's head or face in the aisle | C | 3 | 3 | **9** | Exclusion of children (gate, start key) (2, 3); presence covering low zones (2) | 3 |
| H17 | F11 | Oil fire: overheating while unattended, controller crash, thermal-camera error | everyone | 4 | 3 | **12** | Fail-off contactors, thermocouple high limit, watchdog (2); supervision rule (3) | 4 |
| H18 | F11 | Cloud or remote start of a heater, or the fryer left on | everyone | 4 | 2 | **8** | Local-only control; heater enable only via the contactor; drop the fryer (1) | 4 |
| H19 | All | Pet on the counter enters a hot or blade zone | P | 3 | 3 | **9** | Exclusion (3); counter-top sensing (2) | 3 |
| H20 | All | E-stop does not stop heat, tap or cart; not reachable from the plating side | U A | 3 | 3 | **9** | E-stop matrix, second E-stop (2) | 3 |
| H21 | All | Restart or manual brake release beside a hot wok | U | 3 | 2 | 6 | Restart procedure; set down before release (3) | 2 |

**Residual risk:** H1, H3, H17 and H18 stay at 4 (S4 × P1). That is acceptable only together with the information-for-use measures in §7 and a hardware test showing the safeguards work. Anything still High after the measures needs a user decision, for example dropping the fryer or the sink rinse.

## 5. Risk reduction in the 3-step order

### Step 1: inherent design (remove or reduce the hazard)

1. **Rinse cold, not hot.** Deglaze the wok on the cooker with jug water (under the hood, where steam is extracted), or rinse only below a threshold, for example ≤ 80 °C [E] by the thermal camera. A cold rinse is ~7.5 min of passive cooling from 200 °C [M], so in practice deglaze, then rinse later or in a shielded basin.
2. **Palm key + mechanical latch** on the wok and spatula blocks, so the jaws only lock and gravity cannot free the wok (`r19_arm_hand_cost.md:222` [S] proposes the key). Insulating grip block (PEEK or phenolic) or a metal wok finger set (#15).
3. **Oil pour-out into a fixed, funnel-fed, lidded container**, not a loose cup.
4. **Reduce hot-carry distance and duration.** Keep the hot wok low (the lowest path the checker allows), and do not move the cart with a hot wok out unless the zone is clear. The user allowed cart moves with the arm out (`DECISIONS.md:385` [S]). This analysis recommends restricting that permission for hot loads.
5. **Drop the fryer**, or treat it as a separate project (#22).
6. **Faucet:** open only while the arm is at the sink, or fit a self-closing (timed or push) tap.
7. **Remove protrusions into the aisle:** spider block, tool handles, the plating-stand guard edge.
8. **Speed and force:** lowest practical speeds in the shared space; free transits at reduced TCP speed. Jerk-limited stored paths already exist (#40).
9. **Heater choice:** a cooker that defaults to OFF after a power cycle; no cloud-only heaters.

### Step 2: safeguarding and complementary measures

| Function | Proposed realisation | Rated? | Issue |
|---|---|---|---|
| Person-free hot zone during hot-carry sets (F1, F4 pours, oil tip) | Safety-rated area scanner or safety radar covering the aisle **and low zones**, muting allowed only in idle states; 10-07 clause allows it "where a specific hazard cannot be handled otherwise" (`DECISIONS.md:16` [S]) | yes (PL d target [E]) | #21 new |
| Speed and separation outside hot sets | UR safety controller: reduced mode triggered by the zone sensor; safety planes at the counter front | yes (UR PLd Cat 3 [S]) | new |
| PFL limits | Configure UR force, power and momentum limits to 15066 adult values in the aisle; treat the clamp zones separately | yes | new |
| Clamp zones | Extract from stored swept voxels (gaps < 50 mm); lower the speed in those zones, or add guards or covers | design | new |
| Heat off on fault | Contactor per heater; E-stop, watchdog, thermocouple high limit, stove guard | yes (PL to be assigned, ISO 13849) | #19 |
| E-stop | Matrix per device; second E-stop at the plating and serving side; stop category per phase (SS1 to set the wok down) | yes | #20 |
| Gates and interlocks | Kitchen gate or door contact in the start chain; lever-cutter cover interlock; slicer interlock powered through the contactor | yes for the cutter and gate | new |
| Safe-to-approach signal | 3-colour lamp + audible cue: green = arm parked at a hub, nothing hot in hand; amber = moving; red = hot carry or blade, keep out | comfort (not relied on alone) | new |
| Water | Leak sensor + battery shut-off valve (user decision) | — | new |
| Cart | Wheel guards, edge switches, brakes holding on power loss (`R19_DOCK.md:168` [S]) | — | #14, #39 |

### Step 3: information for use

See §7. Information only addresses residual risk. It is never the main measure for H1, H9, H16, H17 or H19.

## 6. FMEA

Scales [E]:
- **S** (severity) 1–10;
- **O** (occurrence over the service life) 1–10;
- **D** (detectability before harm; 10 = undetectable) 1–10;
- **RPN** = S × O × D.

**Rule: any S ≥ 9 is a priority whatever its RPN**, because RPN under-weights rare, severe events.

| # | Component / function | Failure mode | Effect | S | O | D | RPN | Action | Issue |
|---|---|---|---|---|---|---|---|---|---|
| 1 | PGC gripper / hold wok | Grip lost when tool power drops to 0 V on an E-stop (`hand_options.md:93` [S]) | Hot wok and food fall ~1 m [E] onto the floor or feet | 10 | 4 | 8 | 320 | DH written data; palm key + latch; 20× power-cut test | #20, #16 |
| 2 | Presence sensor (mmWave/ToF) | Misses a small child, crawling child or cat; blind on the counter top | Hot carry continues into a person | 9 | 5 | 8 | 360 | Rated sensor; ray-cast coverage in MuJoCo; exclusion | #21 |
| 3 | Thermal camera / 250 °C limit | Reads low (emissivity on bare steel) | Oil above its smoke point (190–234 °C, `README_R10.md:508` [S]); fire | 9 | 5 | 6 | 270 | Contact thermocouple high limit, hardwired to the contactor | #19, #25 |
| 4 | Cooker knob servo | Holds the last position when the PC dies | Unattended heat up to the dry-burn cut-off | 10 | 4 | 6 | 240 | Contactor + watchdog; cooker off after a power cycle | #19 |
| 5 | Grip block / PETG fingers | Soften (Tg 80 °C) on a hot handle | Slip, wok drop | 9 | 4 | 6 | 216 | Thermal estimate + thermocouple test; insulating block | #15 |
| 6 | E-stop circuit | Scope undefined; heaters, tap and cart keep running; unreachable from the plating side | Hazard continues after the stop | 9 | 4 | 6 | 216 | E-stop matrix; second E-stop | #20, #19 |
| 7 | Wok rinse | Wok at 180–225 °C into cold water [M] | Steam burst, oil spatter at the sink, wok warp | 6 | 8 | 4 | 192 | Deglaze or threshold; splash shield | #21 |
| 8 | Zone 2 MIoT / rice cooker / smart plugs | Cloud command, or a smart plug failing to switch off | Remote start, unattended heat | 9 | 3 | 7 | 189 | Local-only; contactor; VLAN | #22 |
| 9 | Fire suppression | Canister mounted outside its 69–89 cm range (40 cm hood) | Fire not suppressed | 10 | 2 | 9 | 180 | Re-select a product for a 40 cm hood | #22 |
| 10 | Fryer | Oil overheats or the basket is loaded wet | Oil fire or boil-over | 10 | 3 | 6 | 180 | Drop the fryer, or assess it fully | #22 |
| 11 | Oil pour-out | Cup missing, misplaced or overfull | Hot oil on the counter or floor | 8 | 4 | 5 | 160 | Fixed funnel container + level check | new |
| 12 | Plating tip | Sauce or liquid beyond the guard (not simulated) | Hot food on the user's hand or the counter | 6 | 6 | 4 | 144 | Splash test (water, then oil); hand-off states | #21 |
| 13 | Lever cutter / press | Arm presses with a finger under the pusher | Crush or laceration | 8 | 3 | 6 | 144 | Interlocked cover; presence check | new |
| 14 | Kettle pour set | Unchecked grasp; lid opens; drop | Boiling-water scald | 8 | 3 | 6 | 144 | Verify the set; locking-lid kettle; hot-carry tag | #9 |
| 15 | Faucet set | Tap left open after a crash or power loss | Flood; water on power; slip | 7 | 4 | 5 | 140 | Tap only at the sink; leak valve | #20 |
| 16 | Arm brakes | Do not hold in the 20° tilted mount on power loss (data ND, `r19_arm_hand_cost.md:58` [S]) | Arm sags with the wok | 9 | 2 | 7 | 126 | Vendor document; test | #20 |
| 17 | Transit set | Quasi-static clamp against a cabinet or door (10 mm plan gap) | Hand or head trapped | 6 | 3 | 7 | 126 | Clamp-zone extraction; speed and force caps | new |
| 18 | Presence sensor | False trips; arm pauses holding the wok mid-air | User approaches a stopped hot arm; prolonged hold | 7 | 6 | 3 | 126 | Defined safe-hold pose (set down); red lamp | #20 |
| 19 | Stir / spatula hold | Jam (seed 8 above 7 N·m, `DECISIONS.md:597` [S]) | Spatula slips; food or oil flung | 6 | 4 | 5 | 120 | Force monitor; keyed coupling | #16, #26 |
| 20 | Hub / scene-version check | Layout changed; stale path executed | Collision | 6 | 3 | 5 | 90 | Scene-version gate (exists in the proposal); commissioning dry run | #9 |
| 21 | Floor rail / tether | Trip | Fall near the hot cooker | 7 | 4 | 3 | 84 | Flush rail; covered or overhead tether | #18, #39 |
| 22 | Cart drive / docking pin | Wheel over a foot; pinch at a stop; pin 50 N on a paw | Bruise or crush | 5 | 4 | 4 | 80 | Wheel guards; edge switch; slow docking | #14, #39 |
| 23 | Powered slicer / meat slicer | Interlock missing or bypassed | Laceration | 8 | 2 | 5 | 80 | Interlocked models only; contactor | #35 |
| 24 | Fridge door set | Person or pet in the door's path; door released at 35° | Bump or pinch | 4 | 3 | 5 | 60 | Force-monitored pull; presence check | #26 |
| 25 | Spider rest | Block 82 mm past the counter at 1.16 m | Head bump | 3 | 4 | 3 | 36 | Inboard park or padding | #37 follow-up |

**Priority by S ≥ 9 regardless of RPN:** rows 1–6, 8–10 and 16. Together they make up the "hot payload + heat" cluster that the Answer-first table names.

## 7. Children, elderly people and pets

**Position:** the robot cannot be made safe for children or pets by force limitation. ISO/TS 15066 contains no child values, hot payloads are outside its scope, and child scald thresholds are not established ([PMC11076053](https://pmc.ncbi.nlm.nih.gov/articles/PMC11076053/) [S]). The strategy is therefore **exclusion while the robot runs, plus safe idle states**.

| Hazard for this group | Design measure | User measure |
|---|---|---|
| Child at face height near the hot wok or a moving arm (H1, H16) | Rated zone sensor covering low zones; robot will not start or continue a hot set with any detection | Gate or door closed; no child in the kitchen during a run |
| Child starts the robot or presses buttons | Adult key switch or PIN to start; heaters only via the robot's contactor | Keep the key away from children |
| Child pulls the tether, plays with or climbs the cart | Tether covered or overhead; cart brakes on; no step-like surfaces [E] | Do not let children play near the cart |
| Child fingers in the lever cutter, slicer chute or chopper | Interlocked covers; blade plates in locked storage | Lock the storage; never bypass an interlock |
| Cat on the counter, in a hot or blade zone (H19) | Counter-top detection (camera or zone sensor) pauses non-hot sets and blocks hot sets from starting; covered blade stations | Keep pets out of the kitchen; no food left out to lure them |
| Dog underfoot, chewing cables | Wheel guards; cable covers | Keep dogs out |
| Elderly person: slow avoidance, trips, poor sight or hearing | Lamp plus sound; flush rail; slow transits; second E-stop | Clear the floor; know the E-stop |
| Guest or helper who does not know the robot | Clear signage; start interlocked to the gate | Brief them; do not run the robot during visits [E] |

**What the user must do** (information for use, draft):
1. Start the robot only with an adult at home who can respond. Acknowledge the periodic prompt, or the robot turns the heat off and parks.
2. Close the kitchen gate or door. Children and pets stay out until the green lamp says "safe".
3. Approach the plating spots, rice cooker or water containers only when the lamp is green (arm parked, nothing hot in hand).
4. Never reach past the plating guard or into the cutter or slicer. Never bypass interlocks.
5. Know both E-stops. After an E-stop, do not release the brakes or the gripper by hand while the wok is hot. Follow the restart card.
6. Keep the floor around the cart dry and clear. Report any leak or water on the floor.
7. Do not start heaters from a phone app. Do not leave the flat while the robot cooks.
8. Monthly [E]: test the E-stops, the gate contact and the smoke and heat alarms. Inspect the fingers, grip blocks and cable for heat damage.

## 8. Open questions for the user

1. **Who lives in or visits the flat?** Children (ages), elderly people, a domestic helper, pets (cat or dog)? This sets which measures in §7 are mandatory.
2. **Can the kitchen be closed off** (door or gate) while the robot runs, and will you accept that the robot will not start unless it is closed?
3. **Supervision rule:** will you accept "a capable adult at home, with acknowledgements every N minutes, otherwise heat off", and no remote start of heat or motion?
4. **Hot rinse:** accept deglazing on the cooker (and/or a later rinse) instead of putting the hot wok under the tap? A cold rinse at the tap means ~7.5 min of cooling [M].
5. **Cart moves with a hot wok out:** may this permission be withdrawn for hot loads (zone-cleared moves only)?
6. **Budget:** the ¥18k allowance probably needs to cover a safety-rated scanner or radar, contactors, a safety relay and a UPS. Is a higher safety budget acceptable if the analysis requires it? Prices were not checked here.
7. **Faucet:** keep the open-tap design (with a leak sensor and valve, which reverses "no valve"), or open the tap only while the arm is at the sink?

## 9. Next steps / issues to file

Laptop:
1. **DECISIONS entry (user):** re-baseline the safety tier. Name hot oil, hot-wok carries, fire, and children and pets as primary hazards (issue step 2).
2. **Hot-carry tagging + person-free zone design:** tag sets in `library_examples.json` and model ray-cast sensor coverage of the aisle, low zones and counter top in MuJoCo (issue step 4). New issue.
3. **Clamp-zone extraction** from `swept_voxels.npz` (robot–environment gaps < 50 mm) with 15066 limits per zone. New issue.
4. **Rinse policy:** add the §4.1 calculation to the meal model; compare deglazing vs waiting; add a wok-temperature pre-condition to WOK_PLATE_RINSE. Could be part of #21 or new.
5. **Safe-to-approach states and the hand-off schedule** in `meal16.py`, plus the lamp HMI. New issue.
6. **Lever-cutter guard and interlock; oil pour-out container.** New issue, or fold into #35.
7. **Standards applicability matrix** (ISO 13482, ISO/TS 15066, IEC 60335-2-x, ISO 13849, ISO 13855) (issue step 3). New issue.
8. **Safety-function mapping** to the UR safety controller or rated relays, and the E-stop matrix: fold into #19 and #20. If the FR5 is chosen, add its safety PL and functions to #2.

Hardware, later:
- the arm stopping distance with the wok load;
- splash tests with water, then oil, on the tip and rinse paths;
- a power-cut test on the PGC;
- a thermocouple on the grip block (#15, #20).

Related open issues that this analysis feeds: #9, #14, #15, #16, #18, #19, #20, #22, #23 (hygiene, not covered here), #24, #25, #26, #35, #39.

---

### Sources (web, read-only, 2026-10-14)
- ISO/TS 15066 body values (secondary): [arXiv 2311.13814](https://arxiv.org/pdf/2311.13814); background: [DGUV FP-430](https://www.dguv.de/projektdatenbank/0430/ab_18.12.2019_fp430_englisch.pdf), [Control Design 2016](https://www.controldesign.com/articles/2016/robots-allowed-contact-with-humans); Annex move to ISO 10218-2:2025: [arXiv 2602.17822](https://arxiv.org/pdf/2602.17822)
- ISO 13855 formula (vendor summaries): [Leuze](https://www.leuze.com/en-us/navigation/0942f478ebd948d9b0b7c4c7734c3714), [Keyence](https://www.keyence.com/ss/products/safetyknowledge/caution/)
- Scald times: [raisingchildren.net.au](https://raisingchildren.net.au/babies/safety/burns-scalds-fire/scalds-prevention), [NSW Kids Health](https://kidshealth-old.schn.health.nsw.gov.au/sites/default/files/hot_water_and_scalds_april_2019_final.pdf), [PMC11076053](https://pmc.ncbi.nlm.nih.gov/articles/PMC11076053/)
- Contact burn threshold (secondary, verify against ISO 13732-1): [inzonex](https://inzonex.co.uk/insulation/safety/hot-surface-standards/)
