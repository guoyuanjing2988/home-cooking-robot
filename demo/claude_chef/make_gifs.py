"""GIFs of the predefined, sim-checked robot motions (crops away the Chinese caption bands, adds an English title).

Usage: python make_gifs.py  -> gifs/*.gif + gifs/index.json
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REN = ROOT.parent / 'robot_rail/sim/r10/claude/renders'
OUT = ROOT / 'gifs'
FONT = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
W, FPS, TARGET_S = 480, 8, 12.0

# name, source, crop (w:h:x:y) or None, start, end, title, what was checked
GIFS = [
    ('tomato_prep', ROOT / 'clips/tomato_AW_en.mp4', None, 0, 31, 'Tomato: lift, rinse, lever cutter (R11)',
     '5,992–6,653 states, each collision-checked. Starts with the tomato gripped; water and cutting not simulated.'),
    ('carrot_prep', REN / 'carrot_AS.mp4', '1280:590:0:92', 0, 31.3, 'Carrot: pick, wash, peel, slicer chute (R11)',
     '7,431 states, each collision-checked; cart moves between stations.'),
    ('grasp_physics', REN / 'physics_grasp.mp4', '1280:590:0:92', 0, 82, 'Grasp with physics: food is a free body (R12)',
     'MuJoCo rigid-body dynamics, nothing welded to the gripper; slip measured.'),
    ('fridge_arm', REN / 'mac/fridge_arc.mp4', '960:500:0:40', 0, 6.9, 'Fridge: arm pulls the door open, 0-55° (R14)',
     'The checked handle arc from the docked cart: 23 door angles, one IK branch, 0.1–4.2 mm reserve.'),
    ('spatula_rest', REN / 'mac/spatula_r18b.mp4', '960:500:0:40', 0, 16.2, 'Spatula: counter rest to the first stroke (R18b)',
     '26.9 s, one continuous checked path, 6.0 mm reserve; the cart moves while the arm holds the spatula.'),
    ('foods_bench', REN / 'r13/foods_physics.mp4', '1920:1190:0:50', 0, 17, 'Bench, no arm: about 40 foods (R13)',
     '702 rigid + 53 non-rigid runs; one grasp method per food.'),
    ('fridge_door', REN / 'r14/door_drum.mp4', '640:450:0:60', 0, 10.5, 'Bench, no arm: fridge door force (R14)',
     'Door physics, 100 N seal, 14 kg door.'),
    ('pour_drum', REN / 'r14/door_drum.mp4', '640:450:640:60', 0, 10.5, 'Servo, no arm: pour drum release (R14)',
     'Servo turns the drum; granules 100 % in order. Liquids not simulated.'),
    ('stir_bench', REN / 'r15/stir_plate.mp4', '640:450:0:60', 0, 13.5, 'Bench, no arm: stir stroke physics (R15)',
     'Physics bench with 90 rigid dice. R19: executable at about 3.6 s per stroke.'),
    ('plating_tip', REN / 'r15/stir_plate.mp4', '640:450:640:60', 0, 13.5, 'Bench, no arm: plating spill (R15)',
     '81–91 % of rigid dice on the plate (98 % at half load).'),
    ('stir_arm', REN / 'mac/stir_cycle.mp4', '960:500:0:40', 0, 13.5, 'Arm stirring: the 5-stroke scrape cycle (R15, Mac re-run)',
     'Checked path at cart x 0.55: 2.0 mm reserve, 25.8 mm plume clearance; R19: about 3.6 s per stroke.'),
    ('bowl_pour', REN / 'mac/bowl_pour.mp4', '960:500:0:40', 0, 9.36, 'Bowl: counter -> wok -> pour -> back (R19 Mac)',
     'One continuous checked path, 25.8 s, 1.9 mm reserve, 300 g load; 272 states re-checked, 0 hits.'),
    ('cup_pour', REN / 'mac/cup_pour.mp4', '960:500:0:40', 0, 9.4, 'Seasoning cup: station -> wok -> pour -> station (R19 Mac)',
     'One continuous checked path, 20.6 s, 2.2 mm reserve; the station pad moved 10 cm left.'),
    ('wok_plate_rinse', REN / 'r17/wok_sink.mp4', '960:500:0:40', 0, 32, 'Wok: plate, rinse at the sink, back on the cooker (R17)',
     'One continuous path, 48.9 s, every step checked; 2.0 mm min reserve (R19 re-check).'),
    ('faucet_lever', REN / 'r17/lever.mp4', '960:500:0:40', 0, 0.77, 'Faucet: lever lifted 30° from the right (R17)',
     '3.5 s, clip-on block on the user\'s single-lever faucet.'),
    ('lid_rack', REN / 'r17/lid.mp4', '960:500:0:40', 0, 13.9, 'Lid: off the pot, upright into the rack (R17)',
     '20.2 s, 1.0 mm reserve: needs a keyed tab (issue #8).'),
    ('spider', REN / 'r17/spider.mp4', '960:500:0:40', 0, 36.6, 'Spider: scoop from the pot, drain, tip onto the plate (R17)',
     '52.6 s, 2.1 mm reserve.'),
]


def esc(t):
    return t.replace('\\', '\\\\').replace(':', '\\:').replace("'", "’").replace('%', '\\%')


def title_png(title, speed, path):
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new('RGB', (W, 34), (14, 16, 20))
    dr = ImageDraw.Draw(im)
    dr.text((10, 8), title, font=ImageFont.truetype(FONT, 16), fill=(238, 238, 240))
    if speed > 1.05:
        s = f'{speed:.1f}x'
        f = ImageFont.truetype(FONT, 14)
        dr.text((W - 10 - dr.textlength(s, font=f), 9), s, font=f, fill=(217, 119, 87))
    elif speed < 0.95:
        f = ImageFont.truetype(FONT, 14)
        dr.text((W - 10 - dr.textlength('slow', font=f), 9), 'slow', font=f, fill=(217, 119, 87))
    im.save(path)


def make(name, src, crop, a, b, title):
    dur = b - a
    speed = max(1.0, dur / TARGET_S) if dur > 2 else 1 / 3     # long clips sped up; the 0.8 s lever slowed down
    tp = OUT / f'_{name}_title.png'
    title_png(title, speed, tp)
    vf = [f'crop={crop}'] if crop else []
    vf += [f'setpts=PTS/{speed:.4f}', f'fps={FPS}', f'scale={W}:-2:flags=lanczos', 'pad=iw:ih+34:0:34:color=0x0e1014']
    out = OUT / f'{name}.gif'
    flt = (f'[0:v]{",".join(vf)}[v];[v][1:v]overlay=0:0,split[x][y];'
           '[x]palettegen=max_colors=128:stats_mode=diff[p];[y][p]paletteuse=dither=bayer:bayer_scale=4')
    loop = ['-stream_loop', '2'] if dur < 2 else []
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *loop, '-ss', str(a), '-t', str(dur * (3 if loop else 1)), '-i', str(src),
                    '-i', str(tp), '-filter_complex', flt, '-loop', '0', str(out)], check=True)
    tp.unlink()
    return out, speed


def main():
    OUT.mkdir(exist_ok=True)
    idx = []
    for name, src, crop, a, b, title, note in GIFS:
        out, speed = make(name, src, crop, a, b, title)
        idx.append(dict(name=name, file=out.name, title=title, note=note, speed=round(speed, 2),
                        source=str(src.relative_to(ROOT.parent)), kb=out.stat().st_size // 1024))
        print(f'{out.name:24s} {out.stat().st_size / 1e6:5.1f} MB  x{speed:.1f}')
    json.dump(idx, open(OUT / 'index.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
