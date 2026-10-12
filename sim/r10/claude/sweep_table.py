"""Tabulate the R12 no-slip robustness sweep (jobs/j7.txt): per item, design x condition.
Cell = pass/fail and max in-grip slip (mm); pass = placed (tomato on the blade plate /
carrot in the chute) and slip < 10 mm. Writes results/r12_sweep.json and prints markdown."""
import json,os,sys,numpy as np
COND=[('μ0.1',dict(mu='0.1')),('μ0.15',dict(mu='0.15')),('μ0.2',dict(mu='0.2')),('μ0.3',dict(mu='0.3')),('μ0.45',dict(mu='0.45')),('μ0.6',dict(mu='0.6')),
 ('小号',dict(mu='0.3',size='S')),('大号重',dict(mu='0.3',size='L')),('外偏8mm',dict(mu='0.3',shift='+.008,0,0')),('内偏8mm',dict(mu='0.3',shift='-.008,0,0')),
 ('高偏6mm',dict(mu='0.3',shift='0,0,.006')),('最坏',dict(mu='0.2',size='L',shift='+.008,0,0'))]
SZ={'AW':{'S':'.060','L':'.080'},'AS':{'S':'.028','L':'.040'}}
def tag(P,c,f,grip):
 t=f"{P}_mu{c['mu']}_F40"+(f'_f{f}' if f else '')
 if c.get('size'):t+=f"_d0{SZ[P][c['size']]}"+(f"_m{'.22' if P=='AW' else '.16'}" if c['size']=='L' else '')
 if grip:t+=f'_pos{float(grip):.4f}'
 t+='_ns10'
 if c.get('shift'):t+='_shift'+'_'.join(f'{float(x):+.3f}' for x in c['shift'].split(','))
 return t
out={};md=[]
for P,item,designs in (('AW','番茄',[('','原装短指（力控40N）',None),('L','加长平直（40N）',None),('V','横向V槽（40N）',None),('K','金字塔窝（40N）',None),('R','鳍条Fin Ray（40N）',None),('R','鳍条（位控压15mm）','.015'),('D','双区指（40N）',None),('D','双区指（位控压4mm）','.004'),('D','双区指（位控压6mm）','.006')]),
 ('AS','胡萝卜',[('','原装短指',None),('L','加长平直',None),('V','横向V槽',None),('K','金字塔窝',None),('R','鳍条Fin Ray',None),('D','双区指',None)])):
 md.append(f'\n### {item}\n\n| 设计 | '+' | '.join(c for c,_ in COND)+' | 每指力 中位/最大 N |\n|'+'---|'*(len(COND)+2))
 for f,name,grip in designs:
  row=[];fN=None
  for cn,c in COND:
   p=f'results/dyn_{tag(P,c,f,grip)}.json'
   if not os.path.exists(p):row.append('—');continue
   d=json.load(open(p))
   if 'chute_top' in d:  # carrot: bottom end >= 20 mm inside the chute (centre test was wrong for thick carrots)
    fz,ct=d['final_food_pos'],d['chute_top'];r_=(d.get('item_d') or .035)/2
    d['in_chute']=abs(fz[0]-ct[0])<.05 and abs(fz[1]-ct[1])<.035 and fz[2]-(.0625+r_)<ct[2]-.02
   ok=bool(d.get('on_plate',d.get('in_chute'))) and d['max_slip_in_grip_mm']<10
   out[f'{P}|{name}|{cn}']=dict(ok=ok,slip_mm=d['max_slip_in_grip_mm'],slip_deg=d['max_slip_in_grip_deg'],finger_N_median=d.get('finger_N_median'),finger_N_max=d.get('finger_N_max'))
   row.append(('✅' if ok else '❌')+f" {d['max_slip_in_grip_mm']:.0f}" if d['max_slip_in_grip_mm']<1000 else '❌ 掉')
   if cn=='μ0.3':fN=f"{d.get('finger_N_median','?')}/{d.get('finger_N_max','?')}"
  md.append(f'| {name} | '+' | '.join(row)+f' | {fN} |')
json.dump(out,open('results/r12_sweep.json','w'),ensure_ascii=False,indent=1);print('\n'.join(md))
if len(sys.argv)>1:
 # heatmap figure: green = placed and slip < 10 mm; number = max in-grip slip (mm)
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt;from matplotlib import font_manager
 font_manager.fontManager.addfont('C:/Windows/Fonts/msyh.ttc');plt.rcParams['font.family']='Microsoft YaHei'
 fig,axs=plt.subplots(2,1,figsize=(15,9.5),gridspec_kw=dict(height_ratios=[9,6]))
 for ax,(P,title) in zip(axs,(('AW','番茄（力控 40 N，除非注明位控）'),('AS','胡萝卜（力控 40 N）'))):
  names=list(dict.fromkeys(k.split('|')[1] for k in out if k.startswith(P)))
  M=np.full((len(names),len(COND)),np.nan);T=[['—']*len(COND) for _ in names]
  for i,n in enumerate(names):
   for j,(cn,_) in enumerate(COND):
    r=out.get(f'{P}|{n}|{cn}')
    if r is None:continue
    M[i,j]=1 if r['ok'] else 0;T[i][j]='掉' if r['slip_mm']>=1000 else f"{r['slip_mm']:.0f}"
  ax.imshow(np.ma.masked_invalid(M),cmap=matplotlib.colors.ListedColormap(['#e8857a','#8fd19e']),vmin=0,vmax=1,aspect='auto')
  for i in range(len(names)):
   for j in range(len(COND)):ax.text(j,i,T[i][j],ha='center',va='center',fontsize=10)
  ax.set_xticks(range(len(COND)),[c for c,_ in COND]);ax.set_yticks(range(len(names)),names)
  ax.set_title(title+'：绿 = 放到位且滑移 < 10 mm；数字 = 最大滑移 mm；— = 未跑',fontsize=12,loc='left')
 fig.tight_layout();fig.savefig(sys.argv[1],dpi=110);print('saved',sys.argv[1])
