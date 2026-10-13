"""R19 #41: where and why the stir spills. Reads the traces of r19spill_trace.py / r19spill_drive.py. New file.
Traces without a result json (a run stopped at STOP=) are analysed up to their last sample; their stroke / segment
labels come from the trace (r19spill_drive.py) or from results/r19/stir/spill/labels_<tag>.npz (LABELS=1).
python r19spill_ana.py repro [PAIRS='{"<spill tag>":"<phys tag>"}']  traced runs vs the stored #40 runs (metrics equal?)
python r19spill_ana.py spill TAGS=a,b,..     per spilled piece: rim crossing (time, place, speed), last spatula contact,
                                             stroke / segment / phase, the commanded blade state  -> ana_<tag>.json
python r19spill_ana.py agg TAGS=.. OUT=..    every spilled piece of these runs, counted by stroke / segment / contact
python r19spill_ana.py far TAGS=.. OUT=..    far-wall load per stroke (most pieces beyond r .13 / .15 / .16 m in the
                                             far-wall phase, pieces already gone excluded) and spills per stroke
python r19spill_ana.py pile TAGS=.. OUT=..   pieces in each stroke's swath at its start and at the far wall
python r19spill_ana.py dev TAGS=.. OUT=..    commanded blade vs the bench pose at the same bench time, per stroke
python r19spill_ana.py timeline TAGS=.. [T0 T1 DT]   blade and pile state side by side
python r19spill_ana.py table                 controller lanes: seeds 1-3 from results/r19/stir/phys
(outputs in results/r19/stir/spill/)"""
import sys,os,json,glob,numpy as np
sys.path.insert(0,'.')
KV=dict(a.split('=',1) for a in sys.argv[2:] if '=' in a)
OUTD='results/r19/stir/spill';SETTLE=1.5;RS,A_RIM=.20,.17;DEPTH=RS-np.sqrt(RS**2-A_RIM**2)
def load(tag):
 fs=sorted(glob.glob(f'{OUTD}/trace_{tag}_*.npz'));Z=[np.load(f) for f in fs]
 T={k:np.concatenate([z[k] for z in Z]) for k in ('t','fp','fv','fc','sp','sq','sv','mp','mq')}
 if all('lab_k' in z.files for z in Z):T.update({k:np.concatenate([z[k] for z in Z]) for k in ('lab_k','lab_w','lab_tb')})
 o=np.argsort(T['t'],kind='stable');T={k:v[o] for k,v in T.items()}
 assert np.all(np.diff(T['t'])>0),'trace chunks overlap'
 lf=f'{OUTD}/labels_{tag}.npz'
 if 'lab_k' not in T and os.path.exists(lf):
  z=np.load(lf);ii=np.minimum(np.round(T['t']/.001).astype(int),len(z['t'])-1);T.update(lab_k=z['lab_k'][ii],lab_w=z['lab_w'][ii],lab_tb=z['lab_tb'][ii])
 rf=f'{OUTD}/stir2_{tag}.json';T['res']=json.load(open(rf)) if os.path.exists(rf) else None
 T['partial']=T['res'] is None or T['res'].get('stir_s',0)+SETTLE>T['t'][-1]+.02
 return T
def gone_mask(T):
 pos=T['fp'][-1];rr=np.hypot(pos[:,0],pos[:,1]);return ~((rr<A_RIM+.01)&(pos[:,2]>-.02)&(pos[:,2]<DEPTH+.06))
