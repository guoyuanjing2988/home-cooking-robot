"""Sequential final connection, result assembly, measured export and CPU renders."""
import subprocess, sys, time
from pathlib import Path
H = Path(__file__).resolve().parent
ID = sys.argv[1]
started = time.monotonic()
for args in (
    ['connections_batch_v6_r07.py', ID, '3', '4'],
    ['prepare_delivery_v6_r07.py', ID],
    ['measure_export_v6_r07.py', ID],
    ['render_batch_v6_r07.py'],
):
    remaining = 1050 - (time.monotonic() - started)
    if remaining < 180:
        print('ASSEMBLY_DEFERRED', args, flush=True)
        break
    print('ASSEMBLY_STAGE', args, flush=True)
    subprocess.run([sys.executable, '-B'] + args, cwd=H,
                   timeout=remaining, check=True)
print('ASSEMBLY_CHUNK', round(time.monotonic()-started, 2), flush=True)
