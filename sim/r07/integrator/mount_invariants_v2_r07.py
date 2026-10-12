"""Exact mount-obstruction evidence for UR5e's axisymmetric shoulder capsule."""
import json,math
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';rows=[]
for file in sorted(p for p in (O/'layouts').glob('L*.json') if len(p.stem)==3):
 c=json.loads(file.read_text());a=math.radians(c['mount_deg']);y=c['front_mount_y'];z=c['height']
 center_y=y-.123*math.sin(a);center_z=z+.123*math.cos(a)
 ymin=center_y-(.06+.06*abs(math.sin(a)));ymax=center_y+(.06+.06*abs(math.sin(a)))
 zmin=center_z-(.06+.06*abs(math.cos(a)));zmax=center_z+(.06+.06*abs(math.cos(a)))
 wall_gap=.60-ymax;front_reserve=ymin-.24
 row=dict(layout=c['id'],config=c,UR5e_fixed_shoulder_capsule=dict(radius_m=.06,half_segment_m=.06,axis_center_from_base_m=.123,y_min_m=ymin,y_max_m=ymax,z_min_m=zmin,z_max_m=zmax,wall_gap_mm=wall_gap*1000,front_strip_reserve_mm=front_reserve*1000),working_ever_possible=wall_gap>=.010-1e-9,park_ever_possible=wall_gap>=.010-1e-9 and front_reserve>=-1e-9 and zmax<=1.34+1e-9,proof='OEM shoulder body offset0.163m, capsule localcentre z=-0.04m, radius0.06m and half-segment0.06m. First joint rotates about this same local Z axis; the capsule is axisymmetric and unchanged by that rotation. All downstream joints and carriageX likewise preserve its Y/Z bounds. Bounds are exact for every joint configuration, without shrinking the OEM model.',scope='Necessary mount conditions only. A passing necessary condition is not a reachable task, torque, full folded envelope or path certificate.')
 rows.append(row)
(O/'mount_invariants.json').write_text(json.dumps(dict(rows=rows,source='sources/menagerie/universal_robots_ur5e/ur5e.xml'),indent=2))
print([(r['layout'],r['working_ever_possible'],r['park_ever_possible'],r['UR5e_fixed_shoulder_capsule']['wall_gap_mm']) for r in rows])
