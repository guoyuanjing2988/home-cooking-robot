# R19 #42: the six m2 prep sets that failed their full re-plan, fixed by motion (Windows, 2026-10-14)

Checking standard as `R19_MOUNT.md`: the pot-zone layer (`RACK=keyed SPX=1.56 SPY=.20`), gates 10 mm robot↔environment, 5 mm gripper/held↔environment, 0 mm self, states ≤ 4 mm apart, joint step ≤ 10° in planning. The checker, gates, fixtures, objects and the m2 mount are unchanged.
Labels: **[M]** measured in the sim, **[S]** sourced, **[E]** estimate or design choice. No git, no GitHub, no purchases, no browser.

## 0. Answer first

**All six are fixed by motion alone and certified at smoke level** [M]: each smoke plan is `ok`, and its ≤ 4 mm re-check has 0 hit states.

| Set | Arm | Fix (argv) | Smoke result | ≤ 4 mm re-check | Action time (old → new) |
|---|---|---|---|---|---|
| basket | UR5e | `TAPY=.30 TAPZ=.90`: the basket under the tap 3 cm forward, 4 cm lower | ok | 4,567 states, 0 hits, min reserve 2.0 mm | 34.6 → 34.9 s |
| basket | FR5 | the same, on top of its fr5xfull argv | ok | 2,569 states, 0 hits, 2.02 mm | 32.9 → 33.3 s |
| tubempty | UR5e | `EY=.28 EZ=.92` (the emptying pose 3 cm forward, 3 cm lower), plus IK seeds from the certified m2 tubfill (`SEEDUR`) | ok | 4,089 states, 0 hits, 1.8 mm | 23.9 → 23.1 s |
| ct2s | UR5e | `CYAW=35` (new override `r19m2fix_ct2s.py`: the tray turned 35° about the vertical at the pour), and the lane cart free (no `LANEC`) | ok | 4,173 states, 0 hits, 2.0 mm | 26.8 → 28.9 s |
| ct2s | FR5 | `CYAW=10` | ok | 4,978 states, 0 hits, **0.36 mm** (thin) | 29.7 → 30.2 s |
| tomato | FR5 | the R19_FR5_PREP3 argv unchanged, with IK seeds from the exact m2 re-target (`r19mount_seed.py`) | ok | 3,122 states, 0 hits, 2.23 mm | 38.5 → 35.4 s |

