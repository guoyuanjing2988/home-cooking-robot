# R19 #36: the PGC-140 cable outlet and cable in the gripper model (Windows, 2026-10-13)

Checking standard: the pot-zone layer (`RACK=keyed SPX=1.56 SPY=.20`, `PY=.15`), gates 10 / 5 mm, states ≤ 4 mm, the
unchanged checker, contact windows only as declared (the lid rack window; the prep food windows). Nothing was loosened.
Labels: **[M]** measured in the sim, **[E]** estimate, **[S]** sourced (URL in §1). No git, no GitHub writes.

## 0. Answer first

1. **What DH's gripper really has [S].** There is no M8 / M12 socket on the body. A fixed pigtail leaves the round base
   radially, in the jaw plane, under one jaw, through a strain-relief boot that sticks out 12 mm. The cable is Ø6.4 mm,
   200 mm long, with an allowable bending radius of R50 mm, and ends in an M12 8-pin plug. The current DH drawing
   asks for 100 mm of free space beside the body ("Secure at least 100mm"; the old v2.1 manual said 30).
2. **Model.** `r19cable.py` puts the boot, the R50 bend and a 20 mm run of cable on the gripper body as convex enclosing
   hulls. The exit height (21.1 mm measured off two DH drawings, not dimensioned) is covered by a 19–25 mm band [E].
   Arm options:
   - `ur5e_enc2_pgcc`: the conservative default. The outlet is on **both** jaw sides, because which jaw it sits under
     is a mounting choice, and the cable bends down as in DH's drawing.
   - `ur5e_enc2_pgcc_<routing>`: a single routing.
   - `fr5_j6_pgc_sp20c[_<routing>]`: the same for the FR5 candidate.

   Every existing option is byte-identical in behaviour: compiled XML md5, geom count, full-check results and
   envelope file are the same for all 12 earlier options in 2 scenes [M].
3. **The conservative default fails.** The cable meets the wrist-1 link (a self pair) in the lever, wok, plate 2, lid,
   spider, hub and prep sets. Only the spatula and the stir pass.
4. **One routing clears everything: `yp_a-45`.**
   - The gripper is mounted with its outlet under the **+y jaw** (the `R_finger_plus` side of the tool frame).
   - After the boot, the cable is bent at **R50, 45° between "down toward the gripper's mounting face" and "away from
     the robot-flange side"** (tool direction (−x −z)/√2).
   - The first tie is **20 mm after the bend**.

   With `ARM=ur5e_enc2_pgcc_yp_a-45` and the full unchanged checker, **every set passes with 0 hit states**: the 6
   adopted chains, the stir library entry, the 22 current hub edges and the 3 prep sets (§4). The FR5 `sp20` sets
   that exist in this layer pass too.
5. **The gripper's and wrist's reserves do not change with the cable** (§4.1).
   - **Cable vs environment:** the smallest reserve is 34.5 mm past the 5 mm gripper gate on the UR5e (39.5 mm real
     gap), so it would also pass the 10 mm arm gate.
   - **Cable vs the robot (self):** the smallest reserve is 3.9 mm (hub), 4.9 mm (lid) and 6.1 mm (spider).
6. **What the routing needs and what is not yet modelled.**
   - **The tie is required.** The cable must be held tight at the bend and tied within 20 mm. DH's loose 100 mm
     free zone does not fit: it fails the wok, plate 2 and lid on both sides.
   - **Not modelled:** the rest of the pigtail (≈96 mm), the M12 plug junction, and the dress back to the arm
     (to the UR tool connector, or along the arm with a J6 service loop) (§6).

## 1. Dimensions and sources

