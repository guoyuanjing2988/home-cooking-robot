# Finger quick-change, long-stroke IP67 grippers, and food end-effectors

Compiled 2026-10-11 by read-only web research. No logins, carts, purchases or messages.

**Source tags**
- **[M]** I read the number in the primary source: a manufacturer page, datasheet or manual, or the paper itself.
- **[O]** secondary: a news item, distributor, search snippet, or a citation inside another paper.
- **abs** I read only the abstract.
- **derived** my own arithmetic, labelled where used.
- **not found** I searched and found no usable number.

**Limits of this round**
- The session's shared WebSearch budget ran out partway through.
- The Taobao read-only search was blocked at a Chrome site-permission prompt that nobody was present to approve, so **no domestic (CNY) prices were collected**.
- Some manufacturer pages could not be fetched: supermagnete, K&J Magnetics and en.dh-robotics returned 403 or refused the connection. Numbers from those sites come from search snippets and are tagged [O].

**Companion files:**
- `finger_design_inputs.md`: PGC-140-50 jaw interface, tomato forces, friction.
- `hand_options.md`: low-force and long-stroke gripper survey, and the UR5e tool-flange current limits.

---

## 1. Finger quick-change systems a robot can swap without a tool changer

### 1.1 Commercial

| System | Mechanism | How the swap is actuated | Capacity | Mass | Price | Src |
|---|---|---|---|---|---|---|
| **Schunk BSWS-R** (automatic jaw quick-change, "-R" = robot) | **Form-fit lock.** Per jaw there are 2 steel adapter bolts (BSWS-AR) screwed to the gripper's base jaw, a base (BSWS-BR) screwed to the finger, and a storage station (BSWS-SR). A spring-loaded pressure bolt in the base latches onto the adapter bolts | "carried out exclusively by the movement of the robot". When the base is pushed into the station, the station actuates the locking bolt and unlocks it. Pick-up procedure from the manual: insert the gripper with its adapter bolts **vertically** and completely into the base sitting in the station, then **move horizontally** out. Return is the reverse. The teach routine must be redone per station, per gripper, and after any collision. Swap time is "less than three seconds" [O] | Not given in the BSWS-R manual ("catalog data sheet"). The same-size manual BSWS adapter pins are rated: **size 50: My 14 N·m, Fx 350 N**; size 64: 29 N·m / 510 N; size 80: 63 N·m / 1080 N; size 125: 225 N·m / 2815 N [M]. Replacement accuracy ±0.02 mm; height ±0.05 mm [M] | Size 50 (my reading of a garbled weight table): base **0.03 kg**, storage station 0.06 kg, adapter bolts 0.01 kg. Maintenance every **1000 changes** (grease the pressure bolt, adapter bolts and spring). Temperature +5 to +130 °C. Stations up to size 100 sit on elastomer mounts "suitable for cobots". Optional inductive sensor for finger-present and an RFID tag for finger identity. Not compatible with "SD" (dust-proof) grippers | not found | [M] Q1, Q2, Q4; [O] Q3 |
| Schunk BSWS / BSWS-M (manual versions) | Same adapter-pin and base interface. BSWS is released with a hex key; BSWS-M is tool-free | By hand | As above. BSWS-UR 50 locking element weighs 0.006 kg | — | not found | [M] Q4 |
| IPR FWS (for IPR CGS2 grippers) | "specially developed locking kinematics", released by one turn of a tool. Builds "up to 60 % lower" than comparable products | By hand only | not found | not found | not found | [O] Q5 |
| SMC MHF2-X7076A ("Air gripper with finger changer function") | Pneumatic MHF2 gripper with a finger-changer feature and separately sold finger assemblies. The snippet says 8 mm bore and 16 mm stroke | "enables various workpieces to be handled by a single robot". The mechanism is **not found** (catalog PDF not reached) | not found | not found | not found | [M] Q6 page (marketing text only); [O] snippet |
| Kurt RV36 | Pneumatic double-acting parallel gripper. "pull-stud technology" for automatic finger change, with sensors confirming fingers and part are in place | Automatic (details not found) | not found | not found | not found | [O] Q7 |
| Zimmer + Schmalz "MATCH" | Changes whole end effectors (gripper modules, vacuum), not fingers. Robot-actuated change in a station, or one-hand manual click | Station | not found | not found | not found | [O] Q8 |
| OnRobot 2FG14 (relevant trick, not a changer) | The supplied fingers bolt on in **two positions, inwards or outwards**. With the same 50 mm stroke this gives external grip ranges of **5–55 mm or 55–105 mm** (internal 17.6–67.6 or 67.6–117.6 mm) | By hand (screws) | Finger platform torque X 30 N·m, Y 25 N·m | Gripper 1.5 kg | see §2 | [M] Q9 |
| Gimatic, Destaco, Sommer, Robotiq, OnRobot (automatic finger change) | **not found**: no robot-actuated finger changer was found for these brands in this round. Robotiq and OnRobot fingertips bolt on by hand | — | — | — | — | — |
| Chinese (夹爪手指快换) | **not found**: the US-only web search returned only Schunk pages and a CSDN article about **whole-gripper** quick-change plates. Taobao was not reachable (see the limits above) | — | — | — | — | [O] |

