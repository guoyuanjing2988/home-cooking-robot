# R19 pot zone (GitHub #37 spider rest, #8 lid rack), Windows, 2026-10-13

Checking standard throughout: `ARM=ur5e_enc2_pgc PY=.15` (DECISIONS 2026-10-13), gates 10 / 5 mm, states ≤ 4 mm, the unchanged checker.
Tolerances with the #13 tools (`r19tol_*`, run unchanged through a wrapper). Labels: **[M]** measured in the sim, **[E]** estimate.

## 0. Answer first

1. **Spider (#37): move the spider rest from (1.52, 0.36) to (1.56, 0.20)** and re-plan only its two rest-side pieces. [M]
   - The upper arm now keeps **≥ 19.4 mm** from the cabinet over the hood on the whole spider set (was 10.4 mm). On the re-planned rest-side pieces the overhead clearance is ≥ 28 mm. The remaining 19.4 mm is in the stored, unchanged pot-side middle.
   - Tilt toward the counter tolerated before the gate: **0.33°** (was 0.038° on the play, 0.075° on the approach). The approaches tolerate 0.855°. Contact comes at 0.68°.
   - y tolerance: 9.4 mm (was 1.1 mm).
   - **New binding pair:** the spider bowl vs the pot's right ear, 5.0 mm past the 5 mm gate, in x only (x tolerance 5.0 mm).
   - The play passes the ≤ 4 mm full re-check with 0 hits (4,108 states; approaches 49 + 49).
   - **Docking-stop corner** (play): ≥ +2.9 mm [E] from the per-axis tolerances. The exact corner replay is controller lane 2. The approaches keep ≥ 10 mm (was −1.6 mm). The other spots tried keep +5.65 mm on the play [M].
2. **Lid (#8): a keyed V-saddle rack plus a declared insertion window.** [M]
   - **The rack:** two pads with 90° V-grooves under the upright lid's rim (`kitchen19pot.py`). Geometric capture: ±14.8 mm across the rim plane and ±90 mm along the rack. The design claim is ±5 mm.
   - **The window:** the last 50 mm of the existing straight vertical move into the rack is a DECISIONS lift/approach window. The only exempt pairs are the held lid's parts vs the rack's parts.
   - **The 1.0 mm rack-seat reserve is gone as a binding gap.** The stored lid path re-checks clean in the new layout (2,410 states, 113 of them in the window, 0 hits) and is kept unchanged, so the hub's lid endpoints do not move.
   - A full lid re-plan with the window also passes: 20.2 s, 0 hits. It is kept as evidence.
   - **The lid's next binding is the lift off the pot**, 3.0 mm in z, 0.30° tilt. That is the R17 8 mm "seat" at the pot. It is itself a straight 20 mm lift along the pot's face normal. Declared as a second window (optional, `POTWIN=1`), the lid tolerates 0.434° tilt and 11.0 mm in z.
   - **Lead-in** under the docking-stop box: worst rim displacement at the guides 1.9 mm (x), plus arm accuracy ±2 mm and rack placement ±1 mm. That is 4.9 mm against a 14.8 mm capture (margin 9.9 mm). The as-designed budget still fits geometrically: 11.9 mm against 14.8 mm.
3. **Re-screen:** 0 hits for both moved fixtures. They were checked against every stored chain and approach, the 22 hub edges, the 3 prep sets and the 6 checked cup chains (65,756 and 70,195 states). [M] Details are in §4.
   - SPIDER→H_POT: re-planned for the (1.62, 0.26) candidate, it passed straight in 4.48 s. For the chosen spot both SPIDER edges are lane 1 (> 5 min each).
4. **FR5 (#2) side result:** at (1.56, 0.20) the spider block no longer stops the FR5 lid. [M]
   - `fr5_j6_pgc_sp20` lid in the keyed-rack layout: 20.2 s, 0 hits at ≤ 4 mm (136 window states).
   - `fr5_j6_pgc` spider re-planned at the new spot: 51.4 s, 0 hits, arm ≥ 22 mm from the cabinets.
   - Of 18 spots screened against that FR5 lid path, the only front spot that clears it is (1.56, 0.20), by 5.5 mm. That is why it was chosen over (1.62, 0.26).
5. **Nothing loosened, no shared file edited.** All code is new. The default scene is byte-identical with the layer imported but not installed (md5 checked).

## 1. Why the spider was tight

- At the old rest the spider's grip block sits at (1.52, 0.078, 1.164). The 45° handle puts the TCP high, so the elbow ends up at z ≈ 1.64 m, about 10 mm in front of the face of the cabinet over the hood (y = 0.23).
- A lean of the cart toward the counter moves that point by about 28 mm/° (lever ≈ 1.6 m): 1.12 mm reserve → 0.04° tolerance.
- Re-planning at the same spot does not help.
  - With a 15 mm overhead gate (`CABGATE=5`) the pick anchor still has 6 valid postures. But all of them are on other IK branches, and their joins to the stored lane / pot postures swing 190–282° and move the spider 42–56 mm (> 5 cm join rule). The same failure appeared in the #12 enc2 re-plan.
  - The stored branch at other cart positions gives at most 4.0 mm past the gap.
  - So the rest itself must move.

## 2. Spider rest (#37)

### 2.1 Method

1. **Partial re-plan** (`r19pot_chain.py PARTIAL=`).
   - Only the two anchors that depend on the rest are solved again: pick and "on the rest". They use r17chain's own `candidates()` with the stored chain's states as IK seeds (`SEEDUR`).
   - Each candidate is followed to its meet (`follow()`), with its approach (`approach()`). It is joined at the meet to the stored arrival from the pot side (`meet_join()`, food rule 5 cm / 15°).
   - The stored middle (lane → pot → plate → lane) is kept verbatim. Among the candidates that pass, the one with the largest exact overhead clearance is kept.
   - `CABGATE=5` adds a stricter gate of +5 mm on top of the normal gap. It applies to every robot geom vs the cabinet over the hood, the hood, upper cabinet 2, its door and its sensor (exact GJK bound), and to every followed step, join, approach and candidate.
2. **Fixture screen** (`r19pot_screen.py`). Every stored state is replayed with the spider (cradle pad + spider) at the candidate spot, and only the moved fixture's pairs are measured, exactly.
3. **Certificates and tolerances.**
   - `r19pot_check.py`: ≤ 4 mm, `Checker.check(full=True)`.
   - `r19pot_tol.py`: the #13 evaluator, unchanged.

### 2.2 Candidates

The overhead column is the minimum, on the re-planned rest-side pieces + approach + join, of arm-to-overhead distance minus the 10 mm gap, in mm.

| Spot (x, y) | Overhead | Screen: worst pair (lid arm vs spider block) | FR5 lid path | Block past the counter edge |
|---|---|---|---|---|
| 1.52, 0.36 (old) | 0.37 stored / 4.0 best | 13.2 | **hit** | −78 mm (inside) |
| 1.52, 0.30 / 0.42 | no joinable candidate | — | — | |
| 1.56, 0.28 | 8.7 | **hit −3.5** | — | |
| 1.56, 0.36 / 1.60, 0.38 / 1.63, 0.34 | 4.2 / 3.8 / 5.3 | | | |
| 1.60, 0.26 | 9.8 | 7.2 | — | 22 mm |
| 1.60, 0.22 / 1.58, 0.22 | 13.9 / 14.6 | 8.8 / 7.5 | hit −1.5 | 62 mm |
| 1.60, 0.24 / 1.62, 0.24 | 11.7 / 11.2 | 6.3 / 10.4 | hit −8.4 | 42 mm |
| 1.62, 0.26 | 9.4 | 13.9 | hit −10 | 22 mm |
| 1.63, 0.22 / 1.63, 0.26 | 12.8 / 9.3 | 0.5 / 17.0 | — / hit | |
| **1.56, 0.20 (chosen)** | **18.1** | **13.3** | **+5.5 clear** | **82 mm** |
| 1.62, 0.36 | not re-planned (neighbours at y 0.34–0.38 give 3.8–5.3) | | +23 clear | |
| 1.52, 0.42 / 1.56, 0.44 / 1.60, 0.44 | no joinable candidate (no stored-branch IK) | | +26 (at 1.52, 0.44) / +42 / — | |

- Spots at y ≤ 0.24 give the most overhead room: the arm reaches less toward the wall, and the elbow stays lower and farther forward.
- x ≥ 1.63 puts the spider bowl within 4 mm of the lid rack.

### 2.3 The chosen set: `results/r19/pot/chain_spider_s+1_pot_1.56_.20_ur5e_enc2_pgc.json`

| | Old (1.52, 0.36) | New (1.56, 0.20) |
|---|---|---|
| Re-plan | — | partial, `CABGATE=5`; carts 1.093 (as stored); joins 0° |
| Time | 52.6 s | 50.7 s |
| ≤ 4 mm re-check, final layout (keyed rack) | adopted, 0 hits | 4,108 + 49 + 49 states, 0 hits |
| Exact minimum, arm vs overhead | 1.12 / 2.17 mm past gap (play / approaches) | 9.44 / 18.1 mm past gap (19.4 / 28.1 mm) |
| Exact minimum, any pair (play) | 1.12 (cabinet) | 5.0 (bowl vs pot ear +1, 5 mm gate) |
| tilt_x− tolerance, gate / contact | 0.038° / 0.40° (play); 0.075° / 0.43° (approach) | **0.33° / 0.68°** (play); 0.855° / 1.38° (approaches) |
| y+ tolerance (play) | 1.1 mm | 9.4 mm |
| x− tolerance (play) | ≥ 15 mm | 5.0 mm (bowl vs pot ear) |
| Docking-stop corner, gate | −2.63 (play), −1.59 (approach) | approaches ≥ 10; play ≥ +2.9 [E], lane 2 (at 1.60–1.62 / 0.24–0.26 measured +5.65) |
| §5 rule (tilt ≥ 0.3°, y ≥ 3.5 mm) | fail | pass |

- The play's overhead minimum of 9.44 mm (ua_4 vs the cabinet over the hood) is at the lane-to-pot climb of the stored middle. It is the same number for every spot.
- The SPIDER hub edges start from the new endpoint.
  - `hubs.json` was rebuilt with the same tuck. Only the SPIDER endpoint changed: its 2π relabel is now J4 −1.
  - SPIDER→H_POT and SPIDER→H_WOK are lane 1.

## 3. Lid rack (#8)

### 3.1 Design (`kitchen19pot.py`, `RACK=keyed`; replaces the R16 base + two fins inside their footprint x 1.70–1.80)

- **Two pads** under the upright lid (rim plane y-z, rim x 1.725–1.735, centre y 0.25, z 1.017), at y = 0.25 ∓ 0.09.
  - Each pad carries a 90° V-groove whose line is the rim's tangent there. The contact normals are 35.5° off vertical, toward the lid centre: a saddle.
  - Flanks are 20 mm long, 6 mm thick, 40 mm along the groove, on a support block. A 5 mm plate joins the pads.
  - Grooves centre x and square the rim plane (rotation about y and z). The saddle centres y and z.
- **Seated pose = the R16 rack pose, unchanged.** Rim corners sit 0.5 mm off the flanks. At the release pose (4 mm above the seat, as in R17) the gap is 2.8 mm; 50 mm above it, 33.8 mm.
- **Capture.** The mouth half-width is 19.8 mm, so the 10 mm rim is captured up to ±14.8 mm in x. Along y the saddle captures about ±90 mm. The design claim is ±5 mm.
- **Not positive:** rotation about x (the lid's own plane). Friction holds it [E]: 0.8 kg lid, μ 0.3 → ~0.4 N·m against ~0.06 N·m from the tab. The tab stays in the gripper during insertion.

### 3.2 The window (DECISIONS 2026-10-08, lift/approach window)

- **Where:** TCP on the segment from the release keyframe (`in the rack`, 4 mm above the seat) up 50 mm along +z. Lateral tolerance 0.05 mm; rotation fixed (matrix elements within 5·10⁻⁴).
- **Which pairs:** held lid parts (`R_gripper_r16_lid_*` except the grip tab) vs `r19pot_rack_*`.
- **Applied in:**
  - `Checker.permissions` (planning and re-check), the same hook the checker's own grasp / release windows use;
  - the tolerance evaluator, as a pair exclusion in the window states, for gate and contact alike.
- **Nothing else gets a window.** The stored path's last piece is a straight vertical 76 mm move, so its last 50 mm qualifies with no re-plan; the first 26 mm keep the full gate. In the play this covers 113 states.

### 3.3 Results (the stored lid chain, unchanged, spider at (1.56, 0.20) unless noted)

| | R17/R18 rack | Keyed rack + window | + optional pot lift window (`POTWIN=1`) |
|---|---|---|---|
| ≤ 4 mm re-check | 1.0 mm reserve at the seat | 2,410 + 55 + 166 states, **0 hits**, 113 window states | — |
| Exact minimum (play) | 1.0 (rim vs rack base) | 3.0 (rim vs pot wall, lift-off) | 9.99 (rim vs hood) |
| tilt_x− gate / contact | 0.122° / 0.65° | **0.30°** / 0.65° | **0.434°** / 0.65° |
| z− gate | 0.99 mm | 3.0 mm | 11.0 mm |
| y+ | 10.0 mm | ~10 mm (grid: +5 → 3.0, +10 → −0.01) | ~10 mm |
| Rack placement (fix group), x / y / z | z 1.0 mm | ≥ 15 / ≥ 15 / ≥ 15 mm outside the window; inside, the lead-in capture (§0) | |
| Approaches (lift-off, rack release) | — | tilt 0.616° / 0.766°; docking-stop corner ≥ 10 mm | |
| Docking-stop corner (play) | −0.60 mm | ≈ +1.4 mm [E]: tilt grid −0.1° → 2.0, z −0.5 mm; lane 2 | ≈ +7 [E]; lane 2 |

- Measured with the spider at (1.62, 0.26), and again at (1.56, 0.20) for the tilt search (0.30°). The spider pairs differ by < 1 mm (screen: 13.3 vs 13.9 mm past the gate).
- **Re-plan with the window** (`r19pot_chain.py ACT=lid RACK=keyed WINDOW=1`, full r17chain, 160 s): ok, 20.2 s.
  - Its "over the rack" cart is 1.348 (stored: 1.326).
  - ≤ 4 mm re-check: 2,366 states, 0 hits, 122 in the window.
  - Same binding as the stored chain (3.0 mm at the pot).
  - **The stored chain is the one kept,** so the LID hub edges stay valid.
- **The pot lift window.** The R17 lid action grasps the lid seated on the pot, lifts it 8 mm (unchecked seat), and the play starts there; it then goes straight up to 20 mm.
  - Declaring that straight 20 mm lift as a window (lid parts vs the pot rim `r16_pot_wall*`) follows the same rule.
  - It is offered as an option because #8 asked only for the rack. Both seats still need compliance or force control at contact (#26).

## 4. Re-screen of the moved fixtures (moved-fixture pairs only, exact; `results/r19/pot/screen_*.json`)

| Path set | Spider at (1.56, 0.20) | Keyed rack |
|---|---|---|
| 5 adopted chains (wok, plate 2, lever, lid, spatula) | 0 hits; worst lid play 13.3 mm past gate (upper arm vs spider block) | 0 hits; lid play 32.3 mm outside the window (113 window states, intended contact ≥ 2.8 mm nominal) |
| Their 9 approaches | ≥ 73 mm | ≥ 30 mm |
| 22 hub edges (`hub_py.15_ur5e_enc2_pgc`) | ≥ 70 mm (LID_RACK / SPIDER edges) | ≥ 30 mm |
| Prep sets (`chain_*_full_ur5e_enc2_pgc`), cup chains (s10a/b/d/f, s11S, s11enc) | ≥ 500 mm (held object bounded by a 0.2 m sphere) | ≥ 775 mm |
| New spider chain vs keyed rack | its full re-check (0 hits) | |

Other R19 jobs are running on the machine (prep chains for #4). If the prep sets change, re-run the screen (lane 3, about 2 min).

## 5. Files (all new; no shared file changed)

- **Code:**
  - `kitchen19pot.py`: the layer (spider rest, keyed rack, windows). Inactive unless `install()` is called.
  - `r19pot_chain.py`: r17chain executed from its source, plus `CABGATE`, `WINDOW` / `POTWIN`, `RACK`, `PARTIAL`.
  - `r19pot_screen.py`: the fixture re-screen.
  - `r19pot_check.py`: the ≤ 4 mm certificate.
  - `r19pot_tol.py`: the #13 tools with the new paths, the layer and the windows, plus `capture`.
  - `r19pot_hub.py`: r19hub in the new layout, written to its own folder.
- **Results:** `results/r19/pot/`.
  - `summary.json`.
  - Chains:
    - `chain_spider_s+1_pot_<x>_<y>_ur5e_enc2_pgc.json` (the chosen one is `1.56_.20`);
    - `chain_lid_s-1_pot_keyed_ur5e_enc2_pgc.json` (re-plan);
    - `chain_spider_s+1_pot_1.56_.20_fr5_j6_pgc.json`;
    - `chain_lid_s-1_pot_keyed_nospider_fr5_j6_pgc_sp20.json`.
  - `check_*.json`, `screen_*.json`, `tol/<tag>/`, `hub_final*/`, `logs/`.

## 6. Controller lanes (each over 5 min; the hubs.json for lane 1 is already written)

```bash
cd /c/Users/admin/Documents/YJGames/robot_rail/sim/r10/claude
PY=C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe
S=results/r19/pot/chain_spider_s+1_pot_1.56_.20_ur5e_enc2_pgc.json
L="RACK=keyed SPX=1.56 SPY=.20 ARM=ur5e_enc2_pgc PY=.15"
# lane 1: the two SPIDER hub edges for the new endpoint, then the graph (est. 10-15 min)
H="SPIDER=$S HUBTAG=final_1.56_.20 $L"; D=results/r19/pot/hub_final_1.56_.20
$PY r19pot_hub.py edge A=SPIDER B=H_POT PLAN_S=120 $H > $D/log_SPIDER__H_POT.txt 2>&1
$PY r19pot_hub.py edge A=SPIDER B=H_WOK PLAN_S=120 $H > $D/log_SPIDER__H_WOK.txt 2>&1
$PY r19pot_hub.py graph $H > $D/log_graph.txt 2>&1
# lane 2: the corner replays and the rest of the grids (est. 30-60 min; the lid play is the long one)
$PY r19pot_tol.py SCENES=play:spider19 PARTS=scen-dock_stops,scen-as_designed SPIDER=$S TOLTAG=spider_1.56_.20 $L WORKERS=2 DEADLINE=5400 > results/r19/pot/logs/lane2_spider.txt 2>&1
$PY r19pot_tol.py SCENES=play:lid19 PARTS=scen-dock_stops,scen-as_designed,grid-y,grid-z TOLTAG=lid_final_1.56_.20 $L WORKERS=4 DEADLINE=5400 > results/r19/pot/logs/lane2_lid.txt 2>&1
$PY r19pot_tol.py SCENES=play:lid19 PARTS=scen-dock_stops,grid-tilt_x,cart-tilt_x,cart-z POTWIN=1 TOLTAG=lid_final_1.56_.20_potwin $L WORKERS=4 DEADLINE=5400 > results/r19/pot/logs/lane2_lid_potwin.txt 2>&1
# lane 3: the full #13 set on the two pot-zone paths (as R19_TOLERANCE 9.6), then the re-screen once the #4 prep sets settle
A="SCENES=play:spider19,app:spider19:0,app:spider19:1,play:lid19,app:lid19:0,app:lid19:1 SPIDER=$S TOLTAG=final_full $L"
$PY r19pot_tol.py $A PARTS=cart-x,cart-y,cart-z,cart-yaw,cart-tilt_x,cart-tilt_y,fix WORKERS=10 DEADLINE=5400 > results/r19/pot/logs/lane3.txt 2>&1
$PY r19pot_tol.py $A PARTS=grasp-x,grasp-y,grasp-z,grasp-rot ROTMAX=4 WORKERS=10 DEADLINE=3600 >> results/r19/pot/logs/lane3.txt 2>&1
$PY r19pot_screen.py "SPOTS=1.56,.20" RACK=keyed TAG=recheck ARM=ur5e_enc2_pgc PY=.15 WORKERS=16 >> results/r19/pot/logs/lane3.txt 2>&1
# lane 4 (#2): the FR5 option that the lid needs (J6 +-360, 20 mm adapter) for the spider too, full chain (est. 5-10 min)
$PY r19pot_chain.py ACT=spider SIGN=1 SPX=1.56 SPY=.20 RACK=keyed TRIES=12 SEEDS=3 SEEDUR=results/r17/chain_spider_s+1_final_ur5e_enc2_pgc.json TAG=pot_full ARM=fr5_j6_pgc_sp20 PY=.15 > results/r19/pot/logs/lane4_fr5sp20_spider.txt 2>&1
```

## 7. Open points

1. **Aisle.** At (1.56, 0.20) the spider's keyed grip block is 82 mm past the counter edge, at 1.16 m: a pan-handle-like protrusion at the end of the counter run.
   - Every stored robot path clears it by ≥ 13 mm past the gate.
   - If people at that corner matter more than the FR5, (1.62, 0.26) gives the same spider result for the UR5e with 22 mm protrusion. But it keeps the FR5 lid blocked.
2. **The windows are intended contact.**
   - The rack window makes the lead-in work. The lid still drops 4 mm at release, as in R17, and touches the V-flanks.
   - The pot lift-off is a seat. Both belong to #26 (compliance / force control) if contact force matters.
   - The lid's rotation in its own plane is held by friction, not by a key.
3. **The spider play's next limit** is the bowl vs the pot's right ear (x 5.0 mm) and the unchanged middle (overhead 9.4 mm, tilt 0.33°). Both pass the §5 rule. The old spot had no x limit there.
4. **The FR5 lid needs the 20 mm adapter (`sp20`).** The FR5 spider certified here is `fr5_j6_pgc` (no adapter). Lane 4 checks the spider with `sp20`. The rest of the FR5 set with `sp20` is #2's.
5. The docking-stop corner replays for the spider play and the lid play are lane 2. The values given are [E] from the per-axis tolerances.