Sources. DH's current drawings are B and C; D is the DH catalogue on a secondary host; A is the old manual that issue
#36 was based on. A research subagent read them; DH's own HTML/PDF pages were read, and no CAD file was downloaded.
- A: PGC-140 Short Manual v2.1 (2021) — https://uploads.unchainedrobotics.de/media/file_upload/PGC-140-Short-Manual_v2.1_e46a3c6b.pdf
- B: PGC parameter sheet CN.2405, p.6 "技术尺寸图" — https://www.dh-robotics.com/wp-content/uploads/2023/11/PGC系列_参数页_CN.2405.pdf
- C: DH Electric Gripper Brochure 2024, PGC-140-50 page (PDF p.17) — https://en.dh-robotics.com/wp-content/uploads/2024/07/DH_Electric-Gripper-Brochure.pdf
- D: DH catalogue excerpt (Neobotix host), p.3 — https://www.neobotix-robots.com/fileadmin/user_upload/PGC-Gripper_Datasheet.pdf
- E: PGC Series Short Manual v2.3, Fig 2.1 — https://en.dh-robotics.com/wp-content/uploads/2022/12/PGC-Series-Short-Manual-v2.3_DH-Robotics.pdf
- Vendor connector sheets, used only as fallbacks: Lumberg RKT 8-282 (M12 8-pin straight female),
  https://catalog.belden.com/techdata/EN/RKT8-282_techdata.pdf ; RKWT 8-282 (right-angle),
  https://catalog.belden.com/techdata/EN/RKWT8-282_techdata.pdf

