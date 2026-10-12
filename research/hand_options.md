# Hand options: low-force or long-stroke grippers for the UR5e (tomato + carrot)

Compiled 2026-10-11 by read-only web research (no logins, no sellers contacted, nothing added to a cart). Every number has a source key (see **Sources** at the end) and a type:
**[M]** manufacturer datasheet / manual / official product page · **[P]** peer-reviewed paper · **[O]** other (distributor, marketplace, forum, repo, preprint, search snippet).
"derived" = my own arithmetic or reading of a garbled table, labelled as such. "not found" = searched, no usable number.

Prices are web prices seen on 2026-10-11. OnRobot, Robotiq, DH, Schunk, Weiss, JODELL, Hitbot and Inspire show **no list price on their own sites** (they say "request pricing"); the prices below are distributor prices [O], except ROBOTIS, whose own US store shows one [M].

Companion file: `finger_design_inputs.md` (PGC-140-50 baseline, tomato and carrot forces, Fin Ray data).

---

## 0. What the task needs (derived)

| Item | Value | Basis |
|---|---|---|
| Stroke for Fin Ray across Ø30–80 mm with ≥ 10 mm squeeze per jaw | **≥ 70 mm + 2 × approach clearance**. With 5 mm clearance per side: **≥ 80 mm** | derived: open gap ≥ 80 + 2c; closed gap ≤ 30 − 2 × 10 = 10 mm. The finger thickness cancels out because it shifts both ends equally |
| Force window | One gripper must reach **≤ 10 N per finger** (tomato) and **25–40 N** (carrot) | values from the task brief, not re-sourced here |
| Current PGC-140-50 | 50 mm stroke, 40–140 N per jaw, IP67. It fails both criteria | [M] S1/S2 in `finger_design_inputs.md` |
| "Gripping force" means different things | DH quotes force "per jaw". Robotiq Hand-E quotes "per finger" and a "total" that is 2× per finger. OnRobot, Robotiq 2F and Weiss do not say | [M] D1, R4, G1, R1, W1 |

---

## 1. Commercial electric grippers

### 1.1 Candidates that meet at least one criterion (min ≤ 10 N, or stroke ≥ 80 mm)

★ = meets both on paper.

