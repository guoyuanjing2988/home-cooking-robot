"""Pinned raw model excerpts only;meshes/includes are intentionally not installed."""
from pathlib import Path
import json, hashlib, concurrent.futures, time
from fetch_evidence import get, repo_task
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results'
repo=repo_task('UniversalRobots/Universal_Robots_ROS2_Description')
assert 'commit' in repo,repo
manifests=[json.loads((OUT/n).read_text(encoding='utf-8')) for n in ('evidence_manifest.json','supplement_manifest.json')]
repos={r['repo']:r for m in manifests for r in m['repositories'] if 'commit' in r}
repos[repo['repo']]=repo
choices={'jaka7':('JAKARobotics/jaka_ros2','src/jaka_description/urdf/jaka_zu7.urdf'),
 'ur5e':('google-deepmind/mujoco_menagerie','universal_robots_ur5e/ur5e.xml'),
 'cs66':('EliteRobots/Elite_Robots_CS_ROS2_Description','urdf/cs.urdf.xacro'),
 'uf850':('xArm-Developer/xarm_ros','xarm_description/urdf/uf850/uf850.urdf.xacro')}
dest=ROOT/'references'/'model_excerpts';dest.mkdir(exist_ok=True)
def fetch(item):
 name,(r,path)=item;commit=repos[r]['commit'];assert path in repos[r]['paths']
 url=f'https://raw.githubusercontent.com/{r}/{commit}/{path}'
 try:
  data=get(url);local=dest/(name+'_'+Path(path).name);local.write_bytes(data)
  return {'arm_id':name,'repo':r,'commit':commit,'path':path,'url':url,'local_path':str(local.relative_to(ROOT)),
   'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'not_standalone':True}
 except Exception as e:return {'arm_id':name,'url':url,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:downloads=list(pool.map(fetch,choices.items()))
(OUT/'model_excerpt_manifest.json').write_text(json.dumps({'date':'2026-10-07','repositories':[repo],'downloads':downloads},indent=2),encoding='utf-8')
print(json.dumps({'ur_repo_commit':repo['commit'],'ur_model_paths':[p for p in repo['paths'] if p in ('urdf/ur.urdf.xacro','config/ur3e/joint_limits.yaml')],'downloads':downloads},indent=2))
