import json,csv
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';A=H/'audit'
rows=[
 ['baseline','R03 unchanged','19/27','95/105','39/105','0/104','Copied prior result, not R04 pass evidence'],
 ['base_restore','Original UR5e base meshes retained','not scored','not scored','','','New base/frame interference exposed; beam setback required'],
 ['distance','GJK dual versus independent hull QP','','','','','11.33362169/10.37104875mm reproduced; absent-contact20mm claim rejected'],
 ['repair1','Full brush shifted85mm; upright cups, tilted wipe','not scored','92/105','','','Root washes, tomato delivery and wiping repaired; final frame still pending'],
 ['repair3','Raise crossbar/left pad trial','invalid','invalid','','','Cancelled whole-scene cabinet collision; not retained'],
 ['repair4','Lower crossbars, move right offset plate','not scored','101/105','','','Base and frame clear; four target strokes remain'],
 ['repair5','Transverse upright cup wash','not scored','103/105 predicted','','','Q13:1/96 solver solutions; Q21:32/96; final independent replay later'],
 ['repair6','Carrot y435 jawY; colander(-470,230,900)mm','27/27','105/105','','','Q12carrot5/192; Q16soak48/192; selected105 independently verified'],
 ['motion_initial','Global2m hinge certificate','','','2/105','0/104','Finite RRT budgets; raw attempts archived under audit/'],
 ['motion_refined','Pair ancestor displacement certificate','','','2/105','0/104','8179 state evaluations; moving intended-face continuous proof still missing'],
 ['passing','Exact convex swept relative carriage translation','','','','','1 seed/1 solution/1 continuously verified full passing route'],
 ['persistent','Single4-food scene and explicit state ledger','','','','','295 events,157 expanded strokes,293 missing event trajectories; single-owner invariant passes'],
 ['idle','1800 end-fold starts plus two7000 retract trials','','','','','Working cell fails doors/human aisle; alternate retract snapshots unqualified'],
 ['arms','xArm main plus JAKA5/7 raw model screens','','','','','96 starts/task; JAKA inertia/catalogue mismatch rejects hardware admission'],
 ['time','Conservative L+aux resource charged','','','','','85.86min planned;51.333min machine+inspection+clean lower bound; verified time null'],
 ['cost','Five home-tier budgets','','','','','472879.95 best static;349829.95 lowest unqualified; cheapest passing null']]
with (O/'iterations.csv').open('w',newline='',encoding='utf-8') as f:w=csv.writer(f);w.writerow(['iteration','change','phases','static_strokes','internal_paths','meal_connections','outcome']);w.writerows(rows)
