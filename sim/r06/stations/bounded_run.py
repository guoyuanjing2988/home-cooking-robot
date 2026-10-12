"""Foreground CPU-only timeout/Windows job-memory wrapper; one child at a time."""
import ctypes, json, os, subprocess, sys, time
from pathlib import Path
from ctypes import wintypes
HERE=Path(__file__).resolve().parent
class IO(ctypes.Structure):
    _fields_=[(n,ctypes.c_ulonglong) for n in ('ReadOperationCount','WriteOperationCount','OtherOperationCount','ReadTransferCount','WriteTransferCount','OtherTransferCount')]
class BASIC(ctypes.Structure):
    _fields_=[('PerProcessUserTimeLimit',ctypes.c_longlong),('PerJobUserTimeLimit',ctypes.c_longlong),('LimitFlags',wintypes.DWORD),('MinimumWorkingSetSize',ctypes.c_size_t),('MaximumWorkingSetSize',ctypes.c_size_t),('ActiveProcessLimit',wintypes.DWORD),('Affinity',ctypes.c_size_t),('PriorityClass',wintypes.DWORD),('SchedulingClass',wintypes.DWORD)]
class EXT(ctypes.Structure):
    _fields_=[('BasicLimitInformation',BASIC),('IoInfo',IO),('ProcessMemoryLimit',ctypes.c_size_t),('JobMemoryLimit',ctypes.c_size_t),('PeakProcessMemoryUsed',ctypes.c_size_t),('PeakJobMemoryUsed',ctypes.c_size_t)]
k=ctypes.WinDLL('kernel32',use_last_error=True)
k.CreateJobObjectW.restype=wintypes.HANDLE
k.CreateJobObjectW.argtypes=[ctypes.c_void_p,wintypes.LPCWSTR]
k.SetInformationJobObject.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD]
k.AssignProcessToJobObject.argtypes=[wintypes.HANDLE,wintypes.HANDLE]
k.QueryInformationJobObject.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD,ctypes.c_void_p]
k.CloseHandle.argtypes=[wintypes.HANDLE]
job=k.CreateJobObjectW(None,None);lim=EXT();lim.BasicLimitInformation.LimitFlags=0x100|0x200|0x2000;lim.ProcessMemoryLimit=1900*1024**2;lim.JobMemoryLimit=1900*1024**2
if not k.SetInformationJobObject(job,9,ctypes.byref(lim),ctypes.sizeof(lim)):raise ctypes.WinError(ctypes.get_last_error())
env=os.environ.copy()
for n in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:env[n]='1'
env['CUDA_VISIBLE_DEVICES']='';env['PYTHONDONTWRITEBYTECODE']='1'
choices={'build':'build.py','scene':'build_scene.py','delivery':'validate_delivery.py'}
task=sys.argv[1] if len(sys.argv)>1 else 'build'
if task not in choices:raise ValueError('Choose build, scene or delivery')
t=time.monotonic()
p=subprocess.Popen([sys.executable,str(HERE/choices[task])],cwd=HERE,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
if not k.AssignProcessToJobObject(job,wintypes.HANDLE(int(p._handle))):
    p.kill();raise ctypes.WinError(ctypes.get_last_error())
try:
    output,_=p.communicate(timeout=180)
except subprocess.TimeoutExpired:
    p.kill();output,_=p.communicate();output+='\nTIMEOUT180s'
peak=EXT();k.QueryInformationJobObject(job,9,ctypes.byref(peak),ctypes.sizeof(peak),None)
record=dict(timeout_s=180,elapsed_s=round(time.monotonic()-t,3),exit_code=p.returncode,peak_process_MiB=round(peak.PeakProcessMemoryUsed/1024**2,2),peak_job_MiB=round(peak.PeakJobMemoryUsed/1024**2,2),worker_processes=1,cpu_only=True,output=output[-12000:])
(HERE/'audit'/f'{task}_run.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
k.CloseHandle(job)
print(output[-12000:]);print(json.dumps({x:record[x] for x in record if x!='output'}))
sys.exit(p.returncode)