### 1.2 Academic and DIY

| Work | Mechanism | Actuation | Numbers | Src |
|---|---|---|---|---|
| **Ringwald et al. (TUM) 2022, "Quick-Finger-Exchange" (QFE)**, Franka Panda gripper | Passive and **form-closure**, "similar to a door-locking mechanism". A **spring pre-tensioned "secure stone"** drops into a groove in the finger-base tongue. Finger bases are 3D-printed, and fingertips are printed onto them automatically | Gripper motion only: (1) position the QFE units above the magazine's trigger tongues; (2) press down, and transition levers lift the secure stone; (3) **close the gripper** so the finger-base tongues enter; (4) lift, and the spring drives the stone into the groove | No forces, dimensions or cycle counts are reported. The grasp-stability test pushes the held object against a ring with **5 N** in 2 directions; a pass means it moved **< 5 mm**. All three fingertip types handled 1–5 mm z-offsets. 5–15° rotation offsets were unreliable | [M] P1 |
| **Kramberger et al. (SDU/JSI), CASE 2019**: fingertip exchanger on a Weiss WSG50 and a Schunk PG70, used at WRS 2018 on UR10e | Aluminium housing on the jaw. **Two centering pins** plus a **pneumatic zero-point-style lock**: **normally locked**, it opens only at **6 bar**, so it stays locked on power or air loss. The fingertip base plate has 2 precision guide holes and an M5 locking pin. The lock tolerates about **1 mm** misalignment while coupling | A solenoid valve driven by robot digital outputs. Fingertips rest in 3D-printed nests in a sheet-metal holder. They are released about 3 mm above the nest and self-locate | **1000 couple/decouple cycles at 100 %**. Printed fingertips "for a limited number of cycles"; metal for long-term use. For loads > 30 kg they recommend a full tool changer instead | [M] P2 |
| **Berenstein, …, Goldberg (UC Berkeley), CASE 2018**: open passive tool changer, mostly PLA-printed | Male/female **truncated-cone** kinematic coupling ("high resistance to applied moments"). Two **spring-compressed dowel pins** with ball-bearing rollers lock it. Magnets on a side flange plus steel in the housing locate the tool along x | Purely mechanical: the dowel-pin rollers run up an incline in the tool housing to lock or unlock | **92/100** connects and releases; all 8 failures came from inaccurate arm positioning on a mobile Fetch. 16 s average per change. Open source | [M] P3 |
| **Hu, Wan, Harada (Osaka/AIST) 2019**: passive tool held **by a Robotiq 2F-85** on UR3 | Two symmetric parallelograms. **4 torsion springs** open the tool when the gripper releases and provide friction against dropping. Interchangeable tooltips for screws, washers and deformable cans | The gripper's own close/open drives the tool, with no extra power or vacuum. Pose found from AR markers | Holds up to **8 kg** at a 15° tooltip-to-gravity angle. Best tool-hand angle 23° | [M] P4 |
| Žura (Univ. Ljubljana) 2022, MSc thesis | Four printed prototypes compared: snap-fit, rail guide, index bolt, **ball-lock pin** | Robotic exchange tested | The **ball-lock-pin** design was best on simplicity, reliability, stiffness, size, strength and cost. No numbers in the abstract | [M] abs P5 |
| Maskur, Kiyokawa, Harada 2026 (arXiv) | Self-aligning tool changer: **chamfered receptacles + triangular lead-in guides** for angular and lateral error. Motor-driven coupling. Rotating tool station | — | No numbers in the abstract | [M] abs P6 |
| MakerWorld model (UR5e scale replica, magnetic flange) | One **4 × 3 mm N35** disc magnet in the flange and one in each tool, **2 mm apart** and sealed inside the print. A D-shaped key stops rotation | By hand | The author claims it holds each tool at "16 to 65 times its own weight" | [O] M3 |

### 1.3 Magnet and retention numbers for sizing

| Item | Value | Src |
|---|---|---|
| Shear ("displacement") vs. axial adhesive force | A magnet resists sideways (shear) load with only **about 15–25 %** of its rated pull force. Example: S-15-08-N gives 6.7 kg axial vs **1.45 kg** shear | [O] M1 (search snippet; page 403) |
| Rubber layer in shear | Rubber tape raises shear resistance **2–3×**. Example: S-20-10-N goes from about 1.75 kg to about 5.2 kg | [O] M1 |
| Rated pull test condition | "Case 1" = magnet on a thick steel plate with no air gap. Example: K&J D82B-N52 (12.7 × 3.2 mm) **7.97 lb ≈ 35 N** (derived conversion) | [O] M2 (snippet; page refused) |
| Pull vs. gap | **not found** in this round. Rated forces assume zero gap, while a printed skin of 0.4–1 mm reduces the force substantially (magnitude not sourced) | — |

### 1.4 What this means for a 3D-printed robot-swappable interface on the PGC-140-50 (derived; my design reasoning, not sourced)

