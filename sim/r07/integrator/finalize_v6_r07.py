"""Merge complete reserve evidence, refresh resource rows, write post and audit."""
import csv, json, subprocess, sys
from pathlib import Path
H = Path(__file__).resolve().parent
O = H/'results'
ID = sys.argv[1]
refined = json.loads((O/'clearance_refinement_v6.json').read_text())
assert refined['layout'] == ID and refined['complete']
clear = json.loads((O/'clearance.json').read_text())
assert clear['layout'] == ID
clear['refined_reserve_assessment'] = {
    key: refined[key] for key in ('complete', 'counts', 'distribution', 'method')
}
clear['refined_reserve_assessment']['source'] = 'results/clearance_refinement_v6.json'
(O/'clearance.json').write_text(json.dumps(clear, indent=2, allow_nan=False))
with (O/'iterations.csv').open(encoding='utf-8-sig', newline='') as stream:
    reader = csv.DictReader(stream)
    fields = reader.fieldnames
    rows = list(reader)
existing = {row['id'] for row in rows if row['kind'] == 'v6_bounded_run'}
for file in sorted((H/'audit').glob('v6_*.resource.json')):
    if file.stem in existing:
        continue
    data = json.loads(file.read_text())
    values = dict(kind='v6_bounded_run', id=file.stem, starts=0,
        pass_=data.get('exit_code') == 0, budget_s=data['timeout_s'],
        actual_s=data['elapsed_s'],
        status=f"Process result only, not task admission; exit={data.get('exit_code')}, peak_MiB={data['peak_MiB']}",
        evidence=str(file.relative_to(H)))
    rows.append({key: values.get(key, '') for key in fields})
with (O/'iterations.csv').open('w', newline='', encoding='utf-8') as stream:
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
post_only = '--post-only' in sys.argv
for script in (('post_v6_r07.py',) if post_only else ('post_v6_r07.py', 'audit_v6_r07.py')):
    subprocess.run([sys.executable, '-B', script], cwd=H, timeout=900, check=True)
if post_only:
    print('POST_WRITTEN', ID, 'renders and final artifact audit still pending', flush=True)
    raise SystemExit(0)
audit = json.loads((O/'delivery_audit.json').read_text())
assert audit['artifact_fidelity_pass'], [key for key, value in audit['checks'].items() if not value]
print('FINALIZED', ID, 'artifact fidelity PASS; task outcome remains separate', flush=True)
