# R19 m2: stir cycles that the spatula hand-off can join (GitHub #42, lane 5) (Windows, 2026-10-14)

- **Unchanged:** gates, checker, fixtures, the m2 mounts, the spatula chains, the hub roadmaps, the join rule ("the self-motion must arrive exactly at H_stir0, else no join, no fallback"), the stir bench path, the #41 short-push method.
- **What failed:**
  - **UR5e lane 5.** The m2 stir cycle starts on the other wrist branch: q5 ≈ −110° against the spatula end's +111°. The join stopped with "another IK branch".
  - **FR5 #41 spill.** The m2 stir cycle was built with **jaw sense +1**: the spatula sits turned 180° in the jaws. Both r19spill_cycle.py and r19stir2_join.py hold the spatula with jaw sense −1 (`SIGN=-1`, hard-coded).
    - So the spill's new working parts started 223–229° away from the stored states (`start_dev_deg`), and its return1→2 found 0 of 187 options.
    - The FR5 join would have failed the same way: the self-motion ends 130.8° off.
- **Cause, both arms:** `r19stir_cycle.cycle` takes the cheapest chain over all jaw senses and branches. On the m2 mounts the cheapest one is not the spatula chain's branch.
  - UR5e: proxy 11.109 s on the wrist-down branch, against 11.167 s on the spatula's.
  - FR5: 11.298 s with jaw +1. No jaw −1 chain on the spatula's branch existed at the stir cart x = 0.55.
- **Fix [M], motion only:**
  - **UR5e:** the cycle step re-run with the chain restricted to jaw −1 and stroke 0 starting on the spatula end's branch.
    - The existing works and returns are kept. The chain is `[1,1,1,1,1]`, already screened.
  - **FR5:** the stir cart moved from x = 0.55 to **0.45**; reach, works, returns and cycle re-run on that branch only.
    - At 0.50, 0.55 and 0.60 the stroke-4 start on this branch has the forearm elbow in the upper cabinet / closed door (−10 mm reserve). At 0.40 and 0.45 all five stroke starts are clear.
- **Smoke, every step [M]:** cycle, #41 spill pipeline and join were run in `results/r19/stir/m2join/cycle_<arm>_smoke/` at WORKERS = 8.
  - Every certificate has 0 hits, and both joins reach H_stir0.
  - The in-place runs are in `scratchpad/lanes/m2_join.sh`, about 10–15 min with UR5e and FR5 in parallel.

## 1. Results (smoke runs; the lane repeats them in place)

| | UR5e m2 old (adopted 09:18) | **UR5e m2 new** | FR5 m2 old | **FR5 m2 new** | ref UR5e m0 / FR5 sp20 |
|---|---|---|---|---|---|
| chain (jaw, combo), cart x | −1 `[0,0,0,0,0]`, .55 | **−1 `[1,1,1,1,1]`, .55** | +1 `[0,0,0,0,0]`, .55 | **−1 `[0,0,0,0,0]`, .45** | −1, .55 / −1, .55 |
| stroke-0 start: branch (elbow, wrist) | (−1, −1) | **(−1, +1)** | (−1, +1), jaw +1 | **(−1, +1)** | (−1, +1) / (−1, +1) |
| join self-motion: end vs H_stir0 | 180° (fails) | **3.5e−5° (ok)** | 130.8° (regrasp) | **1.3e−7° (ok)** | ok / ok |
| cycle certificate (A): states, hits | 4,357, 0 | **4,326, 0** | 4,293, 0 | **4,181, 0** | 4,484 / 3,973, 0 |
| robot–environment reserve, mm | 86.3 | **17.1** (forearm vs closed door 1_1) | 80.1 | **11.2** (forearm elbow vs closed door 1_0) | 21.6 / 10.0 |
| min plume, mm | 25.8 | 25.8 | 29.1 | 25.8 | 25.8 |
| cycle period A, A_UR (s / stroke) | 2.232 | **2.279** | 2.298 | **2.228** | 2.321 / 2.286 |
| #41 short-push library: states, hits | 4,396, 0 | **4,404, 0** | failed | **4,231, 0** | 4,547 / 4,039 |
| #41 period (jerk 8000, s / stroke) | 2.5968 (W .1) | **2.6183** (W .2) | none | **2.5655** (W .2) | 2.8062 / 2.6446 |
| join: cart travel, states, hits (stir and std) | none | **0.078 m, 112, 0 / 0** | none | **0.017 m, 26, 0 / 0** | 0.078 m, 106 / 0.143 m, 189 |
| join entry time (fastcart) | none | **1.28 s** | none | **0.69 s** | 1.28 / 1.64 s |

- All certificates are the unchanged ones: ≤ 4 mm states, Checker.check(full=True), 10 / 5 / 0 mm, joint ranges, R11 mesh rule, the plume rule.
  - Spill libraries: also re-checked in the current layout ('std'). The minimum is 2.0 mm on both arms, held spatula vs wok.
  - Join: certified in the stir and the std scenes.
