"""Hidden ground-truth wok model for the "Claude as chef" demo (西红柿炒蛋, Wang Gang).
Lumped thermal nodes + simple monotone kinetics; never shown to Claude (it only gets sensors() and
the wok_cam image). Thermal basis is heat15.py (robot_rail/sim/r10/claude):
 - power into the wok = 3.5 kW induction x 0.85 transfer = 2975 W at heat=1;
 - wok 1.5 kg carbon steel, cp 490; oil cp 2000; inner surface AW = 0.119 m^2 (cap, sphere R 0.20, rim 0.17);
 - losses: convection 10 W/m^2K + radiation (emissivity 0.8) from AW to air (30 °C, Singapore);
 - food contact conductance h_c ~300 W/m^2K (heat15's ASSUMED middle value).
Nodes: wok (steel + free oil), egg (two faces: the one on the steel and the one up), tomato
(surface layer 35 % of mass + core), sauce (free liquid = water + juice + ketchup + starch water).
A face or wet surface cannot pass 100 °C while it still has water (evaporation plateau, as heat15)."""
from __future__ import annotations
import copy, math
import numpy as np

TA = 30.; SIG = 5.67e-8
P_MAX = 3.5e3 * .85                       # heat15: induction 3.5 kW x 0.85
M_STEEL, CP_STEEL, CP_OIL = 1.5, 490., 2000.
RS, A_RIM = .20, .17
DEPTH = RS - math.sqrt(RS**2 - A_RIM**2)
AW = 2 * math.pi * RS * DEPTH             # 0.119 m^2, heat15's loss area
L_VAP = 2.26e6
CP_EGG, CP_TOM, CP_W = 3200., 3900., 4186.
H_FRY, H_DRY, H_LIQ, H_BOIL = 300., 120., 400., 1000.   # W/m^2K: food on oiled steel / dry steel / food in sauce / steel to liquid
A_EGG = .030                             # 150 g beaten egg as a ~5 mm sheet, ~20 cm across
H_EGG_IN = 110.                          # through the half thickness of a foamy setting egg (k ~0.3 W/mK over ~2.5 mm)
A_TOM = .048                             # 300 g of wedges (16 x ~19 g), whole surface
STARCH_FRAC = .15                        # starch water: ~5 g starch in 30 g
OIL_FILM_G = 3.                          # what stays on the steel after pouring out the 润锅 oil
LIQ_ITEMS = ('water', 'starch_water', 'ketchup', 'salt', 'sugar')
SOLIDS = ('egg', 'tomato')

# kinetics (per second); all of the form d x = k * f(T) * (1 - x) or a positive rate, so monotone
K_SET = .070      # egg protein setting at f=1; f ramps 62 -> 85 °C (whites set ~62-80, yolk ~70)
K_BROWN = .004    # Maillard on the steel face at 140 °C oil, doubling every +10 °C; x0.5 when stirred
BURNT = .70
K_SOFT = .065     # tomato pectin softening; f ramps 60 -> 95 °C, x0.35 when not in liquid
JUICE = .30       # share of tomato mass released as juice by full softening
K_GEL = .16       # starch gelatinisation; f ramps 70 -> 88 °C, x0.35 if not stirred (and lumps)
CONC_FULL = .025  # starch / liquid mass ratio that gives full thickness when fully gelatinised
SMOKE_C, UNSAFE_C, CUTOFF_C = 200., 250., 280.


def loss(T):
    return AW * (10 * (T - TA) + .8 * SIG * ((T + 273.15)**4 - (TA + 273.15)**4))


_H = np.linspace(0, DEPTH, 400)
_V = math.pi * _H**2 * (RS - _H / 3)


def cap_depth(vol_m3):
    """Depth (m) of a level of volume vol_m3 in the wok bowl."""
    return float(np.interp(vol_m3, _V, _H))


def pool_radius(vol_m3):
    h = cap_depth(vol_m3)
    return math.sqrt(max(0., 2 * RS * h - h * h))


def ramp(T, lo, hi):
    return min(1., max(0., (T - lo) / (hi - lo)))