| Gripper | Total stroke | Force range | Force control / resolution | Weight | IP | UR integration and power | Finger load / moment limits | Price seen | Src |
|---|---|---|---|---|---|---|---|---|---|
| ★ **OnRobot RG2** | 0–110 mm | **3–40 N**. "Gripping force deviation ±25 %" | Adjustable force. "The speed is linearly proportional to the force" (38–127 mm/s). Finger position resolution 0.1 mm. BLDC motor. The step size of the force setting is not found | 0.78 kg | IP54 | OnRobot tool-flange kit (USB stick + tool-flange cable) lists RG2 [O G6]. RG2 V2/V3 talk RS485 [O G10]. Otherwise it goes through the OnRobot Compute Box. Supply 20–25 V; 70–600 mA; "Current spikes up to 3A (max 6mS) may occur during the release action" | Moments **not published**. Fingertip extensions lower the force: 50 mm → 66.67 %, 100 mm → 50 % of the target. The maximum workpiece height depends on grip width (chart only) | $5,778 [O G7] | [M] G1 |
| ★ **OnRobot RG2-FT** | 0–100 mm | 3–40 N | F/T sensors in the fingertips. Nominal capacity Fxy 20 N, Fz 40 N. Noise-free resolution Fxy 0.1 N, Fz 0.4 N. 150 Hz. Proximity sensor 0–100 mm | 0.98 kg | IP54. The fingertip note says "Avoid dust and liquid penetration" | 24 V, 6.5–22 W. RG2-FT is **not** in the tool-flange-kit list, so it probably needs the Compute Box (derived from G6, not confirmed) | not found | not found | [M] G2 |
| **OnRobot RG6** | 0–160 mm | 25–120 N, ±25 % | 51–140 mm/s | 1.25 kg | IP54 | In the tool-flange-kit list [O G6]. 20–25 V, 70–600 mA, 3 A spikes | not published | $6,920 [O G8] | [M] G3 |
| ★ **Robotiq 2F-140** | 140 mm | Spec 10–125 N. **The manual's measured table gives min/max 15–120 N** on steel and aluminium, and as low as 15–75 N max on soft payloads (derived reading of a garbled table) | Force byte rFR 0–255 sets the motor current limit. rFR = 0 gives the "Lowest force", with re-grasp off. Force repeatability ±10 %. "Resolution is the increment modified from a 1 bit difference of position/speed/force request (from 0 to 255)", so ≈ 0.45 N per step **if linear** (derived; linearity is not stated). Position resolution 0.6 mm | 1.025 kg | **IP40** | URCap. For the e-Series wrist coupling: "Power supply, communication signals, grounding, electrical resistance and fusing are managed by the robot itself". The URCap option "Limit gripper current" caps one gripper at 600 mA. 24 V; peak current 1 A | Fx, Fy, Fz 25 N; Mx, My 5 N·m; Mz 3 N·m | $5,995 [O R7] | [M] R1, R2, R3 |
| Robotiq 2F-85 (reference only) | 85 mm | Spec 20–235 N; measured 25–220 N | Same as 2F-140. Position resolution 0.4 mm | 0.925 kg | IP40 | Same as 2F-140 | Fx, Fy, Fz 50 N; Mx, My 5 N·m; Mz 3 N·m | "From $4,999" [O R8] | [M] R1–R3 |
| **Robotiq Hand-E** (50 mm or 100 mm version) | 50 mm or **100 mm** | 20–185 N per finger (40–370 N total) | Position resolution 0.2 mm; closing speed 20–150 mm/s; Modbus RTU (RS-485) | 1 kg (50 mm) / 1.1 kg (100 mm) | **IP67** | "Plug & Play" on top cobot brands (product sheet). The wrist power details were not checked for Hand-E | not found in the product sheet | not found | [M] R4, R5 |
| **DH PGI-140-80** | 80 mm | 40–140 N per jaw | Not verified for PGI (the PGC manual uses a current-% force setting) | 1 kg without fingers | IP54 | Modbus RTU RS485 or digital I/O. 24 V; 0.5 A nominal, 1.2 A max. UR integration not found | Fz 300 N; Mx = My = Mz 7 N·m | PGIA-140-80 (version with brake): €1,259.66 excl. VAT / €1,499 incl. VAT [O D3]. welectron lists 0.7 A nominal / 1.6 A peak for PGIA | [M] D1 |
| **DH AG-95** | 95 mm | 45–160 N per jaw | Screw + linkage drive; 0.7 s open/close | 1 kg | IP54 | URCap. The UR+ kit includes a "Protocol converter" and a separate power cable [O D4], so tool-flange power is not stated. 0.8 A nominal, 1.5 A max | Fz 300 N; Mx = My = Mz 4.75 N·m | AG-160-95: €3,318.49 excl. VAT [O D2] | [M] D1 |
| DH AG-160-95 (current AG-95 version) | 95 mm | 45–160 N per jaw | 0.9 s open/close | 1 kg | IP54 | Modbus RTU / digital I/O. 24 V; 0.8 A / 1.5 A | not specified on the page | €3,318.49 excl. VAT | [O] D2 |
| **DH AG-145** | **145 mm** | 35–105 N per jaw | Linkage drive; 0.7 s | 1.3 kg | IP54 | 0.8 A / 1.5 A | Fz 300 N; Mx = My = Mz 1.95 N·m | not found | [M] D1 |
| **DH DH-3** (3-finger) | 106 mm (parallel) / 122 mm (centric) | **10–65 N** per jaw | Screw nut + gear + linkage | 1.68 kg | not found | 0.5 A / 1 A | Fz 300 N; Mx 2.5, My 2, Mz 3 N·m | not found | [M] D1 |
| ★ **Weiss WSG 50-110** | 110 mm (55 per jaw) | **5–80 N** | not found | 1.2 kg | **IP20** | Ethernet TCP/IP / PROFIBUS (PROFINET optional). 24 V; nominal 0.9 A (Schunk) or 850 mA (Weiss); 2 A max. The UMI reference setup ran a WSG50 on a UR5e over IP [O W4] | Max finger length 170 mm; 0.3 kg per finger; Mx = My 4 N·m; Mz 3 N·m; Fz 80 N | The Schunk page marks it **discontinued** | [M] W1, W2 |
| Weiss WSG 32-068 | 68 mm | 5–50 N | — | 550 g | IP40 | 24 V 750 mA; Ethernet / PROFINET | Max finger length 120 mm; 0.1 kg per finger | "END OF LINE! Available only until December 2026!" | [M] W1 |
| **ROBOTIS RH-P12-RN-UR** | 0–106 mm (store) / 0–109 mm (e-manual, RH-P12-RN) | Max 170 N; **min not found** | Current Control and Current-based Position Control modes. Present Current unit ≈ 4.02 mA. Current Limit default value 820 | 500 g | not found | "UR Certified". URCap download on the e-manual. Kit includes "Robot Cable 180mm (URe Exclusive)". 24 V; 30 mA standby; **3.33 A peak** | not found | $4,169.44 (ROBOTIS US store) [M B2] | [M] B1–B3 |
| Inspire EG2-4C2 (因时) | 70 mm | **0–20 N** | Force repeatability ±1 N; positioning ±0.5 mm; 70 mm/s; RS485 | 231 g | IP40 | 24 V ±10 %; 0.7 A peak. UR integration not found | not found | From $1,103.63 [O I1] | [O] I1 |
| JODELL RG52-050 (钧舵) | 0–52 mm | 2–50 N per side (Dobot page) / 3–50 N (Robotics Center) / "maximum clamping force of 60N" (UR+) | Position, force and speed adjustable; RS485 + I/O | 0.85 kg (Dobot) / 0.75 kg | IP54 | Listed on UR+ for UR3e/UR5e/… and PolyScope X. 0.4 A rated / 0.8 A max | Fz 200 N; Mx 2.5, My 2, Mz 2.8 N·m | RG listing $3,500, model not specified [O J3] | [O] J1, J2, J3 |
| JODELL EPG50-060 / EPG-L80 | 0–50 mm / **0–80 mm** | 2–60 N / L80 minimum force not found | RS485 + I/O | 0.8 kg / — | IP40 / IP40 | 0.4 A / 1.5 A (EPG50-060) | EPG50-060: Fz 200 N; Mx 2.5, My 2, Mz 2.8 N·m | EPG-L series listing $4,200 [O J5] | [O] J4, J5 |
| Hitbot Z-EFG-100 / Z-EFG-130 (慧灵) | 90 mm / 120 mm | 35–60 N / 40–130 N | Z-EFG-130: Modbus + digital I/O | 0.92 kg / not found | not found / IP20 | 24 V. UR integration not found | not found | $1,040 [O H1] / €2,044.54 excl. VAT [O H2] | [O] H1, H2 |
| Schunk EGK 40-EC-N-B | 83 mm (41.5 per jaw; total derived) | 55–150 N | The EGK family has a SoftGrip mode, which reduces impact forces (no number given) | 0.97 kg | IP67 electronics / IP20 base jaws | This variant uses EtherCAT. A UR variant of EGK 40 was not found. 24 V; 0.19 A / 0.38 A | Max finger length 100 mm; Mx 8, My 9, Mz 2 N·m; Fz 500 N | not found | [M] K1 |
| Schunk EGU 50-MB-N-B | 102 mm (51 per jaw; total derived) | 150–300 N (Schunk page) vs 50–300 N (Dobot page) | BasicGrip / StrongGrip modes | 1.44 kg | IP67 electronics | Modbus RTU. The UR5e kit (the 600 N M-variant) is $4,622 [O K6]. 0.24 A / 1.23 A | Max finger length 80 mm; Mx 32, My 35, Mz 32 N·m; Fz 800 N | $4,622 (UR5e kit) | [M] K4; [O] K5, K6 |

