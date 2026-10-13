"""Render the saved, checked stir cycle (results/r19/stir/stirwalk2_h_scrape_dice_r17.json) with the arm in the kitchen.
Run from the sim dir: python render_stir.py out.mp4 [az] [el] [dist]"""
import os, sys, json, subprocess, tempfile
sys.path.insert(0, os.getcwd())
import numpy as np, mujoco
from PIL import Image, ImageDraw, ImageFont
import chain, kitchen15 as K
import kitchen16 as K16
from scene import build
from dress import dress, HIDE
out = sys.argv[1]
az, el, dist = (float(x) for x in (sys.argv[2:5] if len(sys.argv) > 4 else (150, -28, 1.9)))
r = json.load(open('results/r19/stir/stirwalk2_h_scrape_dice_r17.json'))
st = r['states']; Q = np.array(st['q']); kinds = st['kinds']
sign = r['attempts'][-1]['jaw_sign'] if r.get('attempts') else 1
K16.set_design(pot_h=.12, rack=.04, lid_a=0., car_a=45., rack_ry=90.); K16.TOOL_XY['spider'] = (1.52, .36)
SCN = dict(r16=True, r17=True, r16_lid='rack', r15_drum_taken=True, r16_tools={'ladle': None, 'spatula': None})
cfg = chain.chain_cfg('SD', r14=True, present=[], r15=True, r15_spatula=r.get('grip_m', .45), r15_spatula_jaw=sign, **SCN)
tree, _ = build(cfg, None); m = dress(tree); d = mujoco.MjData(m)
rr = mujoco.Renderer(m, 540, 960); c = mujoco.MjvCamera(); c.lookat[:] = [K.WOK0[0] - .15, K.WOK0[1] - .05, K.WOK0[2] + .15]
c.azimuth, c.elevation, c.distance = az, el, dist
o = mujoco.MjvOption(); o.geomgroup[:] = 1; o.geomgroup[HIDE] = 0
font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 22)
tmp = tempfile.mkdtemp(); n = 0; stroke = 0
for i, (q, kd) in enumerate(zip(Q, kinds)):
    if kd.startswith('work'):
        step = 3                                       # 10 ms states -> 30 fps real time
        stroke = int(kd[4:]) + 1
    else:
        step = 2
    if i % step:
        continue
    d.qpos[:len(q)] = q; mujoco.mj_forward(m, d); rr.update_scene(d, c, o)
    im = Image.fromarray(rr.render())
    ImageDraw.Draw(im).text((10, 8), f'stir cycle, stroke {stroke}/5 - checked path (R19: ~3.6 s per stroke)', fill=(0, 0, 0), font=font)
    im.save(f'{tmp}/f{n:05d}.png'); n += 1
rr.close()
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '30', '-i', f'{tmp}/f%05d.png', '-pix_fmt', 'yuv420p', out], check=True)
print(out, n, 'frames', 'jaw sign', sign)
