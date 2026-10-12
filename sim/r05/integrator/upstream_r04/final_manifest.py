"""Seal the requested artifacts and record direct visual review."""
import json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2];O=H/'results'
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as file:
  for chunk in iter(lambda:file.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def main():
 reviewed=['overview','passing','Q01','Q05','Q10','Q16','Q24','Q27']
 qa=dict(schema='r03.visual_review',directly_viewed=[n+'.png' for n in reviewed],result='readable',checks=['Overview shows both fixed lanes and full retained cell envelopes.', 'Passing image labels its separate route PASS and complete meal FAIL.', 'Q05 camera centres the active helper/food rather than the parked main tool.', 'Q16 shows the rejected soak candidate, not a successful rubbing substitute.', 'Accepted and rejected phase candidates have visible labels; phase FAIL and meal FAIL remain explicit.', 'All30 PNGs are1440x960 and decode successfully in the separate artifact audit.'],visibility_omissions=['Opposite south wall/cabinets and access-keepout overlays are hidden for visibility only; collision models retain them.'],limitations=['Collision hull/envelope render rather than photorealistic manufacturing CAD.', 'Structural rails can obscure small food contact details; exact geometric evidence is in the MJCF and per-pose records.'])
 (O/'visual_qa.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
 post=ROOT/'posts/r03/integrator.md';body=post.read_text(encoding='utf-8')
 evidence='\n\nDelivery consistency: [artifact audit](../../sim/r03/integrator/results/deliverable_audit.json), [direct visual review](../../sim/r03/integrator/results/visual_qa.json), and [SHA256 manifest](../../sim/r03/integrator/results/artifact_manifest.json). The artifact audit passes; engineering acceptance remains failed.\n'
 if 'Delivery consistency:' not in body:post.write_text(body+evidence,encoding='utf-8')
 names=['process_v3.json','best.json','phase_summary.json','motion.json','iterations.csv','costs.csv','loads.json','power.json','timeline.json','torque_envelope.json','envelope_reachability_audit.json','stroke_metrics.csv','failed_strokes.csv','installed_parts.json','installed_parts.csv','deliverable_audit.json','visual_qa.json','passing.json']
 files=[O/n for n in names]+[post,H/'models/installed_cell.xml',H/'models/passing.xml']
 files+=sorted((O/'witnesses').glob('*'))+sorted(H.glob('*.py'))+sorted((H/'renders').glob('*.png'))+sorted((H/'renders').glob('*.scene.json'))+[H/'renders/manifest.json']
 records=[dict(file=str(path.relative_to(ROOT)).replace('\\','/'),bytes=path.stat().st_size,sha256=digest(path)) for path in files]
 summary=json.loads((O/'phase_summary.json').read_text());cost=json.loads((O/'cost_summary.json').read_text());timeline=json.loads((O/'timeline.json').read_text())
 final=f"DONE integrator phases={summary['logical_passed']}/{summary['logical_total']} motion=fail arms=UR5e+xArm6 cost_cny={cost['total_cny']:.2f} prep_min={timeline['prep_min']:.2f}"
 out=dict(schema='r03.artifact_manifest',scope='Requested final deliverables, scene exports, witness records and implementation. Historical trials/sources/vendor files retained separately.',files=records,bytes_before_this_manifest=sum(x.stat().st_size for x in H.rglob('*') if x.is_file()),engineering_acceptance_pass=False,final_reply=final)
 (O/'artifact_manifest.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
 print(final);print('sealed',len(records),'files; project bytes',out['bytes_before_this_manifest'])
if __name__=='__main__':main()
