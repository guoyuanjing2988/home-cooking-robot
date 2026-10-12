"""Read-only sensitivity adding the original unscaled UR5e base meshes."""
from reverify import *
import xml.etree.ElementTree as E
def add_base(xml):
 root=E.fromstring(xml);base=root.find(".//body[@name='R_arm_base']");asset=root.find('asset')
 raw,folder=s.model.OEM.source_root('UR5e');src=s.model.OEM.namespaced(raw,folder,'R');source=src.find('worldbody/body');added=[]
 existing={x.get('name') for x in asset}
 for i,g0 in enumerate(source.findall('geom')):
  g=copy.deepcopy(g0);name='R_geom_base_source'+str(i);mesh=g.get('mesh')
  if mesh not in existing:
   asset.append(copy.deepcopy(src.find("asset/mesh[@name='"+mesh+"']")));existing.add(mesh)
  g.attrib.pop('class',None);g.set('name',name);g.set('type','mesh');g.set('contype','2');g.set('conaffinity','3');g.set('margin','.01');g.set('mass','1e-9');base.append(g);added.append(name)
 return E.tostring(root,encoding='unicode'),added
def main():
 ph=s.P['phases'][0];ch=s.Checker(ph,ph['segments'][0]);bid=ch.m.body('R_arm_base').id
 original=dict(base_direct_collision_geoms=int(sum(ch.m.geom_bodyid==bid)),source_visual_base_meshes=['base_0','base_1'],source='sources/menagerie/universal_robots_ur5e/ur5e.xml',limitation='Source base has2 visual geoms and no collision geom. R03 removes visual geoms; its base mass remains present.')
 tree,meta=s.model.build(dict(s.model.CONFIG,transport_only=True));xml,added=add_base(E.tostring(tree.getroot(),encoding='unicode'));m=mujoco.MjModel.from_xml_string(xml);env=json.loads((I/'results/torque_envelope.json').read_text())
 audit=object.__new__(s.ck.Checker);audit.desc=s.ck.hand([0,0,1],jaw_axis=[0,1,0]);audit.bind_model(m);envrows=[]
 for n,w in env['witnesses'].items():
  if n[0]!='R':continue
  q=m.qpos0.copy()
  for j,v in zip(meta['arms']['R'],w['joints_rad']):q[audit.qa[j]]=v
  hits=s.ck.Checker.forbidden(audit,q);hits=[h for h in hits if any(a in added for a in h['pair']) and all(a.startswith('R_') for a in h['pair'])]
  envrows.append(dict(joint=n,source_base_self_blockers=hits))
 best=json.loads((I/'results/best.json').read_text());rows=[]
 for key,w in best['witnesses'].items():
  ph=next(p for p in s.P['phases'] if p['id']==w['phase']);sg=next(p for p in ph['segments'] if p['label']==w['label']);ch=s.Checker(ph,sg);xml,added=add_base(ch.xml);ch.bind_model(mujoco.MjModel.from_xml_string(xml));hits=[]
  for pi,po in enumerate(w['poses']):
   ch.set_contacts(sg['poses'][pi]);q=np.array(po['q']);new=ch.forbidden(q)
   hits += [dict(pose=pi,**h) for h in new if any(a in added for a in h['pair'])]
  rows.append(dict(stroke=key,source_base_reference_blockers=hits))
 dump('base_collision_coverage.json',dict(original=original,diagnostic='Add both original base visual meshes as unscaled convex collision geoms, retain explicit inertial mass and all thresholds. Submitted model/results unchanged. This is sensitivity, not a substitute scored model or exhaustive base/frame distance certificate.',main_envelope_witnesses=envrows,selected_stroke_witnesses=rows,new_reference_blocker_strokes=sum(bool(x['source_base_reference_blockers']) for x in rows),geometry_names=added))
 print('base original geoms',original['base_direct_collision_geoms'],'envelope blockers',sum(bool(r['source_base_self_blockers']) for r in envrows),'stroke blockers',sum(bool(x['source_base_reference_blockers']) for x in rows))
if __name__=='__main__':main()