The jaw interface, from `finger_design_inputs.md` [M]:
- **per jaw: 2 × M4 + 1 × Ø3 dowel**, in line at 5 mm pitch;
- allowable static **Mx = My = Mz = 7 N·m**;
- Fz 300 N;
- 40–140 N per jaw.

1. **Load path.** Carry grip and payload loads by **form fit**, never by magnets or detents.
   - Grip force F acting at lever L gives a moment F·L. At 140 N and L = 50 mm that is **7 N·m**, which is already the jaw limit.
   - A magnet in shear holds only about 15–25 % of its rating. A 35 N-class magnet therefore resists roughly 5–9 N sideways (derived), far below the 40–140 N grip forces.
   - Make the permanent adapter (bolted to the jaw) a stiff part: aluminium, or printed PA-CF/PETG. Give it a **dovetail or T-slot** plus two Ø3–4 mm steel dowels or flanks that take the shear.
2. **Slide axis.** Make the finger slide on **along the jaw's width axis (Y)**, perpendicular to both the grip direction (X) and the tool axis (Z).
   - The grip reaction (X) and the weight of the held object (Z) then both bear on dovetail flanks.
   - The retainer then only has to resist small Y loads: inertia, bumps, and food friction while the fingers withdraw.
   - If the slide is along Z, the friction from a 2.5 kg cabbage (about 12 N per finger) pulls straight along the release direction.
   - The Schunk BSWS-R uses the same pattern: engage vertically, then exit horizontally with the station holding the finger.
3. **Retainer.** A spring-ball detent, ball-lock pin (best in P5) or spring "secure stone" (P1) is better than magnets alone.
   - Magnets are acceptable as a secondary locator, as in P3, if they work in their **axial** direction along the slide axis, with ≤ 0.5 mm of plastic skin.
   - Suggested target: about 10–20 N to pull the finger off the adapter along Y. This is a judgement, not sourced. It is about 20–40× the weight of a 50 g finger, and the UR5e can easily supply it against a rack hook.
4. **Rack (passive station).** Use a fork or nest per finger, with a chamfered lead-in of about 1–2 mm.
   - P2 captured about 1 mm of error; P6 uses chamfers and triangular guides.
   - For a hook that blocks the finger while the gripper withdraws, use **±Y motion only**.
   - Open or close the jaws **to the parking width** before docking, so both fingers enter their nests together. A separate nest per jaw works as in BSWS-R ("one storage station per gripper jaw").
   - Verify the swap by commanding a small close and reading the PGC position register (0x0202) or the object-detect state (`finger_design_inputs.md`). A missing or misplaced finger changes where the jaws stop.
5. **Range coverage with a 50 mm stroke.**
   - Each finger set covers about 40 mm of object width once 5 mm approach clearance per side is allowed.
   - A **Ø10–200 mm** span therefore needs about **5 offset sets**: ≈ 0–40, 40–80, 80–120, 120–160 and 160–200 mm.
   - OnRobot's **two-position (inward/outward) finger** trick (Q9) halves this: one finger reversed gives two windows. Example: a "small" pair for 0–40/40–80 and a "large" pair for 80–120/120–160, plus a cabbage pair.
6. **Moment check, cabbage pair (derived).**
   - Required grip force: 2.5 kg × 9.81 × SF 2 / (2 jaws × μ 0.5) ≈ **49 N per jaw**. μ = 0.5 is an assumption; measure it on wet leaves.
   - Grip moment: at a finger lever of 100 mm, 49 N × 0.1 m = 4.9 N·m < 7 N·m. OK.
   - Weight moment: about 12 N × an outward offset of about 0.07 m ≈ 0.9 N·m.
   - Feasible, but the margin is thin if the contact sits lower than about 140 mm below the jaw (7 / 49).
7. **Hygiene (inference).**
   - Printed parts are porous. Use smooth PP or PETG, or resin parts that are sealed.
   - Keep the latch geometry open and drainable.
   - Treat printed food-contact fingers as consumables. P2 likewise notes that printed tips last "a limited number of cycles".

---

## 2. Long-stroke IP65+/IP67 electric parallel grippers for a UR5e

★ = IP67 **and** ≥ 80 mm stroke. Rows marked "(HO)" are carried over from `hand_options.md` (sources there); the others were read this round.

