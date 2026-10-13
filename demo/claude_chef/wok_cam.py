"""Hood colour camera looking into the wok, rendered by MuJoCo from cook_model.Wok.truth().
The food's appearance encodes the hidden state (no text in the image):
 - oil: thin glossy film; ripples above ~160 °C, faint grey-blue wisps from the smoke point (~195 °C);
 - egg: raw = glossy deep-yellow liquid; it sets opaque bright yellow from the edges inward as the face on
   the steel sets (set_down) and in patches as the top sets (set_up); the steel face's browning shows as a
   lacy golden-to-black rim, the visible face's browning (after a flip) as spots; stirred = curds;
 - tomato wedges: glossy red, sharp-edged with seeds when raw; slump, round off, darken as `soft` rises;
 - sauce: translucent pool coloured by juice/ketchup; boiling = many small bubbles; with `thick` it turns
   opaque and glossy, clings (smaller pool, raised edge), bubbles get fewer and bigger, wedges get coated.
Geometry: wok = spherical cap of sphere radius 0.20 m, rim radius 0.17 m (spatula15.py), frame origin at
the inner bottom point. Camera: under the hood front, above and slightly in front of the wok (R15 design)."""
from __future__ import annotations
import io, math, sys, time
import numpy as np
import mujoco
from PIL import Image
from scipy.ndimage import gaussian_filter
from cook_model import RS, A_RIM, DEPTH, pool_radius, cap_depth

CAM_POS, CAM_LOOK, FOVY = np.array([0., -.24, .57]), np.array([0., .012, .03]), 36.
OFF = .0012                                   # food sits on a thin oil layer


def surf(x, y):
    return RS - np.sqrt(np.maximum(RS**2 - x * x - y * y, 0.))


def normal(x, y):
    n = np.array([-x, -y, RS - surf(x, y)]); return n / np.linalg.norm(n)


def rot_to(n):
    """Rotation taking +z to unit n."""
    z = np.array([0, 0, 1.]); v = np.cross(z, n); c = z @ n
    if np.linalg.norm(v) < 1e-9: return np.eye(3)
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + K + K @ K / (1 + c)


def rotz(a):
    c, s = math.cos(a), math.sin(a); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.]])


def rotx(a):
    c, s = math.cos(a), math.sin(a); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def unoise(rng, n, sigma):
    """Smooth noise rank-normalised to uniform [0,1], n x n."""
    a = gaussian_filter(rng.standard_normal((n, n)), sigma, mode='wrap').ravel()
    out = np.empty_like(a); out[np.argsort(a)] = np.linspace(0, 1, a.size); return out.reshape(n, n)


def lerp(a, b, t):
    """a..b by t; a 2-D t is an image mask (gets a colour axis)."""
    t = np.asarray(t, float); t = t[..., None] if t.ndim == 2 else t
    return np.asarray(a, float) * (1 - t) + np.asarray(b, float) * t


def grid_faces(nu, nv, wrap=False):
    F = []
    for i in range(nu - 1):
        for j in range(nv if wrap else nv - 1):
            a, b, c, d = i * nv + j, (i + 1) * nv + j, (i + 1) * nv + (j + 1) % nv, i * nv + (j + 1) % nv
            F += [(a, b, c), (a, c, d)]
    return np.array(F)


class Scene:
    """Collects textures, materials, meshes and geoms into one MJCF string."""

    def __init__(self):
        self.assets, self.ax, self.gx, self.n = {}, [], [], 0

    def tex(self, name, img):
        b = io.BytesIO(); Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(b, 'PNG')
        self.assets[name + '.png'] = b.getvalue()
        self.ax.append(f'<texture name="{name}" type="2d" file="{name}.png"/>')

    def mat(self, name, rgba=(1, 1, 1, 1), tex=None, spec=.3, shin=.3, emis=0.):
        if any(x.startswith(f'<material name="{name}"') for x in self.ax): return
        t = f' texture="{tex}"' if tex else ''
        self.ax.append(f'<material name="{name}" rgba="{" ".join(f"{x:.3f}" for x in rgba)}"{t} specular="{spec:.2f}" shininess="{shin:.2f}" emission="{emis:.2f}"/>')

    def mesh(self, V, F, UV=None, mat=None):
        self.n += 1; nm = f'm{self.n}'
        uv = '' if UV is None else ' texcoord="' + ' '.join(f'{x:.4f}' for x in np.asarray(UV).ravel()) + '"'
        self.ax.append(f'<mesh name="{nm}" inertia="legacy" vertex="{" ".join(f"{x:.5f}" for x in np.asarray(V).ravel())}" '
                       f'face="{" ".join(str(int(x)) for x in np.asarray(F).ravel())}"{uv}/>')
        self.gx.append(f'<geom type="mesh" mesh="{nm}" material="{mat}" contype="0" conaffinity="0"/>')

    def geom(self, s):
        self.gx.append(s.replace('<geom ', '<geom contype="0" conaffinity="0" ', 1))

    def xml(self, w, h):
        f = CAM_LOOK - CAM_POS; f /= np.linalg.norm(f); r = np.cross(f, [0, 0, 1.]); r /= np.linalg.norm(r); u = np.cross(r, f)
        cam = (f'<camera name="hood" pos="{" ".join(map(str, CAM_POS))}" fovy="{FOVY}" '
               f'xyaxes="{" ".join(f"{x:.5f}" for x in np.r_[r, u])}"/>')
        return (f'<mujoco><compiler angle="radian"/><visual><global offwidth="{max(w, 640)}" offheight="{max(h, 480)}"/>'
                '<quality shadowsize="4096" offsamples="8"/><headlight ambient=".20 .18 .15" diffuse=".16 .15 .13" specular=".05 .05 .05"/>'
                '<map znear=".01" zfar="20"/></visual>'
                f'<asset>{"".join(self.ax)}</asset><worldbody>'
                '<light pos="-.10 -.16 .66" dir=".12 .2 -1" diffuse=".80 .66 .48" specular=".55 .48 .38" cutoff="60" exponent="1" castshadow="false"/>'
                '<light pos=".16 .06 .64" dir="-.18 -.05 -1" diffuse=".50 .42 .32" specular=".30 .26 .2" cutoff="60" exponent="2" castshadow="false"/>'
                f'{cam}{"".join(self.gx)}</worldbody></mujoco>')


