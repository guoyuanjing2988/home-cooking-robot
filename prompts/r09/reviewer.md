SCOPE: review of R09 (post robot_rail/posts/r09/reviewer.md). Read DECISIONS.md, prompts/r09/common.md, the R09 integrator post, scripts and results, and the R08 review.

Check:
1. **Rule fidelity.**
   - The checker keeps the sim/r05/integrator/reference.py semantics; diff it and run the regression.
   - Contact windows: kind, real identities including rotation, ≤50 mm, no working permission on non-working paths. Run your own negative probes, including rotated or forged shapes.
   - The state module cannot commit unchecked paths.
   - Base frozen during strokes. No shrunk geometry, no loosened gates.
2. **Executed sequences.** Replay the carrot sequence end to end, and any other completed product, including base moves and parking, at ≤4 mm steps. Re-verify at least 8 static strokes, including the mandoline and the wash under the jet.
3. **Stability.** Recompute tip-over margins for the worst poses with the check forces and a dynamic factor of 1.5.
4. **Hardware reality.** Cart drive, lift column, arm, gripper and cable reel are real products with public specs and prices. The cable/trip hazard is handled.
5. **Robustness.** The reserve distribution against the target.
6. **Idle parking, home safety, power, water, cleaning, cost and time.** Apply DECISIONS.md.

Deliver the post (Chinese summary first) with:
- a **Verdict**: carrot, products, strokes, connections, idle, tip margin, prep time, cost, and whether to proceed;
- **Findings**: numbered, with severity;
- **Next steps**.

Final reply: `DONE r09_reviewer carrot=<pass|fail> products=<n>/4 strokes=<p>/<t> connections=<c>/<m> idle=<pass|fail> cost_cny=<v> proceed=<yes|no> findings=<n>`.
