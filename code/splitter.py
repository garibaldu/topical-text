"""
Program to take a single file of plain text, and split it into multiple files, which are written back to the same location.
"""
import sys,os

if len(sys.argv) < 4:
    print('delimiter is the string used to split filename into chunks')
    sys.exit('usage: python %s filename   directory_for_docs    delimiter_string' % (sys.argv[0]))

filename = sys.argv[1]
output_dir = os.path.join(os.getcwd(), sys.argv[2])
if not os.path.exists(output_dir):
    os.mkdir(output_dir ) 
delimiter = sys.argv[3]

fp = open(filename,'r')
txt = fp.read()
fp.close()

chunks = txt.split(delimiter)

for i,chunk in enumerate(chunks): 
    fp = open(os.path.join(output_dir, 'doc_%s.txt' % (i+1)),'w')
    fp.write(chunk)
    fp.close()
