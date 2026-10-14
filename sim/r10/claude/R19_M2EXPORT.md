# R19 m2 export: every adopted m2 set exported and densely re-checked with the cable (GitHub #6 / #42, Windows, 2026-10-14)

**Unchanged:** `r19export.py` (format `r19export/1`, time law, writers, re-check rules, R19_EXPORT.md), gates, checker.

## Answer first
- **81 exports, 0 hits:** UR5e 40 (20 sets + 20 hub edges), 78,661 re-checked states; FR5 41 (19 sets + 22 hub edges), 84,805 states. Every re-check is `ok`, with the m2 cable option (`<base>c_yp_a-45_m2tc`) in every scene.
- **Sets:** the 6 cooking chains, every prep set (the two cable-aware ct2s files), the stir short-push library. Not exported: the stir join (`lib_stir_join_*`, a 0.7–1.3 s self-motion; r19export has no join kind yet).
- **Thinnest re-check reserves (above the gates):** UR5e ct2s 0.29 mm; press and tomato 1.0 mm on both arms; fold / unfold 1.97–1.98 mm.
- **Times:** the exported (limit-respecting) durations are longer than the stored plan times on most prep sets, e.g. UR5e basket 34.9 → 61.5 s, ct2s 29.7 → 46.6 s, tubfill 45.3 → 53.6 s; the cooking chains change little (wok 48.9 → 52.6 s, spatula 26.9 → 22.4 s). The per-set table is `results/r19/export/summary.json`.

## How (new file `r19m2export.py`; r19export.py executed from its source with replacements)
1. m2 cooking chains (no r19enc `adopted` block) take their pot-zone certificate `results/r19/mount/check_<chain>_rack_sp1.56_.20.json` and are re-checked in that scene (`r19pot_check.ctx`, RACK=keyed, spider rest 1.56 / .20, PY .15); their fit tolerance is uniform from the certificate's minimum reserve.
2. Hub scenes get the kitchen19pot layer, as when the m2 edges were planned (`r19fr5_hub.py`).
3. `ARMX=1`: every scene is built with the m2 cable option.
4. Both m2 arms relabel their chains by their own hub roadmap (`results/r19/fr5/hub_py.15_<arm>/hubs.json`), so chains and edges carry the same 2pi labels.
5. m2 prep sets with a `_verify4mm_pot.json` certificate (fold, unfold, stgwok, ct2s) are re-checked with `r19prep5_verify` (r19export picks the verifier by folder).
- Two re-checks hit out-of-memory while both arms ran in parallel (UR5e tubempty, FR5 tomato); re-run alone, ok.

## Files
- `results/r19/export/<name>/` (export.json, states.npz, stream.csv, ur_servoj_500hz.csv or the FR5 file, recheck.json); `results/r19/export/summary.json`; logs in `results/r19/export/m2logs/`.
- Lanes: `scratchpad/lanes/m2_export.sh` (exports) and `m2_recheck.sh` (re-checks).

## Addendum (2026-10-14): the stir join exported (kind 'join', point 6 of `r19m2export.py`)
- The STIR_JOIN library entries (`results/r19/stir/lib_stir_join_<arm>.json`) export as one motion piece: the stored certified geometry unchanged, checked in the stir scene (jaw −1, plume rule, cable option), timed by the export's own rest-to-rest law. `REVERSE=1` gives STIR_EXIT.
- **4 exports, 0 hits:** UR5e m2 entry / exit 112 states each, 1.28 s (stored 1.284 s); FR5 m2 entry / exit 26 states each, 0.69 s (stored 0.69 s). State fit 0.0000 mm; min environment reserve 5.71 mm (blade vs wok); limit ratios ≤ 0.95.
- Summary now 132 rows (`results/r19/export/summary.json`). Logs `results/r19/export/m2logs/exp_join_*`, `rc_join_*`.
- #7 (R19_MESHLATE.md) re-checked 25 of these exports again on the exact held-box model: unchanged.
