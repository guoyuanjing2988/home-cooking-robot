"""Claude as the cook: every step it sees the sensors + the wok camera, reasons, and picks one skill.

Usage: python chef_agent.py <run_name> [--max-steps 60] [--seed 0] [--effort medium]
Output: runs/<run_name>/run.json (decisions, gate results, hidden truth per step) + wok images.
"""
from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path

import cook_api
from claude_client import claude_json

ROOT = Path(__file__).resolve().parent
RECIPES = ROOT.parent / 'robot_rail' / 'research' / 'wanggang_cooking.json'


def recipe_text(rid='xihongshichaodan'):
    r = next(x for x in json.load(open(RECIPES, encoding='utf-8'))['recipes'] if x['id'] == rid)
    lines = [f"{r['dish']} — Wang Gang (美食作家王刚), {r['url']}. His words, phase by phase:"]
    for i, p in enumerate(r['phases'], 1):
        heat = ', '.join(p['heat']) or 'not stated'
        lines.append(f"{i}. {p['action']} (heat: {heat}): \"{p['quote']}\"")
    lines.append('Amounts from his video: 3 eggs (+ 1 g white vinegar, skipped here); tomato ~300 g; ketchup 5 g; '
                 'water "adequate"; salt 1 g + sugar 1 g; starch water to thicken; a splash of oil (明油).')
    return '\n'.join(lines)


SYSTEM = """You are the cook. You control a one-arm kitchen robot (UR5e on a cart, induction wok, seasoning station,
fridge) only through the skills below, one call per turn. Your goal: cook Wang Gang's dish exactly in his spirit and
plate it, safely.

{recipe}

Skills (a deterministic gate checks every call; a refused call costs nothing and tells you why). Prefer the
routines: each is a predefined sequence that runs straight through, so nothing waits for your next decision. Use single
skills only for what no routine covers:
{api}

How the world works:
- Time only passes while a skill runs. The cooker keeps heating while the arm does other work, so food can burn
  while you are busy elsewhere. Prepare what you can (cold box, tomato wedges, cups, drum) before turning the heat on.
- Anything that puts the arm over the wok (pour_into_wok, load_drum, tip_wok) needs set_heat(0) first (离火).
  Heat off with food in loses about 6 °C in 5 s. drum_release works with the heat on and without the arm.
- You never see hidden numbers. You judge doneness like Wang Gang does: from the thermometer (oil temperature)
  and the wok camera image (colour, gloss, bubbles, shape of the egg/tomato, thickness of the sauce).
- One cup per item; 6 cups; the holding bowl keeps food you take out to add back later.
- Safety: smoke detector at 210 °C; the stove guard cuts the power at 250 °C. Avoid both.{realtime}

Answer with JSON only: observe = what you see in the image and sensors (one or two sentences, concrete);
why = why this is the right next move, tied to Wang Gang's cue (≤ 60 words, written for the audience watching the
demo); action + args; expect = what you expect to see after it."""

ARGS_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "what": {"type": "string"}, "grams": {"type": "number"}, "source": {"type": "string"},
        "items": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                                             "required": ["what", "grams"],
                                             "properties": {"what": {"type": "string"}, "grams": {"type": "number"}}}},
        "level": {"type": "number"}, "seconds": {"type": "number"}, "into": {"type": "string"},
        "target_C": {"type": "number"}, "tomatoes": {"type": "number"}, "stir_seconds": {"type": "number"},
        "cup": {"type": "string"}, "fry_level": {"type": "number"},
        "cups": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["what", "grams"],
                                            "properties": {"what": {"type": "string"}, "grams": {"type": "number"}}}},
        "drum": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["what", "grams"],
                                            "properties": {"what": {"type": "string"}, "grams": {"type": "number"}}}},
        "success": {"type": "boolean"}, "summary": {"type": "string"}}}
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["observe", "why", "action", "args", "expect"],
          "properties": {"observe": {"type": "string"}, "why": {"type": "string"},
                         "action": {"type": "string", "enum": [s.name for s in cook_api.ROUTINES + cook_api.SKILLS]},
                         "args": ARGS_SCHEMA, "expect": {"type": "string"}}}


REALTIME = False
THINK_CAP_S = 30.0          # one client retry once took 193 s; real deployments would time out and hold a safe state
REALTIME_NOTE = '''
- Real time: the kitchen does not wait for you. Each decision takes you about 10 s and the cooker keeps running
  meanwhile (no stirring). The image you get is from before you started thinking. When timing is tight, lower the
  heat first or pick a longer skill.'''