| Gripper | Total stroke | Force | Allowable moments / finger limit | IP | Mass | UR integration / power | Price | Src |
|---|---|---|---|---|---|---|---|---|
| ★ **Robotiq Hand-E, 100 mm version** | **100 mm** (50 mm version also sold; adjustable) | **20–185 N per finger**; 40–370 N total | **not found** (the product sheet has none; the manual PDF exceeded the fetch size limit). Form-fit payload **7 kg** | **IP67** | **1.1 kg** (50 mm version 1.0 kg) | "Plug-and-play on top cobot brands"; Modbus RTU RS-485; 20–150 mm/s; 0.2 mm position resolution; 5,000,000-cycle warranty (fingertips excluded) | not found | [M] G1 (product sheet, updated June 2026) |
| Robotiq Hand-E C10 | 40 mm | 25–175 N per finger (40–525 N total) | form-fit payload 10 kg | IP67 | 1.5 kg | Modbus RTU | not found | [M] G1 |
| **DH PGC-300-60** | **60 mm** | **40–300 N per jaw** | **Mx = My = Mz 15 N·m**; Fz 600 N; recommended workpiece 6 kg | **IP67** | 1.5 kg | Modbus RTU RS485 + digital I/O (TCP/IP, USB, CAN, PROFINET, EtherCAT optional). 24 V; **0.4 A nominal / 2 A max**. 2 A sits at the UR tool's ≤ 1 s peak (HO §2), so full force may be limited on UR tool power (derived). Rack and pinion + T-slot guide; 0.8 s open/close | not found | [M] G2 |
| DH PGC-140-50 (current) | 50 mm | 40–140 N per jaw | 7 N·m each axis; Fz 300 N | IP67 | 1.0 kg | — | — | [M] `finger_design_inputs.md` |
| OnRobot 2FG14 | **50 mm** (max 55) | 40–280 N, ±10 N. The datasheet says "The required current is 2000 mA, less current will result in less gripping force" | Torque on finger platform: X 30 N·m, Y 25 N·m | **IP67**; NSF H1 gear grease | 1.5 kg | 20–25 V, up to 2000 mA (HO: UR max 600 mA listed) | not found | [M] Q9 |
| OnRobot 2FG7 (HO) | 38 mm | 20–140 N | 5 N·m | IP67 | 1.1 kg | UR 600 mA | $4,892 [O] | HO |
| Schunk EGK 40-EC (HO) | 83 mm | 55–150 N | Max finger length 100 mm; Mx 8, My 9, Mz 2 N·m | IP67 electronics / **IP20 base jaws** | 0.97 kg | EtherCAT variant; no UR variant of size 40 found | not found | HO |
| Schunk EGU 50-MB (HO) | 102 mm | 150–300 N (Schunk page) | Max finger length 80 mm; Mx 32, My 35, Mz 32 N·m | IP67 electronics (per HO) | 1.44 kg | Modbus RTU; UR5e kit | $4,622 (UR5e kit) [O] | HO |
| DH PGI-140-80 / AG-95 / AG-145 (HO) | 80 / 95 / 145 mm | 40–140 / 45–160 / 35–105 N | 7 / 4.75 / 1.95 N·m | **IP54** | 1.0 / 1.0 / 1.3 kg | — | PGIA-140-80 €1,259.66 excl. VAT [O] | HO |
| OnRobot RG2 / RG6 (HO) | 110 / 160 mm | 3–40 / 25–120 N | not published | **IP54** | 0.78 / 1.25 kg | Tool-flange kit | $5,778 / $6,920 [O] | HO |
| JODELL EPG-L80, Hitbot Z-EFG-100/130, Inspire EG2 (HO) | 80 / 90–120 / 70 mm | — | — | IP40 / IP20 or not found / IP40 | — | — | — | HO |
| JODELL, Inspire, Zhixing, Hitbot (searched for IP65+ ≥ 80 mm) | **not found**. The JODELL product list (EPG, EPG-HP, EPG-L, EPG-T, EPG-ST, EPG-Flex, RG) shows no IP data on its home page. The Hitbot home page shows Z-EFG-C50 (40–140 N), C65 and 20P without IP | — | — | — | — | — | — | [M] G3, G4 (home pages only) |

**Bottom line (derived):** in this survey the **only IP67 electric parallel gripper with ≥ 80 mm stroke that is plug-and-play on a UR5e is the Robotiq Hand-E 100 mm**.
- With 2 offset finger sets it covers 0–200 mm (derived).
- Its minimum of 20 N per finger is still above the tomato limit of ≤ 10 N per finger.
- Schunk EGU 50 (102 mm, UR5e kit) is IP67 only for the electronics. EGK 40 (83 mm) has IP20 base jaws.
- DH's IP67 line tops out at 60 mm (PGC-300-60).
- Within the DH/IP67 family, **finger offsets plus a swap rack** are the realistic route.

---

## 3. Food end-effectors in commercial food robots and the food industry

Rows tagged (re-checked) I re-opened myself in this round. The rest come from a parallel sub-research pass and carry its tags.

### 3.1 How commercial food robots touch food

