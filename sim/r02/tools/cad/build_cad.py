"""FreeCAD solid concept parts and countertop assembly. Dimensions in mm.
This is a concept CAD package, not a manufacturing release for vendor interfaces.
"""
import FreeCAD as App, Part, Mesh, json, math, os
from FreeCAD import Vector as V
HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(HERE)
for d in ['step','meshes']:os.makedirs(os.path.join(HERE,d),exist_ok=True)
doc=App.newDocument('R02_Tools')
PARTS=[];INSTANCES=[]
DENS={'316L':8e-6,'POM-C':1.41e-6,'polycarbonate':1.2e-6,'silicone':1.1e-6,'304':7.9e-6}
def box(x,y,z,base=(0,0,0)):return Part.makeBox(x,y,z,V(*base))
def cylinder(r,h,base=(0,0,0)):return Part.makeCylinder(r,h,V(*base))
def holes(shape,positions,r,h,z=-1):
    for x,y in positions:shape=shape.cut(cylinder(r,h,(x,y,z)))
    return shape
def centeredbox(x,y,z,z0=0):return box(x,y,z,(-x/2,-y/2,z0))
def key():
    s=centeredbox(60,28,20)
    for sign in [-1,1]:
        s=s.fuse(box(24,5,8,(-12,(12 if sign==1 else -17),6)))
        s=s.fuse(box(24,8,8,(-12,sign*20-4,6)))
    return holes(s,[(-20,0),(20,0)],2.7,24)
def add(i,label,shape,material,qty,notes):
    o=doc.addObject('PartDesign::Feature',i);o.Label=i+' '+label;o.Shape=shape
    o.addProperty('App::PropertyString','Material');o.Material=material
    o.addProperty('App::PropertyString','EngineeringNotes');o.EngineeringNotes=notes
    doc.recompute()
    assert shape.isValid() and shape.Volume>0 and len(shape.Solids)>0,(i,'invalid')
    path=os.path.join(HERE,'step',i+'.step');Part.export([o],path)
    Mesh.export([o],os.path.join(HERE,'meshes',i+'.stl'))
    b=shape.BoundBox
    PARTS.append(dict(id=i,label=label,material=material,quantity=qty,volume_mm3=round(shape.Volume,3),cad_mass_kg=round(shape.Volume*DENS[material],5),solid_count=len(shape.Solids),valid=shape.isValid(),bounds_mm=[b.XLength,b.YLength,b.ZLength],step_file='step/'+i+'.step',notes=notes))
    return shape
circle6=[(25*math.cos(j*math.pi/3),25*math.sin(j*math.pi/3)) for j in range(6)]
sh={}
sh['C01']=add('C01','wrist master plate',holes(cylinder(34,8),circle6,2.75,12).cut(cylinder(8,12,(0,0,-1))),'316L',2,'ISO9409-1-A50 sixM5 nominalpattern; xArmmanual A50/63 patternmustmatchselectedwrist beforemachining. Boltedmanualadapter,notautochanger.')
sh['C02']=add('C02','tool mate and antirotation dowel plate',holes(cylinder(34,6),circle6+[(12,0),(-12,0)],2.75,10).cut(cylinder(8,10,(0,0,-1))),'316L',2,'Two6mm dowelholes requirefinalreaming; throughholesnominalM5 clearance; controlledboltedmate.')
sh['C03']=add('C03','positive key handle 24x8 lands',key(),'POM-C',9,'Two24x8x8 lands40mm apart; fastenersM5. Foodgrade machinedstock, radiusedges2mm in finalfinishing.')
# Bowl collar with bail; compound solids deliberately represent assembled pieces.
collar=cylinder(104,8,(0,0,82)).cut(cylinder(101,10,(0,0,81)))
ba=[collar]
for sign in [-1,1]:
    ba.append(box(12,12,91,(sign*83-6,-6,89)))
    ba.append(box(27,12,6,((77 if sign==1 else -104),-6,84)))
ba.append(box(178,12,12,(-89,-6,168)))
kk=key();kk.translate(V(0,0,170));ba.append(kk)
sh['C04']=add('C04','bowl collar bail and key assembly',Part.makeCompound(ba),'POM-C',4,'SplitPOM collar aroundstainlessbowl,removablebail. Nominalinner202mm notguaranteedIKEA rimfit; measureactualrim. Metalfasteners andbowl excludedfromCADmass.')
base=centeredbox(310,270,3)
# Two end cups leave the entire centre clear for grip and peeling.
supports=[]
for sign in [-1,1]:
    supports.append(box(16,24,53,(sign*98-8,-12,3)))
    supports.append(Part.makeCylinder(8,20,V(sign*80,0,53),V(sign,0,0)))