### 1.2 Checked and ruled out (stroke < 80 mm **and** minimum force > 10 N, or both too small)

- **OnRobot 2FG7**: 38 mm stroke (external grip widths 1–39 or 35–73 mm). 20–140 N, tolerance ±5 N. Finger-platform torque max 5 N·m; "5 Nm corresponds to full gripping force at 36 mm from finger platform". IP67; 1.1 kg; NSF H1 gear grease; force sensor in one finger. Datasheet: "The required current is 2000 mA, less current will result in less gripping force". Its current table lists **UR: 600 mA** as the maximum. Price $4,892 [O G9]. [M] G4
- **OnRobot 2FG14**: 50 mm stroke; 40–280 N, ±10 N; torque around X 30 N·m, around Y 25 N·m ("25 Nm corresponds to full gripping force at 90 mm"). IP67; 1.5 kg; UR current max 600 mA. [M] G5
- **DH low-force PGE / CGE / PGC series** (all [M] D1):
  - PGE-15: 6–15 N, 26 mm, 0.4 kg, IP40; Mx 0.9, My 0.75, Mz 0.9 N·m.
  - PGE-8: 2–8 N, 14 mm.
  - PGE-5: 0.8–5 N, 14 mm.
  - PGE-2: 0.8–2 N, 12 mm.
  - PGE-50: 15–50 N, 26 mm, IP40.
  - CGE-10: 3-jaw centric, 3–10 N, 10 mm per jaw.
  - PGC-50: 15–50 N, 35 mm, 0.5 kg, IP54.
  - The catalog says the PGE can "achieve the force repeatability of 0.1N". All strokes are far below 80 mm.
- **Schunk EGK 25**: 26.5 mm per jaw; 20–50 N; IP67 / IP20; €2,200–2,600 excl. VAT [O K2]. The UR kit (Modbus RTU, "internal robot wiring") is $4,261 [O K3].
- **Zimmer GEP2000**: 6–20 mm per jaw and 40–500 N across sizes. GEP2016IL: 16 mm per jaw; four force levels of 125 / 250 / 375 / 500 N; max finger length 120 mm; IP40; 0.94 kg; 2 A max. [M] Z1. The UR+ listing names GEH6000IL, GEP2000, GEP5000 and GED5000 with digital I/O or IO-Link, but gives no specs.
- **JODELL EPG26-006** (1–6 N, 26 mm), **EPG26-015** (1–15 N, 26 mm), **EPG40-050** (2–50 N, 40 mm). [O] J4
- **Weiss CRG 30-050** (GRIPKIT-CR): 50 mm stroke and 15–30 N, seen only in a search snippet (tm-robot.com) whose page I did not open. Unverified.

### 1.3 What the specs imply

- **Tomato-capable and long stroke** on paper: OnRobot RG2 and RG2-FT (3 N min), Weiss WSG 50-110 (5 N; discontinued per Schunk, IP20), Robotiq 2F-140 (10 N spec, **15 N measured** in its own manual), DH DH-3 (10 N, 3-finger). **None of these is better than IP54.** Every IP67 option (Hand-E, 2FG7, 2FG14, PGC-140-50) has a minimum of ≥ 20 N (derived from the tables above).
- **RG2 at the carrot end**: the maximum is 40 N with ±25 % deviation, so a 40 N setting can land anywhere from 30 to 50 N, and a 10 N setting from 7.5 to 12.5 N (derived).
- **Robotiq low-force behaviour**: Schouterden et al., citing the 2F manual's force curves (pp. 60–62), say "the lower forces will not be sustained at the higher speed settings when gripping a rigid object with rigid gripper fingers". Soft fingers give "better control over lower gripping forces on higher speeds at the cost of an overall lower achievable gripping" force. [P] P1
- **OnRobot on UR power**: the 2FG7 and 2FG14 need 2000 mA for full force, but their datasheets list 600 mA as the UR maximum, so they grip with less force on UR. The RG2 and RG6 draw at most 600 mA, with 3 A spikes of ≤ 6 ms (from G1, G3–G5; derived comparison).
- **Fin Ray on an RG2 has been done**: Thilakarathna et al. put 3D-printed ABS Fin-Ray fingers "into the interchangeable finger slots of the RG2" on a UR10. They set the RG2 to "a constant force output of 40 N by controlling the driving motor's current output" (food-waste sorting, not produce). [O] P6

