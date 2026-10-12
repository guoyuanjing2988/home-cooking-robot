"""Small public-evidence supplement; one foreground process/two threads, 180 s cap."""
from pathlib import Path
import json, hashlib, time, concurrent.futures
from fetch_evidence import get, repo_task
ROOT = Path(__file__).resolve().parent
URLS = {
 'price_ur5e_csu_2022': 'https://czzx.csu.edu.cn/csustatic/zbgshwfwl/20221213/3497.html',
 'price_fr3_ccgp_2025': 'https://www.ccgp.gov.cn/cggg/zygg/zbgg/202507/t20250701_24887100.htm',
 'price_850_ccgp_2025': 'https://www.ccgp.gov.cn/cggg/dfgg/zbgg/202512/t20251223_25972902.htm',
 'ufactory_joint_parameters': 'https://docs.supportarticle.ufactory.cc/support_articles/hardware/ufactory-joint-parameters.html',
 'ufactory_850_specs': 'https://docs.850.ufactory.cc/8.technical_specifications.html',
 'ufactory_850_safety': 'https://docs.850.ufactory.cc/1.safety.html',
 'ur5e_mount_loads': 'https://www.universal-robots.com/manuals/EN/HTML/SW10_6/Content/prod-usr-man/hardware/arm_e-Series/UR5e/H_g5_sections/mechanical_interface_g5/securing_arm.htm',
 'rm65_brakes': 'https://develop.realman-robotics.com/en/robot4th/robotParameter/RM65OntologyParameters/',
 'sick_scanner_cn_price': 'https://www.icdeal.com/product/117193367411220.html',
 'dh_pgc_placeholder_price': 'https://www.zgjdsbcyw.com/index.php?file=sell&homepage=18814357627a&itemid=5530',
}
def fetch(item):
 key,url=item
 try:
  data=get(url); (ROOT/'references'/f'{key}.html').write_bytes(data)
  return {'id':key,'url':url,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
 except Exception as e: return {'id':key,'url':url,'error':str(e)}
if __name__=='__main__':
 start=time.monotonic()
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  docs=list(pool.map(fetch,URLS.items()))
  repos=list(pool.map(repo_task,['JAKARobotics/jaka_ros2']))
 inputs={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT.parents[2]/'inputs').iterdir() if p.is_file()}
 out={'retrieved_date':'2026-10-07','documents':docs,'repositories':repos,'input_sha256':inputs,'elapsed_s':time.monotonic()-start,'max_network_threads':2}
 (ROOT/'results'/'supplement_manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'documents':[{k:v for k,v in d.items() if k in ('id','bytes','error')} for d in docs],'repositories':[{k:v for k,v in d.items() if k in ('repo','commit','error')} for d in repos],'elapsed_s':out['elapsed_s']},indent=2))
