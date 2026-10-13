"""R19 holding bowl as a held object (import before building a scene; edits no existing file).
Registers kitchen16.OBJ['bowl'] and wraps kitchen17.add (after cupobj's wrapper) so a cfg can place a bowl on the counter.
Bowl (ASSUMPTION): stainless steel bowl, outer diameter 190 mm (R .095), 70 mm tall, 0.35 kg, modelled as a solid
cylinder (conservative: the hollow inside is not used by the checker). Object frame = bottom centre, z up.
Grip (ASSUMPTION): a keyed grip tab welded to the rim on the robot side (-y): a flat steel strap 30 mm wide (x),
20 mm thick (z), sticking out 75 mm beyond the rim, top flush 5 mm below the rim (centre z .055). The PGC closes
across x on the tab's 30 mm faces (JAW_HELD .015, 15 mm per jaw, as the wok handle block); the keying (a slot
in the tab, a pin on one finger) fixes the bowl's yaw and is not modelled. TCP at the tab, 50 mm outside the rim;
approach horizontal toward the wall (+y), as the cup. A wrist roll about the approach axis turns the bowl about
its own front-back axis (sideways pour).
cfg keys: r19_bowl ('spot' = a bowl on the counter at r19_bowl_at, bottom centre)."""
import numpy as np
import kitchen16 as K,kitchen17 as K17
import cupobj   # noqa: F401  (chain order: kitchen17.add -> cupobj -> bowlobj)
BOWL_R,BOWL_H=.095,.070
TAB_W,TAB_T,TAB_OUT,TAB_Z=.030,.020,.075,.055   # tab width (x), thickness (z), length beyond the rim (y), centre height
GRIP_OUT=.050   # TCP: 50 mm outside the rim
BOWL_MASS=.35
SPOT2=np.array([.17,.13,.85])   # the R18 second plating spot (kitchen15 PLATE c with x .17), bottom centre on the counter
def bowl_parts():
 ty=-(BOWL_R+TAB_OUT/2-.005)   # the tab starts 5 mm inside the wall (welded)
 return [('r19_bowl_body','cylinder',[0,0,BOWL_H/2],[BOWL_R,BOWL_H/2],np.eye(3)),
  ('r19_bowl_tab','box',[0,ty,TAB_Z],[TAB_W/2,TAB_OUT/2+.0025,TAB_T/2],np.eye(3))]
K.OBJ['bowl']=dict(parts=bowl_parts(),grip=np.array([0,-(BOWL_R+GRIP_OUT),TAB_Z]),a=np.array([0,1.,0]),j=np.array([1.,0,0]),grip_part=None)
_add0=K17.add
def add(tree,world,cfg):
 _add0(tree,world,cfg)
 if cfg.get('r19_bowl')=='spot':K._add(world,'',K.OBJ['bowl']['parts'],np.eye(3),np.asarray(cfg.get('r19_bowl_at',SPOT2),float),rgba='.78 .8 .83 1')
K17.add=add
