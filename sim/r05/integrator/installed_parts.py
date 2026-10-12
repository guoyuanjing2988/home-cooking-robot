"""Inventory the exact full-cell MuJoCo geometry; no replacement geometry."""
import json,csv
import mujoco
import motion_check as mo
s=mo.s;H=s.HERE
def main():
 ch,hands=mo.empty_cell();m=ch.m;d=ch.d
 motion=H/'results/motion.json'
 d.qpos[:]=json.loads(motion.read_text())['parking']['q'] if motion.exists() else s.PARK
 mujoco.mj_forward(m,d)
 records=[]
 for g,name in enumerate(ch.gnames):
  records.append(dict(name=name,body=mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_BODY,int(m.geom_bodyid[g])),classification='robot_or_attached_frame' if m.geom_contype[g]&2 else 'environment',geom_type=int(m.geom_type[g]),mujoco_size=m.geom_size[g].tolist(),world_position_m=d.geom_xpos[g].tolist(),world_rotation=d.geom_xmat[g].tolist(),contype=int(m.geom_contype[g]),conaffinity=int(m.geom_conaffinity[g]),collision_margin_m=float(m.geom_margin[g])))
 out=dict(schema='r03.installed.fullcell.inventory',config=s.model.CONFIG,xml='models/installed_cell.xml',geom_count=len(records),body_count=m.nbody,parts=records,notes=['Exact union segments preserve long-beam dimensions and divided mass.', 'Primitives and OEM collision hulls are the checker geometry; MuJoCo size entries use half-lengths where appropriate.', 'Stored tools, all bowls and four raw input foods are present in this inventory.', 'Internal cutter mechanisms, OEM lumen shape, moving cable routing and pusher mechanisms remain unqualified envelope assumptions; this is not a complete manufacturing BOM.'])
 (H/'models/installed_cell.xml').write_text(ch.xml,encoding='utf-8')
 (H/'results/installed_parts.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
 with (H/'results/installed_parts.csv').open('w',newline='',encoding='utf-8-sig') as file:
  writer=csv.DictWriter(file,fieldnames=['name','body','classification','geom_type','mujoco_size','world_position_m','contype','conaffinity'])
  writer.writeheader();writer.writerows({k:r[k] for k in writer.fieldnames} for r in records)
 print('installed geometry',len(records),'bodies',m.nbody)
if __name__=='__main__':main()
