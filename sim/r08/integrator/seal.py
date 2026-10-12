"""Artifact consistency and final source hashes; no extra numerical search."""
import hashlib,json
from scene import H,load,save
def main():
 names=['phase_summary.json','motion.json','state_sequence.json','idle.json','schedule.json','costs.csv','clearance.json','iterations.csv']
 assert all((H/'results'/n).exists() for n in names)
 phase=load('results/phase_summary.json');motion=load('results/motion.json');state=load('results/state_sequence.json')
 assert len(motion['connections'])==phase['connections_total']==10
 assert all(c['planner']['budget_s']>=60 and c['planner']['elapsed_s']>=60 for c in motion['connections'] if not c['planner']['ok'])
 assert phase['connections_executed']==state['executed_connections']==0 and phase['products_completed']==0
 assert state['initial']==state['committed'] and abs(state['total_food_kg']-.57)<1e-12
 assert load('results/regression.json')['pass_']
 audit=load('results/delivery_audit.json');assert audit['geometry_preserved'] and all(i['ok'] for i in audit['images'])
 files=[p for p in H.rglob('*') if p.is_file()]
 audit['total_bytes']=sum(p.stat().st_size for p in files);audit['under_3GB']=audit['total_bytes']<3_000_000_000
 audit['hashes']={str(p.relative_to(H)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.suffix in ('.py','.xml') and 'assets' not in p.parts}
 audit['final_artifact_consistency']=True
 save('results/delivery_audit.json',audit)
 print('Artifact consistency passed; bytes',audit['total_bytes'],flush=True)
if __name__=='__main__':main()
