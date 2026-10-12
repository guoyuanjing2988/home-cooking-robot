"""Integrated recipe, geometric datums, explicit contacts and force provenance."""
import json,copy
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
P2=json.loads((ROOT/'sim/r02/tools/results/process_v2.json').read_text())
P2['tools']['empty']=dict(mass_kg=0,com_local_m=[0,0,0],work_local_m=[0,0,0],grip='keyed',geometry=[])
def dump(p,x):p.write_text(json.dumps(x,indent=2,allow_nan=False),encoding='utf-8')
def hand(pos,typ='empty',mass=None,product='carrot',approach=(0,0,-1),jaw=(0,1,0),force=None,check=None,contacts=None,work=None,moment=None):
    t=P2['tools'][typ];m=t['mass_kg'] if mass is None else mass
    carry=[[m*.3,0,0],[-m*.3,0,0],[0,0,m*.3]]
    h=dict(pos=list(pos),held=typ,held_kg=m,product=product,approach=list(approach),jaw_axis=list(jaw),roll_deg=0,
        jaw_opening_m=.065 if typ=='root_food' and product=='potato' else .035 if typ=='root_food' else .028,
        work_offset_m=t['work_local_m'] if work is None else work,mass_offset_m=t['com_local_m'],
        nominal_forces_N=force or carry,check_forces_N=check or [[v*1.5 for v in f] for f in (force or carry)],
        nominal_moments_Nm=[[0,0,0]],check_moments_Nm=[[0,0,0]] if moment is None else [moment],
        intended=[],grip=t['grip'],contacts=contacts or [])
    if typ in ('carried_bowl','colander','food_cup'):
        h.update(approach=[0,1,0],jaw_axis=[0,0,1],jaw_opening_m=.080,object_rotation_deg=[0,0,90])
        if typ=='colander':h['approach']=[-1,0,0]
        if typ=='carried_bowl' and pos[0]<-.70:h.update(approach=[0,0,-1],jaw_axis=[0,1,0],jaw_opening_m=.046,object_rotation_deg=[0,0,0])
        for key in ('work_offset_m','mass_offset_m'):
            if h['object_rotation_deg']==[0,0,90]:
                x,y,z=h[key];h[key]=[-y,x,z]
    return h
def seg(label,hd,points,station,contact_face=None,contact_reason=None,endpoints=None,action='process',loops=None):
    poses=[]
    for i,p in enumerate(points):
        h=copy.deepcopy(hd);h['pos']=list(p)
        h['contacts']=[] if not contact_face or (endpoints is not None and i not in endpoints) else [dict(face=contact_face,held_parts='food' if h['held']=='root_food' else 'all',reason=contact_reason)]
        poses.append({'R':h})
    return dict(label=label,station=station,poses=poses,jaw_axes=[[0,1,0]],action=action,loops=loops or dict(repeat=1))
