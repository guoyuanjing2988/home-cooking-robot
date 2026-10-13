"""The only way this project talks to Claude: headless Claude Code (`claude -p`) on the user's subscription.

  claude -p "<prompt>" --model claude-opus-5-5 --json-schema '<schema>' --output-format json
         --allowedTools Read --no-session-persistence
run with stdin=/dev/null from an empty scratch dir. Images are passed as file paths the model opens with Read.
Every call is appended to a JSONL ledger (seconds, cost, turns, purpose).
"""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORK = ROOT / 'claude_work'              # empty cwd for every call
LEDGER = ROOT / 'logs' / 'claude_calls.jsonl'
MODEL = 'claude-opus-5-5'


def claude_json(prompt: str, schema: dict, tag: str, images=(), purpose='decision', effort='medium',
                timeout=300, retries=1):
    """One structured Claude call. Returns (obj | None, meta)."""
    WORK.mkdir(parents=True, exist_ok=True)
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    if images:
        prompt += '\n\nImages (open each with the Read tool before answering):\n' + '\n'.join(
            str(Path(p).resolve()) for p in images)
    meta = dict(tag=tag, purpose=purpose, prompt_chars=len(prompt), n_images=len(images), attempts=0)
    obj = None
    t_all = time.time()
    for attempt in range(retries + 1):
        meta['attempts'] = attempt + 1
        cmd = ['claude', '-p', prompt, '--model', MODEL, '--effort', effort, '--json-schema', json.dumps(schema),
               '--output-format', 'json', '--allowedTools', 'Read', '--no-session-persistence']
        for d in {str(Path(p).resolve().parent) for p in images}:
            cmd += ['--add-dir', d]
        try:
            p = subprocess.run(cmd, cwd=str(WORK), stdin=subprocess.DEVNULL, capture_output=True,
                               timeout=timeout, check=False)
            out = json.loads(p.stdout.decode(errors='replace') or '{}')
        except subprocess.TimeoutExpired:
            meta['error'] = 'timeout'
            continue
        except json.JSONDecodeError as e:
            meta['error'] = f'bad cli output: {e}'
            continue
        meta['cost_usd'] = meta.get('cost_usd', 0) + (out.get('total_cost_usd') or 0)
        meta['turns'] = out.get('num_turns')
        obj = out.get('structured_output')
        if obj is None and out.get('result'):
            try:
                obj = json.loads(out['result'])
            except json.JSONDecodeError:
                meta['error'] = f"no structured output: {out['result'][:200]}"
        if obj is not None:
            break
    meta['seconds'] = round(time.time() - t_all, 2)
    meta['ok'] = obj is not None
    with open(LEDGER, 'a') as fh:
        fh.write(json.dumps(dict(t=time.strftime('%Y-%m-%d %H:%M:%S'), **meta)) + '\n')
    return obj, meta


if __name__ == '__main__':
    import sys
    schema = {"type": "object", "additionalProperties": False, "required": ["items"],
              "properties": {"items": {"type": "array", "items": {
                  "type": "object", "additionalProperties": False, "required": ["name", "count"],
                  "properties": {"name": {"type": "string"}, "count": {"type": "integer"}}}}}}
    print(claude_json('List the food items or dishes you see.', schema, 'selftest', images=sys.argv[1:2], effort='low'))
