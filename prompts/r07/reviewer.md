SCOPE: review of R07 (post robot_rail/posts/r07/reviewer.md). Read DECISIONS.md, the R07 integrator post, scripts and results, and the R05 review.

Check:
1. **Rule fidelity.** Diff against R05's reference checker. Audit the contact windows (explicit kind and own identity; no working permission on non-working paths) and the wall contact. No shrunk geometry and no loosened gates.
2. **Corrected idle check.** Exactly as defined in DECISIONS.md: robot parts are clear of the door sweeps and out of the front strip and the corridor; the doors are not checked against the corridor. Replay the fold/unfold paths.
3. **Re-runs.** Independently re-verify at least 8 strokes and replay at least 20 connections, including the longest, the tightest and any two-arm overlap. Check the ≤4 mm bound.
4. **Meal conservation.** Food and container states are consistent.
5. **Arms and appliances.** Folded envelopes and payload envelopes match the datasheets. The slicer's dimensions and specs match public data.
6. **Clearance robustness, home safety, power, water, cleaning, cost and time.**

Deliver the post (Chinese summary first) with:
- a **Verdict**: strokes, connections, meal, idle, prep time, cost, and whether to proceed;
- **Findings**: numbered, with severity;
- **Next steps**.

Final reply: `DONE r07_reviewer strokes=<p>/<t> connections=<c>/<m> meal=<pass|fail> idle=<pass|fail> prep_min=<v> cost_cny=<v> proceed=<yes|no> findings=<n>`.
