"""Locate first direct-fold rejection in both directions; diagnostic only."""
import os,sys,json,math,time
os.environ['R07_LAYOUT']=sys.argv[1]
import runtime_v6_r07 as v
import numpy as np,mujoco
from motion_v6_r07 import Planner,mo
from point_bound import PointBound
ID=v.ID;idle=json.loads((v.O/'layouts'/f'{ID}_idle.json').read_text());ch=v.scene(0);ch.xml=(v.H/'models'/f'{ID}_fold_closed_doors.xml').read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False
d=json.loads((v.O/'static_v6'/ID/'0.json').read_text());a=np.array(d['witness']['poses'][0]['q']);b=mo.shortq(ch,a,np.array(idle['q']));pb=PointBound(ch);result=[]
for reverse in (False,True):
 x,y=(b,a) if reverse else (a,b);pl=Planner(ch,{},seconds=65);n=max(1,math.ceil(pb.segment_bound(x,y)/.004));start=time.monotonic();hit=None
 for i in range(n+1):
  q=x+(y-x)*i/n
  if not pl.state(q,{}):hit=pl.last;break
 result.append(dict(reverse=reverse,pass_=hit is None,first_bad_fraction=i/n,states_checked=i+1,max_point_step_mm=pb.segment_bound(x,y)/n*1000,blocker=hit,elapsed_s=time.monotonic()-start))
(v.O/'layouts'/f'{ID}_direct_probe_v6.json').write_text(json.dumps(result,indent=2));print([(r['reverse'],r['first_bad_fraction'],[(h['pair'],h['real_gap_mm']) for h in (r['blocker'] or {}).get('blockers',[])[:3]]) for r in result],flush=True)
