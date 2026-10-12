"""Resume the remaining fold and raw-food unfold staging alternatives."""
import subprocess, sys, time
from pathlib import Path
H = Path(__file__).resolve().parent
started = time.monotonic()
for flags in (['--final'], ['--unfold', '--final']):
    remaining = 1050 - (time.monotonic() - started)
    if remaining < 300:
        print('FOLD_TAIL_DEFERRED', flags, flush=True)
        break
    subprocess.run([sys.executable, '-B', 'fold_v7_r07.py', sys.argv[1]] + flags,
                   cwd=H, timeout=remaining, check=True)
print('FOLD_TAIL_CHUNK', round(time.monotonic()-started, 2), flush=True)
