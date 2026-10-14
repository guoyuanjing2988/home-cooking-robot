"""R19 #42 (R19_M2JOIN.md): stroke-start candidates of r19stir_reach / r15reach restricted to the spatula hand-off's IK
branch. New file. Reads the r15reach-style files results/r19/stir/reach/reach_stir_h_scrape_dice_i<III>_g0.45_cx<CX>_r19_k48_
<arm>.json (written by `r19stir_reach.py one ... CARTX=<CX>`, unchanged) and keeps, per stroke, the candidates
 - with jaw sense SIGN (r19stir2_join's stir scene holds the spatula with jaw sense -1),
 - plume-clear (plume_mm >= 0, as r19stir_cycle.works),
 - on the branch of the spatula chain's end state (SPATCHAIN, last play state): elbow and wrist = signs of sin q3,
   sin q5, shoulder = q1 within 90 deg (mod 2pi) of the spatula end's q1,
 - one per distinct labelled solution (joint vectors within 0.5 deg are the same IK state; the one with the largest
   reserve is kept): r19stir_cycle.groups would merge them anyway, this only saves follow runs.
Every kept candidate is an unchanged r15reach candidate (same checks). Output: the same file name with TAG `r19_k48_m2join`
-> REACH template results/r19/stir/reach/reach_stir_h_scrape_dice_i{i:03d}_g0.45_cx<CX>_r19_k48_m2join_<arm>.json
python r19m2join_reach.py ARM=<arm> CX=.45 SPATCHAIN=<spatula chain json> [SIGN=-1]"""
import sys,json
import numpy as np
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a);ARM=KV['ARM'];CX=KV['CX'];SG=int(KV.get('SIGN',-1))
def br(q):q=np.asarray(q,float)[3:9];return [int(np.sign(np.sin(q[2]))),int(np.sign(np.sin(q[4])))]
E=np.array(json.load(open(KV['SPATCHAIN']))['play'][-1],float);BE=br(E);Q1=np.degrees(E[3])
print('spatula end branch',BE,'q1 %.1f deg'%Q1)
for i in (0,16,32,48,64):
 src=f'results/r19/stir/reach/reach_stir_h_scrape_dice_i{i:03d}_g0.45_cx{CX}_r19_k48_{ARM}.json'
 R=json.load(open(src));keep=[]
 for c in sorted(R['cands'],key=lambda c:-c['reserve_mm']):
  q=np.asarray(c['q'],float)
  if c['jaw_sign']!=SG or c['plume_mm'] is None or c['plume_mm']<0 or br(q)!=BE:continue
  if abs((np.degrees(q[3])-Q1+180.)%360.-180.)>90.:continue
  if any(np.degrees(np.abs(q[3:9]-np.asarray(k['q'][3:9]))).max()<.5 for k in keep):continue
  keep.append(c)
 out=src.replace('_r19_k48_','_r19_k48_m2join_')
 R2=dict(R,cands=keep,n_candidates=len(keep),n_plume_clear=len(keep),best=max(keep,key=lambda c:c['reserve_mm']) if keep else None,
         m2join_filter=dict(source=src,jaw_sign=SG,branch_elbow_wrist=BE,shoulder_q1_deg=round(float(Q1),2),q1_window_deg=90,dedup_deg=.5,spatula_chain=KV['SPATCHAIN'],n_source=len(R['cands'])))
 json.dump(R2,open(out,'w'),indent=1)
 print(i,'kept',len(keep),'of',len(R['cands']),[np.degrees(np.asarray(k['q'][3:9])).round(1).tolist() for k in keep],'->',out)