| Robot | Food interface | Numbers | Src |
|---|---|---|---|
| **Miso Flippy 2** | A parallel gripper clamps a **universal utensil adapter**: a 3D "diamond, sphere, hourglass, or bulb" target on the basket handle. Gripper teeth register in the target's recess; angled faces guide them in. A separate agitator shakes the basket. The AutoBin dispenser fills the basket | It "can self-center and positive lock in same location given **0.75″×0.75″×0.5″** tolerances and **±5 deg**" (≈ 19 × 19 × 13 mm, derived). About 60 baskets/h [O]. A bent handle defeats the grip [O] | [M] F1 (re-checked); [O] F2 |
| **Chef Robotics** | **Quick-change utensils** (scoop types) working from hotel pans on **load scales**. Utensils and pans are the only food-contact parts. Venturi vacuum cup for discrete pieces (chicken breasts, cutlets, pork chops) | 5-min changeover. IP67; 306 stainless + food-grade Delrin; NSF/ANSI 169 [M]. Amy's Kitchen: 30+ trays/min [O] | [M] F3, F4; [O] F5 |
| Dexai Alfred | Ordinary scoops and tongs on a tool-change adapter, working from hotel pans | About 10 s per scoop-and-place; about 1 s utensil swap; about 50 bowls/h | [O] F6 |
| Connected Robotics Delibot | SCARA plus a dedicated hand picks amorphous side dishes from dedicated containers. It **weighs in-hand and re-grasps if outside the weight band** | About 800–850 meals/h for 2 sets across 8 dishes | [O] F7 |
| Spyce / Picnic | No arm touches food: hoppers dose into induction woks (Spyce); dispensers sit over a conveyor (Picnic). Spyce's kale "clumps" took about 3 months of hopper redesign | Up to 200 meals/h; 300 12″ pizzas/h | [O] F8, F9 |
| Moley / Samsung Bot Chef / Nala | Dexterous hands using normal kitchen tools (Moley: Shadow-type hands; Bot Chef: 3-finger hands with knife and spatula). Nala moves woks, with ingredients pre-cut | Demo-level; no grasp numbers | [O] F10–F12 |

**Pattern:** commercial food robots rarely squeeze food with bare jaws. They carry **utensils and containers** (Chef, Dexai, Delibot, Flippy), dispense (Spyce, Picnic), or use dedicated soft, needle or suction end-effectors.

### 3.2 By food class

| Class | Product / work | Mechanism | Numbers | Src |
|---|---|---|---|---|
| **Raw meat / fish** | SINTEF crossed-needle gripper (patent; re-checked) | Pneumatic cylinders drive stainless spring-steel needles that cross inside the fillet. PE-HD block | **12 needles (4 rows × 3), Ø1.5 mm, rows at 30° and 45°, stroke ≈ 32 mm**, needle-cross spacing 6 mm, rows 50 mm apart. Cylinder force ≈ 17 N in / 13 N out at 6 bar. Targets: fish fillets, poultry fillets, small meat pieces, whole fish | [M] F13 |
| | SINTEF/ROBOTNOR follow-up | Crossing-needle, compact-needle and freeze grippers | Accelerations ≤ **2.5 m/s²**: "no observable damage" to salmon, cod and other fillets | [M] F14 |
| | Schmalz SNG-V (not food-marketed) | Crossed needles, double-acting pneumatic | 6 or 10 needles, Ø0.8–1.5 mm, 30°, stroke 0–25 mm, 3–7 bar | [M] F15 |
| | Schmalz mGrip (ex-Soft Robotics, sold to Schmalz 2024) | Pneumatic silicone fingers (2–6); angled-tip fingers slide under thin meat | Up to 120 picks/min; "load capacity up to 10 kg"; 3.0–6.9 bar; finger spacing 20–245 mm; **IP69K**; FDA silicone/POM/stainless | [M] F16, F17 |
| | Raw chicken soft gripper (Rutland 2020, thesis) | Pneumatic fingers + inflatable palm | 63.6 % over > 1000 trials; about 95 % with roughly doubled palm pressure, but the palm burst | [M] abs L1 |
| **Tofu** | Scooping-binding gripper (Wang et al. 2021; re-checked) | **3D-printed PLA scoop plates, 10 mm wide × 1 mm thick, 3 mm bevel**, slid under the food; **Ø3 mm Shore A55 silicone strings at 6 mm pitch** bind from the side. Pneumatic parallel actuator, **60 mm stroke**; opening 84→24 mm or 60→0 mm; 536.8 g | **Tofu (151 g) 5/5**; 17 of 20 foods at 100 %; raw shrimp 80 %, raw oyster 80 %, carangid fish 60 % (they slip through the string-plate gap); takt ≈ 4 s | [M] L2 |
| | Kanazawa fluid fingertips | Rubber bags of viscoelastic fluid; stop while tofu compression is still linear-elastic | Silken tofu 22.7 g, 25 × 25 × 30 mm; fluid pressure 1.5–6.0 kPa; push 4–14 mm at 1 mm/s | [M] F18 |
| | Lands Work tofu robot (Japan) | Vision + special-surface hand | Soft tofu only 1,200–1,500 pcs/h, "if tofu is carried quickly, it breaks" | [O] F19 |
| | CARBS bimanual scoop + pusher (Grannen 2022) | Spoon scoop with a concave pusher | 85.7 % of 14 food classes without breakage; tofu lost 0.44 % of its weight | [M] L3 |
| **Leafy greens / scallion** | Festo DHAS Fin Ray fingers | Passive fin-ray fingers that bolt to standard parallel grippers | Sizes 60/80/120 mm; finger mass 6.5/13/29 g; TPE-U, food-safe (FDA); 10–50 °C | [M] F20 |
| | Ritsumeikan needle-membrane gripper | Grasp mode for shredded/chopped food; pierce mode | Grasped-weight relative SD ≤ 20 %; release after piercing was hard | [M] abs L4 |
| | Bok choy grow-and-twine gripper | Tendon-driven | 4–10 N pull on bok choy | [M] F21 |
| | Scallion-specific gripper | **not found** | — | — |
| **Bulk small** | PFN target-mass grasping (Takahashi et al., RA-L 2021 / ICRA 2022) | Parallel gripper with **spined fork fingertips**. Pre-grasp lift-and-release untangles; a post-grasp vertical pusher strips the excess | **88 % within ±2 g** of target overall, 6 foods, 150 training grasps per food [M, re-checked]. Per food (sub-research): bean sprouts 94–96 %, green onion 92–98 %, shredded cabbage 88 %; baselines < 50 %. 22.5 mm stroke (sub-research) | [M] L5 |
| | Delibot, Chef | Weigh, then re-grasp; scale under the pan | See 3.1 | [O]/[M] |
| | Multi-item grippers (Friedl 2024) | 6-finger constriction / palm + **net** / hybrid / linear scoop | Overall success 75 / 72 / 45 / 41 % on baby carrots, shallots and simulants (summarizer-read; verify) | [M] L6 |
| **Eggs** | Schmalz FG X egg cups; Sanovo, Moba loaders | Silicone suction cups (Sanovo: "gentle two-stage") | Schmalz cups Ø30–35 mm [M]. Sanovo 151,200 eggs/h; Moba 180,000 eggs/h [O] | [M] F22; [O] F23, F24 |
| | Scooping-binding | Scoop + strings | Quail egg 5/5 | [M] L2 |
| | Shell-breaking force for hen eggs | **not found** | — | — |
| **Suction / Bernoulli (cross-class)** | Schmalz SFG flow gripper | High-flow vacuum, FDA silicone | 270–650 l/min; Ø20–60 mm | [M] F25 |
| | Bernoulli (Davis et al. 2008) | Non-contact air flow for tomato and cucumber slices; the flow also removes surface moisture | no numbers seen | [O] L7 |
| | OnRobot Soft Gripper (SG) | Vacuum-driven silicone cups | 2.2 kg max; FDA 21 CFR for **non-fatty foods only** (matters for raw meat) | [M] F26 |

