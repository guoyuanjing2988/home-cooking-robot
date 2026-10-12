"""R15 plating: follow one IK branch through the whole sideways tip (wok held by its grip block,
plate left of the hood, cart parked at CARTX) in STEP° increments, each 96-start solve warm-
started from the previous pose (solver.solve keeps the candidates nearest to it), with the
unchanged checker. A step whose nearest collision-free solution moves any joint more than
BREAK° is a branch change (the arm would have to stop and re-plan with the wok in hand).
Same wok poses as r15reach.py pour (TIP=y, rim-centre pivot, lip DROP above the plate).
python r15tipseq.py [CARTX=.45] [STEP=5] [A0=15] [A1=90] [DROP=.03] [START=<reach json>]
-> results/r15/tipseq_cx<CARTX>.json"""
import sys,os,json,numpy as np
import chain
from scene import build,save
from checker import Checker,reference
from solver import solve
import kitchen15 as K
KV=dict(a.split('=',1) for a in sys.argv[1:])
CX=float(KV.get('CARTX',.45));STEP=float(KV.get('STEP',5));A0=float(KV.get('A0',15));A1=float(KV.get('A1',90));DROP=float(KV.get('DROP',.03));BREAK=float(KV.get('BREAK',20))
PLATE_C=np.array(K.PLATE['c'],float)
def Ry(a):a=np.radians(a);return np.array([[np.cos(a),0,np.sin(a)],[0,1,0],[-np.sin(a),0,np.cos(a)]])
target=PLATE_C+[0,0,K.PLATE['h']+DROP]+np.array([-.05,0,0]);piv=target-Ry(90)@np.array([K.A_RIM,0,0])
a_w,j_w=np.array([0,0,-1.]),np.array([0,1.,0]);bc=K.GRIP['c']-K.WOK0
Rwt=reference.rotation(a_w,j_w);T=np.eye(4);T[:3,:3]=Rwt.T;T[:3,3]=-Rwt.T@bc
cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,r15_wok_held=dict(T_tool_wok=T.tolist()),r15_plate_c=PLATE_C.tolist())
tree,meta=build(cfg,None);ch=Checker(tree,meta);ids=ch.arm_ids
step=lambda q1,q2:float(np.degrees(np.max(abs((np.array(q1)[ids]-np.array(q2)[ids]+np.pi)%(2*np.pi)-np.pi))))
def pose(A):
 R=Ry(A);o=piv-R@np.array([0,0,K.DEPTH]);return o+R@bc,R@a_w,R@j_w
warm=None
if 'START' in KV:
 st=json.load(open(KV['START']));warm=np.array(st['best']['q'])
out=[];prev=warm
for A in np.arange(A0,A1+1e-9,STEP):
 p,ap,jw=pose(A);t=dict(name='tip',points=[list(p)]*2,held=None,kind='transfer',force=None,approach=list(ap),jaws=[tuple(jw)],jaw_q=.015,cart_x=CX)
 r=solve(ch,p,list(ap),target=t,seed=21,warm=None if prev is None else list(prev))
 cands=r['candidates']
 if not cands:out.append(dict(A=float(A),ok=False,status=r['status_counts']));print(A,'no solution',r['status_counts'],flush=True);prev=None;continue
 c=min(cands,key=lambda c:step(prev,c['q'])) if prev is not None else max(cands,key=lambda c:c['reserve_mm'])
 s=step(prev,c['q']) if prev is not None else 0.
 out.append(dict(A=float(A),ok=True,step_deg=round(s,1),branch_change=bool(s>BREAK),reserve_mm=round(c['reserve_mm'],1),q=c['q']));prev=np.array(c['q'])
 print(A,'step',round(s,1),'reserve',round(c['reserve_mm'],1),flush=True)
res=dict(cart_x=CX,step_deg=STEP,break_deg=BREAK,drop_m=DROP,ok=all(o['ok'] for o in out),branch_changes=[o['A'] for o in out if o.get('branch_change')],
 max_step_deg=max((o.get('step_deg',0) for o in out if o['ok']),default=None),min_reserve_mm=min((o['reserve_mm'] for o in out if o['ok']),default=None),poses=out)
os.makedirs('results/r15',exist_ok=True);save(f'results/r15/tipseq_cx{CX:g}.json',res);print(json.dumps({k:v for k,v in res.items() if k!='poses'}))
