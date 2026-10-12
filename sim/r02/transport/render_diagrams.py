"""1600px technical installation diagrams, source FK geometry, CPU only."""
import json,math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.patches import Rectangle
HERE=Path(__file__).resolve().parent;OUT=HERE/'results';R=HERE/'renders';R.mkdir(exist_ok=True)
D=json.loads((OUT/'transport_options.json').read_text());F=D['geometry']['carriage']['folded']
COLORS=['#198a86','#8264b5','#df9139']
def faces(g):
    p=np.array(g['position']);rot=np.array(g['rotation']);s=g['size'];typ=g['type']
    if typ==6:
        v=np.array([[x,y,z] for x in [-s[0],s[0]] for y in [-s[1],s[1]] for z in [-s[2],s[2]]]);v=v@rot.T+p
        return [v[list(a)] for a in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]]
    if typ in [3,5]:
        a=np.linspace(0,2*math.pi,13);radius=s[0];half=s[1]
        rings=[]
        if typ==3:
            for z,rr in [(-half-radius,0),(-half-radius*.7,radius*.7),(-half,radius),(half,radius),(half+radius*.7,radius*.7),(half+radius,0)]:
                rings.append(np.column_stack([rr*np.cos(a),rr*np.sin(a),np.full(len(a),z)])@rot.T+p)
        else:
            for z in [-half,half]:rings.append(np.column_stack([radius*np.cos(a),radius*np.sin(a),np.full(len(a),z)])@rot.T+p)
        f=[rings[0],rings[-1]]
        for lo,hi in zip(rings[:-1],rings[1:]):
            f.extend([np.array([lo[i],lo[i+1],hi[i+1],hi[i]]) for i in range(len(a)-1)])
        return f
    return []