---

## 4. Published work on one gripper (or a small set) for many foods

| Paper | Strategy | Foods | Result | Src |
|---|---|---|---|---|
| Wang, Hirai, Kawamura 2022, *Front. Robot. AI* (review) | Taxonomy by contact surface: top (suction, Bernoulli, needle, freezing), side (fingers, soft), bottom (spatula), and combinations (scoop-binding) | — | **No universal gripper exists**. Suction needs flat, smooth, dry surfaces; needles suit penetrable food; freezing suits moist fish | [M] L8 |
| Wang et al. 2021 scooping-binding | Scoop under + bind | 20 bento items, 9.5–189 g | 17/20 at 100 %; worst were thin slippery seafood | [M] L2 |
| Qiu, Paul, Wang, Hirai, Kawamura 2023, *Foods* (benchmark) | 7 end-effectors: suction; 2-, 3- and 4-finger soft; bladder; scoop-binding | 14 foods, 5 trials each | 2- and 3-finger soft grippers were the most versatile; scoop-binding was best on large or delicate items; suction only on smooth items; **every gripper failed on small kamaboko pieces** | [M] L9 |
| Takahashi et al. 2021/22 (PFN) | Spined parallel jaws + pre/post-grasp manipulation | 6 entangled foods | 88 % within ±2 g | [M] L5 |
| Feng et al. 2019 (SPANet); Gordon 2020; Sundaresan 2022 | Fork skewering with 6 approach angles; vertical for firm food, angled for soft | 16 / 12 / 21 foods (incl. yam, banana, kiwi, lettuce, spinach) | Full plates 83–91 % (SPANet); 71 % visuo-haptic vs 51 % vision-only (Sundaresan) | [M] L10–L12 |
| Grannen 2022 (CARBS) | Scoop + pusher | 14 classes incl. tofu | 85.7 % without breakage | [M] L3 |
| Friedl 2024 | 4 multi-item grippers | small produce | 41–75 % | [M] L6 |
| Kumar, Domae, Wan, Harada 2026 (arXiv) | **Interchangeable fingertip "bits"** per food on one gripper | salmon roe, spaghetti | ≈ 95 % / > 80 % target-weight accuracy | [M] abs L13 |
| Rutland 2020; Davar 2025 (ChicGrasp) | Soft palm gripper; dual-jaw pneumatic + diffusion policy | raw chicken parts; whole carcass | 64 % (about 95 % at higher pressure); 40.6 % | [M] abs L1, L14 |

**Food class → strategy (from the papers above):**

