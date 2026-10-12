"""R17 sink rinse (design proposal, all sizes estimated), added on top of kitchen16 when cfg['r17']
is set. The user decided (2026-10-12): rinse the wok at the sink ("不能把锅拿到水池去刷吗"), the
arm opens the faucet first and leaves it running ("你可以先开水龙头呀，浪费点水无所谓"), no faucet
replacement and no water pipe over the hob.
 - FAUCET: a deck-mounted single-lever faucet like the user's (photo inputs/user_kitchen/sink_leg.jpg:
   a tall square chrome body behind the left bowl): a 45 mm square column at (FX, FY) from the deck
   to 1.13 m, a square spout forward to y 0.37 (outlet at its front end, 1.10 m), and a side lever
   on the column's right face, pivot 1.04 m, 0.10 m long, pointing at the robot when closed; lifting
   its tip LEVER_OPEN deg opens the water. The lever end carries a clip-on keyed block (30 mm, like
   the other R16 grip blocks) on a short bracket BLOCK_OUT to the outside. The PGC takes it from the
   right (approach -x, along the lever's pivot axis), so turning the lever is mostly a wrist roll and
   the gripper body stays right of the faucet. Taken from the front, the 54 mm wide R12 fingers
   (block on the lever itself) and then the PGC housing (lever lifted) came within 5 mm of the
   spout (r17chain lever, runs 1-2). The R07 wall spout
   (scene.py faucet_v3_*, no handle) is removed, and so is the R07 prep colander (wash_basket):
   during cooking it is out of the sink (a 34 cm wok and the 24 cm colander do not both fit in the
   sim's single 0.6 m basin; the user's sink has two bowls).
 - The wok rinse place: the wok frame origin (inner bottom) at SINK_WOK, under the outlet, its
   handle over the basin (grip block 0.235 m left of the wok axis).
Changes to R15 parts near the wok (the wok carry to the sink, r17chain wok runs 1-4):
 - the handle bracket is REMOVED: its anti-rotation job goes to a keyed slot in the cooker's bowl
   rim that takes the handle root (not modeled: it lies below the lifted wok's path). With the
   bracket (top 1.0 m, under the handle) the wok could leave the cooker only lifted 9 cm (the top
   grasp's wrist then met the upper-cabinet doors) or slid 15 cm toward the robot first (the arm
   folded onto its own base), and the open fingers came within 5 mm of it (r17chain wok runs 1-8);
 - the pour-drum holder at the right rim swings its drum away (up under the hood) except while
   stirring (cfg r15_drum_taken in the R17 runs): lifted 4 cm the wok rim was 3 mm under the drum,
   and a holder raised 60 mm (DRUM_C, runs 7-14) put the drum in the arm's way when the lid comes off
   the pot (r17chain lid). The swing is a design assumption, not modeled.
Objects added to kitchen16.OBJ (same conventions: parts in the object frame, grasp point, approach,
jaw axis, grip_part left out when held):
 wok   = kitchen15's wok frame (origin WOK0 on the cooker, world axes), top grasp of its keyed block
 lever = lever frame (origin at the pivot, closed = world axes), grasp at the end block from the right
cfg keys: r17 (bool), r17_lever (lever angle deg, default 0 = closed; None = the lever is held).
held_cfg(obj, sign) gives the scene cfg for a held object (the wok is held through kitchen15's
r15_wok_held, the rest through kitchen16's r16_held)."""
import numpy as np
from scene import box,fmt
import kitchen15 as K15,kitchen16 as K
FX,FY=-.40,.555
COLUMN=dict(x=(FX-.0225,FX+.0225),y=(FY-.0225,FY+.0225),z=(.85,1.13))
SPOUT=dict(x=(FX-.0175,FX+.0175),y=(.37,FY),z=(1.10,1.13))   # 0.185 m reach
PIVOT=np.array([FX+.0475,FY,1.04]);LEVER_L=.10;LEVER_OPEN=30.;BLOCK_OUT=.025
DRUM_C=[1.005,.17,1.165]   # raised holder of runs 7-14 (superseded by the swing-away drum)
SINK_WOK=np.array([FX,.25,.92])   # wok frame origin (inner bottom) for the rinse, under the outlet; its back rim stays 3.5 cm in front of the lever (at y .30 it hit the lever, r17chain wok run 1); at .80-.83 the gripper, turned level by the 90° tip toward the robot, came within 5 mm of the sink's front rim (runs 2-3)
# R17 counter end: the spider lies where the R16 spatula was, 6 cm further back, handle toward the
# robot as in use; the spatula and the ladle are NOT on this rest (R17_TOOLS_OFF). Tried (r17chain):
#  - spider at the R16 spot (1.64, .46) behind the ladle: no arm path between the rest and the pot (R16);
#  - spider at the front (1.60, .14): spider OK, but its grip block, 14 cm past the counter edge, met
#    the wrist when the lid went into the rack (and at 1.54-1.56 too);
#  - spider at (1.52, .30): its own rest-to-pot path failed; at (1.52, .36) the spider and the lid pass.
K.TOOL_XY['spider']=(1.52,.36)
R17_TOOLS_OFF={'ladle':None,'spatula':None}   # the spatula's place near the wok and the soup serving are open
def lever_parts():
 # bar from 30 mm off the pivot (the hub stays on the column) to the end block
 return [('r17_lever_bar','box',[0,-(.03+LEVER_L-.015)/2,0],[.004,(LEVER_L-.015-.03)/2,.006],np.eye(3)),
  ('r17_lever_bracket','box',[BLOCK_OUT/2,-(LEVER_L-.0125),0],[BLOCK_OUT/2,.004,.006],np.eye(3)),
  ('r17_lever_tip','box',[BLOCK_OUT,-(LEVER_L-.0125),0],[.008,.0125,.015],np.eye(3))]
