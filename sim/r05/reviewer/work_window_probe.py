"""Does a nonworking transit still inherit a food/work contact window?"""
import json,numpy as np,mujoco
import motion_audit as a
from policy_r05 import valid_window,window_pairs
rows=[]
for i in [67,86,87,95,101]:
 r=a.M['between_strokes'][i];ph,sg,key=a.mo.items[i];ch=a.mo.scene(ph,sg,i);h=sg['poses'][-1];q=np.array(a.W[key]['poses'][-1]['q']);ch.working_stroke=False;ch.contact_windows=r['planner'].get('contact_windows',[]);a.state(ch,q,h,False)
 for w in ch.contact_windows:
  if w['face'] not in {'clamped_food','wash_food','secondary_work_face'}:continue
  # Distinguish a carried cassette's own floor support from a tool touching
  # the food/work surface; only the latter needs a declared working stroke.
  if h.get(w['side'],{}).get('held') not in {'wash_pad','eye_core_spoon','peeler'}:continue
  pair_names=[w['face'],w['side']+'_held_'+w['held_parts'][0]];pairs=window_pairs(ch)
  origin_valid=valid_window(ch,w);origin_exempt=frozenset(pair_names) in pairs;retreat=None
  if origin_valid:
   sid=ch.m.site(w['side']+'_prep').id;p=ch.d.site_xpos[sid].copy();rot=ch.d.site_xmat[sid].reshape(3,3).copy();qq,ik=a.mo.ik(ch,q,{w['side']:(p+[0,0,.001],rot)});a.state(ch,qq,h,False);pp=window_pairs(ch)
   retreat=dict(IK_exact=bool(ik),valid_window=valid_window(ch,w),pair_exempt_by_window=frozenset(pair_names) in pp,tcp_retreat_mm=float(np.linalg.norm(ch.d.site_xpos[sid]-p)*1000))
  rows.append(dict(connection=i,held=h[w['side']]['held'],working_stroke=False,face=w['face'],valid_straight_origin=origin_valid,pair_exempt_by_window=origin_exempt,window_mm=w['max_window_mm'],one_mm_nonworking_retreat=retreat,reason=w['reason']))
(a.O/'work_window_probe.json').write_text(json.dumps(dict(rows=rows,scope='Failed canonical connections only. This tests a latent rule branch; it does not assert any accepted isolated path used this nonworking food/tool permission.'),indent=2));print('WORK_WINDOW_PROBE',rows,flush=True)
