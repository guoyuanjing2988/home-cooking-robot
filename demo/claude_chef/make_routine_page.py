"""Build the routine-library artifact page from routines/routines.json (+ the demo's executable routines).

Usage: python make_routine_page.py <out.html>
"""
import html
import json
import sys
from pathlib import Path

import cook_api

ROOT = Path(__file__).resolve().parent
LIB = json.load(open(ROOT.parent / 'routines' / 'routines.json', encoding='utf-8'))
EXEC = {s.name: dict(doc=s.doc, args={k: v[0] for k, v in s.args.items()}, seconds=s.seconds) for s in cook_api.ROUTINES}
RUN = None
for name in ('run05', 'run04'):
    p = ROOT / 'runs' / name / 'run.json'
    if p.exists():
        RUN = (name, json.load(open(p, encoding='utf-8')))
        break


def demo_sequence():
    if not RUN:
        return []
    out = []
    for d in RUN[1]['decisions']:
        a = d['decision']['action']
        out.append(dict(a=a, routine=a in EXEC, args={k: v for k, v in (d['decision'].get('args') or {}).items()
                                                       if k not in ('summary',)},
                        t=round(d['t']), ok=d['result']['ok'], steps=d['result'].get('steps') or [],
                        why=d['decision']['why']))
    return out


OWN = json.load(open(ROOT / 'gifs/routines/index.json'))
RELATED = {   # routines without their own GIF: a related checked motion clip
    'wok_grease': ('routines/season_wok.gif', 'same steps as season_wok'),
    'egg_set_and_hold': ('routines/flip_and_fry.gif', 'part of it: flip_and_fry'),
    'add_stir_fry': ('routines/stir_fry.gif', 'part of it: stir_fry'),
    'thicken': ('routines/drum_add_stir.gif', 'same steps as drum_add_stir'),
    'simmer_open': ('routines/drum_add_stir.gif', 'water from the drum, then stir'),
    'wash_wok': ('motions/wok_plate_rinse.gif', 'checked arm path: wok rinse at the sink (R17)'),
    'wok_fill_water': ('motions/wok_plate_rinse.gif', 'checked arm path: wok under the tap (R17)'),
    'blanch_lift': ('motions/spider.gif', 'checked arm path: spider scoop (R17)'),
    'fish_out_item': ('motions/spider.gif', 'checked arm path: spider scoop (R17)'),
    'poach_slices': ('motions/spider.gif', 'checked arm path: spider scoop (R17)'),
    'deep_fry': ('motions/spider.gif', 'spider scoop (R17, from the pot, not the fryer)'),
    'steam_plate': ('motions/lid_rack.gif', 'checked arm path: lid off into the rack (R17)'),
    'braise_lid': ('motions/lid_rack.gif', 'pot lid (R17); the wok lid is not checked'),
    'stew_pot': ('motions/lid_rack.gif', 'pot lid (R17); the stew pot lid is not checked'),
    'prep_cut': ('motions/tomato_prep.gif', 'checked arm path: tomato to the lever cutter (R11)'),
    'prep_peel': ('motions/carrot_prep.gif', 'checked arm path: carrot peel (R11)'),
    'prep_wash': ('motions/carrot_prep.gif', 'checked arm path: carrot wash (R11, old layout)'),
}
GIFS = {k: dict(src=v['file'], cap=v['arm_caption'], own=True, steps=v.get('steps', [])) for k, v in OWN.items()}
GIFS.update({k: dict(src=f, cap=c, own=False) for k, (f, c) in RELATED.items() if k not in GIFS})

ARMP = ROOT.parent / 'routines' / 'arm_impl.json'
ARM = json.load(open(ARMP, encoding='utf-8')) if ARMP.exists() else {}

data = dict(arm=ARM.get('routines', {}), sets=ARM.get('movement_sets', {}), armstats=ARM.get('stats', {}), gifs=GIFS, types=LIB.get('types', []), dishes=LIB.get('dishes', {}), stats=LIB.get('stats', {}),
            exec=EXEC, run=dict(name=RUN[0] if RUN else None, seq=demo_sequence(),
                                realtime=bool(RUN and RUN[1].get('realtime'))))
TEMPLATE = (ROOT / 'routine_page.html').read_text(encoding='utf-8')
page = TEMPLATE.replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False).replace('</', '<\\/'))
Path(sys.argv[1]).write_text(page, encoding='utf-8')
print(sys.argv[1], len(page) // 1024, 'KB', len(data['types']), 'types', len(data['dishes']), 'dishes')
