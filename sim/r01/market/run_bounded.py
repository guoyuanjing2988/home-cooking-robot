"""Foreground subprocess watchdog. No background services; bounded time and RSS."""
import argparse, subprocess, time, json
from pathlib import Path
try:
 import psutil
except ImportError:
 psutil=None
def main():
 p=argparse.ArgumentParser();p.add_argument('--seconds',type=int,default=180);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
 assert 0<a.seconds<1200
 start=time.monotonic();child=subprocess.Popen(a.command);peak=0
 try:
  while child.poll() is None:
   if time.monotonic()-start>a.seconds: raise TimeoutError('foreground watchdog timeout')
   if psutil:
    proc=psutil.Process(child.pid)
    # These research scripts launch no child workers. Avoid enumerating every
    # system process on a busy Windows host just to measure one known child.
    try: rss=proc.memory_info().rss
    except (psutil.Error,OSError): rss=0
    peak=max(peak,rss)
    if rss>1800*1024*1024: raise MemoryError('1800MiB process-tree RSS guard')
   time.sleep(.1)
 finally:
  if child.poll() is None:
   child.kill();child.wait(timeout=5)
 print(json.dumps({'exit_code':child.returncode,'elapsed_s':round(time.monotonic()-start,3),'peak_process_tree_rss_mib':round(peak/1048576,2),'timeout_s':a.seconds,'rss_guard_available':psutil is not None}))
 return child.returncode
if __name__=='__main__': raise SystemExit(main())
