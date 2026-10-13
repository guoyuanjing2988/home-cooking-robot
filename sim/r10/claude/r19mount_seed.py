"""R19 #42: IK seed files for SEEDUR from a checked FR5 chain (new file). r17chain.py / r19fr5prep_chain.py SEEDUR maps a UR5e
chain onto the target arm by q1 - mount_yaw_deg and q6 - clock_deg (arms.py). To seed an FR5 mount option with the states of
a checked FR5 chain, this writes a copy of that chain with q1 + yaw and q6 + clock (in the UR5e convention), so the mapping
returns the FR5 states exactly. Seeds are only starting points: every candidate is re-solved to the new pose and fully checked.
python r19mount_seed.py SRC=<FR5 chain json> -> results/r19/mount/seed_<name>.json"""
import sys,os,json
sys.path.insert(0,'.')
import numpy as np,arms
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a);r=json.load(open(KV['SRC']));a=arms.ARMS[r['arm']]
P=np.array(r['play'],float);P[:,3]+=np.radians(a.get('mount_yaw_deg',0.));P[:,8]+=np.radians(a.get('clock_deg',0.))
out=dict(play=P.tolist(),seed_of=KV['SRC'],note='q1 + mount_yaw_deg, q6 + clock_deg of '+r['arm']+' (UR5e convention for SEEDUR); not a chain')
fn='results/r19/mount/seed_'+os.path.basename(KV['SRC']);assert not os.path.exists(fn);json.dump(out,open(fn,'w'));print(fn,len(P))
