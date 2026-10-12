# R09 mobile cart feasibility package

This is a failed carrot-first feasibility result, with eleven documented structural iterations. Only saved, fully checked local paths earn local-stroke credit. No food state, completed product or end-to-end connection is credited. Read `results/final_reply.txt`, `results/delivery_audit.json`, and the Chinese/English post at `../../../posts/r09/integrator.md`.

The selected configuration is M11: a fixed 850 mm arm mount, canted 20 degrees, a 660 x 500 mm cart with four powered wheels and secured ballast, and a mains tether in a guarded floor guide. No battery or height axis is modeled. The assumed parking alcove is not demonstrated by the kitchen photos. Hardware prices are explicitly historical references or unquoted China planning allowances.

## Modules

- `scene.py`: complete kitchen, retained OEM arm, full gripper housing, cart, full stations, foods, bowls, reel and cable-guide solids. `models/base.xml` is local; no previous-round builders execute.
- `checker.py`: read-only import of the actual R05 reference, with canonical rotation/attachment identities and named contact capabilities. Every working capability spans at most 50 mm. Four consecutive capabilities cover the unchanged 200 mm mandoline stroke.
- `solver.py`: at least 96 real IK starts per endpoint. Each start samples base x/y/yaw and freezes them while solving the six arm joints.
- `planner.py`, `parking.py`: bounded replay, RRT restarts, staging and shortcuts; fold/drive/unfold decomposition. Base movement requires a frozen carry posture, footprint/cable checking and a nonholonomic chord constraint.
- `point_bound.py`, `distance.py`: inherited geometry displacement bound and conservative distance support queries. Native reference contacts are never silently discarded.
- `mobile.py`: full footprint, physical cable branch envelope, level-floor support polygon, gravity/process/payload/cable tip calculation. The final audit includes a 1.5 factor on moving-arm and held gravity.
- `state.py`: transactional conserved food transformations and path commit that rebuilds the scene and replays every state. Caller `ok` flags and Cartesian positions cannot authorize a commit. No production state commit occurred.
- `run.py`, `refine.py`, `execute.py`: numerical experiments. `replay.py` and `replay_routes.py` independently recheck admitted outputs under the final strengthened stability/cable model.
- `hardware.py`, `report.py`, `visuals.py`: traceable bill of materials, honest metrics and CPU renders.

## Reproduction

Use `C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe` as `PY`. Launch each job through `PY bounded.py TIMEOUT NAME PY SCRIPT ...`, from this package or with full relative paths. The guard logs CPU-only execution, elapsed time, exit status and peak working set, kills above 1900 MiB and requires a timeout below 1200 seconds. Run at most four numerical workers simultaneously.

1. `bootstrap.py`; `envelope.py 0` and `envelope.py 20`, each with 180-second guard.
2. `batch.py 1 2 3 4` and `batch.py 5 6 7 8`, each with 900-second guard. These early design screens used the initial cart wheel proxies; they are not evidence for the final sourced drive dimensions.
3. `refine.py M09`, `refine.py M10`, `refine.py M11`, sequentially, 480 seconds each. M09 replaces the wheel envelopes/masses; M11 is authoritative. Keep the final `selected.json` on M11.
4. `batch_execute.py stroke 0 1 2`, `... stroke 3 4 5 6`, `... stroke 7 8 9 10`, each with 1140 seconds; `parking.py search`, 240 seconds.
5. `batch_execute.py connection 0 1 2`, `... connection 3 4 5 6`, `... connection 7 8 9`, each with 1140 seconds. Each attempted fold, base move and unfold has at least a 60-second planner budget. `parking.py idle`, 480 seconds.
6. `replay.py 0 1 2 3 4 5 6 7 8 9 10`, 900 seconds; `replay_routes.py`, 900 seconds; `design_map.py`, 600 seconds; then `replay_maps.py`, 300 seconds.
7. `verify.py`, `hardware.py`, `report.py`, then `visuals.py` and `post.py`, with 60/60/120/300/60-second guards respectively.

Intermediate pilots remain in `results/pilot`; they do not count as final admissions. Numerical searches are finite and do not prove architecture-wide infeasibility. Reproduction with the final stronger cable and dynamic-gravity gate can reject a pilot earlier; final replay is the authority.

The saved interstroke searches used the safe carry pose archived in `results/pilot/upright_carry_search.json`. Their stage names `fold` and `unfold` mean enter and leave that carry pose. Final idle search and renders use the subsequently corrected, explicitly elbow-folded pose in `assets/park_mobile.json`. Neither set provides a successful connected route.

## Important limitations

The 11 carrot templates do not close the drawer, lid, holder, tray and food ownership events required for a complete meal. The state ledger consequently stays at the original 0.57 kg. Full mechanical interfaces, reel ratchet automation, drive-brake hub coupling and power-loss operation remain open. A passing parking snapshot or a local stroke does not remove these limitations. The 24-frame strip is explicitly a local mandoline replay, not an executed carrot sequence.
