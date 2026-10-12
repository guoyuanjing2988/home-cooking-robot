"""Summarise the R13 non-rigid matrix (results/r13s/*.json): one row per run.
Usage: python r13soft.py [table.png]   -> results/r13_soft.json and a markdown table."""
import json,glob,os,sys
import softfoods
rows=[]
for p in sorted(q for q in glob.glob('results/r13s/*.json') if '_vid' not in q):
 r=json.load(open(p));tag=os.path.basename(p)[:-5];it=softfoods.SOFT[r['item']]
 meth={'bulk':'带提手小筐（倒出）','boxed':'连盒夹起倒出'}.get(it['kind']) or ('托底叉' if r.get('grasp')=='support' else ('夹根部' if it['kind']=='bunch' else '夹'))
 prof='常速' if tag.endswith('_chain') else '压力测试'
 why='、'.join({'dropped':'掉落','slip>=10mm':'滑移≥10 mm','not in target':'没放进碗','force>damage':'夹力超上限','moment>allow':'超力矩'}.get(f,f) for f in r.get('fail',[])) or r.get('reason','')
 rows.append(dict(item=r['item'],zh=it['zh'],kind=it['kind'],method=meth,mu=r['mu'] if it['kind'] not in ('bulk',) else None,profile=prof,ok=bool(r.get('ok')),
  F=round(r.get('F',0),1),fN=r.get('finger_N_10ms_max'),dmg=it['dmg'],dsrc=it['dsrc'],slip=r.get('max_slip_mm'),drop_mm=r.get('drop_equiv_mm'),
  pieces_in=r.get('extra_in'),why=why,unstable=r.get('unstable')))
json.dump(rows,open('results/r13_soft.json','w'),ensure_ascii=False,indent=1)
md=['| 食材 | 抓法 | 湿摩擦 μ | 运动 | 结果 | 夹力 N/指（上限） | 备注 |','|---|---|---|---|---|---|---|']
for r in rows:
 note=[]
 if r['pieces_in'] is not None:note.append(f"进碗 {100*r['pieces_in']:.0f}%")
 if r['drop_mm']:note.append(f"落差当量 {r['drop_mm']:.0f} mm")
 if r['unstable']:note.append('仿真不稳定（无效）')
 md.append(f"| {r['zh']} | {r['method']} | {r['mu'] if r['mu'] is not None else '—'} | {r['profile']} | {'✅' if r['ok'] else '❌ '+r['why']} | {r['fN'] if r['fN'] is not None else '—'}（{r['dmg'] if r['dmg'] is not None else '未知'}） | {'；'.join(note)} |")
print('\n'.join(md))
