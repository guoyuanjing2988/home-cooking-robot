"""Merge disjoint replay continuations, preserving the timed-out evidence."""
import sys, json, hashlib, shutil
from pathlib import Path
H = Path(__file__).resolve().parent
O = H/'results'; ID = sys.argv[1]
archive = H/'history/v7_path_retries'; archive.mkdir(exist_ok=True)
records = []
for mode, candidates in (('fold', (2, 3)), ('return', (0, 1))):
    file = O/'layouts'/f'{ID}_{mode}_high_front_v7.json'
    original_hash = hashlib.sha256(file.read_bytes()).hexdigest()
    data = json.loads(file.read_text())
    rows = []
    for candidate in candidates:
        continuation = O/'front_replay_continuations_v7'/f'{ID}_{mode}_{candidate}.json'
        row = json.loads(continuation.read_text())
        assert row['replay_continuation']['original_sha256'] == original_hash
        assert row['motion_model_sha256'] == data['model_sha256']
        assert all(edge['allocated_budget_s'] >= 60 for edge in row['edges'])
        rows.append(row)
        records.append(dict(mode=mode, candidate=candidate, pass_=row['pass_'],
            evidence=str(continuation.relative_to(H)),
            elapsed_s=row['replay_continuation']['elapsed_s'],
            completed_replays=sum(e.get('fresh_replay',{}).get('pass_',False) for e in row['edges']),
            rejected_replay_reasons=[e['fresh_replay']['blocker'] for e in row['edges']
                if e.get('fresh_replay') and not e['fresh_replay']['pass_']]))
    old = archive/(file.stem+'_before_extended_replay.json')
    assert not old.exists(), 'Merge is deliberately not repeatable over changed sources'
    shutil.copy2(file, old)
    for row in rows:
        index = next(i for i,a in enumerate(data['attempts']) if a['candidate'] == row['candidate'])
        data['attempts'][index] = row
    data['pass_'] = any(a['pass_'] for a in data['attempts'])
    data['prior_replay_limit_evidence'] = str(old.relative_to(H))
    file.write_text(json.dumps(data, allow_nan=False))
summary = dict(layout=ID, attempts=records, scope='Longer verification only; original paths, geometry and acceptance gates retained. Remaining legs receive 65 s planning.')
(O/'front_replay_continuation_summary_v7.json').write_text(json.dumps(summary,indent=2))
print('MERGED_FRONT_REPLAYS', records)