- **What the change costs:**
  - **UR5e:** +0.047 s per stroke on the base cycle and +0.02 s on the #41 library. It is still faster than the m0 UR5e. The forearm passes closer to the closed door, 17.1 mm of reserve instead of 86.3.
  - **FR5:** the cart parks 10 cm further left for stirring. The join is shorter, 1.7 cm instead of 14.3 cm on sp20. The forearm's reserve to the closed door is 11.2 mm, the same order as FR5 sp20's 10.0 mm.
  - **Not cable-checked:** neither arm, because no m2 cable options exist yet (#36).
- **Hub edges.** The spatula chains are not changed, so the hub edges that use SPAT stay valid: they start at the chain's pick.

## 2. Why these options

1. **Re-plan the spatula chain's end onto the stir branch.** Not taken.
   - **UR5e:** it would mean a chain re-plan and a ≤ 4 mm re-check. The restricted chain needs only the cycle step, on works and returns that were already screened (and certified in the smoke run).
   - **FR5:** the spatula chain is not the problem. Its end is jaw −1 on (−1, +1), and the join rule and the #41 library both require jaw −1.
   - Using the existing jaw +1 cycle would need:
     - a jaw +1 spatula chain, a different grasp;
     - new SPAT hub edges;
     - `SIGN` changed in both r19stir2_join.py and r19spill_cycle.py.
2. **Restrict the reach / cycle choice.** Taken for both arms.
   - **UR5e:** chains with jaw −1 whose stroke-0 start is on the spatula end's branch: 2 of 3 screened chains are on the branch, 1 of them with jaw −1.
   - **FR5 at x = 0.55:** no such chain. Stroke 4 has no jaw −1 working part on (−1, +1).
     - r15reach found none at 0.55; it found 12 on FR5 sp20.
     - `r19m2join_seed.py`: all 110 seeds (the start and end states of the other strokes' jaw −1 (−1, +1) working parts) converge to the same IK solution, q1..q5 = −112.8, −54.4, −132.9, −82.3, 117.2°.
     - That solution's forearm elbow hits the upper cabinet (upper_cabinet_1_piece1, also closed door 1_0), with −10 mm reserve.
   - **FR5 cart sweep** (stroke starts on (−1, +1), jaw −1, all 5 strokes):

     | cart x | clear stroke starts |
     |---|---|
     | 0.40, 0.45 | 5 of 5 |
     | 0.50, 0.55, 0.60 | 4 of 5 (stroke 4 hits) |
     | 0.65, 0.70 | 2 of 5 |
     | 0.75 | 0 (plume) |

     0.45 was taken: closest to 0.55 with every start clear, and 1.7 cm from the spatula end at x = 0.467.
3. **An extra wrist re-orientation segment** in or out of the wok. Not needed.

## 3. Method

- **`r19m2join_probe.py`** (read-only): runs `r19stir2_join.self_motion` (unchanged) from the spatula end to every stroke-0 working-part branch of `cycle_<arm>/works.json`.
  - It shows which branch the join can reach: UR5e jaw −1 group 1, FR5 jaw −1 group 1.
  - Output: `results/r19/stir/m2join/probe_<arm>.json`. These were run on the old works.
- **`r19m2join_reach.py`:** filters `r19stir_reach.py one … CARTX=.45` output (r15reach unchanged; the five probes took 97 s) to the candidates with:
  - jaw −1, plume-clear;
  - the spatula end's elbow / wrist branch, and q1 within 90° of the spatula end's q1 (the shoulder);
  - one per distinct labelled IK state (0.5°). r19stir_cycle.groups would merge the rest anyway.
  - This keeps 2 per stroke, out of 115–179 (both jaw senses, all branches).
- **`r19m2join_cycle.py`:** runs `r19stir_cycle.py` from its source with three asserted one-line changes:
  - the cycle's chain list is filtered (KSIGN, BR0, Q1);
  - the output folder and the library file can be redirected (OUTDIR, LIBOUT); the defaults are unchanged.
  - Everything else is the original: follow, returns, certification, time laws, and renaming an existing library to `.replaced_<n>.json`.
- **`r19m2join_join.py`:** `r19mount_stirjoin.py` plus a selectable stir library and output paths (used for the smoke runs). The lane uses `r19mount_stirjoin.py` itself.
- **`r19m2join_spill.py`:** `r19m2_spill.py` plus a selectable base / output / library (used for the smoke runs). The lane uses `r19spill_cycle.py` and `r19m2_spill.py`.
- **`r19m2join_seed.py`:** the seeded stroke-start IK used for the FR5 stroke-4 diagnosis at x = 0.55. It wrote an empty candidate file: `reach_stir_h_scrape_dice_i064_g0.45_cx.55_r19_k48_seeded_fr5_j6_pgc_m2.json`.
- **No shared file edited.**

## 4. Lane (controller, background): `scratchpad/lanes/m2_join.sh`

- It runs the UR5e and FR5 blocks in parallel. Logs go to `results/r19/stir/m2join/logs/`. It ends with `M2_JOIN_DONE`.
- **Before rebuilding, it moves the superseded outputs to `*.bak_r19m2join`:**
  - UR5e: `cycle.json` and `cert_cache.pkl` (copied), the spill folder, and `lib_stir_cycle_ur5e_enc2_pgc_m2_short01_u06_j8000.json`. r19spill_cycle.lib refuses to overwrite an existing library.
  - FR5: the whole `cycle_fr5_j6_pgc_m2/` (old jaw +1 works / returns) and the failed spill folder.
  - The old base libraries are renamed `lib_stir_cycle_<arm>.replaced_<n>.json` by r19stir_cycle itself.
- **Commands** (PYTHONPATH = scratchpad/nowmi):
```
# UR5e
$PY r19m2join_cycle.py cycle ARM=ur5e_enc2_pgc_m2 KSIGN=-1 BR0=-1,1 Q1=-13.6 WORKERS=16
for s in works returns "cert PART=new" "cert PART=old"; do $PY r19spill_cycle.py $s ARM=ur5e_enc2_pgc_m2 WORKERS=16; done
X="SPATCHAIN=results/r19/mount/chain_spatula_s-1_rt_ur5e_enc2_pgc_m2.json HUBSFILE=results/r19/fr5/hub_py.15_ur5e_enc2_pgc_m2/hubs.json"
$PY r19m2_spill.py std ARM=ur5e_enc2_pgc_m2 $X WORKERS=16
for w in .1 .2 .4; do $PY r19spill_cycle.py law ARM=ur5e_enc2_pgc_m2 W=$w; done
$PY r19m2_spill.py lib ARM=ur5e_enc2_pgc_m2 $X; $PY r19m2_spill.py report ARM=ur5e_enc2_pgc_m2 $X
$PY r19mount_stirjoin.py join ARM=ur5e_enc2_pgc_m2 $X WORKERS=16
# FR5 (reach at x .45 and its filtered copy already written)
RF='results/r19/stir/reach/reach_stir_h_scrape_dice_i{i:03d}_g0.45_cx.45_r19_k48_m2join_fr5_j6_pgc_m2.json'
$PY r19stir_cycle.py works ARM=fr5_j6_pgc_m2 REACH=$RF WORKERS=16
$PY r19stir_cycle.py returns ARM=fr5_j6_pgc_m2 REACH=$RF ROUNDS=0 FRESH=1 WORKERS=16
$PY r19m2join_cycle.py cycle ARM=fr5_j6_pgc_m2 REACH=$RF KSIGN=-1 BR0=-1,1 Q1=-94.9 WORKERS=16
(spill stages as for the UR5e, with X="SPATCHAIN=results/r19/mount/chain_spatula_s-1_mnt_fr5_j6_pgc_m2.json", no HUBSFILE)
$PY r19mount_stirjoin.py join ARM=fr5_j6_pgc_m2 SPATCHAIN=results/r19/mount/chain_spatula_s-1_mnt_fr5_j6_pgc_m2.json WORKERS=16
```
- **To regenerate the FR5 reach** (97 s; already done):
```
for i in 0 16 32 48 64; do $PY r19stir_reach.py one stir KEYS=results/r15/stir_h_scrape_dice_keys.json I=$i CARTX=.45 GRIP=.45 TAG=r19_k48 ARM=fr5_j6_pgc_m2 KEEP=48 & done; wait
$PY r19m2join_reach.py ARM=fr5_j6_pgc_m2 CX=.45 SPATCHAIN=results/r19/mount/chain_spatula_s-1_mnt_fr5_j6_pgc_m2.json
```
- **Adopt a file only if its own step printed ok:**
  - the cycle "saved", the spill certificates and std ok, and the lib "saved";
  - the join printing "self-motion … end vs H_stir0" below 1e−4 deg, then "saved".
  - The smoke runs are deterministic replicas, so the lane should print the numbers in §1.

## 5. Files

- **Adopted after the lane** (per arm):
  - `results/r19/stir/lib_stir_cycle_<arm>.json`;
  - `results/r19/stir/cycle_<arm>/` (works, returns, cycle.json);
  - `results/r19/stir/lib_stir_cycle_<arm>_short01_u06_j8000.json` and `results/r19/stir/spill/cycle_<arm>_short01_u06/`;
  - `results/r19/stir/lib_stir_join_<arm>.json` and `results/r19/stir/join_<arm>/`.
  - FR5 only: `results/r19/stir/reach/reach_stir_h_scrape_dice_i*_g0.45_cx.45_r19_k48[_m2join]_fr5_j6_pgc_m2.json`.
- **Smoke (record, not adopted):** `results/r19/stir/m2join/cycle_{ur5e_enc2_pgc_m2,fr5_j6_pgc_m2}_smoke/` and `results/r19/stir/m2join/probe_*.json`.
- **Code:** `r19m2join_probe.py`, `r19m2join_reach.py`, `r19m2join_cycle.py`, `r19m2join_join.py`, `r19m2join_spill.py`, `r19m2join_seed.py`.
- **Superseded:** the UR5e m2 #41 library made at 09:18 (wrong branch; moved to `.bak_r19m2join` by the lane), and the FR5 m2 jaw +1 stir cycle.
