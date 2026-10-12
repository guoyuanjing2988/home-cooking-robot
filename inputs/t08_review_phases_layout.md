# T08 review

## Verdict

**R1 Pro: 16/16 FEASIBLE. Ours: 16/16 FEASIBLE. Ours mass: 125.506 kg model/budget; 8.023 kg per arm. Ready for a CAD round: YES, for engineering integration and verification.** R1's reference mass remains the specified 126 kg. The T07 fixture-collision failures and our replacement-mass failures are resolved in the delivered comparative scene. Six remaining findings define the next round's work.

This verdict applies the binding nominal-force, two-key-pose screen. Check-force overloads remain reported diagnostics. It does not establish completed hardware, endurance or powered mobility. I accept the user's unbraked J5–J7 decision and retain its power-loss residual; no wrist brake requirement is added. The CAD decision is to proceed because the previous geometry, mass and powered-static shoulder blockers now have reproducible solutions, while the remaining integration details require CAD to resolve.

I read [mandoline_golden.py](../../sim/golden/mandoline_golden.py) first, then [the authoritative T07 review](../t07/reviewer.md), all three T08 posts, and the T08 scripts/results. [Inventory](../../sim/t08/reviewer/audit/inventory.json) records 229 producer files: scripts parsed, JSON results read, model/source XML parsed, and hashes retained, including explicitly archived research. Producer inputs were left unchanged. [Review summary](../../sim/t08/reviewer/review_summary.json) contains the verdict and verification records.

| Phase | R1 feasible seeds | Ours feasible seeds | R1 nominal / check ratio | Ours nominal / check ratio |
|---|---:|---:|---|---|
| P01 Pick carrot and lift 100 mm | 2 | 2 | 0.759 / — | 0.683 / — |
| P02 Rinse carrot, wrist -60 to +60 deg | 1 | 2 | 0.808 / 0.810 | 0.739 / 0.741 |
| P03 Place carrot on clamp board | 11 | 12 | 0.295 / — | 0.273 / — |
| P04 Peel clamped carrot, 120 mm | 17 | 18 | 0.340 / 0.384 | 0.334 / 0.384 |
| P05 Load carrot in holder on deck | 13 | 13 | 0.212 / — | 0.216 / — |
| P06 Mandoline carrot, 200 mm | 13 | 13 | 0.687 / 0.975 | 0.687 / 0.974 |
| P07 Pick potato | 6 | 6 | 0.219 / — | 0.197 / — |
| P08 Rinse potato, wrist -60 to +60 deg | 2 | 3 | 0.321 / 0.322 | 0.308 / 0.308 |
| P09 Peel clamped potato, 120 mm | 19 | 18 | 0.362 / 0.466 | 0.312 / 0.452 |
| P10 Mandoline potato, 200 mm | 11 | 11 | 0.716 / 1.004 | 0.716 / 1.004 |
| P11 Greens into rinse basket and spinner pump | 11 | 12 | 0.606 / 0.606 | 0.539 / 0.539 |
| P12 Greens knife cuts at 40 mm spacing | 3 | 3 | 0.395 / 0.338 | 0.298 / 0.289 |
| P13 Tomato wedger, 50 N total with R handle | 2 | 2 | 0.499 / 0.776 | 0.513 / 0.616 |
| P14 Lift loaded catch tray and tilt 60 deg over output | 1 | 1 | 0.965 / — | 0.863 / — |
| P15 Pick Y-peeler and return | 3 | 4 | 0.745 / — | 0.624 / — |
| P16 Pick knife and return | 3 | 3 | 0.813 / — | 0.681 / — |

All rows are FEASIBLE. Denominators are 96, except P11's 192 seeds per stroke. P11/P12 counts use the authoritative T07 convention: independently admitted strokes, paired by torque rank; each stroke has a frozen base. Best nominal/check ratios can come from different nominal-admitted seeds. P10's 1.004 check ratio is not a nominal failure. The left arm parks for all these R-only demonstrations; P13 uses the expressly allowed single-hand option with the full total force.

## Independent reruns and exemption review

I performed ten fresh 96-seed mink sweeps, five requested phases on each model, using reviewer-owned [rerun.py](../../sim/t08/reviewer/rerun.py). They reproduce delivered feasible counts, best ratios and solved q values within 1e-8; ratio discrepancies are below 1e-9.

