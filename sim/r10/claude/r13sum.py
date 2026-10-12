"""Summarise results/r13/*.json (optionally filtered by a substring)."""
import json,glob,sys
flt=sys.argv[1] if len(sys.argv)>1 else ''
for p in sorted(glob.glob('results/r13/*.json')):
 if flt not in p:continue
 r=json.load(open(p))
 if 'max_slip_mm' not in r:print(f"{p[12:-5]:48s} {r.get('reason')}");continue
 print(f"{p[12:-5]:48s} {'OK ' if r['ok'] else 'BAD'} set {r['set']:2s} {r['mode']:5s}{r['F']:6.1f} need {r['need_N']:6.1f} fN {r['finger_N_10ms_max']:6.1f}/{r['dmg']:<4} slip {r['max_slip_mm']:7.1f} {r['max_slip_deg']:6.1f}d M {r['moment_Nm_10ms_max']:5.2f} sc {r['scene_contact_N_max']:6.1f} wloc {r.get('width_local_mm')} above {r['grasp_above_centre_mm']} {','.join(r['fail'])}")
