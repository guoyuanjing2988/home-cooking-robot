"""R07 unchanged-input regression and adversarial state/contact checks."""
import copy,hashlib,xml.etree.ElementTree as E
import numpy as np,mujoco
from scene import H,ROOT,load,save,build,variants,targets
from checker import Checker,reference
from state import regression as state_regression
def main():
 old=ROOT/'sim/r07/integrator';admission=__import__('json').loads((old/'results/fresh_admission.json').read_text());rows=[]
 for index in [0,9,54,58]:
  source=old/f'models/L101_stroke_{index}.xml';tree=E.parse(source)
  for mesh in tree.findall('.//mesh'):mesh.set('file',str(H/'assets'/__import__('pathlib').Path(mesh.get('file')).name))
  ch=Checker(tree);saved=admission['rows'][index]
  for k,po in enumerate(saved['reference']['poses']):
   result=ch.check(np.array(po['q']));expected=not po['forbidden'] and po['public_ranges_ok']
   rows.append(dict(index=index,pose=k,expected_geometry=expected,reproduced_geometry=not result['hits'] and result['ranges'],match=expected==(not result['hits'] and result['ranges']),result=result,input_xml_sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
 # Negative cases use exact compiled object and support identities, not names alone.
 cfg=variants()[7];tree,meta=build(cfg,'holder');ch=Checker(tree,meta);t=next(t for t in targets(cfg,meta) if t['name']=='mandoline_work')
 R=reference.rotation([0,0,-1],[0,1,0]);ch.set_working(t['points'][0],t['points'][-1],R)
 sid=ch.m.site('R_prep').id
 # A local capability unit probe sets only the observed TCP query frame. It is
 # not a robot pose or path, and is explicitly never used as execution evidence.
 ch.d.site_xpos[sid]=t['points'][0];ch.d.site_xmat[sid]=R.ravel()
 original=copy.deepcopy(ch.windows);checks={}
 checks['genuine_working_capability']=len(ch.permissions('working'))==2
 checks['nonworking_path_rejects_working_permission']=not ch.permissions('transfer')
 for label,key,value in [('wrong_object','object','carrot'),('wrong_support','support','wash_basket'),('invented_part','parts',['imaginary']),('wrong_kind','kind','anything'),('oversized_working_stroke','length_m',.25),('forged_origin','origin',[9,9,9])]:
  ch.windows=copy.deepcopy(original)
  for w in ch.windows:w[key]=value
  checks[label]=not ch.permissions('working')
 ch.windows=copy.deepcopy(original);g=ch.gnames.index('mandoline_deck');ch.d.geom_xpos[g,0]+=.001;checks['stale_support_geometry']=not ch.permissions('working')
 checks.update(state_regression())
 # Source gates and golden profile dimensions, not a permissive reimplementation.
 checks['reference_sha_unchanged']=hashlib.sha256((ROOT/'sim/r05/integrator/reference.py').read_bytes()).hexdigest()=='46e9002b222cf92970cfc5b30c10fbe23eed06470b8714fc946ffdd44d0f5681'
 checks['golden_holder_radius_65mm']=ch.m.geom_size[ch.gnames.index('R_held_holder'),0]==.065
 hg=ch.gnames.index('R_held_holder');fg=ch.gnames.index('R_finger_minus');saved_grasp=copy.deepcopy(ch.grasp_registry)
 checks['real_grasp_identity']=ch.grasp_allowed(hg,fg)
 for label,key,value in [('grasp_wrong_object','object','tomato'),('grasp_wrong_support','support','wash_basket'),('grasp_forged_part_frame','identity',None),('grasp_forged_finger','fingers',('R_gripper_palm',))]:
  ch.grasp_registry=copy.deepcopy(saved_grasp);ch.grasp_registry['R_held_holder'][key]=value;checks[label]=not ch.grasp_allowed(hg,fg)
 ch.grasp_registry=copy.deepcopy(saved_grasp);ch.m.geom_pos[hg,0]+=.001;checks['grasp_stale_geometry']=not ch.grasp_allowed(hg,fg)
 save('results/regression.json',dict(pass_=all(x['match'] for x in rows) and all(checks.values()),r07_unchanged_inputs=rows,negative_probes=checks,scope='Eight geometry verdicts from four unchanged R07 templates. Contact probes are capabilities unit tests, not kinematic evidence.'))
 print('regression',[(r['index'],r['match']) for r in rows],checks,flush=True)
if __name__=='__main__':main()
