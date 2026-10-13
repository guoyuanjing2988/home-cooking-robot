# R19: cheaper arm and hand that keep (or improve) smooth motion

Compiled 2026-10-13. Read-only web research (WebSearch / WebFetch only). No logins, no carts, no supplier contact, nothing bought. Two small read-only scripts were run against the saved R17/R18 chain results (Section 2.3). No existing file was changed.

**Labels.** [M] = manufacturer datasheet, manual, official page or official repo. [O] = other (distributor, marketplace, news, search-result snippet). [E] = my estimate or derivation. **ND** = not published / not found. Source keys in brackets point to the list at the end.

**Prices.** All prices were seen on 2026-10-13 and are **unconfirmed**. Domestic CNY list prices for cobots are rarely public; where only a foreign price exists it is converted with the project's usual rates (1 USD ≈ 7.1, 1 EUR ≈ 8.3 CNY) for order of magnitude only.

---

## 0. Bottom line

1. **The arm is where the money is.** The UR5e costs about **¥150k–180k** in China [P1, P2, P3]. A domestic 5–6 kg cobot with UR-type kinematics costs **¥20k–60k** [F3, D1]. The gripper (≈ €2.1–2.3k in the EU for the PGC-140-50 [G2, G3]) and the cart drive (≈ $200–250 per hub wheel [C1]) are small by comparison.
2. **Cheapest credible swap: Fairino FR5** at a published ¥23,800 terminal guide price (March 2023) [F3]. It has the same 180 °/s joints as the UR5e and nearly the same link lengths. Its weak points are the **±175° wrist-3 (J6) range**, which 5 of the 7 saved chains exceed, IP54, and a 0–45 °C ambient rating.
3. **Best sim transfer and best for steam and oil: Elite CS66.** It is almost a UR5e twin (d1 identical, a2/a3 within 2 mm), ±360° joints, **IP65 standard (IP68 option)**, 6 kg payload and a UR-style SDK. But J1–J2 are only 150 °/s on the datasheet, so the stir is about 7–13 % slower [E], and its China price is ND.
4. **Best on-controller playback of stored motions: Dobot (CR5A; Nova uses the same protocol)** and **Fairino**. Both can store a dense joint trajectory file on the controller and replay it with speed scaling. That is the most direct fit for the user's "many predefined movements → movement sets, no check after every tiny movement". Dobot CR series average selling price was ¥56.8k in 2025 [D1].
5. **Hand:** the cheaper parallel grippers either lack force (≤ 60 N; the cold box needs ≥ 96 N), lack IP rating, or have **lower** moment limits than the PGC. A **palm key** (a fixed key on the flange adapter that carries the tool's moment, with the jaws only locking it) takes the wok and spatula moments off the jaws. It is a robustness gain, not a cost saving. Keep the IP67 PGC-140-50, or take the **PGC-300-60** (15 N·m, 60 mm, IP67) if the arm has payload margin.
6. **Found in the saved results (a playback issue for any arm, including the UR5e):** the stored `play` joint arrays contain **exact 360° jumps** between consecutive states (2π-equivalent poses) on up to 4 joints per chain. A real controller would turn these into full-turn spins or limit faults. Any exporter must unwrap them first (Section 2.3).

---

## 1. What the current design asks of the arm (from the project's own results)

| Requirement | Value | Source |
|---|---|---|
| Held load at the plating tip | 2.95 kg held; **4.15 kg of the 5 kg payload** with the gripper and fingers | README_R10 R15 §6 |
| Joint torque | max **0.629** of the UR5e's rated-payload envelope (mount tilt −20°) | `results/r17/chain_wok_s-1_final.json` |
| Stir working-part peak joint speeds (5 strokes, max over strokes) | J1 59, **J2 168**, J3 100, **J4 184**, J5 72, J6 128 °/s | `results/r15/stirwalk2_h_scrape_dice_r17.json` (per-stroke `work.vmax`) |
| Stir period | 2.63 s = 2.4 s × (184/180) × 0.76 + 0.77 s return (returns planned at 180 °/s, 360 °/s² trapezoid, an assumption) | `r15stirwalk2.py` lines 21, 65, 95–96 |
| Wok tip | ≤ 2.0° of joint per degree of tip → ≤ 90 °/s of tip at 180 °/s | README_R10 R15 §6 |
| Ambient near the wok | arm kept ≥ 0.20 m from the wok axis; plume estimate about 90 °C on the axis 30 cm above, near ambient 20 cm off it; UR5e rated 0–50 °C | README_R10 R15 §3 |
| Mount | hung from a cantilever beam at 1.12 m, tilted 20° | README |

---

## 2. Arms

### 2.1 Specifications

| Arm | Payload | Reach | Arm mass | Max joint speed (°/s) J1…J6 | Joint ranges | Repeat. | IP (arm) | Collision / force limiting | Src |
|---|---|---|---|---|---|---|---|---|---|
| **UR5e (baseline)** | 5 kg | 850 mm | 20.7 kg incl. cable | 180 all | ±360° all | ±0.03 mm | IP54 | 23 configurable safety functions, PLd Cat 3; flange F/T sensor ±50 N / ±10 N·m | [A1] [M] |
| **Fairino FR5** | 5 kg (max 7 kg) | 922 mm | ≈ 22 kg | 180 all (URDF: 3.15 rad/s J1–J3, 3.2 rad/s J4–J6) | J1 ±175°, J2 +85/−265°, J3 ±160°, J4 +85/−265°, J5 ±175°, **J6 ±175° (±360° optional)** | ±0.02 mm | **IP54 (IP65 optional)** | per-axis collision sensitivity levels 1–10; protective stops 0/1/2 [O F4] | [F1] [M], [F2] [M] |
| **Elite CS66** | 6 kg | 914 mm | 20 kg | **150/150/180/230/230/230** (datasheet); URDF says 180 all | ±360° all (URDF: elbow ±180°) | ±0.03 mm | **IP65 (IP68 upgradable)** | 27 safety functions, PLd Cat 3 [E7] | [E1] [M], [E3] [M] |
| Elite CS66A (CSA series) | ND (6 kg class) | ND | 21 kg | shoulder/elbow 210; wrists 410/470/470 | ±360° all | ±0.02 mm | **IP68** | ND | [E6] [O] (2023-08-03) |
| **Dobot CR5A** | 5 kg | 900 mm | 25 kg | 180/180/180/223/223/223 | ±360° except J3 ±160° | ±0.02 mm | IP54 | 5 adjustable collision levels | [D3] [O] |
| Dobot Nova 5 | 5 kg | 850 mm | 14 kg | **100 all** | J1, J4–J6 ±360°, J2 ±180°, J3 ±160° | ±0.05 mm | IP54 | ND | [D2] [M] |
| JAKA Zu 5 | 5 kg | 954 mm | 23 kg incl. cable | 180 all | J1 ±360°, J2 −85/+265°, J3 ±175°, J4 −85/+265°, J5–J6 ±360° | ±0.02 mm | IP54 | ND | [J1] [O] |
| AUBO i5 | 5 kg | 887 mm | 24 kg | 220 (J1–J3) / 230 (J4–J6) | ±175° all | 0.05 mm (others say 0.02) | IP54 [O] | ND | [AU1] [O] |
| Han's Elfin E05 | 5 kg | 800 mm | 25 kg | 135 | ND | 0.03 mm | IP54 | ND | [H1] [O] |
| Han's/Huayan Elfin-Pro E05-Pro | 7 kg | 800 mm | 25 kg | 180 (J1–J4) / 200 (J5–J6) | ND | ±0.02 mm | **IP66** | ND | [H2] [M] |
| Rokae xMate CR7 | 7 kg | 988 mm | ≈ 25–27 kg | 180/180/234/240/240/300 | ND | ±0.02 mm | **IP67** (controller IP54) | joint torque sensors on all axes [O] | [R1] [M], [R2] [O] |
| Realman RM65-B | 5 kg | **610 mm** | 7.2 kg (controller integrated) | 180 (J1–J2) / 225 (J3–J6) | ND | ±0.05 mm | IP54 | ND | [RM1] [O] |
| UFACTORY 850 | 5 kg | 850 mm | 20 kg | 180 | J1 ±360°, J2 ±132°, J3 −242…3.5°, J4 ±360°, J5 ±124°, J6 ±360° | ±0.02 mm | arm ND (IP40 is listed for the gripper only) | ND | [X1] [M] |
| UFACTORY xArm 6 | 5 kg | **700 mm** | 12.2 kg | ND | ND | 0.1 mm | ND | ND | [X3] [O] |
| UFACTORY Lite 6 | 0.6 kg (memory, not re-checked) | — | — | — | — | — | — | — | excluded: payload far below the 4.15 kg need |

**Brakes:** no candidate's arm brake behaviour was verified in this round (ND for all, UR5e included). The 2026-10-08 decision accepts "the manufacturer's documented power-loss holding in the chosen mounting orientation"; that document must be obtained per model before buying.

**Excluded as drop-ins:** Realman RM65 (610 mm) and xArm 6 (700 mm) are too short for the 850 mm-class layout, and every station would move. Lite 6 has too little payload. Nova 5 (100 °/s) and Elfin E05 (135 °/s) are kept in the tables, but they slow the stir badly (Section 2.4).

### 2.2 Kinematics compared with the UR5e

All the shortlisted arms are the same UR-type 6R topology: a shoulder offset, two parallel long links, and three wrist joints with offsets. So the existing solver, checker and chain machinery carry over unchanged. What changes is the numbers: link lengths, wrist offsets, collision capsules, joint windows and speeds. Every saved path must therefore be **re-run, not re-used**.

| DH (m) | d1 | a2 | a3 | d4 | d5 | d6 | Type |
|---|---|---|---|---|---|---|---|
| **UR5e** [A2] | 0.1625 | −0.425 | −0.3922 | 0.1333 | 0.0997 | 0.0996 | [M] |
| **Elite CS66** [E2] | 0.1625 (0) | −0.4270 (+2.0 mm) | −0.3905 (−1.7) | 0.1475 (+14.2) | 0.0965 (−3.2) | 0.0920 (−7.6) | [M] |
| **Fairino FR5** [F2] | 0.152 (−10.5) | −0.425 (0) | −0.39501 (+2.8) | 0.1021 (−31.2) | 0.102 (+2.3) | **ND** (URDF has no flange offset) | URDF joint origins [M]; mapping to DH is mine [E] |
| **Dobot CR5A** [D5] | 0.147 (−15.5) | −0.427 (+2.0) | −0.357 (**−35.2**) | 0.141 (+7.7) | 0.116 (+16.3) | 0.105 (+5.4) | `cra_description/urdf/cr5_robot.xacro` origins [M]; mapping [E] |
| AUBO i5 [AU2] | base→shoulder 0.122, shoulder lateral 0.1215 | 0.408 (−17) | 0.376 (−16.2) | (in the shoulder offset) | 0.1025 | 0.094 | URDF frames differ from UR's; mapping not attempted |
| Dobot Nova 5 [D5] | ≈ 0.24 | ≈ 0.40 | ≈ 0.33 | ≈ 0.13 | ≈ 0.12 | ≈ 0.088 | values came back rounded from the fetch; re-read the xacro before use |

(Numbers in brackets = difference from the UR5e in mm.)

**Transfer verdict [E]:**
- **CS66:** almost direct. The largest change is a 14 mm wrist-1 offset and an 8 mm shorter flange. Expect most IK branches to survive. Re-check every chain; reserves of 2–3 mm (stir, wok) may move either way.
- **FR5:** close in the long links. But d4 (wrist offset) is 31 mm shorter, which changes the wrist's swept volume near the hood, the faucet and the cabinet doors. The joint windows also need attention (Section 2.3).
- **CR5A:** the forearm is 35 mm shorter and d5 16 mm longer, so this is a meaningful re-plan, though in the same topology.
- **xArm 850 / Elfin / Rokae:** DH not collected. The xArm family is not UR-type, so a full re-plan.

### 2.3 Saved checked chains against the candidates' joint windows (computed here)

Scripts (read-only, in the session scratchpad, not in the repo) loaded the `play` arrays of 7 saved chains: wok (final and R18 plate 2), lever, lid, spider, and the spatula rest and flat runs. 470 + 470 + 16 + 205 + 516 + 249 + 256 states.

**Finding 1: 360° jumps in the stored paths.** Between consecutive stored states there are exact ±360.0° steps:
- wok: J2, J4, J5 (2 each);
- lid: J1, J6;
- spider: J1, J4, J5, J6;
- spatula runs: J1, J2, J6.

These are the same pose numerically (the joins wrap Δq to ±π, as `transfer()` in `r15stirwalk2.py` does), but **commanded literally on hardware they are full-turn spins**. After `np.unwrap` the real spans are small (wok J4 86°, J6 148°; lid J6 153°; spider J6 187°; spatula-flat J6 185°). The playback exporter must unwrap and pick the 2πk offset that keeps every joint inside the robot's window. The lid chain's J2 unwraps to 304–359° (1° from the UR's +360° limit), so it should be shifted by −360°.

**Finding 2: window test after unwrapping.** This assumes the candidate uses the UR joint zero and sign convention. FR5's URDF frames match ur_description's layout; the elbow zero is "straight" for all. J1 is tested by span only, because the base mount yaw is a free design choice.

| Chain | FR5 stock (J6 ±175°) | FR5 with the ±360° J6 option | CS66 (elbow ±180°) | CR5A (elbow ±160°) |
|---|---|---|---|---|
| wok final / wok R18 plate 2 | ✗ J6 | ✓ | ✓ | ✓ |
| lever | ✗ J6 | ✓ | ✓ | ✓ |
| lid | ✗ J6 | ✓ | ✓ | ✓ |
| spider | ✗ J4 | ✗ J4 (needs −299.6…−268.3°; the window allows −265…85°, so it misses by ≈ 4–7°) | ✓ | ✓ |
| spatula rest (roll) | ✓ | ✓ | ✓ | ✓ |
| spatula flat | ✗ J6 | ✓ | ✓ | ✓ |

The stir cycle could not be tested: its result file stores only per-stroke peak speeds, not the joint path. JAKA Zu 5 and AUBO i5 have similar ±175°-about-a-centre windows, but their zero conventions were not confirmed, so they were not tested.

### 2.4 Estimated stir period per arm [E]

Method: the project's own formula, `period = 2.4 s × max(1, maxⱼ vⱼ/Vⱼ) × 0.76 + return`, with the measured per-joint peaks (J2 168, J4 184 …) and each arm's per-joint limit Vⱼ. The return is scaled by 180/V of the slower joints. This **assumes the same joint motion**, which holds only roughly for near-UR kinematics, so it is a ranking, not a result.

| Arm | Binding joint | Est. period | vs 2.63 s |
|---|---|---|---|
| UR5e | J4 184/180 | 2.63 s (as checked) | — |
| FR5, JAKA Zu 5, Elfin-Pro E05-Pro | J4 184/180 | ≈ 2.63 s | 0 |
| Dobot CR5A, AUBO i5 (220/230), Rokae CR7 | none above its limit | ≈ 2.6 s | −1 % |
| Elite CS66A | none | ≈ 2.5–2.6 s | −2 to −6 % |
| **Elite CS66** (datasheet 150 °/s J1–J2) | J2 168/150 | ≈ 2.8–3.0 s | +7 to +13 % |
| Elfin E05 (135 °/s) | J4 184/135 | ≈ 3.5 s | +33 % |
| **Dobot Nova 5** (100 °/s) | J4 184/100 | ≈ 4.7 s | **+80 %** |

For scale: the parallel cost study counts about 247 strokes over the three reference meals (`research/r19_system_cost.md`). So +0.3 s per stroke is about +1.2 min of arm time per three meals, and Nova 5's +2.1 s is about +8.6 min (before that file's 1.3 pause factor).

### 2.5 Controller and power (matters on a tethered cart)

| Arm | Controller | Input | Power | Src |
|---|---|---|---|---|
| UR5e | 460 × 449 × 254 mm, 12 kg, IP44 | 100–240 VAC | 570 W max | [A1] [M] |
| FR5 | **245 × 180 × 44.5 mm, 2.1–2.5 kg** | **30–60 VDC (2 kW) or 100–240 VAC** | 276 W average, 410 W peak | [F4] [O]. fairino.us lists "130 × 60 × 66 mm, 490 g" as the controller, which looks like a different box (ND) |
| CS66 | 505 × 432 × 257 mm, IP54 | 100–240 VAC | 250 W typical | [E1] [M] |
| CR5A | ND | **48 VDC** | 150 W | [D3] [O] |
| Nova 5 | **200 × 120 × 55 mm, 1.3 kg** | **30–60 VDC** | 230 W typical, 770 W max | [D2] [M] |
| JAKA Zu 5 | 410 × 235 × 307 mm, IP44 | 100–240 VAC | 350 W average | [J1] [O] |
| AUBO i5 | 380 × 350 × 265 mm, 15 kg | 100–240 VAC | ND | [AU1] [O] |
| UFACTORY 850 | AC box 345 × 135 × 101 mm, 4.8 kg; DC box 262 × 160 × 76 mm, 2.8 kg | AC, or 48–72 VDC | 240 W typical, 1000 W max | [X1] [M] |
| Elfin-Pro | ND ("1000 Hz communication", 48 V DC output) | ND | 180 W typical | [H2] [M] |
| Realman RM65 | inside the arm base | 24 VDC | 100 W typical, 200 W max | [RM1] [O] |

The small DC-input controllers (FR5, Nova, CR5A, UFACTORY DC) could ride on the cart. That would shorten the tether to one DC feed, but it is a design option, not a requirement. The current design keeps the controller off-board.

### 2.6 Trajectory interface: how smoothly can stored motions be replayed?

| Arm | Streaming (servoJ-like) | Blends between waypoints | Whole-trajectory upload / on-controller playback | ROS 2 | Python | Src |
|---|---|---|---|---|---|---|
| **UR5e** | RTDE at **500 Hz**; `servoj` with t down to 2 ms (e-Series) | `movej/movel/movep` with blend radius r | **Trajectory point interface:** the host forwards timed points (positions plus velocities) and the robot interpolates them with splines, or with movej/movel and a blend radius. No file playback on the controller | official driver | ur_rtde (third party), URCL | [A3] [M], [A4] [M], [A5] [O] |
| **Fairino FR5** | ServoJ (period ND here) | PTP smooth time, LIN smooth radius | **TrajectoryJ:** upload a joint trajectory file to `/fruser/traj/`, `LoadTrajectoryJ(name, ovl 0–100 %)`, `MoveTrajectoryJ()`, speed and force override during playback. **LoadTrajectoryLA:** look-ahead preprocessing with Bezier smoothing and max velocity/acceleration/jerk. Spline and N-Spline groups | frcobot_ros2 | official SDK (also C++/C#/Java) | [F5] [M], [F6] [M], [F7] [M] |
| **Elite CS66** | `writeServoj`, default **8 ms**, look-ahead 0.03–0.2 s | blend radius in trajectory points | `writeTrajectoryPoint(positions, time, blend_radius)` and a trajectory control action. Same design as UR's client library | official ROS 2 driver (ros2_control) | C++ SDK; Python ND | [E4] [M], [E5] [M] |
| **Dobot CR5A / Nova 5** | `ServoJ(t ≥ 0.004 s, aheadtime 20–100, gain 200–1000)`, **recommended 33 Hz (30 ms)** | CP ratio 0–100 or radius r on MovJ/MovL | **StartPath:** replays a trajectory file stored on the controller. Sample interval 8–1000 ms; speed multiplier 0.25–2; filter `freq` in (0, 1], where 1 means no filtering and "perfectly restores the recorded trajectory". Feedback every 8 ms (port 30004) | DOBOT_6Axis_ROS2_V4 (MoveIt trajectory → ServoJ point by point) | TCP/IP API | [D4] [M], [D5] [M] |
| JAKA Zu 5 | ND here | ND | ND | ND (not verified) | ND | — |
| AUBO i5 | SDK with JSON-RPC and RTDE (C++/Python) | ND | ND | ND | yes | [AU3] [O] |
| UFACTORY 850 / xArm | `set_servo_angle_j`, **250 Hz max**, no buffer | `set_position(radius=…)` | ND (teach recording exists; file upload not verified) | xarm_ros2 | official SDK | [X2] [O] |

### 2.7 Prices (all unconfirmed)

| Arm | Price | Basis | Src |
|---|---|---|---|
| **UR5e** | **¥180,000** (arm 140,000 + controller 30,000 + pendant 10,000) | university procurement result, 2022-12-13 | [P1] [O] |
| | ¥170,000 "参考价" for UR3e/UR5e/UR10e | reseller listing, date ND | [P2] [O] |
| | ¥150,000 "全新价格" | second-hand listing, snippet only | [P3] [O] |
| | US$34,527 | Vention, snippet | [P4] [O] |
| **Fairino FR5** | **¥23,800** terminal guide price (FR3 ¥22,800) | Fairino news, March 2023 price conference | [F3] [M] |
| | ¥18,000 FR5-SPARK | 2023 student programme, 1,000 units, not general sale | [F3] [M] |
| | US$6,999 incl. control box and button box (pendant +$800) | top3dshop | [F4] [O] |
| **Dobot CR series** | **¥56,800 average selling price (2025)**; ¥59,700 (2024); ¥66,000 (2023) | HKEX filing digest (Tiger Brokers, 2026-07-08); mix of CR models and channels, not a CR5A list price | [D1] [O] |
| **Dobot Nova series** | **¥20,400 average selling price (2025)**; ¥27,000 (2024) | same | [D1] [O] |
| Dobot CR5A | US$24,320 | top3dshop | [D3] [O] |
| Elite CS66 | **China ND**. Elite range FOB $12k–35k (Q1 2026) | EVS ranking | [M1] [O] |
| JAKA Zu 5 | China ND; €7,846–8,108 (EU marketplace, snippet); JAKA range FOB $12k–36k | | [J2] [O], [M1] [O] |
| AUBO i5 | China ND; €18,600 ex VAT | Unchained | [AU1] [O] |
| UFACTORY 850 / xArm 6 | US$8,999 / US$8,849 | snippet / top3dshop | [X4] [O], [X3] [O] |
| Realman RM65-B | US$30,630 / CA$18,226 (inconsistent) | RobotShop snippet | [RM1] [O] |
| Rokae CR7, Elfin-Pro | ND | | |
| Market context | 2024: "6 kg six-axis lowest 2万多; 5 kg cobots lowest under ¥30k; some six-axis cobots below ¥10k". 2023 average for six-axis cobots: ¥97,300. 2026: industrial-robot prices reported **rising 5–15 %** | news | [M2] [O], [M4] [O] |

### 2.8 Cheaper kinematics (4/5-axis, SCARA + tilt wrist): not credible here [E]

- **5-axis arm** (e.g. xArm 5, about US$5.3k [O, snippet]):
  - The wok tip *toward the robot* is a pitch motion, so it is possible.
  - But the tool's yaw is tied to the base azimuth, so the stir lines (yaw 0/+30° at chosen offsets), the fridge door arc (35°, the grip must yaw with the door), sideways approaches and in-box grasps lose a degree of freedom.
  - It is also not cheaper than an FR5 at China prices.
- **Collaborative SCARA plus a tilt wrist:**
  - Domestic cobot SCARAs are in the 0.75–3 kg class.
  - The wok alone is 2.95 kg, before the gripper and the wrist motor.
  - The Z stroke (a few hundred mm) cannot span counter, fridge bin and upper-cabinet seasoning ports.
- **If the goal is to take the wok off the arm,** the credible route is a mechanism at the cooker (a motorised tilt cradle, which the parallel cost study also lists). That is outside this topic.

---

## 3. Hand

### 3.1 Parallel grippers with ≥ 50 mm stroke (moment limits as published)

What the hand must do today:
- 40–140 N per jaw (force mode ≥ 40 N; ≥ 96 N for the wet cold box);
- IP67 near the wok and sink;
- jaw moment **6.47 of 7 N·m** on the wok;
- 6.4 N·m estimated on a 100 N fridge seal;
- napa cabbage limited to 1.7 kg heads.

| Gripper | Stroke | Force per jaw | Mx / My / Mz (N·m) | IP | Mass | Price seen | Verdict | Src |
|---|---|---|---|---|---|---|---|---|
| **DH PGC-140-50 (current)** | 50 mm | 40–140 N | 7 / 7 / 7; Fz 300 N; recommended workpiece ≤ 3 kg | IP67 | 1.0 kg | €2,268 ex VAT (welectron); €2,119 (-W, openelab); **China ND** | baseline | [G1] [M], [G2] [O], [G3] [O] |
| **DH PGC-300-60** | 60 mm | 40–300 N | **15 / 15 / 15**; Fz 600 N; ≤ 6 kg | IP67 | 1.5 kg | US$2,590 / €2,589 | **upgrade**: 2.1× the moment for about +€470; +0.5 kg | [G1] [M], [G4] [O] |
| DH PGI-140-80 | 80 mm | 40–140 N | 7 / 7 / 7 | IP54 | 1.0 kg | PGIA (with brake) €1,259.66 ex VAT | about €1,000 cheaper and +30 mm stroke, but IP54 | [G1] [M], [G13] [O] |
| DH AG-160-95 | 95 mm | 45–160 N | 4.75 / 4.75 / 4.75 | IP54 | 1.0 kg | €3,318 ex VAT | lower moment, dearer | [G1] [M] |
| DH PGHL-400-80 | 80 mm | 140–400 N | ND | IP40 | 2.2 kg | ND | minimum 140 N too high for food, IP40 | [G5] [O] |
| **Jodell RG75-300** (钧舵) | 75 mm | 40–300 N | **8 / 8 / 8**; Fz 400 N; ≤ 6 kg | IP65 | 1.5 kg | US$3,500 (listing says RG52/RG75, model not specified) | technically a peer of the PGC-300; not cheaper on the price seen | [G6] [O], [G7] [O] |
| Jodell RG52-050 | 52 mm | 2–50 N | 2.5 / 2 / 2.8; ≤ 1 kg | IP54 | 0.85 kg | same listing | too weak (50 N, 2.5 N·m) | [G6] [O] |
| Jodell EPG-HP50/60 | 50/60 mm | 5–50 N | ND (the EPG40-050 is 2 / 1.5 / 2) | IP40 | ND | ND | too weak, IP40 | [G8] [O] |
| **Robotiq Hand-E** (reference) | 50 mm | 20–130 N (2019 manual) | **2.65 / 3.74 / 2.00**; Fx–Fz 100 N; 5 kg form-fit / 3 kg friction | IP67 (product sheet) | 1.07 kg | ND | lower moment limits than the PGC (see 3.3) | [G9] [M] |
| Inspire EG2-4C2 (因时) | 70 mm | 0–20 N | ND | IP40 | 0.23 kg | US$859–1,104 | far too weak for wok and cold box | [G10] [O] |
| Hitbot Z-EFG-100 | 90 mm | 35–60 N | ND | ND | 0.92 kg | US$1,040 | too weak | [G11] [O] |
| 1688 "电动夹爪" listings | ND | ND | ND | ND | ND | ¥576 (rotary RGIC), ¥912 "PGHL-400-80" | the ¥912 for a PGHL is almost certainly a placeholder listing price; specs ND | [G12] [O] |
| 知行机器人 (Zhixing) | — | — | — | — | — | — | maker of grippers and dexterous hands (founded 2018, 0.1–150 kg range); no parallel-gripper datasheet found. The brief's "知行 Jodell" seems to merge two makers: Jodell = 钧舵 | [G14] [O] |

**Conclusion:** none of the cheaper grippers meets force (≥ 96–140 N), IP and moment together. The PGC-140-50 is already the low-cost IP67 option in its class. The only moment upgrades at similar money are PGC-300-60 (IP67, 15 N·m) and Jodell RG75-300 (IP65, 8 N·m).

### 3.2 Keyed tool interface: let the key, not the jaws, carry the moment

**Today's "keyed grip block" is a form fit *between the fingers*.** The tool's moment still goes block → fingers → **jaws → jaw guides**, and that is exactly what the 7 N·m rating limits. Shaping the fingers alone cannot remove it.

**What does remove it [E]: a palm key fixed to the flange adapter** (or to the gripper housing):
- A fork or plate bolted between the robot flange and the gripper reaches forward beside the gripper body. It ends in two tapered pins (or a dovetail) just behind the fingertip zone.
- Each heavy tool (wok, spatula, ladle, spider, lid) gets a standard block with matching tapered holes.
- **Sequence:** a straight insertion of ≤ 50 mm along the pin axis, which fits the existing contact-window rule; then the jaws close on the block's side flats only to stop it sliding off the pins.
- **Load path:** gravity and process moments go pins → adapter → robot flange. The jaws see only the pull-off force along the pin axis.
- **Example:** with the pins 40 mm apart, the wok's 6.47 N·m becomes a ≈ 160 N couple on the pins, which a steel pin carries easily. The jaw moment drops to roughly pull-off force × finger offset, a small fraction of 7 N·m.

**What it buys:**
- The wok moment margin goes from 0.53 N·m to most of 7 N·m.
- The **8–25 N·m spatula wedge spikes** (R15 stir bench) no longer load the jaws at all; today they are above the jaw rating and are handled by "keyed block + arm force limit".
- Heavier dishes (above 1.15 kg of food) are then limited by arm payload, not the jaws.

**What it does not change:**
- Food grasps, the fridge door (≈ 6.4 N·m at a 100 N seal) and napa cabbage still load the jaws.
- So the **force** (≥ 96 N), **stroke** (50 mm) and **IP67** requirements stay. A cheaper low-force gripper is still ruled out by those, not by moment.

**Where the money is:**
- The palm key itself is a small machined part plus new tool blocks: ¥200–800 [E].
- It would allow an **IP54 PGI-140-80** (≈ €1,000 cheaper and 80 mm stroke) only if IP54 is acceptable at the sink and wok. I do not recommend that near steam and oil without a cover.
- Net: the key is a **robustness change, not a cost lever**.

**Sim impact:**
- New palm and adapter collision geometry (box meshes, per the R11 lesson).
- Re-check every grasp where the palm comes within 5 mm of an object: in-box grasps, supported fork, cold box.
- New tool-pickup insertion approaches for the five keyed tools.
- The wok and spatula chains' moment check moves from "PGC moment" to "pin and adapter load".

### 3.3 Note on the Hand-E alternative recorded on 2026-10-11

DECISIONS lists the Robotiq Hand-E 100 mm as the user's option because it "holds full-size napa cabbage" (R13, friction and force based). But Hand-E's published moment limits (Mx 2.65, My 3.74, Mz 2.00 N·m, 2019 manual [G9]) are **lower** than the PGC's 7 N·m. The cabbage and wok moments should be re-checked before that option is taken. I did not verify whether the 100 mm version has different limits (ND).

---

## 4. Cart drive (optional)

| Item | Price | Src |
|---|---|---|
| ZLTECH ZLLG65-ASM500 **V2.0** (current design: 48 V, 165 mm, 10 N·m) | US$250 each (backordered) | [C1] [O] |
| ZLLG65-ASM500 V2.09 | US$195 | [C1] [O] |
| ZLLG80-ASM250 (8 in, 24 V) | US$110–120 | [C1] [O] |
| ZLAC8015D dual-channel driver | standalone ND; a 5 in motor + driver kit was US$556 on eBay | [C2] [O] |
| China prices | ND | — |

Two wheels plus one dual driver are on the order of ¥3–5k [E]. Cheaper hub motors (hoverboard class) exist, but holding brake, encoder and load rating would have to be re-qualified. **Not worth changing for cost.**

---

## 5. Top 3 arm + hand combinations

Baseline: UR5e (¥150k–180k [P1–P3]) + PGC-140-50 (same gripper in A and C, so it cancels).

| | Combination | Est. saving vs UR5e + PGC | Smoothness / interface | Main risks |
|---|---|---|---|---|
| **A** | **Fairino FR5** (with the **±360° J6 option**, IP65 option if offered) + PGC-140-50 + palm key | **≈ ¥126k–156k** (FR5 at the ¥23.8k 2023 guide price; option prices ND) | same 180 °/s → same 2.63 s stroke [E]; **on-controller TrajectoryJ upload with speed override and look-ahead smoothing** | IP54 standard; **0–45 °C ambient** (UR 0–50); stock J6 ±175° fails 5/7 saved chains; the spider chain misses the J4 window by ≈ 4–7°; d4 31 mm shorter; 2023 price may have moved (2026 reports +5–15 % for industrial robots) |
| **B** | **Elite CS66** (or CS66A) + **PGC-300-60** (+ palm key optional) | **≈ ¥76k–136k [E]**: CS66 China price ND, my estimate ¥40k–70k from the market context and the Dobot CR average; PGC-300 adds ≈ €470 | closest UR twin, so the fewest re-plans; UR-style servoj (8 ms) and trajectory points with time and blend; CS66 stroke ≈ 2.8–3.0 s (J1–J2 150 °/s), CS66A ≈ 2.5–2.6 s | price unknown; datasheet 150 °/s vs URDF 180 °/s conflict to resolve; 6 kg payload makes the heavier PGC-300 fit (4.65 of 6 kg = 78 %) |
| **C** | **Dobot CR5A** + PGC-140-50 + palm key | **≈ ¥93k–123k** (CR series 2025 average ¥56.8k; CR5A list price ND) | **StartPath on-controller playback** (8 ms sampling, ×0.25–2 time scaling, filter off = exact); 223 °/s wrists → ≈ 2.6 s stroke; 48 VDC controller | forearm 35 mm shorter and d5 16 mm longer → the most re-planning of the three; IP54; ServoJ streaming only 33 Hz recommended (use StartPath instead) |

The cheapest but slow option is **Dobot Nova 5** (2025 average ¥20.4k, saving ≈ ¥130k–160k). Its 100 °/s joints make the stir ≈ 4.7 s per stroke (+80 %) and all checked actions ≈ 1.8× longer in time. It is only an option if the user accepts slower cooking.

### What to re-check in the sim for each

Common to all (a swap is a new arm model, not a parameter tweak):
1. **New MJCF:** joint frames from the published DH/URDF (see `sim/r10/claude/r19/arm_candidates.json`), collision capsules from the vendor STEP/STL, link masses and inertias from the URDF. The Menagerie UR5e meshes in `dress.py` are visual only.
2. **Rated-payload envelope:** re-run `envelope.py` with the candidate's rated payload and its payload-diagram CoM limit (ND for all candidates; get the payload diagram). Compare against the 0.629 joint ratio.
3. **Re-run every checked chain:** prep chains SD/WD, wok (both plating spots), lever, lid, spider, carrier, spatula rest, fridge door, seasoning and rice ports. Then the R15 stir with **per-joint VMAX** (`r15stirwalk2.py` currently has a scalar `VMAX=180`) and the vendor's acceleration limits (ND; 360 °/s² is an assumption).
4. **Unwrap exported paths** and choose 2πk offsets inside the joint windows (Section 2.3).
5. **Cart:** arm mass changes (FR5 22 kg, CS66 20 kg, CR5A 25 kg vs 20.7 kg) → re-check cart tipping with the arm out.

Per candidate:
- **A (FR5):**
  - J6 window: buy the ±360° option, or re-plan the 5 chains;
  - re-plan the spider chain (J4);
  - wrist clearance (d4 −31 mm) at the hood, faucet and cabinet doors;
  - plume and thermal margin against the 45 °C ambient rating;
  - d6 (flange offset) from the vendor drawing.
- **B (CS66):**
  - re-run the stir with J1–J2 at 150 °/s;
  - check whether the elbow window is ±180° (URDF) or ±360° (datasheet);
  - wrist-1 offset +14 mm;
  - payload with the PGC-300 (+0.5 kg) through the envelope;
  - the wok jaw moment (15 N·m limit).
- **C (CR5A):**
  - full re-plan of the stir and plating geometry (forearm −35 mm);
  - elbow ±160° (passes on the saved chains);
  - check the StartPath playback model (`sample`/`freq`) against the 4 mm path spacing.

---

## 6. Which interface best supports playing back pre-verified smooth trajectories

Ranking for the user's model, "many predefined movements, grouped into movement sets, checked only at set boundaries" [E]:

1. **A dense joint trajectory stored on the controller and replayed there (Fairino TrajectoryJ, Dobot StartPath).**
   - Timing is generated inside the controller, so there is no PC or network jitter, and the PC only sends "play set N".
   - Uniform time-scaling (Fairino `ovl`, Dobot `multi` 0.25–2) keeps the geometric path. So a slowed-down set keeps its collision verdict. Only *speeding up* needs a new load and dynamics check.
   - Use the filter **off** (Dobot `freq=1`). The default 0.2 smooths and therefore leaves the verified path.
2. **The host forwards the whole timed trajectory and the robot interpolates (UR trajectory point interface, Elite `writeTrajectoryPoint`).**
   - Almost as good: the robot interpolates between closely spaced, timed points, so between points it deviates only slightly from the checked path.
   - Keep the checked 4 mm point spacing, so spline deviation stays far below the 5 mm gap.
3. **Streaming servoJ** (UR 500 Hz, xArm 250 Hz, Elite 125 Hz, Dobot 33 Hz recommended).
   - Exact, but the host must be real-time. Dropped packets cause judder, and look-ahead/gain filters shift the path slightly.
4. **Sparse waypoints with vendor blend radius or CP.**
   - The smoothest-looking, but the blended corners are the vendor's geometry, not the verified path.
   - Use only in open free space, after checking the blend's swept volume.

**Practical recipe [E]:**
- Each primitive is an unwrapped, time-parameterised joint trajectory (positions plus velocities at a fixed 8 ms) exported from the checked chain.
- Sets join at shared hub poses: the R17 anchors (zero velocity) or matched-velocity joins.
- One sensing check runs per set (grasp confirmed, wok seated, door open). Inside a set, only the controller's own collision detection and force limits run.
- That needs on-controller playback (option 1) or forwarding (option 2). Of the shortlisted arms, **FR5 and Dobot have option 1 natively**. **UR5e and CS66 have option 2.**

---

## 7. Uncertain or not found

- **China list prices:** Elite CS66, JAKA Zu 5, AUBO i5, Rokae CR7, Elfin-Pro, CR5A (only the CR series average is known), the FR5 J6 ±360° and IP65 options, DH and Jodell grippers in CNY, ZLTECH in CNY. The FR5 price is from March 2023.
- **Arm brake / power-loss holding documents** for every candidate (required by the 2026-10-08 decision).
- **Payload diagrams** (allowed CoM offset at 5–6 kg) for every candidate; needed for the envelope.
- **Vendor joint acceleration limits** (the stir and returns assume 360 °/s²).
- **FR5:** d6 flange offset; ServoJ period; the controller-size discrepancy (130 × 60 × 66 mm on fairino.us vs 245 × 180 × 44.5 mm at the reseller).
- **CS66:** 150 °/s (datasheet) vs 180 °/s (URDF) on J1–J2; elbow ±180° (URDF) vs ±360° (datasheet); CS66A payload, reach and price.
- **JAKA:** servo interface details and DH (no public URDF found).
- **AUBO:** zero convention and trajectory upload.
- **Nova 5:** exact xacro values (the fetch rounded them).
- **The stir cycle's joint path** is not saved, so it could not be range-tested.
- **Robotiq Hand-E 100 mm** moment limits (only the 50 mm manual was read).
- **Price trend:** 2026 news says industrial-robot prices rose 5–15 % [M4]; Dobot's averages were still falling in 2025 [D1].

---

## Sources

**Universal Robots / UR5e price**
- [A1] [M] UR5e datasheet (updated Sept 2026): https://www.universal-robots.com/manuals/latest/en/datasheets/ur5e/
- [A2] [M] UR DH parameters article: https://www.universal-robots.com/articles/ur/application-installation/dh-parameters-for-calculations-of-kinematics-and-dynamics/
- [A3] [M] RTDE guide ("500 Hz on e-Series and ur-Series robots"): https://docs.universal-robots.com/tutorials/communication-protocol-tutorials/rtde-guide.html
- [A4] [M] UR client library trajectory point interface: https://docs.universal-robots.com/Universal_Robots_ROS_Documentation/rolling/doc/ur_client_library/doc/examples/trajectory_point_interface.html
- [A5] [O] UR forum, servoj time range (search snippet: "2ms for e-series"): https://forum.universal-robots.com/t/what-is-servoj-time-range/8935
- [P1] [O] Central South University procurement result, 2022-12-13 (UR5e ¥140,000 + control box ¥30,000 + pendant ¥10,000): https://czzx.csu.edu.cn/csustatic/zbgshwfwl/20221213/3497.html
- [P2] [O] gkzhan reseller (东莞库崎), UR3e/UR5e/UR10e reference price ¥17万: https://m.gkzhan.com/st221785/list_1029470.html
- [P3] [O] aijiuku second-hand listing, "全新价格150000元" (search snippet): https://wap.aijiuku.com/product/1776071725147095042.html
- [P4] [O] Vention UR5e US$34,527 (search snippet): https://vention.io/parts/universal-robots-ur5e-collaborative-robot-arm-2445

**Fairino**
- [F1] [M] FR5 specification (fairino.us): https://www.fairino.us/collaborative-robot/fairino/fr5
- [F2] [M] FR5 URDF (frcobot_ros2): https://raw.githubusercontent.com/FAIR-INNOVATION/frcobot_ros2/main/fairino_description/urdf/fairino5_v6.urdf
- [F3] [M] Fairino news: FR3/FR5 terminal prices ¥22,800/¥23,800 (March 2023), FR5-SPARK ¥18,000: https://fairino.com/Companynews/37.html
- [F4] [O] top3dshop FR5 (US$6,999, controller size, power, collision settings): https://top3dshop.com/product/fairino-fr5-robotic-arm
- [F5] [M] Fairino SDK trajectory recurrence (TrajectoryJ, LoadTrajectoryLA): https://fairino-doc-it.readthedocs.io/3.9.3/SDKManual/CPPRobotTrajectoryRecurrence.html
- [F6] [M] Fairino user manual, coding (Servo, Spline/N-Spline, TrajectoryJ): https://fairino-doc-en.readthedocs.io/latest/CobotsManual/coding.html
- [F7] [M] FAIR-INNOVATION GitHub (ROS/ROS 2, Python/C++/C#/Java SDKs): https://github.com/FAIR-INNOVATION

**Elite Robots**
- [E1] [M] CS66 datasheet (PDF via Neobotix): https://www.neobotix-robots.com/fileadmin/images/downloads/Datenbl%C3%A4tter/CS66_Datasheet.pdf
- [E2] [M] CS66 physical parameters (DH, masses): https://raw.githubusercontent.com/EliteRobots/Elite_Robots_CS_ROS2_Description/humble/config/cs66/physical_parameters.yaml
- [E3] [M] CS66 joint limits: https://raw.githubusercontent.com/EliteRobots/Elite_Robots_CS_ROS2_Description/humble/config/cs66/joint_limits.yaml
- [E4] [M] Elite CS SDK, EliteDriver API (servoj 8 ms, trajectory points): https://raw.githubusercontent.com/EliteRobots/Elite_Robots_CS_SDK/main/doc/API/cn/EliteDriver.cn.md
- [E5] [M] Elite ROS 2 driver (ROS index): https://index.ros.org/p/elite_robots_driver/
- [E6] [O] GeekPark, CSA series (CS66A) launch, 2023-08-03: https://www.geekpark.net/news/322671
- [E7] [O] Elite CS/CP series brochure 2025 (27 safety functions, IP65/IP68), via Moovall: https://bo5.onlinebiz.pt/moovall/_files/moovall-elite-robots-cp-series-2025-en-view-4MLAB20250919094320.pdf

**Dobot**
- [D1] [O] Tiger Brokers announcement digest, 2026-07-08 (CR and Nova average selling prices 2023–2025): https://www.itiger.com/news/1161358325
- [D2] [M] Nova 5 specifications: https://id.dobot-robots.com/products/nova-series/nova5.html
- [D3] [O] top3dshop CR5A (specs, US$24,320): https://top3dshop.com/product/dobot-cr5-collaborative-robot
- [D4] [M] Dobot TCP/IP Remote Control Interface Guide v4.6.6 (ServoJ, StartPath, CP, port 30004): https://a.storyblok.com/f/298593/x/ce7fbaa06a/dobot-tcp_ip-remote-control-interface-guide-v4-6-6_20260527_en.pdf
- [D5] [M] DOBOT_6Axis_ROS2_V4 (CR5 / Nova 5 xacro): https://github.com/Dobot-Arm/DOBOT_6Axis_ROS2_V4 · https://raw.githubusercontent.com/Dobot-Arm/DOBOT_6Axis_ROS2_V4/main/cra_description/urdf/cr5_robot.xacro · https://raw.githubusercontent.com/Dobot-Arm/DOBOT_6Axis_ROS2_V4/main/cra_description/urdf/nova5_robot.xacro

**JAKA, AUBO, Han's/Huayan, Rokae, Realman, UFACTORY**
- [J1] [O] EVS International, JAKA Zu 5 specs (search snippet): https://www.evsint.com/cs/robots-by-brand/jaka/
- [J2] [O] Machineseeker, JAKA Zu 5 €7,846–8,108 (search snippet): https://www.machineseeker.nz/jaka-zu+5/i-21446482
- [AU1] [O] Unchained Robotics, AUBO i5 (specs, €18,600 ex VAT): https://unchainedrobotics.de/en/products/robot/cobot/aubo-robotics-i5
- [AU2] [M] AUBO i5 URDF: https://raw.githubusercontent.com/AuboRobot/aubo_robot/master/aubo_description/urdf/aubo_i5.urdf
- [AU3] [O] pyaubo-sdk (JSON-RPC and RTDE; search snippet): https://pypi.org/project/pyaubo-sdk/0.18.0
- [H1] [O] RoboDK, Han's E05: https://robodk.com/robot/Han-s/E05 (135 °/s from a Qviro search snippet)
- [H2] [M] Huayan Elfin-Pro: https://huayan-robotics.net/elfin-pro
- [R1] [M] IDEC-FS, Rokae CR series (IP67K): https://en.idec-fs.com/rokae/products/cr/
- [R2] [O] Encycam, Rokae xMate CR7 joint speeds (search snippet): https://encycam.com/component-library/rokae-xmate-cr7
- [RM1] [O] RobotShop, Realman RM65-B (search snippet): https://robotshop.com/products/realman-robotic-arm-rm65-b-6-dof-5kg-payload-basic-version
- [X1] [M] UFACTORY 850 technical specifications: https://docs.850.ufactory.cc/8.technical_specifications.html
- [X2] [O] UFACTORY servo mode guide (250 Hz; search snippet): https://docs.supportarticle.ufactory.cc/support_articles/developer/ufactory-servo-mode-guide.html
- [X3] [O] top3dshop xArm 6 (US$8,849): https://top3dshop.com/product/ufactory-xarm-6-robotic-arm
- [X4] [O] Knox Labs UFACTORY 850 (US$8,999; search snippet): https://www.knoxlabs.com/products/ufactory-850-collaborative-robot-arm

**Market context**
- [M1] [O] EVS International, "2026 top cobot manufacturers" (FOB price ranges, Q1 2026): https://www.evsint.com/top-cobot-manufacturers-2026-comparison/
- [M2] [O] Tencent News 2024-12-28, "不到一万元就能买一台": https://news.qq.com/rain/a/20241228A05MDI00
- [M3] [O] NetEase 2026-05-27, cobot price ranges by payload: https://www.163.com/dy/article/KTVI246J0518WUUQ.html
- [M4] [O] Sina Finance 2026-10-03, robot price war (industrial-robot prices +5–15 %): https://finance.sina.com.cn/roll/2026-10-03/doc-initxfyp6561576.shtml

**Grippers**
- [G1] [M] DH-Robotics catalog EN (PGC-140, PGC-300, PGI-140, AG-95; hosted by Unchained): https://uploads.unchainedrobotics.de/media/file_upload/DH-Robotics-catalog-EN_46faa8dd.pdf
- [G2] [O] welectron PGC-140-50 (€2,268.07 ex VAT): https://www.welectron.com/DH-Robotics-PGC-140-50-Collaborative-Electric-Parallel-Gripper
- [G3] [O] OpenELAB PGC-140-50-W (€2,119): https://openelab.io/products/dhrobotics-pgc14050-heavy-duty-gripper
- [G4] [O] PGC-300-60 prices (RobotShop US$2,590; OpenELAB €2,589; search snippets): https://www.robotshop.com/products/dh-robotics-pgc-300-60-dh-robotics-electric-gripper-collaborative-robot-with-reddot-winner-2021 · https://openelab.io/a/s/products/dhrobotics-pgc30060-heavy-duty-gripper
- [G5] [O] OpenELAB PGHL-400-80-W (search snippet): https://openelab.io/products/dhrobotics-pghl40080-long-stroke-gripper
- [G6] [O] Dobot ecosystem, Jodell RG52-050 / RG75-300: https://www.dobot-robots.com/ecosystem/accessories/590.html
- [G7] [O] Robotics Center, Jodell RG US$3,500: https://www.roboticscenter.ai/ar/store/product/jodell-rg-gripper
- [G8] [O] Robotics Center, Jodell EPG-HP (search snippet): https://www.roboticscenter.ai/ar/store/product/jodell-epg-hp-gripper
- [G9] [M] Robotiq Hand-E instruction manual, specifications (2019): https://assets.robotiq.com/website-assets/support_documents/document/online/Hand-E_Instruction_Manual_Web_20190329.zip/Hand-E_Instruction_Manual_Web/Content/6.%20Specifications.htm
- [G10] [O] Knox Labs, Inspire EG2-4C2 (US$859 snippet; US$1,103.63 in `hand_options.md`): https://www.knoxlabs.com/products/inspire-robots-eg2-4c2-electric-gripper
- [G11] [O] Hitbot Z-EFG-100 US$1,040: see `research/hand_options.md` source H1
- [G12] [O] 1688 market page "电动夹爪": https://www.1688.com/market/-BCD0D7A6.html
- [G13] [O] welectron PGIA-140-80: see `research/hand_options.md` source D3
- [G14] [O] PEdaily 2026-03-30 (知行机器人 profile; search summary): https://news.pedaily.cn/20260330/126601.shtml

**Cart drive**
- [C1] [O] aifitlab (ZLLG65-ASM500 V2.0 US$250, V2.09 US$195; ZLLG80-ASM250 US$110–120): https://aifitlab.com/products/zhongling-zllg65-asm500-v2-0-motor · https://aifitlab.com/products/zhongling-zllg80-asm250-4096-v2-02-motor
- [C2] [O] eBay 5 in hub servo + driver kit (US$556; search snippet): https://www.ebay.com/itm/395679398909

**Project files read (not modified):** `home-cooking-robot/README.md`, `robot_rail/DECISIONS.md`, `robot_rail/research/hand_options.md`, `robot_rail/research/r19_system_cost.md` (stroke count only), `sim/r10/claude/README_R10.md`, `envelope.py`, `r15stirwalk2.py`, `r17chain.py`, `hardware.py`, `assets/ur5e.xml`, `assets/envelope_-20.json`, `results/r15/stirwalk2_h_scrape_dice_r17.json`, `results/r17/chain_*` (7 files listed in 2.3).
