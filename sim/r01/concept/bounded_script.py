"""Run one foreground CPU command with a hard wall-time and memory bound."""
import os,sys,time,subprocess,json,argparse
from pathlib import Path
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[n]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import checker as ck
HERE=Path(__file__).resolve().parent
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--seconds',type=int,default=1140);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
    if not 0<a.seconds<1200:raise ValueError('Chunks must be under 20 minutes')
    cmd=a.command[1:] if a.command and a.command[0]=='--' else a.command
    temp=HERE/'temp';temp.mkdir(exist_ok=True);os.environ['TEMP']=str(temp);os.environ['TMP']=str(temp)
    if 'blender' in Path(cmd[0]).name.lower():
        for key,folder in (('BLENDER_USER_CONFIG','blender_config'),('BLENDER_USER_SCRIPTS','blender_scripts')):
            target=HERE/'renders'/folder;target.mkdir(parents=True,exist_ok=True);os.environ[key]=str(target)
    out=HERE/'audit'/a.name;out.parent.mkdir(exist_ok=True);start=time.monotonic();peak=0
    with out.with_suffix('.log').open('w',encoding='utf-8') as f:
        proc=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT)
        try:
            while proc.poll() is None:
                peak=max(peak,ck.tree_peak_memory(proc.pid))
                if time.monotonic()-start>a.seconds:raise TimeoutError(a.name)
                if peak>1900:raise MemoryError(a.name)
                time.sleep(.5)
            if proc.returncode:raise RuntimeError(out.with_suffix('.log').read_text()[-3500:])
        finally:
            if proc.poll() is None:ck.kill_tree(proc)
    record=dict(command=cmd,elapsed_s=time.monotonic()-start,peak_MiB=peak,exit_code=proc.returncode,timeout_s=a.seconds)
    ck.json_write(out.with_suffix('.resource.json'),record);print(json.dumps(record))
