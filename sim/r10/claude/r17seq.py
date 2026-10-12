"""R17 arm action times for meal16.py (ARM=r17), from the checked whole-action paths of r17chain.py
plus estimated free moves of the empty arm between them (NOT collision checked).
Sources (results/r17/):
 lever      chain_lever_s+1_final.json: the faucet lever gripped, lifted 30° (open); close = the same reversed
 wok        WOK=<chain json> (default: the fastest passing chain_wok_*.json): wok off the cooker, plated
            (tip 90° over the plate), rinsed under the running tap (5 s), emptied into the sink, back
 spider     chain_spider_s+1_final.json: rest (1.52, .36) -> pot (scoop, drain 5 s) -> plate (tip) -> rest
Plating with the sink rinse, from the end of the stir-fry (arm at the wok holding the spatula):
 spatula to its rest (R16 estimate, spatula_one_way_s) -> faucet (free move) -> open -> wok (free)
 -> wok chain -> faucet (free) -> close -> spatula rest (free) -> spatula back at the wok (R16 estimate)
Free move of the empty arm: cart |dx| / 0.25 m/s + 1 s, arm 90° at 90°/s + 0.6 s (ASSUMPTION, as r16seq.py).
dump (the wok emptied and rinsed at the sink, no plating) and fill (1 L taken at the running tap) =
the plating sequence minus the plate tip (tip 90° at 45°/s, 2 s hold, back: 6 s) and minus the spatula
handling (the arm does not hold the spatula then).
python r17seq.py [WOK=results/r17/chain_wok_....json] [SPIDER=results/r17/chain_spider_....json] -> results/r17/arm17.json
R18: SPAT=<chain_spatula json> uses that checked rest-to-stroke-start path (+ 0.5 s hand-off into the R15 stir start)
instead of the R16 estimate, and its pick cart as the rest; OUT=<json> names the output."""
import sys,json,glob
from scene import save
KV=dict(a.split('=',1) for a in sys.argv[1:])
def C(f):return json.load(open(f))
lev=C('results/r17/chain_lever_s+1_final.json');spi=C(KV.get('SPIDER','results/r17/chain_spider_s+1_final.json'));r16=C('results/r16/arm_checked.json')
woks=[(f,C(f)) for f in ([KV['WOK']] if 'WOK' in KV else glob.glob('results/r17/chain_wok_*.json'))];woks=[(f,w) for f,w in woks if w['ok']]
assert woks,'no passing wok chain';wf,wok=min(woks,key=lambda fw:fw[1]['time_s'])
an=list(wok['anchors'].values());c_pick,c_set=an[0]['cart'],an[-1]['cart']
c_lev=list(lev['anchors'].values())[0]['cart'];c_sp=C('results/r16/walk_rest_spatula_f2.json')['cart_x']
spat=r16['spatula_one_way_s']
if 'SPAT' in KV:sc=C(KV['SPAT']);assert sc['ok'];spat=sc['time_s']+.5;c_sp=sc['anchors']['pick#0']['cart']   # R18: checked path + hand-off
def free(a,b):return abs(a-b)/.25+1.+90/90+.6
moves=dict(rest_to_faucet=free(c_sp,c_lev),faucet_to_wok=free(c_lev,c_pick),wok_to_faucet=free(c_set,c_lev),faucet_to_rest=free(c_lev,c_sp))
plate=2*spat+sum(moves.values())+2*lev['time_s']+wok['time_s'];TIP=6.
arm=dict(wok_plate=round(plate,1),rinse=0.,dump=round(plate-TIP-2*spat,1),fill=round(plate-TIP-2*spat,1),spider=spi['time_s'])   # no spatula in hand for a dump or a fill
status=dict(wok_plate='checked wok and faucet paths + estimated free moves and spatula handling (R16)',rinse='done on the plating trip',
 dump='as wok_plate minus the plate tip (estimate)',fill='as dump, the wok held under the running tap (estimate)',spider='checked path (pot; used for the fryer and the wok too)')
save(KV.get('OUT','results/r17/arm17.json'),dict(arm_s=arm,status=status,wok_chain=wf,wok_chain_s=wok['time_s'],lever_s=lev['time_s'],spatula_one_way_s=spat,free_moves_s={k:round(v,1) for k,v in moves.items()},
 carts=dict(faucet=c_lev,wok_pick=c_pick,wok_set=c_set,spatula_rest=c_sp)))
print(arm);print('wok chain',wf,wok['time_s'],'free moves',{k:round(v,1) for k,v in moves.items()})
