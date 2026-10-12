import time,json,numpy as np
import final_check as f
s=f.s;H=s.HERE
key='Q05.potato__helper_index_6';ph=next(p for p in s.P['phases'] if p['id']=='Q05.potato');sg=next(x for x in ph['segments'] if x['label']=='helper_index_6')
ch=s.Checker(ph,sg);raw=json.loads((H/'baseline/strokes'/ (key+'.json')).read_text());row=next(r for r in raw['rows'] if r['k']==5)
q=np.array(row['poses'][1]['q']);ch.set_contacts(sg['poses'][1]);beg=time.monotonic();hits,mins,audit=f.contacts(ch,q)
a=ch.gnames.index('L_link2_collision');b=ch.gnames.index('cable_chain_swept_cover_0_piece4')
out=dict(elapsed_s=time.monotonic()-beg,hits=hits,mins=mins,audit=audit,reviewer_discrepancy_pair=ch.bounds.pair(a,b),base_meshes=[n for n in ch.gnames if 'base_source' in n]);(H/'audit/distance_probe.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
