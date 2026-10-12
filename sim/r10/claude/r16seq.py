"""R16 arm action times for meal16.py (ARM=checked), from the checked whole-action paths of
r16chain.py and, for the wok, from R15 pieces.
History: joining the r16walk station walks by straight joint-space moves collided in every action
(lid rim / pot wall, spider / upper cabinet, ladle / pour drum ...), hence r16chain.py.
Sources (results/r16/):
 lid        chain_lid.json: lid off the pot -> upright in the rack (lid on = the same path reversed)
 plate_in   chain_plate_in.json: dish carrier plate spot -> rack in the pot (plate_out = reversed)
 ladle      chain_ladle.json (fetch, 2 scoops, return): a soup of SCOOPS scoops = fetch + return
            + SCOOPS x (pot -> soup bowl -> pot loop); 1.2 L in 150 ml scoops
 spider     chain_spider_p1_45_m_12_1_30.json: rest -> pot (scoop, drain 5 s) -> plate (tip) -> rest;
            every piece passes but the arm's branch change between the rest and the pot was not
            found (straight swings collide, RRT-Connect 120 s failed): ESTIMATE, the two branch
            changes counted as straight swings at 60°/s
 wok_plate, rinse: R15 pieces, NOT chained (wok pick-up grasp sense +1 vs tip walk -1; moves between
            R15 and R16 poses timed, not collision checked): spatula to / from its rest at the counter
            end (cart 0.55 <-> rest walk cart, arm move assumed 90°), wok pick-up -> carry -> tip
            15->90° at 30°/s, hold 2 s, back at 45°/s -> carry back -> set down; rinse adds 6 scrape
            strokes of 2.63 s (r15stirwalk2); the water fill needs a valve over the wok (the R14
            station has no water channel) and takes no arm time
Timing model of the chains: TCP <= 0.10 m/s, rotation <= 45°/s, joints <= 60°/s, cart <= 0.25 m/s,
grasp / release 0.8 s (ASSUMPTIONS; r16chain.py). Free moves here: joints <= 90°/s empty or
60°/s holding, +0.6 s; cart moves add 1 s.
python r16seq.py -> results/r16/arm_checked.json"""
import json,numpy as np
from scene import save
QF,QH,SCOOPS=90.,60.,8
def C(n):return json.load(open(f'results/r16/chain_{n}.json'))
def W(n):return json.load(open(f'results/r16/walk_{n}.json'))
lid,pin,lad,spi=C('lid'),C('plate_in'),C('ladle'),C('spider_p1_45_m_12_1_30')
P=lad['pieces'];J=[j['s'] for j in lad['joins']]
fetch=P[0]['time_s']+P[1]['time_s']+J[0];back=P[6]['time_s']+P[7]['time_s']+J[3]
loop=P[2]['time_s']+J[1]+P[3]['time_s']+P[4]['time_s']+J[2]+P[5]['time_s']
assert abs(fetch+loop+back+1.6-lad['time_s'])<.3,(fetch,loop,back,lad['time_s'])
ladle=fetch+back+1.6+SCOOPS*loop
spider=spi['time_s']+sum(j.get('arm_deg',0)/QH+.6 for j in spi['joins'] if not j['ok'])
def arm_s(qa,qb,held):
 qa,qb=np.array(qa),np.array(qb);dq=np.degrees(np.max(abs(qb[3:9]-qa[3:9])));dc=abs(qb[0]-qa[0])
 return dq/(QH if held else QF)+.6+((dc/.25+1.) if dc>.05 else 0.)
r15=lambda n:json.load(open(f'results/r15/{n}.json'))
pick=r15('reach_pour_a0_top_f1.15')['best']['q'];tip=r15('tipwalk_tipx_top_cx0.45')['path'];sp=W('rest_spatula_f2')
spat_one=(abs(sp['cart_x']-.55)/.25+1.)+90/QH+.6+.6+.8   # cart, arm (assumed 90°), the 6 cm rest walk (~0.6 s), grasp or release
wok_trip=2.+.8+.4+arm_s(pick,tip[0]['q'],True)+(75/30+2.+75/45)+arm_s(tip[-1]['q'],pick,True)+.4+.8+2.
wok_plate=2*spat_one+wok_trip;rinse=6*2.63+2*spat_one+wok_trip
arm=dict(lid=lid['time_s'],plate_in=pin['time_s'],plate_out=pin['time_s'],ladle=round(ladle,1),spider=round(spider,1),wok_plate=round(wok_plate,1),rinse=round(rinse,1))
status=dict(lid='checked path',plate_in='checked path',plate_out='checked path (reverse)',ladle=f'checked path (2 scoops), extrapolated to {SCOOPS}',
 spider='estimate: branch change at the counter end not found',wok_plate='estimate from R15 pieces, not chained',rinse='estimate from R15 pieces, not chained')
save('results/r16/arm_checked.json',dict(arm_s=arm,status=status,ladle_parts_s=dict(fetch=round(fetch,1),per_scoop=round(loop,1),back=round(back,1),scoops=SCOOPS),
 spatula_one_way_s=round(spat_one,1),wok_trip_s=round(wok_trip,1)))
print(arm);print('ladle per scoop',round(loop,1),'s; fetch',round(fetch,1),'back',round(back,1))
