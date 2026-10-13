# Claude cooks — 3-minute talk (Build Day, 13 Oct 2026)

Play `out/run05_pitch.mp4` (real time + routines, 2:07) while talking; `run03_pitch.mp4` is the step-by-step version without real time. Numbers in [brackets] are filled from the final run.

## 0:00 — Hook (20 s)
"Can Claude cook? I don't mean giving you a recipe. I mean running a robot kitchen, one decision at a time, from a thermometer and a camera, with the stove on."

## 0:20 — What you are seeing (40 s)
- Opus 5.5 controls a one-arm kitchen robot: a UR5e on a small cart in a home kitchen, simulated in MuJoCo.
- It gets 13 skills: fetch from the fridge, dose seasonings, pour, stir, flip, set the heat, tip the wok.
- It only knows what a cook would know: Wang Gang's recipe in his own words, the thermometer and the wok camera. The cooking state (how set the egg is, how thick the sauce is) is hidden from it.
- A deterministic safety gate checks every call before anything moves: heat off before the arm goes over the wok, the half-power rule, load limits.
- Real time: the kitchen does not wait while Claude thinks. Each decision takes about 10 s and the cooker keeps running.

## 1:00 — Watch it decide (50 s)
Point at the highlights as they come up:
- **Mise en place first.** It preps everything before turning on the heat: "food burns while the arm is busy".
- **The gate says no, Claude fixes it.** Too much water for a drum compartment: refused, re-planned, no harm done.
- **It plans around the robot.** Swapping the spatula takes 27 s, so Claude loads ketchup, water, starch water and finishing oil into the pour drum before the heat goes on, then adds them with the spatula still in hand.
- **It cooks by eye.** It flips the egg when the camera shows it set and golden, and thickens the sauce when the tomatoes look soft.
- **Plated, and the wok rinsed at the sink.**

Result (run05): 7/7 hidden checks passed (egg set, not burnt, tomato soft, sauce thick, no lumps, no smoke, plated), 25 decisions, 1 refused and fixed, kitchen time 20:29 including Claude's thinking.

## 1:50 — Why the robot needs routines (25 s)
- With real time on, Claude's ~10 s of thinking per step is cooking time. In run04 it released the starch water, then stopped to think before stirring, and the sauce went lumpy.
- Fix: predefined routines. "Release starch water and stir" is one sequence that runs straight through. Claude now decides at the recipe level, and the robot runs the routine.
- run05, real time with 9 routines: 25 decisions instead of 41, Claude thinking 252 s instead of 798 s, 7/7 checks, no lumps. A real kitchen needs hundreds to thousands of these routines (issue #32).

## 2:15 — The kitchen behind it (30 s)
- The robot was designed in 19 rounds over a week: R01–R09 with a Codex multi-agent board, R10–R19 with Claude Code.
- Every motion in the video is one continuous path, collision-checked at every step: the faucet, the wok to the plate and the sink, the spatula rest, the fridge door.
- What is modelled and what is not: the cooking itself is a lumped heat and kinetics model. Cutting and rinse water are not simulated. The user beats the eggs.

## 2:45 — What I built today (30 s)
- Pulled the latest design round (R19) into the demo: it corrected the stir stroke to 3.6 s and the wok clearance to 2 mm. The demo now uses those numbers.
- Real-time mode: the stove keeps running while Claude decides. That exposed the latency problem, so I added a routine layer.
- A motion gallery: every predefined, checked arm motion as a clip (README of the repo).
- A feasibility review with five Claude agents in parallel (mechanical, electrical, control, safety, process): 146 gaps, now on GitHub issues as a shared board between my Windows and Mac Claude sessions.
- The honest conclusion: the motion works in simulation; making it safe and reliable in a real home is the next, much bigger step. First step: I cook two meals by hand exactly the way the robot would, with a stopwatch.

## Backup answers
- **Why one arm?** We tried two arms first (174 kg, too heavy and expensive). One arm plus appliances (pour drum, seasoning station) covers the gaps.
- **Is it real?** It is a simulation and a feasibility study. Nothing has been bought, and no real food has been cooked yet.
- **Why an LLM here?** For the recipe-level decisions: when to flip, when it's thick enough, what to do after a refusal. The motions underneath are pre-checked; Claude never invents a motion.
