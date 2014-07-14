# -*- coding: utf-8 -*-
#NB:  PyTagCloud install instructions at https://github.com/atizo/PyTagCloud
from pytagcloud import create_tag_image, create_html_data, make_tags, \
    LAYOUT_HORIZONTAL, LAYOUTS
from pytagcloud.colors import COLOR_SCHEMES
from pytagcloud.lang.counter import get_tag_counts
import sys,os
import numpy as np
import numpy.random as rng
from operator import itemgetter
max_words_displayed = 80 # gets a bit crowded above this.


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print('eg: python %s texts/ACorpus/cWT.csv   texts/ACorpus/topics   30'  % (sys.argv[0]))
        sys.exit('usage: python %s  ....cWT.csv  output_dir    [max_font_size]' % (sys.argv[0]))

    infile = os.path.join(os.getcwd(), sys.argv[1])
    output_dir = os.path.join(os.getcwd(), sys.argv[2])
    if not os.path.exists(output_dir):
        os.mkdir(output_dir )            
    max_size = 80
    if len(sys.argv) == 4:
        max_size =  int(sys.argv[3])

    cwt = [] # note that counts are still just strings at this point
    wordtokens = []
    fp = open(infile,'r')
    topictokens = fp.readline().strip(' \r\n').replace(';',',').split(',')
    topictokens = topictokens[1:] # UGLY....
    for line in fp:
        elts = line.replace(';',',').strip('\n').split(',')
        wordtokens.append(elts[0])
        therest = elts[1:]
        cwt.append(therest)
    fp.close()
    cWT = np.array(cwt, float) + 0.001
    num_words = cWT.shape[0]
    num_topics = cWT.shape[1]
    # if choice is "dominant" we leave cWT as raw counts, but if it is
    # 'discrim', we normalise over topics, so as to highlight words
    # that discriminate this topic over all others.

    # for each word, normalise over topics to get how specific it is to THIS topic.
    normed_cWT = cWT / cWT.sum(1).reshape(num_words,1)

    # Now, for each topic, make up a big list of strings chosen at
    # random from the word probabilities for that topic, and make a
    # cloud image out of them.
    for t,topic in enumerate(topictokens):
        topic = topic.strip()
        #tmp  = np.power(cWT[:,t],1.0)
        #word_popularity  = tmp / np.max(tmp)  # max of 1
        word_popularity  = cWT[:,t]  / np.max(cWT[:,t])  # max of 1
        word_topicality = normed_cWT[:,t] # max of 1
        print '-------------------------'

        print 'topic: ',topic
        tags = []
        max_shade, min_shade = 255, 5
        for i in range(num_words):
            wd = wordtokens[i]
            wty = word_topicality[i] 
            wpy = word_popularity[i]
            sz = int(max_size * wty)
            # relative populatity is blue-ness, in the following scheme
            b = int(min_shade + (max_shade - min_shade) * wpy)
            g = 115+ rng.randint(35)
            r = 255-g #120+ rng.randint(25)
            #print (r,g,b)
            tags.append({'tag':wd, 'size':sz, 'color':(r,g,b)})

        # Sort the tags according to their 'size' value, so we display the important ones.
        tags = sorted(tags, key=itemgetter('size'), reverse=True)

        # and make the image
        image_name = os.path.join(output_dir,'%s.png' % (topic))
        create_tag_image(tags[:max_words_displayed], image_name, 
                         size=(600, 600), background=(0, 0, 0, 255), 
                         layout=LAYOUT_HORIZONTAL, fontname='Nobile')
        print 'Wrote image to ',image_name

    #print COLOR_SCHEMES.keys()  # shows the options...
