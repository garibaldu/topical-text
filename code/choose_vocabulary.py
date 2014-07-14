import sys, string, os
import numpy as np
import util

# ------------------------------------ main here -----------------------------

if len(sys.argv) < 4:
    print('This will read in ALL the files in the supplied directory')
    sys.exit('usage: python   %s   directory  stopwords_filename   max_num_words_in_vocab' % (sys.argv[0]))

docs_directory_name = sys.argv[1]
stopwords_filename = sys.argv[2]
num_words = 10000000000
num_words = int(sys.argv[3])

# First, concatenate all files in that directory to make one big string!
print 'All files in directory %s will be read' % (docs_directory_name)
docs = []
for item in os.listdir(docs_directory_name):
    if os.path.isfile(os.path.join(docs_directory_name, item)):
        if '.txt' in item:
            docs.append(os.path.join(docs_directory_name, item))
print 'number of original docs is ',len(docs)
txt = ''
for doc in docs:
    fp = open(doc,'r')
    txt = txt + ' ' + fp.read()
    fp.close()

# Now go ahead with that entire string..
print 'removing line breaks, punctuation...'
txt = util.remove_linebreaks_and_punctuation(txt)

print 'would be stemming here, if we were stemming...'
# IN HERE SHOULD GO STEMMING, IF THE REPO WOULD COUGH IT UP...

print 'read in stopwords...'
txtarray =txt.split()
for i in range(len(txtarray)):
    txtarray[i] = txtarray[i].lstrip().rstrip()  # strip off leading and trailing spaces
sfp = open(stopwords_filename,'r')
stopwords_list = sfp.read().split()
sfp.close()

print 'forming a dictionary of the counts... (I bet this crawls)'
print 'There are %d words in the original document' % (len(txtarray))
counts = util.form_dictionary_of_counts(txtarray, stopwords_list)

# sort them into decreasing order of usage frequency.
print 'doing the sort...'
sortedwords = list(sorted(counts, key=counts.__getitem__, reverse=True))


print 'writing out the vocabulary...'
vocabfilename = os.path.join(docs_directory_name, 'vocab.txt')
fp = open(vocabfilename, 'w')
num_words = min(num_words,len(counts))
total=0
for r in sortedwords[:num_words]:
    total += counts[r]
    #print r, '\t', counts[r]
    fp.write('%s\n' % (r))
fp.close()
print 'There are %d words in the document, once stopwords are removed, and we truncate to the %d most common words' % (total,num_words)

print '\nSample Original: \n'
for z in txtarray[:100]:
    print z,
print '\n---------------------------------------------------------\n\nSample Cleaned : \n'

for z in txtarray[:100]:
    if z in counts.keys(): print z,
    else: print '_',