slotted=base
for x in range(-100,101,25):slotted=slotted.cut(box(12,180,8,(x-6,-90,-1)))
endstop=box(8,80,20,(105,-40,3))
sh['C05']=add('C05','peel end-cup support slotted tray and axial stop',Part.makeCompound([slotted,*supports,endstop]),'POM-C',1,'Two16mmODendcups on adjustablepassivespindles;foodaxislocalZ53mm,assembled100mm. Carrotcupcentres+-80mm;potatoset+-45mm. Springtailstockandbearingsnotdetailed. Endcupscontactonly3–5mmtrimregion;centreclearforgripper. Oppositeendstopreacts63N; indexonlyaftertool80mmclear.')
insert=centeredbox(260,230,.5)
for x in range(-100,101,25):
    for y in range(-85,86,25):insert=insert.cut(cylinder(5,6,(x,y,-1)))
wall=centeredbox(260,230,80).cut(centeredbox(259,229,82,-1))
rim=centeredbox(264,234,1,79).cut(centeredbox(259,229,3,78))
sh['C06']=add('C06','sink perforated insert',Part.makeCompound([insert,wall,rim]),'304',1,'Fold/weld.5mmshellandbottom,10mmbottomholes;reinforcedtoprim1mm. Smoothcontinuouswelds,no rivetseams; bailusesC03/C04. Steelbasket carries<=.2kgfood; sheet buckling/handleweldproofstillrequired.')
binbody=centeredbox(280,160,45).cut(centeredbox(276,156,45,2))
lid=centeredbox(280,160,2,45)
sh['C07']=add('C07','lidded peel bin',Part.makeCompound([binbody,lid]),'POM-C',1,'Closedwastebin,captivelid; no foodreturn. Toolhandleabovefrontonly; noteoutputtoolmassbudgetexceedsCADbarebin.')
dock=centeredbox(200,500,3)
lands=[dock]
for yy in [-195,0,195]:
    lands.extend([box(20,80,30,(-70,yy-40,3)),box(20,80,30,(50,yy-40,3))])
