# R19 spill: why the arm stir throws dice over the far rim, and a cycle that does not (2026-10-14, GitHub #41)

Labels: **[M]** measured in the sim, **[E]** estimate or inference, **[S]** sourced.
Checking standard: `ARM=ur5e_enc2_pgc PY=.15` and `ARM=fr5_j6_pgc_sp20 PY=.15`; current layout `RACK=keyed SPX=1.56 SPY=.20`.
Gates unchanged: 10 mm robot↔environment, 5 mm gripper/held↔environment, states ≤ 4 mm apart, plume (arm ≥ 0.20 m from the wok axis).
Food model, friction, masses, piece count, wok and spill definition: untouched. `r19stir2_phys.py`, `stirbench.py` and `results/r15` were not edited. No git.

## Answer first

**Diagnosis.**
- **Start-up transient.** The spill happens in the first two strokes (the two centre strokes, patterns 0 and 1), which bulldoze the freshly dropped heap into the far wall. The heap front goes over the rim near the end of the push, while the blade edge is still about 9–10 cm short of the rim.
  - Of 41 spilled pieces in 24 arm runs [M]:
    - 39 leave in strokes 0–1 and 2 in stroke 2;
    - all 41 leave during a working part, at bench time 0.85–1.19 s (the push reaches the far wall at 1.08 s);
    - **none** had touched the spatula in the 0.5 s before crossing.
  - The bench does the same, at a lower rate: 9 pieces in 13 runs, all in strokes 0–1 [M].
- **The three suspects are not the cause [M].**
  - UR5e stroke 4: 0 of the 50 spilled pieces left in stroke 4. The FR5 has no stroke-4 offset and spills as much.
  - Far-wall blade speed: the arm is never faster than the bench there. Making it slower makes the spill *worse*: 18 vs 7 pieces on 8 seeds.
  - Blade tilt and attack: on strokes 0–3 the arm's commanded blade is the bench pose to within 0.22 mm and 0.1°.
- **The arm-vs-bench gap is real but noisy.**
  - On 8 seeds (full 12 s) the old j8000 cycles spill 11 (UR5e) and 12 (FR5) pieces, against 5 for the bench [M].
  - The heap is chaotic: a 0.04 % change of the bench period turns the bench's seed-3 result from 1 into 2 or 0 [M]. Seeds 1–3 alone cannot rank drivers.
  - No single part of the arm motion reproduces the excess (§1.4). The likely contributor is the arm's slower push at the stroke starts and at the far-wall turn (ṡ dips to about 0.4–0.8 under the jerk-8,000 laws), consistent with the sandbox result that a slower push near the far wall raises the far-wall load [E].

**Fix (motion only).** In the two centre strokes, the push now ends at **u = 0.06 m instead of 0.10 m**: the blade lifts off 4 cm earlier. Start pose, handle elevation (62° → 38° over the push), lift (5 + 1.5 cm, 4 cm back) and bench timing are unchanged, and strokes 2–4 are unchanged.
- Implemented on both arms as a **new periodic C2 cycle** with **the jerk-8,000 law kept**:
  - new IK working parts 0 and 1;
  - three new quintic returns;
  - the other five segments are the stored #3 B-splines, unchanged.
- **Re-certified at ≤ 4 mm**, in the stir scene and in the current layout: 0 hits, 0 out of range, plume ≥ 29.0 mm [M].
- Stored as new entries: `results/r19/stir/lib_stir_cycle_<arm>_short01_u06_j8000.json`.

**Numbers [M], full 12 s.**

| Seeds 1–3 | Spilled | Hot share r 0.09 | Never hot | Flips / 10 s |
|---|---|---|---|---|
| R15 bench | 0 / 0 / 1 | 0.448 / 0.418 / 0.436 | 15 / 15 / 19 | 3.19 / 4.22 / 3.11 |
| UR5e #3 j8000 | 0 / 0 / 6 | 0.423 / 0.427 / 0.446 | 20 / 19 / 12 | 3.47 / 3.94 / 4.51 |
| **UR5e new** | **0 / 0 / 0** | 0.436 / 0.431 / 0.444 | 16 / 17 / 15 | 2.44 / 2.07 / 2.51 |
| FR5 #3 j8000 | 0 / 2 / 3 | 0.427 / 0.421 / 0.432 | 14 / 16 / 18 | 3.51 / 4.22 / 4.48 |
| **FR5 new** | **0 / 0 / 0** | 0.418 / 0.438 / 0.431 | 17 / 16 / 14 | 1.93 / 2.53 / 2.88 |

