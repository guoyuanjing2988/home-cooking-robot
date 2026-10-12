import sys,subprocess
subprocess.run([sys.executable,'-B','init53_v4_r07.py'],check=True,timeout=60)
subprocess.run([sys.executable,'-B','study_aux_v4_r07.py','L53'],check=True,timeout=1050)
