"""Score a chef run against the hidden wok model (Claude never saw these numbers).

Usage: python score.py runs/<name>/run.json
"""
import json
import sys


def score(run):
    D = run['decisions']
    plate = run['final']['plate']
    egg = (plate.get('egg') or {}).get('state') or {}
    tom = (plate.get('tomato') or {}).get('state') or {}
    sau = (plate.get('sauce') or {}).get('state') or {}
    events = [e for d in D for e in d['truth'].get('events', []) if e.get('kind') not in ('add', 'flip')]
    kinds = sorted({e['kind'] for e in events})
    peak = max((d['truth'].get('wok_C') or 0) for d in D)
    refused = [d for d in D if not d['result']['ok']]
    checks = [
        ('egg set on both sides', min(egg.get('set', [0, 0])) >= 0.9, f"set {min(egg.get('set', [0, 0])):.2f}"),
        ('egg not burnt', max(egg.get('brown', [1, 1])) < 0.7, f"brown {max(egg.get('brown', [1, 1])):.2f}"),
        ('tomato soft', tom.get('soft', 0) >= 0.75, f"soft {tom.get('soft', 0):.2f}"),
        ('sauce thickened', sau.get('gel', 0) >= 0.6, f"gel {sau.get('gel', 0):.2f}"),
        ('no starch lumps', sau.get('lumps', 1) < 0.5, f"lumps {sau.get('lumps', 0):.2f}"),
        ('no smoke / scorch / cut-off', not kinds, ', '.join(kinds) or 'none'),
        ('plated', bool(egg) and bool(tom), ', '.join(k for k in plate if k not in ('salt', 'sugar'))),
    ]
    return dict(checks=checks, decisions=len(D), refused=len(refused), kitchen_s=run['final']['t'], peak_C=peak,
                claude_s=sum(d['claude'].get('seconds', 0) for d in D))


if __name__ == '__main__':
    s = score(json.load(open(sys.argv[1], encoding='utf-8')))
    for name, ok, detail in s['checks']:
        print(f"{'PASS' if ok else 'FAIL'}  {name:28s} {detail}")
    print({k: v for k, v in s.items() if k != 'checks'})
