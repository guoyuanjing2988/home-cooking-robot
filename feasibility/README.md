# Feasibility gap review (2026-10-13)

Five parallel read-only reviews of `home-cooking-robot` at commit 77db1cd (R19). Each file has a gap table (status, evidence, risk, study to close, sim or hardware, effort) and its top risks.

| File | Rows | Scope |
|---|---|---|
| `gaps_mechanical.md` | 22 | cart, mass, stability, tolerances, heat exposure, fixtures, materials |
| `gaps_electrical.md` | 25 | power budget, Singapore circuits, tether, E-stop, power loss, compliance |
| `gaps_control.md` | 31 | software layers, registration, perception, recovery, runtime safety, LLM loop |
| `gaps_safety.md` | 39 | hazard analysis, hot loads near people, fire, hygiene, regulation |
| `gaps_process.md` | 29 | recipe/prep coverage, reliability, user workload, cost vs alternatives, staged path |

Spot-checked against the repo: hub edge reserves 2.0–2.3 mm (15 of 22 edges), cart modelled as exact joints, cart mass = MuJoCo box masses in `scene.py`, `r17chain.state()` checks with `mass=0`, `research/r19_asbought.md` cited in DECISIONS.md:499 but missing. Numbers marked [est] in the files are the reviewers' own estimates.
