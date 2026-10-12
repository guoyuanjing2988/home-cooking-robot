"""Public-only retrieval. One foreground process, two network threads, 420 s deadline."""
from pathlib import Path
import urllib.request, json, time, concurrent.futures, subprocess, hashlib
ROOT = Path(__file__).resolve().parent
START = time.monotonic()
PDFS = {
 'jaka_zu_v11': 'https://www.jaka.com/profile/upload/2025/11/25/20251125172527A001.pdf',
 'franka_fr3': 'https://www.franka.de/hubfs/Product%20Manual%20Franka%20Research%203_R02210_1.5_EN-1.pdf',
 'rokae_cr7c': 'https://static.rokae.com/Downloads/Manual/xMate%20CR7-C%20Hardware%20Installation%20Manual.pdf',
 'dobot_cr5': 'https://download.dobot.cc/dobotscstudio/cr5/en/Dobot-CR5-Hardware-User-Guide.pdf',
 'kinova_gen3': 'https://www.kinovarobotics.com/uploads/Kinova_Onepager_Gen3_2024_EN.pdf',
 'ufactory_price_20240809': 'https://assets.zyrosite.com/m6Lb1n8yxOiXQr53/ufactory-product-list-dOqDEyxRogfNgOKP.pdf',
 'xarm_manual': 'https://www.ufactory.cc/wp-content/uploads/2023/04/xArm-User-Manual-V1.11.0.pdf',
}
REPOS = ['google-deepmind/mujoco_menagerie', 'xArm-Developer/xarm_ros', 'frankarobotics/franka_description',
 'Kinovarobotics/ros_kortex', 'EliteRobots/Elite_Robots_CS_ROS2_Description', 'AuboRobot/aubo_description',
 'Dobot-Arm/TCP-IP-ROS-6AXis', 'RokaeRobot/rokae_ros2', 'RealManRobot/ros2_rm_robot',
 'JakaCobot/jaka_ros2', 'JakaCobot/jaka_ros']
def get(url):
 if time.monotonic()-START > 390: raise TimeoutError('whole-run deadline')
 req=urllib.request.Request(url,headers={'User-Agent':'robot-rail-market-research/1.0','Accept':'application/vnd.github+json' if 'api.github.com' in url else '*/*'})
 with urllib.request.urlopen(req,timeout=18) as response:
  data=response.read(18*1024*1024)
  if len(data)>=18*1024*1024: raise ValueError('download size limit')
  return data
def pdf_task(item):
 name,url=item
 try:
  data=get(url)
  if not data.startswith(b'%PDF'): raise ValueError('not PDF')
  path=ROOT/'references'/f'{name}.pdf'; path.write_bytes(data)
  p=subprocess.run(['pdftotext','-layout',str(path),str(path.with_suffix('.txt'))],capture_output=True,timeout=25)
  return {'id':name,'url':url,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'text_exit':p.returncode}
 except Exception as e: return {'id':name,'url':url,'error':str(e)}
def repo_task(repo):
 try:
  meta=json.loads(get('https://api.github.com/repos/'+repo)); branch=meta['default_branch']
  commit=json.loads(get('https://api.github.com/repos/'+repo+'/commits/'+branch))['sha']
  tree=json.loads(get('https://api.github.com/repos/'+repo+'/git/trees/'+commit+'?recursive=1'))
  paths=[x['path'] for x in tree['tree'] if x.get('type')=='blob' and (x['path'].endswith(('.urdf','.xacro','.xml','.yaml')))]
  if repo.endswith('mujoco_menagerie'): paths=[x for x in paths if any(k in x.lower() for k in ['ur3e','ur5e','fr3','kinova','xarm','lite6','ufactory'])]
  return {'repo':repo,'branch':branch,'commit':commit,'paths':paths,'tree_truncated':tree.get('truncated',False),'url':'https://github.com/'+repo+'/tree/'+commit}
 except Exception as e:return {'repo':repo,'error':str(e)}
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
  pdf=list(ex.map(pdf_task,PDFS.items()))
  repos=list(ex.map(repo_task,REPOS))
 result={'retrieved_date':'2026-10-07','pdfs':pdf,'repositories':repos,'elapsed_s':time.monotonic()-START,'max_network_threads':2}
 (ROOT/'results'/'evidence_manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'pdfs':[{k:v for k,v in x.items() if k in ['id','bytes','error']} for x in pdf], 'repos':[{k:v for k,v in x.items() if k in ['repo','commit','error']} for x in repos], 'elapsed_s':result['elapsed_s']},indent=2))
