import json
import solver as s
import motion_check as mo
H=s.HERE;D=H/'models/witnesses';D.mkdir(exist_ok=True);ws=json.loads((H/'results/best.json').read_text())['witnesses']
for ph in s.P['phases']:
 for sg in ph['segments']:
  key=ph['id']+'__'+sg['label'].replace(' ','_');ch=s.Checker(ph,sg)
  (D/(key+'.xml')).write_text(ch.xml);(D/(key+'.json')).write_text(json.dumps(ws[key],indent=2))
ch,hands=mo.empty_cell();(H/'models/passing_full.xml').write_text(ch.xml);print('standalone witness models',len(ws),flush=True)
