"""Disjoint CPU render batches; each accepted image is decoded before reuse."""
import json, shutil, subprocess, sys, time
from pathlib import Path
from PIL import Image
H = Path(__file__).resolve().parent
R = H/'renders'
ID, lane = sys.argv[1], int(sys.argv[2])
stride = int(sys.argv[3]) if len(sys.argv)>3 else 4
manifest = json.loads((R/'manifest_v7.json').read_text())
started = time.monotonic()
for index in range(lane, len(manifest['views']), stride):
    view = manifest['views'][index]
    assert view['scene'].startswith('v7_'+ID+'/')
    target = R/view['image']
    valid = False
    if target.exists():
        try:
            with Image.open(target) as image:
                image.verify()
            valid = True
        except (OSError, SyntaxError):
            valid = False
    if not valid:
        if time.monotonic()-started>760:
            print('RENDER_CHUNK_DEFERRED', view['name'], flush=True)
            break
        print('RENDER_START', view['name'], flush=True)
        with (H/'audit'/f'v7_{ID}_render_{view["name"]}.log').open('w', encoding='utf-8') as log:
            subprocess.run([
                'C:/Program Files/Blender Foundation/Blender 4.5/blender.exe',
                '--background', '--factory-startup', '--threads', '1',
                '--python', str(H/'blender_render_v7_r07.py'), '--', str(R/view['scene'])
            ], stdout=log, stderr=subprocess.STDOUT, timeout=300, check=True)
        with Image.open(target) as image:
            image.verify()
    shutil.copy2(target, R/(view['name']+'.png'))
    print('RENDER_COMPLETE', view['name'], target.stat().st_size, flush=True)
print('RENDER_LANE_CHUNK', lane, round(time.monotonic()-started, 2), flush=True)
