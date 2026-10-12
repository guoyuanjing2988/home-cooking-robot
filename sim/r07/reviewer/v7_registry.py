"""Reconstruct live grasp capabilities from state identities, not saved permissions."""
from v7_common import *

def restore_registry(ch, state):
    import persistent_v7_r07 as p
    from binding_v7_r07 import grasp_window
    world=p.World()
    for name,o in world.objects.items():
        if name in state['objects']:
            st=state['objects'][name]
            o.update(pose=np.array(st['pose']),support=st['support'],mass=st['mass_kg'])
    ch.d.qpos[:]=ch.m.qpos0;mujoco.mj_forward(ch.m,ch.d)
    ch.registered_grasp_faces={};checks=[]
    for name,o in world.objects.items():
        if name==state['attached'] or name not in state['objects']:continue
        win=grasp_window(world,name)
        if not all(part in ch.gnames for part in win['parts']):continue
        local=p.local_geoms(o['body']);frames={};ok=True
        prefix='persistent_'+name.replace(':','_')+'_'
        for part in win['parts']:
            g=ch.gnames.index(part);expected=o['pose']@local[part[len(prefix):]]['transform']
            err=max(np.max(abs(expected[:3,3]-ch.d.geom_xpos[g])),np.max(abs(expected[:3,:3].ravel()-ch.d.geom_xmat[g])))
            ok &= err<1e-7
            frames[part]=dict(pos=ch.d.geom_xpos[g].copy(),rotation=ch.d.geom_xmat[g].copy())
            checks.append(dict(object=name,part=part,frame_error=float(err),pass_=bool(err<1e-7)))
        if ok:ch.registered_grasp_faces[name]=dict(window=win,part_frames=frames,actual_support=o['support'])
    return checks