class Wok:
    """Hidden state. heat: 0..1 of P_MAX, set directly. Call step(dt<=0.5, stirring)."""

    def __init__(self, seed=0):
        self.rng = np.random.default_rng(seed)
        self.t = 0.; self.heat = 0.
        self.Tw = TA; self.oil = 0.; self.film = 0.   # free oil g; residual oil film g
        self.glaze = 0.                                # 明油 on top, g
        self.egg = None; self.tom = None; self.sauce = None
        self.dissolved = {}                            # salt / sugar g
        self.events = []; self._flags = set()
        self.cutoff = False

    # ---- additions / removals ------------------------------------------------------------
    def add(self, name, grams, state=None):
        g = float(grams)
        if name == 'oil':
            C = self._cw()
            self.Tw = (C * self.Tw + g / 1e3 * CP_OIL * TA) / (C + g / 1e3 * CP_OIL)
            self.oil += g
        elif name == 'finishing_oil':
            self.glaze += g
        elif name == 'egg':
            if state:
                e = copy.deepcopy(state); e['g'] = g or e['g']
            else:
                e = dict(g=g, g0=g, T=[5., 5.], set=[0., 0.], brown=[0., 0.], down=0, pieces=1, stirred_s=0., in_sauce_s=0.)
            if self.egg:                                    # merge: keep the less cooked numbers
                e['g'] += self.egg['g']
            self.egg = e
        elif name == 'tomato':
            if state:
                self.tom = copy.deepcopy(state)
            else:
                self.tom = dict(g=g, g0=g, Ts=TA, Tc=TA, soft=0., scorch=0.)
        elif name in LIQ_ITEMS:
            if name in ('salt', 'sugar'):
                self.dissolved[name] = self.dissolved.get(name, 0.) + g
                return
            s = self.sauce or dict(water=0., juice=0., ketchup=0., starch=0., T=TA, gel=0., lumps=0., scorch=0., peak=0.)
            w = g * (1 - STARCH_FRAC) if name == 'starch_water' else (g * .7 if name == 'ketchup' else g)
            Tin = 5. if name == 'starch_water' else TA if name == 'water' else 25.
            m0 = s['water'] + s['juice']
            s['T'] = (m0 * s['T'] + w * Tin) / max(1e-9, m0 + w) if m0 + w > 0 else Tin
            s['water'] += w
            if name == 'starch_water':
                s['starch'] += g * STARCH_FRAC
            if name == 'ketchup':
                s['ketchup'] += g
            s['peak'] = max(s['peak'], s['water'] + s['juice'])
            self.sauce = s
        elif name == 'sauce' and state:
            self.sauce = copy.deepcopy(state)
        else:
            raise ValueError(f'unknown item {name}')
        self._event('add', f'{name} {g:.0f} g')

    def remove(self, name):
        """Take one item out (egg, tomato, sauce); returns its state for add(name, g, state)."""
        attr = {'egg': 'egg', 'tomato': 'tom', 'sauce': 'sauce'}[name]
        st = getattr(self, attr); setattr(self, attr, None)
        return st

    def remove_all(self):
        """Tip the whole wok out (plate / holding bowl). Returns {name: {grams, state}}."""
        out = {}
        if self.egg: out['egg'] = dict(grams=self.egg['g'], state=self.egg)
        if self.tom: out['tomato'] = dict(grams=self.tom['g'], state=self.tom)
        if self.sauce: out['sauce'] = dict(grams=self._liq() + self.sauce['starch'], state=self.sauce)
        if self.oil + self.glaze > 0: out['oil'] = dict(grams=self.oil + self.glaze, state=dict(T=self.Tw))
        for k, v in self.dissolved.items(): out[k] = dict(grams=v, state=None)
        self.egg = self.tom = self.sauce = None; self.oil = self.glaze = 0.; self.dissolved = {}
        self.film = OIL_FILM_G
        return out

    def pour_out_oil(self):
        """润锅 pour-out: free oil goes, a film of OIL_FILM_G stays on the steel."""
        g = max(0., self.oil - OIL_FILM_G)
        self.oil = 0.; self.film = OIL_FILM_G if g > 0 or self.film else 0.
        return g

    def flip(self, name='egg'):
        if name == 'egg' and self.egg:
            self.egg['down'] = 1 - self.egg['down']
            self.egg['pieces'] = max(self.egg['pieces'], int(self.rng.integers(2, 5)))   # a 3-egg sheet breaks when turned
            self._event('flip', 'egg')

    # ---- physics -------------------------------------------------------------------------
    def _cw(self):
        return M_STEEL * CP_STEEL + (self.oil + self.film) / 1e3 * CP_OIL

    def _liq(self):
        return 0. if not self.sauce else self.sauce['water'] + self.sauce['juice']

    def _vol(self):
        """Liquid volume plus half the tomato (it sits in the sauce), m^3."""
        return (self._liq() + (self.tom['g'] * .5 if self.tom else 0.) * (self._liq() > 5)) / 1e6

    def step(self, dt, stirring=False):
        n = max(1, int(round(dt / .05))); h = dt / n
        for _ in range(n):
            self._sub(h, bool(stirring))
        self.t += dt

    def _sub(self, dt, stir):
        if self.Tw >= CUTOFF_C and not self.cutoff:
            self.cutoff = True; self._event('cutoff', f'cooker dry-burn cut-off at {self.Tw:.0f} °C')
        if self.cutoff and self.Tw < CUTOFF_C - 40: self.cutoff = False
        P = 0. if self.cutoff else min(1., max(0., self.heat)) * P_MAX
        oily = self.oil + self.film >= 2.
        L = self._liq()
        qw = P - loss(self.Tw)                       # into the wok node
        s = self.sauce
        if s and L > .5:                             # steel -> liquid, over the wetted area
            A_wet = 2 * math.pi * RS * cap_depth(self._vol())   # tomato in the sauce raises the level
            q = H_BOIL * A_wet * (self.Tw - s['T']); qw -= q
            Cl = L / 1e3 * CP_W
            s['T'] += q * dt / Cl
        e, tm = self.egg, self.tom
        if e:
            in_liq = L > 30.
            d, u = e['down'], 1 - e['down']
            Ce = e['g'] / 2e3 * CP_EGG
            if in_liq:                               # egg back in the sauce at the end
                for i in (0, 1):
                    q = H_LIQ * A_EGG * (s['T'] - e['T'][i]); s['T'] -= q * dt / (L / 1e3 * CP_W); e['T'][i] += q * dt / Ce
                e['in_sauce_s'] += dt
            else:
                hc = (H_FRY if oily else H_DRY) * A_EGG
                faces = (d, u) if stir else (d,)       # stirring turns pieces: both faces meet the steel
                for i in faces:
                    q = hc / len(faces) * (self.Tw - e['T'][i]); qw -= q; e['T'][i] += q * dt / Ce
                q = H_EGG_IN * A_EGG * (e['T'][d] - e['T'][u]); e['T'][d] -= q * dt / Ce; e['T'][u] += q * dt / Ce
                e['T'][u] -= 15 * A_EGG * (e['T'][u] - TA) * dt / Ce
                for i in faces:                      # browning of the face(s) on the steel
                    rate = K_BROWN * 2 ** ((self.Tw - 140) / 10) * (.5 if stir else 1.) * (1.5 if not oily else 1.)
                    if self.Tw > 100:
                        e['brown'][i] = min(1., e['brown'][i] + rate * dt * (.3 + .7 * e['set'][i]))
            for i in (0, 1):
                if e['T'][i] > 100.:                 # water plateau
                    ex = (e['T'][i] - 100) * Ce; e['T'][i] = 100.; e['g'] = max(e['g'] * .85, e['g'] - ex / L_VAP * 1e3)
                e['set'][i] += K_SET * ramp(e['T'][i], 62, 85) * (1 - e['set'][i]) * dt
            if stir:
                e['stirred_s'] += dt
                e['pieces'] = max(e['pieces'], min(14, 1 + int(e['stirred_s'] / 1.5)))
        if tm:
            Cs, Cc = tm['g'] * .35 / 1e3 * CP_TOM, tm['g'] * .65 / 1e3 * CP_TOM
            wet = L > 30.
            fc = (.35 if stir else .25) * A_TOM     # share of the surface on the steel
            if wet:
                fl = min(1., L / 150.) * A_TOM
                q = H_LIQ * fl * (s['T'] - tm['Ts']); s['T'] -= q * dt / (L / 1e3 * CP_W); tm['Ts'] += q * dt / Cs
                fc *= .5
            q = (H_FRY if oily else H_DRY) * fc * (self.Tw - tm['Ts']); qw -= q; tm['Ts'] += q * dt / Cs
            q = 90. * A_TOM * (tm['Ts'] - tm['Tc']); tm['Ts'] -= q * dt / Cs; tm['Tc'] += q * dt / Cc
            if tm['Ts'] > 100.:
                tm['Ts'] = 100.
            ds = K_SOFT * ramp(tm['Ts'], 60, 95) * (1. if wet else .35) * (1 - tm['soft']) * dt
            tm['soft'] += ds
            jg = JUICE * tm['g0'] * ds               # juice joins the sauce at the tomato's temperature
            if jg > 0:
                tm['g'] -= jg
                if not self.sauce:
                    self.sauce = s = dict(water=0., juice=0., ketchup=0., starch=0., T=tm['Ts'], gel=0., lumps=0., scorch=0., peak=0.)
                m0 = s['water'] + s['juice']; s['T'] = (m0 * s['T'] + jg * tm['Ts']) / (m0 + jg); s['juice'] += jg
                s['peak'] = max(s['peak'], s['water'] + s['juice'])
            if self._liq() < 5 and self.Tw > 170:
                tm['scorch'] = min(1., tm['scorch'] + .01 * 2 ** ((self.Tw - 170) / 15) * (.5 if stir else 1.) * dt)
        s = self.sauce
        if s:
            L = self._liq()
            if L > .5:
                if s['T'] > 100.:                    # boiling: excess heat goes into steam
                    ex = (s['T'] - 100) * L / 1e3 * CP_W; s['T'] = 100.
                    ev = ex / L_VAP * 1e3; fw = s['water'] / L
                    s['water'] = max(0., s['water'] - ev * fw); s['juice'] = max(0., s['juice'] - ev * (1 - fw))
                if s['starch'] > 0:
                    dg = K_GEL * ramp(s['T'], 70, 88) * (1. if stir else .35) * (1 - s['gel']) * dt
                    s['gel'] += dg; s['lumps'] = min(1., s['lumps'] + dg * (.05 if stir else .8))
            if L < 10 and self.Tw > 150 and (s['starch'] > 0 or s['ketchup'] > 0 or s['juice'] > 0):
                s['scorch'] = min(1., s['scorch'] + .01 * 2 ** ((self.Tw - 150) / 20) * dt)
        self.Tw += qw * dt / self._cw()
        self._check()

    def _check(self):
        oily = self.oil + self.film >= 2.
        if oily and self._liq() < 20 and self.Tw > SMOKE_C: self._event_once('smoke', f'oil smoking at {self.Tw:.0f} °C')
        if self.Tw > UNSAFE_C: self._event_once('unsafe', f'wok {self.Tw:.0f} °C > {UNSAFE_C:.0f}')
        if self.egg and max(self.egg['brown']) > BURNT: self._event_once('egg_burnt', f"brown {max(self.egg['brown']):.2f}")
        if self.tom and self.tom['scorch'] > .3: self._event_once('tomato_scorched', '')
        s = self.sauce
        if s and s['peak'] > 30 and self._liq() < 10: self._event_once('sauce_dry', f'{self._liq():.0f} g liquid left')
        if s and s['scorch'] > .3: self._event_once('sauce_scorched', '')
        if s and s['lumps'] > .3: self._event_once('starch_lumps', 'thickened without stirring')

    def _event(self, kind, detail=''):
        self.events.append(dict(t=round(self.t, 1), kind=kind, detail=detail))

    def _event_once(self, kind, detail):
        if kind not in self._flags:
            self._flags.add(kind); self._event(kind, detail)

    # ---- outputs -------------------------------------------------------------------------
    def thick(self):
        s = self.sauce
        if not s or s['starch'] <= 0: return 0.
        conc = s['starch'] / max(1., self._liq())
        return min(1., s['gel'] * conc / CONC_FULL)

    def truth(self):
        """Every hidden number (logging / scoring / the camera). Never shown to Claude."""
        r = lambda x: round(float(x), 3)
        out = dict(t=r(self.t), heat=r(self.heat), T_wok=r(self.Tw), oil_g=r(self.oil), film_g=r(self.film), glaze_g=r(self.glaze),
                   smoking=bool(self.oil + self.film >= 2 and self._liq() < 20 and self.Tw > SMOKE_C), unsafe=bool(self.Tw > UNSAFE_C), cutoff=self.cutoff,
                   dissolved={k: r(v) for k, v in self.dissolved.items()}, events=list(self.events))
        e = self.egg
        if e:
            d, u = e['down'], 1 - e['down']
            out['egg'] = dict(g=r(e['g']), T_down=r(e['T'][d]), T_up=r(e['T'][u]), set_down=r(e['set'][d]), set_up=r(e['set'][u]),
                              brown_down=r(e['brown'][d]), brown_up=r(e['brown'][u]), burnt=bool(max(e['brown']) > BURNT),
                              pieces=int(e['pieces']), in_sauce_s=r(e['in_sauce_s']), flipped=bool(d == 1))
        t = self.tom
        if t:
            out['tomato'] = dict(g=r(t['g']), g0=r(t['g0']), T_surf=r(t['Ts']), T_core=r(t['Tc']), soft=r(t['soft']), scorch=r(t['scorch']))
        s = self.sauce
        if s:
            L = self._liq()
            out['sauce'] = dict(liquid_g=r(L), water_g=r(s['water']), juice_g=r(s['juice']), ketchup_g=r(s['ketchup']), starch_g=r(s['starch']),
                                T=r(s['T']), boiling=bool(L > .5 and s['T'] >= 99.5 and self.Tw > 101), gel=r(s['gel']), thick=r(self.thick()),
                                lumps=r(s['lumps']), scorch=r(s['scorch']), reduced=r(1 - L / s['peak']) if s['peak'] else 0.,
                                pool_r=r(pool_radius(self._vol())), depth=r(cap_depth(self._vol())))
        out['load_g'] = r(self._load())
        out['wok_C'] = out['T_wok']                  # aliases used by cook_api
        items = {}
        if self.oil + self.glaze > 0: items['oil'] = dict(grams=r(self.oil + self.glaze))
        for k in ('egg', 'tomato', 'sauce'):
            if k in out: items[k] = dict(grams=out[k]['g'] if k != 'sauce' else out[k]['liquid_g'])
        for k, v in self.dissolved.items(): items[k] = dict(grams=r(v))
        out['items'] = items
        return out

    def _load(self):
        m = self.oil + self.film + self.glaze + self._liq() + sum(self.dissolved.values())
        if self.sauce: m += self.sauce['starch'] + self.sauce['ketchup'] * .3
        if self.egg: m += self.egg['g']
        if self.tom: m += self.tom['g']
        return m

    def sensors(self, rng):
        """What the robot has. thermo_C: IR spot on the wok centre. With >= 20 g of liquid it reads the sauce;
        with oil (>= 2 g, incl. the 润锅 film) the oil/steel; on a dry wok None (seasoned steel emissivity is not
        trusted, the reading would be meaningless). ±3 °C noise. load_g: cooker load cell, tared wok, ±20 g."""
        L = self._liq()
        if L >= 20: T = self.sauce['T']; src = 'liquid'
        elif self.oil + self.film >= 2: T = self.Tw; src = 'oil'
        else: T = None; src = 'dry'
        return dict(thermo_C=None if T is None else round(T + float(np.clip(rng.normal(0, 1.5), -3, 3)), 1), thermo_src=src,
                    elapsed_s=round(self.t, 1), heat=round(float(self.heat), 2),
                    load_g=round(max(0., self._load() + float(np.clip(rng.normal(0, 10), -20, 20))), 0))


