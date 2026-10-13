# R19 prep step 5: making T2L and prep coexist (GitHub #38, 2026-10-14)

Follow-up of `R19_PREP_STEP4.md` §3.5 (the T2L cradle sits in the path of stored prep sets).

**Checking standard:** `ARM=ur5e_enc2_pgc PY=.15`, pot-zone layer `RACK=keyed SPX=1.56 SPY=.20`, unchanged checker:
- 10 mm robot↔environment and arm↔cart part; 5 mm gripper/held↔environment;
- states ≤ 4 mm apart;
- contact windows only on the straight ≤ 50 mm grasp / release approaches.

No gate, mass or force was tuned. Cable re-checks use the adopted routing `ur5e_enc2_pgcc_yp_a-45`.

**Labels**
- [M]: sim-measured.
- [E]: estimate, basis given.
- [S]: sourced (none new here).
- "Smoke": every chain here is a single-seed smoke run (SEEDS=1–2). "Certified" means: planned, then every state re-checked at ≤ 4 mm with the full checker in the pot-zone layout, 0 hits.

---

## 1. Answer first

1. **Conflicts [M].** Five certified sets hit the T2L cradle: carrot, tomato, ctray, bascarrot and ct2p.
   - Empty cradle: penetration depth up to **66.6 mm**.
   - With the pan parked: up to **116.6 mm**.
   - Clear: press, soak, tubempty, tubfill_t15fin, basket_y20p30 (≥ 30 mm with the pan, ≥ 75 mm without).
   - Every hit is in one pocket, in the cart frame: x −0.40…−0.27, y −0.06…+0.14, z 0.91–1.02. That is the arm's low-left reach (tray pick, lever catch tray, chute release).
2. **Route A works, at a price [M, smoke].** All five sets re-plan and pass the ≤ 4 mm re-check with the cradle present. The four non-ct2p sets also pass with the pan parked. Times change by −1.3…+2.0 s per execution, which is within the run-to-run spread of the search ([E] ≈ 0 per meal). But:
   - with the pan parked, **bascarrot fails the cable re-check** (cable run vs the pan, touching on the release retreat); 8 cable-arm re-plans did not close;
   - 3 of the FR5 sets finished so far also hit the cradle, so they would need redoing too;
   - every future prep set inherits the keep-out zone;
   - **no complete staging flow**: the pan never leaves T2L.
3. **Route B: a swing-away cradle [M, smoke].** The leaf turns 90° about a vertical pin toward the left wall, and the pan may stay aboard.
   - Folded, it clears every prep set (≥ 25.2 mm), the cooking chains (≥ 208 mm), the hub edges (≥ 64.6 mm), the cup chains (≥ 132.9 mm) and the stir cycle (≥ 225 mm), with 0 hits.
   - It also clears all 14 FR5 prep files that currently report ok (≥ 23.4 mm).
   - **Fold and unfold are certified**, 4.6 s each, also with the cable. **Added time per meal: 9.2 s** (one fold + one unfold).
   - No existing set needs redoing; `stgwok` is unchanged.
4. **Complete flow with B [M, smoke].** New set `ct2s`: the lever catch tray pours **directly into the pan on the folded cradle**, 26.8 s, certified with both arm models.
   - Cycle: fold → prep → `ct2s` fill → unfold → `stgwok` → fold.
   - This needs neither plating spot 2 nor the failed p2t2l crossing.
5. **Recommendation: B.**

---

## 2. Conflict list (`r19prep5_screen.py MODE=t2l_empty | t2l`, results `screen_t2l_empty.json`, `screen_t2l.json`) [M]

**Method**
- Each stored state is replayed in the set's own scene (≤ 4 mm), with the step-4 cradle (+ pan) added.
- Only the new pairs are measured, with the checker's GJK bound.
- **Depth** is the exact penetration depth (minimum translation distance) of the two convex shapes:
  - separating-axis test over all face normals and edge × edge axes of the checker's hulls;
  - computed on every hit state for the empty cradle, on every 3rd hit state (plus the neighbourhood of the deepest) with the pan.
  - A pair at depth d misses the 10 mm gate by d + 10 mm.
