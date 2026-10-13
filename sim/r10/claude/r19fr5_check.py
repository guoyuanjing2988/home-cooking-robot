"""R19 #2 (FR5): the pot-zone <= 4 mm certificate, r19pot_check.py executed unchanged from its source. The only
changes are where the certificate is written: results/r19/fr5/check_* (not results/r19/pot/check_*), with an optional
OUTSFX=<suffix> on the name (the name does not carry PY), an existing file is never overwritten, and one opt-in:
 WOKPY=1  for a wok chain, PY also moves the chain's own plating spot (scene r15_plate_c), exactly the rule of
          r19enc_check.py recheck PY= (line 77). Without it a wok chain keeps the plate it was planned with, whatever
          PY says (r19pot_check.py reads the chain's scene as stored).
Same options: python r19fr5_check.py <chain json> RACK=keyed SPX= SPY= ARM=<arm> PY=.15 [WOKPY=1] [OUTSFX=..] [WORKERS=16]"""
_src=open('r19pot_check.py',encoding='utf-8').read()
_a="results/r19/pot/check_";_b="os.makedirs('results/r19/pot',exist_ok=True)";_c=""".json";json.dump(out,open(fn,'w')""";_d="def J(f):return json.load(open(f,encoding='utf-8'))"
assert _src.count(_a)==2 and _src.count(_b)==1 and _src.count(_c)==1 and _src.count(_d)==1
_src=_src.replace(_a,"results/r19/fr5/check_").replace(_b,"os.makedirs('results/r19/fr5',exist_ok=True)").replace(_c,
 """{KV.get('OUTSFX','')}.json";assert not os.path.exists(fn),('exists, not overwritten',fn);json.dump(out,open(fn,'w')""").replace(_d,
 """def J(f):
 r=json.load(open(f,encoding='utf-8'))
 if KV.get('WOKPY')=='1' and 'PY' in KV and r.get('obj')=='wok':   # r19enc_check.py line 77
  sc=dict(r.get('scene',{}));pc=list(sc.get('r15_plate_c',[.43,.13,.85]));pc[1]=float(KV['PY']);sc['r15_plate_c']=[float(v) for v in pc];r['scene']=sc;r['plate_y']=float(KV['PY'])
 return r""")
exec(compile(_src,'r19pot_check.py','exec'))
