# R04 integrator evidence

Read [the final post](../../../posts/r04/integrator.md) first. Static phases are27/27; connected meal is FAIL. `results/cheapest.json` deliberately has no admitted configuration or price. Preparation time85.86min is an unverified resource plan.

Use `C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe` with `-B`, from the workspace root. Heavy jobs must use `bounded.py` with a timeout below1200s; keep at most4 CPU workers.

Final entry points:

- `static_audit.py`: independent selected-candidate reference replay on final geometry.
- `motion_r04.py 0 53` and `motion_r04.py 53 105`: bounded RRT-Connect internal/connection attempts.
- `passing_r04.py`: full-cell continuous swept-carriage passing route.
- `state_sequence.py`, `persistent_scene.py`: proposed single-owner ledger and conserved scene, with unsupported transitions explicitly unverified.
- `aggregate_motion.py`, `schedule_cost.py`, `research_update.py`, `bundle_r04.py`: final accounting.
- `final_audit_r04.py`: upstream hashes, force/requirement equality, resource bounds and artifact consistency.

R03 entry points retained for provenance (`report.py`, `engineering.py`, old `motion_check.py` main, old `final_check.py` main) are not the R04 pipeline. Their helper routines are reused where documented. Do not run those old mains over the final results.

`models/witnesses/` contains105 XML/q sets. `renders/manifest.json` distinguishes static pictures, the continuously verified passing route, rejected idle pictures and the unconnected storyboard. `audit/input_hashes.json` pins1690 upstream files; `audit/final_audit.json` records the latest invariant check. Cancelled trials and failed preliminary imports/serialization runs are preserved in audit logs and never counted as passes.
