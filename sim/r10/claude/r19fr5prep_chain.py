"""R19 #2 (FR5) prep sets: r19prepchain.py executed unchanged from its source, plus one opt-in. New file; nothing
shared is edited (r19prepchain.py is read, patched in memory only, and run with exec, as r19fr5_check.py runs
r19pot_check.py).
 SEEDUR=<checked UR5e prep chain json>   extra IK starts at every anchor = the play states of that chain, mapped to
     this arm through arms.py's mount yaw / gripper clocking (q1 - yaw, q6 - clock), each re-solved exactly at the
     anchor (<= 0.5 mm / 0.2 deg) and fully checked like a solver candidate; they go first in the candidate list.
     This is r17chain.py's ur_seeds() (R19 #2, used for the FR5 cooking chains), copied verbatim.
Without SEEDUR the run is identical to r19prepchain.py. Output name and every other option as r19prepchain.py
(results/r19/prep/chain_<ACT>_<TAG>_<arm>.json); use a TAG that is not used by any UR5e run.
python r19fr5prep_chain.py ACT=<set> ARM=fr5_j6_pgc_sp20 SEEDUR=results/r19/prep/chain_<set>_<..>_ur5e_enc2_pgc.json TAG=fr5ur [..]"""
def patched_source():
 """r19prepchain.py's source with the SEEDUR opt-in (also used by r19fr5prep_gap.py)."""
 _src=open('r19prepchain.py',encoding='utf-8').read()
 assert _src.count(_a)==1 and _src.count(_b)==1,'r19prepchain.py changed: the SEEDUR patch points are not unique'
 return _src.replace(_a,_seed+_a).replace(_b,_new)
_a="_cands={}\ndef candidates(k):"
_b=" out=sorted(out,key=lambda c_:-c_['reserve_mm']);_cands[key]=(out,stat);return _cands[key]"
_seed='''SEEDUR=KV.get('SEEDUR')   # R19 #2 (r17chain.py ur_seeds, verbatim)
_seedP=None
def ur_seeds(k,pt_,Rt_):
 global _seedP
 if _seedP is None:
  P=np.array(json.load(open(SEEDUR))['play'],float);P[:,3]-=np.radians(arms.ARMS[ARM].get('mount_yaw_deg',0.));P[:,8]-=np.radians(arms.ARMS[ARM].get('clock_deg',0.));_seedP=P
 sol=[]
 for q0 in _seedP[::2]:
  q=q0.copy();q[-2:]=JAW_HELD
  for j in range(6):
   c_=[q[3+j]+i*2*np.pi for i in (-2,-1,0,1,2) if lo[j]-1e-9<=q[3+j]+i*2*np.pi<=hi_[j]+1e-9]
   if c_:q[3+j]=min(c_,key=abs)
  if isinstance(KF[k]['c'],float):q[0]=KF[k]['c']
  qs=q.copy();q,pe,re,_=solve_to(ch,q,pt_,Rt_)
  if pe<=.0005 and re<=np.radians(.2):sol.append((float(np.max(abs(q[3:9]-qs[3:9]))+abs(q[0]-qs[0])),q))
 got=[];seen=[]
 for d_,q in sorted(sol,key=lambda x:x[0]):
  if any(np.max(abs(q[3:9]-s_))<np.radians(2) and abs(q[0]-c0)<.01 for s_,c0 in seen):continue
  seen.append((q[3:9].copy(),q[0]));r=ch.check(q,full=True,mass=0.)
  if r['ok']:got.append(dict(q=q.tolist(),reserve_mm=min(v['reserve_mm'] for cat,v in r['clearance'].items() if cat!='self')))
  if len(seen)>=12:break
 return sorted(got,key=lambda c_:-c_['reserve_mm'])
'''
_new=""" out=sorted(out,key=lambda c_:-c_['reserve_mm'])
 if SEEDUR:sd=ur_seeds(k,pt_,Rt_);stat['ur_seeds_ok']=len(sd);out=sd+out   # R19 #2: the mapped UR5e states first
 _cands[key]=(out,stat);return _cands[key]"""
if __name__=='__main__':exec(compile(patched_source(),'r19prepchain.py','exec'))