- **Where:** centre of the overlap, in the cart frame (x from the arm base axis, +y toward the counter, z world).

| Set (stored file) | States | Empty cradle: hit states / max depth | With pan: hit states / max depth | Links (deepest) | Part | Where it happens |
|---|---|---|---|---|---|---|
| carrot (`chain_carrot_full`) | 3,415 | 513 / **66.6 mm** | 1,567 / **116.6 mm** | forearm fa_1 66.6, wrist 1 65.9, fa_3 52.4, upper arm ua_4 47.1 (pan: ua_4 116.6, w1_0 85.8) | cradle plate, bracket_y (pan body) | pick approach (60), lifted/out and up/lane (243), chute release approach (172); x −0.36…−0.27, y −0.03…+0.12, z 0.91–0.93 (pan: to z 1.01) |
| tomato (`chain_tomato_full`) | 2,810 | 71 / **16.2 mm** | 181 / **38.1 mm** | wrist 1 w1_1, gripper envelope | cradle plate (pan body) | pick approach only (empty); + pick, lifted (pan); x −0.39…−0.37, y 0.00…+0.13 |
| ctray (`chain_ctray_full`) | 3,391 | 771 / **30.5 mm** | 1,483 / **68.9 mm** | gripper envelope 30.5, fingers 19.0 (pan: gripper upper 68.9, palm 62.4, w2_1 40.9) | cradle plate, bracket_y 7.8 (pan body) | pick approach, raised 18 mm, pulled out 15 cm, set-down retreat; x −0.40…−0.32, y +0.02…+0.13 |
| bascarrot (`chain_bascarrot_full`) | 1,887 | 43 / **33.5 mm** | 43 / 33.5 mm | gripper envelope | cradle plate (pan body 6.2) | pick approach only; x −0.38, y +0.11…+0.14, z 0.93 |
| ct2p (`prep4/chain_ct2p_full`) | 3,431 | 770 / **30.5 mm** | (2,242 / 68.9 mm)* | as ctray | as ctray | as ctray (same pick) |
| press, soak, tubempty, tubfill_t15fin, basket_y20p30 | 227–4,733 | 0 (gate ≥ 75.6 mm) | 0 (≥ 30.5 mm) | — | — | — |

\* ct2p pours into the pan on plating spot 2, so "pan on T2L" cannot coexist with it; listed for completeness.

**Cart parts vs the environment.** The checker does not gate these pairs (`Checker.required` returns None). The closest is the step-4 cradle plate edge vs the spatula handle tip on its R18b rest: 16.1 mm (cart sweep −1.48…1.46). Not a hit.

---

## 3. Route A: re-plan with the cradle present (`r19prep5_chain.py ... T2L=empty|pan`)

### 3.1 Runner and pick carts
- `r19prep5_chain.py` is generated from `r19prep4chain.py` (md5-checked, unchanged) by asserted text replacements. Additions:
  - `T2L=empty|pan` puts the step-4 cradle into the set's scene; it is stored, so the verifier rebuilds it;
  - the p5 layer;
  - `KFC=<label>:<cart>` fixes a keyframe's cart;
  - the food join rule also for the new food sets;
  - output to `results/r19/prep5/`.
- **Regression [M]:** `chain_soak_so1` reproduced exactly (105 states, max |Δq| = 0.0, loads and approaches identical), with the first and the final version of the runner.
- **Why pick carts are needed:** the first round (free carts) failed on the pick approaches, where the gripper's 50 mm retreat passes over the plate. The cradle spans x = cart −0.40…−0.24, so a pick stays clear only with the item ≥ 0.46 m left of the base or ≤ 0.18 m left of it. Fixed carts from that rule, found in 4 smoke rounds:

