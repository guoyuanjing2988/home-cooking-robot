from pathlib import Path
import subprocess,sys
H=Path(__file__).resolve().parent
for name,args in [('doors',[]),('idle',['L101']),('meal',['L101']),('envelopes',[]),('timing',[]),('grasp_probe',[])]:
    subprocess.run([sys.executable,'-B',str(H/('v7_'+name+'.py'))]+args,check=True,timeout=240)
