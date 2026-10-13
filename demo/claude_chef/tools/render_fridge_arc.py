"""Render the R14 checked fridge-door arc (results/r14/fridge_arc_path.json) with the arm, one frame per keyframe.
Run from the sim dir: python render_fridge_arc.py out.mp4"""
import os, sys, json, subprocess, tempfile
sys.path.insert(0, os.getcwd())
import numpy as np, mujoco
from PIL import Image, ImageDraw, ImageFont
import chain, kitchen14 as K
from scene import build
from dress import dress, HIDE
out = sys.argv[1]
r = json.load(open('results/r14/fridge_arc_path.json'))
F = K.FRIDGE
look = [float(np.mean(F['x'])), F['y_face'] + .25, 1.0]
font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 22)
tmp = tempfile.mkdtemp(); n = 0
for a, q, res in zip(r['angles'], r['q_path'], r['reserve_mm']):
    cfg = chain.chain_cfg('SD', r14=True, present=[], r14_fridge=True, r14_fridge_door_deg=a, r14_held_handle=True)
    tree, _ = build(cfg, None); m = dress(tree); d = mujoco.MjData(m)
    d.qpos[:len(q)] = q; mujoco.mj_forward(m, d)
    rr = mujoco.Renderer(m, 540, 960); c = mujoco.MjvCamera(); c.lookat[:] = look
    c.azimuth, c.elevation, c.distance = 125, -18, 2.9
    o = mujoco.MjvOption(); o.geomgroup[:] = 1; o.geomgroup[HIDE] = 0
    rr.update_scene(d, c, o); im = Image.fromarray(rr.render()); rr.close()
    ImageDraw.Draw(im).text((10, 8), f'fridge door {a:g} deg   reserve {res:.1f} mm', fill=(0, 0, 0), font=font)
    for _ in range(3):
        im.save(f'{tmp}/f{n:04d}.png'); n += 1
    print(a, res, flush=True)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '10', '-i', f'{tmp}/f%04d.png', '-pix_fmt', 'yuv420p', out], check=True)
print(out, n)
