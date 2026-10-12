"""Final geometry, admission and resource audit; no new random pose search."""
import hashlib,xml.etree.ElementTree as E
import numpy as np,mujoco
from PIL import Image
from scene import H,ROOT,load,save,build,targets
from checker import Checker,reference
from run import station_audit
def main():
 cfg=load('results/selected.json')['config'];tree,meta=build(cfg);ch=Checker(tree,meta);assembly=station_audit(ch,meta)
 tree.write(H/'models/selected.xml',encoding='unicode')
 # Exact unchanged full robot body geoms (including base meshes and inertias).
 original=E.parse(H/'models/base.xml');geometry=[]
 for g in original.findall(".//body[@name='wall_anchor']//geom"):
  new=tree.find(f".//geom[@name='{g.get('name')}']");geometry.append(dict(name=g.get('name'),same_attributes=new is not None and new.attrib==g.attrib))
 inertias=[]
 for b in original.findall('.//body'):
  source=b.find('inertial')
  if source is None:continue
  dest=tree.find(f".//body[@name='{b.get('name')}']/inertial");inertias.append(dict(body=b.get('name'),same=dest is not None and dest.attrib==source.attrib))
 # Re-admit EVERY selected positive endpoint against the final code/scene.
 replay=[]
 for i,t in enumerate(targets(cfg,meta)):
  fn=f'results/strokes/{i}.json'
  if not (H/fn).exists():continue
  row=load(fn)
  assert row.get('layout')==cfg['id'],('stale selected layout',i)
  ct,cm=build(cfg,t['held']);cc=Checker(ct,cm)
  for k,p in enumerate(row['endpoints']):
   if not p['ok']:continue
   best=p['best'];R=np.array(best['rotation']);cc.configure_target(t,R)
   r=cc.check(np.array(best['q']),kind=t['kind'],mass={'carrot':.12,'holder':.55,'catch_tray':.55,None:0}[t['held']],force=t['force'])
   pe,re=cc.pose_error(best['q'],t['points'][k],R);ok=r['ok'] and pe<=.005 and re<=np.deg2rad(3)
   replay.append(dict(stroke=i,endpoint=k,ok=bool(ok),position_mm=pe*1000,orientation_deg=np.degrees(re),check=r))
   p['ok']=bool(ok);p['best']['check']=r
  row['static_ok']=all(p['ok'] for p in row['endpoints'])
  if not row['static_ok']:row['internal']=dict(ok=False,reason='final_endpoint_admission_failed')
  if row['internal']['ok']:
   R=np.array(row['endpoints'][0]['best']['rotation']);cc.configure_target(t,R);previous=None;maxstep=0;valid=True
   for q in row['internal']['path']:
    result=cc.check(np.array(q),kind=t['kind'],mass={'carrot':.12,'holder':.55,'catch_tray':.55,None:0}[t['held']],force=t['force'])
    valid &= result['ok']
    if previous is not None:maxstep=max(maxstep,cc.point_bound.segment_bound(np.array(previous),np.array(q)))
    previous=q
   row['internal']['final_replay_ok']=bool(valid and maxstep<=.004+1e-8)
   if not row['internal']['final_replay_ok']:row['internal']['ok']=False;row['internal']['reason']='final_internal_replay_failed'
  save(fn,row)
 # Installed station top extrema, including complete bowl adaptations.
 tops={}
 for g,n in enumerate(ch.gnames):
  b=int(ch.m.geom_bodyid[g])
  while ch.m.body_parentid[b]:b=int(ch.m.body_parentid[b])
  name=ch.m.body(b).name
  if name and name.startswith(('mandoline_station','peeler_station','greens_station','tomato_station','stored_bowl')):
   tops[name]=max(tops.get(name,-1),float(ch.bounds.support(g,np.array([0,0,1]))[2]))
 images=[]
 for p in (H/'renders').glob('*.png'):
  with Image.open(p) as im:images.append(dict(name=p.name,width=im.width,height=im.height,ok=max(im.size)<=1600))
 files=[p for p in H.rglob('*') if p.is_file()];size=sum(p.stat().st_size for p in files)
 resources=[load(str(p.relative_to(H))) for p in (H/'audit').glob('*.resource.json')]
 hashes={str(p.relative_to(H)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.suffix in ('.py','.xml') and 'assets' not in p.parts}
 save('results/delivery_audit.json',dict(full_robot_geometry=geometry,inertias=inertias,geometry_preserved=all(r['same_attributes'] for r in geometry) and all(r['same'] for r in inertias),station_tops_m=tops,low_profile_top_limit_m=1.05,low_profile_pass=all(v<=1.05+1e-8 for v in tops.values()),final_assembly=assembly,final_admission=replay,reference_sha256=hashlib.sha256((ROOT/'sim/r05/integrator/reference.py').read_bytes()).hexdigest(),total_bytes=size,under_3GB=size<3_000_000_000,images=images,resource_runs=resources,hashes=hashes,limitations=['Fixed basket cradle/retention not yet engineered; no supported-wash execution credited','Holder pickup/release, fixture interlocks and tray-to-bowl hardware events are not yet closed','Four-product recipe ledger is retained but other product motion sequences are deferred after carrot failure']))
  # Non-binding higher-feed sensitivity at the saved I09 mandoline start.
 iteration=load('results/iterations/I09.json');probe=next(p for p in iteration['probes'] if p['target']=='mandoline_work')
 if probe['ok']:
  ht,hm=build(cfg,'holder');hc=Checker(ht,hm);q=np.array(probe['best']['q']);R=np.array(meta['mandoline_rotation']);sensitivity=[]
  for feed in [40,60,70,100]:
   for lat in [-10,10]:
    force=(R@np.array([-feed,lat,20])).tolist();sensitivity.append(dict(feed_N=feed,lateral_N=lat,load=hc.loads(q,force,.55,.08)))
  save('results/force_sensitivity.json',dict(binding_check_feed_N=60,rows=sensitivity,scope='Saved first-pose static load sensitivity only. 70/100N are not replacement acceptance gates; no executed stroke is implied.'))
 print('audit geometry',all(r['same_attributes'] for r in geometry),'fixed intersections',len(assembly['packing_hits']),'tops',tops,'size MB',size/1e6,flush=True)
if __name__=='__main__':main()
