"""One holder geometry refinement, recorded as additional configurations."""
import json
from pathlib import Path
from run import identifier,static_gate
import checker as ck
HERE=Path(__file__).resolve().parent;p=HERE/'results/configs.json';entries=json.loads(p.read_text())
for count in (2,3):
    c=dict(arm='xArm6',count=count,height=.45,orientation='down30',standoff=.25,hanging=False,grip_extension=.11)
    cid=identifier(c)
    if not any(e['id']==cid for e in entries):entries.append(dict(id=cid,config=c,static_hits=static_gate(c)))
    ck.json_write(HERE/'results'/f'config_xArm6x{count}.json',c)
ck.json_write(p,entries)
print('CONFIGS',len(entries))
