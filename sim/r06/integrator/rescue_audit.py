from rescue_cell import *
import argparse
p=argparse.ArgumentParser();p.add_argument('--inspect',type=int);a=p.parse_args()
if a.inspect:
 ch=Workcell(a.inspect);rows=[]
 for n in ('R_geom_0','R_geom_1','R_geom_2','R_geom_3','R_geom_4','R_geom_5','mount_plate','R_carriage_plate'):
  if n not in ch.gnames:continue
  g=ch.gnames.index(n);b=int(ch.m.geom_bodyid[g]);rows.append(dict(name=n,body=ch.m.body(b).name,body_pos=ch.m.body_pos[b].tolist(),weld=int(ch.weld[g]),geom_type=int(ch.m.geom_type[g]),size=ch.m.geom_size[g].tolist(),local_pos=ch.m.geom_pos[g].tolist(),world_pos=ch.d.geom_xpos[g].tolist(),quat=ch.m.geom_quat[g].tolist()))
 print(json.dumps(rows,indent=2));write(f'v2/audit/inspect_L{a.inspect}.json',rows)
