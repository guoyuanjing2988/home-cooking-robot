"""Copy R05 proposal planner; only sampling distribution changes."""
from pathlib import Path
H=Path(__file__).resolve().parent;s=(H/'planner_r05.py').read_text()
s=s.replace("elif bias<.6:\n     sample=np.array(s.PARK)","elif bias<.55:\n     sample=np.array(s.PARK)")
needle="     i,_=extend(trees[0],sample)"
# Preserve full-range exploration, with an additional near-chord proposal
# distribution to escape tiny endpoint/path grazes without giant joint turns.
old="    i,_=extend(trees[0],sample)"
new="""    if .55<=bias<.90:
     t=self.rng.uniform(0,1);sample=(1-t)*a+t*b
     sample[self.ix]+=self.rng.normal(0,.08 if self.restarts%2 else .25,len(self.ix))*self.scale
     sample[self.ix]=np.clip(sample[self.ix],self.limits[:,0],self.limits[:,1])
    i,_=extend(trees[0],sample)"""
assert old in s;s=s.replace(old,new).replace('RRT-Connect / bounded discrete reference and convex check','RRT-Connect with near-chord/staging sampling / unchanged bounded reference check')
(H/'planner_local_v6_r07.py').write_text(s)
p=H/'motion_v6_r07.py';s=p.read_text().replace('from planner_r05 import Planner as BasePlanner','from planner_local_v6_r07 import Planner as BasePlanner');p.write_text(s)
p=H/'fold_v6_r07.py';s=p.read_text().replace("for name,middle in goals:\n if name in done:continue","for name,middle in goals:\n if '--local-retry' in sys.argv:name='local_'+name\n if name in done:continue");p.write_text(s)