| Seeds 1–8 | Spilled, total (runs with a spill) | Hot share, mean (range) | Never hot, mean | Flips / 10 s, mean |
|---|---|---|---|---|
| R15 bench | 5 (4 of 8) | 0.436 (0.418–0.448) | 16.5 | 3.54 |
| UR5e #3 j8000 | 11 (4 of 8) | 0.441 | 15.9 | 3.40 |
| **UR5e new** | **0 (0 of 8)** | 0.447 (0.425–0.467) | 16.2 | 2.02 |
| FR5 #3 j8000 | 12 (5 of 8) | 0.425 | 16.2 | 3.74 |
| **FR5 new** | **0 (0 of 8)** | 0.436 (0.418–0.452) | 16.1 | 2.21 |

- **Target met on seeds 1–3, and on all 8 seeds.** Spills are 0, against the bench's 0/0/1. Mixing (hot share) and never-hot are within the bench's spread.
- **Trade-off.** Flips fall by about 40 %, to 2.0–2.2 per 10 s, because less of the heap is shoved up the wall and tumbles back. The sandbox shows the same drop when the short push is used in the first cycle only (§2.1).
- **Period.** 2.806 s per stroke (UR5e) and 2.645 s (FR5), against 2.788 / 2.619 s for the old j8000 entries (+0.6 % / +1.0 %).
- **Few seeds.** All of this rests on 8 seeds per driver. Seeds 1–3 were run by me in chunks; the controller lanes (§5) repeat them unchunked and should give identical numbers.

## 1. Diagnosis

### 1.1 Instrumentation (new wrappers, `r19stir2_phys.py` not edited)

- **`r19spill_trace.py`** runs `r19stir2_phys.py` unchanged, apart from one path replacement (OUTD → `results/r19/stir/spill`). Every 10 ms, after the step, it reads:
  - all 90 piece positions and velocities;
  - which pieces touch the spatula;
  - the spatula body pose and velocity;
  - the commanded (mocap) pose.

  Reading the state does not change the integration. The traced runs equal the #40 runs metric for metric [M]:
  - bench s1–3;
  - UR5e s1–3, j8000 s3;
  - FR5 s3, FR5 j8000 s3.

  The only difference is the UR5e s1 `arm_law` metadata.
- **`r19spill_drive.py`** overrides the mocap target inside the step wrapper, to drive counterfactuals:
  - splices of arm and bench parts;
  - time warps of the bench;
  - modified bench keyframes.

  Its `MODE=arm` reproduces the arm driver **bit for bit** [M].
- **`r19spill_ana.py`** analyses the traces: per-piece rim crossings, far-wall load, blade-vs-bench deviation, and pile maps.

### 1.2 When, where and how pieces leave [M]

