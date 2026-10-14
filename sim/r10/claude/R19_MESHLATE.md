# R19 #7: the R11 held-box mesh rule moved into scene.build (Windows, 2026-10-14)

**Unchanged:** gates, checker, every planned motion, r19enc_check.meshheld and the other per-script mesh passes (now no-ops where they follow build).

## Answer first
- **Fix:** `scene.build` now applies the R11 rule a second time, at its very end, after `kitchen14.add` and `arms.swap` (new `scene.meshlate`, only when `mesh_tool` is set, as the first pass). Every tool-side box that was still a MuJoCo box primitive becomes the identical 8-vertex box mesh. Geometry is unchanged; only MuJoCo's 0.5× box-box under-reading inside the contact margin goes away, so the change can only remove false hits, never add a pass that was a hit.
- `meshlate` is exactly `r19enc_check.meshheld` (same `mb19_` names and vertices). A script that already applied it after build gets a byte-identical model.
- **Regression, all 174 scene specs of the 132 exports** (`r19meshlate_md5.py`):
  - before the change: 174 / 174 rebuilt models match the md5 stored in their `recheck.json`;
  - after: 149 identical; **25 changed**, all prep play scenes whose verifier attached a held box after build (e.g. the press set's pusher stem: box → identical box mesh, nothing else in the XML differs);
  - the 25 exports on those scenes (UR5e m2 10, FR5 m2 9, old UR5e 6) were re-checked densely: **all ok, 0 hits, the same states and the same minimum reserves to 0.01 mm** as before (`results/r19/meshlate/recheck_compare.json`). The changed boxes were never the binding pair.
  - final scan with the new `recheck.json` files: 174 / 174 match.
- **Hub edges:** the two UR5e m2 edges that do not plan (SPAT→H_SPAT, SPAT→LEV_C) are **not** #7 artefacts: their scene has no tool-side box, and the blockers are the forearm against the closed door and the fingers against the spatula handle / cart beam.
- **Where the old bug could still have cost something:** planners that built a scene without a later mesh pass (e.g. r19hub, r19dock_m2, r19prep_layout) could reject a path on a held-box false hit. From now on they get the exact model from build. Old rejections are not re-run.

## Files
- `scene.py` (backup `scene.py.bak_r19meshlate`): `meshlate()` + one call at the end of `build`.
- `r19meshlate_md5.py` (new): `list` / `one` / `sum`; `NOLATE=1` builds without the late pass.
- Results: `results/r19/meshlate/{before,after,final}/summary.json`, `recheck_compare.json`, logs in `results/r19/meshlate/logs/`; the replaced re-checks are kept as `recheck.json.bak_r19meshlate`.
- Lanes: `scratchpad/lanes/meshlate_md5.sh <tag>`, `meshlate_recheck.sh`.
