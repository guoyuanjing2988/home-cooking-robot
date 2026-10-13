# R19 hub: seasoning-cup port endpoint CUP (Mac, 2026-10-13)

**Result: PASS.** The new endpoint CUP and 4 new edges all pass the unchanged full checker (every state, <= 4 mm point bound, union scene).

- CUP = `chain_cup_final.json` `approach_qs[0][-1]`: empty gripper, jaws open 25 mm, 6 cm in front (-y) of the cup standing on the port pad (.45, .30, 1.085), cart 0.05. Start and end of the cup chain are the same pose (one node).
- 2pi relabel of the whole cup action (all its states stay in range): pan +1, shoulder lift +1, wrist 1 -1. Largest joint move to the R19 tuck: 143.6 deg.
- Scene = the R19 union scene + the cup pad, its post and the cup on the pad. In this scene the 4 R19 hubs keep 60 mm reserve and the WOK endpoint 11.8 mm; CUP itself 2.8 mm (self 3.9 mm).

| Edge | Method | Time | Estimate (r17seq formula) | Min reserve (env / self) | States |
|---|---|---|---|---|---|
| CUP - H_WOK (home hub, cart 0.05 -> 0.172) | straight | **2.99 s** | 3.09 s | 2.0 / 2.0 mm | 895 |
| CUP - WOK (express to the wok endpoint) | via the tuck at the middle cart (straight: finger meets the cup) | **5.41 s** | 3.09 s | 2.0 / 2.0 mm | 1765 |
| CUP - H_SINK (neighbour hub) | straight | **3.52 s** | 5.52 s | 2.0 / 2.0 mm | 996 |
| CUP - SPAT (express to the spatula endpoint, cart 0.05 -> -1.48) | via the tuck at the middle cart (straight: wrist meets the closed upper door `r07_closed_door_0_1`) | **6.72 s** | 8.72 s | 2.0 / 2.0 mm | 2241 |

Peak TCP speed 0.44-0.54 m/s; highest robot point 1.62-1.82 m.

Files: `r19hub_cup.py` (copy of `r19hub.py`: `import cupobj`, CUP endpoint, pad/post/cup in the union scene, command `hubs_cup`, OUT `results/mac/hub_cup`), `results/mac/hub_cup/hubs.json` (R19 hubs + CUP), `hubs_r19.json` / `endpoints_r19.json` (copies of the R19 inputs), `edge_CUP__{H_WOK,WOK,H_SINK,SPAT}.json`, logs `logs/mac/hubcup_*.log`.

Reproduce: `LIMIT_MB=8000 bash tools/runw.sh logs/mac/hubcup_hubs.log r19hub_cup.py hubs_cup`, then `r19hub_cup.py edge A=CUP B=H_WOK` (and B=WOK, H_SINK, SPAT).

Open points:
- The 18 R19 edges were checked without the cup station. Rule 1 of R19_HUB.md says a new place means re-running them once in the scene with the pad, post and cup. Not done here. Only the 4 hubs and the WOK endpoint were re-checked as single states.
- The 2.0 mm reserve shows up on all four edges, and the self clearance is also 2.0 mm, so it looks like a fixed gripper/arm pair, not a pinch point peculiar to this path (R19's WOK spur had 2.1 mm). Not investigated.
