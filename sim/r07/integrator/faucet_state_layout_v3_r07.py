"""Same full faucet profile at one explicit state, versus all-angle reservation."""
from pathlib import Path
import json
H=Path(__file__).resolve().parent;O=H/'results'
c=json.loads((O/'layouts/L31.json').read_text())
c.update(id='L32',orientation='R07_v3_L32',reason='L31 station swap retained. Distinguish actual faucet geometry at fixed nominal operating angle from prior all140degree simultaneous sweep reservation. Same full225mm handle-sweep/body, complete spout profile, base, nut and hoses. No physical solid or gate reduced. Spout angle is a required known persistent initial state and does not move during the sequence; all-angle robustness is explicitly NOT claimed. Electric valve means no robot knob/spout operation.')
c['replacement_faucet']['spout_state']='nominal_fixed_during_operation'
c['replacement_faucet']['operating_angle_tolerance_deg']=0
c['replacement_faucet']['state_qualification']='Nominal configuration study; angle calibration/detection and disturbance tolerance unqualified. Prior all-angle sweeps remain separate conservative studies.'
(O/'layouts/L32.json').write_text(json.dumps(c,indent=2))
p=json.loads((O/'layouts/L31_park_full.json').read_text());p.update(config=c,pass_=False,warm_start_only=True)
(O/'layouts/L32_park_full.json').write_text(json.dumps(p,indent=2))
print('L32 explicit nominal spout state; no all-swivel guarantee')
c.update(id='L33',orientation='R07_v3_L33',helper_stage_override=[-1.65,.075,1.24],reason='L32 nominal spout state and L31 full fixture swap. Map-guided principal standby at(-1.65,.075,1.24), down orientation, instead of crossing toward helper at(-.65,.10,1.24). Public joint ranges, all tool solids, loaded peeler and sourced inertial forces unchanged. One shared rail preserves carriage order.')
(O/'layouts/L33.json').write_text(json.dumps(c,indent=2));p.update(config=c);(O/'layouts/L33_park_full.json').write_text(json.dumps(p,indent=2))
print('L33 left principal standby, map-supported down approach')
