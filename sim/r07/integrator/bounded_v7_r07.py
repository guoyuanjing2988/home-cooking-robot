"""Four-slot OS-held semaphore around the unchanged bounded CPU runner."""
import os,sys,runpy,msvcrt,json,time
from pathlib import Path
H=Path(__file__).resolve().parent;folder=H/'audit/v6_worker_slots';folder.mkdir(exist_ok=True)
held=None
for i in range(4):
 f=(folder/f'{i}.lock').open('a+b')
 if f.tell()==0:f.write(b'0');f.flush()
 f.seek(0)
 try:msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)
 except OSError:f.close();continue
 held=f;slot=i;break
if held is None:raise SystemExit('Four numerical workers already active; no fifth job launched')
name=sys.argv[2];record=dict(slot=slot,supervisor_pid=os.getpid(),acquired_unix=time.time(),limit=4)
try:runpy.run_path(str(H/'bounded_v4_r07.py'),run_name='__main__')
finally:
 record['released_unix']=time.time();(H/'audit'/f'{name}.slot.json').write_text(json.dumps(record,indent=2));held.seek(0);msvcrt.locking(held.fileno(),msvcrt.LK_UNLCK,1);held.close()

