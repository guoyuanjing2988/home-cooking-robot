from station_cell import *
Workcell=StationCell
hand=payload
def config(v):return register(v)[0]
def write(n,value):
 import os
 path=H/n;path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+f'.{os.getpid()}.tmp')
 tmp.write_text(json.dumps(value,indent=2,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else x.tolist() if isinstance(x,np.ndarray) else str(x)),encoding='utf-8')
 for attempt in range(40):
  try:tmp.replace(path);break
  except PermissionError:
   if attempt==39:raise
   time.sleep(.025)

def recipe(v):
 cfg,s=register(v);loc=initial_locations(cfg);events=[];transfers=[];statics=[];number=0
 for product in ('carrot','potato','tomato','bok_choy'):
  obj='output_'+product
  for src,dst in [('dock_'+product,'wash_basin'),('wash_basin','dock_'+product)]:
   number+=1;origin=list(loc[obj]);dest=list(seats(cfg)[dst] if dst=='wash_basin' else initial_locations(cfg)[obj])
   tr=dict(id=f'T{number:02d}',product=product,object_id=obj,source=src,destination=dst,origin=origin,dest=dest,locations=copy.deepcopy(loc),kind='whole_pan_transfer')
   transfers.append(tr);events.append(tr)
   for action,station,point in [('grasp',src,origin),('release',dst,dest)]:statics.append(dict(id=tr['id']+'_'+action,transfer=tr['id'],action=action,object_id=obj,station=station,origin=point,locations=copy.deepcopy(loc)))
   loc[obj]=dest
   if dst=='wash_basin':events.append(dict(id='P'+product,kind='integrated_station_cycle',product=product,required=['retain_pan','open_lid','couple_lift','lift_basket','wash_index_brush_all_surfaces','dirty_drain','fresh_rinse','retain_root_or_each_leaf','peel_roots_remove_eyes_or_core_or_root_disk','clean_tool_and_pan','feed_supported_cuts_including_terminal','deliver_all_scrap','deliver_edible_to_own_bowl','potato_three_fresh_changes_or_leaf600s_soak','final_drain','lower_basket','uncouple_lift','close_lid','release_pan']))
 return dict(events=events,transfers=transfers,statics=statics,handling_strokes=len(statics),supervisory_events=len(events)+2,quality='Declared assumptions for future physical tests; no simulator wash/peel/cut-quality claim',scope='One integrated bay removes unnecessary wash/process pan transfers; all internal operations remain required')
