# R09 independent review

Read `../../../posts/r09/reviewer.md` for the Chinese summary and English verdict.
The integrator and all earlier rounds are read-only. Synthetic probes never alter
the delivery ledger or count as robot execution.

Use `C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe`
as `PY`, from the repository root:

```
PY -B sim/r09/reviewer/bounded.py 180 rules PY -B sim/r09/reviewer/review.py rules
PY -B sim/r09/reviewer/bounded.py 180 probes PY -B sim/r09/reviewer/review.py probes
PY -B sim/r09/reviewer/bounded.py 180 statics PY -B sim/r09/reviewer/review.py statics
PY -B sim/r09/reviewer/bounded.py 900 paths PY -B sim/r09/reviewer/review.py paths
PY -B sim/r09/reviewer/bounded.py 600 admissions PY -B sim/r09/reviewer/review.py admissions
PY -B sim/r09/reviewer/bounded.py 180 engineering PY -B sim/r09/reviewer/review.py engineering
PY -B sim/r09/reviewer/bounded.py 180 supplemental PY -B sim/r09/reviewer/review.py supplemental
PY -B sim/r09/reviewer/bounded.py 180 attempts PY -B sim/r09/reviewer/review.py attempts
```

Run statics before supplemental. At most four numerical workers; each guard
caps its process tree at 1900 MiB and the stated timeout. No GPU is used.
The largest numerical worker tree was 158.49 MiB; the metadata inventory used
less than 190 MiB. The longest run was 250.672 s.

`rules` reruns the 17 submitted synthetic tests and eight unchanged historical
geometry witnesses. The historical regression explicitly applies the binding
named wall-bracket mating predicate; it does not transplant R09 floor gates onto
R07's wall-mounted machines. `diffs/` retains the actual reference import diff,
the R08-to-R09 adapter diff and the reference-to-adapter source comparison.

`paths` resamples the two available complete local strokes with the global
ancestor displacement bound. It also audits all 30 attempted connection stages
and reconstructs the two saved idle direct-attempt prefixes. There is no complete
carrot or base route to replay. Absence of that evidence is a failure, not a pass.

`admissions` independently checks all 397 submitted accepted candidate/local/map
records. `engineering` recomputes tip moments for those records plus parking,
about the cart origin, and adds worst arbitrary-horizontal acceleration vectors.
`supplemental` replays the six rated-payload witnesses and independently computes
finite-difference load Jacobians at nine admitted selected endpoints.

The initial reviewer rules log used bare reference contacts before applying the
authorized wall-mating adapter; `rules_final` is authoritative. The initial live
support-rotation probe did not rebuild MuJoCo constants for world-fixed geometry;
`probes_final` corrects that diagnostic and is authoritative. Both initial logs
are retained. These were reviewer harness corrections, not producer changes.

Public-source findings use the agent-reach routing skill and available web tools.
The user's workspace-only restriction overrides the skill's generic output-path
guideline. No purchase, supplier contact, messages, or physical testing occurred.
