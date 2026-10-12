SCOPE: review of R05 (post robot_rail/posts/r05/reviewer.md). Read DECISIONS.md (including the 2026-10-08 contact-window and path-checking decision), the R05 integrator post, scripts and results, and the R04 review.

Check:
1. **Rule fidelity.**
   - Diff against R04's reference checker.
   - Audit every contact window: only the declared grasp/release support faces within ≤50 mm straight lift/approach, and food↔work tool during working strokes.
   - Wall contact only at the named bracket mating faces.
   - No geometry shrunk, no thresholds loosened.
2. **Path checking.** Verify the ≤4 mm displacement bound is computed validly. Independently replay at least 15 connections and 5 internal paths, including the longest and the tightest, and two-arm overlapping segments.
3. **Statics.** Re-verify at least 6 phases.
4. **Idle kitchen.** All doors open; front corridor clear.
5. **Schedule.** Path durations are consistent with the speed limits; there are no resource or arm–arm conflicts in overlaps.
6. **Process, safety, cost.** Apply DECISIONS.md. Products and forces unchanged; home-tier safety.

Deliver the post (Chinese summary first) with:
- a **Verdict**: phases, internal paths, connections, idle, prep time, cost, and whether to proceed to detailed design and a bench prototype;
- **Findings**: numbered, with severity;
- **Next steps**, including the physical tests that matter most.

Final reply: `DONE r05_reviewer phases=<p>/<t> connections=<c>/<m> motion=<pass|fail> idle=<pass|fail> proceed=<yes|no> findings=<n>`.