---

## 2. UR5e tool flange electrical limits

| Item | Value | Src |
|---|---|---|
| Connector and flange | M8 8-pin female; flange EN ISO 9409-1-50-4-M6 | [M] U1 |
| Pins | AI3 / RS485−; AI2 / RS485+; TO0 / PWR; TO1 / GND; POWER 0/12/24 V; TI0; TI1; GND. Pins 1 and 2 are certain. The 3–8 order is my reading of a misaligned table. "Tool Connector must be manually tightened up to a maximum of 0.4 Nm" | [M] U2 |
| Voltage | Set to 0 V, 12 V or 24 V in the Installation tab. 24 V mode: 23.5 / 24 / 24.8 V (min/typ/max). 12 V mode: 11.5 / 12 / 12.5 V | [M] U2 |
| Current, **manual SW 5.19 (2024)** | Single pin: typ 600 mA, max 2000 mA. Dual pin: typ 600 mA, max 2000 mA. The 2000 mA is a "Peak for max 1 second, duty cycle max: 10%. Average current over 10 seconds must not exceed typical current." | [M] U2 |
| Current, **manual v5.4 (2019)** | "Supply current in both modes": typ 1000 / max 2000 mA. Dual Pin Power: typ 1500 / max 2000 mA. "2000 mA for max 1 second. Duty cycle max: 10%. Average current must not exceed 600 mA" | [M] U3 |
| Current, **datasheet (Sept 2026)** and the manual's tech-spec page | "1.5 A (Dual pin) 1 A (Single pin)" | [M] U1, U2 |
| → What to design for (derived) | The documents conflict. All of them allow **≤ 2 A for ≤ 1 s at ≤ 10 % duty**. Both manuals tie the long-run average to **600 mA** (≈ 14.4 W at 24 V, derived) | derived |
| Capacitive load | ≤ 8000 µF, with a 400 ms soft start. "Hot-plugging the capacitive load is not allowed" | [M] U2 |
| Dual Pin Power | Wire Power (gray) to TO0 (blue) and Ground (red) to TO1 (pink). It uses both digital outputs. After an E-stop both power pins drop to 0 V | [M] U2 |
| Digital outputs | 2. Modes: sinking (NPN), sourcing (PNP) or push/pull. Source/sink current typ 600 mA, max 1000 mA. Current through GND typ 1000 mA, max 3000 mA. "The Digital Outputs in the tool are not current-limited." | [M] U2 |
| Digital inputs | 2. PNP with weak pull-down. Input −0.5 to 26 V; logic low ≤ 2.0 V, high ≥ 5.5 V; 47 kΩ | [M] U2 |
| Analog inputs | Datasheet: "2 or 1 x RS485", i.e. two analog inputs, or one RS485 when the TCI is on. 0–10 V or 4–20 mA, 12 bit | [M] U1, U2 |
| RS485 (Tool Communication Interface) | Baud rates 9.6k, 19.2k, 38.4k, 57.6k, 115.2k, 1M, 2M, 5M. Stop bits 1 or 2. Parity none, odd or even. Latency 2–4 ms. Internal fail-safe biasing. Enabling the TCI disables the tool analog inputs. Script call: `set_tool_communication(enabled, baud_rate, parity, stop_bits, rx_idle_chars, tx_idle_chars)` | [M] U2, U4 |
| UR5e flange F/T sensor (for reference) | Range ±50 N / ±10 N·m; precision ±3.5 N / ±0.2 N·m; accuracy ±4.0 N / ±0.3 N·m | [M] U1 |

---

## 3. DIY / open-source servo grippers

### 3.1 Projects