def brief(step):
    r = step['result']
    s = r['sensors']
    th = s.get('thermo_C')
    return (f"t={s['t_s']:.0f}s {step['action']}({json.dumps(step['args'], ensure_ascii=False)}) -> {r['code']}: "
            f"{r['message']} | thermo={'—' if th is None else f'{th:.0f}°C'} heat={s.get('heat')} "
            f"load={s.get('load_g')}g smoke={s['smoke_detector']}")


def prompt_for(k, history, last):
    parts = [SYSTEM.format(recipe=recipe_text(), api=cook_api.api_text(), realtime=REALTIME_NOTE if REALTIME else '')]
    if history:
        parts.append('Your previous calls (oldest first):\n' + '\n'.join(brief(h) for h in history[-25:]))
    if last:
        parts.append('Latest result:\n' + json.dumps({k2: v for k2, v in last['result'].items() if k2 != 'image'},
                                                     ensure_ascii=False))
    else:
        parts.append('Start. The kitchen state: ' + json.dumps(k.kitchen_view(), ensure_ascii=False)
                     + '. The wok is clean, cold and empty; the cooker is off.')
    parts.append('Choose the next call.')
    return '\n\n'.join(parts)


def run(name, max_steps=60, seed=0, effort='medium', resume=False):
    out = ROOT / 'runs' / name
    old = json.load(open(out / 'run.json', encoding='utf-8'))['decisions'] if resume and (out / 'run.json').exists() else []
    if out.exists() and not old:
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    k = cook_api.Kitchen(seed=seed)
    decisions, last = [], None
    for d in old:                                 # replay recorded decisions: the kitchen model is deterministic
        k.advance(d.get('think_s') or 0.0, stirring=False)
        res = k.call(d['decision']['action'], d['decision'].get('args') or {})
        assert res['code'] == d['result']['code'], f"replay diverged at step {d['step']}"
        if res.get('image'):
            res['image'] = d['result'].get('image', res['image'])
            k.log[-1]['result']['image'] = res['image']
        last = k.log[-1]
        decisions.append({**d, 'result': res, 'truth': last['truth'], 't': last['t']})
    if old:
        print(f'resumed after {len(old)} recorded decisions, kitchen t={k.t:.0f}s', flush=True)
    for i in range(len(old), max_steps):
        imgs = [last['result']['image']] if last and last['result'].get('image') else []
        t0 = time.time()
        dec, meta = claude_json(prompt_for(k, k.log, last), SCHEMA, f'{name}_{i:03d}', images=imgs,
                                purpose='cook_decision', effort=effort)
        if dec is None:
            print('claude call failed', meta)
            break
        think = 0.0
        if REALTIME:                              # the cooker keeps running while Claude decides
            think = min(float(meta.get('seconds') or 0), THINK_CAP_S)
            k.advance(think, stirring=False)
        res = k.call(dec['action'], dec.get('args') or {})
        if res.get('image'):                      # keep the image with the run
            dst = out / Path(res['image']).name
            shutil.copy(res['image'], dst)
            res['image'] = str(dst)
            k.log[-1]['result']['image'] = str(dst)
        last = k.log[-1]
        decisions.append(dict(step=i, decision=dec, seen_image=imgs[0] if imgs else None, claude=meta, think_s=think,
                              result=res, truth=last['truth'], t=last['t']))
        print(f"[{i:02d} {time.time() - t0:4.1f}s] {brief(last)}\n      why: {dec['why']}", flush=True)
        json.dump(dict(name=name, seed=seed, realtime=REALTIME, decisions=decisions, events=k.events,
                       final=dict(plate=k.plate, holding_bowl=k.holding_bowl, t=k.t)),
                  open(out / 'run.json', 'w'), ensure_ascii=False, indent=1, default=str)
        if k.done:
            break
    return out / 'run.json'


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('name')
    ap.add_argument('--max-steps', type=int, default=60)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--effort', default='medium')
    ap.add_argument('--realtime', action='store_true', help='kitchen time also passes while Claude decides')
    ap.add_argument('--resume', action='store_true', help='replay runs/<name>/run.json, then continue')
    a = ap.parse_args()
    REALTIME = a.realtime
    print(run(a.name, a.max_steps, a.seed, a.effort, a.resume))
