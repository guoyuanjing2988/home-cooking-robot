"""R19 pot zone (GitHub #37 spider, #8 lid): r17chain.py run unchanged, with the kitchen19pot layer and two
optional, STRICTER-or-rule-exact additions. New file; r17chain.py is executed from its source (as r19enc_adopt.py
does), nothing in it is edited, and its defaults are unchanged.

python r19pot_chain.py ACT=spider|lid ... <every r17chain.py option> [SPX= SPY=] [RACK=keyed] [WINDOW=1]
                       [CABGATE=<mm>] [TAG=..] ARM=ur5e_enc2_pgc PY=.15
 SPX / SPY   spider rest (kitchen19pot.install(spider=...); r17chain.py reads the same keys)
 RACK=keyed  the keyed lid rack (V-saddle with lead-in V-grooves, kitchen19pot.py) instead of the R16 base + fins
 WINDOW=1    the declared lid insertion contact window (kitchen19pot.window(), DECISIONS 2026-10-08): while the
             TCP is on the last 50 mm of the straight move down the rack's insertion axis, with the window's
             rotation, the held lid parts vs the keyed rack parts are allowed (Checker.permissions, the same
             place the checker's own grasp / release windows act); every other pair keeps the 10 / 5 mm gates
 CABGATE=e   an EXTRA planning gate of e mm on top of the normal gap for every robot geom vs the overhead
             fixtures of the pot zone (cabinet over the hood, the hood, upper cabinet 2, its door and door sensor):
             e = 5 -> arm >= 15 mm, gripper / held >= 10 mm from them (#37: the docking-stop tilt budget). It is
             applied to every followed step, join, shuffle, grasp approach, and to the anchor candidates (exact
             GJK lower bound, distance.Bounds.pair); it only rejects states, it never accepts one the checker rejects.
Output: results/r19/pot/chain_<ACT>_s<SIGN>[_<TAG>]_<arm>.json (r17chain.py's result, plus "r19pot": the layer,
the window and the gate)."""
import sys,os,json
sys.path.insert(0,'.')
import numpy as np,mujoco
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
import kitchen19pot as P
LAYER=P.install_kv(KV)
WIN={'W':None}
UPPER=('r14_upper_over_hood','r14_hood','upper_cabinet_2','r07_closed_door_2_0','door_pause_sensor_2_0')
EXTRA=float(KV.get('CABGATE',0))/1000.
import checker as _chk
_orig_perm=_chk.Checker.permissions
def _perm(self,kind):
 allowed=_orig_perm(self,kind)
 W=WIN['W']
 if W is not None:
  sid=self.m.site('R_prep').id
  if P.in_window(W,self.d.site_xpos[sid],self.d.site_xmat[sid].reshape(3,3)):
   nm=set(self.gnames);allowed=set(allowed)|{frozenset([a,b]) for a in W['parts'] if a in nm for b in W['faces'] if b in nm}
 return allowed
if KV.get('WINDOW')=='1':_chk.Checker.permissions=_perm
_UG={}
def upper_gate(c,q):
 """min over robot geoms x overhead pot-zone fixtures of (exact distance lower bound - normal gap), m; and the pair."""
 m=c.m;info=_UG.get(id(c))
 if info is None:
  env=[g for g in range(m.ngeom) if not c.robot[g] and m.geom(g).name.startswith(UPPER)]
  rob=[g for g in range(m.ngeom) if c.robot[g] and m.geom_type[g]!=0]
  pr=[]
  for a in rob:
   for b in env:
    r=c.required(c,a,b)
    if r is not None and r[1]!='self':pr.append((a,b,r[0]))
  info=_UG[id(c)]=(np.array([p[0] for p in pr]),np.array([p[1] for p in pr]),np.array([p[2] for p in pr]),sorted(set(rob)),env)
 A,B,N,rob,env=info
 if not len(A):return 1e9,None
 d=c.d;d.qpos[:]=q;mujoco.mj_kinematics(m,d)
 G=sorted(set(rob)|set(env));lo=np.zeros((m.ngeom,3));hi=np.zeros((m.ngeom,3))
 for g in G:
  R=d.geom_xmat[g].reshape(3,3);ctr=d.geom_xpos[g]+R@m.geom_aabb[g,:3];e=np.abs(R)@m.geom_aabb[g,3:];lo[g]=ctr-e;hi[g]=ctr+e
 dl=np.maximum(np.maximum(lo[A]-hi[B],lo[B]-hi[A]),0.);ab=np.sqrt((dl*dl).sum(1))-N
 best=(1e9,None)
 for i in np.argsort(ab):
  if ab[i]>=min(best[0],EXTRA+.02):break
  v=c.bounds.pair(int(A[i]),int(B[i]))['lower_m']-N[i]
  if v<best[0]:best=(float(v),[c.gnames[A[i]],c.gnames[B[i]]])
 return best
