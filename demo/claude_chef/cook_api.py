"""Skill-level robot API for the cooking demo: what Claude can call, the deterministic gate in front of it,
and the kitchen state the skills act on.

Every skill maps to a motion the robot_rail sim already checked (field `evidence`) or is flagged `unverified`.
The wok contents follow cook_model.Wok (hidden truth); Claude only gets sensors and the wok camera.
One registry produces the prompt text, the argument validator and API.md, so they cannot drift apart.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

import cook_model
import wok_cam

ROOT = Path(__file__).resolve().parent
HEAT_DT = 0.25                       # model step while a skill runs (s)
SMOKE_C, CUTOFF_C = 210.0, 250.0     # smoke detector; stove guard cuts power (R15 safety, robot limit 250 °C)
HALF_POWER_PAUSE_S = 6.0             # R15 policy: drop to about half power whenever the spatula stops
MAX_FOOD_G = 1150.0                  # heaviest dish checked for the wok tip (R15 evidence 6; R17 chain: PGC 6.47 of 7 N·m)
SPAT_S = 27.4                        # spatula rest (counter left of the sink) <-> stir stroke start, one way (R18b, results/r18/arm18.json)
PLATE_S = 79.5                       # faucet open, R17 wok chain (plate, rinse under the tap, back on the cooker), faucet closed, free moves (arm18.json minus the spatula)
SPOT2_S = 27.0                       # tip onto the second plating spot and back to the cooker without the sink (R18 tip checked; return = lift path reversed, estimate)
DOSE_LIMITS = dict(oil=60, water=300, starch_water=40, ketchup=20, salt=5, sugar=10, finishing_oil=15)

R15 = 'robot_rail/sim/r10/claude/README_R10.md#R15'
R14 = 'robot_rail/sim/r10/claude/README_R10.md#R14'
R17 = 'robot_rail/sim/r10/claude/README_R10.md#R17'
R18 = 'robot_rail/sim/r10/claude/README_R10.md#R18'
R11 = 'robot_rail/sim/r10/claude/README_R10.md#R11'


@dataclass
class Skill:
    name: str
    doc: str
    args: dict                      # name -> (type, spec, default|REQUIRED)
    seconds: str                    # how the duration is set
    evidence: str
    hardware: str
    unverified: str = ''


REQ = object()
SKILLS = [
    Skill('fridge_fetch', "Open the fridge, take the robot cold box from the door bin (the user loaded today's cold "
          "items: 3 beaten eggs in a cup, 150 g, 5 °C), set it on the counter, close the door.", {}, '25 s',
          f'{R14} fridge: door physics 20–140 N seals open every time; 176 reach probes; continuous door arc',
          'UR5e + PGC-140 finger set P2', unverified='the eggs are cracked and beaten by the user beforehand (one gripper cannot crack eggs)'),
    Skill('prep_tomato', 'Pick one tomato from the raw tray, rinse it under the tap, cut it into 8 wedges on the '
          'lever cutter (about 150 g of wedges into the tomato bowl).', {}, '45 s per tomato',
          f'{R11} results/chain_AW/full.json: 6,653 states, every one collision-checked; R17 faucet lever 3.5 s', 'UR5e + PGC + lever cutter',
          unverified='the replay starts with the tomato already gripped; rinse water and the cutting itself are not '
          'physically simulated; 45 s is an estimate'),
    Skill('dose_cup', 'The seasoning station doses one item by weight into a robot cup and the arm takes it.',
          {'what': ('enum', list(DOSE_LIMITS), REQ), 'grams': ('number', [0.5, 300], REQ)}, '10 s',
          f'{R14} evidence 1: cup at the seasoning port ✓ (reserve 7–23 mm)', 'pumps / extruder + 0.1 g scale'),
    Skill('pour_into_wok', "Arm pours a source into the wok: a cup id ('cup1'…), 'egg', 'tomato' or 'holding_bowl'. "
          'The arm is over the wok, so the heat must be 0 (plume rule).',
          {'source': ('string', None, REQ)}, '8 s',
          f'{R14} evidence 1: cup pour over the wok 23/72 orientations ✓; {R15} plume rule ≥ 0.20 m from the axis',
          'UR5e + PGC'),
    Skill('load_drum', 'Station fills the 4-compartment pour drum (in this order) and the arm drops it into the '
          'servo holder behind the wok. Heat must be 0. Later drum_release() empties one compartment at a time, '
          'with the heat on and without the arm.',
          {'items': ('items', 4, REQ)}, '15 s + 5 s per compartment',
          f'{R14} evidence 4: pour drum releases in order, 100 % (granules); {R15} design 4',
          'servo pour-drum holder', unverified='holder spot behind the wok has zero clearance reserve; liquids not simulated'),
    Skill('drum_release', 'Servo rolls the drum to empty its next compartment into the wok. The arm is not needed. '
          'stir_seconds > 0 makes it one movement set: the arm (taking the spatula first if needed) stirs straight '
          'after the release, with no pause for a decision; use it for anything that must not sit unstirred.',
          {'stir_seconds': ('number', [0, 60], 0)}, '1.5 s (+ stir_seconds)',
          f'{R14} evidence 4 (≥ 1.3 s between compartments); stir as in stir()', 'servo (+ UR5e + spatula)'),
    Skill('set_heat', 'Set the induction cooker power: 0 = off (离火), 0.3 ≈ low, 0.5 ≈ medium, 1.0 = full (2975 W '
          'into the wok).', {'level': ('number', [0, 1], REQ)}, '1 s',
          f'{R15} design 1: bolt-on servo turns the knob; heat15.py budget', 'concave 3.5 kW induction + knob servo'),
    Skill('stir', 'Stir-fry with the arm-held spatula (scrape strokes, about 3.6 s each). If the hand is free, the arm first '
          f'takes the spatula from its rest on the counter left of the sink ({SPAT_S:g} s). Any skill that needs the arm '
          f'(pour, dose, prep, fridge, drum loading, wok tip) first puts the spatula back ({SPAT_S:g} s); the cooker keeps '
          'running meanwhile. drum_release, set_heat, look and wait do not need the arm.',
          {'seconds': ('number', [3.6, 90], REQ)}, f'seconds (+{SPAT_S:g} s to take the spatula)',
          f'{R15} evidence 2–3: 80/80 stroke poses ✓, one continuous 5-stroke cycle ✓ (2.63 s; R19: not executable as timed, about 3.6 s with a stop at each hand-off); stirbench mixing; '
          f'{R18} spatula rest → stroke start one continuous checked path, 6.0 mm reserve',
          'UR5e + PGC + keyed spatula'),
    Skill('flip_egg', 'Slide the spatula under the egg and turn it over.', {}, '4 s',
          f'{R15} stroke', 'UR5e + spatula', unverified='uses the scrape stroke; flipping a single piece was not simulated'),
    Skill('tip_wok', "Heat must be 0. Lift the wok off the cooker, carry it to the counter left of the hood and tip it "
          "toward the robot to 90°. 'plate' = serve: tip onto the plate, then rinse the wok at the sink under the running "
          "faucet and set it back (ends the dish). 'holding_bowl' (take food out to add it back later) or 'oil_cup' "
          "(润锅 oil pour-out) = tip at the second spot and set the wok straight back, no rinse.",
          {'into': ('enum', ['plate', 'holding_bowl', 'oil_cup'], REQ)},
          f'plate {PLATE_S:g} s, holding_bowl / oil_cup {SPOT2_S:g} s',
          f'{R17} wok chain: off the cooker → tip 90° → sink → emptied → back, every step checked, 48.9 s, 2.0 mm (R19 re-check at ≤ 4 mm), '
          f'PGC 6.47 N·m with 1.15 kg; {R18} second plating spot ✓; {R15} physics 81–91 % on a guarded plate',
          'UR5e + PGC keyed wok grip + faucet lever block',
          unverified='holding_bowl / oil_cup: the return to the cooker skips the sink (lift path reversed, not re-run); '
          'tipping into a cup (narrower than a plate) not simulated'),
    Skill('look', 'Take a wok-camera image and read the thermometer.', {}, '1 s',
          'hood colour camera + IR thermometer (R15 design 1)', 'RGB + thermal camera'),
    Skill('wait', 'Do nothing for a while (the cooker keeps running). With food in the wok and heat > 0.5, '
          f'pauses longer than {HALF_POWER_PAUSE_S:g} s are refused (R15 half-power policy).',
          {'seconds': ('number', [1, 120], REQ)}, 'seconds', f'{R15} evidence 1 (6 s pause at 200 °C: +17 °C)', '—'),
    Skill('done', 'Finish and report.', {'success': ('boolean', None, REQ), 'summary': ('string', None, REQ)},
          '0 s', '—', 'app notification'),
]
# Routines: predefined step sequences (recipe-level 'movement sets'). They run without a pause for a decision;
# their stop conditions use only the thermometer and the clock. Claude picks the routine and its parameters.
ROUTINES = [
    Skill('mise_en_place', 'Everything before the heat goes on, in one go: fetch the cold box, cut `tomatoes` tomatoes, '
          'dose each of `cups` into its own robot cup, and load `drum` (up to 4 compartments, in release order).',
          {'tomatoes': ('number', [0, 2], 0), 'cups': ('items', 6, 0), 'drum': ('items', 4, 0)}, 'sum of the steps',
          'fridge_fetch + prep_tomato + dose_cup + load_drum', 'as the steps'),
    Skill('heat_to', 'Heat at `level` until the thermometer reads `target_C` (needs oil or food in the wok), at most '
          '120 s; stops early if the reading passes 200 °C.', {'level': ('number', [0.1, 1], REQ),
          'target_C': ('number', [40, 200], REQ)}, 'until target', 'set_heat + wait (3 s steps)', 'as the steps'),
    Skill('add_off_heat', 'Heat off (plume rule), pour `source` into the wok, then set the heat back to `level` '
          '(0 = leave it off).', {'source': ('string', None, REQ), 'level': ('number', [0, 1], REQ)},
          '~10 s', 'set_heat + pour_into_wok + set_heat', 'as the steps'),
    Skill('fry_still', 'Leave the food to fry undisturbed for `seconds` at the current heat (heat must be ≤ 0.5).',
          {'seconds': ('number', [3, 120], REQ)}, 'seconds', 'wait', 'as the steps'),
    Skill('flip_and_fry', 'Turn the egg over, then fry the second side undisturbed for `seconds`.',
          {'seconds': ('number', [0, 120], REQ)}, '4 s + seconds', 'flip_egg + wait', 'as the steps'),
    Skill('stir_fry', 'Set the heat to `level`, then stir for `seconds` (takes the spatula if needed).',
          {'level': ('number', [0, 1], REQ), 'seconds': ('number', [3.6, 90], REQ)}, 'seconds', 'set_heat + stir',
          'as the steps'),
    Skill('drum_add_stir', 'Release the next drum compartment and stir straight after it for `seconds` (no pause). '
          'Use for ketchup, water, starch water, finishing oil.', {'seconds': ('number', [3.6, 90], REQ)},
          '1.5 s + seconds', 'drum_release(stir_seconds)', 'as the steps'),
    Skill('take_out', 'Heat off, tip everything in the wok into `into` (holding_bowl, oil_cup or plate).',
          {'into': ('enum', ['plate', 'holding_bowl', 'oil_cup'], REQ)}, 'as tip_wok', 'set_heat + tip_wok',
          'as the steps'),
    Skill('return_and_toss', 'Heat off, pour the holding bowl back in, heat at `level` and stir for `seconds`.',
          {'level': ('number', [0, 1], REQ), 'seconds': ('number', [3.6, 60], REQ)}, '~10 s + seconds',
          'set_heat + pour_into_wok + set_heat + stir', 'as the steps'),
    Skill('season_wok', '润锅: heat off, pour oil cup `cup` in, heat at `level` until `target_C`, heat off, pour the oil '
          'out into the oil cup. Leaves a hot, oiled wok.', {'cup': ('string', None, REQ), 'level': ('number', [0.1, 1], REQ),
          'target_C': ('number', [60, 200], REQ)}, '~60 s', 'pour_into_wok + set_heat + wait + tip_wok', 'as the steps'),
    Skill('egg_into_hot_oil', 'Heat off, pour oil cup `cup` in, heat at `level` until `target_C`, heat off, pour the '
          'beaten egg in, then set the heat to `fry_level`.', {'cup': ('string', None, REQ),
          'level': ('number', [0.1, 1], REQ), 'target_C': ('number', [60, 200], REQ),
          'fry_level': ('number', [0, 1], REQ)}, '~40 s', 'pour_into_wok + set_heat + wait + pour_into_wok',
          'as the steps'),
    Skill('season_and_toss', 'Pour each cup in `cups` (e.g. salt, sugar) with the heat off, then heat at `level` and '
          'stir for `seconds` so it dissolves evenly.', {'cups': ('strings', 6, REQ), 'level': ('number', [0, 1], REQ),
          'seconds': ('number', [3.6, 60], REQ)}, '~8 s per cup + seconds',
          'set_heat + pour_into_wok + set_heat + stir', 'as the steps'),
]
BY_NAME = {s.name: s for s in SKILLS + ROUTINES}
ROUTINE_NAMES = {s.name for s in ROUTINES}


@dataclass
class Kitchen:
    seed: int = 0
    t: float = 0.0
    hand: str = 'free'                         # free | spatula
    tomatoes_whole: int = 2                    # Wang Gang uses ~300 g = 2 tomatoes
    counter: dict = field(default_factory=dict)  # 'egg' / 'tomato' -> {grams, state}
    cups: dict = field(default_factory=dict)     # 'cup1' -> {what, grams}
    drum: dict | None = None                     # {'slots': [...], 'next': int}
    holding_bowl: dict = field(default_factory=dict)
    oil_cup: dict = field(default_factory=dict)
    plate: dict = field(default_factory=dict)
    coldbox_fetched: bool = False
    done: bool = False
    events: list = field(default_factory=list)
    log: list = field(default_factory=list)      # every call with truth, for scoring and the video

    def __post_init__(self):
        self.wok = cook_model.Wok(seed=self.seed)
        self.rng = np.random.default_rng(self.seed)
        self.n_img = 0
        self.note = ''

    # ---------------------------------------------------------------- time
    def advance(self, seconds, stirring=False):
        n = max(1, int(round(seconds / HEAT_DT)))
        for _ in range(n):
            self.wok.step(seconds / n, stirring)
            self.t += seconds / n
            T = self.wok.truth().get('wok_C', 0)
            if T >= CUTOFF_C and self.wok.heat > 0:
                self.wok.heat = 0.0
                self.events.append(dict(t=round(self.t, 1), event='STOVE_GUARD_CUT', temp_C=round(T)))

    def sensors(self):
        s = dict(self.wok.sensors(self.rng))
        s['t_s'] = round(self.t, 1)
        s['smoke_detector'] = bool(self.wok.truth().get('wok_C', 0) >= SMOKE_C)
        return s

    def kitchen_view(self):
        """What the robot knows about everything outside the wok (its own bookkeeping, no hidden truth)."""
        return dict(hand=self.hand, tomatoes_whole_left=self.tomatoes_whole, coldbox_fetched=self.coldbox_fetched,
                    counter={k: round(v['grams']) for k, v in self.counter.items()},
                    cups={k: f"{v['what']} {v['grams']:g} g" for k, v in self.cups.items()},
                    drum=None if self.drum is None else dict(
                        remaining=[f"{x['what']} {x['grams']:g} g" for x in self.drum['slots'][self.drum['next']:]]),
                    holding_bowl=sorted(self.holding_bowl), oil_cup=sorted(self.oil_cup), plate=sorted(self.plate))

    def image(self):
        self.n_img += 1
        out = ROOT / 'runs' / 'cur' / f'wok_{self.n_img:03d}.png'
        out.parent.mkdir(parents=True, exist_ok=True)
        wok_cam.render(self.wok.truth(), str(out), seed=self.seed * 1000 + self.n_img)
        return str(out)

    def wok_food_g(self):
        return sum(v.get('grams', 0) for k, v in self.wok.truth().get('items', {}).items() if k != 'oil')

    def wok_has_food(self):
        return self.wok_food_g() > 1

    def park_spatula(self):
        if self.hand == 'spatula':          # back to its counter rest left of the sink (R18b path reversed)
            self.advance(SPAT_S)
            self.hand = 'free'
            self.note = f'spatula put back on its rest first ({SPAT_S:g} s)'

    def take_spatula(self):
        if self.hand != 'spatula':
            self.advance(SPAT_S)
            self.hand = 'spatula'
            self.note = f'spatula taken from its rest first ({SPAT_S:g} s)'

    # ---------------------------------------------------------------- the gate
    def call(self, action, args):
        self.note = ''
        res = self._call(action, dict(args or {}))
        res.setdefault('ok', res['code'] == 'OK')
        if self.note and res['ok']:
            res['message'] = self.note + '; ' + res['message']
        res['sensors'] = self.sensors()
        res['kitchen'] = self.kitchen_view()
        if res['ok'] and action not in ('done',) and (self.wok.heat > 0 or self.wok.truth().get('items')):
            res['image'] = self.image()
        if self.events:
            res['safety_events'] = self.events[-3:]
        self.log.append(dict(action=action, args=args, result={k: v for k, v in res.items()},
                             truth=self.wok.truth(), t=round(self.t, 1)))
        return res

    def _check_args(self, sk, args):
        out = {}
        for k in args:
            if k not in sk.args:
                return None, f'unknown argument {k!r}'
        for k, (typ, spec, default) in sk.args.items():
            if k not in args:
                if default is REQ:
                    return None, f'missing argument {k!r}'
                continue
            v = args[k]
            if typ == 'number':
                if not isinstance(v, (int, float)) or not (spec[0] <= v <= spec[1]):
                    return None, f'{k} must be a number in [{spec[0]}, {spec[1]}]'
            elif typ == 'enum' and v not in spec:
                return None, f'{k} must be one of {spec}'
            elif typ == 'strings':
                if not isinstance(v, list) or not 1 <= len(v) <= spec or not all(isinstance(x, str) for x in v):
                    return None, f'{k} must be a list of 1..{spec} cup ids'
            elif typ == 'items':
                if not isinstance(v, list) or not len(v) <= spec:
                    return None, f'{k} must be a list of up to {spec} {{what, grams}}'
                for it in v:
                    if not isinstance(it, dict) or it.get('what') not in DOSE_LIMITS:
                        return None, f'each item needs what in {list(DOSE_LIMITS)}'
            out[k] = v
        return out, None

    def _routine(self, name, a):
        """Run a routine's primitive steps back to back; stop at the first refusal."""
        def steps():
            if name == 'mise_en_place':
                if not self.coldbox_fetched:
                    yield 'fridge_fetch', {}
                for _ in range(int(a.get('tomatoes') or 0)):
                    yield 'prep_tomato', {}
                for c in a.get('cups') or []:
                    yield 'dose_cup', {'what': c['what'], 'grams': c['grams']}
                if a.get('drum'):
                    yield 'load_drum', {'items': a['drum']}
            elif name == 'heat_to':
                yield 'set_heat', {'level': a['level']}
                for _ in range(40):
                    th = self.sensors().get('thermo_C')
                    if th is None or th >= a['target_C'] or th >= 200:
                        break
                    yield 'wait', {'seconds': 3}
            elif name == 'add_off_heat':
                yield 'set_heat', {'level': 0}
                yield 'pour_into_wok', {'source': a['source']}
                if a['level']:
                    yield 'set_heat', {'level': a['level']}
            elif name == 'fry_still':
                yield 'wait', {'seconds': a['seconds']}
            elif name == 'flip_and_fry':
                yield 'flip_egg', {}
                if a['seconds']:
                    yield 'wait', {'seconds': a['seconds']}
            elif name == 'stir_fry':
                yield 'set_heat', {'level': a['level']}
                yield 'stir', {'seconds': a['seconds']}
            elif name == 'drum_add_stir':
                yield 'drum_release', {'stir_seconds': a['seconds']}
            elif name == 'take_out':
                yield 'set_heat', {'level': 0}
                yield 'tip_wok', {'into': a['into']}
            elif name in ('season_wok', 'egg_into_hot_oil'):
                yield 'set_heat', {'level': 0}
                yield 'pour_into_wok', {'source': a['cup']}
                yield 'set_heat', {'level': a['level']}
                for _ in range(40):
                    th = self.sensors().get('thermo_C')
                    if th is None or th >= a['target_C'] or th >= 200:
                        break
                    yield 'wait', {'seconds': 3}
                yield 'set_heat', {'level': 0}
                if name == 'season_wok':
                    yield 'tip_wok', {'into': 'oil_cup'}
                else:
                    yield 'pour_into_wok', {'source': 'egg'}
                    if a['fry_level']:
                        yield 'set_heat', {'level': a['fry_level']}
            elif name == 'season_and_toss':
                yield 'set_heat', {'level': 0}
                for c in a['cups']:
                    yield 'pour_into_wok', {'source': c}
                yield 'set_heat', {'level': a['level']}
                yield 'stir', {'seconds': a['seconds']}
            elif name == 'return_and_toss':
                yield 'set_heat', {'level': 0}
                yield 'pour_into_wok', {'source': 'holding_bowl'}
                yield 'set_heat', {'level': a['level']}
                yield 'stir', {'seconds': a['seconds']}
        done, msgs = [], []
        for act, ar in steps():
            if name == 'heat_to' and act == 'wait' and self.wok_has_food() and self.wok.heat > 0.5:
                ar = {'seconds': min(3, ar['seconds'])}
            self.note = ''
            r = self._call(act, ar)
            if self.note and r.get('code') == 'OK':
                r['message'] = self.note + '; ' + r['message']
            done.append(act)
            if r['code'] != 'OK':
                self.note = ''
                return dict(code=r['code'], message=f"{name} stopped at step {len(done)} ({act}): {r['message']}"
                            + (f"; done before it: {', '.join(done[:-1])}" if len(done) > 1 else ''), steps=done)
            if act not in ('wait', 'set_heat'):
                msgs.append(r['message'])
        self.note = ''
        th = self.sensors().get('thermo_C')
        parts = msgs[-4:] + ([f'thermometer {th:.0f} °C'] if th is not None else [])
        return dict(code='OK', message=f"{name} done ({len(done)} steps)" + (': ' + '; '.join(parts) if parts else ''),
                    steps=done)

    def _call(self, action, args):
        if self.done:
            return dict(code='REJECTED_PRECONDITION', message='mission already finished')
        sk = BY_NAME.get(action)
        if sk is None:
            return dict(code='INVALID_ACTION', message=f'no skill {action!r}')
        a, err = self._check_args(sk, args)
        if err:
            return dict(code='INVALID_ARGS', message=err)
        if action in ROUTINE_NAMES:
            return self._routine(action, a)
        return getattr(self, f'_do_{action}')(**a)

    def _need_heat_off(self, what):
        if self.wok.heat > 0:
            return dict(code='REJECTED_SAFETY', message=f'{what} puts the arm over the wok; set_heat(0) first '
                        '(plume rule: arm ≥ 0.20 m from the wok axis while the heat is on)')

    # ---------------------------------------------------------------- skills
    def _do_fridge_fetch(self):
        if self.coldbox_fetched:
            return dict(code='REJECTED_PRECONDITION', message='cold box already on the counter')
        self.park_spatula()
        self.advance(25)
        self.coldbox_fetched = True
        self.counter['egg'] = dict(grams=150.0, state=None)
        return dict(code='OK', message='cold box on the counter: beaten eggs 150 g (5 °C)')

    def _do_prep_tomato(self):
        if self.tomatoes_whole <= 0:
            return dict(code='REJECTED_PRECONDITION', message='no whole tomatoes left on the raw tray')
        self.park_spatula()
        self.advance(45)
        self.tomatoes_whole -= 1
        c = self.counter.setdefault('tomato', dict(grams=0.0, state=None))
        c['grams'] += 150.0
        return dict(code='OK', message=f"8 wedges cut; tomato bowl now {c['grams']:.0f} g")

    def _do_dose_cup(self, what, grams):
        if grams > DOSE_LIMITS[what]:
            return dict(code='INVALID_ARGS', message=f'{what} at most {DOSE_LIMITS[what]} g per cup')
        if len(self.cups) >= 6:
            return dict(code='REJECTED_PRECONDITION', message='all 6 robot cups are in use')
        self.park_spatula()
        self.advance(10)
        cid = next(f'cup{i}' for i in range(1, 99) if f'cup{i}' not in self.cups)
        self.cups[cid] = dict(what=what, grams=float(grams))
        return dict(code='OK', message=f'{cid}: {what} {grams:g} g')

    def _do_pour_into_wok(self, source):
        r = self._need_heat_off('pouring')
        if r:
            return r
        if source in self.cups:
            c = self.cups[source]
            items = [(c['what'], c['grams'], None)]
        elif source in ('egg', 'tomato') and source in self.counter:
            c = self.counter[source]
            items = [(source, c['grams'], c['state'])]
        elif source == 'holding_bowl' and self.holding_bowl:
            items = [(k, v['grams'], v.get('state')) for k, v in self.holding_bowl.items()]
        else:
            return dict(code='REJECTED_PRECONDITION', message=f'nothing to pour from {source!r}')
        if self.wok_food_g() + sum(g for n, g, _ in items if n != 'oil') > MAX_FOOD_G:
            return dict(code='REJECTED_SAFETY', message=f'wok food would exceed {MAX_FOOD_G:g} g')
        if source in self.cups:
            del self.cups[source]
        elif source == 'holding_bowl':
            self.holding_bowl = {}
        else:
            del self.counter[source]
        self.park_spatula()
        self.advance(8)
        for n, g, st in items:
            self.wok.add(n, g, st)
        return dict(code='OK', message='poured ' + ', '.join(f'{n} {g:.0f} g' for n, g, _ in items))

    def _do_load_drum(self, items):
        r = self._need_heat_off('placing the drum in its holder')
        if r:
            return r
        if not items:
            return dict(code='INVALID_ARGS', message='items must hold 1..4 compartments')
        if self.drum and self.drum['next'] < len(self.drum['slots']):
            return dict(code='REJECTED_PRECONDITION', message='the drum still has unreleased compartments')
        for it in items:
            g = it.get('grams')
            if not isinstance(g, (int, float)) or not 0.5 <= g <= min(60, DOSE_LIMITS[it['what']]):
                return dict(code='INVALID_ARGS', message=f"{it['what']}: grams in [0.5, {min(60, DOSE_LIMITS[it['what']])}]")
        self.park_spatula()
        self.advance(15 + 5 * len(items))
        self.drum = dict(slots=[dict(what=i['what'], grams=float(i['grams'])) for i in items], next=0)
        return dict(code='OK', message='drum in the holder: ' + ' → '.join(f"{i['what']} {i['grams']:g} g" for i in items))

    def _do_drum_release(self, stir_seconds=0):
        if not self.drum or self.drum['next'] >= len(self.drum['slots']):
            return dict(code='REJECTED_PRECONDITION', message='no loaded drum compartment left')
        if stir_seconds:
            self.take_spatula()
        s = self.drum['slots'][self.drum['next']]
        self.drum['next'] += 1
        self.advance(1.5, stirring=self.hand == 'spatula')
        self.wok.add(s['what'], s['grams'], None)
        if stir_seconds:
            self.advance(stir_seconds, stirring=True)
            return dict(code='OK', message=f"released {s['what']} {s['grams']:g} g, then stirred {stir_seconds:g} s")
        return dict(code='OK', message=f"released {s['what']} {s['grams']:g} g")

    def _do_set_heat(self, level):
        self.wok.heat = float(level)
        self.advance(1, stirring=False)
        return dict(code='OK', message=f'heat {level:g}')

    def _do_stir(self, seconds):
        if not self.wok_has_food():
            return dict(code='REJECTED_PRECONDITION', message='no food in the wok to stir')
        self.take_spatula()
        self.advance(seconds, stirring=True)
        return dict(code='OK', message=f'stirred {seconds:g} s ({int(seconds // 3.6)} strokes)')

    def _do_flip_egg(self):
        if 'egg' not in self.wok.truth().get('items', {}):
            return dict(code='REJECTED_PRECONDITION', message='no egg in the wok')
        self.take_spatula()
        self.advance(4)
        self.wok.flip('egg')
        return dict(code='OK', message='egg turned over')

    def _do_tip_wok(self, into):
        r = self._need_heat_off('lifting the wok')
        if r:
            return r
        if self.wok_food_g() > MAX_FOOD_G:
            return dict(code='REJECTED_SAFETY', message='too heavy to lift')
        tgt = dict(plate=self.plate, holding_bowl=self.holding_bowl, oil_cup=self.oil_cup)[into]
        if into != 'plate' and tgt:
            return dict(code='REJECTED_PRECONDITION', message=f'{into} is not empty')
        if not self.wok.truth().get('items'):
            return dict(code='REJECTED_PRECONDITION', message='the wok is empty')
        self.park_spatula()
        self.advance(PLATE_S if into == 'plate' else SPOT2_S)
        tgt.update(self.wok.remove_all())
        return dict(code='OK', message=f'wok emptied into {into}: ' + ', '.join(sorted(tgt)))

    def _do_look(self):
        self.advance(1)
        return dict(code='OK', message='image and thermometer captured')

    def _do_wait(self, seconds):
        if seconds > HALF_POWER_PAUSE_S and self.wok.heat > 0.5 and self.wok_has_food():
            return dict(code='REJECTED_POLICY', message=f'with food in the wok, lower the heat to ≤ 0.5 before pausing '
                        f'longer than {HALF_POWER_PAUSE_S:g} s (R15 half-power policy)')
        self.advance(seconds)
        return dict(code='OK', message=f'waited {seconds:g} s')

    def _do_done(self, success, summary):
        self.done = True
        return dict(code='OK', message='mission finished')