def phase(q,name,segs,old):return dict(id=q,name=name,segments=segs,replaces_P=old)
def build():
    geo=[]
    def box(n,p,s,**kw):geo.append(dict(name=n,type='box',pos=p,size=s,**kw))
    # Raw/clean support lands elevated so fingers never touch the counter.
    for x,product,h in [(-1.685,'carrot',.035),(-1.535,'potato',.07),(-1.685,'leafy_greens',.07),(-1.535,'tomato',.06)]:
        y=.095 if product in ('carrot','potato') else .245
        box('raw_'+product+'_land',[x,y,.936],[.12,.12,.012])
        box('raw_'+product+'_pedestal',[x,y,.901],[.10,.10,.058])
        box('raw_'+product+'_pedestal_shim',[x,y,.869],[.10,.10,.006])
    box('raw_tray_base',[-1.63,.17,.858],[.31,.27,.016])
    box('peel_tray',[-.935,.17,.89],[.31,.27,.02])
    box('peel_food_land',[-.935,.17,.965],[.17,.075,.01])
    for s in (-1,1):box('peel_endstop'+str(s),[-.935+s*.0875,.17,.9675],[.015,.07,.045])
    geo.append(dict(name='peel_waste_bin',type='shell',pos=[-.935,.17,.9245],size=[.28,.16,.047]))
    for a in geo:
        if a['name'].startswith('peel_'):a['pos'][2]+=.135
    for x in (-1.045,-.825):
        for y in (.065,.275):box('peel_riser_'+str(x)+'_'+str(y),[x,y,.940],[.018,.018,.180])
    for x,p in zip([-1.665,-1.415,-1.165,-.915],['carrot','potato','leafy_greens','tomato']):box('output_'+p+'_land',[x,.435,.856],[.21,.21,.012])
    # The full retained colander is the vessel: no redundant nested fixed insert.
    box('greens_crease_land',[-.23,.17,.948],[.18,.07,.012])
    for x in (-.30,-.16):box('greens_crease_leg'+str(x),[x,.17,.796],[.012,.012,.292])
    box('root_brush_work_face',[-.42,.40,.9285],[.08,.08,.020])
    box('root_brush_fixed_stem',[-.42,.40,.7575],[.025,.025,.215])
    box('root_brush_height_slide',[-.42,.40,.876],[.025,.025,.085])
    box('root_brush_hinge_foot',[-.42,.40,.67],[.06,.05,.04])
    box('root_brush_hinge_pin',[-.42,.40,.69],[.06,.016,.016])
    box('root_brush_sealed_drive',[-.42,.40,.72],[.054,.054,.06])
    for i,(t,x) in enumerate([('peeler',-.55),('wash_pad',-.18),('eye_core_spoon',-.325)]):
        box('dock_'+t+'_face',[x,.46,1.00],[.09,.09,.008])
        box('dock_'+t+'_post',[x+.035,.56,.925],[.02,.02,.15])
        box('dock_'+t+'_rear_bracket',[x+.035,.51,.986],[.02,.12,.02])
    # Guarded greens/trim/wedger cell. Lid slides rearwards above bowl handles.
    box('secondary_base',[-1.27,.17,.88],[.30,.27,.06])
    box('secondary_back_guard',[-1.27,.30,1.045],[.30,.01,.27])
    for s in (-1,1):box('secondary_side_guard'+str(s),[-1.27+s*.145,.17,1.045],[.01,.25,.27])
    box('secondary_work_face',[-1.27,.17,.955],[.27,.23,.01])
    box('secondary_drive_guard',[-1.27,.55,1.267],[.12,.08,.10])
    box('secondary_closed_lid',[-1.27,.17,1.183],[.30,.27,.006])
    # Full current OEM R211 XL envelope 385x245x510, rotated 90 degrees.
    # 35mm casing overhang is NOT added counter: four clamped feet stay on slab.
    # Geometry is conservative shell + filled motor, with explicit feed lumen.
    ax=.425;ay=.0875
    box('slicer_motor',[ax,ay,1.00],[.385,.245,.30])
    for sign in (-1,1):
        box('slicer_casing_x'+str(sign),[ax+sign*.1875,ay,1.255],[.010,.245,.21])
        box('slicer_casing_y'+str(sign),[ax,ay+sign*.1175,1.255],[.365,.010,.21])
    # The 87cm2 large lumen is a CAD assumption pending OEM drawing, explicitly.
    feed=[.40,.085,1.36];fx,fy,fz=feed
    box('slicer_feed_front',[fx,fy-.035,fz-.05],[.155,.01,.10])
    box('slicer_feed_back',[fx,fy+.035,fz-.05],[.155,.01,.10])
    for s in (-1,1):box('slicer_feed_side'+str(s),[fx+s*.0775,fy,fz-.05],[.01,.060,.10])
    box('slicer_head_top_left',[.2775,ay,1.355],[.075,.225,.010])
    box('slicer_head_top_right',[.551,ay,1.355],[.122,.225,.010])
    for x in (.30,.55):
        for y in (.035,.155):box('slicer_foot_'+str(x)+'_'+str(y),[x,y,.857],[.035,.035,.014])
    box('slicer_discharge_guard',[.205,.235,1.010],[.070,.140,.030])
    box('slicer_discharge_extension',[.1425,.28,1.005],[.155,.045,.030])
    box('slicer_bowl_land',[.04,.20,.856],[.21,.21,.012])
    # All installed covers/utility boxes represented; controls outside wet zone.
    box('fixed_controller_R',[-1.55,.30,.40],[.460,.254,.449])
    box('fixed_controller_L',[-1.29,.30,.40],[.285,.18,.101])
    box('presence_sensor',[-1.1,.57,1.30],[.055,.035,.035])
    box('estop',[.63,.04,.89],[.035,.035,.06])
    phases=[]
    water=hand([-.4,.30,.98])
    phases.append(phase('Q01','Stage vessels and enable cold water',[seg('water_on',water,[[-.4,.30,.99],[-.4,.32,.98]],'sink')],[]))
    for product,m,size in [('carrot',.12,[.16,.035,.035]),('potato',.20,[.09,.065,.07])]:
        raw=np.array([-1.685 if product=='carrot' else -1.535,.095,.942+size[2]/2])
        root=hand(raw,'root_food',m,product=product)
        washroot=copy.deepcopy(root);washroot['nominal_forces_N']=[[6.1273,0,0],[-6.1273,0,0],[0,0,6.1273]];washroot['check_forces_N']=[[9.191,0,0],[-9.191,0,0],[0,0,9.191]]
        washroot.update(approach=[0,1,0],jaw_axis=[0,0,1]);wz=.95 if product=='carrot' else .9475
        washpoints=[[-.40,.385,wz],[-.40,.405,wz]]
        phases.append(phase('Q02.'+product,'Acquire and wash '+product,[seg('pick',root,[raw,raw+[0,0,.12]],'raw','raw_'+product+'_land','Food bottom rests on its own raised pickup land',endpoints=[0],action='pick'),seg('wash',washroot,washpoints,'sink','root_brush_work_face','Food under modeled faucet outlet at(-.4,.405,1.032), with6mm bristle deflection; fingers approach from front below spout',loops=dict(repeat=6,roll_increment_deg=60,coverage='all exposed root surfaces'))],['P01','P02'] if product=='carrot' else ['P07','P08']))
        dst=np.array([-.935,.17,1.105+size[2]/2]);ph='Q03.'+product
        ls=seg('load_peel',root,[dst+[0,0,.10],dst],'peel','peel_food_land','Food bottom on its own working land',endpoints=[1],action='place')
        ls['poses'][1]['R']['contacts'] += [dict(face='peel_endstop'+str(s),held_parts='food',reason='Food end against its specific axial working stop face') for s in (-1,1)]
        phases.append(phase(ph,'Load supported peeling nest',[ls],['P03']))
        peeler=hand([-.55,.46,1.0715],'peeler',product=product)
        phases.append(phase('Q04.'+product,'Acquire retained peeler',[seg('pick_peeler',peeler,[[-.55,.46,1.0715],[-.55,.46,1.0965]],'dock','dock_peeler_face','Peeler head lower face rests on its own dock land',endpoints=[0],action='pick')],['P15']))
        z=dst[2]+size[2]/2+.065
        peel=hand([-.935,.17,z],'peeler',product=product,force=[[-42,0,5]],check=[[-63,0,7.5]])
        peel_segments=[];count=12 if product=='carrot' else 10
        for i in range(count):
            angle=i*360/count;t=np.radians(angle);extent=abs(np.sin(t))*size[1]+abs(np.cos(t))*size[2]
            hp=copy.deepcopy(peel);hp['food_roll_deg']=angle;pz=dst[2]+extent/2+.065
            travel=size[0]/2-.005
            ps=seg('peel_index_'+str(i),hp,[[-.935-travel,.17,pz],[-.935+travel,.17,pz]],'peel','clamped_food','Peeler edge/skid contacts supported food; endstops lowered beneath cutting path')
            ps['food_roll_deg']=angle;peel_segments.append(ps)
            hr=hand([-.06,.065,1.17],'peeler',product=product)
            # Regrasp near vertical each time; food-frame rotation is explicit.
            phi=0. #110mm enlarged helper opening accepts every full potato diagonal.
            hl=hand(dst,'root_food',m,product=product,approach=[0,np.sin(phi),-np.cos(phi)],jaw=[0,np.cos(phi),np.sin(phi)])
            hl['food_tool_roll_deg']=float(np.degrees(t-phi));hl['jaw_opening_m']=abs(np.cos(t-phi))*size[1]+abs(np.sin(t-phi))*size[2]
            gh=.008 if product=='carrot' else .011
            hl['food_center_local_m']=[gh,0,0];hl['mass_offset_m']=[gh,0,0];hl['work_offset_m']=[gh,0,0]
            theta2=np.radians((i+1)*360/count);phi2=phi+np.radians(360/count)
            hl2=copy.deepcopy(hl);hl2['approach']=[0,float(np.sin(phi2)),float(-np.cos(phi2))];hl2['jaw_axis']=[0,float(np.cos(phi2)),float(np.sin(phi2))]
            poses=[]
            for j,(height,lhand) in enumerate([(0,hl),(.04,hl),(.04,hl2),(0,hl2)]):
                hh=copy.deepcopy(lhand);a=t if j<2 else theta2;e=abs(np.sin(a))*size[1]+abs(np.cos(a))*size[2]
                # Grasp11mm along approach above food centre; dimensions unchanged.
                from reference import rotation
                centre=np.array([-.935,.17,1.105+e/2+height])
                hh['pos']=(centre-rotation(hh['approach'],hh['jaw_axis'])@np.array(hh['food_center_local_m'])).tolist()
                hh['contacts']=[dict(face=f,held_parts='food',reason='Root on its own working land and axial stop faces at grasp/release') for f in ['peel_food_land','peel_endstop-1','peel_endstop1']] if j in (0,3) else []
                poses.append({'R':copy.deepcopy(hr),'L':hh})
            peel_segments.append(dict(label='helper_index_'+str(i),station='peel',poses=poses,jaw_axes=[[0,1,0]],action='helper_index',loops=dict(repeat=1),food_roll_deg=angle))
        phases.append(phase('Q05.'+product,'Peel and helper-index full root surface',peel_segments,['P04'] if product=='carrot' else ['P09']))
        if product=='potato':
            spoon=hand([-.935,.17,z+.015],'eye_core_spoon',product=product,force=[[26.1639,0,0],[-26.1639,0,0],[0,0,26.1639]],check=[[52.3277,0,0],[-52.3277,0,0],[0,0,52.3277]],moment=[0,.523277,0])
            spoon['nominal_moments_Nm']=[[0,.261639,0]]
            phases.append(phase('Q06','Remove every potato eye',[seg('eye',spoon,[[-.95,.17,1.258],[-.935,.17,1.2555]],'peel','clamped_food','Depth-limited spoon edge and distal neck working faces on supported food',loops=dict(repeat='vision_detected_eyes',maximum_depth_m=.002))],['P09']))
        pad=hand([-.935,.17,1.035],'wash_pad',product=product,force=[[0,0,2.5]],check=[[0,0,3.75]])
        phases.append(phase('Q07.'+product,'Collect peel waste and clean dirty land',[seg('clean_peel',pad,[[-1.00,.17,1.176],[-.88,.17,1.176]],'peel','peel_food_land','Cleaning pad face wipes empty work land with5mm calibrated compression',loops=dict(repeat=3))],['P04','P09']))
        phases.append(phase('Q08.'+product,'Rinse peeled root and shut water',[seg('rinse',washroot,washpoints,'sink','root_brush_work_face','Root food under outlet on bristle working face; jet and rub bounds retained',loops=dict(repeat=6,roll_increment_deg=60)),seg('water_off',water,[[-.4,.30,.99],[-.4,.32,.98]],'sink')],['P02','P08']))
        bowl=hand([.04,.20,1.042],'carried_bowl',.52,product=product)
        phases.append(phase('Q09.'+product,'Install direct-output cooking bowl',[seg('bowl_load',bowl,[[.04,-.06,1.054],[.04,.20,1.054],[.04,.20,1.042]],'slicer','slicer_bowl_land','Bowl bottom on its own output support land; approach below discharge from front',endpoints=[2],action='place')],['P05','P14']))
        load=copy.deepcopy(root)
        if product=='carrot':load['approach']=[0,1,0];load['jaw_axis']=[1,0,0]
        else:
            load['food_state']='half';load['held_kg']=.1;load['jaw_opening_m']=.0325
            load['approach']=[1,0,0];load['jaw_axis']=[0,1,0]
        cass=hand([-1.27,.17,1.075],'cut_cassette',.9+m,product=product)
        trim=seg('trim_split',cass,[[-1.27,.17,1.16],[-1.27,.17,1.075]],'secondary','secondary_work_face','Own cassette bottom on its registered work land at release',endpoints=[1],action='place',loops=dict(repeat=2 if product=='carrot' else 3,guarded_cycle='3-5mm end trims; potato longitudinal split'))
        terminal=copy.deepcopy(cass);terminal['food_state']='terminal'
        last=seg('terminal_10mm_stub',terminal,[[-1.27,.17,1.16],[-1.27,.17,1.075]],'secondary','secondary_work_face','Own terminal-slice cassette bottom on registered work land at release',endpoints=[1],action='place',loops=dict(repeat=2 if product=='carrot' else 4,guarded_cycle='10mm stub becomes two5mm edible slices; keep last5mm slice'))
        phases.append(phase('Q10.'+product,'Guarded trim, split if needed, OEM 5mm disc feed',[trim,seg('load_slicer',load,[[.40,.085,1.49],[.40,.085,1.410 if product=='potato' else 1.445]],'slicer',action='place',loops=dict(repeat=1 if product=='carrot' else 2,cut='5mm OEM disc',feed_axis='original root longitudinal axis; last10mm stub geometry preserved')),seg('withdraw',hand([.40,.085,1.52]),[[.40,.085,1.52],[.30,-.05,1.45]],'slicer'),last],['P06'] if product=='carrot' else ['P10']))
        if product=='potato':
            col=hand([-.30,.385,.92],'colander',1.0,product=product)
            phases.append(phase('Q11','Potato starch wash and drain',[seg('rinse_pieces',col,[[-.30,.385,.92],[-.30,.385,.99]],'sink',loops=dict(repeat=3,fresh_water_changes=3,drain_s=30))],['P14']))
        x=-1.665 if product=='carrot' else -1.415
        outb=hand([x,.435,1.042],'carried_bowl',.52+m,product=product)
        phases.append(phase('Q12.'+product,'Deliver '+product+' next-step bowl',[seg('deliver',outb,[[x,.435,1.067],[x,.435,1.042]],'output','output_'+product+'_land','Filled bowl bottom on its own labelled cooking support',endpoints=[1],action='place')],['P14']))
    # Soft produce remains on the inherited offset bottom-support cup.
    for q,name,points,typ,product,old in [
        ('Q13','Coarse wash bok choy',[[-.25,.385,1.00],[-.25,.405,1.00]],'food_cup','leafy_greens',['P11']),
        ('Q14','Guarded 5-10mm greens root trim',[[-1.27,.17,1.16],[-1.27,.17,1.075]],'cut_cassette','leafy_greens',['P12']),
        ('Q15','Separate and expose every detached basal crease',[[-.23,.14,1.02],[-.23,.20,1.02]],'root_food','leafy_greens',['P11']),
        ('Q16','Ten-minute soak, crease rub and fresh-water rinse',[[-.23,.14,1.037],[-.23,.20,1.037]],'wash_pad','leafy_greens',['P11']),
        ('Q17','Drain greens without wringing',[[-.30,.385,.92],[-.30,.385,.99]],'colander','leafy_greens',['P11']),
        ('Q18','Guarded split each stalk wider than15mm',[[-1.27,.17,1.16],[-1.27,.17,1.075]],'cut_cassette','leafy_greens',['P12']),
        ('Q19','Guarded 40mm sections, bundle at most30mm',[[-1.27,.17,1.16],[-1.27,.17,1.075]],'cut_cassette','leafy_greens',['P12']),
        ('Q20','Deliver greens next-step bowl',[[-1.165,.435,1.067],[-1.165,.435,1.042]],'carried_bowl','leafy_greens',['P14']),
        ('Q21','Wash unpeeled tomato',[[-.25,.385,1.00],[-.25,.405,1.00]],'food_cup','tomato',[]),
        ('Q22','Remove hard core without seed cavity',[[-.935,.17,1.255],[-.935,.17,1.2395]],'eye_core_spoon','tomato',[]),
        ('Q23','Load guarded eight-sector tomato nest',[[-1.27,.17,1.16],[-1.27,.17,1.075]],'cut_cassette','tomato',['P13']),
        ('Q24','Withdraw for guarded eight-wedge cycle',[[-1.27,.17,1.28],[-1.27,-.02,1.22]],'empty','tomato',['P13']),
        ('Q25','Deliver tomato next-step bowl',[[-.915,.435,1.067],[-.915,.435,1.042]],'carried_bowl','tomato',['P14']),
        ('Q26','Inspect four outputs and present bowls',[[-.915,.065,1.15],[-1.665,.065,1.15]],'empty','tomato',['P14']),
        ('Q27','Clean, drain, return tools, water off',[[-.18,.46,1.105],[-.18,.46,1.080]],'wash_pad','tomato',['P15','P16'])]:
        mass=None
        if typ=='food_cup':mass=.4 if product=='leafy_greens' else .45
        elif typ=='root_food':mass=.1
        elif typ=='carried_bowl':mass=.62 if product=='leafy_greens' else .67
        elif typ=='cut_cassette':mass=1.0 if product=='leafy_greens' else 1.05
        h=hand(points[0],typ,mass,product=product)
        if q=='Q16':h['nominal_forces_N']=[[0,0,2.1273]];h['check_forces_N']=[[0,0,3.191]]
        if q in ('Q13','Q21'):
            fn=2.1273 if q=='Q13' else 1.1273;fc=3.191 if q=='Q13' else 1.691
            h['nominal_forces_N']=[[fn,0,0],[-fn,0,0],[0,0,fn]];h['check_forces_N']=[[fc,0,0],[-fc,0,0],[0,0,fc]]
        if q=='Q22':h['nominal_forces_N']=[[26.1639,0,0],[-26.1639,0,0],[0,0,26.1639]];h['check_forces_N']=[[52.3277,0,0],[-52.3277,0,0],[0,0,52.3277]];h['nominal_moments_Nm']=[[0,.261639,0]];h['check_moments_Nm']=[[0,.523277,0]]
        if q=='Q15':
            h['food_state']='leaf';h['jaw_opening_m']=.012
            h['food_center_local_m']=[.005,0,0];h['mass_offset_m']=[.005,0,0];h['work_offset_m']=[.005,0,0]
            points=[[a,b,c+.005] for a,b,c in points]
        face={'Q14':'secondary_work_face','Q18':'secondary_work_face','Q19':'secondary_work_face','Q23':'secondary_work_face','Q20':'output_leafy_greens_land','Q25':'output_tomato_land','Q27':'dock_wash_pad_face','Q22':'clamped_food','Q16':'wash_food'}.get(q)
        s=seg(name,h,points,'secondary' if typ=='cut_cassette' else 'sink' if q in ('Q13','Q15','Q16','Q17','Q21') else 'output' if typ=='carried_bowl' else 'peel' if q=='Q22' else 'dock' if q=='Q27' else 'slicer',face,'Own support land at release; or food/tool working face',endpoints=None if q in ('Q16','Q22') else [1],action='place' if typ in ('cut_cassette','carried_bowl') else 'process')
        if q in ('Q15','Q16'):s['loops']=dict(repeat='every_stalk_and_basal_crease',soak_s=0,after_shared_soak='Q16.soak_bok_choy' if q=='Q16' else None)
        if q=='Q19':s['loops']=dict(repeat=5,index_m=.04,bundle_max_m=.03)
        extra=[]
        if q=='Q15':extra=[seg('place_exposed_leaf',h,[[-.23,.17,1.055],[-.23,.17,.965]],'sink','greens_crease_land','Detached leaf bottom on its own removable washing support; grasp5mm above food centre',endpoints=[1],action='place')]
        if q=='Q27':
            s['action']='place'
            a=np.radians(15);cz=.960-.005+.076*np.cos(a)+.0125*np.sin(a)
            wipe=hand([-1.27,.17,cz],'wash_pad',product=product,approach=[0,float(np.sin(a)),float(-np.cos(a))],force=[[0,0,2.5]],check=[[0,0,3.75]])
            extra=[seg('water_off_final',water,[[-.4,.30,.99],[-.4,.32,.98]],'sink')]
            phases.append(phase(q,name,[seg('wipe_secondary',wipe,[[-1.32,.17,cz],[-1.22,.17,cz]],'secondary','secondary_work_face','Pad working face at15degree front approach, with5mm maximum calibrated compression',loops=dict(repeat=3)),s]+extra,old))
        else:phases.append(phase(q,name,[s]+extra,old))
    # An explicit low colander soak keeps all bok-choy food below the0.84m
    # water line. Filling the full inherited sink is included in the timeline.
    greens=next(ph for ph in phases if ph['id']=='Q16');col=hand([-.30,.385,.90],'colander',1.0,product='leafy_greens')
    greens['segments'].insert(0,seg('soak_bok_choy',col,[[-.30,.37,.90],[-.30,.385,.90]],'sink',loops=dict(repeat=1,soak_s=600,sink_water_level_m=.84,fill_volume_L=.6*.44*(.84-.65)*1000,fill_flow_L_min=6)))
    # Every hand-tool change gets actual acquisition/return geometry and strokes.
    for ph in phases:
        for s in ph['segments']:
            for po in s['poses']:
                for h in po.values():
                    if h['held']=='cut_cassette':h['nominal_forces_N']=[[7.7255,0,0],[-7.7255,0,0],[0,0,7.7255]];h['check_forces_N']=[[11.58825,0,0],[-11.58825,0,0],[0,0,11.58825]]
                    if h['held']=='colander':h['nominal_forces_N']=[[.3+.1273,0,0],[-.3-.1273,0,0],[0,0,.3+.1273]];h['check_forces_N']=[[.45+.191,0,0],[-.45-.191,0,0],[0,0,.45+.191]]
    dock={'peeler':(-.55,1.0715),'wash_pad':(-.18,1.080),'eye_core_spoon':(-.325,1.0865)}
    owner='empty'
    for ph in phases:
        expanded=[]
        for s in ph['segments']:
            typ=s['poses'][0]['R']['held'];prod=s['poses'][0]['R']['product']
            if owner!=typ and owner in dock:
                x,dz=dock[owner];h=hand([x,.46,dz],owner,product=prod)
                expanded.append(seg('return_'+owner,h,[[x,.46,dz+.025],[x,.46,dz]],'dock','dock_'+owner+'_face','Specific support face for the returned tool lower head',endpoints=[1],action='place'))
            if owner!=typ and typ in dock and s['label']!='pick_peeler':
                x,dz=dock[typ];h=hand([x,.46,dz],typ,product=prod)
                expanded.append(seg('acquire_'+typ,h,[[x,.46,dz],[x,.46,dz+.025]],'dock','dock_'+typ+'_face','Specific support face for pickup tool lower head',endpoints=[0],action='pick'))
            expanded.append(s);owner='empty' if s['action']=='place' else typ
        ph['segments']=expanded
    # Explicit part identities accompany every intended face in every pose.
    parts={'root_food':['food'],'peeler':['peeler_edge','peeler_y_head'],'wash_pad':['wash_pad_contact'],'eye_core_spoon':['spoon_edge','spoon_neck_work_face'],'carried_bowl':['bowl_outer_bottom']+['bowl_outer_wall'+str(i) for i in range(16)]+['contents'],'cut_cassette':['cassette_floor'],'colander':['colander_shell_bottom'],'food_cup':['cup_floor']}
    for ph in phases:
        for s in ph['segments']:
            for po in s['poses']:
                for h in po.values():
                    for c in h['contacts']:
                        names=parts.get(h['held'],[])
                        if c['face'].startswith('dock_'):
                            names=[g['name'] for g in P2['tools'][h['held']]['geometry']]+['key_shoulder-1','key_shoulder1']
                            if h['held']=='eye_core_spoon':names+=['spoon_neck_work_face']
                        c['held_parts']=names
                        c['face_geometry']='single named planar support/working-face geom; no associated post, frame or guard'
                        c['reason']+='; shell bottom and lower rim edges may meet this same support plane' if h['held']=='carried_bowl' else ''
                        if h['held']=='carried_bowl':c['reason']+='; attached contained food is part of the held bowl assembly and lies1mm above the exterior bottom, within the5mm proximity band of this same plane, shielded by the bowl bottom'
                    # Complete every generic3-axis magnitude bound in both
                    # signs. Magnitudes/margins remain the inherited values.
                    for level in ('nominal','check'):
                        fs=h[level+'_forces_N']
                        if len(fs)==3 and fs[0][0]>=0 and fs[1][0]==-fs[0][0] and fs[2][2]==fs[0][0] and all(fs[j][k]==0 for j,k in [(0,1),(0,2),(1,1),(1,2),(2,0),(2,1)]):
                            v=fs[0][0];h[level+'_forces_N']=list({tuple(x):x for x in fs+[[0,v,0],[0,-v,0],[0,0,-v]]}.values())
    # Complete nominal specs copied; optional julienne is not substituted.
    p=dict(schema_version='r03.integrator.process.v3',date='2026-10-08',finished_products=P2['finished_products'],tools=P2['tools'],force_models=P2['force_models'],installed_geometry=geo,phases=phases,
        source_catalog=json.loads((ROOT/'sim/r02/tools/research/sources.json').read_text()),units=dict(length='m',force='N',moment='Nm',mass='kg'),
        decision_log=[
            'Started with two xArm6 lanes. R03 96-start peel screen failed 63N margin load (best J4 ratio1.056). Replace principal R with UR5e; retain xArm6 helper and independent lanes; no geometry scaling.',
            'R211 XL continuous-output rotary disc with OEM 5mm accessory; full current envelope retained. 35mm casing overhang, feet remain on T08 slab; no new counter.',
            'Root cutting no longer uses custom slow press. Secondary guarded cell retained only for end trims, terminal slices, potato split, stalk trim/split/40mm sections and tomato eight wedges.',
            '87cm2 feed lumen partition is a geometric assumption pending public OEM CAD; no claimed hardware or food-quality validation.',
            'Peeling, potato/greens/tomato proxy forces retained unchanged. Root disc high-speed food-force not inferred from low-speed literature; drive is detached from arms during cutting.',
            'No mandoline; golden mandoline check not applicable. All finished-product gates remain mandatory physical acceptance.',
            'Final3 removes redundant nested fixed wash insert; retained OEM-sized R02 colander 240mm diameter by100mm high is restored without reduction. Sink brush and exposed-leaf land occupy separate front-left and front-right positions; full-height stems reach the T08 sink floor.',
            'Final3 kept tool docks rearward with25mm release lift and parks held peeler forward for helper indexing; final4 relocates docks over the existing rear sink ledge outside upper cabinets, uses an80mm keyed side grasp with output-bowl approach from the right, and grasps helper roots8mm above centre without changing food dimensions.',
            'Final4 narrows lane spacing from550mm to450mm without reducing installed part dimensions, preserving370mm vertical separation to improve helper reach. Washing/cleaning pad contact poses correspond to5mm spring deflection; original force bounds remain unchanged.',
            'Final5 enlarges helper palm from80mm to100mm, aperture90mm to110mm and EOAT1.2kg to1.5kg; no finger or OEM-arm dimension reduced. Helper roots are grasped11mm along approach above centre, all food diagonals fit. The150N/15Nm gates are retained qualification requirements, not claimed purchased-gripper ratings.',
            'Final5 separates every dock from the unchanged faucet, restores symmetric top grasps for output bowls, and keeps bowl approach lift25mm below upper cabinets. Raw pedestal6mm support shims are explicitly modeled.',
            'Final6 moves root and cup wash poses below the unchanged spout lower-front outlet(-.4,.405,1.032), using front side approaches. The full root brush pivots90degrees onto the sink floor before colander insertion; hinge/drive geometry is included, no part shortened. Its actuator sweep remains a required connected-motion gate.',
            'Final6 adds a submerged bok-choy soak pose at water0.84m and50.16L full-sink fill requirement. Every retained generic force magnitude is checked in all six signed Cartesian directions; no magnitude or margin is reduced.' ],
        acceptance=dict(position_mm=5,orientation_deg=3,robot_environment_gap_mm=10,arm_arm_gap_mm=10,held_gripper_environment_gap_mm=5,PAD=0,mu=.5,SF=1.5,normal_N=150,key_force_N=150,key_moment_Nm=15),
        appliance=dict(model='Robot-Coupe R211 XL',source='https://www.robot-coupe.com/export/en/p/food-processors-r-211-xl/18401',size_m=[.245,.385,.510],mass_kg=13,power_W=550,rpm=1500,disc='5mm Essential OEM disc',disc_source='https://www.robot-coupe.com/nl/nl/p/schijvenverzameling-snijschijven-5-mm/18289',force_status='OEM rated operation; feed force and terminal yield unmeasured; detach arms for all cutting'))
    dump(HERE/'results/process_v3.json',p);print(len(phases),'instances',sum(len(x['segments']) for x in phases),'strokes')
if __name__=='__main__':build()