| Project | What is documented | Stroke / force | Src |
|---|---|---|---|
| **Actuated UMI gripper** (Helmut, Funk, Schneider, Peters, 2024) | BOM: 1× DYNAMIXEL **XL430-W250-T**, U2D2, U2D2 Power Hub, 2× constant-force spring (0.1 × 8 × 110), 2× MGN7C linear rail (80 mm), flat belt (5 × 1 × 300 mm), heat-set inserts, M3/M2 screws. PLA parts; the v2 adds GelSight Mini and D405 mounts; MIT licence; a STEP assembly is included. The ROS 2 node uses extended position mode (`operating_mode = 4`) and PWM mode (goal PWM within ±885), and reads `present_load`. It uses **no current mode** (the XL430 has none) | Stroke **not found**; force **not found** | [O] O1, O2 |
| OpenGrip (Clayton Haight; the base mechanism of actuated UMI) | Dynamixel. "constant force springs prevent collisions from damaging the gripper". "by using different winch materials (Nylon, Rubber, etc.) the compliance of the grasp can be adjusted". 5 custom parts | no numbers | [O] O3 |
| UMI (Chi et al., RSS 2024), robot side | The reference deployment is a UR5/UR5e with a WSG50 gripper addressed by IP | see WSG 50-110 above | [O] W4 |
| **Yale OpenHand** | No parallel-jaw model among the 10 listed. Model T42: 2× Dynamixel RX-28/MX-28 (or Power HD servo), 400 g, holding force 10 N. Model T: XM430/MX-64, 490 g, 10–13 N. Licence CC BY-NC 3.0 | aperture not found | [O] O4, O5, O6 |
| **OpenMANIPULATOR-X gripper** (ROBOTIS) | XM430-W350-T; 12 V; arm payload 500 g; "Open Source Hardware" with STL files | Gripper stroke **20–75 mm**; force not found | [M] O7 |
| **SimpleSliderHand** (ACFR, Sydney) | MX-28T servo, 12 mm linear rail with 2 carts, fishing-line tendon. Rail length is parametric: "a 300mm rail works well", 200 mm "is a good compromise". UR mount: 4× M6 on a Ø50 circle. "less than $500", about 4 days to build. Runs on 24 V from the UR controller with 8 × 4700 µF capacitors. "If you require very precise (<3mm) positioning or torque control this is not a good solution." | Very long stroke possible; force not found | [O] O8 |
| UCD 3D-printed 2-finger gripper (Qiang Wang) | One Dynamixel; UR5(e) mounting shown; Python calibration and control code | no numbers | [O] O9 |

### 3.2 Servos

| Servo | Stall torque | Supply | Current-based position mode | Current resolution | Interface | Weight | Water / IP | Src |
|---|---|---|---|---|---|---|---|---|
| **XM430-W350** | 3.8 N·m @ 11.1 V, 2.1 A. **4.1 N·m @ 12.0 V, 2.3 A.** 4.8 N·m @ 14.8 V, 2.7 A | 10.0–14.8 V (recommended 12.0 V) | **Yes**: "controls both position and current(torque) … ideal for … grippers". Up to ±256 rev | Goal Current / Current Limit unit **≈ 2.69 mA**; range 0–1,193 (≈ 3.21 A, derived) | -T: TTL; -R: RS-485. 9,600 bps to 4.5 Mbps (9.6k, 57.6k, 115.2k, 1M, 2M, 3M, 4M, 4.5M) | 82 g; gear 353.5:1 | No IP rating. Safety text: "Never place items containing water, flammables/open flames, or solvents near the product." | [M] X1 |
| **XL430-W250** (used by actuated UMI) | 1.0 N·m @ 9 V, 1.0 A; 1.4 @ 11.1 V, 1.3 A; 1.5 @ 12 V, 1.4 A | 6.5–12.0 V (recommended 11.1 V) | **No.** Modes: velocity, position, extended position and PWM only. There is no Goal/Present Current; Present Load is reported in 0.1 % units; PWM Limit 0–885 (0.113 % per unit) | — | TTL only (5 V logic) | 57.2 g; gear 258.5:1 | Same water warning; no IP | [M] X2 |
| XL330-M288 (a small option) | 0.52 N·m @ 5.0 V, 1.47 A | 3.7–6.0 V | Yes | 1 mA | TTL | 18 g | no IP | [M] X3 |
| RH-P12-RN actuator (built into the ROBOTIS hand) | Max gripping force 170 N | 24 V nominal | Current-based position: yes | Present Current ≈ 4.02 mA per unit | RS485, 9,600 bps to 10.5 Mbps | 500 g (whole hand); gear 1181:1 | not found | [M] B1 |

### 3.3 Fit with the UR5e tool flange (all derived)

- **Voltage:** the XM430 range (10.0–14.8 V) contains the whole UR 12 V band (11.5–12.5 V), so it fits. The XL430 maximum of 12.0 V is **below** the UR 12 V band's maximum of 12.5 V, so its spec can be exceeded. The XL330 needs a regulator.
- **Bus:** the XM430-W350-**R** speaks RS-485 natively. Baud rates both sides support: 9,600, 57,600, 115,200, 1M and 2M. The XL430 is TTL only and needs a transceiver.
- **Current:** the XM430 stalls at 2.3 A at 12 V, but the UR tool allows only a 600 mA average and 2 A for ≤ 1 s. For continuous holding, set Current Limit to ≤ ≈ 223 units (600 / 2.69). At 0.6 A the torque is ≈ 1.07 N·m **if** the stall ratio of 1.783 N·m/A held. The real torque–current curve (an e-manual graph) was not read.
- **Force (rough):** with one pinion driving two racks, force per jaw = T / (2r), ignoring friction. With r = 10 mm: 1.07 N·m → ≈ 53 N per jaw. 10 N per jaw needs ≈ 0.2 N·m ≈ 0.11 A ≈ 42 current units. Friction, gear efficiency and cogging are ignored. The **practical minimum stable force is not found**.
- **Washdown:** no Dynamixel is IP-rated, and ROBOTIS warns against water near the product. None of the DIY designs states any water protection.

---

## 4. Published comparisons for food and produce

