# R19 rule pass: hub edges re-checked with today's new places (Mac, 2026-10-13)

**Result: all 26 edges pass, with unchanged reserves.** The edges are the 22 R19 hub edges plus the 4 new CUP edges, re-checked in the union scene with three new places added:
- the cup pad, post and cup at (0.45, 0.30, 1.085);
- the holding bowl (190 x 70 mm) at plating spot 2 (0.17, 0.13).

Every stored state was re-checked with the unchanged checker. Results:
- 0 failed states on every edge;
- every edge's min reserve and self clearance equal its stored values;
- path ends match their hub nodes.

`results/mac/hub_recheck/near_new_places.json` lists the edges that come close to the new places.

Files: `results/mac/hub_recheck/summary.json` and `recheck_<edge>.json`.

Note: this report was written from the result files. The session that ran the check was cut off by a network error before it wrote its own report.
