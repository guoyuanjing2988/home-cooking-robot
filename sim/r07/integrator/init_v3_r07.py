from pathlib import Path
import json,copy,hashlib
H=Path(__file__).resolve().parent;O=H/'results';base=json.loads((O/'layouts/L19.json').read_text())
variants=[
 ('L20',{},[-.765,.29],0,'Controlled L19 comparison: same arms/mount/stations, side sink faucet replaces rear centre obstruction.'),
 ('L21',dict(mount_deg=90,front_mount_y=.49,height=1.185),[-.765,.29],0,'L18 vertical principal flange with new side faucet; rear guide and populated park retained.'),
 ('L22',dict(mount_deg=155,front_mount_y=.43,height=1.20,helper_y=.43,helper_mount_deg=155,helper_height=1.20),[-.04,.29],180,'Both tilted arms at same height, right-side faucet frees left wash approaches; single rail.'),
 ('L23',dict(mount_deg=165,front_mount_y=.43,height=1.20,helper_y=.48,helper_mount_deg=155.143,helper_height=1.212596),[-.64,.55],-90,'Rear-left faucet with full140deg low spout sweep, wash targets shifted to left half.'),
 ('L24',dict(mount_deg=140,front_mount_y=.43,height=1.18,helper_y=.48,helper_mount_deg=155.143,helper_height=1.212596),[-.16,.55],-90,'Lower140deg principal mount; rear-right faucet leaves left sink approach.'),
 ('L25',dict(arm='xArm6+xArm6',arms=['xArm6','xArm6'],mount_deg=155.143,front_mount_y=.48,height=1.212596),[-.765,.29],0,'Smaller5kg principal shoulder: unscaled OEM xArm6 compared against UR5e; same1.2kg principal EOAT and3kg service requirement.'),
]
for name,delta,xy,yaw,reason in variants:
 c=copy.deepcopy(base);c.update(delta);c.update(id=name,orientation='R07_v3_'+name,reason=reason,replacement_faucet=dict(model='GROHE Eurosmart33281003',deck_xy_m=xy,yaw_deg=yaw,full_spout_sweep_deg=140,handle_sweep_deg=110,source='sources/faucet_v3/drawing.pdf'))
 # Left faucet conflicts with former leafy output. Keep all bowls, shift that
 # complete output to the spare right countertop in this initial candidate.
 c['station_overrides']['output_leafy_greens']={'new_center':[.02,.43,0]}
 c['station_overrides']['dock_wash_pad']={'new_center':[-.95,.32,0]}
 (O/'layouts'/f'{name}.json').write_text(json.dumps(c,indent=2))
 # Warm start is only a proposal, independently rechecked on each new layout.
 park=copy.deepcopy(json.loads((O/'layouts/L19_park_full.json').read_text()));park.update(config=c,pass_=False,warm_start_only=True)
 (O/'layouts'/f'{name}_park_full.json').write_text(json.dumps(park,indent=2))
source=dict(model='GROHE Eurosmart33281003',drawing='https://www.grohe.co.jp/item/upload/pdf_products_new/03250343_623cbbb4b0fcb.pdf',manufacturer='https://www.grohe-mena.com/en_cy/eurosmart-single-lever-sink-mixer-1-2-33281003.html',buyable_listing='https://www.essentialbathrooms.co.uk/products/grohe-eurosmart-kitchen-sink-mixer-low-spout-33281',dimensions_mm=dict(max_open_handle_height=225,closed_height=180,spout_top=177,outlet_height=146,projection=227,base_diameter=51,max_hose_below_deck=635),drawing_sha256=hashlib.sha256((H/'sources/faucet_v3/drawing.pdf').read_bytes()).hexdigest(),geometry='Conservative full exterior swept covers; no CAD claim. Entire140deg spout and110deg handle retained. Sourceundimensioned local casting covered outward. Sink untouched.',cost_allowance_CNY=1500,price_status='Engineering allowance, not current China quote; no purchase or supplier contact',valve='Below-counter150x120x110mm service reservation; exact NC valve selection and water control not qualified, no executed water-event credit.')
(O/'faucet_v3.json').write_text(json.dumps(source,indent=2))
print('Created six further layout candidates L20-L25')
