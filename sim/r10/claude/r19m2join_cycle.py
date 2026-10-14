"""R19 #42 (R19_M2JOIN.md): r19stir_cycle.py with the cycle's chain restricted to the spatula hand-off's IK branch. New file.
r19stir2_join.join (unchanged) needs the stir cycle's start H_stir0 on the IK branch the spatula chain ends on, with jaw
sense -1 (its stir scene, r19stir2_join.SIGN); otherwise the join fails and no fallback is taken. r19stir_cycle.cycle
takes the cheapest chain (cost_A) of all jaw senses and branches, and on the m2 mounts that chain starts on another
branch (UR5e: wrist flipped) or the other jaw sense (FR5). This wrapper runs r19stir_cycle.py from its source with three
textual changes (each asserted to occur once), everything else unchanged (follow, returns, certification, gates, time
law, library entry):
 - cycle: only chains with jaw sense KSIGN (default -1) whose stroke-0 working part STARTS on the branch BR0
   (elbow, wrist = signs of sin q3, sin q5) and, if Q1 is given, with q1 within 90 deg (mod 2pi) of Q1 (shoulder);
   the cheapest of those (cost_A) is taken, as before;
 - OUTDIR=<dir> replaces results/r19/stir/cycle_<arm> (works.json, returns.json, caches, cycle.json), default unchanged;
 - LIBOUT=<file> replaces results/r19/stir/lib_stir_cycle_<arm>.json, default unchanged (an existing file is renamed
   first by r19stir_cycle.write_outputs, as before).
The stages works / returns take OUTDIR (and r19stir_cycle's own REACH=) too. The patched source is executed at module
level, so the spawned pool workers (which re-run this file as __mp_main__) run the same code.
python r19m2join_cycle.py works|returns|cycle ARM=<arm> [KSIGN=-1] [BR0=-1,1] [Q1=<deg>] [OUTDIR=..] [LIBOUT=..]
       [REACH=<template with {i:03d}>] [ROUNDS=.. PART=.. FRESH=1 WORKERS=..]   (the r19stir_cycle options)"""
import sys,os,json
sys.path.insert(0,'.')
_s=open('r19stir_cycle.py',encoding='utf-8').read()
_R=[("OUT=f'results/r19/stir/cycle_{ARM}'","OUT=KV.get('OUTDIR',f'results/r19/stir/cycle_{ARM}')"),
    ("CH=sorted([c for c in RJ['chains'] if c['cost_A'] is not None],key=lambda c:c['cost_A'])",
     "CH=sorted([c for c in RJ['chains'] if c['cost_A'] is not None and _m2join_keep(G,c)],key=lambda c:c['cost_A'])"),
    ("fn=f'results/r19/stir/lib_stir_cycle_{ARM}.json'","fn=KV.get('LIBOUT',f'results/r19/stir/lib_stir_cycle_{ARM}.json')")]
for a,b in _R:
 assert _s.count(a)==1,('r19stir_cycle.py changed',a);_s=_s.replace(a,b)
def _m2join_br(q):
 import numpy as np
 q=np.asarray(q,float)[3:9];return [int(np.sign(np.sin(q[2]))),int(np.sign(np.sin(q[4])))]
def _m2join_keep(G,c):
 """jaw sense, stroke-0 start branch (and shoulder) of a chain against KSIGN / BR0 / Q1"""
 import numpy as np
 kv=dict(a.split('=',1) for a in sys.argv[2:] if '=' in a)
 if c['sign']!=int(kv.get('KSIGN',-1)):return False
 q=G[(0,c['sign'])][c['combo'][0]]['rep']['states'][0]
 if 'BR0' in kv and _m2join_br(q)!=[int(x) for x in kv['BR0'].split(',')]:return False
 if 'Q1' in kv and abs((np.degrees(q[3])-float(kv['Q1'])+180.)%360.-180.)>90.:return False
 return True
exec(compile(_s,'r19stir_cycle.py','exec'))
