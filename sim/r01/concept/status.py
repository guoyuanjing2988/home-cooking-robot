import os,json,ctypes
class Mem(ctypes.Structure):
    _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong),('total_phys',ctypes.c_ulonglong),('avail_phys',ctypes.c_ulonglong),('total_page',ctypes.c_ulonglong),('avail_page',ctypes.c_ulonglong),('total_virt',ctypes.c_ulonglong),('avail_virt',ctypes.c_ulonglong),('avail_extended',ctypes.c_ulonglong)]
m=Mem();m.length=ctypes.sizeof(m);ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m));print('MEMORY',dict(physical_free_MiB=m.avail_phys/2**20,commit_free_MiB=m.avail_page/2**20,commit_total_MiB=m.total_page/2**20),flush=True)
try:
    import psutil
    for p in psutil.process_iter(['pid','name','memory_info','cmdline']):
        try:
            cmd=' '.join(p.info['cmdline'] or [])
            if p.info['name'].lower().startswith(('python','blender','freecad')):
                print(p.info['pid'],p.info['name'],p.info['memory_info'].rss/2**20,cmd[:300],flush=True)
        except Exception:pass
except ImportError:print('psutil unavailable')