def seg_fn(T):
 """t -> (kind, stroke index k (pattern k % 5), bench time within the stroke [s]); from the stored labels of a
 counterfactual drive, else from the driver of the run"""
 if 'lab_k' in T:
  tt=T['t']
  def f(t):
   i=np.clip(np.searchsorted(tt,np.asarray(t)-1e-6),0,len(tt)-1);return np.where(T['lab_w'][i],'work','return'),T['lab_k'][i],T['lab_tb'][i]
  return f
 res=T['res']
 if res['driver']=='bench':
  P=res['period_s']
  def f(t):
   ph=np.maximum(t-SETTLE,0)/P;k=np.floor(ph).astype(int);fr=ph-k;return np.where(fr<.76,'work','return'),k,fr*P
  return f
 al=res['arm_law'];z=np.load(al['law_file']);L_=json.load(open(al['library']));G=L_['geometry']['segments']
 B=np.array([g['s0'] for g in G]+[G[-1]['s1']]);Lc=B[-1]
 def f(t):
  s=np.interp(np.maximum(t-SETTLE,0),z['t'],z['s']);r=np.mod(s,Lc);j=np.clip(np.searchsorted(B,r,side='right')-1,0,len(G)-1);cyc=(s//Lc).astype(int)
  kind=np.where(j%2==0,'work','return');k=cyc*5+j//2;tb=np.where(j%2==0,r-B[j],.76*2.4+(r-B[j])/(B[j+1]-B[j])*.24*2.4)   # returns: mapped onto the bench's return share
  return kind,k,tb
 return f
def quat2mat(q):
 from scipy.spatial.transform import Rotation
 return Rotation.from_quat(np.asarray(q)[...,[1,2,3,0]]).as_matrix()
def blade_state(T,i):
 """blade (mocap target = the commanded pose, and the spatula body) at sample i: edge-midpoint position, its
 speed, horizontal radius, height above the steel, handle elevation, blade angle to the steel there"""
 import spatula15 as SP
 R=quat2mat(T['mq'][i]);p=T['mp'][i];H=T['t'][1]-T['t'][0]
 i0,i1=max(i-1,0),min(i+1,len(T['t'])-1);v=(T['mp'][i1]-T['mp'][i0])/((i1-i0)*H)
 h=R@SP.HD;elev=np.degrees(np.arcsin(h[2]))   # handle direction (blade -> hand), elevation above horizontal
 n=(SP.C-p)/np.linalg.norm(SP.C-p);bd=np.degrees(np.arcsin(np.clip(R[:,1]@n,-1,1)))
 cor=SP.bottom_corners();gap=RS-np.max(np.linalg.norm(p+cor@R.T-SP.C,axis=1))
 return dict(edge_p=np.round(p,4).tolist(),edge_r_m=round(float(np.hypot(p[0],p[1])),4),edge_gap_mm=round(float(gap*1e3),1),cmd_v_mps=np.round(v,3).tolist(),cmd_speed_mps=round(float(np.linalg.norm(v)),3),
  body_v_mps=np.round(T['sv'][i][:3],3).tolist(),handle_elev_deg=round(float(elev),1),blade_to_steel_deg=round(float(bd),1))
def spill():
 out={}
 for tag in KV['TAGS'].split(','):
  T=load(tag);res=T['res'];t=T['t'];fp=T['fp'];N=fp.shape[1];sf=seg_fn(T)
  pos=fp[-1];rr=np.hypot(pos[:,0],pos[:,1]);inside=(rr<A_RIM+.01)&(pos[:,2]>-.02)&(pos[:,2]<DEPTH+.06)
  assert int((~inside).sum())==res['spilled']
  R_=np.hypot(fp[:,:,0],fp[:,:,1]);rows=[]
  for i in np.nonzero(~inside)[0]:
   outm=R_[:,i]>A_RIM;last_in=np.nonzero(~outm)[0][-1];ic=last_in+1   # first sample of the final excursion beyond the rim radius
   con=np.nonzero(T['fc'][:ic+1,i])[0];il=int(con[-1]) if len(con) else None
   kind,k,tb=sf(t[ic]);row=dict(piece=int(i),t_cross=round(float(t[ic]),2),cross_seg=f'{kind} {int(k)} (pattern {int(k)%5}) bench-time {float(tb):.2f} s = phase {float(tb)/2.4:.3f}',
    cross_p=np.round(fp[ic,i],3).tolist(),cross_az_deg=round(float(np.degrees(np.arctan2(fp[ic,i,1],fp[ic,i,0]))),1),cross_v=np.round(fp[ic,i]*0+T['fv'][ic,i],2).tolist(),cross_speed=round(float(np.linalg.norm(T['fv'][ic,i])),2))
   if il is not None:
    kind,k,tb=sf(t[il]);row.update(t_last_contact=round(float(t[il]),2),dt_contact_to_cross=round(float(t[ic]-t[il]),2),contact_seg=f'{kind} {int(k)} (pattern {int(k)%5}) bench-time {float(tb):.2f} s = phase {float(tb)/2.4:.3f}',
     contact_piece_p=np.round(fp[il,i],3).tolist(),contact_piece_v=np.round(T['fv'][il,i],2).tolist(),contact_piece_speed=round(float(np.linalg.norm(T['fv'][il,i])),2),blade=blade_state(T,il))
   rows.append(row)
  out[tag]=dict(spilled=res['spilled'],pieces=rows);print(tag,'spilled',res['spilled'])
  for r in rows:print(' ',json.dumps(r))
  json.dump(out[tag],open(f'{OUTD}/ana_{tag}.json','w'),indent=1)
def zsurf(r):return RS-np.sqrt(np.maximum(RS**2-np.minimum(r,A_RIM)**2,0))
def timeline():
 """TAGS=a,b T0= T1= DT=.05: blade (commanded edge midpoint) and pile state side by side"""
 import spatula15 as SP
 T0,T1,DT_=float(KV.get('T0',1.5)),float(KV.get('T1',5.2)),float(KV.get('DT',.05))
 for tag in KV['TAGS'].split(','):
  T=load(tag);sf=seg_fn(T);t=T['t'];print('==',tag)
  for tt in np.arange(T0,T1+1e-9,DT_):
   i=int(np.argmin(np.abs(t-tt)));fp=T['fp'][i];rr=np.hypot(fp[:,0],fp[:,1]);h=fp[:,2]-zsurf(rr);bs=blade_state(T,i);kind,k,tb=sf(t[i])
   print(f"t {t[i]:.2f} {str(kind):6s} {int(k)} tb {float(tb):.2f} | edge r {bs['edge_r_m']:.3f} z {bs['edge_p'][2]:.3f} gap {bs['edge_gap_mm']:5.1f} v {bs['cmd_speed_mps']:.2f} elev {bs['handle_elev_deg']:5.1f} bl {bs['blade_to_steel_deg']:5.1f}"
         f" | pile r>.13 {int((rr>.13).sum()):2d} r>.15 {int((rr>.15).sum()):2d} r>.16 {int((rr>.16).sum()):2d} maxr {rr.max():.3f} maxz {fp[:,2].max():.3f} touch {int(T['fc'][i].sum()):2d}")
PAT=[(0,0),(30,0),(0,.05),(30,-.06),(0,-.05)]   # stirbench PATTERN (yaw deg, lateral offset m)
def swath(fp,k):
 """piece coordinates in stroke k's frame: u along the push (az 90 + yaw), e across (offset removed)"""
 ps,e0=PAT[k%5];a=np.radians(90+ps);d=np.array([np.cos(a),np.sin(a)]);l=np.array([-d[1],d[0]])
 return fp[:,:2]@d,fp[:,:2]@l-e0
def pile():
 """TAGS=..: per working part, at its start (tb = 0) and when the blade reaches the far wall (tb = 1.08): pieces in
 the blade's swath (|e| < 6 cm) ahead of the blade, their spread along the push, and stacking"""
 out={}
 for tag in KV['TAGS'].split(','):
  T=load(tag);sf=seg_fn(T);t=T['t'];kind,k,tb=sf(t);rows=[]
  for kk in range(int(k.max())+1):
   w=np.nonzero((kind=='work')&(k==kk))[0]
   if not len(w):continue
   r_=dict(stroke=kk)
   for lab,tt in (('start',0.),('far',1.08)):
    j=w[np.argmin(np.abs(tb[w]-tt))]
    if abs(tb[j]-tt)>.03:continue
    fp=T['fp'][j];u,e=swath(fp,kk);rr=np.hypot(fp[:,0],fp[:,1]);h=fp[:,2]-zsurf(rr);sw=(np.abs(e)<.06)
    r_[lab]=dict(t=round(float(t[j]),2),in_swath=int(sw.sum()),swath_u_gt_0=int((sw&(u>0)).sum()),swath_u_gt_06=int((sw&(u>.06)).sum()),r_gt_13=int((rr>.13).sum()),stacked_gt_20mm=int((h>.02).sum()),
     swath_u_mean=round(float(u[sw].mean()),3) if sw.any() else None)
   rows.append(r_)
  out[tag]=rows;print('==',tag)
  for r_ in rows:print(' ',json.dumps(r_))
 json.dump(out,open(f"{OUTD}/pile_{KV.get('OUT','x')}.json",'w'),indent=1)
def dev():
 """TAGS=..(arm traces): commanded blade (mocap) vs the bench pose at the same bench time, per working part, in the
 stroke frame: position (u along the push, e across, z) and rotation (yaw about z, pitch about e, roll about u);
 also the blade speed ratio s' (arm / bench) at tb bins"""
 import r19stir_cycle as C
 from scipy.spatial.transform import Rotation
 B=C.bench();out={}
 for tag in KV['TAGS'].split(','):
  T=load(tag);sf=seg_fn(T);t=T['t'];kind,k,tb=sf(t);print('==',tag);rows=[]
  for kk in range(5):
   w=np.nonzero((kind=='work')&(k%5==kk)&(t>1.6))[0]
   if not len(w):continue
   ps,e0=PAT[kk];a=np.radians(90+ps);d=np.array([np.cos(a),np.sin(a),0]);l=np.array([-d[1],d[0],0]);z=np.array([0,0,1.]);F=np.c_[d,l,z]
   tbk=tb[w];pb=B['PS'](C.t0_of(kk)+tbk);Rb=B['RS'](C.t0_of(kk)+tbk).as_matrix();pa=T['mp'][w];Ra=quat2mat(T['mq'][w])
   dp=(pa-pb)@F;rv=Rotation.from_matrix(np.einsum('nij,nkj->nik',Ra,Rb)).as_rotvec()@F   # world-frame rotation error, in (roll u, pitch e, yaw z)
   r_=dict(stroke=kk,samples=len(w),max_abs_mm=dict(u=round(float(np.abs(dp[:,0]).max()*1e3),2),e=round(float(np.abs(dp[:,1]).max()*1e3),2),z=round(float(np.abs(dp[:,2]).max()*1e3),2)),
    max_abs_deg=dict(roll_u=round(float(np.degrees(np.abs(rv[:,0]).max())),2),pitch_e=round(float(np.degrees(np.abs(rv[:,1]).max())),2),yaw_z=round(float(np.degrees(np.abs(rv[:,2]).max())),2)))
   far=(tbk>.8)&(tbk<1.2)
   if far.any():r_['far_wall_tb_.8_1.2']=dict(mean_mm=dict(u=round(float(dp[far,0].mean()*1e3),2),e=round(float(dp[far,1].mean()*1e3),2),z=round(float(dp[far,2].mean()*1e3),2)),mean_deg=dict(roll_u=round(float(np.degrees(rv[far,0].mean())),2),pitch_e=round(float(np.degrees(rv[far,1].mean())),2),yaw_z=round(float(np.degrees(rv[far,2].mean())),2)))
   rows.append(r_);print(' ',json.dumps(r_))
  out[tag]=rows
 json.dump(out,open(f"{OUTD}/dev_{KV.get('OUT','x')}.json",'w'),indent=1)
def far():
 """TAGS=..: per working part, the far-wall load: the most pieces beyond horizontal radius .13 / .15 / .16 m during
 the far-wall phase (bench time .8 .. 1.5 s of the stroke), the pieces that leave the wok for good in that stroke,
 and per run the sums (a less noisy spill-risk measure than the spill count)"""
 out={}
 for tag in KV['TAGS'].split(','):
  T=load(tag);sf=seg_fn(T);t=T['t'];kind,k,tb=sf(t);R_=np.hypot(T['fp'][:,:,0],T['fp'][:,:,1]);rows=[]
  gone=gone_mask(T);res=T['res'] or {};nsp=int(gone.sum())
  tx=np.full(R_.shape[1],np.nan)
  for i in np.nonzero(gone)[0]:tx[i]=t[np.nonzero(R_[:,i]<=A_RIM)[0][-1]+1]
  for kk in range(int(k.max())+1):
   w=np.nonzero((kind=='work')&(k==kk)&(tb>=.8)&(tb<=1.5))[0]
   if len(w)<20:continue
   ww=np.nonzero(((kind=='work')&(k==kk))|((kind=='return')&(k==kk)))[0]
   live=~(tx<t[ww[0]])   # pieces not already gone before this stroke
   rows.append(dict(stroke=kk,pattern=kk%5,r13=int((R_[w][:,live]>.13).sum(1).max()),r15=int((R_[w][:,live]>.15).sum(1).max()),r16=int((R_[w][:,live]>.16).sum(1).max()),
    spilled=int(np.sum((tx>=t[ww[0]])&(tx<=t[ww[-1]]+1e-9)))))
  S={x:sum(r_[x] for r_ in rows) for x in ('r13','r15','r16','spilled')}
  out[tag]=dict(strokes=rows,sum=S,partial_to_t=round(float(t[-1]),2) if T['partial'] else None,total_spilled=nsp,hot=res['zones'][0]['hot_frac']['mean'] if res and not T['partial'] else None,never_hot=res['zones'][0]['never_hot'] if res and not T['partial'] else None)
  print(f"{tag:28s} {'to t %.1f'%t[-1] if T['partial'] else 'full    '} spilled {nsp:2d} hot {out[tag]['hot'] or 0:.3f} never {out[tag]['never_hot'] or 0:2d} | per stroke r>.15: {[r_['r15'] for r_ in rows]} r>.16: {[r_['r16'] for r_ in rows]} spill: {[r_['spilled'] for r_ in rows]} | sums r13 {S['r13']} r15 {S['r15']} r16 {S['r16']}")
 json.dump(out,open(f"{OUTD}/far_{KV.get('OUT','x')}.json",'w'),indent=1)
def agg():
 """TAGS=..: every spilled piece of these runs: stroke, segment and bench time at the rim crossing, azimuth, crossing
 speed, whether it touched the spatula in the 0.5 s before, and the commanded blade speed there"""
 rows=[]
 for tag in KV['TAGS'].split(','):
  T=load(tag);sf=seg_fn(T);t=T['t'];fp=T['fp'];R_=np.hypot(fp[:,:,0],fp[:,:,1])
  for i in np.nonzero(gone_mask(T))[0]:
   ic=np.nonzero(R_[:,i]<=A_RIM)[0][-1]+1;kind,k,tb=sf(t[ic]);w0=max(0,ic-50)
   rows.append(dict(run=tag,piece=int(i),t=round(float(t[ic]),2),stroke=int(k),pattern=int(k)%5,seg=str(kind),tb=round(float(tb),2),az_deg=round(float(np.degrees(np.arctan2(fp[ic,i,1],fp[ic,i,0]))),1),
    z_m=round(float(fp[ic,i,2]),3),speed=round(float(np.linalg.norm(T['fv'][ic,i])),2),touched_last_05s=bool(T['fc'][w0:ic+1,i].any()),blade_speed=blade_state(T,ic)['cmd_speed_mps']))
 n=len(rows);S=lambda f:sum(1 for r in rows if f(r))
 out=dict(runs=KV['TAGS'].split(','),pieces=n,in_strokes_0_1=S(lambda r:r['stroke']<=1),in_stroke_4=S(lambda r:r['pattern']==4),in_working_part=S(lambda r:r['seg']=='work'),
  tb_range=[min(r['tb'] for r in rows),max(r['tb'] for r in rows)] if rows else None,far_side=S(lambda r:30<=r['az_deg']<=150),touched_spatula_last_05s=S(lambda r:r['touched_last_05s']),
  crossing_speed_range=[min(r['speed'] for r in rows),max(r['speed'] for r in rows)] if rows else None,blade_speed_range=[min(r['blade_speed'] for r in rows),max(r['blade_speed'] for r in rows)] if rows else None,pieces_list=rows)
 print(json.dumps({k:v for k,v in out.items() if k not in ('pieces_list','runs')}))
 json.dump(out,open(f"{OUTD}/agg_{KV.get('OUT','x')}.json",'w'),indent=1)
def table():
 """the controller lanes' table: seeds 1-3, full 12 s, from results/r19/stir/phys (bench, #3 j8000, new cycle)"""
 P='results/r19/stir/phys';R=[('bench','full_bench_s{s}')]
 for a,nm in (('ur5e_enc2_pgc','UR5e'),('fr5_j6_pgc_sp20','FR5')):R+=[(f'{nm} #3 j8000',f'full_arm_{a}_j8000_s{{s}}'),(f'{nm} new short01_u06_j8000',f'full_arm_{a}_short01_u06_j8000_s{{s}}')]
 for nm,pat in R:
  v=[]
  for s in (1,2,3):
   f=f"{P}/stir2_{pat.format(s=s)}.json"
   if os.path.exists(f):r=json.load(open(f));v.append((r['spilled'],r['zones'][0]['hot_frac']['mean'],r['zones'][0]['never_hot'],r['flips_per_10s']['mean']))
   else:v.append(None)
  print(f'{nm:28s}',' | '.join('missing' if x is None else f'spill {x[0]} hot {x[1]:.3f} never {x[2]:2d} flips {x[3]:.2f}' for x in v))
def repro():
 pairs={'tr_bench_s3':'full_bench_s3','tr_ur5e_s3':'full_arm_ur5e_enc2_pgc_s3','tr_ur5e_j8000_s3':'full_arm_ur5e_enc2_pgc_j8000_s3','tr_fr5_s3':'full_arm_fr5_j6_pgc_sp20_s3','tr_fr5_j8000_s3':'full_arm_fr5_j6_pgc_sp20_j8000_s3'}
 pairs.update(json.loads(KV.get('PAIRS','{}')))
 for a,b in pairs.items():
  fa,fb=f'{OUTD}/stir2_{a}.json',f'results/r19/stir/phys/stir2_{b}.json'
  if not (os.path.exists(fa) and os.path.exists(fb)):continue
  A,B=json.load(open(fa)),json.load(open(fb))
  for X in (A,B):
   X.pop('wall_s',None)
   if X.get('arm_law'):X['arm_law']={k:v for k,v in X['arm_law'].items() if k not in ('law','law_file')}
  diff=[k for k in set(A)|set(B) if A.get(k)!=B.get(k)];print(a,'vs',b,'IDENTICAL' if not diff else f'DIFFER {diff}')
if __name__=='__main__':
 {'spill':spill,'repro':repro,'timeline':timeline,'pile':pile,'dev':dev,'far':far,'agg':agg,'table':table}[sys.argv[1]]()
