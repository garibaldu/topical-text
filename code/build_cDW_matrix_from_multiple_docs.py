import sys, string, os
import numpy as np
import util

# ---------------------------------- main here ------------------------

if len(sys.argv) < 3:
    sys.exit('usage: python %s docs_directory_name   vocab_filename' % (sys.argv[0]))
docs_directory_name = sys.argv[1]
filestem = docs_directory_name
print 'base directory is ',docs_directory_name
vocab_filename = sys.argv[2]

# get all the filenames in the specified docs directory
print 'All .txt files in directory %s will be read' % (docs_directory_name)
docs = []
for item in os.listdir(docs_directory_name):
    if os.path.isfile(os.path.join(docs_directory_name, item)):
        if '.txt' in item:
            docs.append(os.path.join(docs_directory_name, item))

print 'number of .txt docs is ',len(docs)
# get the vocabulary
f = open(vocab_filename,'r')
vocab = f.read().split()
f.close()

outfilename = os.path.join(docs_directory_name,'cDW.csv')
f = open(outfilename,'w')
f.write('doc_names')
for w in vocab:
    f.write(', %s' % (w))
f.write('\n')

for filename in docs:
    #print '%s : ' % (filename)
    fp = open(filename,'r')
    txt = fp.read()
    fp.close()
    txtarray = util.remove_linebreaks_and_punctuation(txt).split()
    # IN HERE SHOULD GO STEMMING, IF THE REPO WOULD COUGH IT UP
    counts = util.form_dictionary_of_counts(txtarray, [], vocab)
    f.write('%s ' % (filename[filename.rfind('/'):].strip('/')))
    for w in vocab:
        f.write(', %d' % (counts[w]))
    f.write('\n')
print '** ATTENTION: Wrote the new file to ',outfilename,' (which is where the docs were - probably want to move it up one...)'
f.close()

