SCOPE: review of R08 (post robot_rail/posts/r08/reviewer.md). Read DECISIONS.md, prompts/r08/common.md (the structural decisions), the R08 integrator post, scripts and results, and the R07 review.

Check:
1. **Rule fidelity.**
   - The clean checker wrapper must keep the sim/r05/integrator/reference.py semantics. Diff it and run the regression.
   - Contact windows: kind, real identities, ≤50 mm, no working permission on non-working paths. Run your own negative probes.
   - Transformation containment. Door scope.
   - No shrunk geometry, no loosened gates.
2. **Executed sequences.** Replay the carrot sequence end to end (and any other completed product), including fold/unfold, at ≤4 mm steps. Re-verify at least 8 static strokes, including the mandoline and the wash under the jet (check the jet/basket alignment).
3. **Stations.** Low-profile and real/sourced (dimensions, blade data); forces sourced. The mandoline loads must match the golden reference.
4. **Robustness.** The reserve distribution against the ≥10 mm target, and any state under 2 mm.
5. **Idle, home safety, power, water, cleaning, cost and time.** Apply DECISIONS.md.

Deliver the post (Chinese summary first) with:
- a **Verdict**: carrot, products, strokes, connections, idle, prep time, cost, and whether to proceed;
- **Findings**: numbered, with severity;
- **Next steps**.

Final reply: `DONE r08_reviewer carrot=<pass|fail> products=<n>/4 strokes=<p>/<t> connections=<c>/<m> idle=<pass|fail> cost_cny=<v> proceed=<yes|no> findings=<n>`.