def render(id,title,subtitle):
    data=json.loads((OUT/(id+'_draw.json')).read_text());v=data['variant']
    fig=plt.figure(figsize=(16,10),dpi=100,facecolor='#f5f6f5')
    fig.text(.035,.954,title,fontsize=25,weight='bold',color='#162b39')
    fig.text(.035,.917,subtitle,fontsize=13,color='#445964')
    ax=fig.add_axes([.015,.205,.65,.69],projection='3d');ax.set_facecolor('#f5f6f5')
    for g in data['geoms']:
        n=g['name'];f=faces(g)
        if not f or 'wall' in n and not n.startswith('fixture') or n.startswith('door_sweep'):continue
        if n.startswith('A'):
            c=COLORS[int(n[1])];alpha=1.
            if 'chain_sweep' in n:alpha=.25
            if 'bracket' in n:c='#71848c'
        elif n.startswith('frame'):
            c='#687d89';alpha=.6
        else:
            c='#ced6d7';alpha=.38 if 'wall' in n else .68
            if n.startswith('upper'):c='#d9ceba';alpha=.30
            if n.startswith('fixture'):c='#8fabc0';alpha=.72
            if 'faucet' in n:c='#426887';alpha=1
            if n=='stove':c='#52606a'
        ax.add_collection3d(Poly3DCollection(f,facecolor=c,edgecolor='#657680',linewidths=.35,alpha=alpha))
    ax.set(xlim=(-1.85,1.85),ylim=(-1.85,.65),zlim=(0,2.4),xlabel='x / m',ylabel='y / m',zlabel='z / m')
    ax.set_box_aspect((3.7,2.5,2.2));ax.view_init(elev=25,azim=-56);ax.tick_params(labelsize=8,pad=0)
    ax.text(-.6,.54,1.77,'UPPER CABINETS',fontsize=9,color='#4f514f')
    ax.text(-.55,.3,.90,'sink',fontsize=9,color='#344e64')
    ax.text(.91,.28,.95,'hob: no tasks',fontsize=9,color='#344e64')
    ax.text(-.65,-1.5,.9,'opposite counter',fontsize=9,color='#344e64')
    ax.text(.40,.48,1.38,'wedger rotated 90 deg',fontsize=9,color='#344e64')
    if v['vertical_slide']['enabled']:
        yy=v['rails'][1]['arm_mount_y_m']
        ax.quiver(-.1,yy-.18,1.23,0,0,-.18,color='#253f51',linewidth=2,arrow_length_ratio=.2)
        ax.text(-.04,yy-.18,1.04,'Z:180 mm',fontsize=10,color='#253f51')
    plan=fig.add_axes([.69,.50,.275,.36]);plan.set_facecolor('#fcfcfb')
    plan.add_patch(Rectangle((-1.8,0),3.6,.6,color='#e2e7e5'))
    plan.add_patch(Rectangle((-1.8,-1.8),3.6,.6,color='#e2e7e5'))
    plan.add_patch(Rectangle((-.70,.08),.6,.44,fill=False,edgecolor='#557b93',lw=2))
    for r in v['rails']:
        i=int(r['id'].split('_')[-1])-1;y=r['arm_mount_y_m'];c=COLORS[i]
        plan.add_patch(Rectangle((-1.78,r['beam_center_y_m']-.15),2.8,.30,facecolor=c,alpha=.25))
        plan.plot(r['carriage_center_travel_x_m'],[y,y],color=c,lw=3)
        x=-1+.7*i;plan.add_patch(Rectangle((x-.18,y-.075),.36,.495,facecolor=c,alpha=.7))
        plan.add_patch(Rectangle((x+F['local_aabb_min_m'][0],y+F['local_aabb_min_m'][1]),F['extent_m'][0],F['extent_m'][1],fill=False,edgecolor=c,lw=1.4,ls='--'))
        plan.text(.99,y,f'lane {i+1}',fontsize=8,va='center',color=c)
    plan.axhline(0,color='#536b79',lw=.8);plan.axhline(-1.2,color='#536b79',lw=.8)
    plan.set(xlim=(-1.9,1.8),ylim=(-1.85,.65),xlabel='x / m',ylabel='y / m',title='Top view: folded arms + carriage envelopes')
    plan.set_aspect('equal');plan.tick_params(labelsize=8);plan.grid(alpha=.18)
    info=[f"Rail: 2.40 m | travel: 1.90 m | structure: 2.80 m",f"Arm mount z: 1.230 m | crosshead top: 1.338 m",f"Lane pitch: {v['rails'][0]['arm_mount_y_m']-v['rails'][1]['arm_mount_y_m']:.3f} m",'Cabinet bottom: 1.350 m | min rail gap: 12 mm','Existing empty gripper attached; tools/food parked']
    if v['vertical_slide']['enabled']:info+=['Z travel: 180 mm down; pass at upper stop','Spring brake on X and Z; column shown in model']
    else:info+=['One arm + one cable chain per lane','Fourth independent lane is not a domestic recommendation']
    fig.text(.70,.448,'\n'.join(info),fontsize=11,linespacing=1.65,color='#263f4e',va='top')
    fig.text(.035,.139,'Installation concept, not a certified kitchen cell',fontsize=15,weight='bold',color='#263f4e')
    fig.text(.035,.097,'OEM UR5e collision shapes and computed folded pose. Geometry screen is separate from process IK and joint ratings.',fontsize=11,color='#475f6c')
    remaining=v['folded_aisle_remaining_at_arm_m']*1000
    warning=f"{v['carriage_count']} arms: {remaining:.0f} mm of aisle remains at the folded arm." if remaining>=0 else f"{v['carriage_count']} arms: foremost folded arm overhangs the opposite counter by {-remaining:.0f} mm."
    fig.text(.035,.065,warning+' Robot-only operation; two working arms are preferred.',fontsize=11,color='#a35d29')
    fig.text(.035,.033,'End portals shown: upper members clear cabinet tops; front uprights clear door sweep. Anchorage/stiffness remain design checks.',fontsize=10,color='#475f6c')
    target=R/(id+'.png');fig.savefig(target,dpi=100);plt.close(fig);print(str(target))
if __name__=='__main__':
    render('passing_rails_cable_2','1  Independent passing rails / two arms','Separate cable chains ABOVE closed beams keep fixed OEM controllers and wired safety/data.')
    render('passing_xz_cable_2','2  Passing rails + short vertical slides / two arms','180 mm Z motion improves station access; return to the upper position before crossing.')
    render('passing_rails_cable_3','1  Three-arm expansion / robot-only galley','Comparison layout: outer arm reaches over the opposite counter. This is not the preferred home configuration.')
    render('passing_xz_cable_3','2  Three-arm expansion with vertical slides','Comparison layout only: third-arm process reach and lowered-Z trajectories remain unverified.')
