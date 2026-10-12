import subprocess,sys,time
ID=sys.argv[1];start=time.monotonic()
for script in ('rules_v4_r07.py','sequence_v4_r07.py','fold_task_v4_r07.py'):
 remain=1060-(time.monotonic()-start)
 if remain<30:break
 subprocess.run([sys.executable,'-B',script,ID],check=True,timeout=remain)
