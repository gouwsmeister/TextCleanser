#!/usr/bin/python

"""
    A command line accessor for the TextCleanser. Accepts noisy strings 
    as input on stdin and outputs normalised strings on stdout. 
    
    Author: Stephan Gouws
    Contact: stephan@ml.sun.ac.za    
"""

from cleanser import TextCleanser
import json
import codecs
import getopt
import sys, time
from random import choice

if __name__ == '__main__':
#    print "Noisy text cleanser"
    clnsr = TextCleanser() 
    
    text=sys.stdin.readline()
    while (text):
        if len(text)<=1:
            break
#        cleantext,error,replacements = clnsr.heuristic_cleanse(text, gen_off_by_ones=False)
        # to use a phonetic edit-distance based similarity function, use the
        # method below:         
#         cleantext,error,replacements = clnsr.phonetic_ED_cleanse(text, gen_off_by_ones=False)
        # to use SSK-based cleanser, use
        cleantext,error,replacements = clnsr.ssk_cleanse(text, gen_off_by_ones=False)
        
        if error=="ERROR":
            sys.stderr.write("ERROR")
            continue
        
        else:
            sys.stdout.write(cleantext)
            
        # need to flush the output buffers so that the java wrapper can read in the input
        sys.stdout.flush()
        sys.stderr.flush()           
        text=sys.stdin.readline()
            
