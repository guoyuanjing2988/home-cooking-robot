SCOPE: review of R03 (post robot_rail/posts/r03/reviewer.md). Read DECISIONS.md, the R03 integrator post, scripts and results, and the R02 review.

Check:
1. **Rule fidelity.**
   - Diff the R03 checker against R02's reference.py and inputs/prep_checker.py.
   - Audit every intended contact: only a held object with its own support face at grasp/release, and food with its work support or tool. Anything broader is BLOCKING.
   - Confirm that solver-found poses were re-verified by the unchanged acceptance logic, and that no geometry was shrunk.
2. **Re-runs.** Independently re-verify at least 6 phases, including the hardest, and replay a section of the connected motion.
3. **Torque/brake rule.** Is the rated-payload envelope computed correctly: right payload, CoM offset, mounting orientation, workspace coverage?
4. **Process.** Is every finished product still produced, with nothing silently dropped? Do the commodity appliances really meet the cut specs (from product data)? Are the forces sourced?
5. **Layout realism.** Faucet use, cabinet doors, outlets, people's use of the counter when the robot is idle, cleaning.
6. **Home safety, power, cost and time.** Apply DECISIONS.md.

Deliver the post (Chinese summary first) with:
- a **Verdict**: phases, motion, cost, prep time, and whether to proceed to detailed design and a bench prototype;
- **Findings**: numbered, with severity;
- **Next steps**, including the most valuable physical tests.

Final reply: `DONE r03_reviewer phases=<passed>/<total> motion=<pass|fail> cost_cny=<value> proceed=<yes|no> findings=<n>`.