# ---------------------------------------------------------------- static kitchen
def _wok_tex(rng, n=512):
    yy, xx = np.mgrid[0:n, 0:n]; x = (xx / (n - 1) - .5) * .36; y = (yy / (n - 1) - .5) * .36
    r = np.hypot(x, y); th = np.arctan2(y, x)
    base = np.ones((n, n, 3)) * [30, 29, 28]
    streak = gaussian_filter(rng.standard_normal((n, n)), (0.6, 6))   # spun tool marks (mostly circumferential in image space -> approx)
    rings = np.sin(r * 900 + gaussian_filter(rng.standard_normal((n, n)), 8) * 6) * 2.5
    pat = unoise(rng, n, 18)
    seasoned = np.clip(1 - r / .13, 0, 1)[..., None]
    img = base + streak[..., None] * 3 + rings[..., None]
    img = lerp(img, img * [1.25, 1.0, .82], seasoned * (.5 + .5 * pat[..., None]))            # brown seasoned centre
    blue = np.clip(1 - np.abs(r - .115) / .03, 0, 1)[..., None] * (pat[..., None] > .55)
    img = lerp(img, [38, 40, 52], blue * .6)                                                    # heat tint ring
    img = lerp(img, [92, 90, 86], np.clip((r - .162) / .006, 0, 1)[..., None])                  # bare steel at the rim
    img += rng.normal(0, 2.5, (n, n, 1))
    return img


def kitchen(S, rng):
    S.tex('wok', _wok_tex(rng)); S.mat('wok', (1, 1, 1, 1), 'wok', spec=.45, shin=.55)
    nr, nt = 44, 120
    rr = np.linspace(0, A_RIM, nr); tt = np.linspace(0, 2 * np.pi, nt, endpoint=False)
    R, T = np.meshgrid(rr, tt, indexing='ij'); X, Y = R * np.cos(T), R * np.sin(T); Z = surf(X, Y)
    V = np.c_[X.ravel(), Y.ravel(), Z.ravel()]; UV = np.c_[.5 + X.ravel() / .36, .5 + Y.ravel() / .36]
    S.mesh(V, grid_faces(nr, nt, True), UV, 'wok')
    # rolled rim and outer skin
    S.mat('steel', (.42, .41, .40, 1), spec=.8, shin=.7)
    a = np.linspace(0, 2 * np.pi, 13); P = []
    for t in tt:
        for b in a[:-1]:
            P.append([(A_RIM + .0035 + .0035 * math.cos(b)) * math.cos(t), (A_RIM + .0035 + .0035 * math.cos(b)) * math.sin(t), DEPTH + .0035 * math.sin(b)])
    S.mesh(np.array(P), _torus_faces(nt, 12), None, 'steel')
    S.mat('glass', (.035, .035, .04, 1), spec=.9, shin=.95)
    # cooker: glass top frame around a square opening (under the rim), dark bowl below the wok
    for x, y, sx, sy in ((0, .1825, .215, .0325), (0, -.1825, .215, .0325), (.1825, 0, .0325, .215), (-.1825, 0, .0325, .215)):
        S.geom(f'<geom type="box" pos="{x} {y} -.01" size="{sx} {sy} .055" material="glass"/>')
    S.geom('<geom type="box" pos="0 0 -.03" size=".15 .15 .025" rgba=".02 .02 .02 1"/>')
    # grip handle (R15: short handle, keyed block at 0.235 m), left side
    S.geom(f'<geom type="capsule" fromto="{-A_RIM:.3f} 0 {DEPTH - .004:.3f} -.228 0 {DEPTH + .012:.3f}" size=".008" material="steel"/>')
    S.geom(f'<geom type="box" pos="-.24 0 {DEPTH + .014:.3f}" size=".016 .02 .012" rgba=".12 .12 .13 1"/>')
    # counter, backsplash
    S.tex('granite', _granite(rng)); S.mat('granite', (1, 1, 1, 1), 'granite', spec=.3, shin=.4)
    S.geom('<geom type="box" pos="0 0 -.065" size=".9 .6 .01" material="granite"/>')
    S.mat('tile', (.88, .86, .82, 1), spec=.4, shin=.5)
    S.geom('<geom type="box" pos="0 .52 .3" size=".9 .01 .4" material="tile"/>')
    for k, x in enumerate((-.12, 0, .12)):
        S.geom(f'<geom type="cylinder" pos="{x} -.205 .048" size=".012 .006" rgba=".55 .55 .56 1"/>')


