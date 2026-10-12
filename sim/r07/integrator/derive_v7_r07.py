from pathlib import Path
H=Path(__file__).resolve().parent
for old,new in [('static_v4_r07.py','static_v7_r07.py'),('motion_v4_r07.py','motion_v7_r07.py'),('fresh_v4_r07.py','fresh_v7_r07.py')]:
 text=(H/old).read_text().replace('runtime_v4_r07','runtime_v7_r07').replace("'static_v4'","'static_v7'").replace("/static_v4/","/static_v7/").replace("'motion_v4'","'motion_v7'").replace("'final_static_v4'","'final_static_v7'")
 if old.startswith('static'):
  text=text.replace("([('L52',index)] if int(v.ID[1:])>=53 else [])", "([('L53',index)] if int(v.ID[1:])>=54 else [])+([('L52',index)] if int(v.ID[1:])>=53 else [])")
  text=text.replace("('L45','L51','L52')", "('L45','L51','L52','L53')")
  text=text.replace("('static_v7' if donor_id", "('static_v4' if donor_id")
  text=text.replace("candidate['poses'][0]['q'][:ch.m.nq]", "candidate['poses'][0]['q'][:ch.m.nq]")
 (H/new).write_text(text)
text=(H/'reach_v4_r07.py').read_text();text=text.replace('tr,meta=rt.s.model.build(dict(cfg,transport_only=True))',"tr,meta=rt.s.model.build(dict(cfg,transport_only=True))\nfor j in tr.getroot().findall('.//joint'):\n if j.get('name')=='R_elbow_joint':j.set('range','-2.792526803190927 2.792526803190927')")
(H/'reach_v7_r07.py').write_text(text)
