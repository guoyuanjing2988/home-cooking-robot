import sys
from run import iteration
for i in map(int,sys.argv[1:]):iteration(i-1)
