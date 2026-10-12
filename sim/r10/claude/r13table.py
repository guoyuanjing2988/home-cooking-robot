"""Summarise the R13 rigid-food matrix (results/r13/*.json) per item and method.
Cell 'ok' = held (slip < 10 mm), placed in the target, finger force <= damage limit,
PGC moment <= 7 N m. Writes results/r13_matrix.json and prints a markdown table.
Usage: python r13table.py [heatmap.png]"""
import json,glob,os,sys,collections
import foods
R=collections.defaultdict(dict)
for p in [q for q in glob.glob('results/r13/*.json') if '_vid' not in q]:
 r=json.load(open(p));tag=os.path.basename(p)[:-5]
 sz='typ'
 for part in tag.split('_'):
  if part.startswith('s') and part[1:2].isdigit():sz=part[1:]
 prof='chain' if tag.endswith('_chain') else 'stress'
 meth=('support' if r.get('grasp')=='support' else 'pinch')+('' if r.get('grasp')=='support' else '_'+r['gripper'])
 R[(r['item'],meth)][(r['mu'],sz,prof)]=r
def cell(r):
 if r is None:return None
 if 'max_slip_mm' not in r:return dict(ok=False,why=r.get('reason','')[:30],F=r.get('F'),set=r.get('set'))
 return dict(ok=bool(r['ok']),why=','.join(r['fail']),F=round(r['F'],1),fN=r['finger_N_10ms_max'],slip=r['max_slip_mm'],set=r['set'],mode=r['mode'],drop=r.get('drop_equiv_mm'))
out={};md=['| 食材 | 损伤上限 N/指 | 夹（PGC） | 夹（Hand-E 100） | 托底夹（PGC） |','|---|---|---|---|---|']
for k,it in foods.ITEMS.items():
 row={}
 for meth in ('pinch_PGC','pinch_HE100','support'):
  D=R.get((k,meth),{});mus=(.15,.3,.5) if meth!='support' else (.15,.3)
  rng=[f'{x:g}' for x in it['rng']]
  def all_sizes(mu,prof='stress'):
   cs=[cell(D.get((mu,s,prof))) for s in ('typ',*rng)];cs=[c for c in cs if c]
   return all(c['ok'] for c in cs) if cs else None,cs
  res={f'{mu:g}':all_sizes(mu) for mu in mus};res['0.15_chain']=all_sizes(.15,'chain')
  # minimal wet friction at which every size passes the stress profile
  mmin=next((mu for mu in mus if res[f'{mu:g}'][0]),None)
  row[meth]=dict(mu_min_stress=mmin,chain_mu015=res['0.15_chain'][0],cells={kk:v[1] for kk,v in res.items()})
 out[k]=dict(zh=it['zh'],dmg=it['dmg'],dsrc=it['dsrc'],**row)
 def txt(m):
  r_=row[m];s=('μ≥%g 全过'%r_['mu_min_stress'] if r_['mu_min_stress'] is not None else '湿滑都不过')
  return s+(' ；常规速度 μ0.15 ✓' if r_['chain_mu015'] else (' ；常规速度 μ0.15 ✗' if r_['chain_mu015'] is False else ''))
 md.append(f"| {it['zh']} | {it['dmg']} ({it['dsrc']}) | {txt('pinch_PGC')} | {txt('pinch_HE100')} | {txt('support')} |")
json.dump(out,open('results/r13_matrix.json','w'),ensure_ascii=False,indent=1);print('\n'.join(md))
if len(sys.argv)>1:
 import numpy as np,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt;from matplotlib import font_manager
 font_manager.fontManager.addfont('C:/Windows/Fonts/msyh.ttc');plt.rcParams['font.family']='Microsoft YaHei'
 cols=[('pinch_PGC','0.15'),('pinch_PGC','0.3'),('pinch_PGC','0.5'),('pinch_PGC','0.15_chain'),('pinch_HE100','0.15'),('pinch_HE100','0.3'),('pinch_HE100','0.5'),('pinch_HE100','0.15_chain'),('support','0.15'),('support','0.3'),('support','0.15_chain')]
 lab=['夹·PGC\nμ0.15','夹·PGC\nμ0.3','夹·PGC\nμ0.5','夹·PGC\nμ0.15常速','夹·HandE\nμ0.15','夹·HandE\nμ0.3','夹·HandE\nμ0.5','夹·HandE\nμ0.15常速','托底\nμ0.15','托底\nμ0.3','托底\nμ0.15常速']
 names=list(out);M=np.full((len(names),len(cols)),np.nan);T=[['']*len(cols) for _ in names]
 for i,k in enumerate(names):
  for j,(m,c) in enumerate(cols):
   cs=out[k][m]['cells'].get(c)
   if not cs:continue
   n_ok=sum(x['ok'] for x in cs);M[i,j]=n_ok/len(cs);T[i][j]=f'{n_ok}/{len(cs)}'
 fig,ax=plt.subplots(figsize=(14,11));ax.imshow(np.ma.masked_invalid(M),cmap=matplotlib.colors.LinearSegmentedColormap.from_list('g',['#e8857a','#f3d37a','#8fd19e']),vmin=0,vmax=1,aspect='auto')
 for i in range(len(names)):
  for j in range(len(cols)):ax.text(j,i,T[i][j],ha='center',va='center',fontsize=9)
 ax.set_xticks(range(len(cols)),lab,fontsize=9);ax.set_yticks(range(len(names)),[f"{out[k]['zh']}（≤{out[k]['dmg']:g} N）" for k in names],fontsize=10)
 ax.set_title('26 种硬质食材 × 抓法 × 湿摩擦：格子 = 通过的尺寸数/3（小/常见/大），压力测试含 7.5 m/s² 急停；"常速" = 规划轨迹的加速度',fontsize=11,loc='left')
 fig.tight_layout();fig.savefig(sys.argv[1],dpi=110);print('saved',sys.argv[1])
