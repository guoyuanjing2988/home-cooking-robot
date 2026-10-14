# R19 #38: slicer drawer bowl → pan on the folded cradle, on the m2 mount (Windows, 2026-10-14) — NOT closed

**Unchanged:** gates, checker, every adopted set. New: `ACT=dr2s` in `r19prep5_actions.py`, round-4 handle variants (`kitchen19p4.dbh(..., kyaw)`, probes `dbk_*`).

## Answer first
- **Reach is no longer the problem.** The m2 mount fixes the step-4 reach failure at the drawer. Single-pose probes with 96 IK starts, counting good starts per pose (the old enc2 mount had 0–8):
  - UR5e m2: 9–16 at the seat, at 15 and 20 cm out, and lifted, for most cranked-handle variants;
  - FR5 m2: 2–16.
  - The knob turned 30–60° toward +x (`dbk_*`) also reaches, but its pour pose over the pan has 0 candidates. The 30°-pitched knob (`dbh_0.17_0.245_0.237_p30`) is the one that reaches both ends.
- **The set itself is not closed.** 8 rounds, 64 smoke runs, every one `ok: false`.
  - Each piece works on its own on the UR5e: pick → slid out → lifted → out from under the cabinet → lane; the pour; and the return from the drawer.
  - The pieces do not connect at the lane. The two sides arrive in arm configurations whose join moves the bowl by **50–58 mm**, against the food rule limit of 50 mm / 15°. RRT joins could not be tried, because they need both sides at one cart. With the lane cart fixed, the pick side hits the cabinet door on the way out.
  - FR5 has two further blockers: in the pour and on the pan → lane path, the **forearm meets the cable plug** (`R_pgc_cable_tc_plug`), and the forearm meets the closed cabinet door.
- **What each round taught** (logs in `results/r19/prep5/logs_dr2s/`, results `results/r19/mount/chain_dr2s_*`):
  1. The bowl must leave the cabinet **horizontally before rising**. Otherwise the handle post (top ≈ bowl bottom + 0.24 m) hits the cabinet bottom at 1.35 m. This is the `DOUT` waypoint.
  2. The lane must not pass over the slicer (top 1.05 m): the bowl floor hits `slicer_base`.
  3. A −130° roll jumps 11.6° in one step (wrist flip). The +130° roll follows.
  4. Mouth 0.16 m over the pan rim: the bowl floor or strut touches the pan body when leaving. 0.24 m clears it.
  5. Following the pick through the pour (`DCHAIN=1`) does not work. The 0.45 m cart travel plus the change of bowl yaw needs a 60–95° arm reconfiguration.

## Next (in order)
1. A **pour-side waypoint** that matches the pick side's lane posture: lane yaw = pour yaw (`LYAW=90`), with the lane directly above the pan approach. Or make the lane a planned carry, as `DPC` in `r19prep4_actions`, with one shared cart for both sides.
2. A shorter handle post (kz 1.06), so `DOUT` can sit lower and nearer.
3. FR5: re-clock the plug, or route the pour on the other side of the base.
4. Fallback that needs no new set: pour the drawer bowl into a counter prep bowl at the front spot (−0.86, 0.15). That is reachable on the old mount (R19_PREP_STEP4.md §2.3), and the prep bowl then goes through the step-3 routes.

## Files
- `r19prep5_actions.py` (backup `.bak_r19drawer5`): `ACT=dr2s`. Options: `DXK DYK DZK DPD DKYAW XO DEG DYAW MOUTHZ FANG CP DUP DLANE LYAW PICKC SLC LIFTC LANEC DOUT OUTC POUR DCHAIN`.
- `kitchen19p4.py` (backup `.bak_r19drawer5`): `dbh(..., kyaw=0)`. Yaw 0 gives the same name and the same geometry as before.
- `r19prep4_probe.py` (backup `.bak_r19drawer5`): round-4 probes `dbk_*`.
- Probe results: `results/r19/prep4/probe_db[hk]_*_<m2 cable arm>.json`.
- Lanes: `scratchpad/lanes/drawer5_probe.sh`, `dr2s_smoke.sh`, `dr2s_r2.sh` … `dr2s_r8.sh`.