| Food class | Strategy |
|---|---|
| Firm produce | Rigid pinch |
| Fragile or irregular items | Soft or wide pinch, or fin-ray |
| Tofu, cubes, fish cake, eggs | **Scoop/spatula + bind**: support from below, low squeeze |
| Raw meat and fish, yam | **Skewer/needle**: vertical for firm, angled for soft; needs a stripper to release |
| Bulk (sprouts, scallion pieces, shredded) | Spined jaws + shaking + **weigh-and-regrasp** |
| Flat, dry pieces | Suction |
| Wet slices | Bernoulli |
| Small pieces (~10 mm) | **Known weak spot** for every gripper in the benchmark |

---

## 5. Sources

**Finger change**
- Q1 [M] Schunk BSWS-R category page: https://schunk.com/in/en/greiftechnik/zubehoer/bsws-r-pgzn-plus/c/PGR_7219
- Q2 [M] Schunk BSWS-R assembly & operating instructions, doc 1562999 v07.00 (08-2026): https://dev.stb.cloud.schunk.com/media/IM0050017.PDF
- Q3 [O] ETMM: https://www.etmm-online.com/automatic-jaw-quick-change-system-a-7390916b2d33338bede7a265e2c40a90/ ; EPP: https://epp-europe-news.com/technology/products/schunk-introduces-new-robot-jaw-quick-change-system/
- Q4 [M] Schunk BSWS-UR 50: https://schunk.com/ch/it/sistemi-di-presa/accessori/bsws-pgzn-plus/bsws-ur-50/p/000000000000302990 ; BSWS-A 64: https://schunk.com/hu/en/gripping-systems/accessories/bsws-m-pgzn-plus/bsws-a-64/p/000000000000303022
- Q5 [O] IPR FWS: https://www.heilbronn.allaboutautomation.de/en/?p=425305
- Q6 [M] SMC MHF2-X7076A: https://www.smcusa.com/products/actuators/grippers/parallel-2-finger-grippers/parallel-2-finger-grippers/mhf/air-gripper-with-finger-changer-function~168717
- Q7 [O] Kurt RV36: https://mmsonline.com/products/kurts-rv36-robotic-gripper-automatically-changes-fingers
- Q8 [O] Zimmer/Schmalz MATCH: https://www.computer-automation.de/robotics-en/end-of-arm-ecosystem-match-530223.htm
- Q9 [M] OnRobot 2FG14 datasheet v1.3: https://onrobot.com/storage/datasheets/2fg14/datasheet_2fg14_v1.3_en.pdf
- P1 [M] Ringwald et al. 2022, arXiv 2210.10015: https://arxiv.org/abs/2210.10015
- P2 [M] Kramberger et al., CASE 2019: https://hcr.ijs.si/resources/papers/case19b.pdf
- P3 [M] Berenstein et al., CASE 2018: https://goldberg.berkeley.edu/pubs/CASE2018-ron-tool-changer-submitted.pdf
- P4 [M] Hu, Wan, Harada 2019, arXiv 1902.09150: https://ar5iv.arxiv.org/html/1902.09150
- P5 [M abs] Žura 2022, Univ. Ljubljana: https://repozitorij.uni-lj.si/IzpisGradiva.php?id=138549
- P6 [M abs] Maskur, Kiyokawa, Harada 2026, arXiv 2603.04760: https://arxiv.org/abs/2603.04760

**Magnets**
- M1 [O] supermagnete FAQ, adhesive vs shear force: https://www.supermagnete.hu/eng/faq/What-is-the-difference-between-adhesive-force-and-displacement-force-shear-force
- M2 [O] K&J D82B-N52: https://www.kjmagnetics.com/d82b-n52-neodymium-disc-magnet
- M3 [O] MakerWorld magnetic flange model: https://makerworld.com/en/models/3409596

**Grippers**
- G1 [M] Robotiq Hand-E product sheet (updated June 2026): https://robotiq.com/hubfs/Hand-E_Adaptive_Gripper_ProductSheet_EN_2024-11_WEB.pdf
- G2 [M] DH-Robotics catalog EN (PGC-300 page): https://uploads.unchainedrobotics.de/media/file_upload/DH-Robotics-catalog-EN_46faa8dd.pdf
- G3 [M] JODELL home page: https://www.jodell-robotics.com/
- G4 [M] Hitbot home page: https://www.hitbotrobot.com/
- HO = `hand_options.md` (its own sources)

