import subprocess,time,sys
ID=sys.argv[1];start=time.monotonic()
for script,args in [('fresh_v4_r07.py',[ID]),('sequence_v4_r07.py',[ID]),('prepare_delivery_v4_r07.py',[ID]),('measure_export_v4_r07.py',[ID]),('frame_hash_metadata_v4_r07.py',[]),('plot_maps_v4_r07.py',[ID]),('render_batch_v4_r07.py',[])]:
 remain=1080-(time.monotonic()-start)
 if remain<30:break
 subprocess.run([sys.executable,'-B',script]+args,check=True,timeout=remain)
