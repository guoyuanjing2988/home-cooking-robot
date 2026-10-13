# R19 cups (GitHub #5): where the seasoning cups wait, and the pick → pour → return set (Windows, 2026-10-13)

Plan: `research/r19_seasoning_cups.md` §5–6; DECISIONS 2026-10-13 ("Seasoning cups: user answers").
New files only: `kitchen19seas.py`, `r19cup_screen.py`, `r19cupchain.py`, `r19cupw_recheck.py`, `r19cup_macpad.py`, `results/r19/cups/`, this file. No existing file was changed.

**Pouring itself is not simulated.** No liquid, granules or slosh. The chain checks only geometry, loads and timing.

## 0. Bottom line

1. **The plan's two short-list spots fail in the sim, for different reasons.**
   - **T1, the counter strip behind the plating spots:**
     - it blocks none of the stored paths (35 paths, 36,884 states, closest 13.2 mm);
     - but the arm reaches only the raised back row, and no pick → pour → return chain was found in about 20 smoke configurations;
     - raising the caddy 0.10 m puts it in the wok's plating path (−50 mm).
   - **T3, the narrow rack beside the cooker:** only 2 S cups fit, and IK finds 0–3 starts.
2. **The only spot where the whole set passed is T2R, a caddy on the cart right of the arm base.** Checked L cup, slot b1, re-checked at ≤ 4 mm:

   | | |
   |---|---|
   | Time | 24.6 s (28.1 s with the lane meet at x 0.56) |
   | Min reserve | 2.0 mm |
   | Plume clearance | ≥ 14.7 mm |
   | PGC jaw moment | 0.22 N·m |
   | Joint torque ratio | 0.352 |
   | Re-check | 0 hits in 1,795 states |

   - The S cup passes too.
   - It also passes with the enclosing arm geometry (`ARM=ur5e_enc`, #12).
   - **But the T2R caddy sits where the arm already moves:** 19 of 35 stored paths hit it, including the wok plating, the spatula fetch, the lid and 11 hub edges.
3. **T2L, the same caddy left of the base, is the spot to pursue.**
   - It is clear of every stored path by ≥ 100 mm.
   - Its pick side and pour side each work, but the chain was not closed in 14 smoke configurations. Next step: §6.3.
4. **Design consequences of the plume rule** (R15: arm ≥ 0.20 m from the wok axis between the rim and 1.25 m, while the heat is on):
   - With the plan's short lug, the fingers are about 0.1 m from the cup axis. A pour near the wok centre therefore needs the grip at ≥ ~1.36 m.
   - I used 1.38 m, so the cup lip is about 0.35–0.4 m above the food.
   - A lower pour needs one of these:
     - a long-handled cup (lug ≥ ~0.15 m);
     - the heat at 0 during the pour (as Mac assumed);
     - the drum in the servo rim holder.
5. **The plan's flat 2×3 caddy cannot be picked when the lugs face the robot.** I stepped the back row up 75 mm.
   - The front row was unreachable at every site anyway (0–1 starts of 192 at T1, T2 and T3): the arm folds onto its base for low targets ~0.4 m in front of it.
   - In practice the caddy is a **one-row, three-cup** holder. That is about the plan's average of ~3 cups per dish group, but it is half of the six slots planned.

## 1. Model (`kitchen19seas.py`, a layer added after `scene.build`)

**Cups** (304 stainless; object frame at the bottom centre):

| Cup | Size | Brimful | Mass (est.) | Contents (est.) |
|---|---|---|---|---|
| S | Ø65 × 45 mm | ~100 ml | 0.08 kg | ≤ 0.05 kg |
| L | Ø85 × 70 mm | ~300 ml | 0.15 kg | ≤ 0.16 kg |

- Each cup carries a 16 × 8 mm lug to the keyed 30 mm block (30 × 24 × 24 mm, the same class as the lid tab, spider and lever blocks). The block centre is 25 mm outside the wall and its top is 6 mm above the rim.
- Lug and block together: 0.02 kg (est.).
- The body is modelled as a solid cylinder, an envelope of cup plus contents.
- **Grasp:** approach along the lug, jaws horizontal across the block.
  - With vertical jaws the lower open finger, 53 mm below the TCP, reaches below the cup bottom.
  - The open fingers straddle the cup at ≥ 40 mm from its axis.
- **Pour:** a roll about the lug axis (a wrist-3 roll), lip 90° from the lug, as the plan says.

**Caddy** (stepped 2×3):
- column pitch 100 mm: the open fingers clear an L neighbour by ~4.5 mm on paper (the approaches in §3 are checked);
- row pitch 95 mm;
- back row on a 75 mm tier: the gripper's lowest point passes ≥ 5 mm over a front-row L block;
- footprint ~0.30 × 0.19 m;
- carry handle: a keyed block on a post at the left end. The plan's centre bail would arch over the middle column's grasp path. **The caddy carry itself is not checked.**

Every box I add is an 8-vertex box mesh. This is the R11 rule, because MuJoCo underestimates box–box gaps.

**Staging sites:**

| Site | Where | Notes |
|---|---|---|
| T1 | Caddy centre (0.315, 0.3875) on the counter; front-row lug blocks at y 0.26 | `Z` = riser |
| T2R / T2L | On a bracket from the cart mast, cart frame x ±0.32, support at 0.86 m, lugs toward the aisle | T2RC/T2LC: lugs toward the counter |
| T3 | S cups only (an L cup does not fit the 80 mm between plating spot 1 and the cooker) at x 0.59, y 0.315 / 0.41 | Lugs toward −x: from the front, the wok's handle block is in the way. **Only 2 cups fit**: open fingers need 90 mm pitch, and the R14 cup rail starts at y 0.505. |

- **T2 geoms belong to the cart body,** so the unchanged checker wants **10 mm** between them and the gripper or the held cup (not 5). The pick is therefore lifted 12 mm instead of 8.

## 2. Screen (`r19cup_screen.py`)

### 2.1 Replay

- Every stored state was replayed with the staging geoms present (all slots filled; L cups except at T3):
  - the 6 checked whole actions with their grasp approaches;
  - the 22 hub edges;
  - the R15 stir cycle (`results/r19/stir`).
- Method: fast checker, as `r18spatreplay.py`, plus the least distance. 35 paths, 36,884 states.

| Site | Paths hit | Closest |
|---|---|---|
| T1 (counter) | 0 | 13.2 mm: held wok to block b0, wok plating |
| T1 + 0.10 m riser | 2 (both wok plating runs) | −50 mm: wok shell into blocks f0 / f2 |
| T2R | **19**: wok plating at spots 1 and 2, spatula fetch, lid (each with its approaches) and 11 hub edges | −172 mm: forearm into cup b2 |
| T2L | 0 | ≥ 100 mm |
| T3 | 0 | 87.8 mm |

### 2.2 IK starts

- Method: 96 starts per run, seed 14, cup held 8 mm above its seat (12 mm at T2).
- Cell format: starts for grasp sense −1 / +1, then the best reserve (mm).

| Site, approach | Front row | Back row |
|---|---|---|
| T1, horizontal | f1: 0 / 1 (2.6) | b1: 0 / 8 (3.0) |
| T1, pitched 30° | f0–f2: 0 / 0 | b0, b1, b2: 5 / 8, 5 / 8, 5 / 6 (3.0–3.4) |
| T1, pitched 45° | f1: 1 / 0 (0.0) | b1: 3 / 8 |
| T1 + 0.10 m / 0.20 m, 30° | f1: 0 / 0, 0 / 1 | b1: 7 / 0, 8 / 0 (5.0) |
| T2R / T2L / T2RC, cart at 0.172 | f1: 0 | b1: 0 / 8, 0 / 8, 0 / 3 (2.0) |
| T3 (s0 front, s1 back), horizontal / 30° | s0: 0 | s1: 0, 3 (2.5) |

Blockers: the upper arm or forearm meets the base plate, mast or counter. This is R14's "not low and close in front of itself".

## 3. The cup-pour set (`r19cupchain.py`, a copy of `r17chain.py` with `ACT=cup`)

**Keyframes:**
1. pick (8 / 12 mm up);
2. lifted (30 mm) — anchor;
3. out: 4 cm toward the robot, 15 cm up;
4. lane (meet);
5. over the wok, level — anchor. Cup axis at (0.83, 0.09): 8 cm in front of the wok axis, because the hood front is at y 0.15. Grip at 1.38 m;
6. tipped 135° about the lug, 2 s dwell;
7. level;
8. lane (meet);
9. out;
10. lowered — anchor;
11. set down.

**Checking:**
- The unchanged checker with its 10 / 5 mm gaps.
- Grasp approach and release retreat: 50 mm, straight, with the cup in the world. They are the only contact windows.
- The R15 plume rule as a hard check at every step, join and shuffle. Anchor candidates inside the plume are dropped, as `r15reach.py` does.
- A filled cup must stay within 5 cm / 15° in a join, or 15° of level on a planned path.
- **Binding re-check (`r19cupw_recheck.py`):** every stored state, joint-linear in between and unwrapped, subdivided to ≤ 4 mm point bound, full checker plus the plume rule.

**Loads:** L 0.33 kg until the tip (0.17 kg after), CoM ~6–7 cm from the TCP.

**Passing runs** (all T2R, slot b1, sense +1; smoke settings SEEDS=1 TRIES=8 KEEP=4):

| Run | Cart pick / pour | Time (s) | Re-check states, hits | Min reserve (mm) | Min plume (mm) | PGC (N·m) | Joint ratio |
|---|---|---|---|---|---|---|---|
| `…_L_s+1_s10f` (meet x 0.70) | 0.40 / 0.45 | **24.6** | 1,795, 0 | 2.0 | 14.7 | 0.22 | 0.352 |
| `…_L_s+1_s10b` | 0.40 / 0.45 | 28.1 | 1,947, 0 | 2.0 | 14.7 | 0.22 | 0.352 |
| `…_L_s+1_s10d` | 0.25 / 0.45 | 27.4 | 1,876, 0 | 2.0 | 14.7 | 0.22 | 0.352 |
| `…_L_s+1_s10a` | 0.40 / 0.40 | 28.5 | 2,091, 0 | 2.0 | 14.7 | 0.22 | 0.357 |
| `…_S_s+1_s11S` | 0.40 / 0.45 | 28.4 | 1,889, 0 | 2.0 | 12.4 | 0.08 | 0.35 |
| `…_L_s+1_s11enc_ur5e_enc` | 0.40 / 0.45 | 28.1 | 1,935, 0 | 2.0 | 14.7 | 0.22 | 0.352 |

- **Where the minimum reserve sits:** 2.0 mm at the pick, where the held cup is 12 mm above its slot against T2's 10 mm rule. The approaches have 2.3 mm.
- **Time:** r17chain's time model, which assumes unlimited acceleration (R19 smooth found executions 20–50 % slower at the same caps).
- **Breakdown of the 24.6 s run:**
  - 20.4 s of held motion, including the 2 s dwell;
  - 1.5 s of joins: 6°, plus a 4 cm cart shuffle;
  - 1.6 s for grasp and release;
  - 1.0 s for the approaches.

**What failed, and the change each failure caused:**

| Attempt | What happened | Change |
|---|---|---|
| Pull the cup 13 cm toward the robot | The arm folded onto its base | Lift 15 cm first ("out") |
| Grip at 1.33 m | Fingers 6–37 mm inside the plume band | Grip at 1.38 m: 15–44 mm clear |
| Free cart on the pour frames | The cart drifts to x 0.7–0.9; shoulder and upper arm 0.2–1.4 mm inside the plume radius | `POURC` fixes the pour cart; the lanes stay free (fixed lanes broke the pick side) |
| T1 (counter) | Every lift from the back-row pose hits the counter (elbow), the upper-cabinet door (wrist) or the base | Tried: horizontal and 30° approaches; lug toward the robot or to the left at the pour (`POUR_YAW`); `ONE=1`; heat off with a low pour; a riser. None closed. |
| T1 + 0.10 m | Both sides follow, but the meet join is blocked and a planned join (`PLAN=1`) fails | Riser dropped anyway: it hits the wok plating |
| T2L | Its free lane lets the cart drift right with the cup until the upper arm grazes the plume (−1 to −5 mm); with the lane cart fixed, the arm hits the held cup | Next step in §6.3 |

## 4. Comparison with the Mac session's cup run (commit 223f9c0; read-only from GitHub)

| | Mac (`results/mac/chain_cup_final.json`) | Windows (this study) |
|---|---|---|
| Where the cup waits | Single pad, cup bottom at (0.45, 0.30, **1.085**) | Caddy on the cart, right of the base; slot b1 at x cart + 0.32, y −0.13, z 0.94 |
| Same spot as T1? | **No.** Same x/y area as T1's right column (x 0.415, y 0.34–0.435), but 0.16–0.23 m higher and a single cup. My counter-level T1 found no chain. | — |
| Cup and grasp | R14 cup, 60 × 70 mm, gripped at its centre, no lug | Plan's cup with the keyed lug |
| Heat / plume rule | Heat off, not applied | On, applied: hard check plus ≤ 4 mm re-check |
| Pour | 120°, low at the front rim (bottom 5.5 cm above the rim), sideways | 135°, grip 1.38 m, lip ~0.35–0.4 m above the food |
| Time | **20.6 s** | **24.6 s** (28.1 s with meet x 0.56) |
| Min reserve | 2.2 mm | 2.0 mm |
| Re-check | 224 stored states | 1,795 states at ≤ 4 mm |
| Method | `ONE=1`: the pour is not an anchor | I added the same idea as `ONE=1` in my copy (written independently). It did not help at T1. |

- **Mac's pad is in the wok's plating path** (`r19cup_macpad.py` → `results/r19/cups/macpad_replay.txt`). I modelled the pad, cup and a post standing in for the unmodelled hanger, from the numbers in Mac's report only.
  - The stored wok plate-and-rinse chains hit it in 152 / 470 states (spot 1) and 63 / 470 (spot 2).
  - The first hit is the pad itself: 2.6 mm from the wok shell, against 5 mm required.
  - The held wok goes up to 85 mm into the post.
  - The other 4 actions are clear: spider ≥ 73.9 mm.

## 5. Drum variant

**Not built.** It is not a simple swap:
- The arm-held R14 drum is Ø80 × 140 mm and is held at its knob end, ~0.10 m from its centre. So the plume rule needs the same high pour.
- The drum has no staging place yet: it does not fit the caddy, and R15 found the right-rim holder unloadable.

`r19cupchain.py` takes a new object in a few lines, the way kitchen16.OBJ objects are added.

## 6. Commands for the full runs (controller, background)

Run them from the work folder:

```
cd C:/Users/admin/Documents/YJGames/robot_rail/sim/r10/claude
PY=C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe
```

Default chain settings are SEEDS=2 TRIES=6 KEEP=6. Expect ~5–15 min per chain plus ~2 min of re-check (WORKERS=8).

### 6.1 Confirm T2R at full settings: all back-row slots, both sizes, both arm models

```
for A in ur5e ur5e_enc; do for SL in b0 b1 b2; do for SZ in L S; do
 $PY r19cupchain.py ACT=cup SITE=T2R SLOT=$SL SIZE=$SZ SIGN=1 CARTX=.40 POURC=.45 MEET_X=.70 TAG=full ARM=$A WORKERS=8
done; done; done
```

### 6.2 Screens not yet run in full

All slots, both sizes, and the enclosing arm. Each ~3–5 min.

```
for S in T1 T2L T2R; do for Z in L S; do $PY r19cup_screen.py SITE=$S MODE=ik SIZE=$Z APITCH=0; $PY r19cup_screen.py SITE=$S MODE=ik SIZE=$Z APITCH=30; done; done
for S in T1 T2L T2R T3; do $PY r19cup_screen.py SITE=$S MODE=replay WORKERS=10 ARM=ur5e_enc; done
```

### 6.3 T2L (clean replay, chain not closed): wider search

```
for C in .10 .25 .40; do for P in .40 .45; do
 $PY r19cupchain.py ACT=cup SITE=T2L SLOT=b1 SIZE=L SIGN=1 CARTX=$C POURC=$P SEEDS=2 TRIES=12 KEEP=6 TAG=full WORKERS=8
 $PY r19cupchain.py ACT=cup SITE=T2L SLOT=b1 SIZE=L SIGN=1 CARTX=$C POURC=$P SEEDS=2 TRIES=12 KEEP=6 PLAN=1 PLAN_S=120 TAG=fullplan WORKERS=8
done; done
```

If these fail, the next design step is an extra "swing" keyframe that brings the cup across in front of the base with the cart fixed. It is not in the code yet.

### 6.4 T1 (counter): settle whether any chain exists with a wider search

```
$PY r19cupchain.py ACT=cup SITE=T1 SLOT=b1 SIZE=L SIGN=-1 APITCH=30 POUR_YAW=-90 CUP_Y=.07 SEEDS=3 TRIES=12 KEEP=6 PLAN=1 PLAN_S=120 TAG=full WORKERS=8
$PY r19cupchain.py ACT=cup SITE=T1 SLOT=b1 SIZE=L SIGN=1 POUR_YAW=-90 CUP_Y=.07 ONE=1 SEEDS=3 TRIES=12 KEEP=6 TAG=full_one WORKERS=8
```

### 6.5 Reproduce the replays already reported (~3–4 min each)

```
for S in T1 T2L T2R T3; do $PY r19cup_screen.py SITE=$S MODE=replay WORKERS=10; done
```

## 7. Caveats

- **Smoke settings.** All chain results are smoke runs (SEEDS=1). No full-setting run has been made yet (§6).
- **The plume rule** is R15's estimate: 90 °C on the axis, near ambient 0.2 m off it. It applies only while the heat is on.
- **T2 hardware is not designed:**
  - the bracket, and the cups riding on a moving cart (slosh at 0.15–0.5 m/s² is not checked);
  - loading the caddy onto the cart;
  - the cart's stability with the extra load.
- **Hand-off.** The chain starts and ends with an empty hand at the slot. Hand-off into the stir cycle or the hub tuck is not checked.
- **Wrist-3 roll.** The 135° tip is a wrist-3 roll. FR5 needs the ±360° J6 option (R19 arm swap). Not run with FR5 or CS66.
- **Logs:** `results/r19/cups/logs/`. The failing smoke chains are kept as `chain_cup_*_s*.json` for the record.
