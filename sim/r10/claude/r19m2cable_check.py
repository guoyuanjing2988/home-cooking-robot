"""R19 #36 / #42 (m2 cable): r19cable_check.py run unchanged for the m2 sets, with the scenes each set was certified in
(new file; writes under results/r19/cable/m2/<mode>/). Options, all applied at the top level so the pool workers (which
re-run this file as __mp_main__) do the same:
 CANDS=<json>  screening model: the candidate runs in the json (r19cable2_tc ROUTES-style specs, keys '<routing>_m2*') are
               registered as routings and as the arm options '<m2 base>c_M2X' (every candidate its own geom group
               'cable.<key>', as r19cable2_screen.py). Use with CABLEONLY=1: a SCREEN, never a certificate.
 P5=1          r19prep5_verify.py in place of r19prep_verify.py (as r19prep5_cable.py): the prep sets that need the T2L cradle
               layers (fold, unfold, ct2s, stgwok).
 WOKPY=1       a wok chain's own plating spot moved to PY (the rule of r19mount_check.py / r19fr5_check.py, used for the m2
               wok certificates).
Modes: chains | hub | prep | stir as r19cable_check.py, plus
 join     LIB=<lib_stir_join_*.json>: the STIR_ENTRY states (the exit is the same states reversed) in the stir scene of
          r19cable_check.py's stir mode (r19stir_cycle.model(-1) + the plume rule), as the join's own 'stir' certificate;
 std      LIB=<stir library or join library> SPATCHAIN=<the arm's spatula chain> RACK=keyed SPX=1.56 SPY=.20 PY=.15: the same
          states in the current layout, i.e. the spatula chain's pot-zone scene (r19pot_check.py ctx of that chain's play,
          held spatula), as the 'std' re-checks of r19stir2_join.py / r19spill_cycle.py (their plume rule is the stir
          scene's, checked by the join / stir modes).
python r19m2cable_check.py <mode> <r19cable_check.py arguments> ARM=<arm> [CANDS=..] [P5=1] [WOKPY=1] [WORKERS=8]"""
import sys,os,json
sys.path.insert(0,'.')
MODE0=os.environ.setdefault('R19M2CABLE_MODE',sys.argv[1])   # the spawned pool workers see the rewritten argv[1]: keep the user's mode for them
KV=dict(a.split('=',1) for a in sys.argv[2:] if '=' in a)
if 'CANDS' in KV:
 import r19cable2_tc as _TC,r19cable as _CAB
 _C=json.load(open(KV['CANDS']))
 for _k,_s in _C.items():_TC.ROUTES[_k]=_s;_CAB.ROUTINGS[_k]=dict(_CAB.ROUTINGS[_s['_base']],tc=_k)
 _CAB.SCREENS['M2X']=list(_C)
 import arms as _arms
 for _b in ('ur5e_enc2_pgc_m2','fr5_j6_pgc_m2'):_arms.ARMS[_b+'c_M2X']=dict(_arms.ARMS[_b],name=_arms.ARMS[_b]['name']+' + m2 tool-connector run candidates (screen)',cable='M2X',cable_source='R19_M2CABLE.md')
if KV.get('P5')=='1':
 import r19prep5_verify
 sys.modules['r19prep_verify']=r19prep5_verify
if MODE0 in ('join','std'):sys.argv[1]={'join':'stir','std':'chains'}[MODE0]   # the r19cable_check mode whose scene is used
import r19cable_check as RC
RC.OUT='results/r19/cable/m2'+('/screen_'+os.path.basename(KV['CANDS'])[:-5] if 'CANDS' in KV else '')   # screens: one folder per candidate file
if RC.MODE=='chains':
 import r19pot_check as RP
 if KV.get('WOKPY')=='1':
  _J=RP.J
  def J(f):
   r=_J(f)
   if 'PY' in KV and r.get('obj')=='wok':   # r19mount_check.py / r19fr5_check.py rule
    sc=dict(r.get('scene',{}));pc=list(sc.get('r15_plate_c',[.43,.13,.85]));pc[1]=float(KV['PY']);sc['r15_plate_c']=[float(v) for v in pc];r['scene']=sc;r['plate_y']=float(KV['PY'])
   return r
  RP.J=J
def lib_parts(L):
 """{part: states}: a stir library by stored segment (as r19cable_check stir mode), a join library: its entry states"""
 import numpy as np
 if 'sets' in L:return {'entry':np.array(L['sets'][0]['states']['q'],float)}
 Q=np.array(L['states']['q'],float);k=np.array(L['states']['kinds']);return {n:Q[k==n] for n in dict.fromkeys(k)}
def main():
 if MODE0=='join':
  L=json.load(open(KV['LIB']));assert L['id']=='STIR_JOIN'
  RC.run({p:('stir',Q) for p,Q in lib_parts(L).items()},'join_'+os.path.basename(KV['LIB'])[:-5],dict(lib=KV['LIB'],note='STIR_ENTRY states in the stir scene (STIR_EXIT = the same states reversed)'))
 elif MODE0=='std':
  import numpy as np,r19smooth as S
  L=json.load(open(KV['LIB']));f=KV['SPATCHAIN'];P=lib_parts(L);_st=RP.states
  def states(f_,part):   # the library's own states (joint-linear between them, cut to <= 4 mm with the checked model)
   if part in P:X,src,sp=S.sample_poly(np.asarray(P[part],float),S.FastBound(RP.ctx(f_,'play')));return X,sp
   return _st(f_,part)
  RP.states=states
  RC.run({p:((f,p),Q) for p,Q in P.items()},'std_'+os.path.basename(KV['LIB'])[:-5],dict(lib=KV['LIB'],scene_chain=f,note='library states in the spatula chain pot-zone scene (current layout)'))
 else:RC.main()
if MODE0=='std':   # every part in the spatula chain's play scene (held spatula); here so the workers map it too
 _co=RC.ctx
 def _ctx(key):
  key=tuple(key) if isinstance(key,list) else key
  return _co((key[0],'play'))
 RC.ctx=_ctx
if __name__=='__main__':main()
