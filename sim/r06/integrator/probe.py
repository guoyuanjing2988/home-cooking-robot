from cell import *
import argparse
p=argparse.ArgumentParser();p.add_argument('--variant',type=int,default=1);p.add_argument('--starts',type=int,default=96);p.add_argument('--held',default='output_carrot');p.add_argument('--station',default='dock');args=p.parse_args()
ch=Cell(args.variant,args.held);(H/f'models/probe_v{args.variant}.xml').write_text(ch.xml)
gp=np.array(next(g for g in SPEC['grasp_handles'] if g['object_id']==args.held)['pose_local']['position_m']);gp[2]+=.02 if args.variant>=2 else 0
origin=next(b['pose']['position_m'] for b in SPEC['bodies'] if b['id']==args.held)
if args.station=='wash':origin=[-.49,.49,.953]
if args.station=='wash' and args.variant>=4:origin[2]+=.12
if args.station=='cell':origin=[.45,.505,.972]
target=np.array(origin)+gp;rt=ch.rot;rng=np.random.default_rng(606);best=None;success=[];counts={};beg=time.monotonic()
floor='pan_'+args.held.removeprefix('output_')+'_floor'
face='dock_'+args.held.removeprefix('output_')+'_land' if args.station=='dock' else 'wash_lift_left' if args.station=='wash' else 'cell_land_a'
parts=['pan_'+args.held.removeprefix('output_')+'_'+n for n in ('floor','left','right','front','rear')]
ch.contact_windows=[dict(kind='grasp_release_support',object_id=args.held,support_id=face,side='R',face=face,held_parts=parts,tcp_origin_m=target.tolist(),tcp_rotation=rt.tolist(),normal=[0,0,1],reason='Own pan bottom and bottom wall rims / named top face')]
if args.station=='wash':ch.contact_windows.append(dict(ch.contact_windows[0],face='wash_lift_right',support_id='wash_lift'))
if args.station=='cell':ch.contact_windows.append(dict(ch.contact_windows[0],face='cell_land_b',support_id='process_cell'))
for k in range(args.starts):
 q=ch.q0.copy()
 for n in ARM:q[ch.qa[n]]=rng.uniform(max(-math.pi,ch.m.jnt_range[ch.jid[n],0]),min(math.pi,ch.m.jnt_range[ch.jid[n],1]))
 q,err=ch.solve(target,rt,q);hits,mins,proof=contacts(ch,q)
 score=err['position_mm']+err['orientation_deg']+100*len(hits)
 row=dict(seed=k,errors=err,hits=hits[:8],min_clearance=mins,q=q.tolist(),score=score)
 if best is None or score<best['score']:best=row
 if err['position_mm']<=5 and err['orientation_deg']<=3 and not hits:success.append(row)
 for x in hits:counts[' / '.join(x['pair'])]=counts.get(' / '.join(x['pair']),0)+1
print(json.dumps(dict(variant=args.variant,target=target.tolist(),starts=args.starts,success=len(success),elapsed_s=time.monotonic()-beg,best=best,blockers=sorted(counts.items(),key=lambda x:-x[1])[:10]),indent=2))
write(f'results/probe_v{args.variant}_{args.held}_{args.station}.json',dict(variant=args.variant,starts=args.starts,success=success,best=best,blockers=counts,elapsed_s=time.monotonic()-beg))