| Study | What was compared | Key findings | Src |
|---|---|---|---|
| Schouterden, Verbiest, Demeester, Kellens 2021, *Agronomy* 11:1922 | 10 gripping principles on apples and pears. Electric ones: Robotiq 2F-85 with custom cone fingers (soft suction-cup and rigid) and the OnRobot SG-b-H soft gripper. Pneumatic ones: Festo DHRS-40-A + DHAS-80 Fin Ray, Piab piSoft, Piab suction, and a blower foam cup | A custom foam suction cup was best overall but used the most energy. Electric Robotiq vs pneumatic Festo with the same fingers: "a slight advantage could be given to the electric Robotiq, based on the lower number of damaged fruits". The conclusion found no "substantial difference in gripping success or quality" between them. Energy per 100,000 picks: Robotiq 2F-85 576 Wh vs Festo 840 Wh (derived alignment of a garbled table, consistent with the text). OnRobot SG fingertips curled into point contacts and damaged pears | [P] P1 |
| Chauhan et al. 2025, *Smart Agricultural Technology* 12:101445 | A rigid gripper (an OnRobot RG2, per the ScienceDirect search snippet) vs two soft grippers (an AMOLF prototype and a PIAB gripper) on strawberries, raspberries and blackberries. Measured quality changes and pathogen transfer | "both hard and soft grippers can cause damage to fragile fruits". Spectral analysis caught subtle changes that visual checks missed. The force settings were **not found** (full text not opened) | [P] P2 |
| Wang, Hirai, Kawamura 2022, *Front. Robot. AI* 8:789107 (review) | Food-handling end-effectors, sorted by grasping principle | The commercial food grippers named are pneumatic or soft (Schunk food gripper, Soft Robotics mGrip, OnRobot soft gripper, SoftGripping, Festo, RightHand). It has **no comparison of electric parallel grippers** | [P] P3 |
| Blanes et al. 2011, *Span. J. Agric. Res.* (review) | Gripper technologies for fresh fruit and vegetables | Not opened, so no numbers | [P] P4 |
| Goulart, Jarvis, Walsh 2023, *Sustainability* 15:6769 | Metrics (picking area, picking volume, grasp force, damage score) and 9 gripper designs for mango | Best: six flexible fingers, picking area ≈ 150 cm², detachment 74 %, harvest 65 %. Whether any of the designs were commercial electric grippers was not checked | [P] P5 |
| Thilakarathna et al. 2026, arXiv 2602.18835 (preprint, food-waste sorting) | RG2 at 40 N vs Fin-Ray fingers on the RG2 vs suction, on a UR10 | Fin-Ray "achieved the highest overall success" in mixed food waste. Both finger grippers did poorly on flat, rigid items | [O] P6 |

The earlier file `finger_design_inputs.md` adds tomato data from gripper studies (T3 Kultongkham 2021: 1.62 N max per finger; T6 Ansari 2026: 0.2–0.5 N).

---

## 5. Not found (searched)

- **Minimum gripping force:** ROBOTIS RH-P12-RN-UR; JODELL EPG-L80.
- **Force-setting step size:** OnRobot RG2 / RG6; Weiss WSG; DH PGI / AG (only the PGC manual was read, in the companion file).
- **Allowable finger moments:** OnRobot RG2 / RG2-FT / RG6; Robotiq Hand-E; ROBOTIS RH-P12; Inspire; Hitbot.
- **IP ratings:** DH DH-3; ROBOTIS RH-P12-RN-UR; Hitbot Z-EFG-100.
- **UR integration:** Inspire EG2; Hitbot; DH PGI-140-80. Also whether the RG2-FT can run without the Compute Box.
- **Prices:** OnRobot 2FG14, Robotiq Hand-E, DH-3, Schunk EGK 40.
- **Actuated UMI gripper:** stroke, grip force and weight. Only the STEP files would give the stroke.
- **Robotiq measured-force table:** the 30 OO polyurethane row did not extract.
- **DH official site:** en.dh-robotics.com returned HTTP 403, so the DH numbers come from the hosted EN catalog (D1). Its catalog date was not found.

---

## Sources

**OnRobot**
- G1 [M] RG2 datasheet v1.8: https://onrobot.com/storage/datasheets/rg2/datasheet_rg2_v1.8_en.pdf
- G2 [M] RG2-FT datasheet v1.3: https://onrobot.com/storage/datasheets/rg2-ft/datasheet_rg2-ft_v1.3_en.pdf
- G3 [M] RG6 datasheet v2.0: https://onrobot.com/storage/datasheets/rg6/datasheet_rg6_v2.0_en.pdf
- G4 [M] 2FG7 datasheet v2.0: https://onrobot.com/storage/datasheets/2fg7/datasheet_2fg7_v2.0_en.pdf
- G5 [M] 2FG14 datasheet v1.3: https://onrobot.com/storage/datasheets/2fg14/datasheet_2fg14_v1.3_en.pdf
- G6 [O] Vention, OnRobot Tool Flange Connection kit for UR ($98; compatibility list): https://vention.com/parts/onrobot-tool-flange-connection-for-universal-robots-1243
- G7 [O] Vention, RG2 price: https://vention.com/parts/onrobot-rg2-2-finger-underactuated-gripper-1239
- G8 [O] Vention, RG6 price: https://vention.com/parts/onrobot-rg6-2-finger-underactuated-gripper-1238
- G9 [O] Vention, 2FG7 price: https://vention.com/parts/onrobot-2fg7-2-finger-parallel-gripper-1240
- G10 [O] UR forum, connecting an RG2 (V1 digital I/O vs V2/V3 RS485): https://forum.universal-robots.com/t/connect-rg2-gripper-to-controller/33280

