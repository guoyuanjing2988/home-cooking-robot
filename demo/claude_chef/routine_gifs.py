"""Per-routine demo GIFs: left = the wok camera while the routine runs in the sim (sampled from the hidden food
model as it evolves), right = the arm motion the routine uses (a checked path replay where one exists).

Usage: python routine_gifs.py  -> gifs/routines/<routine>.gif + gifs/routines/index.json
"""
import copy
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import cook_api
import wok_cam
from make_demo import clip_frames

ROOT = Path(__file__).resolve().parent
REN = ROOT.parent / 'robot_rail/sim/r10/claude/renders'
OUT = ROOT / 'gifs' / 'routines'
FB = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
FR = '/System/Library/Fonts/Supplemental/Arial.ttf'
W, H, PW, PH, N, FPS = 840, 372, 410, 308, 28, 7

# arm view per routine: (source, crop, a, b, caption, kind)  kind: path = checked continuous path, bench, pose, none
CUP = REN / 'mac/cup_pour.mp4'
ARM = {
    'mise_en_place': (ROOT / 'clips/tomato_AW_en.mp4', None, 0, 31, 'arm: tomato chain (R11, checked path)', 'path'),
    'heat_to': (None, None, 0, 0, 'no arm: knob servo + IR thermometer', 'none'),
    'fry_still': (None, None, 0, 0, 'no arm: the egg fries undisturbed', 'none'),
    'add_off_heat': (REN / 'mac/bowl_pour.mp4', '960:500:0:40', 0, 9.36, 'arm: bowl / cup pour, checked paths (R19 Mac)', 'path'),
    'season_and_toss': (CUP, '960:500:0:40', 0, 30, 'arm: cup pour (checked path), then stir', 'path'),
    'egg_into_hot_oil': (CUP, '960:500:0:40', 0, 30, 'arm: cup pour, checked path (R19 Mac)', 'path'),
    'flip_and_fry': (REN / 'mac/spatula_r18b.mp4', '960:500:0:40', 0, 16.2, 'arm: spatula fetch (R18b path); flip stroke not simulated', 'path'),
    'stir_fry': (REN / 'mac/stir_cycle.mp4', '960:500:0:40', 0, 13.5, 'arm: 5-stroke stir cycle, checked path', 'path'),
    'drum_add_stir': (REN / 'mac/stir_cycle.mp4', '960:500:0:40', 0, 13.5, 'servo drum releases; arm: checked stir cycle', 'path'),
    'take_out': (REN / 'r17/wok_sink.mp4', '960:500:0:40', 0, 32, 'arm: wok plate + rinse (R17, checked path)', 'path'),
    'season_wok': (REN / 'r17/wok_sink.mp4', '960:500:0:40', 0, 9, 'arm: wok lift + tip (R17 path); tip into the oil cup', 'path'),
    'return_and_toss': (REN / 'mac/bowl_pour.mp4', '960:500:0:40', 0, 9.36, 'arm: holding bowl pour, checked path (R19 Mac)', 'path'),
}
# a fallback for the cup routines while no cup chain exists
CUP_FALLBACK = (REN / 'r14/overview.png', 'pose')

# the script: every demo routine once, in a 7/7 order
SEQ = [('mise_en_place', dict(tomatoes=2, cups=[dict(what='oil', grams=40), dict(what='oil', grams=30), dict(what='salt', grams=1),
                                                 dict(what='sugar', grams=1)],
                               drum=[dict(what='ketchup', grams=5), dict(what='water', grams=60),
                                     dict(what='starch_water', grams=30), dict(what='finishing_oil', grams=5)])),
       ('season_wok', dict(cup='cup1', level=0.6, target_C=120)),
       ('add_off_heat', dict(source='cup2', level=0.6)),
       ('heat_to', dict(level=0.6, target_C=120)),
       ('add_off_heat', dict(source='egg', level=0.3)),
       ('fry_still', dict(seconds=55)),
       ('flip_and_fry', dict(seconds=20)),
       ('take_out', dict(into='holding_bowl')),
       ('add_off_heat', dict(source='tomato', level=0.3)),
       ('stir_fry', dict(level=0.3, seconds=40)),
       ('season_and_toss', dict(cups=['cup3', 'cup4'], level=0.3, seconds=20)),
       ('drum_add_stir', dict(seconds=15)),
       ('drum_add_stir', dict(seconds=45)),
       ('drum_add_stir', dict(seconds=20)),
       ('drum_add_stir', dict(seconds=5)),
       ('return_and_toss', dict(level=0.3, seconds=10)),
       ('take_out', dict(into='plate'))]