sh['C08']=add('C08','three covered tool support dock',Part.makeCompound(lands),'POM-C',1,'Actualknife/peeleredgesstoredwithremovableguards; gripperbodyrequires5mmgaptoallnonsupportsurfaces.')
base=holes(centeredbox(480,340,3,12),[(-210,-130),(-210,130),(210,-130),(210,130)],3.3,30)
feet=[box(28,28,12,(x-14,y-14,0)) for x,y in [(-210,-130),(-210,130),(210,-130),(210,130)]]
sh['C09']=add('C09','press base and four mount feet',Part.makeCompound([base,*feet]),'316L',1,'Onlyfeetmounttocounter;plateunderside12mmaboveenvironment. M6counteranchoragebackingplateandstrengthrequireinstallationengineering. Heavybaseisfixednotcarried.')
post=centeredbox(25,25,330).cut(centeredbox(21,21,332,-1))
sh['C10']=add('C10','press hollow post',post,'316L',2,'25x25x2mmSSsquaretube. Twoinclinedforcepaths notmodeled; mustcloseboltedjointsandguidebearingdesign.')
bridge=centeredbox(425,45,40).cut(centeredbox(421,41,42,-1))
# correct beam cavity runs horizontally alongX; retain endcaps for bolted mounts.
bridge=centeredbox(425,45,40).cut(box(421,41,36,(-210.5,-20.5,2)))
sh['C11']=add('C11','press hollow bridge',bridge,'316L',1,'425x45x40x2mmclosedbeamnominal. Frame1000Ndesign; deformationestimateinvalidationreport; runningmotorproofnotprovided.')
front=box(460,4,310,(-230,-122,25)).cut(box(320,10,285,(-160,-125,25)))
guards=[front,box(460,4,310,(-230,158,25)),box(4,280,310,(-232,-120,25)),box(4,280,310,(228,-120,25))]
leftdoor=box(160,4,285,(-160,-126,25));rightdoor=box(160,4,285,(0,-126,25))
sh['C12']=add('C12','press enclosure panel set',Part.makeCompound([*guards,leftdoor,rightdoor]),'polycarbonate',1,'Fourframepanelsandtwo160x285mmfrontdoorleaves. HingesatlocalX+-160,Y-124;open90degforward withincounter. Interlocksontwoleaves. Nonfoodcontact;hinges/linkeddrivefittingrequireengineering.')
floor=centeredbox(240,160,8)
channel=centeredbox(220,85,30,8).cut(centeredbox(220,75,32,13))
channel=channel.cut(box(4,110,50,(88,-55,0)))
sh['C13']=add('C13','root feed cassette and blade clearance slot',Part.makeCompound([floor,channel]),'POM-C',1,'160mmcarrotfits210mmchannel,<=70mmchord. Bladeslot4mm atX=90; machinefeedtoward+X. Measuredfeedrequired; geometryisanopenchannelnotamandolinesweep.')
follower=centeredbox(70,70,12)
for y in [-26,26]:follower=follower.fuse(box(8,8,18,(-4,y-4,12)))
sh['C14']=add('C14','flat follower with positive travel stop',follower,'POM-C',1,'Followerface neverwithin5mmofbladeplane; last5mmedibleremainderreleasedintactafterbladeparks; noextrafoodstubdiscarded. Feeddriveandfinalreleasehingeconceptnotdetailed.')
comb=centeredbox(240,160,8)
for yy in [-60,-45,-30,-15,0,15,30,45,60]:comb=comb.fuse(box(210,3,30,(-105,yy-1.5,8)))
comb=comb.cut(box(4,160,45,(88,-80,-1)))
sh['C15']=add('C15','greens longitudinal and section guide comb',comb,'POM-C',2,'Slots15mmpitch;<=30mmhighbundle. Longitudinalsplitusesoneknifeandregisteredstalk; transverseindex40mmorlength/n. Two clean/dirtycopiesavoidsoiltransfer.')
ring=cylinder(70,8).cut(cylinder(50,12,(0,0,-1)))
ring=holes(ring,[(60,0),(-60,0),(0,60),(0,-60)],2.75,12)
sh['C16']=add('C16','wedger adapter review blank',ring,'316L',1,'140mmOD100mmIDblank,4M5nominalholesPCD120. NOTNemcomeasuredinterface! Vendorbladefitdimensionsunavailable; measure428-8and55434beforecuttingthisblank.')
catch=centeredbox(180,160,2)
walls=centeredbox(180,160,55).cut(centeredbox(176,156,57,-1))
pad=centeredbox(174,154,5,2)
ramp=centeredbox(120,100,2);ramp.rotate(V(0,0,0),V(0,1,0),-15);ramp.translate(V(0,0,53))
sh['C17']=add('C17','contained catch nest and sloping chute blank',Part.makeCompound([catch,walls,pad,ramp]),'POM-C',2,'Rootandtomatocopies. Rootramp15deg;tomatopadheightinmode-specificassembly. Finalcontactpadmouldedsilicone,notPOM;CADmassconservativelyusesPOM. <=30mmrootdropand<=10mmtomatodropareassemblygates.')
cup=centeredbox(90,90,4)
cup=cup.fuse(box(90,4,40,(-45,41,4)))
for xx in [-40,40]:cup=cup.fuse(box(8,90,22,(xx-4,-45,4)))
cup=cup.fuse(box(8,20,86,(36,-10,4))).fuse(box(110,20,8,(40,-10,86)))
cupkey=key();cupkey.translate(V(150,0,90))
cup=cup.fuse(cupkey)
sh['C18']=add('C18','bottom support cup with offset key handle',cup,'POM-C',2,'Foodcupkeygraspsite150mm tosideand100mmabovefloor;keeps otherhandclearforcreasewash. Siliconepads. Rawtray22mmaccessslots for8mmfingers+2x5mmgap;gripperinterfacesnotvendormeasured. CupbudgetupdatedfromCAD; no15NmOEMmomentclaim.')
doc.recompute();doc.saveAs(os.path.join(HERE,'custom_parts.FCStd'))
Part.export([doc.getObject(p['id']) for p in PARTS],os.path.join(HERE,'custom_parts.step'))
# Assembly is a separate document; local part definitions are unchanged.
assembly=App.newDocument('R02_Counter_Layout')
def inst(name,shape,xyz,color,kind='custom'):
    o=assembly.addObject('PartDesign::Feature',name);s=shape.copy();s.translate(V(*xyz));o.Shape=s
    assembly.recompute();Mesh.export([o],os.path.join(HERE,'meshes','layout_'+name+'.stl'))
    b=s.BoundBox;INSTANCES.append(dict(name=name,xyz_mm=xyz,color=color,kind=kind,mesh='cad/meshes/layout_'+name+'.stl',bounds_mm=[[b.XMin,b.XMax],[b.YMin,b.YMax],[b.ZMin,b.ZMax]],valid=s.isValid()))
    return o
