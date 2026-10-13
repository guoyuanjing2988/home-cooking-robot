# R19 #36, part 2: the PGC-140 cable measured from DH's CAD, the run to the tool connector, and the tolerance fix (Windows, 2026-10-14)

Checking standard, as in R19_CABLE.md: the pot-zone layer (`RACK=keyed SPX=1.56 SPY=.20`, `PY=.15`), gates 10 mm robot↔environment and 5 mm gripper/held/cable↔environment, 0 mm self, states ≤ 4 mm apart, the unchanged checker. Nothing was loosened.
Labels: **[M]** measured (sim or CAD), **[E]** estimate, **[S]** sourced (file or URL). No git, no GitHub writes, no supplier contact.

## 0. Answer first

1. **The exit is where the model already assumed it [S, DH STEP v4.0].**
   - The cable axis is **21.00 mm** above the mounting face, exactly in the jaw plane (0.00 mm off), and radial under one jaw.
   - The boot is **Ø15.5** at its collar and sticks out **10.5 mm** past the Ø75 body.
   - The pigtail is **153.0 mm** of Ø6.4 cable plus a **47.0 mm** M12 plug (Ø16.2), 200.0 mm in all.
   - All of this lies inside the modelled 19–25 mm band, Ø16 boot and 12 mm boot length, so **the cable geometry is unchanged.** Only the source labels were updated.
   - All **72 arm options that existed before this round build byte-identical scenes (90 of 90)**.
2. **The standard flange is already in the model, but the gripper pose has a bigger problem.**
   - DH's flange is a Ø75 × 5.0 mm plate with a Ø31.5 × 2.5 spigot and two 14.9 mm ears that sit inside the gripper's outline.
   - The gripper STEP contains this same flange: its bottom face *is* the flange's robot face. DH's 98 / 138.5 mm heights, and therefore `X0` in `arms.py`, already include it.
   - **However, the modelled tool pose puts the housing 16.9 mm inside wrist 3 on the UR5e** (16.3 mm on the FR5 `sp20`) [M]. That is an adjacent pair the checker never sees.
   - The pose is the inherited "26.6° angled adapter": the gripper axis is 26.6° off J6, and the bottom face is 45 mm behind the flange plane and 78 mm off axis. Even just to touch wrist 3, the gripper would have to move about 41 mm further out along the flange axis.
   - **This needs a decision (§8).** It is outside #36, and changing it would invalidate every certificate.
3. **Tool connectors.**
   - **UR5e:** M8 8-pin (Lumberg RKMW 8-354). It is male before 1 Sep 2024 and female after. Its axis is radial, on the dowel-hole line, **31.55 mm** behind the flange face [S].
   - **FR5:** it has two flush end connectors 21 mm behind the flange [M, vendor STL]: an **RS485 5-pin** at −90° and an **M12 8-pin I/O** at 180°. The I/O connector has no RS485, and its type, size and position are not published [S].
   - **DH:** no robot-specific cable code or length is published for UR or Fairino. DH says an **M8 outlet can be customised on request** [S].
4. **The run with DH's M12 junction does not fit (`yp_a-45_tc`).**
   - After the adopted `yp_a-45` dress, the pigtail has 47.9 mm of free cable left. Then comes the rigid 90 mm M12 plug + socket.
   - That junction cannot be placed in any direction the pigtail can reach without hitting something in some adopted path:
     - UR5e: the north wall on the lever (all 185 states) and the forearm on the lid (559 states);
     - FR5: lever, lid, spatula and spider.
   - A free-space map built from every set confirms this: no junction placement clears all sets. Hub group A and the carrot prep each block it on their own.
   - The variant with the tie at the end of the bend (`yp_a-45_r0_tc`) fails the same way.
