import string
import numpy as np

def remove_linebreaks_and_punctuation(txt):
    # REMOVE LINE BREAKS AND PUNCUATION
    txt = txt.replace('-\n','') # hypen breaks don't get space..
    txt = txt.replace('\n',' ') # ...but normal line breaks do.
    for c in string.punctuation:
        txt = txt.replace(c,"").lower()
    txt = txt.replace('\'','')  # ...but normal line breaks do.
    return txt

def form_dictionary_of_counts(txtarray, stopwordslist, vocab=[]):
    counts = {}
    if len(vocab) > 0: 
        #print '     vocabulary is supplied.  ',
        for w in vocab:
            counts[w]=0 # initialise all words in the vocabulary to zero
    for w in txtarray:
        if (not w.isdigit()) and (len(vocab)==0 or w in vocab):
            if w in counts.keys():  counts[w] = counts[w] + 1
            else: counts[w] = 1
    # print '%d word instances in total' % (len(txtarray))
    # DELETE STOP WORDS
    for w in stopwordslist:
        if w in counts: 
            del counts[w]
    return counts

