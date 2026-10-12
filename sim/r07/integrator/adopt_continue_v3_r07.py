import runpy,sys,time
source,destination,index=sys.argv[1:4];began=time.monotonic()
sys.argv=['adopt_equivalent_v3_r07.py',source,destination,index];runpy.run_path('adopt_equivalent_v3_r07.py')
sys.argv=['static_v2_r07.py',destination,index,str(int(index)+1),str(1020-(time.monotonic()-began)),'96','96'];runpy.run_path('static_v2_r07.py')
