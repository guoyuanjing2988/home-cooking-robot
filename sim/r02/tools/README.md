R02 tools package. Canonical handover is `results/process_v2.json`: 27 logical phases,
36 ingredient-specific instances, and unchanged checker tolerances/contact rules.
The post is `../../../posts/r02/tools.md`; CAD datums are in millimetres, process
coordinates in metres relative to the counter (world Z offset +0.850 m).

Run all commands from the workspace with the specified venv interpreter:
`C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe`.
Use `run_bounded.py NAME SECONDS PROGRAM ARGS...`; it sets one CPU worker/thread,
keeps temporary files inside this package, limits working set to1,900 MiB, and
terminates at a foreground timeout below20 minutes. PROGRAM and script paths must
be absolute because the supervisor runs its child in this tools directory.

Reproduction order (one worker at a time):

1. `cad`,180 seconds: FreeCADCmd with `--user-cfg` set to the package's
   `audit/freecad_user.cfg`, then `cad/build_cad.py`. The installed executable is
   `C:/Users/admin/AppData/Local/CodexEngineeringTools/FreeCAD/FreeCAD_1.1.3-Windows-x86_64-py311/bin/freecadcmd.exe`.
2. `process`,90 seconds: sim-venv Python, `build_process.py`.
3. `finalize`,90 seconds: same Python, `finalize_spec.py`.
   Always regenerate the base before finalizing: finalization is a one-time
   assembly/datums transform, not an idempotent patch to already-finalized data.
4. `blender`,180 seconds: `C:/Program Files/Blender Foundation/Blender 4.5/blender.exe`
   `--background --factory-startup --threads 1 --python` `renders/render_layout.py`.
   The script forces Cycles CPU, ten samples,1500x840, and stores the .blend here.
5. `plan`,90 seconds: same Python, `renders/draw_plan.py`.
6. `validate`,90 seconds: same Python, `validate_delivery.py`. Inspect its JSON.
7. `post`,90 seconds: same Python, `write_post.py` (requires validation pass).
8. `cad_roundtrip`,90 seconds: FreeCADCmd with the same user config and
   `cad/audit_step.py`. Keep its independent STEP import check in audit/.
9. `seal`,90 seconds: same Python, `seal_delivery.py`, after post and STEP audit
   both exist. This verifies local report links and records final artifact hashes.

Reproduction writes only within the tools directory and `posts/r02/tools.md`.
sim/r01, inputs and robot_v5 are read-only sources. A missing qualification
measurement is an engineering gate, never a relaxed checker or invented pass.
The BOM's tools subtotal excludes optional grippers, arms, rails and person
detection. Only bowl retail is a verified selected Chinese price; machining,
imports and safety/drive integration remain allowances.
