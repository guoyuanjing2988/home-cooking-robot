"""Finish a timed-out staging replay without changing geometry or admission gates."""
import os, sys, json, time, copy, hashlib, math
from pathlib import Path
os.environ['R07_LAYOUT'] = sys.argv[1]
import numpy as np
import mujoco
import runtime_v7_r07 as v
from motion_v7_r07 import Planner
from point_bound import PointBound

ID, mode, candidate = sys.argv[1], sys.argv[2], int(sys.argv[3])
H, O = v.H, v.O
source = O/'layouts'/f'{ID}_{mode}_high_front_v7.json'
original = json.loads(source.read_text())
prior = next(a for a in original['attempts'] if a['candidate'] == candidate)
assert prior['edges'][-1]['fresh_replay']['blocker']['reason'] == 'independent replay timeout'
index = 58 if mode == 'return' else 0
ch = v.scene(index)
ch.xml = (H/original['model_xml']).read_text()
assert hashlib.sha256(ch.xml.encode()).hexdigest() == original['model_sha256']
ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml))
ch.hands = {}; ch.allowed = []; ch.contact_windows = []; ch.working_stroke = False
ch.search_carriage = True; ch.lock_initial_carriage = False; ch.night_robust = False
pb = PointBound(ch)
row = copy.deepcopy(prior)
row.update(edges=[], states=[], pass_=False)
row['replay_continuation'] = dict(reason='Complete the independent replay that exhausted its former 60 s limit',
    original_file=str(source.relative_to(H)), original_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    per_edge_replay_budget_s=240, planner_budget_s=65, geometry_and_gates_unchanged=True)
points = [np.array(row['start_q']), np.array(row['stage_q'])]
alignment = row.get('carriage_alignment', {})
if alignment.get('clear'):
    q = np.array(alignment['q'])
    if np.max(abs(q-points[-1])) > 1e-8:
        points.append(q)
points.append(np.array(row['goal_q']))
assert len(points)-1 == row['planned_legs']
maximum_step = maximum_ratio = 0.
began = time.monotonic()
valid = True
for leg, (qa, qb) in enumerate(zip(points, points[1:])):
    if time.monotonic()-began > 850:
        row['continuation_blocker'] = 'Bounded chunk exhausted before next leg'
        valid = False
        break
    pl = Planner(ch, {}, seed=986000+candidate*10+leg, seconds=65)
    v.s.PARK = qb.copy()
    if leg < len(prior['edges']) and prior['edges'][leg]['ok']:
        edge = copy.deepcopy(prior['edges'][leg])
        edge['prior_timed_replay'] = edge.pop('fresh_replay', None)
        edge['reused_unchanged_geometric_proposal'] = True
    else:
        edge = pl.plan(qa, qb, {}, {})
    row['edges'].append(edge)
    if not edge['ok']:
        valid = False
        break
    path = np.array(edge['path'])
    valid = bool(np.max(abs(path[0]-qa)) <= 1e-7 and np.max(abs(path[-1]-qb)) <= 1e-7)
    edge['endpoint_joint_continuity'] = valid
    deadline = time.monotonic()+240
    states, bad = [], None
    for si, (u, z) in enumerate(zip(path, path[1:])):
        if not valid:
            break
        bound = pb.segment_bound(u, z)
        n = max(1, math.ceil(bound/.004))
        maximum_step = max(maximum_step, bound/n)
        for k in range(n+1):
            q = u+(z-u)*k/n
            if time.monotonic() > deadline:
                valid = False; bad = {'reason': 'independent replay timeout', 'allocated_s': 240}
                break
            valid = pl.state(q, {}) and all(not ch.m.jnt_limited[ch.jid[nm]] or
                ch.m.jnt_range[ch.jid[nm],0]-1e-8 <= q[ix] <= ch.m.jnt_range[ch.jid[nm],1]+1e-8
                for nm, ix in ch.qa.items())
            ratio = float(ch.torque_multi(q, {}, {})['ratio'])
            maximum_ratio = max(maximum_ratio, ratio)
            valid = bool(valid and ratio <= 1)
            if not valid:
                bad = {'reason': 'gap, joint or load', 'blocker': pl.last, 'ratio': ratio}
                break
            states.append(dict(q=q.tolist(), leg=leg, segment=si, alpha=k/n))
    edge['fresh_replay'] = dict(pass_=valid, states_checked=len(states), blocker=bad,
        allocated_s=240, max_point_step_mm=maximum_step*1000, max_envelope_ratio=maximum_ratio)
    row['states'] += states
    print('REPLAY_LEG', mode, candidate, leg, valid, len(states), bad, flush=True)
    if not valid:
        break
idle = json.loads((O/'layouts'/f'{ID}_idle.json').read_text())
row.update(pass_=bool(valid and len(row['edges']) == len(points)-1 and idle['snapshot_pass']),
    max_point_step_mm=maximum_step*1000, max_envelope_ratio=maximum_ratio,
    states_checked=len(row['states']))
row['replay_continuation']['elapsed_s'] = time.monotonic()-began
folder = O/'front_replay_continuations_v7'; folder.mkdir(exist_ok=True)
(folder/f'{ID}_{mode}_{candidate}.json').write_text(json.dumps(row, allow_nan=False))
print('REPLAY_CONTINUATION', mode, candidate, row['pass_'], time.monotonic()-began, flush=True)
