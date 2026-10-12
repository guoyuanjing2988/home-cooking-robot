"""Configuration-invariant audits for every completed reachability candidate."""
import sys,subprocess,json,time
from pathlib import Path
steps=[['mount_invariants_v2_r07.py']]+[['carriage_barrier_v2_r07.py',x] for x in ('L01','L03','L05','L07','L08','L09','L13')]
for command in steps:
 started=time.monotonic();r=subprocess.run([sys.executable,*command],timeout=90);assert r.returncode==0,command;print('AUDIT',command,round(time.monotonic()-started,2),flush=True)
Path('audit/superseded_v2_evidence.json').write_text(json.dumps(dict(superseded=[dict(path='results/layouts/L12_target_certificates.json',reason='Old negative audit mistakenly included door-sweep masks as work obstacles; do not use. Corrected L13 audit excludes those masks and reports0/105 endpoint impossibility certificates.'),dict(path='results/reachability_bad_initialization',reason='Bounds initialized before mj_forward; superseded.'),dict(path='results/reachability_opposite_arm_pair_bug',reason='Per-arm maps unintentionally retained opposite-arm/frame pairs restored by Bounds. Superseded by explicit-filter complete paired maps.'),dict(path='results/static_v2/L11',reason='Early13-start rows also had a tiny fixed-lock clipping error; retain as diagnostics, never count positive witnesses.')],source_files_unchanged=True),indent=2))
