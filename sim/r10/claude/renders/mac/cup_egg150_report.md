# R19 cup with beaten egg: 150 g load (Mac, 2026-10-13)

**Result: PASS.** `r19cup_chain.py` ONE=1 with the same keyframes as `chain_cup_final.json`. The only change is the load, `LIQ=.15`: cup 0.12 kg + 0.15 kg of egg = 0.27 kg held until the pour, 0.12 kg after.

| | egg150 | final (60 g liquid) |
|---|---|---|
| ok | yes | yes |
| cycle time | **20.6 s** | 20.6 s |
| min reserve (robot-environment) | **2.2 mm** | 2.2 mm |
| grasp approach / release retreat min reserve | 2.5 / 2.5 mm | 2.5 / 2.5 mm |
| meet join | 0.1 deg | 0.1 deg |
| max PGC moment | **0.02 N·m** (limit 7) | 0.01 N·m |
| max joint torque ratio | **0.464** | 0.459 |

- The playback path is identical to `chain_cup_final.json` (same 224 states). The load does not affect the IK or the checker, only the torque and moment numbers. `renders/mac/cup_pour.mp4` therefore shows this path too; it was not rendered again.
- Assumption: the egg's CoM is 2 cm above the cup bottom and fixed in the cup frame until the cup is levelled, as for the liquid. Egg slosh and pour flow are not simulated, and the 120 deg roll and 2 s dwell were not re-tuned for egg viscosity.
- Files: `results/mac/chain_cup_egg150.json`, log `logs/mac/cup_egg150.log`.
- Reproduce: `LIMIT_MB=8000 bash tools/runw.sh logs/mac/cup_egg150.log r19cup_chain.py ACT=cup TAG=egg150 ONE=1 PORTC=.05 PORT=.45,.30,1.085 SEEDS=3 TRIES=12 OUTY=none LANE=.58,.10,1.08 POUR=.79,.08,1.075 LIQ=.15`
