"""R19 #42: the binding <= 4 mm re-check of a chain, r19pot_check.py executed unchanged from its source (as r19fr5_check.py
does). New file. The only changes are where the certificate is written: results/r19/mount/check_* (not
results/r19/pot/check_*), an existing file is never overwritten, an optional OUTSFX=<suffix>, and the opt-in WOKPY=1 of
r19fr5_check.py (a wok chain's own plating spot moved to PY, the r19enc_check.py rule). The arm is ARM=<id>: for a mount
option the bracket pieces (R_gripper_oem_mount_*) are part of R_tool, so they are checked like the housing (5 mm to the
environment, 0 mm self against wrist 2 / wrist 1 / forearm / base; the wrist-3 pair is static: r19mount_static.py).
python r19mount_check.py <chain json> RACK=keyed SPX=1.56 SPY=.20 ARM=<arm> PY=.15 [WOKPY=1] [OUTSFX=..] [WORKERS=16]"""
_src=open('r19pot_check.py',encoding='utf-8').read()
_a="results/r19/pot/check_";_b="os.makedirs('results/r19/pot',exist_ok=True)";_c=""".json";json.dump(out,open(fn,'w')""";_d="def J(f):return json.load(open(f,encoding='utf-8'))"
assert _src.count(_a)==2 and _src.count(_b)==1 and _src.count(_c)==1 and _src.count(_d)==1
_src=_src.replace(_a,"results/r19/mount/check_").replace(_b,"os.makedirs('results/r19/mount',exist_ok=True)").replace(_c,
 """{KV.get('OUTSFX','')}.json";assert not os.path.exists(fn),('exists, not overwritten',fn);json.dump(out,open(fn,'w')""").replace(_d,
 """def J(f):
 r=json.load(open(f,encoding='utf-8'))
 if KV.get('WOKPY')=='1' and 'PY' in KV and r.get('obj')=='wok':   # r19enc_check.py line 77 (as r19fr5_check.py)
  sc=dict(r.get('scene',{}));pc=list(sc.get('r15_plate_c',[.43,.13,.85]));pc[1]=float(KV['PY']);sc['r15_plate_c']=[float(v) for v in pc];r['scene']=sc;r['plate_y']=float(KV['PY'])
 return r""")
exec(compile(_src,'r19pot_check.py','exec'))
