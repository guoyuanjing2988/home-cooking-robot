SCOPE: review of R02 (post robot_rail/posts/r02/reviewer.md). Read all R02 posts, scripts and results, and the R01 review.

Check:
1. **Rule fidelity.** Diff the concept2 checker against R01's checker and inputs/prep_checker.py. Any loosened contact, IK, grip or acceptance rule is a blocking finding.
2. **Force honesty.** Every new process force must trace to a source or to a sound physics estimate with margin. Spot-check at least 5 against the literature. A force tuned to pass is a blocking finding.
3. **Process completeness.** Do the new phases really produce every finished product (wash quality; cut shape, size and quality; output container)? Is any step silently dropped?
4. **Re-runs.** Re-run at least 5 phases on the best design, including the hardest.
5. **Transport realism.** Carriage capacity, switching, power and data to moving arms, braking, cleanability, wall mounting.
6. **Safety and hygiene.** Blades, appliances, people nearby, cleaning. Also electrical safety of any power track or conductor rail near the sink: voltage, IP rating, RCD, splash, and whether a household 轨道插座 is used beyond its rating (it is not rated for sliding contact under load).
7. **Safety tier.** Read robot_rail/DECISIONS.md. The user chose a **home-use safety tier** after R01. Judge safety against that tier, not against industrial-cell practice, and reprice safety accordingly (no industrial scanner, light curtain or safety PLC unless a specific hazard needs one). Blade guarding and interlocks remain mandatory.
8. **Throughput realism.** The tools role chose very slow cutting (about 0.5 mm/s feed, roughly 70 s per carrot slice). Check this against the data of real commercial and household electric slicers and dicers (cutting speeds, blade types, motor power). Estimate a realistic prep time for the reference meal. If the slow feed is an unjustified over-restriction, say so and give the defensible speed.
9. **Cost and simplicity.** Compare the R02 best with the R01 single-rail baseline and an R1 Pro (~CNY 470k). Is the extra freedom worth it?

Deliver the post (Chinese summary first) with:
- a **Verdict**: best design, phases, cost, and whether to proceed to detailed design and a physical prototype;
- **Findings**: numbered, with severity;
- **Next steps**.

Final reply: `DONE r02_reviewer best=<description> phases=<passed>/<total> cost_cny=<value> proceed=<yes|no> findings=<n>`.
