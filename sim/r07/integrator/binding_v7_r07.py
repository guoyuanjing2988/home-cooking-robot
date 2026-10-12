"""Named finger/object grasp windows and geometric attachment transactions."""
import numpy as np,mujoco,copy,math
from scipy.spatial.transform import Rotation
import persistent_v7_r07 as p
from motion_v7_r07 import Planner as Base,continuation_ik

GRASP_PARTS={'root_food':['food'],'wash_pad':['pad_handle'],'eye_core_spoon':['spoon_handle'],'food_cup':['cup_key'],'cut_cassette':['cassette_handle'],'colander':['colander_key'],'carried_bowl':['key']}

def grasp_window(world,name):
 o=world.objects[name];t=o['pose'];prefix='persistent_'+name.replace(':','_')+'_'
 return dict(kind='grasp_release_support',object_id=name,support_id=prefix+'grasp_faces',tcp_origin_m=t[:3,3].tolist(),tcp_rotation=t[:3,:3].tolist(),normal=(-t[:3,0]).tolist(),max_window_mm=50,parts=[prefix+x for x in GRASP_PARTS[o['h']['held']]],fingers=['R_finger_minus','R_finger_plus'],closing_axis=t[:3,1].tolist())

def admitted_pairs(ch,w):
 if not isinstance(w,dict) or w.get('kind')!='grasp_release_support':return set()
 # Permissions are capabilities of this compiled world, not caller supplied
 # names. The registry is constructed from full live objects in World.build.
 registry=getattr(ch,'registered_grasp_faces',{})
 trusted=registry.get(w.get('object_id'))
 if trusted is None:return set()
 expected=trusted['window']
 if set(w)!=set(expected):return set()
 for key,value in expected.items():
  if isinstance(value,list) and value and not isinstance(value[0],str):
   try:
    a,b=np.asarray(w[key],dtype=float),np.asarray(value,dtype=float)
    if a.shape!=b.shape or not np.all(np.isfinite(a)) or np.max(abs(a-b))>1e-9:return set()
   except (ValueError,TypeError):return set()
  elif w[key]!=value:return set()
 # Reject stale registries following any unregistered model/object movement.
 for name,frame in trusted['part_frames'].items():
  if name not in ch.gnames:return set()
  gi=ch.gnames.index(name)
  if np.max(abs(ch.d.geom_xpos[gi]-frame['pos']))>1e-8 or np.max(abs(ch.d.geom_xmat[gi]-frame['rotation']))>1e-8:return set()
 t=p.fk(ch,ch.d.qpos);delta=t[:3,3]-w['tcp_origin_m'];n=np.array(w['normal']);axial=float(delta@n)
 if np.linalg.norm(delta-axial*n)>.00002 or not(-.00002<=axial<=.05000001) or np.max(abs(t[:3,:3]-w['tcp_rotation']))>.0002:return set()
 pairs=set()
 for a in w['fingers']:
  for b in w['parts']:
   if a not in ch.gnames or b not in ch.gnames:continue
   ia,ib=ch.gnames.index(a),ch.gnames.index(b);contacts=[c for c in ch.d.contact[:ch.d.ncon] if set(map(int,c.geom))=={ia,ib} and c.dist<=0]
   # Only opposite finite jaw faces: no hard penetration and no accidental
   # finger-tip/edge collision becomes an intended grasp contact.
   if any(c.dist < -.00001 or abs(np.array(c.frame[:3])@w['closing_axis'])<.85 for c in contacts):continue
   pairs.add(frozenset((a,b)))
 return pairs

class Planner(Base):
 def state(self,q,hands=None):
  stages=getattr(self.ch,'staging_poses',[])
  if stages and self.states%128==0:
   selected=(self.states//128)%len(stages);p.v.s.PARK=np.array(stages[selected]['q']).copy()
   if not hasattr(self,'staging_bias_updates'):self.staging_bias_updates=[]
   self.staging_bias_updates.append(dict(state_call=self.states,stage=stages[selected]['name']))
  result=super().state(q,hands)
  if result or not getattr(self.ch,'pending_grasp',None):return result
  allowed=admitted_pairs(self.ch,self.ch.pending_grasp)
  hits,_,_=p.v.f.contacts(self.ch,q);left=[]
  for hit in hits:
   if frozenset(hit['pair']) in allowed:continue
   if not hit.get('reason') and hit.get('real_gap_mm',0)>0:
    ia,ib=(self.ch.gnames.index(n) for n in hit['pair']);gap=self.ch.bounds.pair(ia,ib)
    if gap['lower_m']>=hit['required_gap_mm']/1000-1e-6:continue
   left.append(hit)
  self.last=None if not left else dict(q=np.array(q).tolist(),blockers=left[:8]);return not left
 def result(self,*args,**kwargs):
  out=super().result(*args,**kwargs);out['staging_bias_updates']=getattr(self,'staging_bias_updates',[]);out['staging_candidates']=getattr(self.ch,'staging_poses',[]);return out

def jaw_path(ch,q,target_opening,hands):
 pl=Planner(ch,hands,seconds=65);b=np.array(q).copy()
 for side in ('minus','plus'):b[ch.qa['R_jaw_'+side]]=target_opening/2
 pl.restarts=1;ok=pl.edge(q,b,hands,hands);window=getattr(ch,'pending_grasp',None) or {};return b,dict(kind='grasp_release_support' if window else 'free_space_jaw_motion',object_id=window.get('object_id'),support_id=window.get('support_id'),contact_permission_used=bool(window),pass_=ok,q_start=np.array(q).tolist(),q_end=b.tolist(),states_checked=pl.states,max_point_step_mm=pl.max_step*1000,blocker=pl.last)

def exact_goal(ch,q,world_transform):
 return continuation_ik(ch,q,{'R':(world_transform[:3,3],world_transform[:3,:3])})

def support_hand(world,name,h):
 h=copy.deepcopy(h);face=world.objects[name]['support'];parts=[g.get('name') for g in world.objects[name]['body'].findall('.//geom')]
 p.v.rt.SUPPORT_REGISTRY.setdefault(name,set()).add(face)
 h['contacts']=[dict(kind='grasp_release_support',object_id=name,support_id=face,face=face,held_parts=parts,reason='Own registered support; finite named top face during straight insertion/removal only')]
 return h
