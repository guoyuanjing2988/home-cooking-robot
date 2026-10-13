# R19 cart: BOM, mass and CoG, dynamic tip-over, sliding and protective stops (issue #14, 2026-10-13)

The question: `R19_SMOOTH.md` says a cart acceleration of 0.5 m/s² keeps a 42.7 mm tip margin with the wok held. That number comes from the quasi-static `mobile.dock_stability` model. This round:
- replaces the guessed boxes with a component list;
- runs MuJoCo inverse dynamics along the real smoothed time laws, with the held loads;
- adds sliding, UR5e protective stops and cart E-stops.

Code (new files only):
- `r19cart_bom.py`: BOM and model patch;
- `r19cart_dyn.py`: time laws, inverse dynamics, support, stops, sweeps;
- `r19cart_options.py`: design options, jerk, friction mechanism;
- `r19cart_report.py`: tables;
- `r19cart_cad.py`: build123d concept CAD.

Results are in `results/r19/cart/`; CAD is in `cad/r19_cart/`. No existing file was changed.

Labels: **[S]** sourced, **[D]** derived from sourced numbers or geometry, **[M]** measured in the sim, **[E]** engineering estimate.

## Answer first

- **Tipping: the 42.7 mm claim is conservative, not optimistic.**
  - Method: the smoothed time laws regenerated exactly as `r19smooth.py` does them (same times). The held payload is on the gripper and `mj_inverse` acts on the whole cart+arm tree.
  - In normal motion no action comes near tipping. The smallest rigid-body margin is 71.8 mm (stir at bench timing). For the wok at 0.5 m/s² it is 78.6 mm (BOM masses) or 55.7 mm (the sim's own boxes).
  - The quasi-static model's ×1.5 on 0.5 m/s² in *every* direction overstates the load. With the same support assumptions it gives 42.7 mm where the dynamics give 103.8 mm.
- **But 0.5 m/s² is not safe for the wok as designed, because of sliding, which R19 never checked.**
  - R10 has two hub-motor drive wheels in tandem on one line (y = −0.22, axles along y) plus two swivel casters. Swivel casters carry no horizontal force, so all traction, all side force *and* the yaw couple go through the two drive wheels.
  - The yaw couple exists because the drive wheels sit 0.22 m behind the CoG; the arm also moves the CoP sideways.
  - The worst instant: wok, plate→sink, cart braking at 0.38 m/s². The CoP is 116 mm towards +x, which leaves the trailing drive wheel only 63 N while it carries half of a 46 N side-force couple. That needs **μ = 0.43** (0.68 with the sim's mass distribution).
  - The same instant needs 0.09 without the cart's acceleration; the 20 N tether adds 0.07.
  - PU tyres on kitchen tile: about 0.5 dry and 0.2–0.3 wet [E]. A drive wheel therefore slips on a wet floor, and with 1–2 mm clearance reserves an unobserved cart slip is a collision risk.
- **The dock bumper does nothing with swivel casters.**
  - Its −y reaction would have to be carried by drive-wheel friction. But the drive wheels unload as the CoP moves to the caster line: μ·z_bumper/wheelbase = 0.45 < 1.
  - `mobile.py`'s "bumper ≤ 250 N, ≤ μW" model implicitly assumes friction on all four wheels, i.e. fixed castors.
  - In every smoothed law the CoP stays at least 44 mm behind the caster line (lever, sim boxes; ≥ 80 mm with BOM masses), so the bumper is never needed in normal motion.
- **Protective stops do not tip or measurably slide the cart, at any instant, in any category, for any action, including wok held out + cart moving.**
  - UR5e stopping data (manual 2.3 graphs) imply a near-constant deceleration whatever the speed: J0 19 rad/s², J1 11 rad/s², J2 19 rad/s² at 5 kg (and higher at 66 % payload). So a stop at any speed briefly puts the ZMP far outside the support: up to 176 mm (272 mm with the 66 %-payload set) beyond the edge, i.e. up to 116 N·m beyond the edge, for 4–60 ms.
  - The issue's estimate of 23–46 N·m against a ~30 N·m reserve is right about the peak.
  - The duration makes it harmless. Rocking energy is at most 0.23 % of the energy needed to lift the CoG over an edge; a crude upper bound (all arm momentum about the worst edge) gives ≤ 3.5 %.
  - Wheel lift is ≤ 0.12 mm and slip ≤ 1 mm (arm stop alone) to ≤ 3.1 mm (arm stop plus a traction-limited cart E-stop).
- **Maximum safe cart acceleration is set by friction, not tipping.** At 1.2 m/s² the tip margin is still ≥ 52 mm.
  - Allowing friction use ≤ 80 %:
    - wok ≤ 0.46 m/s² on a dry floor (μ 0.5), **≤ 0.24 m/s² on a wet floor (μ 0.3)**;
    - spider, spatula and lid ≥ 0.6 m/s² even wet.
  - With fixed castors the wok gets ≥ 0.9 m/s² dry and 0.53 m/s² wet.
  - **Jerk:** rigid-body tipping does not depend on it. With an estimated 3–8 Hz rocking mode on the PU tyres, R19's 0.1 s acceleration ramp (5 m/s³ at 0.5 m/s²) costs about 10 mm; ramps ≥ 0.2 s (j ≤ 5·a) cost nothing.
- **Fixes, cheapest first:**
  1. **Fixed (rigid, x-aligned) castors** instead of swivel casters. 0 kg, about CNY 0 [E]. The cart can only travel along x anyway.
     - Wok at 0.5 m/s²: μ 0.43 → 0.23, margin 79 → 101 mm.
     - The bumper becomes effective.
     - Stir: μ 0.44 → 0.19.
  2. **Or a per-phase limit:** cart ≤ 0.3 m/s² while the wok is held, and ≤ 0.5 m/s² elsewhere. Wok 36.2 s → about 39.6 s.
  3. **A holding brake / caster locks for the parked stir.**
  4. Ballast (+10 kg: μ 0.36) and a wider track (+50 mm per side: μ 0.33) help, but less.
  5. A lower mount is not worth re-planning everything.

  So: keep 0.5 m/s² for spider, spatula and lid. For the wok, keep it only with fixed castors.
- **The issue cannot be closed yet.** Every chain keeps a positive *rigid* margin, but four constants are still estimates: μ (dry/wet), the rocking frequency, caster trail and bumper/cabinet strength. The stir's elastic-rocking estimate is near zero at 3–5 Hz (§6).

## 1. Mass, CoG and BOM (`r19cart_bom.py`, `results/r19/cart/bom.json`)

Cart frame (= the sim's `rail_structure`): origin on the floor under the cart reference point; x along the counter, y towards the cabinets (docked at world y −0.21, bumper face at local +0.21), z up.

| Item | kg | CoM (x, y, z) m | Label |
|---|---|---|---|
| Chassis frame, steel RHS 40×40×2, 3.2 m (2.39 kg/m) | 7.64 | 0, −0.05, 0.11 | D |
| Deck, Al 5 mm, 0.60×0.50 | 4.05 | 0, −0.05, 0.13 | D |
| Wheel/caster brackets, mast foot gussets | 2.0 | 0, −0.12, 0.13 | E |
| Mast, steel RHS 100×100×4, 0.865 m (12.06 kg/m) | 10.43 | 0, −0.17, 0.62 | D |
| Beam, steel RHS 100×50×4, 0.30 m | 2.68 | 0, −0.045, 1.08 | D |
| Mast–beam plates, bolts | 0.8 | 0, −0.17, 1.08 | E |
| UR adapter, 20° Al wedge, pocketed (CAD: 2.75) | 2.0 | 0, 0.08, 1.10 | E |
| 2 × ZLTECH ZLLG65ASM500 V2.0 hub motor | 2 × 4.85 | ±0.22, −0.22, 0.083 | S |
| 2 × 100 mm swivel caster with lock | 2 × 0.9 | ±0.22, 0.11, 0.06 | E |
| ZLAC8015D driver / 48 V 600 W supply / safety relay, enclosure, wiring | 0.8 / 1.5 / 1.9 | ≈ 0, −0.10, 0.22 | E |
| Bumper (rubber D-profile + Al backing) | 1.0 | 0, 0.205, 0.30 | E |
| Covers: skirt / mast | 1.5 / 1.0 | — | E |
| E-stop / UR cable on the cart (1.5 m) / tether inlet / fasteners / dock pads | 0.3 / 0.5 / 0.4 / 1.0 / 0.3 | — | E |
| **Cart without the arm** | **51.3** (Al mast: 44.5) | **0.001, −0.102, 0.353** | |
| UR5e | 20.6 | links: UR DH table | S |
| PGC-140-50 + fingers + flange adapter | 1.0 + 0.2 + 0.15 | | S / E / E |
| **Machine (first wok state)** | **73.2** | **0.068, −0.015, 0.590** | |
| Sim (`SD` preset, compiled) | 66.7 | 0.065, 0.023, 0.536 | M |

**UR5e links**

| Link | UR DH table [S] | Sim (menagerie) [M] |
|---|---|---|
| Base | 2.90 kg (20.6 datasheet minus links) [D] | 4.0 kg |
| Shoulder | 3.761 kg | 3.7 kg |
| Upper arm | 8.058 kg | 8.393 kg |
| Forearm | 2.846 kg | 2.275 kg |
| Wrist 1 | 1.37 kg | 1.219 kg |
| Wrist 2 | 1.3 kg | 1.219 kg |
| Wrist 3 | 0.365 kg | 0.189 kg |
| **Total** | **20.6 kg** | **21.0 kg** |

Model notes:
- The DH CoMs are mapped onto the menagerie bodies through the DH frames. The menagerie base frame is the DH base turned 180° about z; the flanges agree within 1.2 mm.
- The link inertias are the menagerie values scaled by mass [E].

**Mismatches in the sim's boxes**, fixed in my model copy only (`r19cart_bom.patch`, in memory):
- **Casters weigh 4.85 kg each.** `verified_wheels` re-sizes every `R_cart_wheel_*` geom to the hub motor. That is +7.9 kg, low and forward, which flatters front stability and friction.
- **The mast is 4 kg**, i.e. aluminium 100×100×4. I use steel (10.4 kg): it is stiffer for the OEM "rigid base" rule and better for stability (§7).
- **No covers, E-stop, cable or fasteners** (+5 kg). Electrics are 3 kg vs 4.2 kg.
- **The adapter is a flat 1.13 kg plate** at 15 mm above the beam top. A 20° wedge under a 170 mm flange needs about 41 mm (CAD, §8).
- **`mobile.dock_stability` uses its own contact lines**, independent of the geoms.

**Mass sensitivity** (wok, 0.5 m/s²; min tip margin / max μ_req):

| Model | Margin | μ_req |
|---|---|---|
| Sim boxes | 55.7 mm | 0.68 |
| BOM, steel mast | 78.6 mm | 0.43 |
| BOM, Al mast | 67.8 mm | 0.58 |
| Chassis −30 % | 71.7 mm | 0.48 |
| Chassis +30 % | 84.7 mm | 0.39 |

## 2. Method (`r19cart_dyn.py`)

1. **Time laws.**
   - For each `results/r19/smooth/<act>_spline_move.json`, the stored checked geometry is re-timed with `r19smooth.Seg` + `time_segment` and the `same` / `fast` / `fastcart` limits. The motion times reproduce R19 exactly (wok 36.18 s at `fastcart`).
   - q, q̇, q̈ come analytically from the path derivatives on the 2 ms grid. Dwells are held poses.
   - Stir: the stored R15 states (`results/r19/stir/`). Working parts run at the bench timing (k = 1), or slowed ×k. The stored law jumps in velocity at every hand-off, so each working part is started and stopped *on its path* with a 360°/s² ramp [E]. Returns are 180°/s / 360°/s² trapezoids, as in `r15stirwalk2`.
2. **Inverse dynamics.**
   - `mj_inverse` + `mj_rnePostConstraint` with contacts off. The cart root's `cfrc_int` is the wrench the floor and bumper must supply: gravity, the cart's own acceleration, all link inertia and the payload.
   - Payload on R_tool (`r19smooth.load_parts`):
     - wok 1.8 kg + food 1.15 kg until the plate tip, or water 0.5 kg from the tap to emptying;
     - spider 0.45 kg; spatula 0.3 kg; lid 0.8 kg;
     - stir spatula 0.3 kg at the TCP [E].
   - Checked against a finite-difference Newton–Euler: they agree to 1e-6 N and N·m.
3. **Support.**
   - Contacts: drive wheels (±0.22, −0.22); swivel casters at (±0.22, 0.11), with their contacts trailing 35 mm behind the last motion [E]. When the trail direction is unknown, the worse side is taken.
   - Margin = the distance of the floor CoP (ZMP) to the polygon, minus worst-direction extras: tether 20 N at 0.10 m (`mobile.py` cap), slope, and process force.
   - Friction: per drive wheel, μ_req = |f|/N_wheel. x is split by load; y includes the yaw couple.
   - Fixed-castor variant: y friction on all four wheels, and the bumper up to min(250 N, μN − |F_y|), as `mobile.py` models it.
4. **Stops**, from every 10 ms of every law (cart E-stops every 50 ms). Arm:
   - cat 0: each joint at its own deceleration;
   - cat 1/2: path-synchronous, same limits. UR: "the load during stopping motion is independent of the stop category type".
   - none.

   Cart: on its law / E-stop at 0.5 m/s² / traction-limited E-stop (μ × drive load, ≤ 2 × 30 N·m / r).

   Per stop, the rigid-body ZMP is computed through the stop. The angular impulse beyond each edge gives a rotation energy, which is divided by the energy needed to lift the CoG over that edge (≥ 1 = tips). Lift and slip are reported too; friction is allowed to arrest the slip.

   UR deceleration = π / t_stop at 100 % speed (180°/s) and 100 % extension:
   - 5 kg: J0 0.164 s, J1 0.288 s, J2 0.162 s;
   - 66 % of 5 kg: J0 0.140 s, J1 0.210 s, J2 0.102 s.

   The graphs are linear in speed through about zero, i.e. constant deceleration; J0 gives 19 m/s² at the TCP from both the 33 % and the 100 % speed points. Wrists: no data, taken as J2 [E].
5. **Elastic rocking [E].** The cart rocks on PU tyres and casters. An estimate with tyre stiffness about 2·10⁵ N/m: k_rot ≈ 4·k·0.22² ≈ 3.9·10⁴ N·m/rad and I ≈ 36 kg·m², so f ≈ 5 Hz. The rigid CoP is passed through a unit-gain SDOF at 3 / 5 / 8 Hz, ζ 0.05. This is a flag, not a verdict: the mode must be measured.

## 3. Dynamic margins along the smoothed laws

BOM masses, swivel casters, tether 20 N, rigid body. "Fixed castors" is the same law with the fixed-castor support.

| Action | Profile | Motion s | Min tip margin mm (edge) | Static mm | max μ_req | Elastic 3 / 5 / 8 Hz mm [E] | Slope 1° mm | Fixed castors: mm / μ |
|---|---|---|---|---|---|---|---|---|
| wok | same | 56.0 | 81.3 (+x) | 81.6 | 0.18 | 79.9 / 81.2 / 81.1 | 70.9 | 104.8 / 0.13 |
| wok | fast | 46.8 | 81.3 (+x) | 81.6 | 0.18 | 79.4 / 81.2 / 81.1 | 70.9 | 104.8 / 0.13 |
| wok | **fastcart** | 36.2 | **78.6 (+x)** | 81.6 | **0.43** | 69.5 / 68.9 / 74.5 | 68.1 | 101.4 / 0.23 |
| spider | same / fast / fastcart | 56.4 / 42.8 / 37.2 | 110.6 (front) | 113.6 | 0.13 / 0.13 / 0.17 | ≥ 103.9 | 99.2 | ≥ 146.5 / ≤ 0.14 |
| spatula | same / fast / fastcart | 31.3 / 21.3 / 17.5 | 118.7 (back) | 125.6 | 0.10 / 0.10 / 0.19 | ≥ 111.9 | 107.3 | 119 / ≤ 0.15 |
| lid | same / fast / fastcart | 25.0 / 20.2 / 16.8 | 122.0 (+x) | 123.2 | 0.09 / 0.10 / 0.17 | ≥ 108.7 | 111.4 | ≥ 140.6 / ≤ 0.14 |
| lever | all | 2.1 | 79.8 (front) | 79.9 | 0.12 | 79.6 | 69.3 | 146.1 / 0.14 |
| **stir**, bench (k = 1) | parked | 13.5 / cycle | **71.8 (+x)** | 141.3 | **0.44** | **−26.8 / −4.7 / 21.0** | 60.2 | 90.3 / 0.19 |
| stir, k = 1.25 / 1.5 / 2 | parked | 15.6 / 17.8 / 22.2 | 79.5 / 91.3 / 111.0 | 141.3 | 0.39 | 3 Hz −1 / −7 / −29; 5 Hz 4 / 9 / 28 | ≥ 67.9 | ≥ 98.4 / 0.18 |

**Comparison with the claim** (wok, 0.5 m/s²):

| Model | Margin | μ_req |
|---|---|---|
| R19 quasi-static: sim boxes, ×1.5, 0.5 m/s² in any direction, bumper | 42.7 mm | not computed |
| Dynamic, sim boxes, the same support (fixed castors + bumper) | 103.8 mm | 0.36 |
| Dynamic, sim boxes, swivel | 55.7 mm (front) | 0.68 |
| **Dynamic, BOM, swivel (design as named)** | **78.6 mm** | **0.43** |

**Sensitivities** (wok `fastcart`, BOM):

| Change | Margin | μ_req |
|---|---|---|
| Slope 0.5° / 1° | 73.3 / 68.1 mm | 0.46 / 0.48 |
| No tether | 81.3 mm | 0.36 |
| No caster trail | 92.6 mm (front binds) | — |
| Fixed castors with a 100 N bumper | 101.4 mm | — |

μ itself does not move the swivel margins: the verdict is μ_req against the floor's μ.

**Stir process force** (R15 bench, spatula contact force p95 5.6 N, max 24.9 N [M]), applied horizontally at the TCP in the worst direction:

| Force | Margin | μ_req |
|---|---|---|
| 6 N | 61.9 mm | 0.46 |
| 25 N spike | 30.8 mm | 0.51 |

**Stir IK kink.** The stored stir has an IK kink in working part 4: wrist acceleration about 9,500°/s² near state 116. Its working parts reach 450–1,450°/s² elsewhere. This is the R15 bench timing; it needs a real time law like the R19 smoothing.

## 4. Protective stops and E-stops

BOM masses, swivel casters; worst over all start instants. Each cell gives: min instantaneous ZMP margin (mm) · rocking energy ratio (1 = tips) · lift (mm) · slip (mm). Deceleration set: 5 kg / 66 %.

| Case | wok `fastcart` | spider `fastcart` | spatula `fastcart` | lid `fastcart` | stir k = 1 (parked) |
|---|---|---|---|---|---|
| Arm cat 0, cart on its law | −176 / −272 · 0.0006 / 0.0012 · 0.04 · 0.2 | −91 / −174 · ≤ 0.0009 · 0.04 · 0.8 | −41 · 0.0000 · 0 · 0 | −69 · 0.0002 · 0.01 · 0.3 | −85 / −173 · ≤ 0.0017 · 0.11 · 1.0 |
| Arm cat 1/2 (path-synchronous) | −117 / −188 · ≤ 0.0011 · 0.03 · 0.2 | −71 / −136 · ≤ 0.0007 · 0.03 · 0.7 | −29 · 0 · 0 · 0 | −49 · 0.0002 · 0.01 · 0.2 | +21 / −56 · ≤ 0.0015 · 0.09 · 1.0 |
| Arm cat 0 + cart E-stop 0.5 m/s² | −176 / −272 · ≤ 0.0012 · 0.04 · 0.2 | −91 / −174 · ≤ 0.0009 · 0.04 · 0.9 | −47 · 0 · 0 · 0.1 | −69 · 0 · 0 · 0.2 | — |
| Arm cat 0 + traction-limited cart E-stop | −176 / −272 · ≤ 0.0013 · 0.05 · 3.1 | −197 / −251 · ≤ 0.0010 · 0.06 · 1.9 | −223 · 0.0011 · 0.07 · 2.8 | −188 · 0.0008 · 0.05 · 0.7 | — |
| Cart E-stop 0.5 m/s² only | +50.9 (μ_req 0.51) | +102 | +114 | +113 | — |
| Cart E-stop traction-limited only | −26 · 0.0023 · 0.10 · 0.2 | −20 · 0.0005 · 0.03 · 0 | −32 · 0.0011 · 0.07 · 0 | −24 · 0.0006 · 0.04 · 0.1 | — |

The other profiles give the same picture (`results/r19/cart/logs/r19cart_report.log`, table C).

- **The worst instants are the wok held out with the cart moving.** Example: t = 4.8 s, the food-laden wok, cart at −0.07 m/s, front edge, 116 N·m beyond the edge for 4 ms.
- **Peaks do not depend on speed.** The UR brakes at a constant rate, so even a slow arm gives the same peak, only shorter. The stir peaks are identical for k = 1–2.
- **Hand check of the bound.** Arm momentum is ≤ about 3 N·s at about 1.1 m. That gives ≤ 3.3 N·m·s about an edge, so the rotation energy is ≤ 0.14 J. The energy needed to tip over the wok's 80 mm lateral edge is about 4 J.
- **No brake.** R10 has none. A cat 0 cart stop (power removed) coasts. At 0.25 m/s with 0.1–0.2 m/s² of rolling resistance [E], that is 0.16–0.3 m with the arm out: a collision risk, not a tip risk.
- **Wet floor.** The 0.5 m/s² cart E-stop needs μ 0.51 on the wok, so it is not achievable on a wet floor.

## 5. Maximum cart acceleration and jerk

**Acceleration sweep** (`fast` caps, cart jerk = a/0.1 s; BOM, swivel). The cart speed cap of 0.25 m/s limits the acceleration actually reached in short moves.

| Action | Limit 0.15 | 0.3 | 0.5 | 0.8 | 1.2 m/s² |
|---|---|---|---|---|---|
| wok: margin mm / μ_req | 81 / 0.18 | 81 / 0.28 | 79 / 0.43 | 65 / 0.59 | 52 / 0.85 |
| spider | 111 / 0.13 | 111 / 0.13 | 111 / 0.17 | 111 / 0.23 | 100 / 0.33 |
| spatula | 119 / 0.10 | 119 / 0.14 | 119 / 0.19 | 119 / 0.34 | 119 / 0.31 |
| lid | 122 / 0.10 | 122 / 0.12 | 122 / 0.17 | 117 / 0.25 | 102 / 0.33 |

**Largest safe cart acceleration**, criterion μ_req ≤ 0.8·μ (dry μ 0.5 → 0.40; wet μ 0.3 → 0.24 [E]):

| Action | Swivel, dry | Swivel, wet | Fixed castors, dry | Fixed castors, wet |
|---|---|---|---|---|
| wok | 0.46 | **0.24** | > 1.2 (reaches 0.9) | 0.53 |
| spider | > 1.2 | 0.85 | > 1.2 | > 1.2 |
| spatula | > 1.2 | 0.60 | > 1.2 | 0.78 |
| lid | > 1.2 | 0.76 | > 1.2 | > 1.2 |
| stir (parked, arm only) | μ_req 0.44 at bench timing: exceeds 0.40 | exceeds | 0.19: OK | 0.19: OK |

The tip margin never binds below 1.2 m/s².

**Jerk** (wok, `fast` caps):

| a_cart | Ramp a/j | Motion s | Rigid mm | μ_req | Elastic 3 / 5 / 8 Hz mm |
|---|---|---|---|---|---|
| 0.3 | 0.4 / 0.2 / 0.1 s | 55.6 / 43.9 / 39.6 | 81.3 | 0.17 / 0.23 / 0.28 | 80 / 81 / 81 → 70 at 3 Hz with the 0.1 s ramp |
| 0.5 | 0.4 / 0.2 / 0.1 s | 49.3 / 39.9 / 36.2 | 81.3 / 81.3 / 78.6 | 0.22 / 0.32 / 0.43 | 0.1 s ramp: 69.5 / 68.9 / 74.5; 0.2 s ramp: 71.0 / 81.2 / 81.1 |

Recommendation: cart jerk ≤ a/0.2 s, i.e. ≤ 2.5 m/s³ at 0.5 m/s² (R19 used 5 m/s³). (0.3 m/s², 0.1 s ramp) beats (0.5 m/s², 0.2 s ramp) on both time and μ.

## 6. Stir cycle

- **Rigid body.** The stir at bench timing is fine: 71.8 mm, the worst in working part 3.
- **Friction (cart parked).** The cart is parked, but the arm alone needs μ 0.44. Arm reactions reach 46 N horizontal plus the J1 yaw reaction, all on two drive wheels; on the lighter wheel this means μ 0.44.
- **Elastic rocking estimate.** At 3–5 Hz it is −27 / −5 mm at k = 1, and it does not improve monotonically with k (resonance with the stroke content). This is the one result that needs a measured rocking frequency and damping.
- **Recommendation:**
  - lock the casters while parked for the stir (caster total-lock or fixed castors): μ 0.19, margin 90 mm, 5 Hz elastic +13 mm;
  - give the stir a jerk-limited time law (it has velocity jumps and an IK kink as stored);
  - add 10–20 kg of ballast if a tap test finds a mode ≤ 5 Hz.

## 7. Design changes

Effect = min tip margin mm | max μ_req | elastic 5 Hz mm. Mass and cost are [E].

| Change | wok `fastcart` | wok `fast` | spider `fastcart` | stir k = 1 | Mass | Cost / remark |
|---|---|---|---|---|---|---|
| Baseline (BOM, swivel) | 78.6 \| 0.43 \| 68.9 | 81.3 \| 0.18 \| 81.2 | 110.6 \| 0.17 \| 110.3 | 71.8 \| 0.44 \| −4.7 | — | — |
| **Fixed x-aligned castors** | **101.4 \| 0.23 \| 92.2** | 104.8 \| 0.13 \| 93.8 | 146.5 \| 0.14 \| 110.3 | **90.3 \| 0.19 \| 13.0** | 0 | Fixed castors cost less than swivel ones; directional-lock swivels +CNY 100–300 per pair. Cart travels along x only anyway; the bumper becomes effective (250 N reserve) |
| Ballast 10 kg (steel plate under the deck) | 92.4 \| 0.36 \| 83.7 | 95.1 \| 0.15 \| 95.0 | 116.5 \| 0.16 \| 116.3 | 86.9 \| 0.36 \| 19.7 | +10 kg | about CNY 100–200; against the R10 "less weight" goal |
| Ballast 20 kg | 103.3 \| 0.31 \| 95.4 | 106.1 \| 0.13 \| 106.0 | 121.1 \| 0.16 \| 120.9 | 98.9 \| 0.30 \| 38.9 | +20 kg | about CNY 150–300 |
| Track +50 mm per side (x ±0.27) | 92.6 \| 0.33 \| 92.2 | 94.8 \| 0.16 \| 93.8 | 110.6 \| 0.16 \| 110.3 | 113.5 \| 0.34 \| 45.0 | +1 kg | about CNY 100; the cart grows to 0.70 m along the counter, so re-check the x travel ends (the spatula uses −1.48) |
| Fixed castors + 10 kg | 114.7 \| 0.21 \| 100.1 | 118.1 \| 0.11 \| 101.6 | 153.3 \| 0.13 \| 116.3 | 105.5 \| 0.16 \| 37.6 | +10 kg | |
| Aluminium mast (vs steel) | 67.8 \| 0.58 \| 58.1 | 68.3 \| 0.24 \| 68.2 | 93.3 \| 0.20 \| 93.0 | 57.5 \| 0.58 \| −26.8 | −6.8 kg | worse on all counts and about 3× less stiff: keep steel |
| Per-phase limit: cart ≤ 0.3 m/s² with the wok held, jerk ≤ a/0.2 s | wok `fast` at 0.3: 81 mm, μ 0.23–0.28 | | | | 0 | Wok 36.2 → about 39.6–43.9 s; spider, spatula and lid keep 0.5 |
| Plinth guide rail / docking latch (rollers on a rail along the plinth) | not modelled: carries y and holds the front down | | | | +1–2 kg | about CNY 1–2 k + drilling the user's plinth |
| Lower mount (1.12 → 1.0 m) | about −7 % of the acceleration-induced CoP shift (CoG −0.04 m) | | | | 0 | Invalidates every checked path (R10 raised it for the sink rim): not recommended |
| Holding brake (spring-applied on the hub motors) + cat 1 cart E-stop ramp | needed for power loss, slopes and parking | | | | +1–2 kg | about CNY 4 k for two (R09 allowance: 8 k for four with custom hub couplings); caster total-locks for parking are about CNY 50 |

## 8. Concept CAD (`r19cart_cad.py` → `cad/r19_cart/r19_cart.step`, `.stl`, `r19_cart_mass.json`)

The CAD is parametric (track, mount height, tilt). Its volumes × density cross-check the BOM:

| Part | CAD | BOM |
|---|---|---|
| Mast | 10.12 kg | 10.43 kg |
| Beam | 2.68 kg | 2.68 kg |
| Frame | 6.87 kg | 7.64 kg (corner overlaps) |
| Adapter wedge | 2.75 kg | 2.0 kg estimate |

Geometric findings that the sim's boxes hide:
- **Adapter height.** A 20° wedge under the 170 mm UR flange needs its bottom at mount − 41 mm (w = 10…72 mm). The sim's beam top is at mount − 15 mm, so its tilted 24 mm base plate overlaps the beam. Lowering the beam 26 mm keeps the flange at 1.12 m and only adds clearance.
- **Wheel fit.** The 167 mm hub motors (top at 0.166 m) and 100 mm casters (≥ 0.125 m overall) do not fit under a chassis floor at z = 0.09 m. The frame needs wheel cut-outs or a floor about 0.04 m higher. That raises the CoG about 10 mm, which costs about 1–2 mm of margin [E].

## 9. Assumptions and sources

| Quantity | Value | Label |
|---|---|---|
| UR5e mass, payload | 20.6 kg, 5 kg | S, [datasheet](https://www.universal-robots.com/manuals/latest/en/datasheets/ur5e/) |
| UR5e link masses and CoMs | DH table | S, [UR article](https://www.universal-robots.com/articles/ur/application-installation/dh-parameters-for-calculations-of-kinematics-and-dynamics/) |
| Stop times and distances, J0–J2, 33 / 66 / 100 % payload | manual graphs, pp. 19–24 | S, [UR5e user manual SW5.19](https://www.universal-robots.com/manuals/EN/PDF/SW5_19/user-manual-UR5e-PDF_online/710-965-00_UR5e_User_Manual_en_Global.pdf) |
| Stop category reactions: E-stop → cat 1, safeguard stop → cat 2, limit violation / fault → cat 0; "load independent of stop category" | — | S, same manual, 10.2.2 and 6.2 |
| Stand loads in stops (incl. ×2.5) | Mxy 750 N·m, Fxy 910 N | S, same manual, 6.2 |
| Wrist stop deceleration | as J2 | E |
| Hub motor ZLLG65ASM500 V2.0 | 4.85 kg, 10 / 30 N·m, 200 kg per 2, PU 70A, Ø165 | S, [ZLTECH datasheet](https://www.zlingkj.com/Data/zlingkj/upload/file/20240102/ZLLG65ASM500%20V2.0%E5%8D%95%E5%87%BA%E8%BD%B4.pdf) |
| ZLAC8015D E-stop behaviour (coast or brake) | ND | Manual text not extractable |
| PGC-140-50 | 1 kg | S (as recorded in `hardware.py`) |
| Floor μ, PU on tile | 0.5 dry / 0.2–0.3 wet | E. Qualitative support only ([Gallagher](https://gallaghercorp.com/polyurethane-vs-rubber-wheels/): PU loses grip when wet); measure on site (#11) |
| Bumper / cabinet force | ≤ 250 N | E (`mobile.py`), sensitivity 100 N |
| Caster trail | 35 mm | E |
| Tether | 20 N at 0.10 m | E, `mobile.py` design cap |
| Rocking mode | 3–8 Hz, ζ 0.05 | E |
| Stir spatula force | p95 5.6 N, max 24.9 N | M, `results/r15/stir_h_scrape_dice.json` |
| Food, water and object masses | `r19smooth.load_parts` | project values |

## 10. Not checked / open

- **Measurements still needed:**
  - floor μ, dry and wet, on the user's tiles;
  - a tap test for the cart's rocking frequency and damping;
  - a push test of the bumper on the real doors.
- **Mast, beam and adapter FEA and first mode** (issue step 3). Not done.
- **Wrist stop data.** None from UR.
- **The ZLAC8015D E-stop mode.**
- **Free hub moves between actions** (TCP up to 0.91 m/s in R19).
- **Station interaction forces** (knobs, lever). Only the stir process force is included.
- **Approach / grasp pieces.** Static, slow.
- **The stir law.** It is not executable as stored (velocity jumps, IK kink). The ramps added here are an assumption.
- **The elastic model.** It is a single rocking mode on an estimated stiffness, not a multibody simulation with compliant contacts.

## 11. Commands

Run from `robot_rail/sim/r10/claude`. Python is the `robot_v5/board/work/t01/.venv` interpreter; CAD uses conda env `robocasa`. Each command takes < 5 min, single process.

```
python r19cart_bom.py                                                    # BOM, sim vs BOM (5 s)
python r19cart_dyn.py ACT=wok PRO=same,fast STOPS=1 ALPHA66=0 TAG=_a     # 1.5 min
python r19cart_dyn.py ACT=wok PRO=fastcart STOPS=1 ALPHA66=1 TAG=_b      # 1.7 min
python r19cart_dyn.py ACT=wok PRO=none STOPS=0 ASWEEP=.15,.3,.5,.8,1.2 TAG=_sweep
python r19cart_dyn.py ACT=spider PRO=same,fast STOPS=1 ALPHA66=0 TAG=_a
python r19cart_dyn.py ACT=spider PRO=fastcart STOPS=1 ALPHA66=1 ASWEEP=.15,.3,.5,.8,1.2 TAG=_b   # 2.5 min
python r19cart_dyn.py ACT=spatula PRO=same,fast,fastcart STOPS=1 ALPHA66=0 ASWEEP=.15,.3,.5,.8,1.2   # 3.2 min
python r19cart_dyn.py ACT=lid PRO=same,fast,fastcart STOPS=1 ALPHA66=0
python r19cart_dyn.py ACT=lid PRO=none STOPS=0 ASWEEP=.15,.3,.5,.8,1.2 TAG=_sweep
python r19cart_dyn.py ACT=lever PRO=same,fast,fastcart STOPS=1 ALPHA66=0
python r19cart_dyn.py ACT=stir STIRK=1,1.25 STOPS=1 ALPHA66=1 TAG=_a
python r19cart_dyn.py ACT=stir STIRK=1.5,2 STOPS=1 ALPHA66=1 TAG=_b
python r19cart_options.py PART=opt CASES=wok:fastcart,wok:fast
python r19cart_options.py PART=opt CASES=spider:fastcart,stir:k1
python r19cart_options.py PART=jerk
python r19cart_report.py                                                 # tables -> results/r19/cart/summary.json
<robocasa python> r19cart_cad.py cad/r19_cart                            # STEP / STL / CAD masses
```

Run logs are in `results/r19/cart/logs/`.
