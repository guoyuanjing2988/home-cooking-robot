"""R19 #36 part 2: routing SCREEN of many candidate tool-connector runs at once (new file; never a certificate).
Loads candidate runs (r19cable2_tc ROUTES-style specs) from a JSON file, registers them as routings of r19cable and as one
screening arm option '<base>c_TCX' (every candidate its own geom group 'cable.<key>'), then runs r19cable_check.py unchanged
(use CABLEONLY=1: only the cable groups' pairs are evaluated, with the checker's rules). Writes where r19cable_check writes
(results/r19/cable/<mode>/<name>__<base>c_TCX_cableonly.json); TAG= keeps hub runs apart.
python r19cable2_screen.py <mode> CANDS=<json> <r19cable_check.py arguments> ARM=<ur5e_enc2_pgc|fr5_j6_pgc_sp20>c_TCX CABLEONLY=1"""
import sys,json
sys.path.insert(0,'.')
_KV=dict(a.split('=',1) for a in sys.argv[2:] if '=' in a)
import r19cable2_tc as _TC,r19cable as _CAB
_C=json.load(open(_KV['CANDS']))
for _k,_s in _C.items():
 _TC.ROUTES[_k]=_s;_CAB.ROUTINGS[_k]=dict(_CAB.ROUTINGS[_s['_base']],tc=_k)
_CAB.SCREENS['TCX']=list(_C)
import arms as _arms
for _b in ('ur5e_enc2_pgc','fr5_j6_pgc_sp20'):_arms.ARMS[_b+'c_TCX']=dict(_arms.ARMS[_b],name=_arms.ARMS[_b]['name']+' + tool-connector run candidates (screen)',cable='TCX',cable_source='R19_CABLE2.md')
import r19cable_check as _RC
if __name__=='__main__':_RC.main()
