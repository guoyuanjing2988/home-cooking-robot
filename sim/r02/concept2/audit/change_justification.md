Checker and model change justification

The numerical acceptance rules are inherited from R01, not reimplemented with
new limits. `reference.diff` is empty. The source AST checks cover `solve`,
`forbidden`, `bind_model`, `grip` and `target_rotation`. `adapter.diff` is a full
source-to-adapter comparison; the adapter imports the intact reference class.

| Changed responsibility | Reason and boundary |
|---|---|
| Model dispatch | Old configurations go directly to the read-only R01 builder for the baseline. New configurations replace rail/carriage and station geometry. Source arm links, hulls, joint ranges and inertias remain unchanged. |
| Real arm variants | Same/mixed xArm6, UR5e, xArm7, AUBO i5 and Franka FR3 source models are compiled. FR3/xArm7 are limited to helper comparisons; no 3 kg main-arm claim is made. |
| Rail joints | Each carriage gets frozen X; XZ adds frozen Z; switching adds a sampled discrete lane. The original solver freezes every BASE coordinate for the stroke. |
| Fourth arm | D extends the same R/L/C side classification and 10 mm between-arm rule. No new adjacent-link or ACM rule is added. |
| Parking | Unused arms sample a parked joint set and freeze it. All resulting poses still pass through the literal forbidden gate; a failed park rejects the seed. Finite searches do not prove that no other park exists. |
| Stations | New layout replaces obsolete stations; cabinet and outlet envelopes follow the supplied galley layout. Dedicated wall brackets keep the pre-existing mount exception. Fixed appliance feet are mounting pairs only in the supplementary audit; they do not waive any arm/tool contact. |
| Long rail boxes | Exact touching-box unions preserve total volume and mass. This improves contact conditioning without accepting a formerly forbidden penetration. |
| Phase inputs | All 36 handed-off instances are retained. `id` becomes instance_id for ingredient expansion. Only counter-to-world z+=0.85 m/frame conversion changes targets. `phase_contract.diff` records this. |
| Held geometry | New tool primitives carry full food envelopes. Removed destination vessels avoid duplicating the same object. C06's delivered rectangular CAD envelope resolves its circular JSON shorthand for both held and supported states; mass/COM/key capacity stay as supplied. |
| Work contacts | Exact old support identities are relocated. Original indexed families, including rinse_basket, remain intact. No whole guard, guide post, drawer or fixture exemption is introduced. |
| Door state | Loading uses the open door; only the final detached powered-cycle withdrawal closes it. This is state plumbing, not a permission to touch the door. |
| Side-specific wrench | The old R-only calculation cannot model L-only/paired phases. Each active hand contributes Jlinear-transpose F, Jangular-transpose M and held-mass gravity; the original thresholds apply. The supplied eye/core 0.262/0.524 Nm free moment is included. |
| Grip site | Each active hand uses the same mu=0.5, SF=1.5, 150 N normal/key force and 15 Nm key moment rules. The supplied free moment adds to wrench demand, rather than changing a capacity. |
| Saved-witness recheck | All original 96-seed solve witnesses are rechecked after the work-face/C06/wrench corrections. q/errors are identical; zero-moment load ratios are asserted identical. Source/output hashes and moment-case changes are recorded. No IK seed is discarded or newly optimized. |

`model.diff` records the architecture changes. `checker_contract.json` records
the input hashes, rules and unchanged core. The new geometry still fails the
literal gate; no render or reference torque result grants hardware admission.
