"""Independent geometric process check, not collision or IK admission."""
import os,sys,json,math
os.environ['R07_LAYOUT']=sys.argv[1]
import runtime_v7_r07 as v
import numpy as np
from scipy.spatial.transform import Rotation
jet=np.array(v.cfg['replacement_faucet']['wash_reference_pos_m']);rows=[]
for i in (33,43):
 ch=v.scene(i);h=v.items[i][1]['poses'][0]['R']
 shape=next(x for x in v.P['tools']['colander']['geometry'] if x['name']=='colander_shell')
 rt=ch.target_rotation(h,0)@Rotation.from_euler('xyz',h.get('object_rotation_deg',[0,0,0]),degrees=True).as_matrix()
 axis=rt@np.array(shape['axis_local']);center=np.array(h['pos'])+rt@np.array(shape['center_m'])
 mouth=center-axis*shape['height_m']/2
 radial=float(np.linalg.norm(mouth[:2]-jet[:2]));radius=shape['radius_m']-shape['thickness_m']
 # Pose tolerance can translate the mouth by at most5mm plus the3degree
 # rotational displacement of its complete offset from the tool origin.
 movement=float(.005+2*np.linalg.norm(mouth-np.array(h['pos']))*math.sin(math.radians(3)/2))
 rows.append(dict(index=i,mouth_center_m=mouth.tolist(),axis=axis.tolist(),jet_xy_m=jet[:2].tolist(),radial_offset_mm=radial*1000,opening_radius_mm=radius*1000,maximum_pose_tolerance_displacement_mm=movement*1000,vertical_jet_hits_opening=radial<=radius,excluded_even_with_pose_tolerance=radial-movement>radius,scope='Straight vertical jet and upright circular opening at first rinse pose; no spray dispersion or food-quality assumption. Drain endpoint is intentionally away from jet.'))
out=dict(layout=v.ID,rows=rows,pass_=all(x['vertical_jet_hits_opening'] for x in rows),qualification='A collision-admitted template is not process success. This test grants no static/path credit. A missed jet remains an unresolved functional station-layout obligation.')
(v.O/'wash_alignment_v7.json').write_text(json.dumps(out,indent=2));print('WASH_ALIGNMENT',out['pass_'],[(x['index'],x['radial_offset_mm']) for x in rows])
