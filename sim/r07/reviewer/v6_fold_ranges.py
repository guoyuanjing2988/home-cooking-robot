from v6_common import *
data=read('idle.json');seen=set();rows=[]
for group in ('task_fold','meal_end_return_diagnostic','explicit_unfold'):
 for r in data[group]['attempts']:
  key=(r['motion_model_xml'],r['name'])
  if key in seen:continue
  seen.add(key);ch=v.scene(0);ch.xml=(I/r['motion_model_xml']).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml))
  for ei,e in enumerate(r['edges']):
   if not e.get('path'):continue
   bad=[]
   for pi,q in enumerate(e['path']):
    for n,ix in ch.qa.items():
     j=ch.jid[n]
     if ch.m.jnt_limited[j] and not ch.m.jnt_range[j,0]-1e-8<=q[ix]<=ch.m.jnt_range[j,1]+1e-8:bad.append(dict(point=pi,joint=n,value=q[ix]))
   rows.append(dict(group=group,attempt=r['name'],edge=ei,waypoints=len(e['path']),pass_=not bad,violations=bad))
dump('fold_ranges.json',dict(rows=rows,all_pass=all(r['pass_'] for r in rows),method='Range intervals are convex; checking all saved linear-segment endpoints proves every interpolated coordinate stays in its public/model joint range.'))
print('FOLD_RANGES',len(rows),all(r['pass_'] for r in rows))