def _granite(rng, n=256):
    a = gaussian_filter(rng.standard_normal((n, n)), 1.2); b = rng.random((n, n)) > .985
    img = np.ones((n, n, 3)) * [88, 84, 80] + a[..., None] * 16
    img[b] = [170, 165, 158]; return img


def _torus_faces(nt, na):
    F = []
    for i in range(nt):
        for j in range(na):
            a, b = i * na + j, ((i + 1) % nt) * na + j
            c, d = ((i + 1) % nt) * na + (j + 1) % na, i * na + (j + 1) % na
            F += [(a, b, c), (a, c, d)]
    return np.array(F)


# ---------------------------------------------------------------- oil, smoke, bubbles
def oil(S, tr, rng, has_food):
    T = tr['T_wok']; g = tr['oil_g']; film = tr['film_g']
    if g + film < 2 or (tr.get('sauce') and tr['sauce']['liquid_g'] >= 20): return
    pool = g >= 2 and not has_food                             # food displaces it into a thin film
    S.mat('oil', (.42, .26, .05, (.12 if pool else .05) if g >= 2 else .06), spec=1., shin=1.)   # dark amber: any bright tint dominates the black steel
    rad = min(max(pool_radius((g / .92) / 1e6), .03) * 1.25, .15) if pool else .125
    lvl = cap_depth((g / .92) / 1e6) if pool else 0.
    ripple = .0003 * np.clip((T - 150) / 40, 0, 1.5)
    nr, nt = 16, 72; rr = np.linspace(0, rad, nr); tt = np.linspace(0, 2 * np.pi, nt, endpoint=False)
    Rg, Tg = np.meshgrid(rr, tt, indexing='ij'); X, Y = Rg * np.cos(Tg), Rg * np.sin(Tg)
    ph = rng.random(3) * 6.3
    Z = np.maximum(surf(X, Y) + .0004, lvl + .0003) + ripple * (np.sin(X * 300 + ph[0]) * np.sin(Y * 260 + ph[1]) + np.sin((X + Y) * 410 + ph[2]))
    S.mesh(np.c_[X.ravel(), Y.ravel(), Z.ravel()], grid_faces(nr, nt, True), None, 'oil')
    if g >= 2 and T > 160 and not has_food:                 # shimmer: wavy bright streaks on the oil
        S.mat('shim', (1, .9, .7, .22), spec=1, shin=1, emis=.2)
        for _ in range(int(np.clip((T - 160) / 4, 3, 12))):
            r, a = rad * .85 * math.sqrt(rng.random()), rng.random() * 6.3
            x, y = r * math.cos(a), r * math.sin(a); z = max(surf(x, y), lvl) + .0008
            S.geom(f'<geom type="ellipsoid" pos="{x:.4f} {y:.4f} {z:.4f}" size="{.003 + .005 * rng.random():.4f} .0012 .0001" '
                   f'euler="0 0 {rng.random() * 3.14:.3f}" material="shim"/>')
    if T > 195 and g + film >= 2:
        smoke(S, rng, int(np.clip((T - 185) / 8, 2, 8)), .07)


def smoke(S, rng, n, spread, steam=False):
    """n rising plumes of faint overlapping puffs (grey-blue oil smoke, or white steam)."""
    nm = 'steam' if steam else 'smoke'
    S.mat(nm, (1, 1, 1, .02) if steam else (.86, .88, .94, .045), spec=0, shin=0, emis=.6)
    for _ in range(n):
        r, a = spread * math.sqrt(rng.random()), rng.random() * 6.3
        x, y = r * math.cos(a), r * math.sin(a); z = surf(x, y) + .01
        dx, dy = rng.normal(0, .25, 2)
        for k in range(9):
            q = .006 + .003 * k
            S.geom(f'<geom type="sphere" pos="{x:.4f} {y:.4f} {z:.4f}" size="{q:.4f}" material="{nm}"/>')
            z += .014 + .004 * k; x += dx * .012 + rng.normal(0, .004); y += dy * .012 + rng.normal(0, .004)