PICK = {'add_off_heat': 4, 'drum_add_stir': 13, 'take_out': 7}   # which occurrence (SEQ index) shows the routine
EXTRA = [('egg_into_hot_oil', [SEQ[0], SEQ[1], ('egg_into_hot_oil', dict(cup='cup2', level=0.6, target_C=120, fry_level=0.3)),
                               ('fry_still', dict(seconds=20))], 2)]


def record(seq):
    """Run seq; return per call: (name, args, result, [(t, truth, thermo)])."""
    k = cook_api.Kitchen(seed=0)
    snaps = []
    orig = k.advance
    cur = {'step': None}
    orig_call = k._call

    def _call(action, args):                       # tag snapshots with the primitive step that made them
        if action not in cook_api.ROUTINE_NAMES:
            cur['step'] = (len(cur.setdefault('n', [])), action, dict(args))
            cur['n'].append(1)
            snaps.append((round(k.t, 1), copy.deepcopy(k.wok.truth()), k.wok.sensors(k.rng).get('thermo_C'), k.wok.heat, cur['step'], 'before'))
        return orig_call(action, args)
    k._call = _call

    def adv(seconds, stirring=False):
        left = seconds
        while left > 1e-9:
            dt = min(1.0, left)
            orig(dt, stirring)
            left -= dt
            snaps.append((round(k.t, 1), copy.deepcopy(k.wok.truth()), k.wok.sensors(k.rng).get('thermo_C'), k.wok.heat, cur['step'], 'during'))
    k.advance = adv
    out = []
    for name, args in seq:
        snaps = []
        cur['n'] = []
        res = k.call(name, args)
        out.append((name, args, res, snaps))
    return out


def arm_frames(name):
    src, crop, a, b, cap, kind = ARM[name]
    if src is None:
        return None, cap, kind
    if not Path(src).exists():
        p, kind = CUP_FALLBACK
        im = Image.open(p).convert('RGB').crop((900, 36, 1800, 600)).resize((PW, PH))
        return [im] * N, 'arm: cup over the wok, checked pose only (R14); no continuous path yet', kind
    if isinstance(crop, str):                       # 'w:h:x:y' -> (x0, y0, x1, y1)
        w_, h_, x_, y_ = map(int, crop.split(':'))
        crop = (x_, y_, x_ + w_, y_ + h_)
    return clip_frames(src, crop, a, b, N, PW, PH), cap, kind


def make(name, args, res, snaps, path):
    fb, fr, fs = ImageFont.truetype(FB, 19), ImageFont.truetype(FR, 14), ImageFont.truetype(FR, 13)
    if not snaps:
        snaps = [(0, {}, None, 0, None, 'during')]
    idx = [round(i * (len(snaps) - 1) / max(N - 1, 1)) for i in range(N)]
    tmp = Path(tempfile.mkdtemp())
    wok = {}
    for i in sorted(set(idx)):
        f = tmp / f'w{i}.png'
        wok_cam.render(snaps[i][1], str(f), seed=7, size=(PW, PH))
        wok[i] = Image.open(f).convert('RGB')
    arms, cap, kind = arm_frames(name)
    steps = ' → '.join(dict.fromkeys(res.get('steps') or [name]))
    title = f"{name}({', '.join(f'{k}={v}' for k, v in args.items() if k not in ('cups', 'drum'))})"
    frames = []
    for j, i in enumerate(idx):
        t, tr, th, heat = snaps[i][:4]
        im = Image.new('RGB', (W, H), (14, 16, 20))
        dr = ImageDraw.Draw(im)
        dr.text((10, 6), title[:78], font=fb, fill=(238, 238, 240))
        dr.text((10, 30), f'{len(res.get("steps") or [])} steps, no pause: {steps}'[:118], font=fs, fill=(150, 155, 165))
        im.paste(wok[i], (10, 52))
        dr.rectangle((10, 52 + PH - 22, 10 + PW, 52 + PH), fill=(0, 0, 0))
        dr.text((16, 52 + PH - 19), f'wok camera · t={t:.0f} s · {"—" if th is None else f"{th:.0f} °C"} · heat {heat:.0%}',
                font=fr, fill=(240, 190, 80))
        if arms:
            im.paste(arms[j], (W - PW - 10, 52))
        else:
            dr.rectangle((W - PW - 10, 52, W - 10, 52 + PH), outline=(60, 64, 72))
            dr.text((W - PW + 20, 52 + PH // 2 - 10), 'the arm is not needed', font=fb, fill=(150, 155, 165))
        dr.rectangle((W - PW - 10, 52 + PH - 22, W - 10, 52 + PH), fill=(0, 0, 0))
        dr.text((W - PW - 4, 52 + PH - 19), cap[:60], font=fr, fill=(217, 119, 87) if kind == 'path' else (200, 200, 205))
        frames.append(im)
    seq = tmp / 'f%03d.png'
    for n, f in enumerate(frames):
        f.save(tmp / f'f{n:03d}.png')
    flt = 'split[x][y];[x]palettegen=max_colors=160:stats_mode=diff[p];[y][p]paletteuse=dither=bayer:bayer_scale=4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', str(seq), '-filter_complex', flt,
                    '-loop', '0', str(path)], check=True)
    return kind, cap