src=open('r17chain.py',encoding='utf-8').read();cut=src.index('t0=time.monotonic();pieces={}')
sys.argv=[sys.argv[0]]+[a for a in sys.argv[1:] if a.split('=',1)[0] not in ('RACK','WINDOW','CABGATE')]
g={'__name__':'r17chain_pot','__file__':os.path.abspath('r17chain.py')}
exec(compile(src[:cut],'r17chain.py','exec'),g)
if KV.get('WINDOW')=='1':WIN['W']=P.window(sign=g['SIGN'])
if EXTRA>0:
 _st=g['state']
 def state(c,q,full):
  hits,rmin=_st(c,q,full)
  if not hits:
   v,pr=upper_gate(c,q)
   if v<EXTRA:hits=[dict(pair=pr,real_gap_mm=None,reason=f'r19pot CABGATE: {1000*v:.1f} mm past the normal gap < {1000*EXTRA:.1f}')]
  return hits,rmin
 g['state']=state
_cd=g['candidates']
def candidates(k):
 out,stat=_cd(k);out=[dict(c_,src='stored-branch seed' if i<stat.get('ur_seeds_ok',0) else 'solver') for i,c_ in enumerate(out)]
 if EXTRA<=0:return out,stat
 keep=[c_ for c_ in out if upper_gate(g['ch'],np.array(c_['q'],float))[0]>=EXTRA];stat=dict(stat,r19pot_cabgate_dropped=len(out)-len(keep))
 return keep,stat
g['candidates']=candidates
_save=g['save'];OUTF=[]
def save(fn,res):
 fn=fn.replace('results/r17/','results/r19/pot/');os.makedirs('results/r19/pot',exist_ok=True)
 res=dict(res,r19pot=dict(layer=LAYER,window=None if WIN['W'] is None else {k:(v.tolist() if hasattr(v,'tolist') else v) for k,v in WIN['W'].items()},
  cabgate_extra_mm=EXTRA*1000,upper_fixtures=list(UPPER),argv=sys.argv[1:]+[f'{k}={KV[k]}' for k in ('RACK','WINDOW','CABGATE') if k in KV]))
 OUTF.append(fn);return _save(fn,res)
