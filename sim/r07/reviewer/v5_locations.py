from v5_common import *
rows=[];seen=set()
for file in sorted((I/'results/connections_v5'/v.ID).glob('*.json'),key=lambda p:int(p.stem)):
 r=json.loads(file.read_text())
 for trace in r['conditional_state_construction']:
  if trace['operation']!='conditional_food_transformation':continue
  ev=trace['event'];key=(ev['product'],ev['operation'])
  if key in seen:continue
  seen.add(key);obj=r['state_before']['objects']['food:'+ev['product']];pos=np.array(obj['pose'])[:3,3];row=dict(connection=r['connection'],product=key[0],operation=key[1],station=ev['station'],food_reference_center_m=pos.tolist(),owner=obj['owner'],executed=False)
  if ev['station']=='BFP610_processing_bowl':
   ch=v.scene(r['from_stroke']['index']);mujoco.mj_forward(ch.m,ch.d);g=ch.m.geom('bfp610_complete_envelope').id;c=ch.d.geom_xpos[g];size=ch.m.geom_size[g];row.update(appliance_box_lo=(c-size).tolist(),appliance_box_hi=(c+size).tolist(),reference_center_inside_complete_external_box=bool(np.all(abs(pos-c)<=size)))
  rows.append(row)
dump('transformation_locations.json',dict(first_conditional_occurrences=rows,scope='Location at first occurrence of each conditional transformation; not executed motion. Entire external BFP box is a generous necessary containment test, not exact internal-bowl geometry.'))
print(json.dumps(rows,indent=2))
