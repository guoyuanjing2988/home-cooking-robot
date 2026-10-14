# R19 m2 cable: the PGC-140 cable run on the m2 wedge mount (GitHub #36 / #42, Windows, 2026-10-14)

**Unchanged:** gates, checker, fixtures, the m2 mount, the first cable section `yp_a-45` (the #36 decision, R19_CABLE2.md), every adopted motion except the two ct2s sets below.

## Answer first
- **One routing key, `yp_a-45_m2tc`, with a per-arm run to the tool connector.** Arm options: `ur5e_enc2_pgc_m2c_yp_a-45_m2tc` and `fr5_j6_pgc_m2c_yp_a-45_m2tc`. One flexible cable from the boot to the plug, with no M12 junction.

| | UR5e m2 | FR5 m2 |
|---|---|---|
| Port | UR tool connector (as R19_CABLE2) | FR5 end RS485 connector, with a **compact right-angle plug** (M8-size envelope, 18 mm face to top) |
| Run, boot to plug | 276 mm, 2 corners | 394 mm, 2 corners |
| Pigtail length from the boot tip | **≈ 380 mm** | **≈ 497 mm** |
| Plug vs the wedge / housing (static) | 15.8 mm | 6.8 mm |
| Plug vs wrist 2 over the whole J6 turn | 6.3 mm | 9.6 mm |
| Plug vs wrist 1 over J5 × J6 (7,200-point grid) | **−7.6 mm in 1.7 % of the grid** (around J5 = J6 = −180°) | ≥ 18.1 mm |
| Cable vs fingers / held objects | 68 mm / ≥ 146 mm | 68 mm / ≥ 146 mm |

- **Certificates [M]:** every adopted m2 set, full checker with the cable modelled (no CABLEONLY):
  - UR5e: 24 result files, 88,380 states, **0 hits**, min environment reserve 0.29 mm (ct2s);
  - FR5: 23 result files, 95,089 states, **0 hits**, min environment reserve 1.0 mm.
  - Covered: the 6 cooking chains, every prep set (with the T2L cradle layers where certified so), every ok hub edge (UR5e 20, FR5 22), the stir short-push library, the stir join, and both stir libraries in the current layout.
- **One motion change per arm: ct2s.** With the cable present, the tray pick put the cable into the cart's staging block (`R_cart_p5_stg_block`, MuJoCo contact −26 mm; this pair is seen by the contact rule only). Re-planned with the cable option, so the planner avoids it:
  - UR5e: `chain_ct2s_cabk62_ur5e_enc2_pgc_m2c_yp_a-45_m2tc.json` (tray yaw 35°, pick / return cart fixed at −0.62 by the new `r19m2cable_ct2s.py`); 5,542 states, 0 hits, min 0.29 mm; 29.7 s (was 28.9 s).
  - FR5: `chain_ct2s_cabf_fr5_j6_pgc_m2c_yp_a-45_m2tc.json` (tray yaw 10°, free pick cart → −0.614); 5,241 states, 0 hits, min 2.0 mm (the cable-less fix had 0.36 mm); 30.5 s (was 30.0 s).
  - Why fix the UR5e pick cart: left free, the pick moved to −1.18 and the lane join to the pour cart (−0.52) was blocked (tray vs base plate in the 0.7 m shuffle).
- **No other arm option changed:** md5 of all 110 scenes of the 86 options that existed before is identical (`results/r19/cable/m2/md5_compare.json`).

## 1. What was rejected
- **UR5e, flat run with no corners (`yp_fl`):** clears the cart, but the run meets the range hood in the wok play (bound −5.0 mm, contact −42 mm).
- **UR5e, runs behind the gripper:** clean on every set except ct2s (cart staging block); fixed by the ct2s re-plan rather than by routing, because no run clears both the hood (wok) and the staging block (ct2s): the cart free-space map search (`scratchpad/m2cable/opt_ur_m2_cart*.json`) found none.
- **FR5, standard M12 right-angle plug on the RS485 port:** meets the forearm's wrist-1 housing on the spatula chain at every plug clocking.
- **FR5, the end I/O M12 8-pin connector:** fails in the wok play (closed door, bound −4.8 mm, contact −13.9 mm). It also has no RS485, so the PGC would run in I/O mode.

## 2. Open, before buying anything
- **FR5 plug [E]:** the 5-pin RS485 connector type and size are not published (R19_CABLE2.md §3). This route holds only if a right-angle plug no taller than the M8-size envelope mates with it. Confirm the connector type from Fairino docs or the arm, then the pigtail.
- **Pigtail length:** UR5e ≈ 380 mm, FR5 ≈ 497 mm, against the ≈ 455 mm estimated for the old mount. Order only once the arm is chosen. Nobody has been contacted (DH custom pigtail is the user's call).
- **UR5e wrist-1 zone:** the plug overlaps wrist 1 when J5 and J6 are both near −180°. No adopted state enters it (all are path-checked); new plans must keep out of it, which the path checker already enforces because the cable is modelled.
- **Not modelled:** cable sag and stiffness (the run is a fixed shape, as in R19_CABLE2.md).

## 3. Files (all new unless noted)
- `r19m2cable.py`: the m2 cable options (registered from `arms.py`, hook added earlier with backup `arms.py.bak_r19m2cable`); `ROUTES_M2['yp_a-45_m2tc']`, `PORTS_M2['fr5c']`.
- `r19m2cable_check.py` (path checks per mode: chains, prep, hub, stir, join, std), `r19m2cable_static.py`, `r19m2cable_free.py`, `r19m2cable_md5.py`, `r19m2cable_ct2s.py`.
- Results: `results/r19/cable/m2/` (certificates per mode, `static.json`, `md5_compare.json`, screens in `screen_*/`, candidates in `cands/`, logs in `logs/` and `logs/cert/`).
- Search scratch (not results): `scratchpad/m2cable/` (route optimiser, free-space and cart maps).
- Lane: `scratchpad/lanes/m2_cable.sh` (both arms in parallel, about 30 min).

## 4. Next
- Point the dock manifest (R19_DOCK.md §10) and the export at the two new ct2s files and the cable options, then re-run the dock lane and the re-export.