- The approaches and retreats of every set re-checked with 0 hits too.
- **The full-setting runs** (SEEDS=3 TRIES=12 KEEP=4) and their re-checks are in the lane script `scratchpad/lanes/m2_fix.sh` (§3).
- **Not covered: the cable.** No m2 cable options exist yet (#36), so none of these files is cable-checked. The old UR `ct2s_c3` had been chosen for its cable result.

**Environment finding (affects every running lane).** The Windows WMI service stopped answering on 2026-10-14. `Get-CimInstance` and `tasklist` both hang.
- Python 3.12+'s `platform.machine()` asks WMI first. `numpy.testing` calls it on import, and `scipy.linalg` imports `numpy.testing`.
- So **every new Python process that imports scipy blocks until WMI answers** [M]: faulthandler stack in `platform._wmi_query`.
- Lane 1's ct2s re-check is a "skipped" no-op, yet it ran from 06:56 to 08:33.
- **Workaround, no system change:** `scratchpad/nowmi/sitecustomize.py` makes the WMI query raise `OSError`, so `platform` takes its own documented fallback. Put that folder on `PYTHONPATH` (children inherit it).
  - With it, `import scipy.linalg, kitchen16` takes 0.8 s; without it, more than 200 s.
  - `m2_fix.sh` exports it.
  - The lanes already running do not have it.

## 1. Causes [M]

All causes were found with `r19m2fix_probe.py`. It runs the planner's own source up to its anchors loop, then for one anchor prints the 96-start IK status, the most frequent hit pairs, and each candidate's follow to both sides.

**basket, both arms: "under the tap" has 0 IK candidates.**
- The knob is grasped pitched 30° down, approach about (−0.81, 0.30, −0.5) in the world.
- m2 puts the flange 94 / 77 mm further back along that axis. On the UR5e that is about 47 mm up and 76 mm toward +x [M, geometry], into the closed door over the sink.
- UR5e hits: upper arm `ua_4` vs `r07_closed_door_1_0` / `upper_cabinet_1` / `counter_right`.
- FR5 hits: wrist 2 vs door 1_0; the elbow vs counter / sink; the forearm vs the gripper housing.
- These did not fix it:
  - the cart alone (`XTAPC=−0.15` / `+0.10`; lane 1's xt15 agrees): still 0 candidates;
  - `TAPZ=.90` alone or `TAPY=.30` alone: fails on the follow (wrist 2 vs door).
- With both `TAPY=.30` and `TAPZ=.90`, the FR5 had 3 of 3 candidates through both sides and the UR5e 1 of 3.

**tubempty, UR5e.**
- Pick and return ("lifted → lane", "over its spot → lane"): forearm vs `upper_cabinet_1`.
- Emptying ("over the sink → rolled"): forearm vs door 1_0.
- A lower or more forward lane did not help:
  - `BLANE` z .93 / .94 / .95 still hit the cabinet;
  - y .30 puts the held tub into the basket on the front spot.
- **Why the seeds work:** the m2 tubfill (pick, lifted and lane keyframes identical to tubempty's) passed as an exact re-target. Its states as IK seeds put both tub anchors on the passing branch.
- `EY=.28 EZ=.92` clears the door at the roll (1 of 3 candidates in the probe).

**ct2s, UR5e: reach.**
- At the pour (cart −0.52, the pan riding on the folded cradle), the shoulder is at (−0.52, −0.074, 1.273) and wrist 3 at (−1.04, −0.774, 1.247).
- That is 0.87 m horizontally, against the UR5e's 0.85 m reach. The 120° roll fails on orientation error (pose error 0.4–1.8 mm, no hits).
- **With the fixed lane cart (`LANEC=−.52`), "over the pan → lane" also jumps 17.2° at every candidate.**
- Turning the tray brings the wrist in:

| CYAW | UR5e (over the pan, both sides) | FR5 |
|---|---|---|
| −90 | 0 IK (out of reach) | 0 IK |
| −45 | not tried | 0 IK |
| 0 (as before) | roll: orientation error | roll: forearm vs gripper housing |
| 10 | — | **2 of 4 through** |
| 20 | 2 of 4 | roll: pose error 2.8 mm |
| 35 | **4 of 4** | roll: forearm vs gripper / wrist 2 |
| 45 | all 3 printed passed | roll: forearm vs wrist 3 |
| 60 / 90 / 180 | base plate, cart beam, door, or > 10° | same |

- **FR5 also tried, without success:**
  - `CDEG=−120` (roll the other way): 0 IK at yaw 0;
  - −120 at yaw 20, 35, 45: > 10° jumps or self-hits;
  - `MOUTHZ=.20`: 0 IK.

**tomato, FR5.**
- The exact re-target fails only on 3 states: joint steps of 10.3–12.2° between "level" and "backed out" (the source had 9°).
- A re-plan with the PREP3 argv and the UR5e seeds fails at "under the tap": 25 candidates, all through forearm vs wrist 2, or upper arm vs cabinet.
- **Seeded with the re-target's own states, the same argv passes.**

## 2. Costs [M unless marked]

- **basket.** The basket floor under the spout moves from (−0.40, .33, .94) to (−0.40, .30, .90).
  - The stream now lands 7 cm behind the basket centre instead of 4, inside the Ø200 basket.
  - With the ±4 cm rinse sweep it stays at least 1.9 cm inside the wall.
  - The rim is 10 cm under the spout instead of 6.
  - The basket is still over the basin centre (basin x −0.70…−0.10, y .08….52).
  - Rinse coverage of the front half is not modelled [E]; no rinse dwell here is sourced anyway.
  - The drain and shake poses move with the tap pose (they are defined relative to it).
- **tubempty.** The emptying pose moves to (−0.55, .28, .92).
  - The tub (R .117) stays inside the basin footprint: x −0.67…−0.43, y .16….40.
  - The pour leaves the same side of the tub as before, 3 cm further forward and lower [E: the water's path is not modelled].
- **ct2s.**
  - The tray is turned about the vertical: 35° (UR5e) or 10° (FR5). The mouth stays on the same point, 12 cm over the pan centre, and the 120° roll is unchanged. The food still drops onto the pan centre; only the mouth edge is turned [E].
  - UR5e: the lane cart is now free, so the meets need cart shuffles where `LANEC` gave 0° joins. +2.1 s.
  - FR5: min reserve 0.36 mm. That is above the gate, but thin.
- **tomato.** No change in task space: the keyframes are the adopted FR5 tomato's. −3.1 s.

## 3. Lanes

**Smoke runs already done.** Commands as in §0, through `r19mount_run.py`; each ran in under 3 minutes.
- Re-checks:
  - `r19prep_verify.py FILE=… NPROC≤6` for basket, tubempty and tomato;
  - `r19prep5_verify.py … $POT` for ct2s.
- Logs: `results/r19/mount/logs/fixs*_*.txt`.

**Full settings: `scratchpad/lanes/m2_fix.sh`** (controller, background, about 15–30 min).
- Two parallel groups, UR5e then FR5. Each runs its three sets at SEEDS=3 TRIES=12 KEEP=4, TAG `fix`.
- Then the ≤ 4 mm re-checks with NPROC=8.
- It ends with `M2_FIX_DONE`. It exports the WMI shim.

```bash
D=results/r19/mount; P=results/r19/prep; CT="ACT=ct2s CP=-.52 PLUME=0 MOUTHZ=.12 CLANE=-0.954,-.16,1.12 SEEDS=3 TRIES=12 KEEP=4"
$PY r19mount_run.py RUNNER=r19fr5prep_actions.py ACT=basket SEEDS=3 TRIES=12 KEEP=4 BYAW=-20 BPITCH=30 TAPY=.30 TAPZ=.90 SEEDUR=$P/chain_basket_y20p30_ur5e_enc2_pgc.json ARM=ur5e_enc2_pgc_m2 TAG=fix
$PY r19mount_run.py RUNNER=r19fr5prep_actions.py ACT=tubempty SEEDS=3 TRIES=12 KEEP=4 EY=.28 EZ=.92 SEEDUR=$D/chain_tubfill_rt_ur5e_enc2_pgc_m2.json ARM=ur5e_enc2_pgc_m2 TAG=fix
$PY r19mount_run.py RUNNER=r19m2fix_ct2s.py $CT CYAW=35 ARM=ur5e_enc2_pgc_m2 TAG=fix
$PY r19mount_run.py RUNNER=r19fr5prep_actions.py ACT=basket SEEDS=3 TRIES=12 KEEP=4 BYAW=-20 BPITCH=30 TAPY=.30 TAPZ=.90 XD=0,-.06,.02 XTAPC=-0.25 "XCART=pick:-0.55;over the tub:-0.55" SEEDUR=$P/chain_basket_y20p30_ur5e_enc2_pgc.json ARM=fr5_j6_pgc_m2 TAG=fix
$PY r19mount_run.py RUNNER=r19m2fix_ct2s.py $CT CYAW=10 ARM=fr5_j6_pgc_m2 TAG=fix
$PY r19mount_run.py RUNNER=r19fr5prep_actions.py ACT=tomato SEEDS=3 TRIES=12 KEEP=4 SEEDUR=$D/seed_chain_tomato_rt_fr5_j6_pgc_m2.json XL1=-0.65,.06,1.10 XL1R=level LVC=-0.25 L2C=-0.25 "XCART=pick:-0.90" ARM=fr5_j6_pgc_m2 TAG=fix
# then r19prep_verify.py (basket, tubempty, tomato) / r19prep5_verify.py ... $POT (ct2s) on each chain_*_fix_*.json
```

**Adoption rule.** Adopt the `fix` file where the run is `ok` and its re-check is `ok`. Otherwise keep the certified smoke file below.

## 4. Files

**Adopted now (smoke level, certified)** in `results/r19/mount/`, each with its re-check file (`_verify4mm.json`, or `_verify4mm_pot.json` for ct2s):
- UR5e:
  - `chain_basket_fixs1_ur5e_enc2_pgc_m2.json`
  - `chain_tubempty_fixs2_ur5e_enc2_pgc_m2.json`
  - `chain_ct2s_fixs2_ur5e_enc2_pgc_m2.json`
- FR5:
  - `chain_basket_fixs1_fr5_j6_pgc_m2.json`
  - `chain_ct2s_fixs1_fr5_j6_pgc_m2.json`
  - `chain_tomato_fixs2_fr5_j6_pgc_m2.json`

**Kept for the record, not adopted:**
- `chain_ct2s_fixs1_ur5e…`: KEEP=2, no consistent join pair.
- `chain_tubempty_fixs1_ur5e…`: default emptying pose.
- `chain_tomato_fixs1_fr5…`: UR5e seeds.
- `chain_basket_fixs2_ur5e…`: plus `XTAPC=−0.15`; ok but not needed, not re-checked.
- `chain_basket_fixs3/fixs4_ur5e…`: cart only.
- `chain_basket_fixs2_fr5…`: `TAPZ` only.

**Seeds:**
- `seed_chain_tomato_rt_fr5_j6_pgc_m2.json`, from `r19mount_seed.py`.
- `seed_tomato_rt_fr5_j6_pgc_m2.json` is the same play (max |Δ| = 0). It was written by a duplicate tool, since removed, and is the file named in the tomato smoke's argv.

**New code (no shared file edited):**
- `r19m2fix_probe.py`: the per-anchor diagnostics.
- `r19m2fix_ct2s.py`: the `CYAW` override, run as r19prep5_chain.py's source with one line changed. Without `CYAW` the keyframes are r19prep5_actions' exactly.

**Environment shim:** `scratchpad/nowmi/sitecustomize.py`, outside the repo.