def _objs():
 wp=K15.wok_parts(offset=0.)+K15.handle_parts()
 K.OBJ['wok']=dict(parts=wp,grip=K15.GRIP['c']-K15.WOK0,a=np.array([0,0,-1.]),j=np.array([0,1.,0]),grip_part='r15_wok_grip')
 K.OBJ['lever']=dict(parts=lever_parts(),grip=np.array([BLOCK_OUT,-(LEVER_L-.0125),0]),a=np.array([-1.,0,0]),j=np.array([0,0,1.]),grip_part='r17_lever_tip')
_objs()
import spatula15 as SP
def _spatula_blade():
 """The R15 spatula as an object in its BLADE frame (R15 stir keys give blade poses), grasped at its
 keyed block 0.45 m along blade + handle, approach along the handle toward the blade, jaws across."""
 b=SP.grip_point(.45);parts=[(f'r18_spat_blade{k}','box',c,h,np.eye(3)) for k,(c,h) in enumerate(SP.blade_parts())]
 parts.append(('r18_spat_handle','capsule',np.r_[[0,SP.BH,0],b-SP.HD*.03],[.008],None))
 K.OBJ['spatula_b']=dict(parts=parts,grip=b,a=-SP.HD,j=np.array([1.,0,0]),grip_part=None)
_spatula_blade()
def spatula_rest_blade():
 """Blade-frame pose of the spatula lying on its rest (kitchen16.pose('spatula','rest') is the tool frame
 of the jaw +1 grasp: tool = blade @ Rt(+1))."""
 from checker import reference
 Rt=reference.rotation(-SP.HD,[1,0,0]);Rtool,pt=K.pose('spatula','rest');Rb=Rtool@Rt.T;return Rb,pt-Rb@K.OBJ['spatula_b']['grip']
def set_wok_tilt(deg):
 """Wok grasp leaned deg toward the robot about the handle (x) axis: the gripper body goes toward
 the robot and away from the upper-cabinet doors; the keyed block's jaw faces are tilted the same."""
 b=np.radians(deg);K.OBJ['wok']['a']=np.array([0,np.sin(b),-np.cos(b)]);K.OBJ['wok']['j']=np.array([0,np.cos(b),np.sin(b)])
def set_wok_end_grasp():
 """End-on grasp: the gripper lies along the handle, approaching from the left (+x), jaws closing
 top / bottom on the keyed block (R15 GRASP=end). The wrist stays at the grip's height, far below the
 upper cabinets, and tipping the wok about the handle is a roll of the last wrist joint. With the
 top grasp the wrist sits ~0.3 m above the grip and met the cabinet doors (r17chain wok runs 1-7)."""
 K.OBJ['wok']['a']=np.array([1.,0,0]);K.OBJ['wok']['j']=np.array([0,0,1.])
def lever_pose(deg):
 """Lever pose (R, pivot) with the end lifted deg (rotation about the pivot's x axis)."""
 return K.Rx(-deg),PIVOT.copy()
def held_cfg(obj,sign):
 T=K.T_tool_obj(obj,sign).tolist()
 if obj=='spatula_b':return dict(r16_held=dict(obj=obj,T_tool_obj=T),r16_tools={'ladle':None,'spatula':None})   # off its rest while held
 return dict(r15_wok_held=dict(T_tool_wok=T)) if obj=='wok' else dict(r16_held=dict(obj=obj,T_tool_obj=T))
def add(tree,world,cfg):
 for g in list(world.iter('geom')):
  if g.get('name') in ('faucet_v3_fixed_spout_full_envelope','faucet_v3_wall_bracket_mating','faucet_v3_concealed_thread_and_connector'):
   for par in world.iter():
    if g in list(par):par.remove(g);break
 for bb in list(world.findall('body')):   # cooking-time layout: the prep colander is out of the sink
  if bb.get('name')=='wash_basket':world.remove(bb)
 for g in list(world.iter('geom')):
  if g.get('name')=='r15_handle_bracket':
   for par in world.iter():
    if g in list(par):par.remove(g);break
 b=lambda n,x,y,z,c=(.75,.77,.8,1):box(world,n,[(x[0]+x[1])/2,(y[0]+y[1])/2,(z[0]+z[1])/2],[x[1]-x[0],y[1]-y[0],z[1]-z[0]],c)
 b('r17_faucet_column',COLUMN['x'],COLUMN['y'],COLUMN['z']);b('r17_faucet_spout',SPOUT['x'],SPOUT['y'],SPOUT['z'])
 b('r17_lever_hub',(COLUMN['x'][1],PIVOT[0]+.008),(FY-.012,FY+.012),(PIVOT[2]-.012,PIVOT[2]+.012))
 if cfg.get('r17_plate2') is not None:   # a second plating spot (R18)
  from scene import fmt as _f;import xml.etree.ElementTree as _E
  pc=np.asarray(cfg['r17_plate2'],float);_E.SubElement(world,'geom',name='r17_plate2',type='cylinder',pos=_f(pc+[0,0,K15.PLATE['h']/2]),size=_f([K15.PLATE['r'],K15.PLATE['h']/2]),rgba='.95 .95 .93 1',contype='1',conaffinity='2',mass='.000001')
 held=(cfg.get('r16_held') or {}).get('obj')
 if held!='lever' and cfg.get('r17_lever',0.) is not None:
  R,p=lever_pose(float(cfg.get('r17_lever',0.)));K._add(world,'',K.OBJ['lever']['parts'],R,p,rgba='.75 .77 .8 1')