# ---------------------------------------------------------------- egg
def brown_col(b):
    b = np.clip(b, 0, 1)
    k = np.array([0, .15, .4, .65, .85, 1.]); C = np.array([[252, 214, 72], [232, 168, 60], [190, 112, 38], [110, 60, 25], [45, 30, 20], [22, 18, 16]], float)
    return np.stack([np.interp(b, k, C[:, i]) for i in range(3)], -1)


def egg_tex(e, rng, outline, n=192, curd=False):
    yy, xx = np.mgrid[0:n, 0:n]; x = (xx / (n - 1) - .5) * 2.6; y = (yy / (n - 1) - .5) * 2.6
    rho = np.hypot(x, y) / outline(np.arctan2(y, x))
    sd, su, bd, bu = e['set_down'], e['set_up'], e['brown_down'], e['brown_up']
    if curd: sd, su = max(sd, su), max(sd, su)               # stirred: both faces mixed into the curds
    n1, n2, n3, n4 = unoise(rng, n, 9), unoise(rng, n, 3), unoise(rng, n, 5), unoise(rng, n, 2)
    front = 1 - .72 * sd                                     # edges set first (thin, and the steel face sets through)
    ring = np.clip((rho - front) / .1 + .7 * (n1 - .5), 0, 1) * (sd > .04)
    patch = np.clip((su - n1) / .12 + .5, 0, 1)
    s = np.maximum(ring, patch)
    raw = np.array([236, 172, 46.]) * (.94 + .08 * n2[..., None])
    setc = np.array([255, 236, 128.]) * (.86 + .16 * n1[..., None] ** .5) * (.96 + .05 * n2[..., None])   # puffy, mottled
    img = lerp(raw, setc, s ** .8)
    img = lerp(img, [250, 244, 222], ((n4 > .86) * s * .55))                       # set white streaks
    img = lerp(img, (img + [255, 236, 170]) / 2, np.clip((s - .2) * (1 - s) * 2.2, 0, 1) * .5)   # cloudy setting front
    spots = np.clip((bu * 1.25 - n3) / .12 + .5, 0, 1) * np.clip(su * 1.4, 0, 1)
    img = lerp(img, brown_col(np.clip(bu * (.75 + .5 * n2), 0, 1)), spots * min(1, bu * 3.5))
    w = .05 + .16 * bd
    rim = np.clip((rho - (1 - w)) / .04 + .4 * (n3 - .5), 0, 1)
    img = lerp(img, brown_col(np.clip(bd * (.8 + .45 * n2), 0, 1)), rim * min(1, bd * 4))
    return img


def egg_piece(S, e, rng, cx, cy, R0, k, curd, lift=0.):
    amps = rng.normal(0, 1, 8) * [.06, .045, .03, .022, .016, .012, .01, .008] * (1.6 if curd else 1); ph = rng.random(8) * 6.3
    def outline(t):
        return 1 + sum(amps[i] * np.cos((i + 2) * t + ph[i]) for i in range(8))
    S.tex(f'egg{k}', egg_tex(e, rng, outline, curd=curd))
    sd, su = (max(e['set_down'], e['set_up']),) * 2 if curd else (e['set_down'], e['set_up'])
    sv = max(su, .7 * sd)
    S.mat(f'egg{k}', (1, 1, 1, 1), f'egg{k}', spec=.7 - .55 * sv, shin=.85 - .6 * sv)
    nr, nt = 14, 72; rr = np.linspace(0, 1, nr); tt = np.linspace(0, 2 * np.pi, nt, endpoint=False)
    rot = rng.random() * 6.3
    P, UV = [], []
    bump = gaussian_filter(rng.standard_normal((nr, nt)), (1.2, 2.5), mode='wrap'); bump /= bump.std() + 1e-9
    th = .0022 + .0028 * sv
    for i, r in enumerate(rr):
        for j, t in enumerate(tt):
            rad = R0 * outline(t) * r
            lx, ly = rad * math.cos(t), rad * math.sin(t)
            x, y = cx + lx * math.cos(rot) - ly * math.sin(rot), cy + lx * math.sin(rot) + ly * math.cos(rot)
            h = th * (1 - r**6)**.5 + .0018 * sv * bump[i, j] * (1 - r**4) * min(1, 3 * r) + .004 * e['brown_down'] * max(0, r - .85) / .15 * (not curd)
            P.append([x, y, surf(x, y) + OFF + max(h, .0004) + lift]); UV.append([.5 + lx / R0 / 2.6, .5 + ly / R0 / 2.6])
    # skirt down to the steel
    for t in tt:
        rad = R0 * outline(t); lx, ly = rad * math.cos(t), rad * math.sin(t)
        x, y = cx + lx * math.cos(rot) - ly * math.sin(rot), cy + lx * math.sin(rot) + ly * math.cos(rot)
        P.append([x, y, surf(x, y) + OFF * .5 + lift]); UV.append([.5 + lx / R0 / 2.6, .5 + ly / R0 / 2.6])
    S.mesh(np.array(P), grid_faces(nr + 1, nt, True), np.array(UV), f'egg{k}')
    if not curd and sv < .65 and lift == 0:                   # wet glaze over the still-raw centre
        front = 1 - .72 * e['set_down']; a = .25 * (1 - sv / .65)
        S.mat(f'glz{k}', (1., .9, .6, a), spec=1., shin=1.)
        gr = np.linspace(0, front * .95, 8); P = []
        for r in gr:
            for t in tt:
                rad = R0 * outline(t) * r; lx, ly = rad * math.cos(t), rad * math.sin(t)
                x, y = cx + lx * math.cos(rot) - ly * math.sin(rot), cy + lx * math.sin(rot) + ly * math.cos(rot)
                P.append([x, y, surf(x, y) + OFF + th * (1 - (r)**6)**.5 + .0006])
        S.mesh(np.array(P), grid_faces(len(gr), nt, True), None, f'glz{k}')
    return outline, rot


