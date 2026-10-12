SCOPE: review of R06 (post robot_rail/posts/r06/reviewer.md). Read DECISIONS.md, both R06 posts, the scripts and the results, and the R05 review.

Check:
1. **Rule fidelity.** Diff against the R04/R05 reference checker. Audit the contact windows: each needs an explicit kind and its own object/support identity, with no working permission on non-working paths. No shrunk geometry and no loosened gates.
2. **Re-runs.** Independently re-verify at least 8 strokes and replay at least 20 connections, including the longest, the tightest and any two-arm overlap. Check the ≤4 mm displacement bound.
3. **Meal conservation.** Food is never duplicated or lost. Every container, lid and appliance state is consistent.
4. **Appliance reality.** Do the chosen devices really exist with the stated dimensions, openings, power and controls? Can a robot really operate them (lids, pushers, interlocks)? Do they meet the cut/peel/wash specs according to product data? Flag weak evidence.
5. **Clearance robustness.** Distribution of the reserve above the gates. Is it robust enough for a real build (tolerances, deflection)?
6. **Home safety, water, power, cleaning, cost and time.** Apply DECISIONS.md.

Deliver the post (Chinese summary first) with:
- a **Verdict**: strokes, connections, meal, prep time, cost, and whether to proceed to detailed design;
- **Findings**: numbered, with severity;
- **Next steps**.

Final reply: `DONE r06_reviewer strokes=<p>/<t> connections=<c>/<m> meal=<pass|fail> prep_min=<v> cost_cny=<v> proceed=<yes|no> findings=<n>`.