SKIP_STEPS = {'set_heat', 'fridge_fetch', 'prep_tomato', 'dose_cup', 'load_drum', 'done', 'look'}


def step_gifs(name, snaps, outdir):
    """One small top-down wok GIF per primitive step that changes the wok."""
    from collections import OrderedDict
    groups = OrderedDict()
    for s in snaps:
        if s[4] is not None:
            groups.setdefault(s[4][0], []).append(s)
    merged = OrderedDict()                          # consecutive short waits (heat-to loops) become one step
    for idx, g in groups.items():
        act = g[0][4][1]
        last = next(reversed(merged)) if merged else None
        if act == 'wait' and last is not None and merged[last][0][4][1] == 'wait' and g[0][4][2].get('seconds') == 3:
            merged[last] = merged[last] + g
            merged[last][0] = (*merged[last][0][:4], (merged[last][0][4][0], 'wait', {'until': 'target °C'}), merged[last][0][5])
        else:
            merged[idx] = list(g)
    groups = merged
    out = []
    fr = ImageFont.truetype(FR, 12)
    for idx, g in groups.items():
        _, act, args = g[0][4]
        if act in SKIP_STEPS or len(g) < 2:
            continue
        pick = [g[round(i * (len(g) - 1) / 9)] for i in range(10)] if len(g) > 10 else g
        tmp = Path(tempfile.mkdtemp()); frames = []
        for j, s in enumerate(pick):
            f = tmp / f'{j}.png'
            wok_cam.render(s[1], str(f), seed=7, size=(240, 180))
            im = Image.open(f).convert('RGB'); dr = ImageDraw.Draw(im)
            dr.rectangle((0, 160, 240, 180), fill=(0, 0, 0))
            dr.text((5, 163), f"t={s[0]:.0f}s {'—' if s[2] is None else f'{s[2]:.0f}°C'} heat {s[3]:.0%}", font=fr, fill=(240, 190, 80))
            frames.append(im)
        label = act + ('(' + ', '.join(f'{k}={v}' for k, v in args.items()) + ')' if args else '()')
        path = outdir / f'{name}_s{idx}.gif'
        frames[0].save(path, save_all=True, append_images=frames[1:] + [frames[-1]] * 3, duration=280, loop=0, optimize=True)
        out.append(dict(file=f'routines/steps/{path.name}', step=label, t=[g[0][0], g[-1][0]]))
    return out


def main():
    (OUT / 'steps').mkdir(parents=True, exist_ok=True)
    rec = record(SEQ)
    index = {}
    for i, (name, args, res, snaps) in enumerate(rec):
        if name in index or (name in PICK and i != PICK[name]):
            continue
        kind, cap = make(name, args, res, snaps, OUT / f'{name}.gif')
        index[name] = dict(file=f'routines/{name}.gif', arm=kind, arm_caption=cap, sim_span_s=[snaps[0][0], snaps[-1][0]] if snaps else None,
                           steps=step_gifs(name, snaps, OUT / 'steps'))
        print(name, res['code'], kind)
    for name, seq, at in EXTRA:
        r = record(seq)[at]
        kind, cap = make(name, r[1], r[2], r[3], OUT / f'{name}.gif')
        index[name] = dict(file=f'routines/{name}.gif', arm=kind, arm_caption=cap, steps=step_gifs(name, r[3], OUT / 'steps'))
        print(name, r[2]['code'], kind)
    json.dump(index, open(OUT / 'index.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
