import numpy.random as rng
import numpy as np

def run_GibbsSamplerIteration(CT, CWT, CDT, CDWT,  num_itns=1):
    (nwords, ndocuments) = CWT.shape
    (ndocuments,ntopics) = CDT.shape
    for itn in range(num_itns):
        for d in range(ndocuments):
            for w in range(nwords): # note that w is just an int index
                # remember the current counts over topics for this (word,doc)
                topic_counts = CDWT[d,w,:].copy()
                #print '%10s \t %10s \t %s' % (doc,word,str(topic_counts))
                for t,c in enumerate(topic_counts):
                    for word_instance in range(c):
                        # decrement stuff
                        CDWT[d,w,t] -= 1
                        CWT[w,t] -= 1
                        CT[t] -= 1
                        CDT[d,t] -= 1
                        # multiply and divide stuff to get a tmp prob vector to sample from
                        #CDTdfake = CDT[d]
                        #CDTdfake[0] = CDTdfake[1:].sum() # pushes exactly half the topic prior into topic 0. Is different from doing same to alpha???? Every doc will have about 50% topic0 in it. This is hopefully going to grab the stop words. But of course the 50% is guessed...
                        #tmp = CWT[w] * CDTdfake / CT
                        tmp = CWT[w] * CDT[d] / CT 
                        tmp /= tmp.sum()
                        # choose a new topic for that word instance, from categorical distribution tmp
                        change = (rng.multinomial(1,tmp) == 1)  # MADNESS!!!
                        # increment stuff
                        CDWT[d,w,change] += 1
                        CWT[w,change] += 1
                        CT[change] += 1
                        CDT[d,change] += 1


