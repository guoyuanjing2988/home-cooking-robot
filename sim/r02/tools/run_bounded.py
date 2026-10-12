"""One foreground CPU worker, 1900 MiB working-set ceiling, <20 minute timeout."""
import ctypes, ctypes.wintypes as wt, json, os, pathlib, subprocess, sys, time
ROOT = pathlib.Path(__file__).resolve().parent
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ['TEMP'] = os.environ['TMP'] = str(ROOT / 'audit' / 'temp')
pathlib.Path(os.environ['TEMP']).mkdir(exist_ok=True)
class PMC(ctypes.Structure):
    _fields_ = [('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong),
        ('PeakWorkingSetSize',ctypes.c_size_t),('WorkingSetSize',ctypes.c_size_t),
        ('QuotaPeakPagedPoolUsage',ctypes.c_size_t),('QuotaPagedPoolUsage',ctypes.c_size_t),
        ('QuotaPeakNonPagedPoolUsage',ctypes.c_size_t),('QuotaNonPagedPoolUsage',ctypes.c_size_t),
        ('PagefileUsage',ctypes.c_size_t),('PeakPagefileUsage',ctypes.c_size_t)]
class PE(ctypes.Structure):
    _fields_=[('dwSize',wt.DWORD),('cntUsage',wt.DWORD),('pid',wt.DWORD),('heap',ctypes.c_size_t),('module',wt.DWORD),('threads',wt.DWORD),('parent',wt.DWORD),('priority',wt.LONG),('flags',wt.DWORD),('exe',wt.WCHAR*260)]
kernel=ctypes.windll.kernel32
kernel.CreateToolhelp32Snapshot.restype=wt.HANDLE
kernel.OpenProcess.restype=wt.HANDLE
kernel.CloseHandle.argtypes=[wt.HANDLE]
psapi=ctypes.windll.psapi
psapi.GetProcessMemoryInfo.argtypes=[wt.HANDLE,ctypes.POINTER(PMC),wt.DWORD]
def process_tree(root_pid):
    snap=kernel.CreateToolhelp32Snapshot(2,0)
    pe=PE();pe.dwSize=ctypes.sizeof(pe);parents={};names={}
    kernel.Process32FirstW.argtypes=[wt.HANDLE,ctypes.POINTER(PE)]
    kernel.Process32NextW.argtypes=[wt.HANDLE,ctypes.POINTER(PE)]
    ok=kernel.Process32FirstW(snap,ctypes.byref(pe))
    while ok:
        parents[pe.pid]=pe.parent;names[pe.pid]=pe.exe
        ok=kernel.Process32NextW(snap,ctypes.byref(pe))
    kernel.CloseHandle(snap)
    selected={root_pid}
    while True:
        expanded=selected|{pid for pid,parent in parents.items() if parent in selected}
        if expanded==selected:break
        selected=expanded
    return {pid:names.get(pid,'terminated') for pid in selected}
name, seconds, *command = sys.argv[1:]
seconds = int(seconds)
assert 0 < seconds < 1200
start = time.monotonic(); peak = 0; reason = None; observed={}
with (ROOT/'audit'/f'{name}.log').open('w',encoding='utf-8') as log:
    proc = subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env=os.environ.copy())
    while proc.poll() is None:
        # Windows venv python.exe is a redirector; monitor its real worker too.
        for pid,exe in process_tree(proc.pid).items():
            handle=kernel.OpenProcess(0x0400|0x0010,False,pid)
            pmc=PMC();pmc.cb=ctypes.sizeof(pmc)
            if handle:
                if psapi.GetProcessMemoryInfo(handle,ctypes.byref(pmc),pmc.cb):
                    measured=pmc.PeakWorkingSetSize/2**20
                    peak=max(peak,measured)
                    old=observed.get(pid,dict(exe=exe,peak_working_set_MiB=0))
                    old['peak_working_set_MiB']=round(max(old['peak_working_set_MiB'],measured),2);observed[pid]=old
                kernel.CloseHandle(handle)
        if peak > 1900: reason = 'memory'
        if time.monotonic()-start > seconds: reason = 'timeout'
        if reason:
            subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'],stdout=log,stderr=log,timeout=15)
            proc.wait(timeout=15); break
        time.sleep(.2)
record = dict(command=command,timeout_s=seconds,elapsed_s=round(time.monotonic()-start,3),
    peak_working_set_MiB=round(peak,2),memory_limit_MiB=1900,exit_code=proc.returncode,termination=reason,
    workers=1,cpu_only=True,processes_observed=observed,memory_scope='Each child and descendant, including Windows venv redirector/real worker; max per-process OS PeakWorkingSet sampled every200ms.')
(ROOT/'audit'/f'{name}.resource.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record)); sys.exit(proc.returncode or (124 if reason else 0))
