"""Installation-only diagnostics; no new phase admission gates."""
import sys,json,math
from pathlib import Path
import numpy as np,mujoco
HERE=Path(__file__).resolve().parent;CONCEPT=HERE.parent/'concept';sys.path.insert(0,str(CONCEPT))
import checker as ck
best=json.loads((CONCEPT/'results/best.json').read_text());ck.configure(best['config'])
p=ck.P06();c=ck.Checker(p,p['segments'][0]);m,d=c.m,c.d
park=json.loads((CONCEPT/'renders/parked.validation.json').read_text());d.qpos[:]=park['q'];mujoco.mj_forward(m,d)
doors=[g for g in range(m.ngeom) if m.geom(g).name.startswith('cabinet_door_sweep_')]
robot=[g for g in range(m.ngeom) if c.robot[g]];hits=[];nearest=[]
for door in doors:
    pairs=[]
    for g in robot:
        if m.geom_contype[g]==0:continue
        dist=mujoco.mj_geomDistance(m,d,g,door,1.,None)
        pair=dict(pair=[m.geom(g).name,m.geom(door).name],gap_mm=1000*dist)
        pairs.append(pair)
        if dist<.01-1e-6:hits.append(pair)
    nearest.append(min(pairs,key=lambda row:row['gap_mm']))
power_radius=.078;power_od=.0104
beam30x70x3_I=(.03*.07**3-(.03-.006)*(.07-.006)**3)/12
record=dict(parked_door_direct_distance_hits=hits,nearest_parked_door_pairs=nearest,
    note='Direct geom distances include arms despite door collision masks only addressing mounting hardware. Representative door boxes, not measured hinge CAD.',
    cable=dict(power_od_m=power_od,minimum_radius_m=power_radius,minimum_U_turn_outer_dimension_m=2*power_radius+power_od,modeled_loop_xyz_m=[.2,.025,.06],modeled_transverse_diagonal_m=math.hypot(.025,.06),envelope_contains_longitudinal_U_turn=False),
    beam_illustration=dict(section='Assumed steel RHS30x70x3mm; NOT selected in concept',E_Pa=200e9,I_m4=beam30x70x3_I,point_force_N=240,overhang_to_parked_carriage_m=2.12-.55,point_load_deflection_mm=1000*240*(2.12-.55)**3/(3*200e9*beam30x70x3_I),note='Illustration of sensitivity only; omits self-weight, arm moment, torsion, brackets, dynamic stops and source mass discrepancy.'),
    exact_full_payload_check_witness=None)
# Reproduce the published capacity diagnostic while leaving original held masses untouched.
r=json.loads((CONCEPT/'results/final'/best['id']/'P06.json').read_text());seg=r['rows'][52]['segments'][0];q=np.array(seg['poses'][0]['q'])
hd=r['definition']['segments'][0]['poses'][0]['R'];force=[-60,10,20]
record['exact_full_payload_check_witness']=dict(phase='P06',seed=52,pose=0,force_N=force,held_mass_kg=3.,torque=c.torque(q,dict(hd,held_kg=3.),force),check_is_diagnostic_not_phase_gate=True)
(HERE/'audit/installation.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record,indent=2))
