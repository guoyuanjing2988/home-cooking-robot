SCOPE: review of R01 (post robot_rail/posts/r01/reviewer.md). Read both posts, the scripts and the results.

Check:
1. **Rule fidelity.** Diff the concept checker against inputs/prep_checker.py and inputs/mandoline_golden.py. Only robot-model plumbing and datasheet torque limits may change. Any loosened contact, force, grip or acceptance rule is a blocking finding.
2. **Re-runs.** Re-run P01, P02, P06, P13 and P14 on the best design.
3. **Model honesty.** Are the arm models, joint limits, torques, masses, payloads and grippers true to the datasheets? Is the mounting orientation allowed by the manufacturer?
4. **Realism and safety.** Rail/anchor sizing, splash and grease, people working next to the arms, power loss.
5. **Cost.** Is the comparison honest? Is the 3-arm option worth it?

Deliver the post (Chinese summary at the top) with:
- a **Verdict**: best design, phases, cost, and whether to proceed to detailed design;
- **Findings**: numbered, with severity;
- **Next steps**.

Final reply: `DONE r01_reviewer best=<arm>x<count> phases=<n>/16 cost_cny=<value> proceed=<yes|no> findings=<n>`.
