import json
import render_setup as re
s=re.s;H=s.HERE;best=json.loads((H/'results/best.json').read_text());manifest=json.loads((H/'renders/manifest.json').read_text());rows=[]
for name,pid,label in [('potato_wash','Q02.potato','wash'),('potato_peel','Q05.potato','helper_index_0'),('potato_cut','Q10.potato','load_slicer'),('potato_delivery','Q12.potato','deliver')]:
 ph=next(x for x in s.P['phases'] if x['id']==pid);sg=next(x for x in ph['segments'] if x['label']==label);key=pid+'__'+label;w=best['witnesses'][key];ch=s.Checker(ph,sg);side='L' if sg.get('action')=='helper_index' else 'R';focus=sg['poses'][-1][side]['pos']
 re.export(ch,w['poses'][-1]['q'],name,'STATIC WITNESS PASS / MEAL FAIL',focus=focus,label=pid+' '+label)
 rows.append(dict(file=name+'.png',scene=name+'.scene.json',stroke=key,static_witness=True))
manifest['potato_views']=rows;(H/'renders/manifest.json').write_text(json.dumps(manifest,indent=2));print('potato scenes4')
