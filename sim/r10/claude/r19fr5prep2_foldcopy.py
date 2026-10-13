"""R19 #2 / #38 (R19_FR5_PREP3.md): put the FOLDED swing-away T2L cradle with the pan aboard into the scene of a stored
prep set, so that the unchanged step-5 re-check tools (r19prep5_verify.py, r19prep5_cable.py) check every stored state
with the cradle present. New file; it only writes a COPY of the set with one scene key added, under results/r19/prep5/.
The motion (play, approach_qs, keyframes, grasps) is copied unchanged; scene['r19p5'] = the same dict r19prep5_chain.py
stores for P5STATE=folded P5PAN=1 (kind swing, knob top), so r19prep5_verify / r19prep5_cable rebuild the cradle (cart
parts R_cart_p5_*, 10 mm arm / held vs cart part) in the play scene and in every approach scene.
python r19fr5prep2_foldcopy.py FILE=results/r19/prep/chain_<..>.json
 -> results/r19/prep5/chain_<..>_fold_<arm-tag>.json (name: the set's name with '_fold' before the arm tag)"""
import sys,json,os
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a);FN=KV['FILE']
R=json.load(open(FN));assert R.get('ok'),'only a passing set is copied'
assert 'r19p5' not in R['scene'],'the set already carries a T2L cradle state'
import arms
tag=arms.tag(R['arm']);base=os.path.basename(FN)[:-5];assert base.endswith(tag),(base,tag)
R['scene']=dict(R['scene'],r19p5=dict(kind='swing',knob='top',state='folded',pan=True))
R['fold_copy_of']=FN;R['fold_copy_note']='motion unchanged; scene + kitchen19p5 cradle folded with the pan aboard (as r19prep5_chain.py P5STATE=folded P5PAN=1), for r19prep5_verify.py / r19prep5_cable.py'
os.makedirs('results/r19/prep5',exist_ok=True);fo=f"results/r19/prep5/{base[:-len(tag)]}_fold{tag}.json"
assert not os.path.exists(fo),('exists',fo)
json.dump(R,open(fo,'w'));print(fo)
