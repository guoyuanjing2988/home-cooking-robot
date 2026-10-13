"""R19 #42: the tables of R19_MOUNT.md from the stored results (new file; reads only).
results/r19/mount/: design_mounts.json (r19mount_design.py PART=mounts), static.json, payload.json, every pilot chain
chain_<set>_..._<TAG>_<arm>.json (r19mount_retarget.py TAG rt*, r19mount_run.py TAG mnt*) and its <= 4 mm re-check
(check_<chain>_rack_sp1.56_.20[_t8].json from r19mount_check.py, <chain>_verify4mm[_pot].json from r19prep_verify.py /
r19prep4_verify.py / r19prep5_verify.py).
Certificates of ur5e_enc2_pgc_m2 / fr5_j6_pgc_m2 made before the m2 boss became 8 mm (r19mount.py t1) are marked
superseded; only the _t8 ones and those made after that change count for m2 (by file time).
python r19mount_table.py -> results/r19/mount/summary.json"""
import sys,os,json,glob,re,time
sys.path.insert(0,'.')
D='results/r19/mount';J=lambda f:json.load(open(f,encoding='utf-8'))
M2_CHANGE=1791924348.2   # 2026-10-14 04:45:48 local: r19mount.py with the m2 boss 8 mm + face-plane clip (results made earlier used the 5 mm boss)
ARMS=['ur5e_enc2_pgc','fr5_j6_pgc']
def parse(fn):
 b=os.path.basename(fn)[:-5]
 for a in ARMS:
  for k in ('m1','m2','m3'):
   s='_'+a+'_'+k
   if b.endswith(s):
    head=b[:-len(s)];m_=re.match(r'chain_(\w+?)(_s[+-]1)?_(rt\w*|mnt\w*)$',head)
    return dict(set='plate2' if 'plate2' in m_.group(3) else m_.group(1),tag=m_.group(3),arm=a,mount=k,base=b) if m_ else None
 return None
rows=[]
for f in sorted(glob.glob(D+'/chain_*.json')):
 if '_verify4mm' in f:continue
 p=parse(f)
 if not p:continue
 r=J(f);x=r.get('r19mount') or r.get('r19fr5prep') or {}
 kind='re-target (stored path kept)' if p['tag'].startswith('rt') else 're-plan'
 settings=x.get('argv') if x else (r.get('r19mount_run') or {}).get('argv') or r.get('argv')
 row=dict(p,kind=kind,ok=bool(r.get('ok')),act_time_s=r.get('time_s'),act_time_upper_E_s=r.get('time_s_upper_E'),elapsed_s=x.get('elapsed_s',r.get('elapsed_s')),
  bad_states=(x.get('play_bad',0)+x.get('approach_bad',0)) if x else None,settings=settings,file=f)
 if not r.get('ok') and 'anchors' in r:row['failed_anchors']=[k for k,v in r['anchors'].items() if not v.get('ok')];row['failed_joins']=sum(1 for j in r.get('joins',[]) if not j.get('ok'))
 chk=[]
 for c in glob.glob(D+'/check_'+p['base']+'_rack_sp1.56_.20*.json')+glob.glob(D+'/'+p['base']+'_verify4mm*.json'):
  cc=J(c);sup=p['mount']=='m2' and os.path.getmtime(c)<M2_CHANGE
  if 'parts' in cc:st=sum(v['states'] for v in cc['parts'].values());hit=sum(v['hit_states'] for v in cc['parts'].values());mr=min(v['min_env_reserve_mm'] for v in cc['parts'].values() if v['min_env_reserve_mm'] is not None);el=cc['elapsed_s']
  else:st=sum(v['states'] for v in cc['summary'].values());hit=sum(v['hit_states'] for v in cc['summary'].values());mr=min(v['min_reserve_mm'] for v in cc['summary'].values());el=cc['elapsed_s']
  chk.append(dict(file=c,ok=bool(cc['ok']),states=st,hit_states=hit,min_reserve_mm=round(mr,2),elapsed_s=round(el),superseded_by_m2_t8=sup))
 row['checks']=chk;row['certified']=any(c['ok'] and not c['superseded_by_m2_t8'] for c in chk);rows.append(row)
best={}
for r in rows:
 k=(r['set'],r['arm'],r['mount'])
 if r['certified'] and (k not in best or not best[k]['certified'] or (r['kind'].startswith('re-target') and not best[k]['kind'].startswith('re-target'))):best[k]=r
 elif k not in best:best[k]=r
out=dict(method=__doc__,made=time.strftime('%Y-%m-%d %H:%M'),design=J(D+'/design_mounts.json')['MOUNTS'] if os.path.exists(D+'/design_mounts.json') else None,
 static=J(D+'/static.json'),payload=J(D+'/payload.json'),attempts=rows,
 best={f'{s}/{a}/{m}':dict(certified=v['certified'],kind=v['kind'],tag=v['tag'],act_time_s=v['act_time_s'],elapsed_s=v['elapsed_s'],settings=v['settings'],
  check=[c for c in v['checks'] if not c['superseded_by_m2_t8']][:1]) for (s,a,m),v in sorted(best.items())})
json.dump(out,open(D+'/summary.json','w'),indent=1,default=str);print(D+'/summary.json',len(rows),'attempts')
sets=sorted({k[0] for k in best});print('set'.ljust(9),' | '.join(f'{a[:4]} {m}' for a in ARMS for m in ('m1','m2','m3')))
for s in sets:
 cells=[]
 for a in ARMS:
  for m in ('m1','m2','m3'):
   v=best.get((s,a,m));cells.append('  -   ' if v is None else ('OK '+('rt' if v['kind'].startswith('re-t') else 'pl')+'  ' if v['certified'] else ('fail  ' if not v['ok'] else 'nochk ')))
 print(s.ljust(9),' | '.join(cells))
for k,v in sorted(best.items()):
 c=[c for c in v['checks'] if not c['superseded_by_m2_t8']]
 print('/'.join(k),'certified' if v['certified'] else 'NOT','|',v['kind'],v['tag'],'| act',v['act_time_s'],'s (upper E',v.get('act_time_upper_E_s'),') | plan',v['elapsed_s'],'s |',(f"<=4mm {c[0]['states']} states, {c[0]['hit_states']} hits, min env {c[0]['min_reserve_mm']} mm, {c[0]['elapsed_s']} s" if c else ''),'|',v.get('failed_anchors',''))
