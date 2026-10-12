import sys,subprocess,time,shutil,json
from pathlib import Path
H=Path(__file__).resolve().parent;start=time.monotonic();old=H/'history/v7_map_before_refresh';old.mkdir(exist_ok=True)
for ID in sys.argv[1:]:
 f=H/'results/reachability'/ID/'R.json';flag=H/'audit'/(ID+'_map_v7_refreshed.json')
 if flag.exists():continue
 if f.exists() and not (old/(ID+'_R.json')).exists():shutil.copy2(f,old/(ID+'_R.json'))
 remain=1040-(time.monotonic()-start)
 if remain<60:break
 subprocess.run([sys.executable,'-B','study_task_v7_r07.py',ID,'map'],check=True,timeout=remain)
 flag.write_text(json.dumps(dict(layout=ID,full151mm_cover=True,elbow_limit_deg=160,low_faucet_targets=True,new_peeler_targets=True)))