g['save']=save
def partial():
 """PARTIAL=<stored chain json> REANCHOR=<kf>,<kf>: only the named anchors (the ones whose keyframes depend on the
 moved fixture, e.g. the spider's pick and 'on the rest') are solved again (r17chain candidates(), the same
 TRIES / SEEDS / SEEDUR), followed to their meet (r17chain follow()) and joined there to the STORED arrival from
 the other side (r17chain meet_join(): joint-space join, food within 5 cm / 15 deg, shuffle if the carts differ);
 the grasp approach / release retreat of each is r17chain approach(). Everything between those meets is the
 stored play, verbatim. Of the candidates that pass, the one with the largest exact overhead clearance (the
 CABGATE measure) on its piece + approach + join is kept. The assembled play must then pass r19pot_check.py
 (<= 4 mm, full checker) like any stored chain."""
 import re,time
 t0=time.monotonic();r0=json.load(open(KV['PARTIAL']));P0=np.array(r0['play'],float)
 A,M,KF,GR=g['A'],g['M'],g['KF'],g['GR'];REA=[int(v) for v in KV['REANCHOR'].split(',')]
 steps={tuple(int(re.findall(r'#(\d+)',p[k])[0]) for k in ('frm','to')):p['steps'] for p in r0['pieces']}
 # the stored play's layout, as r17chain.py assembles it (a straight join with arm_deg 0 stores 2 states)
 assert A[0]==0 and A[-1]==len(KF)-1,'layout: action must start and end at an anchor'
 arr={};idx=1;mid_j={}
 for a,b in zip(A,A[1:]):
  x=[mm for mm in M if a<mm<b][0];arr[(a,x)]=idx+steps[(a,x)]-1;idx+=steps[(a,x)]
  j=next(jj for jj in r0['joins'] if jj['at']==KF[x]['label']);assert j.get('arm_deg',0)==0 and 'cart_m' not in j,'layout: only zero joins supported'
  idx+=2;arr[(b,x)]=idx-1;idx+=steps[(b,x)]-1+1
 assert idx==len(P0),(idx,len(P0))
 ch,sid=g['ch'],g['sid']
 for (a,x),i in arr.items():   # verify: the TCP of each arrival is the meet's object pose
  pt_,Rt_=K.tcp_pose(g['OBJ'],KF[x]['R'],KF[x]['p'],g['SIGN']);ch.d.qpos[:]=P0[i];mujoco.mj_kinematics(ch.m,ch.d)
  assert np.linalg.norm(ch.d.site_xpos[sid]-pt_)<1e-3,('layout check failed',a,x,i)
 out={};log=[]
 for a in REA:
  x=g['sides'](a)[0];other=max(b for b in A if b<x) if a>x else min(b for b in A if b>x);q_other=P0[arr[(other,x)]]
  cs,stat=g['candidates'](a);print(KF[a]['label'],'start candidates',len(cs),stat,flush=True);best=None
  world=dict(GR)[a]
  for i,c_ in enumerate(cs[:g['TRIES']]):
   pc,f=g['follow'](a,x,c_['q'])
   if f:log.append(dict(anchor=KF[a]['label'],cand=i,ok=False,fail=f));print(' cand',i,'fail',f,flush=True);continue
   ap=g['approach'](a,world,c_['q'])
   if not ap['ok']:log.append(dict(anchor=KF[a]['label'],cand=i,ok=False,fail=dict(approach={k:v for k,v in ap.items() if k!='qs'})));print(' cand',i,'approach fail',ap.get('hits'),flush=True);continue
   j=g['meet_join'](pc[-1]['q'],q_other,x) if a<x else g['meet_join'](q_other,pc[-1]['q'],x)
   if not j['ok']:log.append(dict(anchor=KF[a]['label'],cand=i,ok=False,fail=dict(join={k:v for k,v in j.items() if k!='qs'})));print(' cand',i,'join fail',{k:v for k,v in j.items() if k!='qs'},flush=True);continue
   qs_all=[np.array(c_['q'])]+[np.array(s_['q']) for s_ in pc]+[np.array(q) for q in ap['qs']]+[np.array(q) for q in j['qs']]
   ug=min(upper_gate(ch,q)[0] for q in [np.array(c_['q'])]+[np.array(s_['q']) for s_ in pc]+[np.array(q) for q in j['qs']])
   ce=g['_empty'][json.dumps(world,sort_keys=True)];ug=min(ug,min(upper_gate(ce,np.array(q))[0] for q in ap['qs']))
   log.append(dict(anchor=KF[a]['label'],cand=i,src=c_.get('src'),ok=True,cart=round(c_['q'][0],3),overhead_min_mm=round(1000*ug,2),join_deg=j['arm_deg']));print(' cand',i,c_.get('src',''),'ok cart',round(c_['q'][0],3),'overhead (past normal gap) %.2f mm'%(1000*ug),'join',j['arm_deg'],flush=True)
   if best is None or ug>best['ug']:best=dict(ug=ug,c=c_,pc=pc,ap=ap,j=j,i=i)
   if sum(1 for l_ in log if l_['anchor']==KF[a]['label'] and l_['ok'])>=int(KV.get('KEEP',6)):break
  out[a]=dict(best=best,x=x,stat=stat)
 ok=all(v['best'] is not None for v in out.values())
 res=dict(act=g['ACT'],obj=g['OBJ'],arm=g['ARM'],**({'plate_y':float(KV['PY'])} if 'PY' in KV else {}),grasp_sense=g['SIGN'],design=g['DESIGN'],scene=g['SCENE'],wok_tilt=float(KV.get('GTILT',0)),
  wok_grasp=KV.get('GRASP','top'),tool_xy={k_:list(v) for k_,v in K.TOOL_XY.items()},ok=ok,partial_of=KV['PARTIAL'],reanchored=[KF[a]['label']+f'#{a}' for a in REA],tries=log,
  keyframes=[dict(i=i,label=k_['label'],p=np.round(k_['p'],3).tolist(),c=k_['c'],anchor=k_['anchor'],meet=k_['meet']) for i,k_ in enumerate(KF)])
 if ok:
  # assemble: new ends + the stored middle verbatim
  P=[];a0,aN=A[0],A[-1];new0=out.get(a0);newN=out.get(aN)
  def jq(j,qa,qb):
   qs=[np.array(q) for q in j['qs']]
   if np.max(abs(qs[-1]-qb))>1e-9:qs.append(np.array(qb))
   return qs
  if new0:P+=[np.array(new0['best']['c']['q'])]+[np.array(s_['q']) for s_ in new0['best']['pc']]+jq(new0['best']['j'],None,P0[arr[(A[1],new0['x'])]]);i0=arr[(A[1],new0['x'])]+1
  else:i0=0
  iN=arr[(A[-2],newN['x'])] if newN else len(P0)-1
  P+=list(P0[i0:iN+1])
  if newN:P+=jq(newN['best']['j'],None,newN['best']['pc'][-1]['q'])[1:]+[np.array(s_['q']) for s_ in reversed(newN['best']['pc'][:-1])]+[np.array(newN['best']['c']['q'])]
  res['play']=[q.tolist() for q in P]
  apps=[];aqs=[]
  for k,world in GR:
   if k in out:ap=out[k]['best']['ap'];apps.append({k_:v for k_,v in ap.items() if k_!='qs'});aqs.append(ap['qs'])
   else:i_=[a for a in r0['approaches']].index(next(a for a in r0['approaches'] if a['kf']==k));apps.append(r0['approaches'][i_]);aqs.append(r0['approach_qs'][i_])
  res['approaches']=apps;res['approach_qs']=aqs
  res['anchors']={KF[a]['label']+f'#{a}':dict(ok=True,cand=v['best']['i'],cart=round(v['best']['c']['q'][0],3),start_reserve_mm=round(v['best']['c']['reserve_mm'],1),overhead_min_past_gap_mm=round(1000*v['best']['ug'],2)) for a,v in out.items()}
  res['joins']=[dict({k_:v for k_,v in o['best']['j'].items() if k_!='qs'},at=KF[o['x']]['label']) for o in out.values()]
  res['pieces_new']=[dict(frm=KF[a]['label']+f'#{a}',to=KF[o['x']]['label']+f"#{o['x']}",steps=len(o['best']['pc']),time_s=round(sum(s_['dt'] for s_ in o['best']['pc']),1)) for a,o in out.items()]
  # time: the stored action time minus the replaced pieces / joins / approaches, plus the new ones
  old=sum(p['time_s'] for p in r0['pieces'] if int(re.findall(r'#(\d+)',p['frm'])[0]) in out)+sum(.6 for a in out)+sum(r0['approaches'][[x_['kf'] for x_ in r0['approaches']].index(a)]['time_s'] for a in out)
  new=sum(sum(s_['dt'] for s_ in o['best']['pc'])+o['best']['j']['s']+o['best']['ap']['time_s'] for o in out.values())
  res['time_s']=round(r0['time_s']-old+new,1);res['stored_time_s']=r0['time_s']
  res['max_pgc_moment_Nm']=r0.get('max_pgc_moment_Nm');res['max_joint_ratio']=r0.get('max_joint_ratio')
 res['elapsed_s']=round(time.monotonic()-t0)
 fn=f"results/r17/chain_{g['ACT']}_s{g['SIGN']:+d}"+('_'+KV['TAG'] if 'TAG' in KV else '')+g['arms'].tag(g['ARM'])+'.json';save(fn,res)
 print(OUTF[-1]);print(json.dumps({k_:v for k_,v in res.items() if k_ not in ('play','approach_qs','keyframes','tries')},default=str))
if 'PARTIAL' in KV:
 K=g['K'];partial()
else:exec(compile(src[cut:],'r17chain.py','exec'),g)
