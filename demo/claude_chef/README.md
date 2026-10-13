# Claude chef (Build Day demo, 2026-10-13)

Claude Opus 5.5 cooks Wang Gang's 西红柿炒蛋 with the robot, one decision at a time. It works from the recipe in his words, the thermometer and the wok camera only. A deterministic gate checks every call before anything moves.

| File | What |
|---|---|
| `cook_api.py` | Skills (13 primitives) and **routines** (12 predefined sequences that run without a pause for a decision); the gate; the kitchen state. Each skill names its sim evidence or is flagged `unverified`. |
| `cook_model.py`, `wok_cam.py` | The hidden wok model (heat, egg set and brown, tomato soft, sauce gel and lumps) and the hood camera that renders it with MuJoCo. Claude never sees the numbers. |
| `chef_agent.py` | The loop: `claude -p --json-schema` per decision. Flags: `--realtime` (the cooker keeps running while Claude thinks), `--resume` (replay a recorded run, then continue). |
| `score.py` | 7 hidden checks. |
| `make_demo.py`, `make_gifs.py`, `routine_gifs.py`, `make_routine_page.py` | Videos, motion GIFs, per-routine and per-step wok GIFs, and the routine catalogue page. |
| `runs/run0N/run.json` | Every decision, gate result and hidden state per step. |
| `PITCH.md` | The 3-minute talk. |

| Run | Mode | Decisions | Claude thinking | Checks |
|---|---|---|---|---|
| run01–03 | step by step, time paused while Claude thinks | 56 / 48 / 48 | (not counted) | 7/7 |
| run04 | real time, primitives only | 41 | 798 s | 6/7: starch lumps. Claude released the starch water, then thought for ~10 s before stirring |
| run05 | real time, 9 routines | 25 | 252 s | 7/7 |

**Layout.** The scripts expect the Mac workspace layout: `build_day/` next to `robot_rail/` (a copy of this repo's `sim/` tree, run with MuJoCo 3.2.5 + mink 0.0.13) and `routines/`. They are kept here for reference and reproduction.

**Not simulated:** liquids, cutting, single-piece flips; the eggs are beaten by the user. Bowl and cup pours into the wok are checked as poses only, not as continuous paths (issue #9).
