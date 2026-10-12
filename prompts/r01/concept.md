SCOPE: kinematic concept and the 16-phase check (robot_rail/sim/r01/concept/).

1. **Scene.** Rebuild the authoritative T08 counter layout (inputs/t08_review_phases_layout.md and inputs/prep_checker.py) as a standalone MJCF with the back wall, upper cabinets (sourced typical heights) and faucet as obstacles. Re-implement or adapt the checker so that the robot is pluggable; keep all rules unchanged (diff your checker against inputs/prep_checker.py and justify every change; only robot-model plumbing may change).
2. **Robot.** Rail(s) on the back wall; each arm on its own prismatic carriage (x along the counter). Use real arm models (Menagerie / official URDF) with their real joint limits, masses and collision geometry, plus a realistic gripper/tool-holder mass and geometry.
3. **Sweep (coarse, then refine).**
   - arm model: at least UR5e, xArm7 (or xArm6), Franka FR3 and one Chinese cobot if a model exists;
   - rail height above the counter: 0.0 (counter-level rail on the backsplash), 0.15, 0.30, 0.45 m, and hanging under the upper cabinets;
   - arm base orientation: base facing forward (horizontal), angled 30–60° down, vertical (on a shelf off the wall), inverted;
   - stand-off from the wall: 0.05–0.25 m;
   - arm count: 2 vs 3 (third arm for holding/stabilising or parallel work).
   Rank by phases passed, then torque/reach margins, then simplicity and cost.
4. **For the best 1–2 designs:** run all 16 phases with ≥96 seeds each (and the golden mandoline check adapted the same way). Report per phase the feasible seeds and the best torque ratio vs the arm's datasheet ratings, and where a third arm changes the result. Explain in one paragraph why the earlier humanoid-arm wall rail failed (0/16) and why this one does or does not.
5. **Loads:** worst static carriage force and moment on the rail and per-carriage drive force, as inputs for mounting.
6. **Renders** (≤1600 px, CPU): the best design washing at the sink, peeling, mandoline slicing, and parked; plus one overview image.

Deliver results/sweep.csv, results/best.json, renders, and robot_rail/posts/r01/concept.md.
Final reply: `DONE concept best=<arm>x<count> phases=<n>/16 rail_height_m=<value> mount=<orientation> max_rail_moment_Nm=<value>`.
