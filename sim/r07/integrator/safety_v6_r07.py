"""Logical pause contract only; sensor electronics/stopping distance unqualified."""
import json
from pathlib import Path
H=Path(__file__).resolve().parent
class PauseController:
 def __init__(self):self.state='parked';self.needs_deliberate_restart=False
 def inputs(self,door_open,present):
  if any(door_open) or present:
   if self.state=='moving':self.state='paused';self.needs_deliberate_restart=True
  return self.state
 def start(self,door_open,present,deliberate=False):
  if any(door_open) or present:return False
  if self.needs_deliberate_restart and not deliberate:return False
  self.state='moving';self.needs_deliberate_restart=False;return True
 def advance_allowed(self):return self.state=='moving'
c=PauseController();checks={};checks['door_open_prevents_start']=not c.start([True]+[False]*4,False);checks['all_closed_starts']=c.start([False]*5,False);c.inputs([False,True,False,False,False],False);checks['door_open_pauses_motion']=not c.advance_allowed();c.inputs([False]*5,False);checks['closure_does_not_auto_restart']=not c.advance_allowed() and not c.start([False]*5,False);checks['deliberate_closed_clear_restart']=c.start([False]*5,False,True);c.inputs([False]*5,True);checks['presence_pauses']=not c.advance_allowed()
out=dict(pass_=all(checks.values()),checks=checks,door_count=5,model_part_prefix='door_pause_sensor_',cover_size_m=[.012,.016,.020],scope='Logical state contract and conservative component reservations; not a physical safety-function qualification.',package=dict(existing_allowance_cny=18000,door_sensor_wiring_control_allocation_cny=600,additional_package_count=0,total_package_count=1),door_scope=dict(parked='full opening sweeps,10mm every robot part',moving='closed leaves/cabinet bodies with ordinary gaps; sensors pause upon opening or presence'))
(H/'results/safety_v6.json').write_text(json.dumps(out,indent=2));print('SAFETY_LOGIC',out['pass_'])
