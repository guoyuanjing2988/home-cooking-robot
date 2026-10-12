"""Validate reviewer delivery structure and evidence links; no submitted writes."""
from pathlib import Path
import ast, hashlib, json, re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
POST = ROOT / 'posts/r03/reviewer.md'
body = POST.read_text(encoding='utf-8')
findings = re.findall(r'^([0-9]+)\. \*\*(BLOCKING|HIGH|MEDIUM) —', body, re.M)
assert [int(n) for n, _ in findings] == list(range(1, 13))
assert sum(sev == 'BLOCKING' for _, sev in findings) == 3
assert re.search(r'[\u4e00-\u9fff]', body.splitlines()[0])
missing = []
local_links = []
for target in re.findall(r'\]\(([^)]+)\)', body):
    if target.startswith(('https://', 'http://')):
        continue
    path = Path(target) if re.match(r'^[A-Za-z]:[/\\]', target) else POST.parent / target
    if not path.exists():
        missing.append(target)
    local_links.append(target)
assert not missing, missing
json_count = 0
for path in HERE.rglob('*.json'):
    json.loads(path.read_text(encoding='utf-8-sig'))
    json_count += 1
scripts = []
for path in HERE.glob('*.py'):
    ast.parse(path.read_text(encoding='utf-8-sig'))
    scripts.append(path.name)
summary = json.loads((HERE / 'results/review_summary.json').read_text())
assert (summary['logical_passed'], summary['logical_total']) == (19, 27)
assert summary['independently_verified_witnesses'] == 2134
assert summary['motion'] == 'fail' and summary['proceed'] is False
assert summary['cost_cny'] == 467129.95
base = json.loads((HERE / 'results/base_collision_coverage.json').read_text())
assert len(base['main_envelope_witnesses']) == 6
assert len(base['selected_stroke_witnesses']) == 95
assert base['new_reference_blocker_strokes'] == 0
audit = json.loads((HERE / 'results/delivery_audit.json').read_text())
assert audit['unchanged_submitted_and_binding_files']
size = sum(p.stat().st_size for p in HERE.parent.rglob('*') if p.is_file())
assert size < 3_000_000_000
record = dict(post=str(POST), post_sha256=hashlib.sha256(POST.read_bytes()).hexdigest(),
              findings=[dict(number=int(n), severity=s) for n, s in findings],
              missing_links=missing, local_links_checked=len(local_links),
              json_artifacts_parsed=json_count, reviewer_scripts_AST_parsed=scripts,
              r03_total_bytes=size, summary_matches=True)
(HERE / 'results/post_validation.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
print('Delivery validated:12 findings;3 blocking;19/27;2134 witnesses;links exist;originals unchanged;under3GB.')