def api_text():
    """Prompt section listing the skills (same registry as the gate)."""
    lines = ['Routines (predefined sequences; they run straight through without waiting for you):']
    for s in ROUTINES:
        a = ', '.join(f"{k}: {t}{'' if spec is None else ' ' + json.dumps(spec, ensure_ascii=False)}"
                      for k, (t, spec, d) in s.args.items())
        lines.append(f'- {s.name}({a}) [{s.seconds}] — {s.doc}')
    lines.append('Single skills (for anything the routines do not cover):')
    for s in SKILLS:
        a = ', '.join(f"{k}: {t}{'' if spec is None else ' ' + json.dumps(spec, ensure_ascii=False)}"
                      for k, (t, spec, d) in s.args.items())
        lines.append(f'- {s.name}({a}) [{s.seconds}] — {s.doc}' + (f' (not verified in sim: {s.unverified})' if s.unverified else ''))
    return '\n'.join(lines)


def write_api_md(path=ROOT / 'API.md'):
    rows = ['| Skill | Duration | Real hardware | Evidence in robot_rail sim | Not verified |', '|---|---|---|---|---|']
    for s in SKILLS:
        rows.append(f'| `{s.name}` | {s.seconds} | {s.hardware} | {s.evidence} | {s.unverified or "—"} |')
    Path(path).write_text('# Cooking skills Claude can call\n\nGenerated by `cook_api.write_api_md()`.\n\n'
                          + api_text() + '\n\n' + '\n'.join(rows) + '\n', encoding='utf-8')
