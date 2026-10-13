"""Demo video from a Claude chef run: left = the robot doing the skill (replays/stills of motions the robot_rail
sim checked) + the wok camera Claude saw; right = Claude's panel (what it sees, why, the call, the gate's answer).

Usage: python make_demo.py runs/<name>/run.json out.mp4 [--pace 1.0] [--steps a:b]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import textwrap
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
REN = ROOT.parent / 'robot_rail/sim/r10/claude/renders'
W, H, FPS = 1920, 1080, 25
FONT = '/System/Library/Fonts/HelveticaNeue.ttc'
CJK = '/System/Library/Fonts/STHeiti Medium.ttc'
F = {k: ImageFont.truetype(FONT, s, index=i) for k, (s, i) in dict(
    h1=(40, 1), h2=(28, 1), b=(25, 0), bb=(25, 1), s=(20, 0), sb=(20, 1), xs=(17, 0), mono=(23, 0)).items()}
FZ = ImageFont.truetype(CJK, 36)
UNI = '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
_FB = {}
_SAFE = set('–—‘’“”…•')


def _runs(text, font):
    """Split text into (chunk, font) runs: Helvetica for Latin, Arial Unicode for arrows, ticks and CJK."""
    fb = _FB.setdefault(font.size, ImageFont.truetype(UNI, font.size))
    out = []
    for ch in text:
        f = font if (ord(ch) < 0x2000 or ch in _SAFE) else fb
        if out and out[-1][1] is f:
            out[-1][0] += ch
        else:
            out.append([ch, f])
    return out


def tlen(dr, text, font):
    return sum(dr.textlength(c, font=f) for c, f in _runs(text, font))


def tdraw(dr, xy, text, font, fill):
    x, y = xy
    for c, f in _runs(text, font):
        dr.text((x, y), c, font=f, fill=fill)
        x += dr.textlength(c, font=f)


BG, PANEL, INK, DIM = (243, 245, 247), (255, 255, 255), (22, 26, 32), (88, 98, 112)
CLAUDE, OK_C, BAD_C, WARN = (196, 98, 52), (43, 133, 81), (191, 67, 46), (176, 110, 12)

# (source, crop box in px or None, time a, time b) for clips; stills are (path, crop box)
CLIPS = {
    'fridge_fetch': (REN / 'r14/door_drum.mp4', (0, 60, 640, 510), 0, 10.5),
    'drum_release': (REN / 'r14/door_drum.mp4', (640, 60, 1280, 510), 0, 10.5),
    'prep_tomato': (ROOT / 'clips/tomato_AW_en.mp4', None, 0, 31),
    'stir': (REN / 'r15/stir_plate.mp4', (0, 60, 640, 510), 0, 13.5),
    'flip_egg': (REN / 'r15/stir_plate.mp4', (0, 60, 640, 510), 3, 8),
    'tip_wok': (REN / 'r17/wok_sink.mp4', (0, 40, 960, 540), 0, 32),        # plate + sink rinse + back (R17)
    'tip_wok_spot2': (REN / 'r17/wok_sink.mp4', (0, 40, 960, 540), 0, 8),   # lift and tip only
    'cup_pour': (REN / 'mac/cup_pour.mp4', (0, 40, 960, 540), 0, 9.4),      # station -> wok -> pour -> back (R19 Mac)
    'stir_arm': (REN / 'mac/stir_cycle.mp4', (0, 40, 960, 540), 0, 13.5),   # the checked 5-stroke cycle with the arm (R15/R18, Mac re-run)
    'spatula_fetch': (REN / 'mac/spatula_r18b.mp4', (0, 40, 960, 540), 0, 16.2),   # rest -> stroke start (R18b)
}
STILLS = {
    'dose_cup': (REN / 'r14/overview.png', (0, 36, 900, 600)),
    'pour_into_wok': (REN / 'r14/overview.png', (900, 36, 1800, 600)),
    'load_drum': (REN / 'r15/cooking.png', (2280, 34, 3040, 620)),
    'tip_wok_lift': (REN / 'r15/cooking.png', (760, 34, 1520, 620)),
    'stir_pose': (REN / 'r15/cooking.png', (0, 34, 760, 620)),
}
LABEL = {
    'fridge_fetch': 'Fridge door physics + cold-box fetch (R14, MuJoCo). The eggs were cracked and beaten by the user beforehand',
    'prep_tomato': 'Tomato chain replay, 6,653 collision-checked states (R11). Starts with the tomato already in the gripper; '
                   'the rinse water and the cutting are not physically simulated',
    'dose_cup': 'Robot cup at the seasoning station port (R14, checked pose)',
    'pour_into_wok': 'Arm over the wok, heat off (R14 checked pose)',
    'load_drum': 'Pour drum into the holder behind the wok (R15, zero reserve)',
    'drum_release': '4-compartment pour drum, released in order (R14 physics)',
    'stir': 'Scrape stroke, physics bench (R15). Executable at about 3.6 s per stroke (R19 smooth-motion check)',
    'flip_egg': 'Spatula stroke (single-piece flip not simulated)',
    'tip_wok': 'Heat off: plate, rinse the wok under the running tap, set it back (R17 path, re-checked at ≤ 4 mm in R19, sped up)',
    'tip_wok_spot2': 'Heat off: tip at the second plating spot and set the wok back (R18 checked spot; replay shows the R17 tip)',
    'cup_pour': 'Seasoning cup: station → wok → pour → back, one checked path (R19)',
    'stir_arm': 'Arm stirring: the checked 5-stroke scrape cycle (2.0 mm reserve; R19: about 3.6 s per stroke)',
    'spatula_fetch': 'The arm takes the spatula from its rest to the wok, one checked path (R18b)',
}


def fit(img, w, h, bg=BG):
    img = img.convert('RGB')
    s = min(w / img.width, h / img.height)
    im = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.LANCZOS)
    out = Image.new('RGB', (w, h), bg)
    out.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
    return out


def clip_frames(src, crop, a, b, n, w, h):
    """n frames evenly over [a, b] of src, cropped and fitted into w x h."""
    vf = (f'crop={crop[2] - crop[0]}:{crop[3] - crop[1]}:{crop[0]}:{crop[1]},' if crop else '')
    fps = max(n / max(b - a, 0.1), 0.5)
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(a), '-t', str(b - a), '-i', str(src), '-vf',
           vf + f'fps={fps:.4f},scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=0xe8ecf0',
           '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    k = len(raw) // (w * h * 3)
    frames = [Image.frombuffer('RGB', (w, h), raw[i * w * h * 3:(i + 1) * w * h * 3]) for i in range(k)]
    if not frames:
        frames = [Image.new('RGB', (w, h), BG)]
    return [frames[min(int(i * len(frames) / n), len(frames) - 1)] for i in range(n)]


def wrap(dr, xy, text, font, fill, width_px, line_h, max_lines=99):
    x, y = xy
    words, line, lines = text.split(), '', []
    for wd in words:
        t = (line + ' ' + wd).strip()
        if tlen(dr, t, font) <= width_px:
            line = t
        else:
            lines.append(line); line = wd
    if line:
        lines.append(line)
    if len(lines) > max_lines:
        lines = lines[:max_lines]; lines[-1] += ' …'
    for ln in lines:
        tdraw(dr, (x, y), ln, font, fill); y += line_h
    return y


def fmt_call(action, args):
    if not args:
        return f'{action}()'
    def v(x):
        if isinstance(x, list):
            return '[' + ', '.join(f"{i['what']} {i['grams']:g}g" if isinstance(i, dict) else str(i) for i in x) + ']'
        return f'{x:g}' if isinstance(x, float) else json.dumps(x, ensure_ascii=False)
    return f"{action}(" + ', '.join(f'{k}={v(x)}' for k, x in args.items() if k != 'summary') + ')'


def mmss(t):
    return f'{int(t // 60)}:{int(t % 60):02d}'


def panel(d, k, n_total, t_frac=1.0):
    """Static parts of one step's frame except the robot view."""
    im = Image.new('RGB', (W, H), BG)
    dr = ImageDraw.Draw(im)
    dec, res = d['decision'], d['result']
    s = res['sensors']
    # header
    dr.text((30, 18), 'Claude cooks', font=F['h1'], fill=INK)
    x = 30 + dr.textlength('Claude cooks ', font=F['h1'])
    dr.text((x, 18), 'tomato & egg', font=F['h1'], fill=CLAUDE)
    x += dr.textlength('tomato & egg', font=F['h1']) + 14
    dr.text((x, 26), "· Wang Gang's recipe, one-arm kitchen robot (MuJoCo)", font=F['b'], fill=DIM)
    dr.text((W - 330, 22), f'kitchen clock {mmss(s["t_s"])}', font=F['h2'], fill=WARN)
    dr.text((W - 330, 56), f'decision {k + 1} of {n_total}', font=F['s'], fill=DIM)
    # bottom-left: wok camera Claude saw + gauges
    dr.rounded_rectangle((20, 760, 1160, 1060), 14, fill=PANEL)
    if d.get('seen_image') and Path(d['seen_image']).exists():
        im.paste(fit(Image.open(d['seen_image']), 384, 288), (34, 766))
        tdraw(dr, (40, 770), 'wok camera → Claude', F['xs'], (255, 255, 255))
    else:
        dr.text((60, 900), 'no wok image yet (cold, empty wok)', font=F['s'], fill=DIM)
    gx = 440
    th = s.get('thermo_C')
    dr.text((gx, 778), 'thermometer', font=F['s'], fill=DIM)
    dr.text((gx, 802), '—' if th is None else f'{th:.0f} °C', font=F['h1'],
            fill=BAD_C if (th or 0) >= 200 else WARN if (th or 0) >= 150 else INK)
    dr.text((gx + 230, 778), 'induction power', font=F['s'], fill=DIM)
    hv = float(s.get('heat') or 0)
    dr.rounded_rectangle((gx + 230, 812, gx + 430, 840), 8, outline=DIM, width=2)
    if hv > 0:
        dr.rounded_rectangle((gx + 232, 814, gx + 232 + int(196 * hv), 838), 7, fill=(235, 120, 60))
    dr.text((gx + 440, 812), f'{hv:.0%}', font=F['bb'], fill=INK)
    if s.get('smoke_detector'):
        dr.text((gx, 850), 'SMOKE DETECTOR', font=F['bb'], fill=BAD_C)
    kv = res.get('kitchen', {})
    inv = []
    if kv.get('counter'):
        inv.append('counter: ' + ', '.join(f'{a} {b} g' for a, b in kv['counter'].items()))
    if kv.get('cups'):
        inv.append('cups: ' + '; '.join(kv['cups'].values()))
    if kv.get('drum') and kv['drum'].get('remaining'):
        inv.append('drum: ' + ' → '.join(kv['drum']['remaining']))
    if kv.get('holding_bowl'):
        inv.append('holding bowl: ' + ', '.join(kv['holding_bowl']))
    if kv.get('plate'):
        inv.append('plate: ' + ', '.join(x for x in kv['plate'] if x not in ('salt', 'sugar')))
    y = 890
    for ln in inv[:5]:
        y = wrap(dr, (gx, y), ln, F['s'], INK, 690, 26, 2)
    # right: Claude panel
    X0 = 1180
    dr.rounded_rectangle((X0, 100, W - 20, 1060), 16, fill=PANEL)
    dr.ellipse((X0 + 24, 122, X0 + 52, 150), fill=CLAUDE)
    dr.text((X0 + 64, 118), 'Claude  ·  Opus 5.5', font=F['h2'], fill=INK)
    sec = d.get('claude', {}).get('seconds')
    if d.get('think_s'):
        tx = f"{d['think_s']:.0f} s to decide · the cooker kept running"
        dr.text((W - 40 - dr.textlength(tx, font=F['s']), 124), tx, font=F['s'], fill=WARN)
    elif sec:
        dr.text((W - 200, 124), f'{sec:.0f} s to decide', font=F['s'], fill=DIM)
    cw = W - 20 - X0 - 48
    y = 176
    dr.text((X0 + 24, y), 'SEES', font=F['sb'], fill=CLAUDE); y += 30
    y = wrap(dr, (X0 + 24, y), dec['observe'], F['b'], INK, cw, 33, 6) + 14
    dr.text((X0 + 24, y), 'DECIDES', font=F['sb'], fill=CLAUDE); y += 30
    y = wrap(dr, (X0 + 24, y), dec['why'], F['b'], INK, cw, 33, 9) + 16
    call = fmt_call(dec['action'], dec.get('args') or {})
    box_h = 20 + 32 * len(textwrap.wrap(call, 44))
    dr.rounded_rectangle((X0 + 20, y, W - 40, y + box_h), 10, fill=(246, 241, 237), outline=CLAUDE, width=2)
    yy = y + 10
    for ln in textwrap.wrap(call, 44):
        tdraw(dr, (X0 + 36, yy), ln, F['mono'], INK); yy += 32
    y += box_h + 16
    if res['ok']:
        tdraw(dr, (X0 + 24, y), '✓ safety gate: executed', F['bb'], OK_C); y += 36
        y = wrap(dr, (X0 + 24, y), res['message'], F['s'], DIM, cw, 27, 2) + 8
    else:
        tdraw(dr, (X0 + 24, y), f"✗ safety gate: {res['code']}", F['bb'], BAD_C); y += 36
        y = wrap(dr, (X0 + 24, y), res['message'], F['s'], INK, cw, 27, 4) + 8
    if dec.get('expect') and y < 960:
        dr.text((X0 + 24, y + 6), 'EXPECTS', font=F['sb'], fill=CLAUDE)
        wrap(dr, (X0 + 24, y + 36), dec['expect'], F['s'], DIM, cw, 27, max(1, (1040 - y - 36) // 27))
    return im


ROUTINE_VIEW = dict(mise_en_place='prep_tomato', add_off_heat='pour_into_wok', fry_still='wait', heat_to='set_heat',
                    flip_and_fry='flip_egg', stir_fry='stir', drum_add_stir='drum_release', take_out='tip_wok',
                    return_and_toss='pour_into_wok')


def robot_view(d, n):
    """n frames (1140 x 640) of what the robot does for this decision."""
    w, h = 1140, 640
    routine, res = d['decision']['action'], d['result']
    act = ROUTINE_VIEW.get(routine, routine)
    args = d['decision'].get('args') or {}
    src_ = str(args.get('source') or args.get('cup') or '')
    if routine in ('season_and_toss', 'egg_into_hot_oil', 'pour_cup_mid_stir') or (act == 'pour_into_wok' and src_.startswith('cup')):
        act = 'cup_pour'
    elif act in ('stir', 'flip_egg') and 'spatula taken' in res.get('message', ''):
        act = 'spatula_fetch'
    elif routine == 'season_wok':
        act = 'tip_wok_spot2'
    elif act in ('stir', 'drum_release'):
        act = 'stir_arm'
    if not res['ok']:
        img = Image.new('RGB', (w, h), (251, 234, 230))
        dr = ImageDraw.Draw(img)
        dr.text((60, 270), 'Refused before anything moved', font=F['h1'], fill=BAD_C)
        dr.text((60, 330), 'Claude reads the reason and plans again', font=F['h2'], fill=INK)
        return [img] * n
    wok_p = res.get('image') or d.get('seen_image')
    wok = fit(Image.open(wok_p), w, h) if wok_p and Path(wok_p).exists() else None
    inset = None
    if act in ('cup_pour', 'spatula_fetch', 'stir_arm') and wok is not None:
        src, crop, a, b = CLIPS[act]
        frames = clip_frames(src, crop, a, b, n, w, h)
        inset = [fit(Image.open(wok_p), 420, 315)] * n
    elif act in ('stir', 'flip_egg', 'drum_release') and wok is not None:
        frames = [wok] * n                  # the wok itself is the story; the checked motion goes in the inset
        src, crop, a, b = CLIPS[act]
        inset = clip_frames(src, crop, a, b, n, 420, 296)
    elif act in CLIPS:
        if act == 'tip_wok' and (d['decision'].get('args') or {}).get('into') != 'plate':
            act = 'tip_wok_spot2'
        src, crop, a, b = CLIPS[act]
        frames = clip_frames(src, crop, a, b, n, w, h)
    elif act in STILLS:
        p, box = STILLS[act]
        frames = [fit(Image.open(p).crop(box), w, h)] * n
        if act == 'pour_into_wok' and wok is not None:
            inset = [fit(Image.open(wok_p), 420, 315)] * n
    else:                                   # set_heat / wait / look / done: the wok itself
        frames = [wok or Image.new('RGB', (w, h), BG)] * n
    if inset:
        frames = [f.copy() for f in frames]
        for f, s in zip(frames, inset):
            ImageDraw.Draw(f).rectangle((w - 446, 14, w - 14, 26 + s.height), fill=(22, 26, 32))
            f.paste(s, (w - 440, 20))
    lab = LABEL.get(act, {'set_heat': 'Induction cooker (knob servo)', 'wait': 'Waiting, cooker running',
                          'look': 'Hood camera + IR thermometer', 'done': 'Done'}.get(act, act))
    if routine in ROUTINE_VIEW and res.get('steps'):
        ns = len(res['steps'])
        if ns > 1:
            lab = f"Routine, {ns} steps without a pause: {' → '.join(dict.fromkeys(res['steps']))} · " + lab
    if res['message'].startswith('spatula'):
        lab += ' · ' + res['message'].split(';')[0] + ', R18b checked path'
    tmp = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    words, lines = lab.split(), ['']
    for wd in words:
        if tlen(tmp, (lines[-1] + ' ' + wd).strip(), F['s']) > w - 28:
            lines.append(wd)
        else:
            lines[-1] = (lines[-1] + ' ' + wd).strip()
    bar = 12 + 26 * len(lines)
    out = []
    for f in frames:
        f = f.copy()
        dr = ImageDraw.Draw(f)
        dr.rectangle((0, h - bar, w, h), fill=(255, 255, 255))
        for i, ln in enumerate(lines):
            tdraw(dr, (14, h - bar + 6 + 26 * i), ln, F['s'], INK)
        out.append(f)
    return out


def step_seconds(d, pace, hl=None, routine=None):
    """Reading time; with a highlight list, routine steps flash by and highlights stay long enough to read."""
    if hl is not None:
        return hl if d['step'] in HL else routine
    dec = d['decision']
    n = len(dec['observe']) + len(dec['why'])
    return pace * min(9.0, max(4.0, 2.0 + n / 55))


HL = set()


def card(lines, sub=None):
    """Full-frame text card: lines = [(text, font key, colour)]."""
    im = Image.new('RGB', (W, H), BG)
    dr = ImageDraw.Draw(im)
    y = 300 if sub is None else 220
    for text, fk, col in lines:
        f = FZ if fk == 'zh' else F[fk]
        tdraw(dr, ((W - tlen(dr, text, f)) // 2, y), text, f, col)
        y += {'h1': 70, 'h2': 50, 'zh': 60}.get(fk, 40)
    if sub:
        y += 20
        for ln in sub:
            y = wrap(dr, (360, y), ln, F['b'], INK, 1200, 36) + 12
    return im


REALTIME_RUN = False


def intro():
    return card([('Claude cooks Wang Gang\u2019s', 'h1', INK), ('tomato & egg stir-fry', 'h1', CLAUDE)], sub=[
        'Opus 5.5 runs a one-arm kitchen robot, one skill call at a time. It works only from the recipe in Wang Gang\u2019s '
        'own words, a thermometer and a wok camera.',
        'A deterministic safety gate checks every call before anything moves.',
        *(['Real time: the kitchen does not wait while Claude thinks. The cooker keeps running during every decision.']
          if REALTIME_RUN else []),
        'Robot motions are replays of paths checked in MuJoCo; each clip says what was checked.'])


OVERVIEW = REN / 'r17/r17_overview.png'
OVERVIEW_EN = ['Open the faucet: lever lifted 30°', 'Plate: tip the wok 90° at the plating spot',
               'Rinse: under the running tap, 5 s', 'Empty the rinse water', 'Spider: scoop from the pot',
               'Lid: off the pot, upright into the rack']


def kitchen_card():
    """The kitchen Claude cooks in: R17 checked actions with English captions."""
    im = Image.new('RGB', (W, H), BG)
    dr = ImageDraw.Draw(im)
    title = 'The kitchen: designed and checked in MuJoCo over 18 rounds'
    tdraw(dr, ((W - tlen(dr, title, F['h1'])) // 2, 40), title, F['h1'], INK)
    sub = ('R01–R09 with Codex · R10–R18 with Claude. Every motion below is one continuous path, '
           'collision-checked at every step (10 mm robot, 5 mm gripper reserve).')
    tdraw(dr, ((W - tlen(dr, sub, F['b'])) // 2, 104), sub, F['b'], DIM)
    ov = Image.open(OVERVIEW).convert('RGB')
    pw, ph = ov.width // 3, ov.height // 2
    tw, th = 600, 338
    for i, cap in enumerate(OVERVIEW_EN):
        r, c = divmod(i, 3)
        tile = fit(ov.crop((c * pw, r * ph + 36, (c + 1) * pw, (r + 1) * ph)), tw, th)
        x, y = 30 + c * (tw + 30), 170 + r * (th + 70)
        im.paste(tile, (x, y))
        tdraw(dr, (x, y + th + 10), f'{i + 1}  {cap}', F['bb'], INK)
    return im


def outro(run):
    import score as S
    s = S.score(run)
    lines = [('Plated. Scored against the hidden wok model Claude never saw', 'h2', INK)]
    im = card(lines, sub=None)
    dr = ImageDraw.Draw(im)
    y = 400
    for name, ok, detail in s['checks']:
        tdraw(dr, (520, y), ('✓ ' if ok else '✗ ') + name, F['h2'], OK_C if ok else BAD_C)
        dr.text((1120, y + 4), detail, font=F['b'], fill=DIM); y += 52
    y += 20
    stats = (f"{s['decisions']} decisions by Claude · {s['refused']} refused by the gate, then fixed by Claude · "
             f"kitchen time {mmss(s['kitchen_s'])}{' incl. thinking' if run.get('realtime') else ''} · peak {s['peak_C']:.0f} °C")
    tdraw(dr, ((W - tlen(dr, stats, F['b'])) // 2, y), stats, F['b'], WARN)
    y += 70
    wrap(dr, (300, y), 'Modelled, not real: the cooking itself (heat, egg setting, tomato softening, sauce thickening) is a '
         'lumped thermal and kinetics model rendered by MuJoCo. Not simulated: liquids and rinse water, cutting (the tomato '
         'replay starts with it already gripped), flipping a single piece. The eggs are cracked and beaten by the user '
         'beforehand.', F['s'], DIM, 1320, 30)
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run'); ap.add_argument('out')
    ap.add_argument('--pace', type=float, default=1.0)
    ap.add_argument('--steps', default=None)
    ap.add_argument('--highlights', default=None, help='comma list of step numbers to hold')
    ap.add_argument('--hl', type=float, default=6.5)
    ap.add_argument('--routine', type=float, default=1.6)
    ap.add_argument('--cards', action='store_true')
    a = ap.parse_args()
    run = json.load(open(a.run, encoding='utf-8'))
    global REALTIME_RUN
    REALTIME_RUN = bool(run.get('realtime'))
    D = run['decisions']
    sel = range(len(D))
    if a.steps:
        i, j = a.steps.split(':'); sel = range(int(i or 0), int(j or len(D)))
    tmp = Path(a.out).with_suffix('.tmp.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                          '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20',
                          '-movflags', '+faststart', str(tmp)], stdin=subprocess.PIPE)
    total = 0
    if a.highlights:
        HL.update(int(x) for x in a.highlights.split(','))
    def hold(img, sec):
        nonlocal total
        for _ in range(int(sec * FPS)):
            p.stdin.write(img.tobytes())
        total += int(sec * FPS)
    if a.cards:
        hold(intro(), 5)
    for k in sel:
        d = D[k]
        n = int((step_seconds(d, a.pace, a.hl, a.routine) if a.highlights else step_seconds(d, a.pace)) * FPS)
        base = panel(d, k, len(D))
        for f in robot_view(d, n):
            fr = base.copy()
            fr.paste(f, (20, 100))
            p.stdin.write(fr.tobytes())
        total += n
    if a.cards:
        hold(outro(run), 10)
    p.stdin.close(); p.wait()
    tmp.rename(a.out)
    print(a.out, f'{total / FPS:.1f} s')


if __name__ == '__main__':
    main()
