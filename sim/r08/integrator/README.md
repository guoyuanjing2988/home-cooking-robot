R08 compact under-cabinet rail study. Run from the robot_rail workspace root.

Python: `C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe`.
Use `-B` for every command. The scripts never write to R05/R07.

The selected diagnostic layout is in `results/selected.json`. Do not interpret a
static pose, a disconnected link, a synthetic state test, or a render as an
executed product. The delivery is allowed by the documented-iteration stop rule.

Reproduction, in order:

1. `bootstrap.py` copies the minimal base model, two referenced OEM base meshes,
   complete bowl components, envelope and source contract. No old solver stack.
2. `bounded.py 1140 iteration01 <python> -B sim/r08/integrator/run.py iteration 1`
   repeats a 96-start, three-corridor full-scene layout screen. Run IDs 1–9 in
   separate chunks. At most four numerical workers concurrently. Writes the
   iteration JSON and ledger; `report.py` reconstructs the final ledger safely.
3. `bounded.py 1140 stroke0 <python> -B sim/r08/integrator/execute.py stroke 0`
   runs both endpoints with 96 starts each, then tries a Cartesian internal path
   if both endpoints pass. Repeat indices 0–10, at most four workers.
4. `bounded.py 180 regression <python> -B sim/r08/integrator/verify.py` reproduces
   eight R07 verdicts from four unchanged inputs and runs identity/containment
   negative probes. `audit.py` independently re-admits selected positive states.
5. `bounded.py 180 connection0 <python> -B sim/r08/integrator/execute.py connection 0`
   runs a 65-second RRT-Connect budget, with restarts, staging and shortcutting.
   Repeat indices 0–9. Endpoints that fail do not skip the allocated search.
6. `bounded.py 300 idle <python> -B sim/r08/integrator/execute.py idle` tests the
   snapshot and attempts both exact-state fold/unfold diagnostics with 65s each.
7. `bounded.py 300 render <python> -B sim/r08/integrator/render.py` creates CPU
   projections, including an explicitly unexecuted 24-candidate frame strip.
8. Run `audit.py`, `report.py`, then `post.py` through the same bounded wrapper.

Checker implementation: `checker.py` imports the actual immutable R05 reference
with a read-only metadata shim, and calls its collision, rotation and grip code.
It adds full convex distance certificates and narrowly bound contact capabilities.
`distance.py` and `point_bound.py` are unchanged selected source files. Additional
restrictions never relax reference gaps, dimensions or tolerances. Local model
metadata replaces the old import-time builder to prevent upstream side effects.

The nine layout searches and selected 11 carrot templates are a feasibility
diagnostic, not a completed four-product controller. `state.py` contains the
transactional mass/containment mechanism; physical holder, guard, drawer and
container bindings still block any committed carrot execution. The finished
product contract for all four vegetables is retained verbatim in assets.

All process timings and costs are identified as component-derived allowances or
unknowns. A null makespan is intentional. Nothing has been purchased, no supplier
has been contacted, and no physical testing has been performed.
