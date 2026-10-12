"""Delivery inventory, resource and semantic checks; no numerical pass invention."""
import ast,csv,hashlib,json
from PIL import Image
from scene import H,ROOT,load,save,build
def main():
 required=['hardware.json','phase_summary.json','motion.json','state_sequence.json','stability.json','idle.json','schedule.json','clearance.json','iterations.csv','costs.csv']
 tests={n:(H/'results'/n).exists() for n in required}
 tests['post']=(ROOT/'posts/r09/integrator.md').exists()
 for p in H.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
 phase=load('results/phase_summary.json');state=load('results/state_sequence.json');motion=load('results/motion.json')
 tests['no_unchecked_execution']=state['executed_connections']==0 and motion['connections_pass']==0 and phase['products_completed']==0
 tests['food_conserved']=abs(state['total_mass_kg']-.57)<1e-12
 tests['iterations_ge8']=len(list((H/'results/iterations').glob('M??.json')))>=8
 tests['starts_all_ge96']=all(load(f'results/statics/{i}_{j}.json')['starts']>=96 for i in range(11) for j in [0,1])
 tests['reference_unchanged']=hashlib.sha256((ROOT/'sim/r05/integrator/reference.py').read_bytes()).hexdigest()=='46e9002b222cf92970cfc5b30c10fbe23eed06470b8714fc946ffdd44d0f5681'
 tests['all_regressions']=load('results/regression.json')['all_pass']
 tests['final_replay']=all(load(f'results/replay/{i}.json')['all_pass'] for i in range(11))
 tests['map_replay']=load('results/replay/maps.json')['all_pass']
 tests['route_replay']=load('results/replay/routes.json')['all_pass']
 tests['all_saved_tips_pass']=load('results/stability.json')['pass_for_saved_admitted_samples']
 tests['all_sub2_explained']=all(x.get('written_reason') for x in load('results/clearance.json')['under2mm'])
 tests['idle_really_folded']=load('results/park_search.json').get('folded',False)
 idle=load('results/idle.json');park=load('assets/park_mobile.json')
 tests['idle_matches_final_park']=idle['park_q']==park['q'] and abs(idle['park_q'][5])>=1.6
 # Explicit provenance: interstroke searches used the narrower-footprint safe
 # carry candidate, not the later corrected folded IDLE snapshot. Both are
 # allowed carry concepts; neither earns an execution claim.
 for i in range(10):
  p=f'results/connections/{i}.json';r=load(p)
  r['safe_carry_pose_reference']='results/pilot/upright_carry_search.json'
  r['carry_note']='Interstroke safe carry was within cart envelope; this is distinct from the later folded idle pose. Stages named fold/unfold mean enter/leave carry. All stages failed.'
  tests[f'connection{i}_budgets']=all(r['planner'][k].get('budget_s',0)>=60 for k in ['fold','base_move','unfold'])
  save(p,r)
 images=[]
 for p in (H/'renders').glob('*.png'):
  im=Image.open(p);images.append(dict(file=str(p.relative_to(H)),size=list(im.size)));tests[p.name]=max(im.size)<=1600
 resources=[load(str(p.relative_to(H))) for p in (H/'audit').glob('*.resource.json')]
 tests['bounded_memory']=all(r['peak_MiB']<1900 for r in resources)
 tests['bounded_timeouts']=all(0<r['timeout_s']<1200 for r in resources)
 costs=list(csv.DictReader((H/'results/costs.csv').open(encoding='utf-8')))
 tests['one_reserve']=sum('reserve' in r['item'].lower() for r in costs)==1
 tests['one_safety_package']=sum('safety package' in r['item'].lower() for r in costs)==1
 total=sum(p.stat().st_size for p in H.rglob('*') if p.is_file());tests['under3GB']=total<3*1024**3
 # Refresh selected model after source compaction; its geometry stays unchanged.
 cfg=load('results/selected.json')['config'];tree,meta=build(cfg);tree.write(H/'models/selected.xml',encoding='unicode')
 save('results/seal.json',dict(tests=tests,all_pass=all(tests.values()),output_bytes=total,images=images,resource_peak_MiB=max(r['peak_MiB'] for r in resources),largest_timeout_s=max(r['timeout_s'] for r in resources),no_git_repository=True,temporary_pdf_dependency_retained='Optional deletion blocked by automatic approval review; retained under audit/pdfdeps, within output budget.',python_source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in H.glob('*.py')}))
 print(json.dumps(dict(all_pass=all(tests.values()),failed=[n for n,v in tests.items() if not v],output_MB=total/1e6,peak_MiB=max(r['peak_MiB'] for r in resources))))
 assert all(tests.values())
if __name__=='__main__':main()