# ---- self-test: the canonical recipe ---------------------------------------------------------
def run_recipe(log=print, snap=None):
    """Wang Gang's 西红柿炒蛋 with sensible robot timings. snap(tag, wok) is called at key states."""
    w = Wok(); rng = np.random.default_rng(1)
    snap = snap or (lambda tag, wk: None)

    def run(sec, stir=False, until=None, every=5.):
        t0 = w.t; nxt = w.t
        while w.t - t0 < sec - 1e-9:
            w.step(.5, stir)
            if until and until(): break
            if w.t >= nxt - 1e-9:
                nxt += every
        line()

    def line(tag=''):
        tr = w.truth(); se = w.sensors(rng)
        x = f"t={tr['t']:6.1f} heat={w.heat:.2f} Twok={tr['T_wok']:6.1f} thermo={se['thermo_C']} load={se['load_g']:.0f}"
        if 'egg' in tr: x += f" | egg set d/u {tr['egg']['set_down']:.2f}/{tr['egg']['set_up']:.2f} brown d/u {tr['egg']['brown_down']:.2f}/{tr['egg']['brown_up']:.2f} T {tr['egg']['T_down']:.0f}/{tr['egg']['T_up']:.0f}"
        if 'tomato' in tr: x += f" | tom soft {tr['tomato']['soft']:.2f} Ts {tr['tomato']['T_surf']:.0f} Tc {tr['tomato']['T_core']:.0f}"
        if 'sauce' in tr: x += f" | sauce {tr['sauce']['liquid_g']:.0f} g {tr['sauce']['T']:.0f} °C thick {tr['sauce']['thick']:.2f}"
        log(x + (f'  <{tag}>' if tag else ''))

    log('-- 润锅: heat the dry wok, oil it, pour the oil out')
    w.heat = .7; run(15); snap('hot_empty', w)
    w.add('oil', 40); run(6, stir=True)
    log(f'   poured out {w.pour_out_oil():.0f} g')
    log('-- oil to 120 °C, beaten eggs in, low heat, fry ~60 s without stirring')
    w.add('oil', 30); w.heat = .5
    run(120, until=lambda: w.Tw >= 120); line('oil at 120')
    w.add('egg', 150); w.heat = .25; snap('egg_raw', w)
    run(40); snap('egg_half', w); run(20); snap('egg_flip_ready', w)
    w.flip('egg'); line('flip'); run(25); snap('egg_done', w)
    egg = w.remove('egg'); line('egg out')
    log('-- tomato + ketchup, low heat, mix')
    w.heat = .35; w.add('tomato', 300); snap('tomato_raw', w); run(15, stir=True); w.add('ketchup', 5); run(10, stir=True)
    log('-- water, simmer ~60 s until soft')
    w.add('water', 100); w.heat = .6; run(10, stir=True); snap('sauce_thin_boil', w); run(22); snap('tomato_mid', w); run(28); run(5, stir=True); snap('tomato_soft', w)
    log('-- starch water, stir until thick, 明油')
    w.add('starch_water', 30); w.step(1., True); snap('starch_in', w); run(14, stir=True); snap('sauce_thick', w)
    w.add('finishing_oil', 5)
    log('-- eggs back, a few stirs, plate')
    w.add('egg', 0, state=egg); run(6, stir=True); snap('final', w)
    w.heat = 0.; plate = w.remove_all()
    log('   plated: ' + ', '.join(f"{k} {v['grams']:.0f} g" for k, v in plate.items()))
    log('   events: ' + '; '.join(f"{e['t']}s {e['kind']}" for e in w.events if e['kind'] not in ('add', 'flip')))
    return w


