"""Foreground runner: one CPU worker, <20 min, 1900 MiB, workspace-only logs."""
import os,sys,time,subprocess,json,ctypes
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
class PMC(ctypes.Structure):
    _fields_=[('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong),('PeakWorkingSetSize',ctypes.c_size_t),('WorkingSetSize',ctypes.c_size_t),('QuotaPeakPagedPoolUsage',ctypes.c_size_t),('QuotaPagedPoolUsage',ctypes.c_size_t),('QuotaPeakNonPagedPoolUsage',ctypes.c_size_t),('QuotaNonPagedPoolUsage',ctypes.c_size_t),('PagefileUsage',ctypes.c_size_t),('PeakPagefileUsage',ctypes.c_size_t)]
def rss(pid):
    kernel=ctypes.WinDLL('kernel32',use_last_error=True);psapi=ctypes.WinDLL('psapi',use_last_error=True)
    kernel.OpenProcess.restype=ctypes.c_void_p
    h=kernel.OpenProcess(0x410,False,pid)
    if not h:return 0
    info=PMC();info.cb=ctypes.sizeof(info)
    psapi.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.POINTER(PMC),ctypes.c_ulong]
    psapi.GetProcessMemoryInfo(h,ctypes.byref(info),info.cb)
    kernel.CloseHandle.argtypes=[ctypes.c_void_p];kernel.CloseHandle(h)
    return info.PeakWorkingSetSize/1048576
class ProcessEntry(ctypes.Structure):
    _fields_=[('dwSize',ctypes.c_ulong),('cntUsage',ctypes.c_ulong),('th32ProcessID',ctypes.c_ulong),('th32DefaultHeapID',ctypes.c_size_t),('th32ModuleID',ctypes.c_ulong),('cntThreads',ctypes.c_ulong),('th32ParentProcessID',ctypes.c_ulong),('pcPriClassBase',ctypes.c_long),('dwFlags',ctypes.c_ulong),('szExeFile',ctypes.c_wchar*260)]
def tree(pid):
    k=ctypes.windll.kernel32;k.CreateToolhelp32Snapshot.restype=ctypes.c_void_p
    snap=k.CreateToolhelp32Snapshot(2,0);z=ProcessEntry();z.dwSize=ctypes.sizeof(z);parents={}
    try:
        ok=k.Process32FirstW(ctypes.c_void_p(snap),ctypes.byref(z))
        while ok:
            parents[z.th32ProcessID]=z.th32ParentProcessID
            ok=k.Process32NextW(ctypes.c_void_p(snap),ctypes.byref(z))
    finally:k.CloseHandle(ctypes.c_void_p(snap))
    found={pid}
    while True:
        more={p for p,parent in parents.items() if parent in found}
        if more<=found:break
        found|=more
    return sorted(found)
if __name__=='__main__':
    seconds=int(sys.argv[1]);name=sys.argv[2];cmd=sys.argv[3:]
    assert 0<seconds<1200
    out=Path(__file__).parent/'audit';out.mkdir(exist_ok=True)
    started=time.monotonic();peak=0
    with (out/(name+'.log')).open('w',encoding='utf-8') as f:
        p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT)
        try:
            while p.poll() is None:
                peak=max(peak,sum(rss(pid) for pid in tree(p.pid)))
                if time.monotonic()-started>seconds:raise TimeoutError(name)
                if peak>1900:raise MemoryError(name)
                time.sleep(.25)
        finally:
            if p.poll() is None:
                k=ctypes.windll.kernel32;k.OpenProcess.restype=ctypes.c_void_p
                for pid in reversed(tree(p.pid)):
                    h=k.OpenProcess(1,False,pid)
                    if h:
                        k.TerminateProcess(ctypes.c_void_p(h),1);k.CloseHandle(ctypes.c_void_p(h))
                p.wait(timeout=10)
    record=dict(command=cmd,elapsed_s=time.monotonic()-started,peak_MiB=peak,exit_code=p.returncode,timeout_s=seconds,worker_processes=1,cpu_only=True)
    (out/(name+'.resource.json')).write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(json.dumps(record))
    print((out/(name+'.log')).read_text(encoding='utf-8')[-2500:])
    sys.exit(p.returncode)
