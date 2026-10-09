import sys 
import random 

filename = sys.argv[1]
with open(filename, 'r') as f:
    for line in f:
        if random.random() < 0.01:
            print(line, end='')