if __name__ == '__main__':
    run_recipe()
    print('-- abuse: 120 °C oil, egg at full heat, no flip for 120 s')
    w = Wok(); w.add('oil', 30); w.heat = 1.
    while w.Tw < 120: w.step(.5)
    w.add('egg', 150)
    for k in range(24):
        w.step(5.); e = w.truth()['egg']
        if k % 4 == 3: print(f"t={w.t:5.0f} Twok={w.Tw:5.0f} set d/u {e['set_down']:.2f}/{e['set_up']:.2f} brown_down {e['brown_down']:.2f}")
    print('   events:', [(x['t'], x['kind']) for x in w.events if x['kind'] != 'add'])
    print('-- heat-up check: 30 g oil, full power, 30 -> 180 °C')
    w = Wok(); w.add('oil', 30); w.heat = 1.
    while w.Tw < 180: w.step(.05)
    print(f'   {w.t:.1f} s (heat15: 42.5 s)')
    print('-- sauce boiled dry at full heat')
    w = Wok(); w.add('oil', 10); w.add('tomato', 300); w.add('water', 100); w.heat = 1.
    for k in range(40):
        w.step(5., stirring=k % 2 == 0)
    tr = w.truth(); print(f"   t={w.t:.0f} Twok={tr['T_wok']:.0f} liquid {tr['sauce']['liquid_g']:.0f} g scorch tom {tr['tomato']['scorch']:.2f} sauce {tr['sauce']['scorch']:.2f}")
    print('   events:', [(x['t'], x['kind']) for x in w.events if x['kind'] != 'add'])