`results/r19/stir/spill/agg_arms_orig.json` and `agg_bench.json`. Arm runs: seeds 1–3 (#40, traced), seeds 4–11 strokes 0–1, and j8000 seeds 4–8 full, for both arms.

| | Arm runs (24) | Bench runs (13) |
|---|---|---|
| Spilled pieces | 41 | 9 |
| In strokes 0–1 / stroke 2 / stroke 4 | 39 / 2 / **0** | 9 / 0 / 0 |
| In a working part / in a return | 41 / 0 | 9 / 0 |
| Bench time at the rim crossing | 0.85–1.19 s (push ends at 1.08 s) | 1.02–1.15 s |
| Over the far side (azimuth 30–150°) | 41 | 9 |
| Touched the spatula in the 0.5 s before | **0** | **0** |
| Piece speed at the crossing / commanded blade speed | 0.05–0.54 / 0.07–0.23 m/s | 0.08–0.34 / 0.12–0.21 m/s |

**The worst case, UR5e #3 seed 3** (9 pieces, `ana_tr_ur5e_s3.json`; timeline in `r19spill_ana.py timeline`):
- All 9 pieces cross in stroke 1 (pattern 1, yaw 30°), at bench time 0.94–1.15 s, azimuth 96–127°, z ≈ 0.105 m (1 cm above the rim).
- At bench time 1.03 s, 39 pieces are beyond r 0.13 m, against 13 on the bench at the same blade pose. The heap front reaches the rim while the blade edge is at r ≈ 0.065–0.08 m.
- The pieces that go over are bottom-layer dice. At the start of stroke 1 they sat mid-swath, 7–9 mm above the steel.
- The heap is bigger on the arm because the bench lets about 18 pieces escape sideways around the blade in that stroke, and the arm none. The blade states are the same (§1.3).

### 1.3 The suspects [M]

**Blade pose.** On strokes 0–3 the arm's commanded blade is the bench pose at the same bench time to within 0.22 mm (along / across / height) and 0.1° (roll, pitch, yaw). This holds for both arms and both laws (`dev_s3.json`).
- UR5e stroke 4: up to 15.2 mm across and 2.15° roll (the smoothed spline, as #40 found).
- No spilled piece in any run left during stroke 4. The FR5 (0.0 mm) spills as much as the UR5e. So stroke 4 was left unchanged.

**Blade speed at the far wall.** The working parts run at ṡ ≤ 1 (never faster than the bench). Around the far-wall turn (bench time 1.0–1.2 s), ṡ is:

| Law | Work 0 | Work 3 | Work 4 |
|---|---|---|---|
| UR5e #3 | 0.80–0.94 | — | 0.63–0.97 |
| UR5e j8000 | 0.56–0.72 | 0.65–0.78 | 0.44–0.79 |
| FR5 #3 | — | — | 0.61–0.83 |
| FR5 j8000 | 0.87 | — | 0.61–0.74 |

Elsewhere ṡ is about 0.98. A slower blade does *not* reduce the spill:
- **Bench geometry slowed to 0.4× over bench time 0.75–1.25 s** (`MODE=bwarp`, strokes 0–1): 18 pieces on 8 seeds, against 7 for the bench on the same seeds.
- **The whole bench 25 % slower** (`PERIOD=3.0`): 9 vs 7.

**Blade attitude.** Identical within 0.1° (above). The attack angle runs 13° → 43° over the push, as on the bench.

### 1.4 Why the arm differs: chaos plus a small systematic excess

- **Chaos [M].** The bench seed 3 at PERIOD 2.399 / 2.4 / 2.401 spills 2 / 1 / 0.
- **Strokes 0–1, seeds 4–11 [M].** The bench spills 6 and the UR5e #3 cycle 6. The far-wall load (sum of pieces beyond r 0.15 m) is 67 vs 70.
- **Full 12 s, seeds 1–8 [M].**
  - The old j8000 cycles spill 11 and 12 pieces against the bench's 5.
  - Among the nominal drivers, big events (≥ 4 pieces) only occur on the arm laws: UR5e seed 3 with 9 (#3) and 6 (j8000). A 25 % slower bench also had one (5 pieces, seed 3).
- **Splice tests on seeds 1–3** (to t 5.8 s, `MODE=bret` / `aret` / `bench RAMP=1`):

  | Splice | Spilled, s1 / s2 / s3 |
  |---|---|
  | Arm works + bench returns | 0 / 4 / 0 |
  | Bench works + arm returns | 0 / 5 / 0 |
  | Bench with the arm's start-from-rest ramp | — / — / 0 |

  No single component (work timing, return geometry and timing, entry ramp) carries the excess.
- **Conclusion [E].** The excess comes from small timing differences acting on a chaotic heap. The slower push at the hand-offs and at the far-wall turn is the most plausible contributor (§1.3). That is why the fix removes the mechanism instead of tuning the timing.

## 2. Fix

### 2.1 Choice, in the bench sandbox [M]

Bench geometry and timing with stirbench's own keyframes rebuilt (`MODE=bkeys`; identical to the R15 export when unmodified).

| Variant | Spilled | Hot share r 0.09 | Flips / 10 s |
|---|---|---|---|
| Push of strokes 0–1 to u = 0.06 m, strokes 0–1 only, 8 seeds | 0 on 8 seeds; far-wall load 0–2 (bench 2–14) | — | — |
| **Patterns 0/1 push to 0.06 m every cycle (chosen), seeds 1–3, 12 s** | **0 / 0 / 0** | 0.444 / 0.444 / 0.434 | 1.97 / 2.65 / 2.94 |
| Patterns 0/1 push to 0.08 m every cycle, seeds 1–3, 12 s | 0 / 1 / 1 | 0.423 / 0.436 / 0.433 | — |
| First two strokes only to 0.06 m, seeds 1–3, 12 s | 0 / 0 / 0 | 0.445 / 0.448 / 0.424 | 2.01 / 2.53 / 3.38 |

- The periodic variant was chosen: it is a plain `STIR_CYCLE` entry with the same format, hub and driver.
- The startup-only variant needs a non-periodic entry and would not recover the flips.
- 0.08 m is not short enough.

### 2.2 The new cycle (`r19spill_cycle.py`)

**Keyframes.** `results/r19/stir/spill/keys_short01_u06.json`: stirbench `keyframes()` with U1 = 0.06 m for patterns 0 and 1. Checked: with U1 = 0.10 it equals the R15 export exactly, and it equals the sandbox keys [M].

**Working parts 0 and 1.**
- Method: `r19stir_cycle.follow`, unchanged gates:
  - 10 ms IK steps, pose ≤ 5 mm / 3°;
  - fast check every step, full check every 25th, plume every step.
- Started from the stored cycle's own start states: same IK branch, same 2π labels, so H_stir0 is unchanged.
- Both arms [M]:
  - pose error < 0.001 mm;
  - no joint on a limit (interpolating quintics);
  - blade reserve 2.2 mm;
  - plume margin 63 mm (it was 25.8 mm at u = 0.10).

**Returns 4 → 0, 0 → 1, 1 → 2.**
- C2 quintics (`r19stir_cycle.ret_A`), with q, q′, q″ matched to both working parts.
- Screened cheapest first, without vias, then the 16 via sets (none was needed).
- Taken (in the order 4 → 0, 0 → 1, 1 → 2): T = 0.3 / 0.3 / 0.3 s (UR5e) and 0.2 / 0.3 / 0.3 s (FR5), no via. Each certified at its first option.

**Reused, unchanged.** work2, return2→3, work3, return3→4, work4 (the stored B-splines; the UR5e work 4 is the range-safe smoothing spline).

**Certificate [M].**
- Method: every segment, new and reused, cut at ≤ 4 mm (`r19stir_cycle.certify`), then `Checker.check(full=True)` + `r19enc_check.one` + the plume rule.
- The stir-scene model md5 equals the #3 certificates' (`arms.py` was edited by the cable agent during this session, but only for the `…c` cable variants).

| | UR5e | FR5 |
|---|---|---|
| States (≤ 4.0 mm) / hits / out of range | 4,547 / 0 / 0 | 4,039 / 0 / 0 |
| Held/gripper vs environment, self | 2.0 / 2.0 mm | 2.0 / 2.0 mm |
| Robot vs environment | 21.6 mm (forearm vs hood) | 10.0 mm (forearm vs door 1, the reused return 3→4, as #3) |
| Plume margin / violations | 29.0 mm / 0 | 29.0 mm / 0 |
| **Current layout** (`r19stir2_join` scene `std`: PY .15, keyed rack, spider rest (1.56, .20), held spatula_b; relabel J2 −1 turn (UR5e) / J6 −1 turn (FR5), as #40) | 4,547 states, 0 hits, 0 out of range, plume 29.0 mm | 4,039 states, 0 hits, 0 out of range, plume 29.0 mm |

**Continuity [M]** (`report.json`, from the library JSON alone): the jump in q, q′ and q″ at every hand-off and around the cycle is 0.000000. Joint-range margin ≥ 0 everywhere; the UR5e work 4 touches the elbow limit by construction (−160° + h²).

**Time law: the #40 jerk-8,000 law, kept.**
- Method: `r19stir2_law.timelaw`, as `r19stir2_retime.law`:
  - periodic, 3 cycles unrolled;
  - ṡ ≤ 1 on the working parts;
  - datasheet speeds, A = min(800, J·W/2);
  - fastest of W = 0.1 / 0.2 / 0.4 s.
- Solved at 0.95·J. At 0.99·J the independent check exceeded J by 4 % (UR5e), but only at the two one-sided-difference ends of the stored period; in the law itself the peak was 7,875 °/s³.

| | UR5e | FR5 |
|---|---|---|
| W / A | 0.1 s / 400 °/s² | 0.2 s / 800 °/s² |
| Per stroke | **2.806 s** (old j8000: 2.788) | **2.645 s** (old: 2.619) |
| Per segment (s) | 2.182 / 0.496 / 1.989 / 0.515 / 1.966 / 0.629 / 2.142 / 0.751 / 2.634 / 0.726 | 2.240 / 0.494 / 2.024 / 0.450 / 2.091 / 0.573 / 2.046 / 0.465 / 2.245 / 0.595 |
| Independent check (`r19stir2_retime.check`): speed / acceleration / jerk ratio | 0.747 / 0.991 / 0.985 | 0.904 / 0.867 / 0.979 |
| Geometry md5 = certificate md5 | yes | yes |

### 2.3 Library entries (new; nothing overwritten)

- `results/r19/stir/lib_stir_cycle_ur5e_enc2_pgc_short01_u06_j8000.json` (md5 cd77e3e6716900b457a8f24a15d03e64).
- `results/r19/stir/lib_stir_cycle_fr5_j6_pgc_sp20_short01_u06_j8000.json` (md5 933e0d66d0a04be6738ea439e59443ee).

Same format as the #40 `_j8000` entries: `STIR_CYCLE`, hub H_stir0 (the same state as #3, so the #40 join still lands on it), geometry (10 B-splines), `time_law` (one period, 2 ms grid), states, certificate (stir scene and current layout), `derived_from` (#3 entry and its md5).

From-rest law for the physics driver: `results/r19/stir/spill/cycle_<arm>_short01_u06/fromrest_j8000.npz`.

## 3. Verification [M]

- All 16 new-cycle runs (2 arms × seeds 1–8) were run to the full 12 s through the unchanged arm driver (`r19stir2_phys.py DRIVER=arm LIB=… LAWNPZ=…`), traced and chunked with exact checkpoints. **0 pieces spilled in 16 of 16 runs.**
- If the cycles still spilled at the bench's rate (a spill in 4 of 8 runs), 0 of 8 per arm would have about a 0.4 % chance [E].
- Far-wall load in strokes 0–1 (sum of pieces beyond r 0.15 m), UR5e seeds 1–8: 0–4 (new) against 0–26 (#3). Nearest miss: FR5 seed 3, stroke 3 (pattern 3, unchanged), with 3 pieces beyond r 0.16 m and none over.
- **Spatula load.** On seeds 1–7 the typical load stays in the old cycles' range. Seed 8 is a jam case for every driver, and the new FR5 cycle is the worst there. #40's force-limited / keyed-block requirement stands.
  - Seeds 1–3: p95 force 7.6–9.5 N; jam samples (> 30 N) 2–9 per run, against 2–11 for #3 j8000.
  - Seeds 1–7, p95 grip moment: 2.2–3.5 N·m (new, both arms), against 2.4–3.6 for the old j8000 cycles and 2.2–3.7 for the bench.
  - **Seed 8** has a large jam event on every driver, the bench included: peak force 930–980 N, 24–66 samples above 30 N. Its sustained load (p95 grip moment) is 17.3 N·m (FR5 new), 10.3 (FR5 #3 j8000), 8.3 (UR5e new), 6.9 (UR5e #3 j8000) and 2.5 (bench), against the PGC-140's 7 N·m. In the bench and old runs the blade edge then barely touches the steel (edge-on-steel p95 0 N); in the new runs it does (18–20 N). I did not investigate this further: it is a load question, not a spill one.
- `arm_law.works_vs_bench_max_mm` in the new runs reads 43.6 mm. That is by design: works 0 and 1 now follow the shortened push, and the diagnostic compares them with the original bench path.

## 4. Checked / not checked

**Checked:**
- The cause, by per-piece traces and counterfactual drivers (§1).
- The new cycle's geometry at ≤ 4 mm with the plume rule, in the stir scene and in the current layout; C2 continuity; joint ranges.
- The jerk-8,000 law, with the independent re-check.
- The physics at 12 s on seeds 1–8 for both arms.

**Not checked / open:**
- Only 8 seeds per driver; seeds 9–11 only for the old cycle, strokes 0–1.
- One food type and size (90 rigid 15 mm dice), as R15. A deeper or larger load may need a shorter push still.
- **Flips per 10 s fall by about 40 %** (2.0–2.2, against 3.4–3.7 for the arms and 3.5 for the bench). Every driver leaves some piece unflipped (min 0). Whether this matters for cooking needs heat modelling, which `stirbench` does not have.
- The UR5e stroke-4 offset (15.6 mm) is kept: it does not cause spill.
- **The seed-8 jam (§3).** Sustained grip moment above the PGC's 7 N·m on both FR5 cycles and on the new UR5e cycle; worst on the new FR5 cycle (17.3 N·m p95). Not investigated.
- Real controller tracking, jerk and acceleration limits, as #40 (8,000 °/s³ is an assumption [E], not a datasheet value).
- **Observation.** The stored `lib_stir_cycle_fr5_j6_pgc_sp20_j8000.json` re-checks at a jerk ratio of 1.018 with the same independent check, at the period ends. It is not mine and was not changed (R19_STIR2's lane 1 would recompute it).

## 5. Controller lanes

```bash
cd /c/Users/admin/Documents/YJGames/robot_rail/sim/r10/claude
PY=C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe
D=results/r19/stir/phys; S=results/r19/stir/spill
# lane 1 (~10-12 min, 6 runs in parallel): full 12 s, seeds 1-3, both arms, the new cycle (spill fix, jerk 8,000)
for A in ur5e_enc2_pgc fr5_j6_pgc_sp20; do for SD in 1 2 3; do
 $PY r19stir2_phys.py DRIVER=arm ARM=$A LIB=results/r19/stir/lib_stir_cycle_${A}_short01_u06_j8000.json LAWNPZ=$S/cycle_${A}_short01_u06/fromrest_j8000.npz SEED=$SD TAG=full_arm_${A}_short01_u06_j8000_s$SD > $D/log_${A}_short01_u06_j8000_s$SD.txt 2>&1 &
done; done; wait
# lane 2 (~5 s): the table (bench, #3 j8000, new; seeds 1-3) and the comparison with my chunked runs of the same seeds (expect IDENTICAL; wall time excluded)
$PY r19spill_ana.py table
$PY r19spill_ana.py repro PAIRS='{"nw_ur5e_s1":"full_arm_ur5e_enc2_pgc_short01_u06_j8000_s1","nw_ur5e_s2":"full_arm_ur5e_enc2_pgc_short01_u06_j8000_s2","nw_ur5e_s3":"full_arm_ur5e_enc2_pgc_short01_u06_j8000_s3","nw_fr5_s1":"full_arm_fr5_j6_pgc_sp20_short01_u06_j8000_s1","nw_fr5_s2":"full_arm_fr5_j6_pgc_sp20_short01_u06_j8000_s2","nw_fr5_s3":"full_arm_fr5_j6_pgc_sp20_short01_u06_j8000_s3"}'
```

Expected from my chunked runs: spilled 0/0/0 for both arms; hot share 0.436/0.431/0.444 (UR5e) and 0.418/0.438/0.431 (FR5).

## 6. Files (all new; no existing file changed)

**Code:**
- `r19spill_trace.py`: traced runs of `r19stir2_phys.py`.
- `r19spill_drive.py`: counterfactual drivers.
- `r19spill_ana.py`: analyses and controller table.
- `r19spill_cycle.py`: keys, works, returns, cert, std, law, lib, report.

**Library entries:** `results/r19/stir/lib_stir_cycle_ur5e_enc2_pgc_short01_u06_j8000.json`, `results/r19/stir/lib_stir_cycle_fr5_j6_pgc_sp20_short01_u06_j8000.json`.

**Results:** `results/r19/stir/spill/` (about 230 MB):
- `keys_short01_u06.json`;
- `cycle_<arm>_short01_u06/`: `works.json`, `returns.json`, `cert_new.pkl`, `cert_old.pkl`, `std_recheck.json`, `law_j8000_w*.{npz,json}`, `fromrest_j8000.npz`, `cycle.json`, `report.json`, logs;
- `check_short01_u06.json`;
- the run results `stir2_*.json`;
- analyses: `far_*`, `agg_*`, `pile_s3`, `dev_s3`, `ana_*`, `diag_*`;
- traces `trace_*.npz`, `labels_*.npz`, checkpoints `ckpt_*.pkl`.

The traces and checkpoints are mine and safe to remove; the analyses only need them to be re-run.

**Deleted:** only my own two `_short01_u06_j8000` entries, once, by exact name, to rebuild them with the 5 % jerk margin.
