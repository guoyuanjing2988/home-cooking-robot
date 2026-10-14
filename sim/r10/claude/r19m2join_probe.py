"""R19 #42 (R19_M2JOIN.md): which stored stir working-part branches can the spatula hand-off join? New file, read-only.
For every jaw sense and every stroke-0 working-part branch of results/r19/stir/cycle_<arm>/works.json (r19stir_cycle.groups,
representative = largest reserve), run r19stir2_join.self_motion (unchanged: tool-fixed IK continuation, cart stepped
1 mm from the spatula end E to that branch's start S, tool pose = FK(E)) and report whether it arrives at S (joint
difference mod 2pi; r19stir2_join.join demands < 1e-4 deg after its 2pi relabel). The scene is r19stir2_join's 'stir'
scene (jaw sense -1, r19stir2_join.SIGN): a sense +1 branch holds the spatula turned 180 deg in the jaws, so it can
only be reached by a regrasp; it is reported with its pose gap for the record.
python r19m2join_probe.py ARM=<arm> SPATCHAIN=<spatula chain json> [HUBSFILE=<hubs.json>] [STROKE=0]
 -> stdout + results/r19/stir/m2join/probe_<arm>.json"""
import sys,os,json
sys.path.insert(0,'.')
import numpy as np
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a);ARM=KV['ARM'];K0=int(KV.get('STROKE',0))
sys.argv=['r19stir2_join.py','probe',f'ARM={ARM}','WORKERS=1']
import r19stir2_join as JN
import r19stir_cycle as SC
JN.SPAT[ARM]=KV['SPATCHAIN']
if 'HUBSFILE' in KV:JN.HUBS[ARM]=KV['HUBSFILE']
TWO=2*np.pi
def br(q):q=np.asarray(q)[3:9];return [int(np.sign(np.sin(q[2]))),int(np.sign(np.sin(q[4])))]
if __name__=='__main__':
 M=JN.scene('stir');r,U,lab=JN.spat_end();E=U[-1].copy()
 W=json.load(open(f'{SC.OUT}/works.json'));G=SC.groups(W['works']);out=[]
 print('spatula end',np.round(np.degrees(E[3:9]),1).tolist(),'cart',round(E[0],4),'branch (elbow, wrist)',br(E))
 for sign in (-1,1):
  for gi,g in enumerate(G.get((K0,sign),[])):
   S=np.array(g['rep']['states'][0],float)
   X,p0,R0,pe=JN.self_motion(M,E,S);d=(X[-1,3:9]-S[3:9]+np.pi)%TWO-np.pi;dend=float(np.degrees(np.abs(d)).max())
   o=dict(stroke=K0,sign=sign,group=gi,members=g['n'],branch=br(S),start_deg=np.degrees(S[3:9]).round(2).tolist(),
          self_motion_states=len(X),max_pose_err_mm=round(pe*1e3,4),end_vs_start_deg_mod2pi=round(dend,4),reaches=bool(dend<1e-4 and sign==JN.SIGN))
   out.append(o);print(json.dumps(o))
 os.makedirs('results/r19/stir/m2join',exist_ok=True)
 json.dump(dict(arm=ARM,spatula_chain=KV['SPATCHAIN'],spatula_end_deg=np.degrees(E[3:9]).round(2).tolist(),spatula_end_branch=br(E),join_sign=JN.SIGN,probes=out),
           open(f'results/r19/stir/m2join/probe_{ARM}.json','w'),indent=1)
