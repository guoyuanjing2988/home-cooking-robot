from common import *
from planner_r05 import Planner
from point_bound import PointBound
import xml.etree.ElementTree as E
ph,sg,key=mo.items[0];ch=mo.scene(ph,sg,0);q=np.array(read('idle.json')['q']);ch.set_contacts(sg['poses'][0]);ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False
hits,mins,_=f.contacts(ch,q);parts=[]
strip=(np.array([-1.8,0,.85]),np.array([1.8,.23,1.35]));corridor=(np.array([-1.6,-.75,.85]),np.array([.6,-.05,1.85]))
def overlap(lo,hi,box):return bool(np.all(hi>box[0]) and np.all(lo<box[1]))
for g,n in enumerate(ch.gnames):
    if not ch.robot[g]:continue
    lo=np.array([ch.bounds.support(g,-v)[k] for k,v in enumerate(np.eye(3))]);hi=np.array([ch.bounds.support(g,v)[k] for k,v in enumerate(np.eye(3))])
    parts.append(dict(name=n,lo_m=lo.tolist(),hi_m=hi.tolist(),door_sweep_gap_lower_mm=float((1.35-hi[2])*1000),front_strip_intersection=overlap(lo,hi,strip),person_corridor_intersection=overlap(lo,hi,corridor),behind_front_with_10mm=bool(lo[1]>=.24-1e-6)))
fold=[];goal=np.array(read('final_static/0.json')['poses'][0]['q']);ib=IndependentBound(ch)
for label,a,b in [('fold',goal,q),('unfold',q,goal)]:
    D=ib.segment(a,b);N=max(1,math.ceil(D/.004));pl=Planner(ch,sg['poses'][0],seed=1107,seconds=65);ch.allowed=[];ch.contact_windows=[];first=None;states=0
    for k in range(N+1):
        v=a+(b-a)*k/N;states+=1
        if not pl.state(v):first=dict(grid_index=k,q=v.tolist(),rejection=pl.last);break
    fold.append(dict(direction=label,pass_=first is None,states_checked=states,grid_intervals=N,max_grid_bound_mm=D/N*1000,first_rejection=first,scope='Independent diagnostic using rejected deployed Q01 empty-hand endpoint and submitted populated tuck; no submitted fold/unfold trajectory exists. Stops at first failure.'))
# Full-size doors' bottom is invariant under their vertical hinge rotations.
tree=E.parse(I/'models/idle_doors_open.xml');doors=[]
for b in tree.findall('.//body'):
    if not b.get('name','').startswith('r07_open_door'):continue
    g=b.find('geom');p=np.fromstring(b.get('pos'),sep=' ');size=np.fromstring(g.get('size'),sep=' ');gp=np.fromstring(g.get('pos'),sep=' ');j=b.find('joint')
    doors.append(dict(name=b.get('name'),dimensions_m=(2*size).tolist(),hinge_axis=np.fromstring(j.get('axis'),sep=' ').tolist(),range_rad=np.fromstring(j.get('range'),sep=' ').tolist(),z_bottom_m=float(p[2]+gp[2]-size[2])))
gap=min(p['door_sweep_gap_lower_mm'] for p in parts)
latest=np.array(read('park_full.json')['q']);lhits,_,_=f.contacts(ch,latest)
dump('idle.json',dict(q=q.tolist(),populated_snapshot_pass=not hits,snapshot_hits=hits,min_clearance=mins,parts=parts,doors=doors,door_sweep_pass=gap>=10-1e-3,door_sweep_min_gap_mm=gap,front_strip_pass=not any(p['front_strip_intersection'] for p in parts),corridor_pass=not any(p['person_corridor_intersection'] for p in parts),doors_checked_against_corridor=False,fold_diagnostics=fold,submitted_fold_obligations=read('idle.json')['fold_paths'],accepted_fold_trajectories=0,full_idle_pass=False,later_park_full_candidate=dict(q_diff_max_rad_or_m=float(np.max(abs(latest-q))),hits=lhits,pass_=not lhits),proof='Exact original-shape support upper bounds for all robot components at the submitted idle.json q; all five 18mm door leaves remain z>=1.35m at every 0..90 degree hinge angle. Vertical separating plane proves full sweep clearance. Corridors tested only against robot parts. Populated-scene collisions and absent admitted fold/unfold roots prevent idle acceptance. Later failed park_full.json is separately rejected; it is not substituted for the reported bare tuck.'))
print('idle doors',gap,'mm','snapshot',not hits,'folds',sum(r['pass_'] for r in fold))