def egg(S, tr, rng, others):
    e = tr['egg']; npc = int(min(e['pieces'], 12))
    in_sauce = e['in_sauce_s'] > 0 or bool(tr.get('tomato'))
    curd = npc > 4 or in_sauce
    if npc == 1 and not in_sauce:
        cx, cy = rng.normal(0, .008, 2)
        R0 = .094 * (e['g'] / 150) ** .5
        outline, rot = egg_piece(S, e, rng, cx, cy, R0, 0, False)
        if tr['T_wok'] > 105 and e['set_down'] < .97 and tr['oil_g'] > 2:    # sizzle along the edge
            S.mat('fizz', (1, .97, .85, .6), spec=.8, shin=.8)
            for _ in range(int(np.clip((tr['T_wok'] - 100) * 1.2, 4, 60))):
                a = rng.random() * 6.3; r = R0 * outline(a) * (1.02 + .05 * rng.random())
                x, y = cx + r * math.cos(a + rot), cy + r * math.sin(a + rot)
                S.geom(f'<geom type="sphere" pos="{x:.4f} {y:.4f} {surf(x, y) + .001:.4f}" size="{.0008 + .0013 * rng.random():.4f}" material="fizz"/>')
        return [(cx, cy, .094)]
    n = max(npc, 6 if in_sauce else npc)
    placed = []
    R0 = .094 * (e['g'] / 150) ** .5 / math.sqrt(n) * (1.1 if curd else 1.25)
    for k in range(n):
        for _ in range(200):
            r, a = .10 * math.sqrt(rng.random()), rng.random() * 6.3
            x, y = r * math.cos(a), r * math.sin(a)
            if all(math.hypot(x - px, y - py) > R0 * 1.25 + pr * .5 for px, py, pr in placed + others): break
        egg_piece(S, e, rng, x, y, R0 * (.8 + .4 * rng.random()), k, curd, lift=.004 if in_sauce else 0.)
        placed.append((x, y, R0))
    return placed


