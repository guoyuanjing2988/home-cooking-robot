import sys
from execute import stroke,connection
fn=stroke if sys.argv[1]=='stroke' else connection
for i in map(int,sys.argv[2:]):fn(i)