| Quantity | Value | Label |
|---|---|---|
| Connector on the body | none: a fixed pigtail through a strain-relief boot; only a side outlet ("S Side") is offered, no right-angle or through-flange version | [S] B, C |
| Exit direction / side | radial, horizontal, in the jaw plane, under one jaw (90° from the flats with the rail pins) | [S] A Fig 1.3, B/C drawings, C photo |
| Exit height (cable axis above the gripper's bottom face) | 21.1 mm on two DH drawings, 22–24 mm on a photo; not dimensioned. **Modelled: band 19–25 mm** | [E] measured off B and A |
| Boot protrusion from the body | 12 mm | [S] B/C ("12") |
| Boot diameter | ≈11.7–15.8 mm; **modelled Ø16** | [E] measured off B |
| Cable | Ø6.4 mm, 200 mm from the boot tip to the plug | [S] B/C |
| Bending radius | R50 mm, one value, no static / dynamic split. **Modelled as the inside radius: centreline 53.2 mm** (the reading that reaches further out) | [S] B, C, D; reading [E] |
| Free space beside the body | "Secure at least 100mm" (old A: "at least 30") | [S] B, C, D |
| Plug at the pigtail end | M12 8-pin (A-coded), M12×1, max Ø15, ≈47 mm long; probably male | [S] B/C, A §1.6; length and gender [E] |
| Mating M12 straight / right-angle socket (fallback) | 43 mm long, Ø14.5 / 26.6 mm to the mating face, 31 mm axis to overmould end, Ø14.5 | [S] Lumberg sheets |
| UR integration | DH sells a "Robot Cable" option (code 01: UR CB / UR e). Its connector and length are not published. The old manual shows the pigtail ending in a right-angle M8 into the robot wrist ("customizable") | [S] C, A p.6–7 |

CAD that would settle the exit height and the boot shape. Not downloaded; ask the user:
- `PGC-140-50_2D3D-Model.zip`, https://www.dh-robotics.com/wp-content/uploads/2023/10/PGC-140-50_2D3D-Model.zip (its 2D drawing should give the exit height);
- `PGC-140-50-W-S_简易模型_v4.0_20240814.step`, https://en.dh-robotics.com/wp-content/uploads/2023/10/PGC-140-50-W-S_简易模型_v4.0_20240814.step (a "simplified model": the cable may be missing).

"Right-angle vs straight" therefore does not apply at the body: the boot is straight and fixed. It applies only to the
M12 junction at the far end of the pigtail, which is beyond the modelled part (§6).

## 2. The model (`r19cable.py`, arm options in `arms.py`)

- **Frame.** The PGC drawing housing (`scene.oem_pgc_drawing`): tool x = gripper axis, y = jaw stroke; the gripper's
  bottom face is at x0 = −0.1735 m. The cable geoms take the housing's finger-design shift, so they sit on the housing
  in every finger design.
- **Shapes.** Each side gets convex MuJoCo mesh hulls; every circle is a polygon circumscribed about the true circle:
  - **boot:** Ø16, from 3 mm inside the body surface to 12 mm outside it;
  - **bend:** the Ø6.4 cable turning at a centreline radius of 53.2 mm, as 3 arcs of 30°, each the hull of
    cross-sections every 5° (inflated by the outer-fibre sagitta);
  - **run:** 20 mm of straight cable [E].

  Every piece is the hull over the 19–25 mm exit-height band.
- **Routings** (`ROUTINGS`), named `<side>_<dress>[_r0]`:
  - side `yp` / `ym`: the outlet under the +y / −y jaw;
  - dress `dn`: down toward the mounting face (DH's drawing);
  - dress `fl`: toward the robot-flange side (+z);
  - dress `a<deg>`: in between (negative = away from the flange side);
  - `_r0`: no straight run (the tie right at the end of the bend);
  - `k100`: DH's whole 100 mm free zone on that side;
  - `both_dn`: the default.
- **Size (`yp_a-45`).** At most 80.6 mm out from the body surface, 35 mm below to 33 mm above the bottom face [M].
  Its radial reach about the J6 axis is 174.7 mm, against 111.3 mm for the housing [M].
- **Checker categories.** The geoms are on `R_tool`, so the checker gives them the 5 mm gripper gate and 0 mm self.
  They are named `R_pgc_cable*`, so no grasp or food window of chain.py / r19prepchain.py / r19prep_verify.py
  (`R_finger_*` / `R_gripper_*` vs the food) ever exempts them.
- **Default unchanged.** `r19cable_md5.py` builds two scenes for each of the 12 earlier options, once with
  `arms.py.bak_r19cable` and once with the new file. XML md5, geom count, a full check and the envelope file are
  identical: 24 / 24 [M]. The diff of `arms.py` is 7 added lines (the options) and 1 line in `swap()`.

## 3. Static checks (`r19cable_static.py` → `results/r19/cable/static.json`)

These pairs are fixed relative poses, or are not checked by the checker. Values in mm [M].

| Option | Cable vs wrist 3 (adjacent, unchecked) | vs fingers | vs held objects (5 chains) | vs wrist 2, whole J6 turn | Share of the J5 × J6 grid where the cable meets wrist 1 (housing alone) |
|---|---|---|---|---|---|
| `ur5e_enc2_pgcc` (both, dn) | 28.4 | 68 | ≥ 146 | ≥ 33.8 | 31.3 % (22.3 %) |
| `yp_dn` / `ym_dn` | 28.4 / 30.0 | 68 | ≥ 146 | ≥ 33.8 | 15.7 / 15.6 % |
| **`yp_a-45`** | **28.4** | **68** | **≥ 146** | **≥ 33.8** | **5.2 %** |
| `ym_fl_r0` / `ym_a-45_r0` | 30.0 | 68 | ≥ 146 | ≥ 33.9 | 10.1 / 5.2 % |
| `k100` (either side) | 26.4–27.7 | 68 | ≥ 146 | ≥ 24.2 | 26.8 % |

Notes:
- The sweep columns use MuJoCo's convex distance. They are a map of the postures a routing forbids, not a certificate.
- Wrist 1 is the binding link for the cable, as it was for the housing (#12).

## 4. Re-check results

**Method.** `r19cable_check.py` builds the same scenes and states as the existing tools, unchanged:
- chains: `r19pot_check` (keyed rack and its window);
- hub: `r19hub.union_tree` with the pot layer, as `r19pot_hub`;
- stir: `r19stir_cycle.model(-1)` with its plume rule;
- prep: `r19prep_verify` (scenes, unwrap, densify).

States are cut to ≤ 4 mm with the checked model's point bound. Every state goes through `Checker.check(full=True)`.

**Routing screens.** `ARM=..._ALL` / `_SEL` carry several routings at once, each its own geom group.
- A routing fails a state if its pairs fail the checker's rules: the bound reserve, the MuJoCo-contact rule, or (stir)
  the plume rule.
- `CABLEONLY=1` evaluates only those pairs; every other pair is the one already certified.
- On the lid, the screen gave exactly the same per-routing hit counts as the full check [M].

The certificates are runs of one routing with no `CABLEONLY`.

### 4.1 Certificate: `ARM=ur5e_enc2_pgcc_yp_a-45` (full checker; reserve = lower bound − gate, mm) [M]

| Set | States | Hits | Min env reserve / self (all pairs) | Gripper (housing, palm, fingers) env / self | Wrist 1–3 env / self | **Cable env / self** |
|---|---|---|---|---|---|---|
| wok (py.15) + 2 approaches | 4,696 | 0 | 2.02 / 1.87 | 7.6 / 1.87 | 11.3 / 1.87 | **34.7 / 42.8** |
| plate 2 (py.15) | 4,669 | 0 | 2.02 / 1.87 | 7.6 / 1.87 | 11.3 / 1.87 | **34.7 / 42.8** |
| lever | 166 | 0 | 2.67 / 2.00 | 15.2 / 15.4 | 40.2 / 13.7 | **79.1 / 75.4** |
| lid (keyed rack; 113 window states) | 2,631 | 0 | 2.02 / 1.11 | 14.6 / 1.11 | 32.8 / 1.11 | **134.9 / 4.92** |
| spatula | 2,810 | 0 | 2.04 / 2.00 | 27.0 / 14.1 | 139.8 / 6.26 | **173.9 / 32.0** |
| spider (1.56, 0.20) | 4,206 | 0 | 2.08 / 0.78 | 20.0 / 0.78 | 95.4 / 1.01 | **127.1 / 6.13** |
| stir library entry (10 segments; plume 25.8) | 4,811 | 0 | 2.00 / 2.00 | 150.6 / 19.9 | 215.5 / 5.16 | **322.8 / 35.8**, plume 195.6 |
| hub, 22 edges (`results/r19/pot/hub_final_1.56_.20/`) | 34,288 | 0 | 2.03 / 1.28 | 17.0 / 1.28 | 4.3 / 1.28 | **38.0 / 3.89** |
| prep carrot | 4,209 | 0 | 2.00 / 2.00 | 4.5 / 5.55 | 30.3 / 5.62 | **34.5 / 7.07** |
| prep press | 227 | 0 | 1.00 / 2.85 | 3.6 / 32.1 | 50.8 / 18.0 | **120.0 / 55.3** |
| prep tomato | 2,810 | 0 | 1.00 / 1.44 | 1.0 / 1.44 | 30.2 / 1.44 | **62.0 / 7.79** |

How to read the table:
- **Reserves without the cable are unchanged.** The non-cable reserves equal the certificates without the cable: wok
  2.016 / 1.87 (measured here with `ur5e_enc2_pgc` on the same states), lid 1.11, spider 0.78, prep as their
  `_verify4mm.json`.
- **The cable is never the binding pair.**
- **Hub folder.** The 22 hub edges are the pot-zone hub after controller lane 1: 20 edges are identical to
  `hub_py.15_ur5e_enc2_pgc`, and the two SPIDER edges are new.
- **Not re-run:** `r19stir_report.py`. It writes the shared `results/r19/stir/summary.json`, and its time-law and
  kinematics outputs do not depend on collision geometry. The stir entry's certified states were re-checked directly
  instead.

### 4.2 Routing screens: which routing clears what (hit states; cable env / self reserve, mm) [M]

| Set | `yp_dn` | `ym_dn` | `yp_fl` | `yp_fl_r0` | **`yp_a-45`** | `yp_a-45_r0` | `ym_fl_r0` | `ym_a-45_r0` |
|---|---|---|---|---|---|---|---|---|
| wok | ok 31.5/24.6 | **844** | **78** (hood −3.2) | ok 16.8 | **ok 34.7/29.1** | ok | ok | ok |
| plate 2 | ok | **844** | **78** | ok | **ok** | ok | ok | ok |
| lever | ok | **30** | ok | ok | **ok 79.1/75.4** | ok | ok | ok |
| lid | **498** | **560** | ok | ok | **ok** | ok | ok | ok |
| spatula | ok | ok | **315** | **70** | **ok** | ok | ok | ok |
| spider | **1,449** | **1,059** | **160** | ok | **ok** | ok | ok | ok |
| stir | ok | ok | **804** | ok | **ok** | ok | ok | ok |
| hub (22 edges) | **1,548** | **503** | **1,497** | **20** | **ok 38.0** | ok | ok | ok (4.7) |
| prep (3 sets) | **467** | **42** | **583** | ok | **ok 34.5** | ok | ok (9.9) | **94** |

Notes:
- **Failing pairs.** Self failures are the cable vs the wrist-1 link (`R_geom_enc2_w1_*`). The environment failures
  are:
  - the `yp_fl` run vs the hood (wok, plate 2: −3.2 mm);
  - `yp_fl_r0` on the hub edge WOK__H_POT (−5.0);
  - `ym_dn` and `ym_a-45_r0` in the tomato prep set (−4.4 / −5.0).
- **Routings that pass everything:** `yp_a-45`, `yp_a-45_r0` and `ym_fl_r0`. `yp_a-45` is recommended: it keeps the
  20 mm run in the model, so it is the more conservative one, and it has the largest cable margins.
- **The default `ur5e_enc2_pgcc` (`both_dn`) fails.** It fails wherever `yp_dn` or `ym_dn` fails. The full checker
  confirms this:
  - lever: 11 play + 19 approach states;
  - lid: 1,018 + 36 + 4 states;
  - every hit is the cable vs `R_geom_enc2_w1_1`.
- **DH's whole 100 mm zone (`k100`) fails** the wok and plate 2 (−5 mm vs the hood), the lid (both sides) and the lever
  (−y). The cable must be tied tight; it cannot be left loose in the zone.

### 4.3 FR5 candidate `fr5_j6_pgc_sp20c` (cheap part done) [M]

The screens give the same picture as the UR5e. `yp_a-45` clears every set, and its full-checker certificates pass
with 0 hit states:

| Set | States | Cable env / self |
|---|---|---|
| lid (keyed rack, spider at 1.56, 0.20; 136 window states) | 2,576 | 134.9 / 11.7 |
| lever | 178 | 79.1 / 82.2 |
| spatula | 2,487 | 171.7 / 63.6 |
| wok (py.17) | 4,819 | 20.2 / 47.1 |
| plate 2 (py.17) | 4,799 | 20.2 / 47.1 |
| stir (plume: cable 195.6) | 4,237 | 322.7 / 57.1 |

There is no FR5 `sp20` spider at the new rest: controller lane 4 failed to plan it, so it is not checked.

## 5. Decisions needed

1. **Adopt the routing `yp_a-45` as part of the checking standard (`ARM=ur5e_enc2_pgcc_yp_a-45`):**
   - mount the gripper with its outlet under the +y jaw;
   - bend the cable at R50, down and 45° away from the robot-flange side;
   - tie it within 20 mm of the bend.

   The alternatives are `ym_fl_r0` (the other jaw side, bent toward the flange side, tied right at the bend) and
   `yp_a-45_r0`.
2. **Choose how the cable reaches the robot** (needed for the next modelling step):
   - DH's "Robot Cable 01" into the UR tool connector on wrist 3, which stays rigid with the gripper;
   - or the 5 m M12 extension dressed along the arm, which needs a J6 service loop.

## 6. Limits

- **Exit height and boot shape** are scaled off DH drawings, not dimensioned, and covered by the 19–25 mm band. The
  CAD in §1 would settle them.
- **Not modelled beyond the first tie:**
  - the remaining pigtail, about 200 − 12 − 83.6 (bend arc) − 20 ≈ 96 mm [E];
  - the M12 plug (Ø15 × ≈47 mm [E]) and its mating socket;
  - the dress to the arm.

  With `yp_a-45` the cable leaves toward the outside of the wrist. Bringing it back to the arm needs another R ≥ 50
  turn, which is not checked.
- **Adapter.** The adapter bracket between the UR flange and the gripper is not modelled (inherited, as before).
- **Gate.** The checker gives the cable the 5 mm gripper gate (it is on `R_tool`). Its smallest environment reserve
  with `yp_a-45` is 34.5 mm past that (UR5e) and 20.2 mm (FR5), so the 10 mm arm gate holds too.
- **Tolerance tools (#13).** `r19tol_core.py` marks every `R_tool` geom except the palm and `R_gripper_oem*` as
  held, so `R_pgc_cable*` would count as held there. It needs a one-line exclusion before #13 runs with a `*_pgcc`
  option. That is a shared file; it was not changed.
- **FR5 static sweeps.** The radial-reach column of `static.json` assumes the UR wrist-3 frame; ignore it for the FR5.

## 7. Controller lanes (optional; every command < 5 min, est. per line)

Everything asked in #36 was run here. Options:

```bash
cd /c/Users/admin/Documents/YJGames/robot_rail/sim/r10/claude
PY=C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe
L="RACK=keyed SPX=1.56 SPY=.20 PY=.15"
# lane A (only if an alternative routing is preferred): certificates for it, e.g. R=ym_fl_r0 (or yp_a-45_r0); ~1.5 / 1.5 / 2.5 / 1.5 / 2.5 / 2.5 / 1.5 / 2.5 min
R=ym_fl_r0; A=ur5e_enc2_pgcc_$R
$PY r19cable_check.py chains FILES=results/r17/chain_wok_s-1_final_py.15_ur5e_enc2_pgc.json $L ARM=$A WORKERS=30
$PY r19cable_check.py chains FILES=results/r17/chain_wok_s-1_r18plate2b_py.15_ur5e_enc2_pgc.json,results/r17/chain_lever_s+1_final_ur5e_enc2_pgc.json $L ARM=$A WORKERS=30
$PY r19cable_check.py chains FILES=results/r17/chain_lid_s-1_final_ur5e_enc2_pgc.json,results/r17/chain_spatula_s-1_r18roll-1.15_.30_ur5e_enc2_pgc.json,results/r19/pot/chain_spider_s+1_pot_1.56_.20_ur5e_enc2_pgc.json $L ARM=$A WORKERS=30
for P in work return; do $PY r19cable_check.py stir LIB=results/r19/stir/lib_stir_cycle_ur5e_enc2_pgc.json PARTS=$P ARM=$A WORKERS=30; done
D=results/r19/pot/hub_final_1.56_.20; H="DIR=$D POT=1 $L ARM=$A WORKERS=30"
$PY r19cable_check.py hub EDGES=LEV_O__WOK,SPAT__LEV_C,LID_RACK__H_WOK,SPIDER__H_WOK,LID_RACK__H_POT,SPIDER__H_POT,LID_POT__H_WOK $H TAG=hubpot_a
$PY r19cable_check.py hub EDGES=LID_POT__H_POT,LEV_C__H_WOK,LEV_C__H_SPAT,LEV_O__H_WOK,LEV_O__H_SPAT,LEV_C__H_SINK,LEV_O__H_SINK $H TAG=hubpot_b
$PY r19cable_check.py hub EDGES=SPAT__H_SINK,SPAT__H_SPAT,WOK__H_POT,WOK__H_SINK,WOK__H_WOK,H_SINK__H_WOK,H_SPAT__H_SINK,H_WOK__H_POT $H TAG=hubpot_c
for f in carrot press tomato; do $PY r19cable_check.py prep FILE=results/r19/prep/chain_${f}_full_ur5e_enc2_pgc.json ARM=$A WORKERS=30; done
# lane B (not asked in #36): the step-3 prep sets with the recommended routing, ~1 min each
for f in bascarrot_bc1 basket_y20p30 ctray_cq1 soak_so1 tubempty_ex2 tubfill_t15fin; do $PY r19cable_check.py prep FILE=results/r19/prep/chain_${f}_ur5e_enc2_pgc.json ARM=ur5e_enc2_pgcc_yp_a-45 WORKERS=30; done
# tables: python r19cable_table.py PAT='*/*__ur5e_enc2_pgcc_yp_a-45.json'
```

If a prep set or a chain is re-planned (the #4 jobs), re-run its line with the recommended routing; each takes < 2 min.

## 8. Files

- **New code:**
  - `r19cable.py`: the shapes, routings and screening sets;
  - `r19cable_check.py`: the chains / hub / stir / prep re-check, routing groups and `CABLEONLY` screens;
  - `r19cable_static.py`: the static and sweep checks;
  - `r19cable_md5.py`: the default-unchanged check;
  - `r19cable_table.py`: the tables.
- **New results:** `results/r19/cable/`
  - `chains/`, `hub/`, `stir/`, `prep/`: `<set>__<arm>[_cableonly].json`, with per-state reserves;
  - `static.json`, `md5_old.json`, `md5_new.json`;
  - `log_*.txt`.
- **Changed:** `arms.py` (backup `arms.py.bak_r19cable`): the `*_pgcc*` / `fr5_j6_pgc_sp20c*` options, and one line in
  `swap()` that adds the cable shapes.
- No other shared file was changed. No other job's results were written.