**Robotiq**
- R1 [M] 2F-85 / 2F-140 product sheet (May 2025): https://blog.robotiq.com/hubfs/Product-sheets/Adaptive%20Grippers/Product-sheet-Adaptive-Grippers-EN.pdf
- R2 [M] 2F-85 & 2F-140 Instruction Manual for UR (2020-02-11): force control §4.5.1, measured force table p. 59, specs §5.2–5.3, e-Series wrist coupling §3.5.5: https://assets.robotiq.com/website-assets/support_documents/document/2F-85_2F-140_UR_PDF_20200211.pdf
- R3 [M] 2F-85 / 2F-140 manual, Specifications page (HTML, 2019; force and moment limits, electrical): https://assets.robotiq.com/website-assets/support_documents/document/online/2F-85_2F-140_TM_InstructionManual_HTML5_20190315.zip/2F-85_2F-140_TM_InstructionManual_HTML5/Content/6.%20Specifications.htm
- R4 [M] Hand-E product sheet (updated June 2026): https://robotiq.com/hubfs/Hand-E_Adaptive_Gripper_ProductSheet_EN_2024-11_WEB.pdf
- R5 [M] Hand-E product page (50 / 100 mm versions): https://robotiq.com/products/hand-e-adaptive-robot-gripper
- R7 [O] Robotics Center, 2F-140 $5,995: https://www.roboticscenter.ai/ar/store/product/robotiq-2f-140-gripper
- R8 [O] Robotics Center, 2F-85 "From $4,999": https://www.roboticscenter.ai/en/hardware/robotiq-2f-85

**DH Robotics (大寰)**
- D1 [M] DH-Robotics Servo-Electric Grippers catalog EN (PGE, CGE, PGI, PGC, AG-95, AG-145, DH-3), hosted by Unchained Robotics: https://uploads.unchainedrobotics.de/media/file_upload/DH-Robotics-catalog-EN_46faa8dd.pdf
- D2 [O] welectron, AG-160-95: https://www.welectron.com/DH-Robotics-AG-160-95-Adaptive-Electric-Gripper
- D3 [O] welectron, PGIA-140-80: https://www.welectron.com/DH-Robotics-PGIA-140-80-electric-parallel-gripper-with-brake
- D4 [O] UR+ listing, AG-95 (kit contents, URCap): https://universal-robots.com/plus/products/dh-robotics/ag-95-adaptive-gripper

**Weiss / Schunk / Zimmer**
- W1 [M] Weiss WSG series page (WSG 32-068, WSG 50-110): https://weiss-robotics.com/servo-electric/wsg-series/product/wsg/
- W2 [M] Schunk WSG 050-110-B page (moments, finger limits, "discontinued"): https://schunk.com/ca/en/gripping-systems/parallel-gripper/wsg/wsg-050-110-b/p/000000000000306120
- W3 [M] Weiss GRIPLINK Plugin for UR, manual v3.0.0 (Ethernet via GRIPLINK-ET4; Tool I/O Modbus RTU for WPG / INTRAPAL / GRIPKIT): https://weiss-robotics.com/files/griplink-plugins-table/um_griplink_plugin_ur_en.pdf
- W4 [O] UMI repository README (UR5e + WSG50 over IP): https://github.com/real-stanford/universal_manipulation_interface
- K1 [M] Schunk EGK 40-EC-N-B: https://schunk.com/tw/zh/tecnologia-de-garras/garras-paralelas/egk/egk-40-ec-n-b/p/000000000001491770
- K2 [O] Unchained Robotics, Schunk EGK 25: https://unchainedrobotics.de/en/products/end-of-arm-effectors/grippers/finger-grippers/schunk-egk-25
- K3 [O] Vention, Schunk EGK 25 for UR: https://vention.com/parts/schunk-egk-25-gripper-for-small-components-for-universal-robots-2647
- K4 [M] Schunk EGU 50-MB-N-B: https://schunk.com/cz/cs/greiftechnik/parallelgreifer/egu/egu-50-mb-n-b/p/000000000001491536
- K5 [O] Dobot ecosystem, Schunk EGU table: https://www.dobot-robots.com/ecosystem/accessories/schunk-egu-gripper.html
- K6 [O] Vention, Schunk EGU 50 for UR5e: https://vention.com/parts/schunk-egu-50-universal-gripper-for-universal-robots-ur5e-2649
- Z1 [M] Zimmer GEP2016IL-00-B datasheet (includes the GEP2000 series table): https://www.zimmer-group.com/fileadmin/pim/MER/GD/PG/MER_GD_PG_GEP2016IL-00-B__SEN__APD__V1.pdf
- Zimmer UR+ listing [O]: https://universal-robots.com/plus/products/zimmer/zimmer-group-electric-grippers

