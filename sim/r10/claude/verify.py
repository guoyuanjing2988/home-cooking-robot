"""State-level adversarial regression; synthetic probes earn zero execution."""
import copy,hashlib
import numpy as np,mujoco
from scene import build,variants,save,ROOT,H,load
from checker import Checker,reference
from state import World
def main():
 cfg=variants()[-1];cfg['mount_tilt_deg']=20;tests={}
 t,m=build(cfg,'carrot');ch=Checker(t,m);g=ch.gnames.index('R_held_carrot');f=ch.gnames.index('R_finger_minus')
 tests['canonical_grasp']=ch.grasp_allowed(g,f)
 ch.m.geom_quat[g]=[2**-.5,0,2**-.5,0]
 tests['rotated_food_denied']=not ch.grasp_allowed(g,f)
 q=ch.m.qpos0.copy();q[:3]=[0,-.4,0]
 tests['rotated_food_full_state_denied']=not ch.check(q)['ok'] and not ch.last['identity_ok']
 t,m=build(cfg,'catch_tray');t.find(".//geom[@name='R_held_tray_floor']").set('size','.3 .3 .3')
 try:Checker(t,m);tests['forged_600mm_tray_denied']=False
 except ValueError:tests['forged_600mm_tray_denied']=True
 t,m=build(cfg,'catch_tray');t.find(".//geom[@name='R_held_tray_floor']").set('quat','.707106781187 0 .707106781187 0')
 try:Checker(t,m);tests['rotated_tray_constructor_denied']=False
 except ValueError:tests['rotated_tray_constructor_denied']=True
 w=World();w.attach('carrot',w.objects['carrot']['pos']);before=w.snapshot()
 try:w.commit_path('carrot',{'ok':True,'path':[[0]]},[[9,9,9]]);tests['forged_commit_denied']=False
 except ValueError:tests['forged_commit_denied']=w.snapshot()==before
 t,m=build(w.config,'carrot');cc=Checker(t,m)
 for label,path in [('wrong_dimensions',[[0],[0]]),('nonfinite',[[float('nan')]*cc.m.nq]*2)]:
  try:w.commit_path('carrot',{'ok':True,'path':path},checker=cc,start_q=[0]*cc.m.nq);tests[label]=False
  except ValueError:tests[label]=w.snapshot()==before
 w=World();w.objects['carrot'].update(pos=np.mean(w.regions['mandoline']['input'],axis=0).tolist(),support='mandoline');before=w.snapshot()
 try:w.transform('carrot','peeled','mandoline',w.regions['mandoline']['input'],1);tests['incompatible_station_denied']=False
 except ValueError:tests['incompatible_station_denied']=w.snapshot()==before
 try:w.transform('carrot','slices','mandoline',w.regions['mandoline']['input'],1,.9);tests['overlap_scrap_denied']=False
 except ValueError:tests['overlap_scrap_denied']=w.snapshot()==before
 t,m=build(cfg,'holder');hc=Checker(t,m)
 from scene import targets
 target=next(x for x in targets(cfg,m) if x['name']=='mandoline_work');R=reference.rotation([0,0,-1],[0,1,0]);hc.configure_target(target,R)
 tests['windows_at_most50mm']=all(x['length_m']<=.05+1e-12 and x['kind']=='working_stroke' for x in hc.windows)
 tests['no_work_on_transfer']=not hc.permissions('transfer')
 tests['binding_constants']=(reference.PAD,reference.MU,reference.SF,reference.KEY_FORCE_N,reference.KEY_MOMENT_NM)==(0,.5,1.5,150,15)
 tests['reference_hash']=hashlib.sha256((ROOT/'sim/r05/integrator/reference.py').read_bytes()).hexdigest()=='46e9002b222cf92970cfc5b30c10fbe23eed06470b8714fc946ffdd44d0f5681'
 if (H/'results/statics/0_1.json').exists():
  # Synthetic setup only: put the state in an already-attached admitted carry
  # pose, then prove a replayed hold can commit and an unchecked jump cannot.
  w=World();tree,meta=build(w.config,'carrot');cc=Checker(tree,meta)
  accepted=[r for r in load('results/statics/0_1.json')['rows'] if r['status']=='ok']
  if accepted:
   q=np.array(accepted[0]['q']);cc.d.qpos[:]=q;mujoco.mj_forward(cc.m,cc.d)
   w.objects['carrot'].update(pos=cc.d.site_xpos[cc.m.site('R_prep').id].tolist(),attached=True,support='robot')
   w.commit_path('carrot',dict(ok=True,path=[q.tolist(),q.tolist()]),checker=cc,start_q=q)
   tests['checked_hold_commit_synthetic']=w.executed_connections==1
   before=w.snapshot();jump=q.copy();jump[0]+=.1
   try:w.commit_path('carrot',dict(ok=True,path=[q.tolist(),jump.tolist()]),checker=cc,start_q=q);tests['unchecked_jump_transactional']=False
   except ValueError:tests['unchecked_jump_transactional']=before==w.snapshot()
   try:w.commit_path('carrot',dict(ok=True,path=[jump.tolist(),jump.tolist()]),checker=cc,start_q=jump);tests['stale_start_transactional']=False
   except ValueError:tests['stale_start_transactional']=before==w.snapshot()
 save('results/regression.json',dict(tests=tests,all_pass=all(tests.values()),scope='synthetic tests, not execution'))
 print(tests);assert all(tests.values())
if __name__=='__main__':main()
