"""Bounded public-source acquisition; reads legacy permanent scene only, never writes it."""
import os, subprocess, json, time, hashlib, urllib.request
from pathlib import Path
import xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent
SRC=HERE/'sources'; SRC.mkdir(parents=True,exist_ok=True)
def run(args,wd=None):
    return subprocess.run(args,cwd=wd,check=True,timeout=300,capture_output=True,text=True).stdout.strip()
def checkout(url,name,paths):
    dest=SRC/name
    if not (dest/'.git').exists():
        run(['git','clone','--depth','1','--filter=blob:none','--sparse',url,str(dest)])
    run(['git','sparse-checkout','set',*paths],dest)
    return dict(url=url,commit=run(['git','rev-parse','HEAD'],dest),paths=paths)
records={}
records['menagerie']=checkout('https://github.com/google-deepmind/mujoco_menagerie.git','menagerie',
 ['universal_robots_ur5e','ufactory_xarm7','franka_fr3'])
records['aubo']=checkout('https://github.com/AuboRobot/aubo_description.git','aubo_description',
 ['urdf','meshes/aubo_i5/collision'])
legacy=Path('C:/Users/admin/Documents/YJGames/robot_v5/board/sim/t05/ref_robots/models/r1pro_kitchen_galley.xml')
root=ET.parse(legacy).getroot(); w=root.find('worldbody')
permanent=ET.Element('mujoco',model='authoritative_permanent_kitchen'); world=ET.SubElement(permanent,'worldbody')
for e in w:
    if e.tag=='geom': world.append(e)
ET.ElementTree(permanent).write(SRC/'permanent_kitchen.xml',encoding='unicode')
meta=json.loads(legacy.with_suffix('.json').read_text())
(SRC/'permanent_scene.json').write_text(json.dumps(meta['scene'],indent=2))
records['permanent_scene']=dict(source=str(legacy),access='read-only extraction of fixed environment; no robot retained',
 sha256=hashlib.sha256(legacy.read_bytes()).hexdigest())
(SRC/'sources.json').write_text(json.dumps(records,indent=2))
print(json.dumps(records,indent=2))