| Set | Run (passing) | Carts (anchors) | Time vs stored | ≤ 4 mm re-check (pot), states / hits / min reserve | Cable `yp_a-45` |
|---|---|---|---|---|---|
| carrot | `Ap1` (= `Ae5e`, same path) | pick −0.95, tap −0.016, chute −1.37 | **45.7 s** vs 47.0 (−1.3) | 2,994 / 0 / 1.9 mm | **ok** |
| tomato | `Ap1` (= `Ae3c`), lane L1 (−0.75, 0.10, 1.15) | −0.72 / −0.016 / −0.35 | **35.9 s** vs 36.5 (−0.6) | 2,618 / 0 / 1.0 mm | **ok** |
| ctray | `Ap1` | −1.29 / −0.16 / −1.19 (the tray picked with the lever on the arm's right) | **40.1 s** vs 38.1 (+2.0) | 4,419 / 0 / 2.0 mm | **ok** |
| bascarrot | `Ap1` (pan) / `Ae2b` (empty) | pick −0.90, basket −0.476 | **15.0 s** vs 14.4 (+0.6) | 2,053 / 0 / 1.32 mm; 2,814 / 0 / 3.0 mm | **pan: FAIL** (12 play + 90 retreat states, −3.7 mm, touching); empty: ok |
| ct2p | `Ae2a` (empty: its pan is on plating spot 2) | −1.29 / −0.16 / −1.19 | **39.7 s** vs 37.9 (+1.8) | 4,418 / 0 / 2.0 mm | **ok** |

- The `Ap1` runs were planned with the pan parked. A path clear of cradle + pan is clear of the empty cradle (a removed part only removes pairs).
- **bascarrot with the pan, cable arm.** Eight smoke re-plans planned directly with `ARM=ur5e_enc2_pgcc_yp_a-45` (`Apc1–8`) did not close:
  - basket anchor at carts −0.62 / −0.55 / −0.42: no IK;
  - other variants: lane joins blocked;
  - pick at −1.30: no IK;
  - one RRT variant hit the 5-min limit.
- **Carrot, a runner weakness that is not cradle-specific.** Two passing carrot runs (`Ae3a`, `Ae3c`) failed the re-check with 28–31 self-contact states (upper arm vs gripper):
  - wrist 3 reached the join at +359.9° (range ±360°) while the next piece continued at 0.4°, so the joint-linear playback contains a −359.5° unwind;
  - the certified `carrot_full` has the same kind of unwind (wrist 1, −359.5° → −2.6°); it happened to be collision-free;
  - joins do not check joint-range wrap; pick cart −0.95 avoids it.
- **Time [M → E].** Per execution −1.3…+2.0 s vs the stored full runs. That is within the spread of the search itself (carrot stored: smoke 49.9 s, full 47.0 s), so Route A costs ≈ 0 s per meal [E].

### 3.2 What Route A leaves
- bascarrot with the pan parked is not cable-clean (above).
- **FR5 [M, screen]:** of the 14 FR5 prep files that currently report ok, the fixed cradle hits:
  - `carrot_fr5x_cD` (52 states, 33.5 mm);
  - `bascarrot_fr5` (42, 33.5 mm);
  - `ctray_fr5` and `ctray_fr5full` (865 / 910 states, 30.5 mm; with the pan up to 80.4 mm).
  
  So FR5 tomato and ct2p would also need doing with the cradle, once they exist.
- Every future prep set must be planned around the cradle zone (cart constraints at every low-left pick).
- No staging flow: in A the pan stays on T2L. Filling needs the plating-spot-2 → T2L link (600 s RRT lanes: no join at −0.19/−0.25; a 47° pan tilt at −0.16), and direct pours into the deployed T2L pan failed in step 4 (24 smoke configurations).

---

## 4. Route B: a cradle that swings away (`kitchen19p5.py`)

### 4.1 Design [E: all sizes, masses and hardware are design proposals, not sourced]

**Leaf and hinge**
- The step-4 cradle plate (160 × 160 × 4 mm) and its 30 × 30 mm arm are **one rigid leaf**, turning about a **vertical pin** at the arm's root, H = cart frame (−0.32, −0.17, 0.911).
- **Deployed (0°)** = exactly the step-4 T2L pose, so `stgwok` picks the pan as before.
- **Folded (+90°)**: the leaf lies along the cart's left side ("swings toward the wall": the left rail end). The plate centre moves to (−0.54, −0.17): behind the arm base line, left of the cart, at the same height.
- **The pan may stay aboard.** The swing keeps it level, and the pin carries no gravity moment about its axis.

**Fixed part**
- The mast bar of step 4, lowered 42 mm to z 0.854–0.884. The leaf turns over it with a **12 mm gap**: the 10 mm cart-part gate + 2 mm, like the pan's 12 mm pick.
- In that gap, **not modelled** (as the R17 faucet lever's hub): the pin, two bushes, end stops at 0° and 90°, and a detent at each end.
- Loads on the hinge [E]:
  - cantilever ≈ 2.2 N·m (filled pan 0.64 kg × 0.22 m + leaf 0.45 kg × ~0.15 m);
  - detent holding needed ≥ ~0.1 N·m (1.1 kg × 0.5 m/s² cart E-stop × 0.2 m), so ≥ 0.3 N·m proposed.

**Knob**
- A keyed 30 mm block on a stub, 70 mm left of the leaf arm and 30 mm from the pin, top 20 mm over the arm.
- It is outside `stgwok`'s gripper corridor (x −0.32 ± 0.04, z ≈ 1.01).
- Gripped **from above** (straight 50 mm approach, jaws across the block). The fold is then a wrist-3 roll about the vertical plus a 76 mm TCP arc.
- A side-grip variant (from −x) was also reachable.

**Layer**
- `cfg['r19p5'] = dict(state='deployed'|'folded'|'held', kind='swing'|'flip', knob, pan, angle)`.
- A no-op without the key, so all earlier scenes are unchanged.
- The held leaf (+pan) objects are `fold_swing_top[_pan]`.

**Flip-down alternative (screened only)**
- An x-axis hinge; the leaf hangs down to z ≈ 0.61.
- Folded, it also clears the prep sets (≥ 25.2 mm, intermediate geometry).
- Rejected: the pan must come off first, and the deployed leaf needs a lock against ~2.2 N·m of droop.

### 4.2 Clearance screens (final geometry; `r19prep5_screen.py`) [M]

| State | Paths | States | Min gate | Hits |
|---|---|---|---|---|
| **Folded + pan** (`screen_fold_final_swing_pan.json`) | 10 prep sets (+ approaches) | — | **25.2 mm** (carrot pick approach, forearm vs fixed bar) | 0 |
| | 6 cooking chains + approaches | — | **208.4 mm** | 0 |
| | 22 hub edges | — | **64.6 mm** | 0 |
| | 6 cup chains (held cup as a 0.20 m sphere) | — | **132.9 mm** | 0 |
| | stir cycle | — | **225.0 mm** | 0 |
| | total | 100,585 | | 0 |
| Folded, empty | — | — | ≥ the above (a removed pan only removes pairs) | 0 |
| **Deployed + pan** (`screen_deployed_final_swing_pan.json`) | cooking chains / hub / cups / stir | 76,263 (with stgwok) | 78.1 / 58.6 / 132.9 / 195.6 mm (as step 4) | 0 |
| | `stgwok_full`, `stgwok_m5` (own cradle replaced by the p5 leaf) | — | **2.0 mm** (held pan over the plate, as certified); approaches 9.2 mm | 0 |
| **Folded + pan vs FR5** (`screen_fold_fr5_swing_pan.json`, `ARM=fr5_j6_pgc_sp20`) | 14 FR5 prep files reporting ok now | — | **23.4 mm** | 0 |

**Cart parts vs the environment.** Not a checker pair; my screen applies 10 mm.
- Folded: no static geometry within 30 mm anywhere along any path.
- Deployed: the parked pan passes 13.6 mm from the spatula handle tip. This is the step-4 geometry, unchanged.

### 4.3 Fold / unfold sets (`ACT=fold | unfold`, `r19prep5_actions.py`) [M, smoke]
- **Keyframes.** The leaf frame sits on the pin, so the motion is a pure rotation in 15° keyframes (≤ 2° steps). The cart is fixed, because the leaf rides on it.
- **Approach / release.** Straight 50 mm down onto the knob, the leaf a cart part. The held leaf (+pan, food 0.40 kg [E]) is fully carried by the arm in the sim: conservative for the arm; the pin load is not simulated.
- **Plume rule on:** they may run with the heat on (plume ≥ 413 mm).

| Set | Cart | Time | ≤ 4 mm re-check (pot): states / hits / min reserve | Cable `yp_a-45` | PGC moment / joint ratio |
|---|---|---|---|---|---|
| fold, pan aboard (`fold_s1`) | 0.172 | **4.6 s** (2.0 s turning) | 466 / 0 / 1.99 mm (leaf vs bar) | ok (466 states) | 1.79 N·m / 0.41 |
| unfold, pan aboard (`unfold_s1`) | 0.172 | **4.6 s** | 494 / 0 / 1.99 mm | ok | 1.79 / 0.48 |
| fold / unfold, no pan (`s1np`) | 0.172 | 4.6 / 4.6 s | 466 / 494, 0 hits | ok / ok | 0.55 / 0.39–0.46 |
| fold / unfold, pan, cart −0.45 (`s1c45`) | −0.45 | 4.6 / 4.6 s | 466 / 494, 0 hits | ok / ok | 1.79 / 0.41–0.48 |

- The same sets pass at both carts and the knob probes are identical at −0.45 / 0.17 / 1.21 [M]. So the fold is done wherever the cart already is: **no extra cart transit**.
- **Added time [M]: 9.2 s per fold + unfold pair.**
  - Per meal: 9.2 s when the cradle stays folded except around one `stgwok`.
  - [E]: 9.2 s per staged wok dish if each dish has its own fill–pour cycle. Both states clear all cooking paths, so the cradle may stay folded everywhere except right around `stgwok`.

---

## 5. Complete staging flow (coordinator's question: p2t2l failed)

**Route B closes it [M, smoke]**, with `ACT=ct2s`: the step-3 catch tray pulled out at the lever, poured (+120° roll, mouth 12 cm over the rim) into the **pan riding on the folded cradle**, then returned.
- **Reach probes:** pour pose 8/96 starts, 42 mm reserve, at any cart; tray seat with the cradle folded 8/96.
- **`ct2s_s2`** (planned with `ur5e_enc2_pgc`) passed its re-check, then failed the cable check: 38 states, cable run vs the pan body, −2.3 mm.
- **`ct2s_c3`** was planned with the cable arm itself (lane raised to z 1.12):

| Set | Carts | Time | Re-check `ur5e_enc2_pgc` (pot) | Cable `yp_a-45` |
|---|---|---|---|---|
| **`ct2s_c3`** | pick −0.614, pour −0.52, return −0.464 (joins 0°) | **26.8 s** (vs ct2p 37.9 s into plating spot 2) | 3,752 states, 0 hits, min reserve 2.0 mm | 3,804 states, 0 hits |

**Cycle per staged dish**
1. Cradle folded, empty pan aboard; prep sets run.
2. `ct2s` fills the pan (26.8 s).
3. Unfold with the filled pan (4.6 s).
4. `stgwok` (20.2 s, certified, unchanged) pours into the wok and returns the empty pan.
5. Fold (4.6 s).

No plating-spot-2 staging, no crossing in front of the base.

**Not covered**
- Filling from the slicer drawer bowl or a prep bowl into the folded pan (only the lever output is done).
- Washing the pan between dishes.
- Pieces sticking.
- Slosh / pan creep on the swinging leaf (pins locate it; not modelled).

**Route A has no such flow** (see §3.2).

---

## 6. Recommendation: **B (swing-away cradle)**

| | Route A (fixed cradle, re-plan) | Route B (swing-away cradle) |
|---|---|---|
| Time per meal | ≈ 0 [E] (per set −1.3…+2.0 s [M], within search spread) | **+9.2 s** per fold/unfold pair [M]; `ct2s` 26.8 s instead of ct2p 37.9 s + the missing link |
| Certified sets to redo (UR5e) | 5 (carrot, tomato, ctray, bascarrot, ct2p): done in smoke; **bascarrot-with-pan not cable-clean** | **0**; `stgwok` unchanged (screened) |
| New sets | — | 2 (fold, unfold) + `ct2s` for the flow: certified incl. cable |
| FR5 (`fr5_j6_pgc_sp20`) | ≥ 4 of the FR5 files ready now hit (carrot, bascarrot, ctray ×2), + tomato / ct2p later | 0 to redo (folded clears all 14 ready FR5 files ≥ 23.4 mm); fold / unfold / ct2s to plan on the FR5 (lane 3) |
| Future prep sets | must all avoid the cradle zone | unconstrained (folded zone ≥ 23 mm clear) |
| Complete staging flow | **no** | **yes** (fold → prep → ct2s → unfold → stgwok → fold) |
| Mechanism risk [E] | none | moderate: pin + 2 bushes (2.2 N·m cantilever), end stops, detents (≥ 0.3 N·m); the deployed stop must repeat to ~1–2 mm (stgwok picks 12 mm over the plate with 2.0 mm reserve). Failure modes: detent not engaged (leaf drifts), pan creeping on the leaf. All standard parts; nothing sourced |

---

## 7. Methods and honesty notes
- **Smoke runs only.** Every chain is SEEDS=1–2. The re-checks are full ≤ 4 mm checks with the pot-zone layer; full-setting runs are the controller's (§8).
- **Modelling simplifications**
  - The hinge (pin, bushes, stops, detents) is not modelled; the 12 mm gap is where it sits, as the R17 faucet lever's 30 mm hub gap.
  - The leaf's and pan's weight is carried by the arm in the sim; in reality the pin carries it.
- **Conflict depth (§2)** is the exact penetration depth of the convex hulls the checker uses (SAT). With the pan it is computed on every 3rd hit state plus the deepest neighbourhood, so it is a lower bound there; the empty-cradle values cover every hit state.
- **Two screen results are lower bounds** (the 30 mm AABB cap of `r19prep4_screen`): "≥ 30.0 mm" values and the cups' held-cup sphere bound.
- **Superseded files**
  - Route B screens and probes before the final knob / 12 mm gap: `screen_fold_swing*.json`, `screen_fold_flip.json`, `screen_*_cook.json`, `screen_deployed_swing_stgwok.json`, and `probe_sw_*_c+0.17 / c+1.21` (10 mm gap).
  - The final ones are `screen_fold_final_swing_pan.json`, `screen_deployed_final_swing_pan.json` and `screen_fold_fr5_swing_pan.json`.
  - `ct2s_s1/s2` pass the standard re-check but `s2` fails the cable check; superseded by `ct2s_c3`.
- **MuJoCo gap misreads:** none observed here (no counter-seam or plate-edge flags in any re-check). No gate changed.
- **`arms.py` changed during this session** (00:49, by another agent; content change only `r19cable.add(..., arm)` for the tool-connector routings). It happened before my first chain run, so all results use one version. Protected files are unchanged by me (md5 before = after): `r19prepchain.py`, `r19prep_verify.py`, `r19prep3_actions.py`, `r19prep4*.py`, `kitchen19p4.py`.
- **Process hygiene.** One early screen was killed by `timeout` and left 15 idle spawn workers of my own (parent dead, started at the kill time); I stopped exactly those. All later pool runs have their own clean time limit.

---

## 8. Controller lanes (each may exceed 5 min)
```bash
cd /c/Users/admin/Documents/YJGames/robot_rail/sim/r10/claude
PY=C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe
A="ARM=ur5e_enc2_pgc"; C="ARM=ur5e_enc2_pgcc_yp_a-45"; P="RACK=keyed SPX=1.56 SPY=.20"
# lane 1 (Route B, ~15-30 min): full settings of the three new sets, then the <= 4 mm re-check and the cable re-check
$PY r19prep5_chain.py ACT=fold   PAN=1 FC=.172 SEEDS=3 TRIES=12 KEEP=4 TAG=full $A
$PY r19prep5_chain.py ACT=unfold PAN=1 FC=.172 SEEDS=3 TRIES=12 KEEP=4 TAG=full $A
$PY r19prep5_chain.py ACT=ct2s CP=-.52 LANEC=-.52 PLUME=0 MOUTHZ=.12 CLANE=-0.954,-.16,1.12 SEEDS=3 TRIES=12 KEEP=4 TAG=full $C
for f in chain_fold_full_ur5e_enc2_pgc chain_unfold_full_ur5e_enc2_pgc chain_ct2s_full_ur5e_enc2_pgcc_yp_a-45; do
  $PY r19prep5_verify.py FILE=results/r19/prep5/$f.json NPROC=16 $A $P
  $PY r19prep5_cable.py prep FILE=results/r19/prep5/$f.json $C $P WORKERS=16; done
#  (if a full run picks a failing candidate, the smoke settings reproduce the passes:
#   fold/unfold SEEDS=1 TRIES=8 KEEP=1; ct2s SEEDS=1 TRIES=8 KEEP=2 as above)
# lane 2 (Route A, only if A is chosen; ~40-90 min): full settings with the cradle + pan, re-check, cable
$PY r19prep5_chain.py ACT=carrot SEEDS=3 TRIES=12 KEEP=4 "KFC=pick:-0.95" T2L=pan TAG=Afull $A
$PY r19prep5_chain.py ACT=tomato SEEDS=3 TRIES=12 KEEP=4 "KFC=pick:-0.72" L1=-0.75,.10,1.15 T2L=pan TAG=Afull $A
$PY r19prep5_chain.py ACT=ctray SEEDS=3 TRIES=12 KEEP=4 STG=0.17,.15,180 CLANE2=0.0,.06,1.04 CDEG=-120 "KFC=pick:-1.29;over the staging bowl:-0.16;in front of the lever base:-1.19" T2L=pan TAG=Afull $A
$PY r19prep5_chain.py ACT=ct2p PLUME=0 SEEDS=3 TRIES=12 KEEP=4 "KFC=pick:-1.29;over the pan:-0.16;in front of the lever base:-1.19" T2L=empty TAG=Afull $A
$PY r19prep5_chain.py ACT=bascarrot SEEDS=3 TRIES=12 KEEP=4 "KFC=pick:-0.90" PLAN=1 PLAN_S=300 PLAN_N=4 T2L=pan TAG=Afullc $C   # the cable-clean case is open
for s in carrot tomato ctray ct2p; do $PY r19prep5_verify.py FILE=results/r19/prep5/chain_${s}_Afull_ur5e_enc2_pgc.json NPROC=16 $P; $PY r19prep5_cable.py prep FILE=results/r19/prep5/chain_${s}_Afull_ur5e_enc2_pgc.json $C $P WORKERS=16; done
# lane 3 (Route B on the FR5, ~20-40 min): the same three sets on fr5_j6_pgc_sp20 (smoke first; its cable variant if adopted)
F="ARM=fr5_j6_pgc_sp20"
$PY r19prep5_chain.py ACT=fold PAN=1 FC=.172 SEEDS=2 TRIES=10 KEEP=2 TAG=fr5 $F
$PY r19prep5_chain.py ACT=unfold PAN=1 FC=.172 SEEDS=2 TRIES=10 KEEP=2 TAG=fr5 $F
$PY r19prep5_chain.py ACT=ct2s CP=-.52 PLUME=0 MOUTHZ=.12 CLANE=-0.954,-.16,1.12 SEEDS=2 TRIES=10 KEEP=2 TAG=fr5 $F
for s in fold unfold ct2s; do $PY r19prep5_verify.py FILE=results/r19/prep5/chain_${s}_fr5_fr5_j6_pgc_sp20.json NPROC=16 $P; done
```
**Quick follow-up (< 1 min):** when the FR5 agent finishes, re-screen the folded cradle against all FR5 prep files:
`$PY r19prep5_screen.py MODE=fold P5_kind=swing PAN=1 KINDS=prep SETS=<comma list of ok FR5 files> ARM=fr5_j6_pgc_sp20 PY=.15 TAG=fr5`.

**Next steps (not done)**
- The hinge hardware: sourcing, detent torque, stop repeatability.
- Filling the folded pan from the slicer drawer bowl / prep bowls.
- Folded-cradle screens vs the FR5 cooking chains.
- The cups' T2L caddy (same site) vs the swing leaf.

---

## 9. Files
**New code** (nothing else changed)
- `kitchen19p5.py`: fold-away cradle layer (swing / flip, knob styles, held leaf ± pan objects, mesh rule). A no-op without `cfg['r19p5']`.
- `r19prep5_actions.py`: `fold`, `unfold`, `ct2s` keyframes.
- `r19prep5_chain.py`: generated copy of `r19prep4chain.py` (`T2L=`, `P5STATE=`, `KFC=`, the p5 layer, the food join rule for the new sets, output to `prep5/`).
- `r19prep5_verify.py`: generated copy of `r19prep4_verify.py` + the p5 layer (tolerant KEY=VALUE parser).
- `r19prep5_cable.py`: runs `r19cable_check.py` (unchanged) prep mode with `r19prep5_verify` scenes. Output `results/r19/prep5/cable/prep/`.
- `r19prep5_screen.py`: T2L / fold screens with penetration depth, where and phase, a cart-part vs environment check and a clean time limit.
- `r19prep5_probe.py`: knob reach and catch-tray-into-folded-pan probes.

**Results** (`results/r19/prep5/`)
- Conflict list: `screen_t2l_empty.json`, `screen_t2l.json`.
- Route A: `chain_{carrot,tomato,ctray,bascarrot}_Ap1`, `chain_ct2p_Ae2a`, `chain_bascarrot_Ae2b` + `_verify4mm_pot.json`.
- Route B: `chain_{fold,unfold}_{s1,s1np,s1c45}` + `_verify4mm_pot.json`; `chain_ct2s_c3_ur5e_enc2_pgcc_yp_a-45` + `_verify4mm_pot.json`.
- Screens (final): `screen_fold_final_swing_pan.json`, `screen_deployed_final_swing_pan.json`, `screen_fold_fr5_swing_pan.json`, and the FR5 cradle screens `screen_t2l_empty_fr5.json`, `screen_t2l_fr5.json`.
- Cable: `cable/prep/*__ur5e_enc2_pgcc_yp_a-45.json` (15).
- Regressions: `chain_soak_regress_so1`, `chain_soak_regress2_so1`.
- Kept for the record: failed / superseded smoke runs (`*_Ae1..Ae5*`, `*_Apc*`, `ct2s_s1..s5, c2, c4`), 83 `probe_*.json`, logs in `logs/`.
