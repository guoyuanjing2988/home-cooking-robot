"""The 2:30–3:00 Build Day video: title, scenario, setup, prep tools, checked motions, routines, one dish, status.
Light theme, 1920x1080, 25 fps. Usage: python make_final.py out/final.mp4"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

from make_demo import F, FONT, W, H, FPS, tdraw, tlen, wrap, clip_frames, fit
from PIL import ImageFont

ROOT = Path(__file__).resolve().parent
REN = ROOT.parent / 'robot_rail/sim/r10/claude/renders'
G = ROOT / 'gifs'
M = Path('/private/tmp/claude-501/-Users-yg736648-SingleAgent/c4e71ca0-97c9-4211-a65b-bfe953e755b5/scratchpad/deck/m')
BG, PANEL, INK, DIM, LINE = (243, 245, 247), (255, 255, 255), (22, 26, 32), (88, 98, 112), (220, 225, 231)
COP, STEEL, OK = (181, 90, 34), (42, 106, 156), (43, 133, 81)
D = {k: ImageFont.truetype(FONT, s, index=1) for k, s in dict(hero=96, h=58, m=34, tile=27).items()}
B = {k: ImageFont.truetype(FONT, s, index=0) for k, s in dict(l=30, b=25, s=21).items()}


def base(sec, title):
    im = Image.new('RGB', (W, H), BG)
    dr = ImageDraw.Draw(im)
    if sec:
        tdraw(dr, (80, 52), sec.upper(), F['sb'], COP)
    if title:
        tdraw(dr, (80, 84), title, D['h'], INK)
    return im, dr


def still(path, w, h, box=None):
    im = Image.open(path).convert('RGB')
    if box:
        im = im.crop(box)
    return fit(im, w, h, bg=(232, 236, 240))


def anim(src, n, w, h, a=0, b=None):
    if b is None:
        b = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(src)],
                                 capture_output=True, text=True).stdout.strip() or 4)
    return clip_frames(src, None, a, b, n, w, h)


def tile(dr, x, y, w, name, text, color=DIM):
    tdraw(dr, (x, y), name, D['tile'], INK)
    wrap(dr, (x, y + 36), text, B['s'], color, w, 27, 3)


class Out:
    def __init__(self, path):
        self.p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                                   '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-r', str(FPS), str(path)],
                                  stdin=subprocess.PIPE)
        self.n = 0

    def put(self, im):
        self.p.stdin.write(im.tobytes()); self.n += 1

    def close(self):
        self.p.stdin.close(); self.p.wait()


def section(out, seconds, bg, layers):
    """bg: static frame; layers: [(frames, (x, y))] animated tiles pasted each frame."""
    n = int(seconds * FPS)
    for i in range(n):
        f = bg.copy()
        for frames, xy in layers:
            f.paste(frames[i % len(frames)], xy)
        out.put(f)


def grid_section(out, seconds, sec, title, items, cols=3, tw=540, th=304, top=200, gap=40, caption_h=110):
    bg, dr = base(sec, title)
    x0 = (W - (cols * tw + (cols - 1) * gap)) // 2
    layers = []
    n = int(seconds * FPS)
    for k, (src, name, text, kind) in enumerate(items):
        r, c = divmod(k, cols)
        x, y = x0 + c * (tw + gap), top + r * (th + caption_h)
        if kind == 'still':
            bg.paste(still(src, tw, th), (x, y))
        else:
            layers.append((anim(src, min(n, 200), tw, th), (x, y)))
        tile(dr, x, y + th + 10, tw, name, text)
    section(out, seconds, bg, layers)


def main(path):
    out = Out(path)
    # 1 title
    bg, dr = base('Claude Code Build Day · Singapore · 13 Oct 2026', None)
    tdraw(dr, (80, 150), 'Claude cooks dinner', D['hero'], INK)
    tdraw(dr, (84, 270), 'A one-arm home kitchen robot · Claude Opus 5.5 decides every step', B['l'], DIM)
    rob = clip_frames(REN / 'r17/wok_sink.mp4', (0, 40, 960, 540), 0, 32, 150, 1400, 729)
    section(out, 6, bg, [(rob, (260, 330))])
    # 2 scenario
    bg, dr = base('1 · The scenario', 'Dinner for a family, in an ordinary home kitchen')
    bg.paste(still(M / 'kitchen.jpg', 1500, 656), (80, 200))
    y = 260
    for head, txt in [('You', 'load groceries, press start'), ('Robot', 'preps, cooks, plates'), ('You', 'serve')]:
        tdraw(dr, (1620, y), head, D['m'], COP); tdraw(dr, (1620, y + 46), txt, B['b'], INK); y += 150
    section(out, 9, bg, [])
    # 3 setup
    grid_section(out, 16, '2 · The setup', 'One arm, and appliances that do the precise work', [
        (M / 'robot.jpg', 'Robot', 'UR5e on a tethered cart', 'still'),
        (M / 'wok_station.jpg', 'Wok', '3.5 kW induction + cameras', 'still'),
        (M / 'station.jpg', 'Seasoning station', 'doses into cups', 'still'),
        (G / 'fridge_arm.gif', 'Fridge', 'opened by the arm', 'anim'),
        (G / 'faucet_lever.gif', 'Faucet', 'lever lifted by the arm', 'anim'),
        (M / 'drum.jpg', 'Pour drum', 'under review', 'still'),
    ], th=330, caption_h=80, top=170)
    # 4 tools
    bg, dr = base('3 · Prep tools', 'Appliances do the cutting; the arm loads them and pulls the lever')
    car, tom = anim(G / 'carrot_prep.gif', 250, 860, 474), anim(G / 'tomato_prep.gif', 250, 860, 474)
    tile(dr, 80, 720, 860, 'Slicer: slices · shreds · dice', 'carrot chain checked', OK)
    tile(dr, 1000, 720, 860, 'Lever cutter: wedges · dice', 'tomato chain checked', OK)
    section(out, 11, bg, [(car, (80, 220)), (tom, (1000, 220))])
    # 5 small steps
    grid_section(out, 22, '4 · Small steps', 'Each arm motion is one continuous, collision-checked path', [
        (G / 'stir_arm.gif', 'Stir-fry', '5 strokes', 'anim'),
        (G / 'cup_pour.gif', 'Seasoning cup', 'built today', 'anim'),
        (G / 'bowl_pour.gif', 'Bowl pour', 'built today', 'anim'),
        (G / 'spatula_rest.gif', 'Spatula fetch', '26.9 s', 'anim'),
        (G / 'wok_plate_rinse.gif', 'Plate + rinse', '48.9 s', 'anim'),
        (G / 'spider.gif', 'Spider', 'scoop + drain', 'anim'),
    ], th=330, caption_h=80, top=170)
    # 6 routines
    bg, dr = base('5 · Why routines', 'The stove doesn\'t wait while Claude thinks')
    tdraw(dr, (80, 230), '~10 s per decision → starch went lumpy', B['l'], INK)
    tdraw(dr, (80, 285), 'Fix: 57 predefined routines that run without a pause', B['l'], DIM)
    y = 420
    for row, col in [(('Real-time run', 'Decisions', 'Thinking', 'Checks'), DIM), (('Single skills', '41', '798 s', '6/7 lumps'), INK),
                     (('With routines', '25', '252 s', '7/7'), OK)]:
        for j, v in enumerate(row):
            tdraw(dr, (80 + j * 220, y), v, B['l'] if col != DIM else F['sb'], col)
        dr.line((80, y + 46, 960, y + 46), fill=LINE, width=2); y += 64
    gif = anim(G / 'routines/drum_add_stir.gif', 200, 860, 381)
    section(out, 11, bg, [(gif, (990, 230))])
    # 7 one dish: the shortened demo video, then the score card
    bg, dr = base('6 · One dish, start to finish', 'Tomato & egg stir-fry, in real time: Claude decides, routines run')
    section(out, 3, bg, [])
    out.close()
    return out.n


if __name__ == '__main__':
    print(main(sys.argv[1]) / FPS, 's')


def end(path):
    out = Out(path)
    bg, dr = base('7 · Where it stands', 'Proven in simulation. A real home is the next, bigger step.')
    y = 240
    for big, txt in [('Checked', 'every motion is a collision-checked path'),
                     ('Not yet', 'nothing bought · 146 gaps tracked as issues'),
                     ('Next', 'cook two meals by hand, the robot\'s way'),
                     ('Built with', 'Claude Code: two sessions, one GitHub issue board')]:
        tdraw(dr, (80, y), big, D['m'], COP); y = wrap(dr, (360, y + 4), txt, B['l'], INK, 1440, 42) + 34
    tdraw(dr, (80, 900), 'github.com/guoyuanjing2988/home-cooking-robot', B['l'], STEEL)
    section(out, 7, bg, [])
    out.close()
