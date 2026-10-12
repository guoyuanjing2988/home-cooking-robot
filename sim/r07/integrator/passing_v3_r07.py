"""One-lane passing diagnostic: complete robot retained, no passing credit."""
import os,sys,json,hashlib
os.environ['R07_LAYOUT']=sys.argv[1]
import numpy as np,mujoco
import runtime_v2_r07 as v
from motion_v2_r07 import Planner
idle=json.loads((v.O/f'layouts/{v.ID}_idle.json').read_text());ch=v.scene(104);ch.xml=(v.H/idle['model_xml']).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False
a=np.array(idle['q']);b=a.copy();ri,li=[ch.qa[s+'_carriage_x'] for s in ('R','L')];b[ri],b[li]=a[li],a[ri];cross=(a+b)/2;hits,mins,_=v.f.contacts(ch,cross);v.s.PARK=a.copy();result=Planner(ch,{},seconds=65,seed=997034).plan(a,b,{},{})
out=v.O/'motion_v2'/v.ID;out.mkdir(parents=True,exist_ok=True);xml=f'models/{v.ID}_passing.xml';(v.H/xml).write_text(ch.xml)
row=dict(pass_=False,geometry_proposal_pass=result['ok'],planner=result,q_crossing=cross.tolist(),model_xml=xml,model_sha256=hashlib.sha256(ch.xml.encode()).hexdigest(),crossing_hits=hits,scope='One shared lane. Continuous carriage-order swap requires equal carriageX; overlapping fixed carriage blocks reject that crossing. The posed crossing render is NOT an executed state. Normal operation must preserve carriage order.')
(out/'passing.json').write_text(json.dumps(row,indent=2));print('PASSING',v.ID,result['ok'],'crossing records',len(hits),flush=True)
