"""Close source-timing distinctions and identify the hardest rerun explicitly."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
p=ROOT/'posts/r02/reviewer.md'
t=p.read_text(encoding='utf-8')
changes=[
 ('Public research used the agent-reach skill.', 'Public research used the [agent-reach skill](C:/Users/admin/.codex/skills/agent-reach/SKILL.md).'),
 ('Category1 stop requests must reach the appropriate OEM input and rail drive, then apply brakes;', 'The [OEM stop table](https://docs.xarm.ufactory.cc/7.production_information.html) assigns Category1 to EI/emergency stop and Category2 to SI/safeguard stop. SI alone cannot satisfy a Category1 request. Route the required controlled stop to the appropriate OEM input and rail drive, then apply brakes;'),
 ('At 0.2 m/s, 60 ms engagement and 1 m/s² controlled deceleration imply 12+20=32 mm before uncertainties, within a nominal 50 mm reserve.', 'Using the submitted conservative 60 ms brake-delay assumption at 0.2 m/s and 1 m/s² controlled deceleration gives 12+20=32 mm before uncertainties, within a nominal 50 mm reserve. The catalogue labels 60 ms as armature hold-in and 20 ms as armature release; confirm their brake-apply/release mapping and the dedicated controller sequence rather than treating 60 ms as a verified application delay.'),
 ('Q09 and Q27 cover the greatest tested multi-stroke burden; Q05 tests direct peeling reaction,', 'Q05.carrot is tied for the largest supplied nominal arm process-force norm, **42.30 N**; it therefore includes the hardest direct arm-load operation, not only easier transfers. Q09 and Q27 each have four strokes/eight endpoints per seed, tied for the largest endpoint burden. [Difficulty inventory](../../sim/r02/reviewer/audit/difficulty.json). Q05 tests direct peeling reaction,')
]
for old,new in changes:
 assert t.count(old)==1,old
 t=t.replace(old,new)
p.write_text(t,encoding='utf-8')
print('Final source/timing distinctions recorded; findings unchanged.')
