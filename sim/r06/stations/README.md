R06 station research, 2026-10-08. Read `../../../DECISIONS.md` and `../../../posts/r06/stations.md` before integrating.

Required artifacts are `results/survey.csv`, `results/stations.json`, `results/concepts.json`, and `plans/*.png` (maximum dimension1500px). Source and BOM ledgers, product requirements, ordered event lists, nominal food catalog and event-boundary ownership ledgers accompany them.

Build with the supplied simulation venv in the workspace foreground:

```powershell
& 'C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe' sim/r06/stations/bounded_run.py
```

The runner enforces180s timeout and1900MiB per-process/job memory, one worker and CPU-only environment variables. It records `audit/build_run.json`. `build.py` writes only inside this role directory, compiles the station XML and calls `mj_forward` for initialization; it does not integrate dynamics, find IK, check gaps or plan motion.

`stations.json` boxes use full edge lengths and cylinders use radius/full height. All poses are local to named parents; quaternions arewxyz. `results/station_primitives.xml` is generated from these primitives; `initial_joints.json` contains nonzero joint initialization values. Install the arm externally using the recorded read-only local OEM model and mount, plus audited R04/R05 full collision geometry. The EOAT/jaw attachment is specified separately in JSON.

To re-export directly from a revised JSON without regenerating research, use the same foreground command with `scene` after `bounded_run.py`. To run the final delivery consistency audit, append `delivery`. Both retain the same process/time limits and write their own run logs. `build_scene.py` consumes the JSON and performs XML compilation/kinematic initialization only.

Every contact references its own runtime object/support and exact geometry or support face. Future food parts must replace their source through a conserved, continuous physical cut transition. The whole-head/whole-tomato conservative part proxies cannot earn packing or grasp acceptance. Appliance macros and boundary states are proposed contracts, not witnessed intermediate trajectories.

79/93 count supervisory events; each grasp/release is separate. Minimum named expanded operations are216/223 before repeated strokes and all pan-lid actions. No<=80 atomic-operation, path, torque, food quality or safety pass is claimed. Preserve5mm/3deg pose acceptance,10/5mm gaps,PAD0,mu.5,SF1.5,150N/15Nm key proof,<=4mm point displacement checks and>=60s planner budget per connection.

Recommended research concept: `cassette_fixed`, one fixed UR5e,45min planning estimate, CNY268985 with15% contingency. Every selected price is an engineering allowance, not a supplier quotation. No purchasing or contact occurred.
