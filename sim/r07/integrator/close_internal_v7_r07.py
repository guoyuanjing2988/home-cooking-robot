"""Finish current isolated-path diagnostics and measure the populated counter."""
import json, subprocess, sys, time
from pathlib import Path
H = Path(__file__).resolve().parent
ID = sys.argv[1]
started = time.monotonic()
jobs = []
if not (H/'results/motion_v7'/ID/'internal_53.json').exists():
    jobs.append(['failed_internal_v7_r07.py', ID, '53'])
record = json.loads((H/'results/motion_v7'/ID/'internal_17.json').read_text())
if not record['ok'] and not record.get('retry_policy'):
    jobs.append(['retry_internal17_v7_r07.py', ID])
jobs.append(['counter_v7_r07.py', ID])
for args in jobs:
    remaining = 1050 - (time.monotonic() - started)
    if remaining < 240:
        print('CHUNK_DEFERRED', args, flush=True)
        break
    subprocess.run([sys.executable, '-B'] + args, cwd=H,
                   timeout=remaining, check=True)
print('CLOSE_INTERNAL_CHUNK', round(time.monotonic()-started, 2), flush=True)
