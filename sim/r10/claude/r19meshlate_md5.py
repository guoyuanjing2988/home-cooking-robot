"""R19 #7: md5 of the model XML of every scene spec in results/r19/export/*/recheck.json, rebuilt as the re-check
builds it (m2 arms: r19m2export.py with ARMX=1; other arms: r19export.py), against the stored
model_md5. Used before and after the late held-box mesh pass in scene.build (R19_MESHLATE.md).
python r19meshlate_md5.py list OUT=<dir>          -> <dir>/specs.json (unique specs, with the stored md5)
python r19meshlate_md5.py one OUT=<dir> I=<k> [NOLATE=1] [XML=<file>]  -> <dir>/md5_<k>.json (one spec per process: r19export.scene;
   NOLATE=1 builds without scene.meshlate, XML= also writes the model XML)
python r19meshlate_md5.py sum OUT=<dir>           -> <dir>/summary.json"""
import sys,os,json,glob
sys.path.insert(0,'.')
CMD=sys.argv[1];KV=dict(a.split('=',1) for a in sys.argv[2:] if '=' in a);OUT=KV['OUT']
if CMD=='list':
 S={}
 for f in sorted(glob.glob('results/r19/export/*/recheck.json')):
  for s in json.load(open(f))['scenes']:
   k=json.dumps(s['spec'],sort_keys=True);S.setdefault(k,dict(spec=s['spec'],stored=s['model_md5'],exports=[]))['exports'].append(os.path.basename(os.path.dirname(f)))
 os.makedirs(OUT,exist_ok=True);json.dump(list(S.values()),open(OUT+'/specs.json','w'),indent=1);print(len(S),'specs')
elif CMD=='one':
 k=int(KV['I']);e=json.load(open(OUT+'/specs.json'))[k]
 m2='_m2' in e['spec']['arm']   # the m2 exports were re-checked by r19m2export.py, the others by r19export.py
 sys.argv=['r19export.py','recheck']+(['ARMX=1'] if m2 else [])
 g={'__name__':'r19export_scan','__file__':os.path.abspath('r19export.py')}
 if m2:import r19m2export as M2;src=M2.source()
 else:src=open('r19export.py',encoding='utf-8').read()
 exec(compile(src,os.path.abspath('r19export.py'),'exec'),g)
 if KV.get('NOLATE')=='1':import scene;scene.meshlate=lambda tree:None   # the build of before the patch (no late pass)
 M=g['scene'](e['spec'])
 if KV.get('XML'):open(KV['XML'],'w',encoding='utf-8').write(M['ch'].xml)
 json.dump(dict(i=k,spec=e['spec'],stored=e['stored'],md5=M['md5'],same=M['md5']==e['stored']),open(f'{OUT}/md5_{k}.json','w'),indent=1);print(k,M['md5']==e['stored'])
elif CMD=='sum':
 E=json.load(open(OUT+'/specs.json'));R=[json.load(open(f'{OUT}/md5_{k}.json')) if os.path.exists(f'{OUT}/md5_{k}.json') else None for k in range(len(E))]
 out=dict(specs=len(E),built=sum(r is not None for r in R),same=sum(1 for r in R if r and r['same']),missing=[k for k,r in enumerate(R) if r is None],
  differ=[dict(i=k,spec=E[k]['spec'],exports=E[k]['exports']) for k,r in enumerate(R) if r and not r['same']])
 json.dump(out,open(OUT+'/summary.json','w'),indent=1);print({k:v for k,v in out.items() if k!='differ'},'differ',len(out['differ']))