**ROBOTIS, Inspire, JODELL, Hitbot**
- B1 [M] RH-P12-RN e-manual: https://emanual.robotis.com/docs/en/platform/rh_p12_rn/
- B2 [M] ROBOTIS US store, RH-P12-RN-UR: https://robotis.us/robotis-hand-rh-p12-rn-ur
- B3 [M] RH-P12-RN-UR e-manual page (user manual + URCap downloads): https://emanual.robotis.com/docs/en/platform/rh_p12_rn_ur/
- I1 [O] Knox Labs, Inspire EG2-4C2: https://www.knoxlabs.com/products/inspire-robots-eg2-4c2-electric-gripper. EG2-4B2 (0–15 N, 70 mm, 223 g) comes from a search snippet only: https://www.knoxlabs.com/products/inspire-robots-eg2-4b2-electric-gripper
- J1 [O] Dobot ecosystem, JODELL RG52-050 / RG75-300: https://www.dobot-robots.com/ecosystem/accessories/590.html
- J2 [O] UR+ listing, JODELL RG series: https://universal-robots.com/plus/products/jodell-robotics/rg-series-robot-electric-gripper
- J3 [O] Robotics Center, JODELL RG: https://www.roboticscenter.ai/ar/store/product/jodell-rg-gripper
- J4 [O] Dobot ecosystem, JODELL EPG: https://www.dobot-robots.com/ecosystem/accessories/598.html
- J5 [O] Robotics Center, JODELL EPG-L: https://www.roboticscenter.ai/ar/store/product/jodell-epg-l-gripper
- H1 [O] Robotics Center, Hitbot Z-EFG-100: https://www.roboticscenter.ai/store/product/hitbot-z-efg-100/
- H2 [O] welectron, Hitbot Z-EFG-130: https://www.welectron.com/HITBOT-Cobot-Gripper-Z-EFG-130-for-Fairino

**Universal Robots**
- U1 [M] UR5e datasheet (updated September 2026): https://www.universal-robots.com/manuals/latest/en/datasheets/ur5e/
- U2 [M] UR5e User Manual, PolyScope 5 (doc 710-965-00, SW 5.19, ©2024), §8.7 Tool I/O: https://www.universal-robots.com/manuals/EN/PDF/SW5_19/user-manual-UR5e-PDF_online/710-965-00_UR5e_User_Manual_en_Global.pdf
- U3 [M] UR5e User Manual v5.4 (2019), §5.7 Tool I/O: https://s3-eu-west-1.amazonaws.com/ur-support-site/53188/UR5e_User_Manual_en_US.pdf
- U4 [M] URScript `set_tool_communication` (SW 5.24): https://www.universal-robots.com/manuals/EN/HTML/SW5_24/Content/prod-scriptmanual/all_scripts/set_tool_communication.htm

**Open-source projects and servos**
- O1 [O] actuated-UMI gripper repo (README, BOM, STL / STEP): https://github.com/actuated-umi/actuated-umi-gripper. Project page: https://actuated-umi.github.io/
- O2 [O] actuated-UMI ROS 2 node (`actuated_umi/actuated_umi/actuated_umi_node.py`): https://github.com/actuated-umi/actuated-umi-ros2
- O3 [O] OpenGrip: https://github.com/clayhaight01/OpenGrip
- O4 [O] Yale OpenHand model index: https://www.eng.yale.edu/grablab/openhand/
- O5 [O] Yale OpenHand Model T42: https://www.eng.yale.edu/grablab/openhand/model_t42.html
- O6 [O] Yale OpenHand Model T: https://www.eng.yale.edu/grablab/openhand/model_t.html
- O7 [M] OpenMANIPULATOR-X specification: https://emanual.robotis.com/docs/en/platform/openmanipulator_x/specification/
- O8 [O] SimpleSliderHand: https://github.com/jaspereb/SimpleSliderHand
- O9 [O] UCD 3D-printed 2-finger gripper: https://github.com/wq13552463699/3D_Printed_2_Fingers_Gripper
- X1 [M] DYNAMIXEL XM430-W350 e-manual: https://emanual.robotis.com/docs/en/dxl/x/xm430-w350/
- X2 [M] DYNAMIXEL XL430-W250 e-manual: https://emanual.robotis.com/docs/en/dxl/x/xl430-w250/
- X3 [M] DYNAMIXEL XL330-M288 e-manual: https://emanual.robotis.com/docs/en/dxl/x/xl330-m288/

**Comparisons**
- P1 [P] Schouterden G. et al. 2021, Agronomy 11(10):1922, doi:10.3390/agronomy11101922. PDF: https://mdpi-res.com/d_attachment/agronomy/agronomy-11-01922/article_deploy/agronomy-11-01922.pdf
- P2 [P] Chauhan et al. 2025, Smart Agricultural Technology 12:101445, doi:10.1016/j.atech.2025.101445. Abstract via OpenAlex: https://api.openalex.org/works/doi:10.1016/j.atech.2025.101445. The RG2 / AMOLF / PIAB gripper identities come from the ScienceDirect search snippet: https://www.sciencedirect.com/science/article/pii/S2772375525006768
- P3 [P] Wang Z., Hirai S., Kawamura S. 2022, Front. Robot. AI 8:789107: https://pmc.ncbi.nlm.nih.gov/articles/PMC8794010/
- P4 [P] Blanes C. et al. 2011, Spanish J. Agric. Res. (not opened): https://sjar.revistas.csic.es/index.php/sjar/article/view/2437
- P5 [P] Goulart R., Jarvis D., Walsh K.B. 2023, Sustainability 15:6769, doi:10.3390/su15086769 (abstract via OpenAlex)
- P6 [O] Thilakarathna M. et al., arXiv 2602.18835v2 (2026): https://arxiv.org/abs/2602.18835
