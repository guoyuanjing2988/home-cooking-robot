# R19 prep audit step 4: slicer output and the cooking-time staging spot (GitHub #38, 2026-10-13/14)

Follow-up of `R19_PREP_STEP3.md` §1, §2, §4, §5. Checking standard: `ARM=ur5e_enc2_pgc PY=.15`, the current cooking layout (pot-zone layer `RACK=keyed SPX=1.56 SPY=.20`), the unchanged checker (gates 10 mm robot–environment, 5 mm gripper/held–environment, 10 mm arm vs a cart part; states ≤ 4 mm; contact windows only on the ≤ 50 mm straight grasp/release approaches). No gate, mass or force was tuned.

**Labels.** [M] measured in the sim (all chain results are **single-seed smoke runs**); [E] estimate, basis stated; [S] sourced (none new here). "Checked" = the whole set planned with the r17chain method and every state re-checked at ≤ 4 mm with the full checker.

---

## 1. Answer first

| Set | What it does | Time (r17 timing) | ≤ 4 mm re-check: states (play + approaches), hits | Min reserve | Plume min | PGC moment (held kg) | Joint ratio |
|---|---|---|---|---|---|---|---|
| **stgwok** (cooking time) | staging pan picked off its T2L cradle on the cart → over the wok → tipped −135° about the lug (2 s) → level → back onto the cradle; cart fixed at **1.21** (right of the wok, the pan stays on the arm's left) | **20.2 s** [M] (+ cart transit to 1.21, e.g. 4.2 s from H_WOK 0.172 at 0.25 m/s [M timing rule]) | 1,795 + 51 + 51, **0** (same in the pot-zone layout) | **2.0 mm** (pan 12 mm over its cart cradle vs the 10 mm cart rule) | **28.2 mm** (heat may stay on) | 0.70 N·m (0.64 kg = pan 0.22 + lug 0.02 + food 0.40 [E]) | 0.352 |
| **ct2p** (prep time, cooker off) | lever catch tray pulled out → poured (−120°) into the staging pan standing on plating spot 2 → back, slid in | **38.3 s** [M] | 3,470 + 87 + 95, **0** (same in the pot-zone layout) | **2.0 mm** | — (PLUME=0: prep time) | 0.34 N·m (0.30 kg) | 0.379 |

Both pass [checked, smoke]. **Not closed:**
1. **The link plating spot 2 → T2L** (`p2t2l`): both ends follow, both approaches pass, but the pan must cross 0.68 m in front of the arm base. IK continuation hits the base plate; the RRT planned carry found no path in 4 × 100 s. Controller lane 2 (600 s budget).
2. **Any direct pour into the cart-mounted pan** (catch tray: 24 smoke configurations; bowl at plating spot 2: 7; drawer bowl: 3). Cause below (§3.4).
3. **Slicer output, option (a) drawer:** designed, modelled and **reachable** [probe] (seat 6/96, slid 20 cm 5/96, lifted 8/96 starts), and clear of every stored path by ≥ 117 mm. The whole set did not close in 12 smoke configurations (§2.3).
4. **Option (b) chute:** excluded by geometry [M]: 40 mm of drop available against 106–350 mm needed, and no free bowl spot in the open strip (§2.4).
5. **New finding: T2L hardware conflicts with prep.** The cradle (even empty) and the pan clear every cooking path, but seven stored prep sets put the wrist/forearm through them (§3.5). The cups' larger T2L caddy (R19_CUPS) was never screened against the prep sets and is affected too.

So the cooking-time half is solved and verified (pick from T2L, pour into the wok with the plume rule, return), and the catch-tray output reaches a staging pan at prep time. What is missing is getting the filled pan (or any container) onto the cart without crossing in front of the base, plus a T2L mount that is out of the way during prep.

---

## 2. Slicer output (`kitchen19p4.py`, `r19prep4_probe.py`, `ACT=drawer`)

### 2.1 Geometry that decides it [M, scene model]
- Slicer (turned 90°) body x −1.795…−1.585, y 0.06–0.39, top 1.05 m. Spout x −1.74…−1.64, y 0.39–0.45, **bottom 0.95 m**; it discharges at the back. Out bowl under the cabinet at (−1.69, 0.50).
- Upper cabinet from y 0.23 (door 0.212–0.23), bottom 1.35 m. Raw tray x −1.515…−1.195, y 0.04–0.34 (7 cm right of the slicer). R07 potato staging bowl x −1.504…−1.296, y 0.356–0.564.

### 2.2 Option (a): printed side drawer (modelled)
- **Guide** (`p4_drawer_*`): 5 mm plate from under the spout to the out position, two 15 mm rails (8 mm radial play to the bowl's wall corners), a left stop; axis y **0.495** (step 3: 0.50) so the 204 mm wide guide fits between the slicer face (0.39) and the wall (0.60) with 3 mm each side. The bowl itself is the drawer; it is pulled +x by its handle. In the sim the slide is held 8 mm above the plate (conservative stand-in for sliding, as the step-3 catch tray).
- **Bowl** Ø170 × **75 mm** (R11 radius, 15 mm lower than R11's 90 mm): lifted 8 mm at the grasp its rim must stay ≥ 5 mm under the spout (0.85 + 0.005 + 0.008 + H ≤ 0.945 → H ≤ 82 mm). Rim at 0.938 when lifted: 12 mm under the spout.
- **The R07 potato staging bowl must move** (as the R07 tomato bowl already did): the bowl's out position is its spot. A removed obstacle cannot create hits.
- **Handle, round 1** (step-3 strut + knob toward +x, the only side free of the slicer): **0/96** at the seat and slid +0.09…+0.29 m, pitches 0/15/30/45° (24 probes) [M]. Blockers: upper arm / forearm vs the upper cabinet and its door. The knob is 0.265 m behind the cabinet front.
- **Handle, round 2: cranked handle** (`kitchen19p4.dbh`): rim strut along +x to a post 0.17 m from the bowl axis (beside the slicer's right face when parked), post up to 1.10 m, bar forward to a keyed 30 mm knob at y **0.30**, facing the robot. Probes (seed 14, 96 starts) [M]:

  | Pose | good starts | best reserve |
  |---|---|---|
  | parked under the spout (8 mm) | 6 | 3.0 mm |
  | slid out 15 cm / 20 cm | 4 / 5 | 3.0 mm |
  | slid 20 cm, lifted 10 cm | 8 | 10.6 mm |
  | pitched 30° knob, same poses | 0–2 | — |

- **Screen** (`r19prep4_screen.py MODE=drawer`, guide + parked bowl with handle): 104 stored paths + the stir cycle, 116,618 + 8,428 states, **0 hits, ≥ 117 mm** (AABB lower bound; worst: carrot set approach, finger vs the knob) [M].

### 2.3 Option (a) set: not closed (12 smoke configurations, `results/r19/prep4/chain_drawer_*`)
- **Pour into the T2L pan** (`DTGT=T2L`): with the mouth 6 cm over the pan rim 0/96. At 12–18 cm the rolled pose is reachable (up to 34/96, reserve up to 103 mm), but the crank makes the roll a ~0.3 m swing about the knob: the knob (TCP) ends at y −0.35…−0.46 (out in the aisle) and the level → rolled path sweeps the bowl through the pan (s3: bowl floor vs pan) [M].
- **Pour into a counter prep bowl** (front spot (−0.86, 0.15) or plating spot 2): reachable [probe], e.g. front spot, yaw 0, −130°: 8 starts, 68 mm reserve [M].
- **Chains** (`DTGT=FS`, carts pinned after the free slide): the pick side follows slide → lift → out from under the cabinet (fs4, fs7, pc1, pc2). It fails:
  - on the carry from "out" to the pour (upper arm / shoulder vs gripper);
  - with RRT planned carries (pc1/pc2), at the 50 mm grasp retreat at the seat (upper arm vs wrist 2) and at the pour roll with cart −1.05 (forearm vs gripper).
- **Next design step:** a handle the arm can back off from without folding (the retreat runs straight toward the robot from y 0.30); e.g. a knob turned 30–45° toward +x, or the post further right. Then re-probe.

### 2.4 Option (b): chute on the spout: excluded by geometry (`r19prep4_probe.py MODE=chute`, `chute_geometry.json`) [M]
- Outlet bottom 0.95 m. Even a shallow 60 mm catch bowl (rim 0.91 m) leaves **40 mm of drop**.
- A forward or sideways chute from the spout to the nearest candidate spots needs runs of 0.29–0.42 m, i.e. **106–350 mm of drop at 20–40°**. The slope pieces need to slide is **[E], not sourced** (wet cut produce on printed PETG/PP; 20–40° tried, even 20° fails).
- There is also no free bowl spot in the open strip: the raw tray starts 7 cm right of the slicer, the counter ends 5 mm left of it.
- A chute would need the slicer raised by roughly 0.07–0.3 m, which moves the checked carrot chute-drop set. Not pursued. Option (c) (sink leg) waits for #11.

---

## 3. Cooking-time staging spot (`kitchen19p4.py` T2L, `ACT=stgwok | ct2p | p2t2l | ct2l | p2b`)

### 3.1 The staging pan and its cradle (design [E])
- Pan: cup-style envelope cylinder **r 70 × 85 mm (~1.2 L)**, keyed 30 mm block on a lug, **lug gap 40 mm** (the cups' 25 mm put the open fingertips 7.6 mm from the r 70 mm wall, under the 10 mm cart-geom gap; m2 approaches). Approach along the lug, jaws horizontal; pour = roll about the lug (a wrist-3 roll).
- Masses [E]: pan 0.22 kg + lug/block 0.02 + food 0.40 (one wok dish of cut vegetables; ~0.6 kg/L loose [E]).
- Cradle: 4 mm plate on a 30 × 30 mm bar from the mast, as the cups' T2 bracket. Pan bottom-centre at cart frame (−0.32, 0.05), bottom 0.93 m, inside the cups' T2L envelope. Pins under the pan locate it (not modelled). Cart parts → the checker wants 10 mm, so the pick is 12 mm up.

### 3.2 Reach [probe, seed 14]
- **Pick off T2L:** 8/96 (capped list; 31–40 ok starts) for all five cradle positions tried and at any cart (−0.90, −0.45, 0.17, 1.10–1.30); reserve 2.0 mm.
- **Pour at the cups' pose** (axis (0.83, 0.09), grip 1.38 m, cart 0.45): the pan (r 70) hit the hood front (y 0.15) → axis moved to y **0.07**. Even so, 0/96 at cart 0.45 (no converged IK).
- **Mirrored** (cart right of the wok, pan on the arm's left): cart 1.10–1.30, lug toward the robot: level 23–51, tipped ±135° 8–40 good starts [M]. This mirrors the cups' passing T2R set (cup right of the base, cart 0.45).

### 3.3 The cooking-time set `stgwok` [checked, smoke]
- Keyframes: pick 12 mm over the cradle → lifted 3 cm (**the only anchor**, followed through the whole set; `ANCH=lifted`) → up to 1.11 m → lane over the counter edge (cart frame (−0.36, 0.19, 1.26)) → over the wok (axis (0.83, 0.07), grip 1.38 m) → **tipped −135°**, 2 s → level → back the same way → set down. Cart **1.21** throughout.
- The wok-anchored version (`ANCH="over the wok"`, m6) gives the same 20.2 s.
- Swinging the pan in front of the base with the cart at 0.45 (the cups' T2L idea) failed in 7 smoke runs: upper arm vs the pan, cabinet door, hood.
- **Pour geometry [M]:** tipped, the lowest point of the pan mouth is at z 1.326 m, at (0.875, 0.073), 0.11 m from the wok axis. That is **~0.31 m above the wok rim plane and ~0.40 m above the wok bottom**. The high pour is forced by the plume rule (grip ≥ ~1.36 m, as R19 cups).
  - Not simulated: oil splash from a 0.3–0.4 m drop, and pieces sticking to the pan. A pan this tipped empties loose pieces [E].
  - A lower pour needs the heat off for the add, or a longer lug (as R19_CUPS §0.4).

### 3.4 Filling the pan
- **`ct2p` passes** (table §1): the step-3 catch-tray route with the pan standing on **plating spot 2** at prep time (cooker off). Carts −0.614 → 0.498 → −0.464; joins 23.2° and 3.1°.
- **`p2t2l` (pan from plating spot 2 onto T2L) is the missing link.**
  - The pan at plating spot 2 is only pickable with that spot on the arm's right: carts −0.15…−0.26 [M]; 0/96 at 0.45–0.49.
  - T2L is always 0.32 m left of the base, so the pan must cross 0.68 m in front of it. The meet shuffle hits the base plate.
  - The RRT planned carry (new in `r19prep4chain.py`, cart fixed −0.16/−0.19/−0.25): both sides follow, both approaches pass (5.0 / 9.2 mm), but no path in 100 s (4 runs). → lane 2.
- **Direct pours into the pan on the cart failed** for the same structural reason: the pan rides only 0.32 m from the base.
  - **Catch tray from the lever:**
    - The pick works only with the cart at about −1.2 (lever on the right), and the crossing self-collides: low, high (z 1.40–1.45 crossing waypoints), or by moving the cart under the held tray.
    - The left-side pick that step 3 used (cart −0.614) is blocked by the T2L cradle itself: the gripper body passes through it (screen §3.5; fixed-cart IK 0/96 with T2L present).
    - At cart −0.70 the seat, pull-out and lift solve one by one (15/14/16 starts), but the continuous 15 cm pull hits the cart mast in all 12 candidates. The pull cannot be shortened: the tray must clear the 130 mm blade plate (y 0.145–0.275).
  - **Prep bowl at plating spot 2 → pan:** the arm reaches into the cabinet door on the lift, or folds at the pour.
  - **Drawer bowl → pan:** see §2.3.

### 3.5 Screen of the T2L parts (`r19prep4_screen.py MODE=t2l`; cart parts, recomputed every state; exact GJK on the new pairs) [M]

| Paths | T2L cradle + pan | Cradle empty (pan not parked) |
|---|---|---|
| 6 adopted cooking chains (pot-zone spider re-plan) + 11 approaches | **≥ 78.1 mm**, 0 hits | — |
| 22 hub edges (PY=.15) | **≥ 58.6 mm**, 0 hits | — |
| stir cycle (8,428 states) | **≥ 195.6 mm** | — |
| 6 checked cup chains (held cup as a 0.20 m sphere) | **≥ 128.8 mm** | — |
| stored prep sets (exact, own scenes) | **hit** (gate −10 mm, contact): carrot full/r2, tomato full/r2, catch tray full/cq1, carrot-into-basket bc1/full (approach), and `ct2p` | **hit**: the same sets except tomato play (approaches still hit) |
| prep sets not hit | soak ≥ 30 mm; tub fill / empty, basket wash, press ≥ 94 mm; carrot-into-basket full play 6.5 mm (its approach hits) | — |

- The hits are real arm-vs-cart-part proximities: wrist 2, forearm or gripper body low on the arm's left during the tray pick, tomato pick, catch-tray pull and carrot drop.
- So a T2L rack must be off the cart, or folded away, during those prep sets, or those sets must be re-planned with it present.
- The same applies to the cups' T2L caddy (larger envelope, never screened against prep sets).

### 3.6 Basket as the staging container (coordinator's suggestion, not modelled)
- Considered, not simulated.
- One point in its favour: the step-3 basket is picked with the tub on the arm's **left** (anchor carts −0.47 / −0.44, tub at x −0.84), the same side as T2L. A basket → T2L placement would therefore not need the right-to-left crossing that blocks plating spot 2 → T2L.
- Against it:
  - a Ø200 basket on a T2L cradle is bigger than the pan, so the prep-set conflict of §3.5 gets worse;
  - its cooking-time pour would be the mirrored `stgwok` motion with an end-on knob, which is unchecked.

---

## 4. Methods and evidence notes
- **New runner** `r19prep4chain.py`: a copy of `r19prepchain.py`; the original and `r19prep3_actions.py` are unchanged (md5 before = after). Additions, all stricter or additive:
  - the step-4 layer;
  - the R15 plume rule as a hard check in follows, shuffles, joins and candidates (the cups' rule, held step-3/4 objects skipped);
  - the cups' food join rule (≤ 5 cm / 15°; planned paths ≤ 15° tilt);
  - grasps of cart-parked objects;
  - fixed carts per keyframe;
  - the RRT "planned carry" between two meet keyframes (cart fixed, `planner.plan`, edges ≤ 4 mm).
  - **Regression [M]:** the stored step-3 soak set re-run through the copy (`chain_soak_regress_so1`) reproduces `chain_soak_so1` exactly: 105 states, max |Δq| = 0.0, loads and approaches identical.
- **New verifier** `r19prep4_verify.py`: a copy of `r19prep_verify.py` (unchanged). It adds the step-4 layer, cart-parked grasps, the plume rule on every re-checked state, and optionally the pot-zone layer (`RACK= SPX= SPY=` → `*_verify4mm_pot.json`).
- **MuJoCo gap readings [M].** The gate checks were not affected; the evidence:
  - For a 16-gon prism 4/8/9 mm over a counter box, MuJoCo contacts read exactly 4.0/8.0/9.0 mm at three positions.
  - `mj_geomDistance` (distmax 0.05) read **−170…−208 mm** for the same true +9 mm gap whenever the prism was over the box's back half.
  - The checker uses contacts plus its own GJK, not `mj_geomDistance`. The plume helper (`kitchen19seas` / `r19stir` style) does use it; I only saw negative misreads (false alarms), but have not proven that in general.
- The step-3 out-bowl probe blockers ("held bowl vs counter_left") did not reappear with the 75 mm bowl at 13 mm over the counter.
- **Superseded:** runs before `stgwok_m3`, and the `stg_*`/`stgwok_*`/`ct2_*` probes, used the 25 mm lug. The passing m5 and all verifications use the 40 mm lug.
- `screen_t2l_INVALID_stock_ur5e.json` was run without `ARM=` (stock capsules). Kept only for the record; do not use it.

---

## 5. Step 4 of the audit (tool drawer, plate swap, finger swap): plan only
No probes were run (time went into §2–3). Plan, in the step-3 method:
1. **Where:** the left column is now slicer + drawer, the work spot is the lever/cold box, and T2L must stay clear of the low left during prep. Candidate homes:
   - (i) an under-counter push-to-open drawer front below the work spot (front z 0.70–0.80 m);
   - (ii) a printed wall rack under the upper cabinet behind the tray (y ≥ 0.40, z 1.0–1.1; R14 found reach there up to z 1.05–1.12);
   - (iii) a cart-mounted rack. Screen it against the prep sets first: §3.5 shows the low-left cart region is used.
2. **Reach probes** (`r19prep4_probe.py` pattern, 96 starts):
   - drawer handle pull, fully open, at two heights;
   - lever-plate dock pick/place (keyed handles; the AY-403 plate is ~0.25 kg [E]);
   - pusher dock;
   - finger-rack pose for the R13 dovetail (the gripper presented to the rack, not a held object).
3. **Sets:**
   - TOOL_FETCH/RETURN (9 uses): drawer open → lever base out → work spot;
   - LEVER_PLATE_SWAP (7): the plate lifted off its pins, 8 mm seat windows;
   - FINGER_SWAP (15): approach, release pin, retreat; the pin release needs a physics run (`dyn.py`).
4. **Screens:** against the 6 chains, the hub edges, the stir and the prep sets, with `r19prep4_screen.py` (add a MODE for each fixture).

---

## 6. Controller lanes (each > 5 min)
```bash
cd /c/Users/admin/Documents/YJGames/robot_rail/sim/r10/claude
PY=C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe
A="ARM=ur5e_enc2_pgc"; P="RACK=keyed SPX=1.56 SPY=.20"
# lane 1 (~10-25 min): full settings of the two passing sets, then the <= 4 mm re-check (plume, pot-zone layout)
$PY r19prep4chain.py ACT=stgwok C0=1.21 POURC=1.21 "SW=-.32,.05,1.11,0" SLANE=-.36,.19,1.26 TIP=-135 ANCH=lifted SEEDS=3 TRIES=12 KEEP=1 TAG=full $A
$PY r19prep4_verify.py FILE=results/r19/prep4/chain_stgwok_full_ur5e_enc2_pgc.json NPROC=16 $P
$PY r19prep4chain.py ACT=ct2p PLUME=0 SEEDS=3 TRIES=12 KEEP=4 TAG=full $A
$PY r19prep4_verify.py FILE=results/r19/prep4/chain_ct2p_full_ur5e_enc2_pgc.json NPROC=16 $P
#  (if a full run picks a failing candidate, the smoke settings reproduce the passes: stgwok SEEDS=1 TRIES=8 KEEP=1; ct2p SEEDS=1 TRIES=8 KEEP=2)
# lane 2 (~20-60 min each): the missing link plating spot 2 -> T2L, RRT planned carry with a 600 s budget
for C in -.19 -.16 -.25; do $PY r19prep4chain.py ACT=p2t2l PCARRY=1 CB=$C PLUME=0 SEEDS=2 TRIES=8 KEEP=2 PLAN_N=4 PLAN_S=600 TAG=plan$C $A; done
#  for each file with "ok": true:  $PY r19prep4_verify.py FILE=results/r19/prep4/chain_p2t2l_plan<C>_ur5e_enc2_pgc.json NPROC=16 $P
# lane 3 (exploration, ~20-40 min; expected to fail at the seat retreat until the handle changes, sec. 2.3)
$PY r19prep4chain.py ACT=drawer DTGT=FS MOUTHZ=.14 DPC=1 DYAW=90 DEG=-130 SLC=-1.28 LIFTC=-1.20 OUTC=-1.05 DOUT=-1.45,.33,1.03 PLUME=0 SEEDS=2 TRIES=10 KEEP=3 PLAN_N=4 PLAN_S=300 TAG=plan $A
# lane 4 (~2-6 min each): re-run the screens after the step-3 full runs settle (they read results/r19/prep/chain_*_full_*)
$PY r19prep4_screen.py MODE=t2l WORKERS=16 $A PY=.15
$PY r19prep4_screen.py MODE=t2l EMPTY=1 KINDS=prep WORKERS=16 $A PY=.15
$PY r19prep4_screen.py MODE=drawer WORKERS=16 $A PY=.15
```

---

## 7. Files
**New code**
- `kitchen19p4.py`: the layer. Drawer guide, 75 mm drawer bowl, cranked-handle variants (`dbh`), staging pan (`stg`, `stg_p*`), T2L cradle as cart geoms, mesh rule. A no-op without `cfg['r19p4']`.
- `r19prep4_actions.py`: keyframes of `drawer`, `ct2l`, `stgwok`, `p2b`, `ct2p`, `p2t2l`.
- `r19prep4chain.py`: copy of `r19prepchain.py` with the step-4 additions (§4).
- `r19prep4_verify.py`: copy of `r19prep_verify.py` with the step-4 additions.
- `r19prep4_probe.py`: reach probes and the option (b) chute geometry (`MODE=chute`).
- `r19prep4_screen.py`: new-part screens; imports `r19pot_screen.py` helpers, which are unchanged.

**Results** (`results/r19/prep4/`)
- Passing chains with re-checks:
  - `chain_stgwok_m5_ur5e_enc2_pgc.json` + `_verify4mm.json` + `_verify4mm_pot.json` (also `m6`);
  - `chain_ct2p_s1_ur5e_enc2_pgc.json` + `_verify4mm.json` + `_verify4mm_pot.json`.
- Regression: `chain_soak_regress_so1_ur5e_enc2_pgc.json`.
- Screens: `screen_t2l.json`, `screen_t2l_empty.json`, `screen_t2l_stir.json`, `screen_drawer.json`, `screen_drawer_stir.json`.
- Chute geometry: `chute_geometry.json`.
- Failed smoke runs kept for the record: `chain_{ct2l,p2b,p2t2l,drawer,stgwok}_*` (one tray run, `ct2l_s3`, was cut by its 295 s limit and left no file).
- 429 `probe_*.json`; logs in `logs/`.

**Changed:** nothing outside these new files. `r19prepchain.py`, `r19prep_verify.py`, `r19prep3_actions.py`, `kitchen19p3.py`, `kitchen19.py`, `kitchen19pot.py`, `kitchen19seas.py`, `r19pot_screen.py` and `r19cupchain.py` all have the same md5 as before.