steel=[.55,.64,.68];blue=[.10,.42,.57];ivory=[.88,.90,.84];orange=[.85,.30,.08]
inst('LeftCounter',box(1100,600,30,(-1800,0,-30)),(0,0,0),[.58,.51,.40],'environment')
inst('RightCounter',box(800,600,30,(-110,0,-30)),(0,0,0),[.58,.51,.40],'environment')
sinkwall=box(600,440,180,(-700,80,-200)).cut(box(594,434,180,(-697,83,-197)))
inst('ExistingSink',sinkwall,(0,0,0),steel,'environment')
inst('ProtectedStove',box(780,520,40,(690,40,0)),(0,0,0),[.12,.13,.14],'protected')
inst('PeelFixture',sh['C05'],(-935,170,47),ivory)
inst('PeelBin',sh['C07'].Solids[0],(-935,170,0),orange)
inst('SinkInsert',sh['C06'],(-400,300,-125),steel)
raw=box(310,270,3,(-155,-135,0)).fuse(box(310,3,80,(-155,132,0)))
for xx in [-155,152]:raw=raw.fuse(box(3,270,80,(xx,-135,0)))
inst('RawTray',raw,(-1615,170,0),blue)
# Exact thin spherical-like bowl solid using revolution, open top.
def bowl():
    # Frustum envelope is conservative; market bowl curvature not reverse engineered.
    outer=Part.makeCone(55,100,90);inner=Part.makeCone(54,99,90,V(0,0,1))
    return outer.cut(inner)
for food,x in zip(['Carrot','Potato','Greens','Tomato'],[-1665,-1415,-1165,-915]):
    inst(food+'Bowl',bowl(),(x,435,0),steel,'bought_proxy')
    inst(food+'Bail',sh['C04'],(x,435,0),blue)
inst('Colander',bowl(),(-1295,170,0),steel,'bought_proxy')
inst('ToolDock',sh['C08'],(0,300,0),ivory)
for j,yy in enumerate([105,300,495]):inst('KeyTool'+str(j),sh['C03'],(0,yy,45),blue)
inst('PressBase',sh['C09'],(400,300,0),steel)
for x in [200,600]:inst('PressPost'+str(x),sh['C10'],(x,320,15),steel)
inst('PressBridge',sh['C11'],(400,320,335),steel)
inst('PressGuards',Part.makeCompound(guards),(400,300,0),[.32,.75,.78])
ld=leftdoor.copy();ld.rotate(V(-160,-124,0),V(0,0,1),-90)
rd=rightdoor.copy();rd.rotate(V(160,-124,0),V(0,0,1),90)
inst('LeftGuardDoorOpen',ld,(400,300,0),[.32,.75,.78])
inst('RightGuardDoorOpen',rd,(400,300,0),[.32,.75,.78])
inst('RootCassette',sh['C13'],(400,290,132),ivory)
inst('FeedFollower',sh['C14'],(340,290,140),blue)
inst('CatchNest',sh['C17'],(400,290,45),ivory)
inst('WedgerParkedBlank',sh['C16'],(400,290,240),steel)
# A machine crosshead + actual straight blade envelope: source thickness retained.
inst('Crosshead',centeredbox(160,60,20),(400,320,280),steel,'mechanism_proxy')
inst('PressDriveEnvelope',centeredbox(57,57,113),(400,410,215),[.12,.13,.14],'vendor_envelope')
inst('StraightBladeEnvelope',box(.952,100,75,(-.476,-50,0)),(490,290,175),steel,'cutting_edge_proxy')
assembly.recompute();assembly.saveAs(os.path.join(HERE,'counter_layout.FCStd'))
Part.export(list(assembly.Objects),os.path.join(HERE,'counter_layout.step'))
json.dump(dict(version=App.Version(),length_unit='mm',custom_part_designs=len(PARTS),parts=PARTS,instances=INSTANCES,release='Conceptvalidsolids;matchedvendorinterfaces,actuatormounts,feedkinematics,guardsandhygienicfinishingstillrequired',all_valid=all(p['valid'] for p in PARTS)),open(os.path.join(HERE,'cad_manifest.json'),'w',encoding='utf-8'),indent=2)
print('CAD_DONE parts='+str(len(PARTS)),flush=True)
