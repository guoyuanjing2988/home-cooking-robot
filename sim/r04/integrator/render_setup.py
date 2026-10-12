"""Export actual saved MJCF/q poses, with visible acceptance labels."""
import json,copy,sys
import numpy as np,mujoco
import final_check as f
import motion_check as mo
s=f.s;H=s.HERE;R=H/'renders';O=H/'results';R.mkdir(exist_ok=True)
def export(ch,q,name,status,focus=None,label=None):
 m,d=ch.m,ch.d;d.qpos[:]=q;mujoco.mj_forward(m,d);meshes={};geoms=[]
 for g,n in enumerate(ch.gnames):
  if n.startswith(('south_wall','south_cabinets','cabinet_door_sweep','outlet_access')):continue
  typ=int(m.geom_type[g]);a=dict(name=n,type=typ,size=m.geom_size[g].tolist(),pos=d.geom_xpos[g].tolist(),rot=d.geom_xmat[g].reshape(3,3).tolist(),rgba=m.geom_rgba[g].tolist())
  if m.geom_matid[g]>=0:a['rgba']=m.mat_rgba[m.geom_matid[g]].tolist()
  if typ==7:
   i=int(m.geom_dataid[g]);a['mesh']=str(i)
   if str(i) not in meshes:
    va,fa=m.mesh_vertadr[i],m.mesh_faceadr[i];meshes[str(i)]=dict(vertices=m.mesh_vert[va:va+m.mesh_vertnum[i]].tolist(),faces=m.mesh_face[fa:fa+m.mesh_facenum[i]].tolist())
  geoms.append(a)
 (R/(name+'.scene.json')).write_text(json.dumps(dict(config=s.model.CONFIG,label=label or name,status=status,focus=focus,geoms=geoms,meshes=meshes)),encoding='utf-8')
def main():
 best=json.loads((O/'best.json').read_text());summary=json.loads((O/'phase_summary.json').read_text());motion=json.loads((O/'motion.json').read_text()) if (O/'motion.json').exists() else None
 selected=sys.argv[sys.argv.index('--view')+1] if '--view' in sys.argv else None
 if motion and not selected:
  ch,hands=mo.empty_cell();q=motion['parking']['q'];export(ch,q,'overview','CANDIDATE CELL / COMPLETE MEAL FAIL',label='overview');export(ch,q,'parked','PARK '+('PASS' if motion['parking']['pass_'] else 'FAIL')+' / MEAL FAIL',label='parked')
  export(ch,motion['passing']['q_crossing'],'passing','PASSING ROUTE '+('PASS' if motion['passing']['pass_'] else 'FAIL')+' / MEAL FAIL',label='passing')
  if '--transport-only' in sys.argv:
   manifest=json.loads((R/'manifest.json').read_text());manifest['transport_views']=[dict(file=name+'.png',scene=name+'.scene.json',q=motion['passing']['q_crossing'] if name=='passing' else q,status='passing_pass' if name=='passing' and motion['passing']['pass_'] else 'parking_pass' if name=='parked' and motion['parking']['pass_'] else 'candidate_cell_meal_fail') for name in ('overview','passing','parked')]
   (R/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');print('3 final transport-state scene exports',flush=True);return
 manifest=[]
 preferred={'Q02':'wash','Q05':'helper_index_0','Q07':'clean_peel','Q08':'rinse','Q09':'bowl_load','Q10':'load_slicer','Q16':'soak_bok_choy','Q27':'wipe_secondary'}
 for logical in summary['logical_phases']:
  if selected and logical['id']!=selected:continue
  qid=logical['id'];ph=next(p for p in s.P['phases'] if p['id'].split('.')[0]==qid)
  sg=next((a for a in ph['segments'] if a['label']==preferred.get(qid)),ph['segments'][-1]);key=ph['id']+'__'+sg['label'].replace(' ','_')
  checker=s.Checker(ph,sg);w=best['witnesses'].get(key)
  if w:q=w['poses'][-1]['q'];status='STATIC STROKE PASS'
  else:
   raw=json.loads((H/best['stroke_sources'][key]).read_text());q=raw['best']['poses'][-1]['q'];status='REJECTED STATIC CANDIDATE'
  focus=list(sg['poses'][-1]['L' if sg.get('action')=='helper_index' else 'R']['pos']);focus[2]=1.18 if sg['station']=='slicer' else 1.06
  export(checker,q,qid,status+' / '+qid+' '+('PASS' if logical['ok'] else 'FAIL')+' / MEAL FAIL',focus=focus,label=qid+' '+ph['id']+' '+sg['label'][:35])
  manifest.append(dict(file=qid+'.png',logical=qid,instance=ph['id'],stroke=sg['label'],static_witness=bool(w),q=q,scene=qid+'.scene.json'))
 if selected:
  existing=json.loads((R/'manifest.json').read_text());existing['views']=[manifest[0] if v['logical']==selected else v for v in existing['views']];(R/'manifest.json').write_text(json.dumps(existing,indent=2),encoding='utf-8');print(selected+' actual-state scene export',flush=True);return
 existing=json.loads((R/'manifest.json').read_text()) if (R/'manifest.json').exists() else {}
 (R/'manifest.json').write_text(json.dumps(dict(size_px=[1440,960],CPU_only=True,views=manifest,transport_views=existing.get('transport_views',[]),visual_omissions=['opposite south wall/cabinets','cabinet-door and outlet-access keepout overlays only; still in collision checks'],source='Actual copied OEM collision hulls, full installed geometry and savedq. Rejected pictures are labelled; no generated or illustrative replacement geometry.'),indent=2),encoding='utf-8')
 print(('30' if motion else '27')+' actual-state scene exports',flush=True)
if __name__=='__main__':main()
