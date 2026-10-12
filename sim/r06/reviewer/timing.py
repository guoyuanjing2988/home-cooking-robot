"""Independent synchronized prefix duration and serial-chain acceleration bound."""
import os
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[n]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import sys,json,math
from pathlib import Path
import numpy as np
H=Path(__file__).resolve().parent;ROOT=H.parents[2];UP=ROOT/'sim/r06/integrator';sys.path.insert(0,str(UP));import cell as c
ch=c.Cell(7);pb=c.PointBound(ch);path=json.loads((UP/'results/executed_prefix.json').read_text())['paths'][0];rows=[];total=0
def curvature(a,b):
    dq=np.abs(b-a);ch.pose(a);radii={};bygeom={}
    for g,j,k,down in pb.levers:
        radius=np.linalg.norm(ch.d.geom_xpos[g]-ch.d.xanchor[j])+ch.m.geom_rbound[g]
        radius+=pb.weights[g,down]@dq[down]
        radii[g,k]=min(pb.weights[g,k],radius);bygeom.setdefault(g,[]).append((k,list(down)))
    values=np.zeros(ch.m.ngeom)
    for g,ancestors in bygeom.items():
        for k,down in ancestors:
            values[g]+=radii[g,k]*dq[k]**2
            # Mixed Hessian j(ancestor),k(descendant): rotation of the
            # descendant point derivative has norm <=R_descendant.
            for distal in down:
                if (g,distal) in radii:values[g]+=2*dq[k]*dq[distal]*radii[g,distal]
                elif distal in pb.slides:values[g]+=2*dq[k]*dq[distal]
    return float(max(values))
for a,b in zip(path['path'],path['path'][1:]):
    a=np.array(a);b=np.array(b);dq=np.abs(b-a);B=pb.segment_bound(a,b)
    limits=[(B,.1,.15)]+[(dq[ch.qa[n]],.2,.25) for n in c.ARM]+[(dq[ch.qa[n]],.01,.02) for n in ('R_jaw_minus','R_jaw_plus')];limits=[x for x in limits if x[0]>1e-14]
    v=min(speed/dist for dist,speed,acc in limits);ac=min(acc/dist for dist,speed,acc in limits);peak=min(v,math.sqrt(ac));duration=2/math.sqrt(ac) if 1<=v*v/ac else 1/v+v/ac;total+=duration;C=curvature(a,b)
    rows.append(dict(point_displacement_bound_m=B,duration_s=duration,normalised_speed_peak_s_inverse=peak,normalised_acceleration_s_inverse2=ac,curvature_bound_m=C,point_acceleration_bound_m_s2=B*ac+C*peak**2,point_speed_bound_m_s=B*peak,global_radius_curvature_acceleration_diagnostic_m_s2=B*ac+pb.curvature(b-a)*peak**2))
result=dict(computed_duration_s=total,submitted_duration_s=path['duration_s'],duration_error_s=abs(total-path['duration_s']),point_acceleration_max_m_s2=max(x['point_acceleration_bound_m_s2'] for x in rows),point_speed_max_m_s=max(x['point_speed_bound_m_s'] for x in rows),segments=rows,proof='q(s)=a+s*dq. Diagonal hinge Hessian <= its radius; mixed ancestor/descendant Hessian <= descendant radius; ancestor hinge/slide mixed derivative <=1. Radii bounded over the segment by global or starting radius plus downstream displacement. Acceleration <=B*s_ddot+C*s_dot^2.',scope='Only the accepted three-segment empty-arm approach; no full-meal timing or future loaded motions certified')
(H/'results/timing.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print('PREFIX TIMING',total,'max point acceleration bound',result['point_acceleration_max_m_s2'],flush=True)
