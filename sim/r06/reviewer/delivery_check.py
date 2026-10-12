"""Read-only integrity checks, with one audit written inside reviewer."""
import ast
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
POST = ROOT / 'posts/r06/reviewer.md'
def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

text = POST.read_text(encoding='utf-8')
metrics = read(HERE / 'results/metrics.json')
assert text.startswith('中文摘要：')
findings = text.split('## Findings\n', 1)[1].split('## Next steps\n', 1)[0]
numbers = [int(x) for x in re.findall(r'^(\d+)\. \*\*(?:HIGH|BLOCKING|MEDIUM)', findings, re.M)]
assert numbers == list(range(1, 11)), numbers
assert (metrics['static_strokes_passed'], metrics['all_obligations']) == (22, 530)
assert (metrics['meal_connections_passed'], metrics['meal_connections_total']) == (1, 529)
assert metrics['unique_full_strokes_replayed'] >= 8
assert metrics['connection_review_count'] >= 20
assert metrics['maximum_stroke_point_step_mm'] <= 4
assert metrics['prep_min'] is None and not metrics['meal']
assert metrics['cost_cny'] == 277265
assert metrics['native_sources_unchanged'] and metrics['binding_inputs_unchanged']

links = re.findall(r'\[[^\]]+\]\(([^)]+)\)', text)
local = [x for x in links if not x.startswith(('https://', 'http://'))]
missing = [x for x in local if not (POST.parent / x).resolve().is_file()]
assert not missing, missing
for path in HERE.glob('*.py'):
    ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))

prov = read(HERE / 'audit/provenance.json')
unchanged = all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == digest
                for p, digest in prov['binding_hashes'].items())
assert unchanged
for item in prov['copies']:
    assert hashlib.sha256((ROOT / item['source']).read_bytes()).hexdigest() == item['sha256']
    assert hashlib.sha256((ROOT / 'sim/r06/integrator' / item['copy']).read_bytes()).hexdigest() == item['sha256']

runs = [read(p) for p in (HERE / 'audit').glob('*run.json')]
assert all(x['exit_code'] == 0 and x['elapsed_s'] < 1200 and x['peak_process_MiB'] < 1900 for x in runs)
events = [(x['start_monotonic_s'], 1) for x in runs] + [(x['end_monotonic_s'], -1) for x in runs]
active = maximum_active = 0
for _, change in sorted(events):
    active += change
    maximum_active = max(maximum_active, active)
assert maximum_active <= 4
review_bytes = sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file()) + POST.stat().st_size
assert review_bytes < 3 * 1024**3
audit = dict(post_sha256=hashlib.sha256(POST.read_bytes()).hexdigest(),
             numbered_findings=len(numbers), local_links_checked=len(local), missing_links=missing,
             upstream_hashes_unchanged=unchanged, reviewer_script_syntax='pass',
             completed_runs=len(runs), maximum_simultaneous_workers=maximum_active,
             maximum_worker_MiB=max(x['peak_process_MiB'] for x in runs),
             maximum_run_s=max(x['elapsed_s'] for x in runs), reviewer_output_bytes=review_bytes,
             strokes='22/530', connections='1/529', meal='fail', prep_min=None,
             cost_cny=277265, proceed='no', findings=10)
(HERE / 'audit/delivery.json').write_text(json.dumps(audit, indent=2), encoding='utf-8')
print(json.dumps(audit))
