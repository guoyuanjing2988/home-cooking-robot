# R05 reference meal integration

The requested connected meal is **not achieved**. Read `results/motion.json`
and `../../../posts/r05/integrator.md` for scope-qualified counts and failures.
An isolated template path is not a conserved meal execution. `prep_min=null`
and `cheapest_passing_cny=null` are deliberate.

R04 is copied unchanged under `upstream_r04/`. The original `reference.py`
is byte-identical to R04 and R02. All edits are confined to this R05 tree.

Use the supplied Windows Python environment with `-B`:

```powershell
$r05Python = 'C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe'
& $r05Python -B -u sim/r05/integrator/bounded.py 600 statics_replay $r05Python -B -u sim/r05/integrator/statics_r05.py
& $r05Python -B -u sim/r05/integrator/bounded.py 120 checker_validation $r05Python -B -u sim/r05/integrator/validate_r05.py
```

`chunk4.py` accepts up to four `internal:lo:hi` or `connection:lo:hi` jobs.
Ranges are half-open. Cover internal0:105 and connection0:104 in bounded
chunks; use at most four numerical workers total, including other jobs.
The saved attempts include exact-pose and offset-grasp retries. Each RRT search
has65 seconds and restarts; a coarse proposal receives a separate180-second
full4mm verification budget. `grasp_variant_r05.py lo hi` tests full-food
30mm grasp offsets with compensated TCP targets and unchanged force bounds.

Generate state data with `sequence_r05.py` and `persistent_scene.py`, aggregate
with `aggregate_r05.py`, and freshly replay positive paths with
`verify_paths_r05.py lo hi` and `verify_connections_r05.py`. Then aggregate
again. `jaw_events_r05.py lo hi` produces subordinate stationary-jaw probes,
not completed meal events.

Run `idle_r05.py --repair`, then `idle_path_r05.py`, `doors_r05.py` and
`storage_loads_r05.py`. The final deployment and complete person corridor fail.
Run `schedule_r05.py`, `failure_tables_r05.py`, `renders_r05.py`; render scene
files with `render_chunk.py` in sequential groups under20 minutes; assemble
with `strip_r05.py`. Finish with `write_post_r05.py`, then
`delivery_audit_r05.py`. Wrap numerical jobs in `bounded.py` with a timeout
strictly below1200 seconds. Blender uses one CPU thread.

The overview, parked view and24-frame strip are diagnostic snapshots of full
compiled geometry, explicitly labelled unexecuted. They are not an executed
meal video. Resource/provenance evidence is retained under `audit/` and
`results/delivery_audit.json`.