| Phase | Fresh R1 feasible | R1 nominal / check | Fresh ours feasible | Ours nominal / check |
|---|---:|---|---:|---|
| P01 | 2/96 | 0.758809 / — | 2/96 | 0.683180 / — |
| P02 | 1/96 | 0.807773 / 0.809835 | 2/96 | 0.738745 / 0.740807 |
| P06 | 13/96 | 0.686698 / 0.974584 | 13/96 | 0.686698 / 0.974232 |
| P13 | 2/96 | 0.499290 / 0.776321 | 2/96 | 0.513424 / 0.615977 |
| P14 | 1/96 | 0.965293 / — | 1/96 | 0.863446 / — |

Runs were foreground CPU chunks with at most four numerical workers, one numerical-library thread each, the shared four-slot lock, a 1,140 s timeout and a 1,900 MiB guard. Auxiliary audits ran only after slots were available, with explicit 90/300 s timeouts and a 1.8 GiB job cap. Largest measured sweep worker: **228.64 MiB**; longest: **271.31 s**. Rerun q/load/error records and resource logs are in [reruns](../../sim/t08/reviewer/reruns/). Final reviewer output is checked below 2 GB.

**No additional mounting or guide contact exemption remains.** The [T07→T08 full diff](../../sim/t08/reviewer/audit/t07_to_t08.diff), [golden→T08 full diff](../../sim/t08/reviewer/audit/golden_to_t08_full.diff) and [golden evaluation-function diff](../../sim/t08/reviewer/audit/golden_to_t08_functions.diff) make the changes reviewable. Only `P13`, `scene_tree` and `Checker.bind_model` function bodies changed from T07: guide-post exemption removed, hardware relocated, and prefix matching replaced by explicit intended identities. All contact evaluation, IK, torque, grip, seed admission and phase-summary functions are AST-identical to T07. The golden SHA256 remains `28e1cb23ea8ca0706588cf9361061423309e12e678763d766e9b558c784d191e`.

The 10/5/0 mm thresholds, padding correction, weld, parent/child, ACM, same-gripper and base/floor skips match golden. Its same-gripper predicate is inherited unchanged. The only generalized intended contacts are food with its basket/clamp/holder, tools with their work surfaces, and pickup/return support surfaces accepted in T07. Mount clamps, lugs, receivers/supports, guide posts and guide feet are forbidden obstacles. No ACM pair was added. P06 retains the 65 mm sphere, 80 mm work offset and 0.55 kg load. All prescribed force vectors and the 5 mm/3° acceptance remain unchanged; the 60 N P06 check follows this round's table, rather than golden's separate 70/100 N exploration.

The golden gravity-plus-Jacobian calculation is preserved; generalized tools separate COM and work sites, which coincide for the golden holder. Phase continuous ceilings remain torso 108 Nm and arms 55,55,25,25,18,18,18 Nm. The original golden has no grip calculation: the added evaluator uses the specified μ=0.5, SF=1.5, 150 N total jaw normal, and declared form-fit bearing capacities without changing those numbers.

I independently replayed **554 admitted endpoints** across all 16 phases on both models: actual pose errors, floor bounds, frozen base, contacts, Newton–Euler gravity, work/COM Jacobians and grip. Independent torque-ratio discrepancy is **zero**. Each ours process-stroke pool also contains a witness within the chosen catalog actuator ratings, including the 60 Nm yaw core; this separate hardware sizing check does not alter the binding phase ceiling. [R1 replay](../../sim/t08/reviewer/audit/r1pro_saved_replay.json), [ours replay](../../sim/t08/reviewer/audit/ours_saved_replay.json), [actual skipped R1 contacts](../../sim/t08/reviewer/audit/r1pro_intended_contacts.json) and [ours contacts](../../sim/t08/reviewer/audit/ours_intended_contacts.json) retain the evidence.

Signed-distance checks against every repaired mounting/guide solid confirm all robot 10 mm and gripper/tool 5 mm gaps across admitted endpoints. Minimum held-tool gaps to the repaired clamp/post are identical on both models: **P06/P10 38.169 mm; P13 12.660 mm; P14 21.994 mm**, against 5 mm. These repair the T07 forbidden overlaps geometrically.

## Actuator, mass and powered-range assessment

The manufacturer's parameter tables match the selected core values:

