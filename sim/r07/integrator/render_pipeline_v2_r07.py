import subprocess,sys
for script in ('comparison_export_v2_r07.py','render_batch_v2_r07.py'):
 p=subprocess.run([sys.executable,script],timeout=1000)
 if p.returncode:raise RuntimeError(script)
