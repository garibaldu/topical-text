import numpy as np
import numpy.random as rng
import pylab as pl
import sys, os

from gibbs_iteration_c  import   run_GibbsSamplerIteration
#from gibbs_iteration  import   run_GibbsSamplerIteration

def save_topics_per_doc():
    #normedCDT = cDT / np.sum(cDT,1).reshape(nDocs,1)
    filename = os.path.join(localdir,'cDT.csv')
    fp = open(filename, 'w')
    write_counts(cDT, doctokens, topictokens, fp)
    fp.close()
    print 'Wrote %s' % (filename)

def save_words_per_topic():
    #normedCWT = cWT / np.sum(cWT,0)
    filename = os.path.join(localdir,'cWT.csv')
    fp = open(filename, 'w')
    write_counts(cWT, vocabtokens, topictokens, fp)
    fp.close()
    print 'Wrote %s' % (filename)

def write_counts(counts, row_labels, col_labels, fp):
    # write out the counts as a csv file.
    if (fp is sys.stdout): delimiter = '\t'
    else: delimiter = ','
    nr,nc = counts.shape
    if (nr != len(row_labels)) or (nr != len(row_labels)):
        print('can\'t write csv file: labels don\'t match dimensions)')
        return
    # write the top row, of col headers
    fp.write('document names')
    for label in col_labels:
        fp.write('%s %s ' % (delimiter,label.strip()))
    for r,label in enumerate(row_labels):
        fp.write('\n%s' % (label)),
        for c in range(len(col_labels)):
            fp.write('%s %d' % (delimiter,counts[r,c]))
    fp.write('\n')
    
def show_typical_topic_words(Specificity_Threshold = 0.2, fp=sys.stdout):
    nTypical = min(10, nVocab)
    specificity = cWT / np.sum(cWT,1).reshape(nVocab,1) #normalise over topics.
    fp.write('THE MOST TOPIC-SPECIFIC WORDS (specificities > %.2f):\n' % (Specificity_Threshold))
    result = []
    # find the words that are sufficiently topic-specific, and save in 'result'.
    for t,topicname in enumerate(topictokens):
        result.append([])
        for i,w in enumerate(vocabtokens):
            if specificity[i,t] > Specificity_Threshold:
                result[t].append(w)
    # print headers for the columns
    for topicname in topictokens:
        fp.write( '%12s\t' % (topicname))
    fp.write('\n')
    for t,topicname in enumerate(topictokens):
        fp.write('%08s%.2f\t' % ('',(cT / np.sum(cT))[t]))
    fp.write('\n')
    for topicname in topictokens:
        fp.write('%12s\t' % ('---------'))
    fp.write('\n')
    # print out the words, line by line
    linecounter=0
    something_printed = True
    while something_printed:
        something_printed = False
        for t,topicname in enumerate(topictokens):        
            if len(result[t]) > linecounter:
                fp.write('%12s\t' % ((result[t])[linecounter]))
                something_printed = True
            else:
                fp.write('%12s\t' % (''))
        fp.write('\n')
        linecounter += 1
    # consider adapting the Specificity_Threshold (cosmetic really).
    longest_column_length = 0
    for r in result:
        if len(r) > longest_column_length:  longest_column_length = len(r)
    if longest_column_length > 20: 
        Specificity_Threshold = 1-0.75*(1-Specificity_Threshold)
    if longest_column_length < 5: 
        Specificity_Threshold = 0.75*Specificity_Threshold
    return Specificity_Threshold


# get set up by reading in the CSV file and making the matrix cDW.
if len(sys.argv) < 4:
    sys.exit('usage: python %s  ./texts/.../cDW.csv  numTopics  numIterations' % (sys.argv[0]))
filename = sys.argv[1]
i = filename.rfind('/')
if i == -1:
    localdir = './'
else:
    localdir = filename[0:filename.rfind('/')] + '/'
nTopics = int(sys.argv[2])  # how many topics.
num_itns_Gibbs = int(sys.argv[3]) # how many iterations of Gibbs to do.
fp = open(filename,'r')
vocabtokens = fp.readline().strip(' \r\n').replace(';',',').split(',')
vocabtokens = vocabtokens[1:] # UGLY, but the first is just the "document names" column header, not a word in the vocabulary.
print vocabtokens
doctokens = []
topictokens = []
for i in range(nTopics):
    topictokens.append('topic_%d' % (i))  #ie. we start with "topic_0" as first topic.
cdw = [] # note that counts are still just strings at this point
for line in fp:
    elts = line.replace(';',',').strip('\n').split(',')
    doctokens.append(elts[0])
    therest = elts[1:]
    if len(therest) != len(vocabtokens): 
        sys.exit('len(therest) %d,  len(wordtokens)  %d, but they should equal' % (len(therest),len(vocabtokens)))
    cdw.append(therest)
fp.close()
cDW = np.array(cdw, int)
nDocs, nVocab = cDW.shape
if (nDocs != len(doctokens)) or (nVocab != len(vocabtokens)):
    sys.exit('ooooops:   (nDocs != len(doctokens) or (nVocal != len(vocabtokens))')

# invent the hyperpriors: alpha and beta. There's a guide - but I'm just punting here so...
alpha = 0.1 * np.ones(nTopics,float) 
alpha[0] = 9*np.sum(alpha[1:])   # should encourage topic0 to be half of all topic usage.
beta  = 0.01 * np.ones(nVocab,float) 

#create the big matrix, cDWT, and its projections
cDWT = np.zeros((nDocs,nVocab,nTopics),int)
for d,doc in enumerate(doctokens):
    for w,word in enumerate(vocabtokens): # note that w is just an int index
        cDWT[d,w]=rng.multinomial(cDW[d,w],alpha/np.sum(alpha)) #GOD that's easy
cWT = np.sum(cDWT,0) +beta.reshape(nVocab,1) # nb. reshape doesn't change beta
cDT = np.sum(cDWT,1) + alpha
cT    = np.sum(cWT,0)

print 'starting that Gibbs Sampler now'
num_reports = 5
Specificity_Threshold = 0.5
for itn in range(num_itns_Gibbs+1):
    run_GibbsSamplerIteration(cT, cWT, cDT, cDWT)
    if (itn % (num_itns_Gibbs/5) == 0):
        print '\n=============   iteration %d =============' % (itn)
        Specificity_Threshold = show_typical_topic_words(Specificity_Threshold)

save_topics_per_doc()
save_words_per_topic()
print 'nb:  one version of cT is ',np.sum(cDT,0),'\n and another is ',np.sum(cWT,0)
filename = os.path.join(localdir,'topic-specific-words.txt')
fp = open(filename, 'w')
show_typical_topic_words(Specificity_Threshold,fp)
fp.close()
print 'Wrote %s' % (filename)
