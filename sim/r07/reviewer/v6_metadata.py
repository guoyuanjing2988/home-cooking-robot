from pathlib import Path
import json,hashlib,collections,ast
H=Path(__file__).resolve().parent;O=H/'results_v6';I=H.parent/'integrator';R=H.parents[2]
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
audit=load(I/'results/delivery_audit.json');edges=[]
for r in audit['slot_intervals']:
 edges.append((r['acquired_unix'],1));edges.append((r['released_unix'],-1))
active=peak=0
for _,delta in sorted(edges):active+=delta;peak=max(peak,active)
src=[]
for n in ['DECISIONS.md','posts/r05/integrator.md','posts/r05/reviewer.md','posts/r04/reviewer.md','posts/r07/integrator.md']+[f'posts/r07/reviewer_v{i}.md' for i in range(1,6)]:
 p=R/n;src.append(dict(file=n,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
rows=[load(p) for p in (I/'results/connections_v6/L84').glob('*.json')];bad=[];windows=[]
for row in rows:
 for leg in row['legs']:
  w=leg['grasp_window']
  if not w:continue
  prefix='persistent_'+w['object_id'].replace(':','_')+'_'
  own=w['kind']=='grasp_release_support' and w['support_id']==prefix+'grasp_faces' and all(part.startswith(prefix) for part in w['parts']) and w['max_window_mm']<=50 and w['object_id'] in leg['state']['objects']
  windows.append(dict(connection=row['connection'],own_identity_matches=own,window=w))
  if not own:bad.append(row['connection'])
# Safety logic replay in reviewer namespace; remove its top-level integrator output.
s=(I/'safety_v6_r07.py').read_text();s=s[:s.index("(H/'results/safety_v6.json')")];space={'__file__':str(I/'safety_v6_r07.py')};exec(compile(s,'reviewer_safety_copy','exec'),space)
result=dict(source_hashes=src,integrator_worker_peak_reconstructed=peak,integrator_slot_count=len(audit['slot_intervals']),integrator_resource_claim=audit['resource_compliance_pass'],grasp_window_records=windows,actual_saved_identity_mismatches=bad,safety_logic=space['out'],public_source_review=[dict(url='https://www.breville.com/en-au/product/bfp610',finding='Current labelled WxDxH=39.5x19.7x23cm,120mm chute; retained395x295x395mm exterior is conservative but revision/axes/cavity unqualified.'),dict(url='https://assets.breville.com/BFP610/BFP610_ANZ_WEB_IB_A23_LR.pdf',finding='0.3-5mm slicing; batch bowl, lid/large-pusher interlock, supplied pusher, stop/unplug for disassembly, no unattended use or external switching timer; exact batch duration absent.'),dict(url='https://www.actuonix.com/p16-200-256-12-p',finding='200mm stroke,247mm closed holes,12V,300N maximum,500N backdrive,150N efficiency load.'),dict(url='https://www.actuonix.com/assets/images/datasheets/ActuonixP16Datasheet.pdf',finding='150N at3.4mm/s,20percent duty,4N side load for200mm version,1000mA stall,IP54; automatic position control allowed.'),dict(url='https://www.universal-robots.com/manuals/EN/HTML/SW5_23/Content/prod-usr-man/complianceUR5e/H_g5_sections/appendix_g5/tech_spec_sheet.htm',finding='5kg,850mm,151mm footprint,elbow +/-160deg,570W max,IP54. Archived full solids kept; physical revision needs freeze.'),dict(url='https://www.dfrobot.com/product-1530.html',finding='FIT0498 normally closed12V/0.42A,IP00; not waterproof electronics.'),dict(url='https://www.grohe-mena.com/en_cy/eurocube-bath-spout-13303000.html',finding='OEM search result projection170mm; direct page403. Prior manufacturer drawing retained in submission.'),dict(file='sim/r03/reviewer/audit/ur_payload_91.png',finding='Visually inspected archived manual graph: total5kg through350mm CoG offset including EOAT; dimensions are not an OEM folded envelope.')],decisions=['Current worker cap is4; historic v5 cap incident is not a new v6 finding.','Use L84-L89 only for corrected motion scope; L74-L83 excluded by submitted correction record.','Food quality is an authorized declared assumption; unexecuted full mechanical interfaces remain failures.','Use14 complete internal replays and every supplied connection trajectory, plus rejection diagnostics. Do not run fresh random planners for a read-only saved-witness review.','Retain one complete principal arm,3kg service payload plus1.2kg EOAT,all gaps and forces. No upstream edits or physical tests.'])
(O/'metadata.json').write_text(json.dumps(result,indent=2));print('METADATA',peak,len(windows),bad,space['out']['pass_'])