| Use | Core | Rated Nm | Core kg | Gear ratio | Core envelope mm |
|---|---|---:|---:|---:|---|
| Arm J1–J3; torso T4 | [WHJ60](https://develop.realman-robotics.com/en/joints/parameter/WHJ60/) | 60 | 1.040 | 100 | 70 × 91 |
| Arm J4 | [WHJ30](https://develop.realman-robotics.com/en/joints/parameter/WHJ30/) | 30 | 0.750 | 80 | 60 × 86.5 |
| Torso T2/T3 | [WHJ120](https://develop.realman-robotics.com/en/joints/parameter/WHJ120/) | 120 | 2.300 | 100 | 88 × 109 |
| Torso T1 | [WHG32240](https://develop.realman-robotics.com/en/joints/parameter/WHG32240/) | 240 | 5.700 | 100 | 142 × 125 |

WHJ60/30 list latch brakes; WHJ120/WHG32240 list electromagnetic brakes. That wording is not used as spring-holding proof. [Miki's BXR-LE table](https://www.mikipulley.co.jp/en/electromagnetic-clutches-brakes/offbrakes/holding/bxr-le) confirms spring-applied, electrically released holding operation, size035 **0.120 kg / 0.62 Nm**, size040 **0.160 kg / 1.32 Nm**, and size050 **0.400 kg / 3.20 Nm** at the input. The twelve credited springs are arm J1–J4 and all torso joints; the six original wrist inertias/collision meshes are retained exactly, without added brakes. Ideal output holds are 62 Nm at arm J1–J3, 49.6 at J4, and torso 320/132/132/62 Nm. These are input torque multiplied by ratio, with no backdrive-friction credit. Source checks and limitations are recorded in [sources.json](../../sim/t08/reviewer/audit/sources.json). The [2026 Galaxea specification](https://docs.galaxea-dynamics.com/R1Pro/en/docs/2026/) confirms the binding 126 kg, 7.8 kg arm, 3.5 kg at 0.6 m and 1680 Wh facts; the [A2 hardware guide](https://docs.galaxea-ai.com/Guide/R1Pro/hardware_introduction/R1Pro_Hardware_Introduction/) supplies the native no-brake statement.

The independently added mass budget is:

| Assembly boundary | kg |
|---|---:|
| Published baseline, battery/grippers retained | 126.000 |
| Remove published two-arm boundary | −15.600 |
| New arms, including native wrists/omitted hardware | +16.046 |
| Remove original URDF torso links | −17.620 |
| New torso, including springs/endcaps/structure | +15.280 |
| Control/harness/regeneration allowance | +0.400 |
| Common integration growth | +1.000 |
| **Total** | **125.506** |

The compiled subtree is **125.506000028 kg**, 4.494 kg below the approximate 130 kg target and 31.644 kg below T07. Per arm: 3.870 kg cores +0.480 kg springs +0.380 kg endcaps +1.100 kg structure +2.193 kg native wrist/retained hardware = 8.023 kg. Left/right native wrists differ, but their published-minus-URDF hardware corrections produce equal totals. Those corrections are counted once; no battery mass reduction is credited.

I replayed **81 empty and 81 simultaneous dual-3 kg height samples**, at actual grasp sites 0.6 m world-forward of the shoulders. Heights span 0.500–1.300 m. The final-model gravity, payload torques, stability and contacts reproduce; the loaded poses also remain clear in the comparative T08 scene. Maximum torso ratios against selected cores are **0.802936 empty / 0.872298 loaded**, rather than a brake being credited as powered torque. Maximum knee load is **209.352 Nm against 240 Nm**; loaded level/5° margins are at least **49.683/22.778 mm**. Arm and credited spring-holding statics pass these samples. The height study's 0.9 sizing target is a disclosed design margin, not a new prep acceptance rule. The native park width is independently **674.928 mm**, within 720 mm. [Mass, width and height replay](../../sim/t08/reviewer/audit/design_replay.json).

## Findings

1. **HIGH — The integrated actuators remain a custom mechanical proposal.** Public torque, brake and mass entries check out, but motor-input shaft access, rotor hub, encoder/endcap fit, bearing loads, sealing and continuous thermal performance are not demonstrated by adding catalog brake length plus 4 mm. The selected torso yaw core supplies 60 Nm even though the immutable phase checker uses 108 Nm: delivered witnesses fit 60 Nm, and unrestricted 108 Nm hardware capability must not be claimed. Distinct transient motor ratings are unpublished. The spring catalog includes permissible braking work, but stop speed/reflected inertia/energy and engagement sequencing have not been allocated to those limits. CAD must build the twelve actual torque paths and provide assembled mass/COM, heat and stopping calculations.

2. **MEDIUM — Mass and COM closure still depend on assembly assumptions.** The arithmetic/model agree and the target is met as a budget. However, 17.620 kg torso removal is a URDF-link boundary, 4.700 kg new structure plus endcaps is estimated, and **30.382879 kg** of retained chassis hardware is concentrated at (−0.07,0,0.20) m. The published-arm discrepancy is sensibly restored on the arm bases, but its true distribution remains unknown. Raising the chassis calibration 0.60 m would lose **12.128 mm** of worst-direction 5° margin; moving it 0.10 m forward shifts loaded COM **23.104 mm**. The knee has **30.648 Nm** to rated torque and **6.648 Nm** to the author's 0.9 sizing target. CAD must close the BOM, load-bearing structures and actual COM before treating the mass/range margins as hardware results.

3. **MEDIUM — There are two fixture scenes and remaining work-datum/moving-mass proxies.** The light-design standalone model/post has 6 mm retainers, rearward posts and an output bowl at x=0.120 m; the independently verified comparison uses full 54110 clamps/lugs, outboard posts/feet and the bowl at x=0.000 m. Use the comparison layout below as the CAD authority. Light-design's P11 check ratio 0.149 covers the pump stroke alone; the comparative full-phase value is **0.539**, including placement gravity, which is the reviewed value. Peeler work is still at food-centre height; handles/keys also receive intended food-contact skips. The tray begins in a solid deck proxy without its real catch-space void. P13's **0.18 kg** remains a bridge proxy, without separately reconciled native plunger/guide-bearing mass; P11 does not model basket return from the faucet into the spinner. These are disclosed modelling gaps, not new phase rejection gates. CAD must supply genuine blade/deck datums, a removable catch cavity, guide-bearing mechanics and complete moving-mass boundaries, then rerun the unchanged screen.

4. **MEDIUM — Key bearing limits are proposed proof capacities.** The μ=0.5 and SF=1.5 friction gate is correct. Keyed tools use **150 N / 15 Nm** declared capacities inherited from T06; they are not measured assembly strengths. The design now allocates moment through two 24×8 mm lands at 40 mm spacing, reaching about **1.999 MPa** on selected witness cases against a proposed 5 MPa interface allowance. That calculation improves the T07 report but does not establish land material, anchor, gripper/jaw reaction or tool-specific proof capacity. CAD must define and check those load paths while retaining the fixed bearing/friction evaluation numbers.

5. **MEDIUM — Powered mobility and runtime remain conditional.** Width passes. The 20 mm threshold has only **2.55 mm** nominal steering clearance; the counterbalanced dual-load case requires ideal wheel torques **20.091/20.089/23.020 Nm**. Ramp statics pass selected poses, but a 5° ramp needs **112.437 N** ideal traction and **7.871 Nm** total ideal wheel torque. The fixed-wheel URDF contains no powered drive rating. The 1680 Wh / 626.8 W budget gives **2.680 h**, but duty averages are allowances; the two-hour ceiling is **840 W**. CAD must specify wheel/steer drives, tires, compliant clearance and mounting, power distribution/regeneration and brake-release control, and deliver a cycle-energy validation plan. These open user requirements are not treated as prep torque or contact failures.

6. **HIGH — Accepted unbraked wrists permit substantial power-loss tool motion.** The revised brake pattern is correct. The delivered zero-stiction gravity scenarios give up to **363.831 mm** hand sag, **174.349°** tool rotation and **11.679 J** released energy with a retained 3 kg load. Those are numerical free-wrist scenarios, not measured timing or guaranteed endpoints; gripper retention and environment interception are unresolved. Right wrist check-force witness envelopes reach **23.652/19.317/23.709 Nm** at J5/J6/J7 versus known 18 Nm continuous limits; best nominal phase passes remain valid. CAD must preserve the requested unbraked wrists and build tool docks/retention, proximal brake control, and a controlled unload/shutdown arrangement around this residual, with sudden-loss behaviour explicitly retained in the brief.

## CAD round and authoritative layout

**Proceed with one engineering CAD round.** Build the retained R1 seven-axis arm/four-joint torso geometry with twelve spring-brake interfaces, native unbraked wrists and the 125.506 kg budget as the starting ledger. The round must deliver actuator sections/shaft and encoder interfaces; load-bearing links and verified mass/COM; the common galley fixture assemblies and tool keys; wheel/steer/power hardware; and brake/tool-retention shutdown provisions. Use the reviewed loaded height q bank and prep witness q bank as fit/load references. Update inertias and collision solids from the resulting CAD and rerun the original numerical acceptance rules before freezing the next design brief. Sampled quasistatics establishes powered-static capability at documented poses; connecting motion, thermal duty and hardware validation remain the round's verification work.

Counter z=0.850 m; free slabs x −1.80…−0.70 and −0.11…0.69 m, y 0…0.60 m. Stove x 0.69…1.47 m is protected. Complete assembly bounds, including mounts, feet, open-vessel walls and stored tools, give **30.5 mm minimum separation**. The [independent layout audit](../../sim/t08/reviewer/audit/layout.json) confirms all eight assemblies fit on free counter.

| Station | Reference centre x,y m | Complete footprint mm | Actual x bounds; y bounds m |
|---|---|---|---|
| board | 0.080, 0.190 | 315.0 × 295.0 | -0.0775…0.2375; 0.0425…0.3375 |
| mandoline | 0.470, 0.120 | 345.0 × 160.6 | 0.2975…0.6425; 0.0610…0.2216 |
| wedger | 0.390, 0.400 | 216.0 × 280.0 | 0.2820…0.4980; 0.2600…0.5400 |
| output_bowl | 0.000, 0.470 | 204.0 × 204.0 | -0.1020…0.1020; 0.3680…0.5720 |
| peeler_tray | 0.590, 0.410 | 90.0 × 160.0 | 0.5450…0.6350; 0.3300…0.4900 |
| basket | -1.530, 0.200 | 420.0 × 340.0 | -1.7400…-1.3200; 0.0300…0.3700 |
| spinner | -1.125, 0.200 | 270.0 × 270.0 | -1.2600…-0.9900; 0.0650…0.3350 |
| knife_dock | -1.005, 0.475 | 360.0 × 100.0 | -1.1850…-0.8250; 0.4250…0.5250 |

Mandoline clamp centres are (0.320,0.200,0.86075) and (0.620,0.200,0.86075) m, with 19×43.2×21.5 mm envelopes and 24×12×16 mm receiver lugs. [Mitee-Bite's 54110 table](https://www.miteebite.com/products/compact-toe-clamps/) supports the clamp dimensions; anchorage/lug strength and the 0.20 kg clamp mass allowance remain engineering estimates. Wedger posts are at x=0.290/0.490, y=0.470 m, with 16×16×458.6 mm proxies and 20×24×12 mm guide feet. The [Nemco reference](https://nemco.com/catalog/easy-wedger/) supports the vertical-pusher product concept; the relocated guides are custom engineering. Retain the reviewed 50 mm receiving-end supports in P01/P03/P05 and P11's 0.725 m sink-basket bottom. Bowl x=0.000 m applies in every phase.

Tool dimensions and mass provenance remain [T06 tools.csv](../../sim/t06/tool_ref/results/tools.csv) and [fixtures.json](../../sim/t06/tool_ref/results/fixtures.json), with estimates distinguished in [T08 fixture records](../../sim/t08/scene_fix/results/fixtures.json). No tool dimensions, held loads, forces, gap, IK, torque, friction or safety-factor number was changed during review. No purchasing or supplier contact occurred.

Reproduction: run reviewer `rerun.py --batch r1pro:P01 r1pro:P02 ours:P01 ours:P02`; then `--batch r1pro:P06 ours:P06 r1pro:P13 ours:P13`; then `--batch r1pro:P14 ours:P14`, in the shared venv. Run reviewer `audit.py inventory`, `r1pro`, `ours`, `design` and `layout` through scene_fix's bounded foreground runner (90 s inventory/layout, 300 s numerical audits), then `finish_review.py` with a 90 s timeout. Numerical audits can use free slots while other bounded sweeps run; combined numerical workers must remain at most four.