# ---------------------------------------------------------------- tomato
def tomato_tex(t, rng, n=256):
    sf = t['soft']; img = np.zeros((n, n, 3))
    yy, xx = np.mgrid[0:n, 0:n / 2]
    nn = unoise(rng, n, 6)[:, :n // 2]
    skin = np.array([212, 28, 18.]) * (.92 + .14 * nn[..., None])
    skin = lerp(skin, np.array([150, 32, 14.]) * (.8 + .35 * nn[..., None]), sf ** .8)
    img[:, :n // 2] = skin
    s = xx / (n / 2 - 1); v = yy / (n - 1)                     # cut face: s 0 axis -> 1 skin, v along the stem axis
    wall = np.array([226, 52, 34.]); gel = np.array([238, 150, 70.]); core = np.array([238, 128, 108.])
    face = np.where((s > .74)[..., None], wall, np.where((s < .28)[..., None], core, gel))
    loc = (s > .30) & (s < .72) & (np.abs(np.sin(v * np.pi * 3)) > .25)
    face = np.where(loc[..., None], face, wall * .97)
    seeds = np.zeros((n, n // 2))
    for _ in range(int(60 * (1 - .7 * sf))):
        sx, sy = .33 + .36 * rng.random(), rng.random()
        seeds += np.exp(-(((s - sx) / .035)**2 + ((v - sy) / .018)**2))
    face = lerp(face, [240, 224, 150], np.clip(seeds, 0, 1) * (1 - sf) ** 2)
    face *= (.94 + .1 * unoise(rng, n, 3)[:, :n // 2])[..., None]
    face = lerp(face, np.array([196, 46, 22.]) * (.85 + .25 * nn[..., None]), np.clip(sf * 1.15, 0, 1))
    img[:, n // 2:] = face
    return img


def wedge(rt, na=6, nf=16, ns=5):
    """One 1/8 tomato wedge (stem axis = z). Returns V, F, UV (skin left half, cut faces right half of the atlas)."""
    a0 = math.pi / 8; P, UV, F = [], [], []
    phis = np.linspace(.02, math.pi - .02, nf)
    def add_grid(pts, uvs, nu, nv, flip=False):
        b = len(P); P.extend(pts); UV.extend(uvs)
        for f in grid_faces(nu, nv):
            F.append(tuple(b + f[::-1]) if flip else tuple(b + f))
    pts, uvs = [], []
    for p in phis:
        for a in np.linspace(-a0, a0, na):
            pts.append([rt * math.sin(p) * math.cos(a), rt * math.sin(p) * math.sin(a), rt * math.cos(p)]); uvs.append([.02 + .45 * (a + a0) / (2 * a0), p / math.pi])
    add_grid(pts, uvs, nf, na)
    for sgn in (-1, 1):
        pts, uvs = [], []
        for p in phis:
            for s in np.linspace(0, 1, ns):
                pts.append([s * rt * math.sin(p) * math.cos(sgn * a0), s * rt * math.sin(p) * math.sin(sgn * a0), rt * math.cos(p)])
                uvs.append([.5 + .49 * s, p / math.pi])
        add_grid(pts, uvs, nf, ns, flip=sgn > 0)
    return np.array(P), np.array(F), np.array(UV)


def tomato(S, tr, rng, others):
    t = tr['tomato']; sf = t['soft']
    S.tex('tom', tomato_tex(t, rng))
    wet = tr.get('sauce') and tr['sauce']['liquid_g'] > 30
    S.mat('tom', (1, 1, 1, 1), 'tom', spec=.65 - .25 * sf + (.25 if wet else 0), shin=.75 - .2 * sf + (.2 if wet else 0))
    nw = int(round(16 * t['g0'] / 300)); scale = (t['g'] / t['g0']) ** (1 / 3)
    rt = .033 * scale
    thick = tr['sauce']['thick'] if tr.get('sauce') else 0.
    if thick > .25:
        sc = sauce_col(tr['sauce'])
        S.mat('coat', (*sc[:3], .35 + .45 * thick), spec=1, shin=1)
    placed = []
    for k in range(nw):
        for _ in range(300):
            r, a = .105 * math.sqrt(rng.random()), rng.random() * 6.3
            x, y = r * math.cos(a), r * math.sin(a)
            if all(math.hypot(x - px, y - py) > .030 * scale * (1 + .3 * sf) for px, py, _ in placed): break
        V, F, UV = wedge(rt)
        V = V - [rt * .55, 0, 0]
        # lie down: stem axis horizontal; skin down (spine up) or on a cut face
        V = V @ np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0.]]).T              # z(stem) -> x
        roll = (0., 5 * math.pi / 8, -5 * math.pi / 8)[int(rng.integers(3))] + rng.normal(0, .1)   # skin down (spine up) or on a cut face
        V = V @ rotx(roll).T
        # soften: round toward a flattened blob, slump, lumps
        c = V.mean(0); D = V - c
        if sf > 0:
            d = D / (np.linalg.norm(D, axis=1, keepdims=True) + 1e-9)
            ax = np.array([rt * .95, rt * .55, rt * .5])
            blob = d / np.sqrt(((d / ax)**2).sum(1, keepdims=True))
            D = D * (1 - .85 * sf) + blob * .85 * sf
            D[:, 2] *= 1 - .5 * sf; D[:, :2] *= 1 + .2 * sf
            kd = rng.normal(0, 1, (2, 3)); ph2 = rng.random(2) * 6.3                     # lumpy, lost shape
            D *= (1 + .2 * sf * (np.sin(D @ kd[0] * 160 + ph2[0]) + .6 * np.sin(D @ kd[1] * 260 + ph2[1])))[:, None]
        D = D @ rotz(rng.random() * 6.3).T
        parts = [(D, x, y)]
        if rng.random() < np.clip((sf - .5) * 2.2, 0, .85):  # very soft wedges fall apart into mushy halves
            off = rng.normal(0, 1, 2); off = .012 * off / np.linalg.norm(off)
            parts = [(D * [.72, .72, .8] @ rotz(rng.normal(0, .8)).T, x + off[0] * sgn, y + off[1] * sgn) for sgn in (-1, 1)]
        for D_, x_, y_ in parts:
            V = D_ @ rot_to(normal(x_, y_)).T + [x_, y_, 0]
            V[:, 2] += OFF - (V[:, 2] - surf(V[:, 0], V[:, 1])).min()        # rest on the steel
            S.mesh(V, F, UV, 'tom')
            if thick > .25:
                S.mesh(V + (V - V.mean(0)) * .06, F, None, 'coat')
        placed.append((x, y, .03))
    if sf > .3:                                              # broken-down pulp and loose curled skins in the wok
        S.mat('pulp', (.80, .15, .06, 1), spec=.7, shin=.7); S.mat('skin', (.88, .26, .12, 1), spec=.5, shin=.5)
        for k in range(int(70 * (sf - .3))):
            r, a = .10 * math.sqrt(rng.random()), rng.random() * 6.3; x, y = r * math.cos(a), r * math.sin(a)
            q = .003 + .005 * rng.random(); skin = k % 3 == 0
            sz = f'{q * 1.8:.4f} {q * .5:.4f} .0007' if skin else f'{q:.4f} {q * (.6 + .4 * rng.random()):.4f} {q * .35:.4f}'
            S.geom(f'<geom type="ellipsoid" pos="{x:.4f} {y:.4f} {surf(x, y) + .003 + .003 * rng.random():.4f}" size="{sz}" '
                   f'euler="{rng.normal(0, .5):.3f} {rng.normal(0, .5):.3f} {rng.random() * 6.3:.3f}" material="{"skin" if skin else "pulp"}"/>')
    return placed


# ---------------------------------------------------------------- sauce
def sauce_col(s):
    L = max(s['liquid_g'], 1e-6)
    red = np.clip((s['juice_g'] + 8 * s['ketchup_g']) / (L + 8 * s['ketchup_g']), 0, 1) ** .7
    th = s['thick']
    thin = lerp([.62, .48, .42], [.96, .26, .08], red); a_thin = .10 + .55 * red
    col = lerp(thin, [.80, .13, .03], th ** .8); a = a_thin + (.9 - a_thin) * th ** .7
    return np.r_[col, a]


def sauce(S, tr, rng, has_tom):
    s = tr['sauce']; L = s['liquid_g']
    if L < 3 and s['scorch'] < .1: return
    th = s['thick']; c = sauce_col(s)
    if s['scorch'] > .1: c[:3] = lerp(c[:3], [.18, .08, .04], min(1, s['scorch']))
    S.mat('sauce', c, spec=.55 + .45 * th + (.2 if tr['glaze_g'] > 0 else 0), shin=.6 + .4 * th)
    rad = max(s['pool_r'], .035) * (1 - .22 * th)
    lvl = cap_depth(L * (.55 if has_tom else 1) / 1e6) + .001 if L > 20 else surf(rad, 0)   # drawn low so the food pokes out (camera cue, not physics)
    dome = .0006 + .003 * th
    nr, nt = 18, 72; rr = np.linspace(0, 1, nr); tt = np.linspace(0, 2 * np.pi, nt, endpoint=False)
    wob = 1 + .06 * th * np.sin(tt[None, :] * 3 + rng.random() * 6) + .04 * np.sin(tt[None, :] * 5 + rng.random() * 6)
    Rg, Tg = np.meshgrid(rr, tt, indexing='ij'); Rr = Rg * rad * wob
    X, Y = Rr * np.cos(Tg), Rr * np.sin(Tg)
    prof = dome * (1 - Rg**8) ** .5 if th > .2 else dome * (1 - Rg**2)
    Z = np.maximum(np.maximum(lvl, surf(X, Y)) + .0004 + prof * (lvl > 0), surf(X, Y) + .0005)
    S.mesh(np.c_[X.ravel(), Y.ravel(), Z.ravel()], grid_faces(nr, nt, True), None, 'sauce')
    # bubbles
    T = s['T']; boil = s['boiling']
    if L > 10 and (boil or T > 88):
        if th < .45:
            nb = int((55 if boil else 6) * (1 - th)); rb = (.0012, .0028); col = (1, .93, .88, .55)
        else:
            nb = int(6 + 6 * rng.random()) if boil else 2; rb = (.0035, .0065); col = (*np.clip(c[:3] * 1.35, 0, 1), .9)
        S.mat('bub', col, spec=1, shin=1)
        for _ in range(nb):
            r, a = rad * (.92 * math.sqrt(rng.random()) if boil else .8 + .15 * rng.random()), rng.random() * 6.3
            x, y = r * math.cos(a), r * math.sin(a); rr_ = rb[0] + (rb[1] - rb[0]) * rng.random()
            z = max(lvl, surf(x, y)) + .0004 + dome * (1 - min(1, r / rad)**8) ** .5
            S.geom(f'<geom type="ellipsoid" pos="{x:.4f} {y:.4f} {z - .3 * rr_:.4f}" size="{rr_:.4f} {rr_:.4f} {rr_ * .7:.4f}" material="bub"/>')
        if boil: smoke(S, rng, 5, .07, steam=True)
    if tr['glaze_g'] > 0:                                    # 明油 droplets
        S.mat('glazeoil', (1, .78, .3, .55), spec=1, shin=1)
        for _ in range(int(min(18, 3 * tr['glaze_g']))):
            r, a = rad * .9 * math.sqrt(rng.random()), rng.random() * 6.3; x, y = r * math.cos(a), r * math.sin(a)
            z = max(lvl, surf(x, y)) + dome + .0006; q = .003 + .005 * rng.random()
            S.geom(f'<geom type="ellipsoid" pos="{x:.4f} {y:.4f} {z:.4f}" size="{q:.4f} {q * .8:.4f} .0004" material="glazeoil"/>')


# ---------------------------------------------------------------- public
def build(tr, seed=0):
    rng = np.random.default_rng(seed)
    S = Scene(); kitchen(S, np.random.default_rng(12345))
    has_food = bool(tr.get('egg') or tr.get('tomato'))
    oil(S, tr, rng, has_food)
    if tr.get('sauce'): sauce(S, tr, rng, bool(tr.get('tomato')))
    placed = []
    if tr.get('tomato'): placed = tomato(S, tr, rng, [])
    if tr.get('egg'):
        placed += egg(S, tr, rng, placed)
        e = tr['egg']
        if max(e['brown_down'], e['brown_up']) > .55 and tr['T_wok'] > 150:   # burning food smokes too
            smoke(S, rng, int(4 + 10 * (max(e['brown_down'], e['brown_up']) - .55)), .08)
    return S


def render(wok_state_truth: dict, out_png: str, seed=0, size=(640, 480)):
    """Render the hood camera view of the wok for this truth() dict to out_png. Returns seconds taken."""
    t0 = time.time(); w, h = size
    S = build(wok_state_truth, seed)
    m = mujoco.MjModel.from_xml_string(S.xml(w, h), S.assets); d = mujoco.MjData(m); mujoco.mj_forward(m, d)
    r = mujoco.Renderer(m, h, w); r.update_scene(d, camera='hood'); img = r.render(); r.close()
    Image.fromarray(img).save(out_png)
    return time.time() - t0


# ---------------------------------------------------------------- canonical states + contact sheet
def canonical_states():
    """[(tag, label, truth)] from cook_model runs: the recipe at its key moments plus two abuse cases."""
    import cook_model as cm
    snaps = {}
    cm.run_recipe(log=lambda s: None, snap=lambda tag, w: snaps.__setitem__(tag, w.truth()))
    w = cm.Wok(); w.add('oil', 30); w.heat = .9
    while w.Tw < 205: w.step(.5)
    snaps['oil_smoking'] = w.truth()
    w = cm.Wok(); w.add('oil', 30); w.heat = .5
    while w.Tw < 122: w.step(.5)
    snaps['oil_120'] = w.truth()
    while w.Tw < 185: w.step(.5)
    snaps['oil_185'] = w.truth()
    w = cm.Wok(); w.add('oil', 30); w.heat = .8
    while w.Tw < 150: w.step(.5)
    w.add('egg', 150); w.heat = .37
    for _ in range(120): w.step(.5)
    w.flip('egg'); w.step(1.)
    snaps['egg_golden'] = w.truth()
    w = cm.Wok(); w.add('oil', 10); w.add('tomato', 300); w.add('ketchup', 5); w.add('water', 100); w.heat = .6
    while w.tom['soft'] < .9: w.step(.5, True)
    w.heat = 0.
    while w.sauce['T'] > 80: w.step(.5)
    snaps['tomato_soft_still'] = w.truth()
    w = cm.Wok(); w.add('oil', 30); w.heat = .8
    while w.Tw < 140: w.step(.5)
    w.add('egg', 150)
    for _ in range(140): w.step(.5)
    w.flip('egg'); w.step(1.)
    snaps['egg_burnt'] = w.truth()
    order = [('hot_empty', 'empty hot wok'), ('oil_120', 'oil at 120 °C'), ('oil_185', 'oil at 185 °C'), ('oil_smoking', 'oil past smoke point'), ('egg_raw', 'raw egg just poured'),
             ('egg_half', 'egg half set (40 s)'), ('egg_flip_ready', 'egg bottom set, ready to flip (60 s)'), ('egg_done', 'egg flipped, both sides set'),
             ('egg_golden', 'egg flipped, golden (medium heat)'), ('egg_burnt', 'egg burnt (high heat, flipped)'), ('tomato_raw', 'raw tomato wedges'), ('sauce_thin_boil', 'water in, thin sauce'), ('tomato_mid', 'tomato half soft (22 s simmer)'),
             ('tomato_soft', 'tomato softened, thin boiling sauce'), ('tomato_soft_still', 'tomato soft, heat off'), ('starch_in', 'starch water just added'), ('sauce_thick', 'sauce thickened'), ('final', 'eggs back, ready to plate')]
    return [(k, lab, snaps[k]) for k, lab in order]


def contact_sheet(out='out/wok_cam_states.png', size=(640, 480), cols=6):
    from PIL import ImageDraw, ImageFont
    import os
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    st = canonical_states(); tiles = []; times = []
    for i, (tag, lab, tr) in enumerate(st):
        p = f'{os.path.dirname(out) or "."}/wok_{tag}.png'; times.append(render(tr, p, seed=i, size=size)); tiles.append((lab, p))
    rows = (len(tiles) + cols - 1) // cols; W, H = size
    sheet = Image.new('RGB', (cols * W, rows * (H + 34)), (250, 250, 248)); dr = ImageDraw.Draw(sheet)
    try: font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 22)
    except OSError: font = ImageFont.load_default()
    for i, (lab, p) in enumerate(tiles):
        x, y = (i % cols) * W, (i // cols) * (H + 34)
        sheet.paste(Image.open(p), (x, y + 34)); dr.text((x + 8, y + 6), lab, fill=(20, 20, 20), font=font)
    sheet.save(out)
    print(out, f'render {np.mean(times):.2f} s/frame (max {max(times):.2f})')
    return st


if __name__ == '__main__':
    contact_sheet(*(sys.argv[1:2] or []))