5. **A single flexible cable does fit the UR5e (`yp_a-45_tcf`): all sets certified, 0 hit states.**
   - It is the `yp_a-45` first section continued as **one Ø6.4 cable with no M12 junction**: under the gripper's far side and up its −y side to a right-angle M8 on the tool connector.
   - **The full unchecked checker passes every set with 0 hit states:** 6 chains, both stir halves, the 22 hub edges and 9 prep sets (§5).
   - **Smallest cable reserves:** 10.1 mm to the environment (bascarrot) and 1.3 mm to self (carrot).
   - **Cost:** the pigtail must be **454.5 mm** from the boot tip [M]; DH's standard is 200 mm. It must end in a right-angle M8 plug. This is a DH custom cable [E], not yet confirmed.
6. **The FR5 has no passing run yet.**
   - On the spatula chain, the FR5 forearm's wrist-1 housing comes inside the right-angle plug on the RS485 connector. This happens for every run tried, because it depends on the connector and the plug [E: plug size], not on the route.
   - The flexible FR5 run also meets the closed door on the wok chain.
7. **Tolerance tool fixed (#13).**
   - `r19tol_core.py` no longer counts `R_pgc_cable*` as held, and a cable option now uses its base option's stored paths.
   - **Proof:** 8 stored `ur5e_enc2_pgc PY=.15` tolerance results reproduce exactly.
   - With `ur5e_enc2_pgcc_yp_a-45` the held set is the same 2 geoms as without the cable, and the results equal the cable-free ones. Before the fix the held set was 7 geoms (5 cable shapes) and the run used the wrong (old UR5e) path.

## 1. What DH's CAD shows

**Method.** The files were opened read-only:
- `inputs/dh_cad/step/PGC-140-50-W-S_simple_v4.0_20240814.step` (byte-identical to the zip copy);
- `inputs/dh_cad/zip_x/PGC-140-50_2D&3D Model/PGC-140-50_标准法兰_v1.0.STEP`, copied to the scratchpad to get an ASCII path.

They were read with **gmsh 4.15.2** (OpenCASCADE), pip-installed into a new isolated venv `scratchpad/stepenv` and run with `-I`. Every trimmed face was point-sampled (a parametric grid kept by `isInside`, plus the boundary curves; 1.02 M points). The measurements were taken from those points [M on S].

The gripper model has 10 solids (the two fingertips) plus a 1,304-face surface model (the body, boot, cable and plug).

| Quantity | Value | Model (r19cable.py) | Verdict |
|---|---|---|---|
| Mounting (bottom) face | the annulus at the lowest level; 98.0 mm to the jaw top, 138.5 mm to the fingertips (the drawing's 98 / 138.5) | `X0` | the same datum |
| Exit (cable-axis) height above it | **21.00 mm** | band 19–25 mm | inside: **kept** |
| Position around the body | **0.00 mm** off the jaw plane; radial, along the jaw stroke, under one jaw | radial under the ±y jaw | **as modelled** |
| Boot | collar **Ø15.50** (0–0.5 mm out), then Ø13.4 tapering to Ø11.3; the tip **10.50 mm** past the Ø75 surface; it sits in a pocket down to r 30.0 | Ø16, from 3 mm inside to **12 mm** out | encloses it: **kept**. The modelled bend starts 1.5 mm past the real tip, which is a valid dress |
| Cable | Ø6.40; **153.0 mm** of free cable, then an M12 plug **47.0 mm × Ø16.2** (knurled nut); 200.0 mm in all (the drawing's "200") | Ø6.4 | as modelled |
| Body near the exit | Ø75.0 (r 37.50) from the face to h ≈ 30 mm; a taper to the 53 mm flats (±26.5 across the jaw plane) from h ≈ 51; at the exit a pocket (r 34.5) and a 0.27 mm collar | Ø75 polygon (faces at r 37.50), 53 mm part from h 52 | see the note below |
| Small protrusions | 4 radial screw heads Ø7.0, r 38.13 (**0.63 mm proud**) at ±73.8° / ±106.2° from the exit, h 11.9–18.2; a Ø≈5 dome at 180°, r 38.40 (**0.90 mm proud**), h 11.5–16.5 | not enclosed | §9 |

**The standard flange (`法兰-PGC140`, one solid, 22.6 cm³, ≈ 61 g if aluminium [E]):**
- a Ø75 × **5.0 mm** plate;
- robot side: a Ø31.5 × **2.5 mm** spigot (bore Ø25.5), and 4 × Ø6.5 holes with Ø12.5 counterbores on PCD 50 plus a Ø6 pin (ISO 9409-1-50-4-M6);
- two **ears**, circular segments r 31.6–37.5 spanning ±30° and **14.9 mm** tall. Each has a Ø3 pin hole on top and two radial Ø7.5 counterbores at 15.0 mm for the screws into the gripper.

**The flange is inside the gripper model.**
- The gripper STEP's bottom annulus (3,413.4 mm²) and its Ø31.5 × 2.5 ring (179.0 mm²) are the flange's robot face and spigot: 3,413.3 / 179.1 mm².
- The gripper's 4 radial screw heads are the ear screws.
- So the "98" and "138.5" on DH's W-S drawing are measured from the flange's robot face, and so is the model's `X0`.
- `arms.py` therefore already includes the standard flange's thickness; nothing is missing between the robot face and the gripper.
- The FR5 `sp20` plate in R19_FR5.md §4.1 "replaces DH's standard flange". It is therefore a 20 mm stand-off in place of the 5 mm plate, and the ears and the screws still have to be provided.

**What `arms.py` gets wrong (not changed here).** The tool pose is inherited from R10 ("custom flange adapter orientation remains a design assumption").
- **Where it puts the gripper:**
  - the gripper axis is **26.6°** off the J6 axis;
  - the bottom face centre is **45 mm behind the flange plane and 78 mm off axis** [M].
- **Overlap with wrist 3:** the housing then lies inside the wrist-3 shapes by **16.9 mm** on the UR5e and **16.3 mm** on the FR5 `sp20` [M]. Wrist 3 is R_tool's parent, so the checker never looks at that pair.
- **Stand-off needed:** moving the gripper along the flange axis gives −16.9 at 0 mm, −4.2 at +30 mm, −0.3 at +40 mm and +3.9 at +50 mm. So it needs about **41 mm** of extra stand-off just to touch.
- **Adapter:** no adapter is modelled, and none could sit in that space.

## 2. The cable model

- **Shapes unchanged.** Every measured value is inside the band or enclosed by the model, so `r19cable.py` keeps its geometry. Its `DIMS_SRC` now cite the STEP values.
- **New routings.** `r19cable.py` loads the runs from the new `r19cable2_tc.py` as routings `'<routing>_tc*'`, added after the screening sets.
  - `arms.py` then creates the options `ur5e_enc2_pgcc_<r>` and `fr5_j6_pgc_sp20c_<r>`, plus the screen `<base>c_TC`.
  - `arms.swap()` now passes the arm to `r19cable.add()`, so a run ends on that arm's tool connector. This is the only `arms.py` change, one line.
- **Existing options unchanged.**
  - `r19cable2_md5.py` builds every option that existed before, once with the backups (`*.bak_r19cable2`) and once with the new files.
  - Result: **72 options, 90 scenes, 90 identical** (`results/r19/cable/md5_2_compare.json`).

## 3. The tool connectors and the plugs

| | Value | Source |
|---|---|---|
| UR5e tool connector | M8 8-pin, robot side Lumberg RKMW 8-354; male before 1 Sep 2024, female after (in a redesigned cap; UR supplies a 15 cm M–M adapter); RS485 + 24 V | [S] UR5e tool drawing https://www.universal-robots.com/media/1833559/ur5e-tool-drawing.jpg ; PCN https://www.universal-robots.com/articles/ur/documentation/product-change-notification-change-to-m8-female-connector-on-the-e-series/ |
| Its position | axis radial, on the line of the Ø6 dowel hole, **31.55 mm** behind the flange face | [S] drawing. [M] The Menagerie `wrist3.obj` bump is at 31.57 mm, Ø≈9.8, top at r 43.5: used for the model |
| FR5 end connectors | **RS485 5-pin** (485-A, 485-B, 24 V, GND) and **M12 8-pin female I/O** (AI0, AO0, DI0, DI1, 24 V, DO0, DO1, GND: no RS485). Type and size of the 5-pin: not published | [S] Fairino Cobots manual 3.5.4, https://fairino-doc-en.readthedocs.io/latest/CobotsManual/installation.html |
| Their position | both flush, radial, centre **21 mm** behind the flange (z 79.0 in the wrist-3 frame); 5-pin at **−90°** and 8-pin at **180°** from DH frame 6 x; Ø≈14.6 faces | [M] vendor `wrist3_link.STL` (frcobot_ros2 fairino5_v6), contact patterns |
| DH cable / kit | the pigtail ends in an M12 8-pin plug; a 5 m extension is included; an **M8 outlet for robots with an M8 port "can be customised"**; the UR+ kit "includes connection cables" (code and length not published); **no Fairino kit**, and Fairino is not in DH's partner list | [S] PGC Short Manual v2.1 pp.5–7, https://uploads.unchainedrobotics.de/media/file_upload/PGC-50-Short-Manual_v2.1_b768bd7b.pdf ; https://www.universal-robots.com/marketplace/products/01tP40000071NMzIAM ; DH catalogue p.26, https://uploads.unchainedrobotics.de/media/file_upload/DH-Robotics-catalog-EN_46faa8dd.pdf |
| Pinout match (FR5) | DH pins 3/4 (OUT1/2), 6/7 (IN2/1), 5 (24 V) and 8 (GND) match FR5 I/O pins 3/4 (DI0/1), 6/7 (DO0/1), 5 and 8. **But DH pins 1/2 are RS485, while the FR5 I/O pins 1/2 are AI0/AO0.** A straight M12–M12 cable is therefore not safe; RS485 needs the 5-pin connector | [S] the two pinouts above |
| UR plug model | right-angle M8 8-pin, from Binder 77 3408: 18 mm from the mating face to the top, 24 mm from the axis to the strain relief, 4.5 mm behind the axis, head 10.8 mm. Modelled as a box, +1 mm on every side | [S] https://www.binder-connector.com/prod_media/masszeichnung_produktzeichnung/77-3408-0000-WD08.jpg ; the male (post-2024) version taken the same [E] |
| FR5 plug model | right-angle M12 envelope of Lumberg RKWT 8-282: 26.6 mm to the mating face, 31 mm from the axis to the overmould end, Ø14.5 | [S] R19_CABLE.md §1; the 5-pin connector type is assumed [E] |
| M12 junction | DH plug 47.0 × Ø16.2 [S, STEP] + a straight M12 socket of 43 mm [S, Lumberg RKT 8-282] = one rigid Ø16.2 × 90 mm body, with no mating overlap credited | [E] |

## 4. Modelling the run (`r19cable2_tc.py`)

**Fixed to wrist 3.** The whole run is rigid with wrist 3, because the gripper is bolted to the flange and the connector is on the wrist-3 housing. It is therefore a fixed shape on `R_tool`, placed in the housing frame like the first section.
- On the FR5 the tool-connector pose is taken through `arms.swap`'s flange→tool transform: 90° clocking and the 20 mm spacer.

**How the centreline is built.**
- It starts at the end of the first section, the first tie, on the measured 21.0 mm exit height. The first section itself stays the 19–25 mm band hull.
- It is a corner polyline. Every corner is filleted at the **R50 rule (centreline 53.2 mm)**, which is also used for the adapter cable [E].
- The M12 junction must lie on a straight, starting where the 47.9 mm of free pigtail ends.

**How the shapes are built.** Every bend is a set of hulls of circumscribed cross-sections every 5°, inflated by the sagitta, as in `r19cable.bend`. The plug is a box. The names start with `R_pgc_cable_tc_`, so the run gets the 5 mm gate and no contact window.

**How the routes were found** (scratch `opt_tc.py`). A random search plus local refinement over:
- the junction direction, inside the cone the pigtail rest allows (≤ 51.6° from the dress direction);
- 0–3 corners;
- the clocking of the plug;
- the tail length.

Hard limits:
- housing ≥ 2 mm, fingers ≥ 10 mm, wrist 3 ≥ 2 mm (the plug, which sits on the connector, is excluded);
- wrist 2 ≥ 3 mm over a whole J6 turn.

Score: reach about J6, staying in front of wrist 2, length, and the share of a J5 × J6 grid where the run meets wrist 1. In the second stage it also used:

**Free-space maps** (`r19cable2_free.py`).
- **What it computes:** for every state of a set, using the scenes and states of `r19cable_check.py`, the distance from each voxel of a grid fixed in the housing frame to:
  - every environment geom the checker pairs with the cable;
  - every robot geom it pairs with the cable as self;
  - the held object.

  It keeps the minimum over all states.
- **Settings used:** 10 mm voxels and every 4th–6th state, so the maps are a guide only.
- **The map does not certify anything:** every candidate it suggested was afterwards screened or certified with the real checker.

**What the maps show** (UR5e, all 16 set maps combined).
- **The free region:** a compact bubble around the gripper, about x −260 … −20 mm and within about 130 mm of the gripper axis. The first tie and the connector both lie in it.
- **The junction does not fit:** the best placement of the rigid 90 mm junction falls **39 mm** short of the needed clearance with `yp_a-45` (**17.6 mm** with `yp_a-45_r0`).
  - Taken set by set, hub group A (−30.7 / −28.9 mm env / self) and the carrot prep (self −21.1 mm) each leave no room on their own.
- **A flexible cable fits:** without the junction, runs that fit within the map's own error exist. They were then confirmed exactly (§5).

## 5. Results

### 5.1 Pass / fail (hit states; smallest cable reserve past the gate, environment / self, mm) [M]

**Certificate** = the full checker, one routing, no `CABLEONLY`. **Screen** = `CABLEONLY=1`: only the cable pairs are evaluated, under the checker's own rules; every other pair is the one already certified.

| Set | UR5e **`yp_a-45_tcf`** (certificate) | UR5e `yp_a-45_tc` (screen) | UR5e `yp_a-45_r0_tc` (screen) | FR5 `yp_a-45_tc` (screen) | FR5 `yp_a-45_tcf` (screen) |
|---|---|---|---|---|---|
| wok + 2 approaches | **0**; 33.8 / 19.2 | 0; 32.8 / 2.0 | 0; 38.8 / 2.0 | 0; 10.8 / 2.0 | **159**; closed door |
| plate 2 | **0**; 33.9 / 19.2 | 0 | 0 | 0 | **1**; door |
| lever | **0**; 20.5 / 20.1 | **185 (all)**; north wall | **185**; wall | **195**; wall | 0; 3.8 / 7.6 |
| lid (keyed rack) | **0**; 63.4 / 3.0 | **559**; forearm vs junction | **234**; forearm | **654**; forearm | 0; 18.4 / 2.0 |
| spatula | **0**; 155.3 / 25.6 | 0 | 0 | **777**; plug vs forearm wrist-1 housing | **908**; plug vs forearm |
| spider | **0**; 104.2 / 6.1 | 0 | 0 | **1,010**; forearm | 0; 59.2 / 1.3 |
| stir (work + return; plume rule) | **0**; 225.5 / 35.8; plume 166.6 | n.r. | n.r. | n.r. | n.r. |
| hub, 22 edges (`hub_final_1.56_.20`) | **0**; 19.0 / 2.8 | n.r. | n.r. | n.r. | n.r. |
| prep carrot / press / tomato | **0**; 34.5 / 1.3, 68.5 / 16.2, 12.0 / 5.4 | n.r. | n.r. | — | — |
| prep step 3 (bascarrot, basket y20p30, ctray, soak, tub empty, tub fill t15fin) | **0**; smallest 10.1 / 8.8 | n.r. | n.r. | — | — |
| **Verdict** | **PASS: every set, 0 checker hits** | FAIL | FAIL | FAIL | FAIL |

Notes:
- **n.r.** = not run: the option already fails. **—** = no FR5 prep sets in this layer (another agent is re-planning them).
- **Checker reserves of the `tcf` certificates:** every hit count of the checker as a whole is 0. The non-cable reserves are the certified ones (wok 2.016 / 1.87; lid self 1.109; spider self 0.781).
- **Data:** per-set data is in `results/r19/cable/summary2.json` (`python r19cable2_table.py`).
- **Screening candidates:** the UR5e screening model `TCX` carried 3 flexible candidates. `f0` is the adopted one; `f1` and `f2` also passed every set.

### 5.2 Static checks (`results/r19/cable/static2.json`; pairs the checker cannot see; mm) [M]

| Option | Run vs housing | vs wrist 3 (plug excluded) | vs fingers | vs held objects | vs wrist 2, whole J6 turn | Share of J5 × J6 where the cable meets wrist 1 | Length (pigtail / adapter) |
|---|---|---|---|---|---|---|---|
| UR5e `yp_a-45_tcf` | 15.0 | 16.7 | 44.3 | ≥ 133 | 6.2 | 7.4 % (5.2 % with the first section alone) | run 350.9; **pigtail from the boot tip 454.5**; reach about J6 215.8 (was 174.7) |
| UR5e `yp_a-45_tc` | 16.7 | 15.6 | 30.8 | ≥ 118 | 6.5 | 6.9 % | 502.6 (pigtail rest 47.9 + junction 90 + adapter **364.7**) |
| UR5e `yp_a-45_r0_tc` | 16.7 | 15.6 | 29.2 | ≥ 117 | 6.6 | 6.9 % | 430.5 (adapter 272.6) |
| FR5 `yp_a-45_tcf` | 15.5 | 19.3 | 5.1 | ≥ 56 | 7.9 | 0 % | 481.4 (pigtail 585.0) |
| FR5 `yp_a-45_tc` | 58.0 | 21.7 | 50.8 | ≥ 98 | 5.8 | 0 % | 593.5 (adapter 455.6) |

Notes:
- **The plug on the connector:** it touches the wrist-3 shapes (0.0 mm). This is expected, because its coupling nut surrounds the connector, which the wrist-3 hull encloses.
- **FR5 reach:** the radial-reach field of `r19cable_static` assumes the UR frame; ignore it for the FR5.

## 6. What the runs mean in hardware

**UR5e, `yp_a-45_tcf` (adopted for the checking standard if §8.1 is accepted).**
- **Outlet and dress:** the outlet is under the +y jaw, the cable is bent R50 down and away from the flange side, and it is tied 20 mm after the bend, all as decided.
- **Path:** the cable then continues in one piece:
  - under the gripper's bottom on its far side;
  - up the −y side, 15 mm off the body;
  - into a right-angle M8 on the tool connector, whose cable exit points away from the flange side (tool −z).
- **Bends:** all at ≥ R50.
- **Needs:**
  - a DH pigtail **≈ 455 mm** from the boot tip (DH lists 200 mm), ending in a **right-angle M8 8-pin** plug: female for robots built before 1 Sep 2024, male after;
  - ties along the run. The model fixes the run's shape, so the ties must hold it there: at least at the corners (§4; corner points in `ROUTES`).
- **Not confirmed:** DH says an M8 outlet is possible "after confirmation". The length and the right-angle plug are [E]. No one was contacted.

**With DH's standard pigtail + an M12–M8 adapter (`yp_a-45_tc`).** The 90 mm M12 junction has to hang 50–140 mm past the tie, and every place it can reach is hit in some adopted path. That option fails.

**FR5.** No run passes.
- **Spatula:** in this chain the plug on the RS485 connector meets the forearm's wrist-1 housing. That is the connector and the plug [E: plug size]; a run cannot change it.
- **Possible fixes, not tried:**
  - a smaller or straight 5-pin plug once its type is known;
  - the M12 I/O connector at 180°, which faces the outlet side. It has no RS485, so it would only work with DH's I/O control mode and an adapter that leaves pins 1/2 open;
  - a different FR5 clocking.

## 7. Tolerance tool (#13): `r19tol_core.py` (backup `r19tol_core.py.bak_r19cable2`)

**What changed.**
- **Cable not held:** `Ev.held` now excludes `R_pgc_cable*`, so the cable is part of the robot. Cart perturbations move it, and grasp perturbations do not.
- **Paths of a cable option:** `tagged()` / `hubdir()` use the base option's stored paths for a cable option (`_path_arm`: `<base>c[_<routing>]` → `<base>`). Every other option is unaffected (`PTAG == TAG`).

**The proof** (`r19cable2_tolcheck.py`). It writes to `results/r19/cable/tolcheck/`, never to the stored folder.

| Run | Tasks | Result |
|---|---|---|
| `ARM=ur5e_enc2_pgc PY=.15`, re-run against the stored `results/r19/tol/ur5e_enc2_pgc_py.15` | lever grasp-x, grasp-rot (`ROTMAX=4`, as stored), cart-x, fix, grid-z, scen-R09_requirement; spatula grasp-y | **8 / 8 identical** (every JSON value, timing fields excluded) |
| `ARM=ur5e_enc2_pgcc_yp_a-45 PY=.15`, compared with the same stored results | lever grasp-x, grasp-rot, cart-x, fix; spatula grasp-y | held geoms 2 (the cable 0); 4 / 5 identical. The 5th (fix) differs only in two informational group lower bounds: counter 79.1 and sink 79.58 mm against the 80 mm cap, because the cable now counts as robot |
| Old core, same cable option | — | held geoms **7**: the 5 cable pieces counted as held, and the run used `results/r17/chain_lever_s+1_final.json` (the old UR5e path) |

## 8. Decisions needed

1. **Adopt `yp_a-45_tcf` for the UR5e** (`ARM=ur5e_enc2_pgcc_yp_a-45_tcf`): one ≈ 455 mm DH pigtail with a right-angle M8, routed and tied as in §6, with no M12 junction on the wrist.
   - It needs DH to confirm the custom cable.
   - The alternative, DH's standard pigtail plus an M12–M8 adapter, does not fit the adopted paths.
2. **The gripper pose (from §1):** the modelled housing is 16.9 mm inside wrist 3. A real adapter needs about 41 mm or more of extra stand-off along the flange axis, or a different pose.
   - Any real fix moves the gripper relative to the flange, so every chain, hub edge, the stir entry, the prep sets and the cable routing would have to be re-planned or re-checked.
   - I recommend deciding this before more certificates are built on the current pose.
3. **FR5:** confirm the type and size of the RS485 5-pin connector before redesigning its run, or choose the I/O connector (DH in I/O mode) or a different clocking.

## 9. Limits

- **Small body protrusions:** the 4 screw heads (0.63 mm) and the dome (0.90 mm) at h 11.5–18.2 mm stick out of the Ø75 housing model. They are inside every gate (5 mm), but they are not enclosed by the shared housing model (`scene.oem_pgc_drawing`), which was not changed.
- **Run shape:** the modelled run is one specific dress. The real cable must be tied to it, and a slack cable is not modelled. The adapter cable / custom pigtail bend radius is taken as DH's R50 [E].
- **Plugs:** the plug envelopes come from Binder / Lumberg sheets. The post-2024 male M8 and the FR5 5-pin are [E].
- **Free-space maps:** coarse (10 mm voxels, every 4th–6th state). They are only a search guide; the certificates are the real checker.
- **Hub edges:** `TCX` and `TC` screen files share names across runs. The 24- and 8-candidate screens of `yp_a-45` are kept in `logs2/scr_ur_lever.txt` and `logs2/scr8_ur_lid_spat.txt`; their JSONs were overwritten by the flexible-candidate screen.
- **Not done:** `r19stir_report.py` (it writes the shared stir summary); tolerance runs with the cable (now possible); the FR5 prep sets (being re-planned elsewhere).

## 10. Controller lanes (optional; each line < 5 min, est.)

```bash
cd /c/Users/admin/Documents/YJGames/robot_rail/sim/r10/claude
PY=C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe
L="RACK=keyed SPX=1.56 SPY=.20 PY=.15"
# lane A (record only; the FR5 options already fail): the FR5 screens of the three runs on stir and hub (~1 min, then ~2-3 min per hub line)
$PY r19cable_check.py stir LIB=results/r19/stir/lib_stir_cycle_fr5_j6_pgc_sp20.json ARM=fr5_j6_pgc_sp20c_TC CABLEONLY=1 WORKERS=26
D=results/r19/fr5/hub_py.15_fr5_j6_pgc_sp20
$PY r19cable_check.py hub DIR=$D POT=1 $L ARM=fr5_j6_pgc_sp20c_TC CABLEONLY=1 WORKERS=26 TAG=fr5tc_a EDGES=LEV_O__WOK,SPAT__LEV_C,LID_RACK__H_WOK,SPIDER__H_WOK,LID_RACK__H_POT,SPIDER__H_POT,LID_POT__H_WOK
$PY r19cable_check.py hub DIR=$D POT=1 $L ARM=fr5_j6_pgc_sp20c_TC CABLEONLY=1 WORKERS=26 TAG=fr5tc_b EDGES=LID_POT__H_POT,LEV_C__H_WOK,LEV_C__H_SPAT,LEV_O__H_WOK,LEV_O__H_SPAT,LEV_C__H_SINK,LEV_O__H_SINK
$PY r19cable_check.py hub DIR=$D POT=1 $L ARM=fr5_j6_pgc_sp20c_TC CABLEONLY=1 WORKERS=26 TAG=fr5tc_c EDGES=SPAT__H_SINK,SPAT__H_SPAT,WOK__H_POT,WOK__H_SINK,WOK__H_WOK,H_SINK__H_WOK,H_SPAT__H_SINK,H_WOK__H_POT
# lane B: when a UR5e prep set or chain is re-planned (#4 jobs), re-certify it with the adopted run (~1-2 min each), e.g.
$PY r19cable_check.py prep FILE=results/r19/prep/chain_<set>_ur5e_enc2_pgc.json ARM=ur5e_enc2_pgcc_yp_a-45_tcf WORKERS=26
# lane C (#13): tolerance runs now work with the cable, e.g. the lever, as r19tol_replay (writes results/r19/tol/ur5e_enc2_pgcc_yp_a-45_tcf_py.15)
$PY r19tol_replay.py SCENES=play:lever PARTS=cartT,cartR,grasp ARM=ur5e_enc2_pgcc_yp_a-45_tcf PY=.15 WORKERS=8
# tables
$PY r19cable2_table.py
```

## 11. Files

- **New code:**
  - `r19cable2_tc.py`: the measurements, ports, plugs, the route builder and `ROUTES`;
  - `r19cable2_screen.py`: many candidate runs in one screening model;
  - `r19cable2_free.py`: the free-space maps;
  - `r19cable2_static.py`: the static checks of the runs;
  - `r19cable2_md5.py`: the default-unchanged check;
  - `r19cable2_tolcheck.py`: the tolerance reproduction;
  - `r19cable2_table.py`: the tables.
- **Changed** (backups `*.bak_r19cable2`):
  - `r19cable.py`: the `DIMS_SRC` labels, the `_tc` routings and screen `TC`, `add(.., arm)`, and `summary()` skipping the runs;
  - `arms.py`: one line in `swap()`;
  - `r19tol_core.py`: the cable exclusion and the base-option paths.
- **New results** (`results/r19/cable/`):
  - certificates `*__ur5e_enc2_pgcc_yp_a-45_tcf.json` (chains, stir, `hub/hubtcf_{a,b,c}`, prep);
  - screens `*__*_TC_cableonly.json`, `*__*_TCX_cableonly.json`, `hub/flexhub_*`;
  - `static2.json`, `summary2.json`, `md5_2_*.json`, `cands_*.json`;
  - `free/*.npz`, `tolcheck/`, `logs2/`.
- **Scratch:** `stepenv/` (gmsh) and `cable2/` (the CAD survey, search and plot scripts).
- **Not touched:** no other agent's or controller lane's outputs. `inputs/dh_cad` was read only.
