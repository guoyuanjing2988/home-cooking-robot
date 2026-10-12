"""Independent STEP import and valid-solid/volume check with FreeCAD."""
import FreeCAD as App, Part, json, os
HERE=os.path.dirname(os.path.abspath(__file__))
m=json.load(open(os.path.join(HERE,'cad_manifest.json'),encoding='utf-8'))
rows=[]
for p in m['parts']:
    s=Part.Shape();s.read(os.path.join(HERE,p['step_file']))
    row=dict(id=p['id'],valid=s.isValid(),solid_count=len(s.Solids),volume_mm3=s.Volume,volume_error_fraction=abs(s.Volume-p['volume_mm3'])/p['volume_mm3'])
    assert row['valid'] and row['solid_count']>0 and row['volume_error_fraction']<1e-5,row
    rows.append(row)
json.dump(dict(status='pass',parts=rows),open(os.path.join(HERE,'..','audit','step_roundtrip.json'),'w'),indent=2)
print('STEP_ROUNDTRIP_PASS18')