**Food robots and industry**
- F1 [M] Miso patent US11167421B2: https://patents.google.com/patent/US11167421B2/en
- F2 [O] Miso Flippy 2 news: https://info.misorobotics.com/newsroom/miso-robotics-announces-flippy-2-next-generation-flagship-product
- F3 [M] Chef Robotics system: https://www.chefrobotics.ai/solutions/chef-ai-enabled-system
- F4 [M] Chef piece-picking: https://chefrobotics.ai/post/introducing-piece-picking-automating-individual-food-items-from-unstructured-totes
- F5 [O] Amy's Kitchen: https://automationworld.com/process/robotics/article/55131189/amys-kitchen-boosts-yields-and-production-with-chef-robotics
- F6 [O] Dexai Alfred (Boston Globe): https://www.bostonglobe.com/2020/03/05/business/meet-alfred-robot-who-can-help-out-kitchen
- F7 [O] Delibot: https://monoist.itmedia.co.jp/mn/articles/2309/25/news077.html
- F8 [O] Spyce: https://www.technologyreview.com/2018/08/22/240253/engineering-lunch/
- F9 [O] Picnic: https://www.geekwire.com/2019/secretive-seattle-startup-picnic-unveils-pizza-making-robot-heres-delivers-300-pies-hour/
- F10 [O] Moley: https://www.idtechex.com/en/research-article/worlds-first-robotic-kitchen/7720
- F11 [O] Bot Chef: https://www.techradar.com/news/samsungs-bot-chef-made-me-a-salad-at-ces-2020-and-i-ate-it
- F12 [O] Nala: https://hospitalitytech.com/nra-show-news-nala-robotics-introduces-autonomous-bots
- F13 [M] SINTEF needle gripper patent US20070290516A1: https://patents.google.com/patent/US20070290516A1/en
- F14 [M] ROBOTNOR: https://robotnor.no/research/new-gripper-solutions-for-non-rigid-objects/
- F15 [M] Schmalz SNG-V: https://www.schmalz.com/en/vacuum-technology-for-automation/vacuum-components/special-grippers/needle-grippers/needle-grippers-sng-v
- F16 [M] Schmalz mGrip: https://schmalz.com/mgrip
- F17 [M] Schmalz mGrip flyer: https://media.schmalz.com/MAM_Library/Dokumente/Publikation/Flyer/315ffe95df2b_29.01.03.01498_Flyer_VA-CO_mGrip_Übersicht_enEN.pdf
- F18 [M] Kanazawa tofu fluid fingertips: https://kanazawa-u.repo.nii.ac.jp/record/9584/files/TE-PR-WATANABE-T-2016.pdf
- F19 [O] Lands Work tofu robot: https://robohub.org/?p=17297
- F20 [M] Festo DHAS: https://www.landefeld.com/shop/media/festo/gruppendatenblaetter/dhas_en.pdf
- F21 [M] Grow-and-twine gripper: https://cris.huji.ac.il/en/publications/smart-grow-and-twine-gripper-for-vegetable-harvesting-in-vertical/
- F22 [M] Schmalz food: https://schmalz.com/food
- F23 [O] Sanovo OptiLoader Plus 12C: https://www.sanovogroup.com/en/egg/solutions/egg-grading/optiloader-plus-12c/
- F24 [O] Moba egg loader: https://wattagnet.com/egg/egg-production/product/15473217/moba-egg-loader
- F25 [M] Schmalz SFG (same page as F22)
- F26 [M] OnRobot Soft Gripper: https://onrobot.com/en/products/soft-gripper

**Literature**
- L1 [M abs] Rutland 2020: https://open.clemson.edu/all_theses/3399
- L2 [M] Wang, Furuta, Hirai, Kawamura 2021: https://pmc.ncbi.nlm.nih.gov/articles/PMC8032991/
- L3 [M] Grannen 2022 (CARBS): https://arxiv.org/abs/2211.14652
- L4 [M abs] Wang, Makiyama, Hirai 2021: https://www.fujipress.jp/jrm/rb/robot003300040935/
- L5 [M] Takahashi et al.: https://arxiv.org/abs/2201.00933
- L6 [M] Friedl 2024: https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2024.1351932/full
- L7 [O] Davis et al. 2008: https://salford-repository.worktribe.com/output/1435879/an-end-effector-based-on-the-bernoulli-principle-for-handling-sliced-fruit-and-vegetables
- L8 [M] Wang, Hirai, Kawamura 2022 review: https://pmc.ncbi.nlm.nih.gov/articles/PMC8794010/
- L9 [M] Qiu et al. 2023: https://pmc.ncbi.nlm.nih.gov/articles/PMC10670141/
- L10 [M] Feng et al. 2019 (SPANet): https://arxiv.org/abs/1906.02350
- L11 [M] Gordon et al. 2020: https://arxiv.org/abs/1908.07088
- L12 [M] Sundaresan et al. 2022: https://arxiv.org/abs/2211.14648
- L13 [M abs] Kumar et al. 2026: https://arxiv.org/abs/2601.00305
- L14 [M abs] Davar et al. 2025 (ChicGrasp): https://arxiv.org/abs/2505.08986

## 6. Not found / next pass

**Finger changers**
- BSWS-R catalog moment ratings and price.
- Mechanisms and forces for the SMC MHF2-X7076A and Kurt RV36.
- Any automatic finger changer from Gimatic, Destaco, Sommer, Robotiq or OnRobot.
- Chinese 夹爪手指快换 products and all CNY prices: Taobao needs the user to approve the Chrome site permission.

**Magnets and grippers**
- Magnet pull vs. gap data.
- Hand-E allowable moments, maximum finger length and price.
- Any Chinese IP65+ gripper with ≥ 80 mm stroke.

**Foods**
- Hen-egg shell-breaking force.
- Grippers designed specifically for scallions or bean sprouts.
- Numbers for Piab piSOFTGRIP and Bernoulli grippers.
