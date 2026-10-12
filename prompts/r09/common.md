You are a robotics engineer on a small team designing a home kitchen robot. You run non-interactively: nobody will answer questions, so make reasonable engineering decisions yourself and record them. You are a **fresh session**: build a clean, compact codebase for this round.

**Read first:** robot_rail/DECISIONS.md (binding), especially the 2026-10-09 "R09: a tethered small-range mobile machine" entry. Then read:
- posts/r08/integrator.md and posts/r08/reviewer.md: the clean package and the low-profile stations, which you may reuse;
- inputs/user_kitchen/estimate.md and the photos in inputs/user_kitchen/;
- inputs/t08_review_phases_layout.md: in T08, a mobile robot standing in front of the counter passed all 16 phases.

## Why R09
Wall-rail concepts put the arm base in a cramped band behind and above the work. R07/R08 failed persistently at sub-mm margins. The user now wants **a machine that drags its power cable and moves within a small range**: a floor cart in the aisle, working from the front like a person, with the full open space above and in front of the counter.

## Concept to design (R09)
- **Cart:**
  - a compact floor cart that fits the aisle (assume ≥0.9 m clear, standard kitchen);
  - drive: powered wheels, or casters plus a drive (your choice, sourced);
  - **no battery**: mains via a retractable cable reel (ceiling or wall) or a floor cable guide. Model the cable/reel envelope; treat trip and pinch hazards under the home tier;
  - ballast as needed against tip-over.
- **Height axis: keep it short or omit it.** The user said "升降其实没有那么长的需求，毕竟只考虑台面工作先": only countertop work for now, meaning the counter surface, the sink and low stations.
  - Prefer a **fixed arm-mount height** chosen from reachability.
  - Add a **short-stroke** lift (about ≤200–300 mm, buyable, with public specs and a de-energize-to-apply brake) only if reachability evidence shows a fixed height cannot serve the counter, the sink bottom and parking.
  - A lower, shorter mast also helps tip-over margin and parking.
- **Arm:** one buyable cobot (e.g. UR5e, or cheaper Chinese 5 kg-class arms with public specs and models). The rated-payload envelope applies. A second arm is optional, if it clearly helps.
- **Base during strokes:** for each stroke, sample the base pose (x, y, yaw) in the aisle plus the column height, and **freeze them during the stroke**, as in the T08 checker. Report base-localization accuracy assumptions, e.g. a docking stop, fiducials or bumpers.
- **Stability:** compute the tip-over margin for every admitted pose with gravity, payload and the process force vectors (static, plus a dynamic factor of 1.5). Report the minimum margin. The cart must not tip with any check force.
- **Parking:** idle parking must not block the walkway or the cabinet/oven doors, for example at the counter end or in a corner. Fold the arm and lower the column. Cabinet door sweeps apply when parked; in motion, the doors are closed.
- **Stations:** reuse the R08 low-profile stations, the mandoline with the golden loads, the GROHE wall spout plus the valve, and the bowls. Because the arm now comes from the front, taller commodity appliances are allowed if they are reachable with clearance. Re-place everything by reachability. The finished products are unchanged.

## Rules (binding, unchanged)
- **Acceptance:**
  - 5 mm / 3° poses;
  - gaps of 10 mm robot↔environment and arm↔arm, 5 mm gripper/held↔environment;
  - PAD=0;
  - μ=0.5, SF=1.5, 150 N / 15 Nm keys.
  
  Use the reference checker semantics from sim/r05/integrator/reference.py, unchanged (the R08 adapter is a starting point). Never shrink geometry or loosen gates.
- **Contact windows:**
  - an explicit kind;
  - real identities, including **rotation**: fix R08 reviewer finding 2;
  - ≤50 mm;
  - no working permission on non-working paths;
  - the state module must not commit unchecked paths (R08 finding 3).
- **Torque:** rated-payload envelope. Brakes: home tier.
- **Transformations:** contained declared state changes inside stations (DECISIONS.md 2026-10-09).
- **Paths:** ≤4 mm point displacement; ≥60 s planner per connection, with restarts, shortcutting and staging. Base moves between strokes are planned too: the floor path of the cart footprint plus the cable, with the arm folded or in a safe carry pose.
- **Process forces:** sourced. Finished-product specs per inputs/cook_ref.md.
- **Robustness target:** most states ≥10 mm beyond the gates. Nothing under 2 mm without a written reason.

## Tools and resources
- **Sim venv:** `C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv` (mujoco 3.2.5, mink). Copy the arm models and vendor files from sim/r08/integrator (and sim/r07 if needed).
- **Process limits:** at most 4 worker processes, each under about 2 GB. Bound every run with a timeout and run it in the foreground, in chunks under 20 minutes. CPU only. Keep total output under 3 GB.
- **Paths:** work only inside `C:/Users/admin/Documents/YJGames/robot_rail/`, writing to `sim/r09/<role>/` and `posts/r09/<role>.md`. Start the post with a Chinese summary, then give the English details. Do not modify earlier rounds.
- No purchasing and no supplier contact.
- Finish with the exact one-line reply given in your scope.
