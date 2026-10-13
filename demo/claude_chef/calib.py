"""Calibration: can Claude judge the canonical wok_cam states the way the recipe needs? (python calib.py [tags...])"""
import json, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from claude_client import claude_json

OUT = Path(__file__).resolve().parent / 'out'
PROMPT = ("You are the eyes of a cooking robot making 西红柿炒蛋 (tomato and egg stir-fry, Wang Gang's recipe). "
          "The image is from a colour camera under the range hood looking down into the wok. Judge only from the image; "
          "use null for questions about food that is not in the wok.\n"
          "- oil_smoking: is the oil/wok smoking (too hot)?\n"
          "- egg_ready_to_flip: Wang Gang fries the beaten egg as a sheet and flips it 'when the egg is consolidated'. Is it consolidated enough to flip now?\n"
          "- egg_burning: is the egg burning (dark brown/black)?\n"
          "- tomato_soft: Wang Gang simmers the tomato 'until the tomatoes are soft'. Are they soft (collapsed, losing shape)?\n"
          "- sauce_thickened: after starch water he waits 'until it has thickened'. Is the sauce thickened (glossy, clinging)?\n"
          "Then describe in one sentence what you see.")
SCHEMA = {"type": "object", "additionalProperties": False,
          "required": ["oil_smoking", "egg_ready_to_flip", "egg_burning", "tomato_soft", "sauce_thickened", "seen"],
          "properties": {**{k: {"type": ["boolean", "null"]} for k in
                            ("oil_smoking", "egg_ready_to_flip", "egg_burning", "tomato_soft", "sauce_thickened")},
                         "seen": {"type": "string"}}}
# expected answers (from the truth numbers); keys not listed are not scored
EXPECT = {'oil_smoking': dict(oil_smoking=True), 'oil_120': dict(oil_smoking=False),
          'egg_raw': dict(egg_ready_to_flip=False, egg_burning=False), 'egg_half': dict(egg_ready_to_flip=False, egg_burning=False),
          'egg_flip_ready': dict(egg_ready_to_flip=True, egg_burning=False), 'egg_burnt': dict(egg_burning=True),
          'sauce_thin_boil': dict(tomato_soft=False, sauce_thickened=False), 'tomato_soft': dict(tomato_soft=True, sauce_thickened=False),
          'sauce_thick': dict(sauce_thickened=True), 'oil_185': dict(oil_smoking=False), 'egg_golden': dict(egg_burning=False),
          'tomato_mid': dict(tomato_soft=False), 'starch_in': dict(tomato_soft=True, sauce_thickened=False), 'tomato_soft_still': dict(tomato_soft=True, sauce_thickened=False)}


def ask(tag, rnd):
    obj, meta = claude_json(PROMPT, SCHEMA, f'wokcam_calib_r{rnd}_{tag}', images=[OUT / f'wok_{tag}.png'], effort='low')
    return tag, obj, meta


if __name__ == '__main__':
    rnd = int(time.time()) % 100000
    tags = sys.argv[1:] or list(EXPECT)
    with ThreadPoolExecutor(3) as ex:
        res = list(ex.map(lambda t: ask(t, rnd), tags))
    rows = []
    for tag, obj, meta in res:
        ok = None if obj is None else all(obj.get(k) == v for k, v in EXPECT[tag].items())
        rows.append(dict(tag=tag, expect=EXPECT[tag], answer=obj, ok=ok, s=meta.get('seconds')))
        print(tag, 'OK' if ok else 'XX', json.dumps(obj, ensure_ascii=False), meta.get('seconds'), 's')
    with open(OUT / 'calib_log.jsonl', 'a') as fh:
        for r in rows: fh.write(json.dumps(dict(round=rnd, **r), ensure_ascii=False) + '\n')
