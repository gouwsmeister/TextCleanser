"""
This module implements a version of the noisy text normalization system 
described in "Contextual Bearing on Linguistic Variation" by Gouws et al. (2011).

Author: Stephan Gouws
Contact: stephan@ml.sun.ac.za
"""

from generator import Generator
from decoder import Decoder
import re
import nltk

class TextCleanser(object):
    
    def __init__(self):
        """Constructor"""
        self.generator = Generator()
        self.decoder = Decoder()
#        print "READY"
    
    def heuristic_cleanse(self, text, gen_off_by_ones=False, ssk=False):
        """Accept noisy text, run through cleanser described in Gouws et al. 2011, and 
        return the cleansed text. 
        If gen_off_by_ones==True, generate spelling variants (1 edit distance away)."""
        gen = self.generator
        if ssk:
            string_sim_func=gen.SSK_SIM
        else:
            string_sim_func=gen.IBM_SIM
        replacements, old_tokens, candidates = gen.sent_generate_candidates(text, string_sim_func, 
                                                                            gen_off_by_ones)
#        print candidates
#        word_lattice = gen.generate_word_lattice(candidates)
        word_mesh = gen.generate_word_mesh(candidates)
        cleantext,error = self.decoder.decode(word_mesh)
        if error:
            print "mesh: ", word_mesh
            print cleantext
            print error
#            raw_input("[PRESS ENTER]")
#            exit(2)
#        print "clean: ", cleantext
        replacements = self.get_replacements(cleantext, old_tokens)                
        return cleantext, error, replacements
    
    def phonetic_ED_cleanse(self, text, gen_off_by_ones=True):
        gen = self.generator
        replacements, old_tokens, candidates = gen.sent_generate_candidates(text, gen.PHONETIC_ED_SIM, 
                                                                            gen_off_by_ones)
        #print candidates
#        word_lattice = gen.generate_word_lattice(candidates)
        word_mesh = gen.generate_word_mesh(candidates)
        cleantext,error = self.decoder.decode(word_mesh)
        replacements = self.get_replacements(cleantext, old_tokens)                
        return cleantext, error, replacements
    
    def ssk_cleanse(self, text, gen_off_by_ones=False):
        "Use subsequence overlap similarity function"
        return self.heuristic_cleanse(text, gen_off_by_ones, ssk=True)
    
    def log_oovs(self, text):
        """return a list of all out-of-vocabulary words for pre-processing purposes"""
        raise NotImplemented("Not yet implemented")

    def get_replacements(self, cleantext, old_tokens):
        """return the token replacements that were made"""
        new_tokens = self.generator.fix_bad_tokenisation(cleantext.split())
        # if new_tokens contain more tokens than old_tokens then alignment is screwed
        if len(new_tokens)>len(old_tokens):
            replacements = -1
        else:
            replacements = []
            for i, new_tok in enumerate(new_tokens):
                if i >= len(old_tokens):
                    break
                old_tok = old_tokens[i]
                if new_tok!=old_tok.lower():
                    replacements.append((old_tok, new_tok))
                    
        return replacements


if __name__ == "__main__":
    tc = TextCleanser()
    
    testSents = ['test sentence one', 'test s3ntens tw0', 't0day iz awssam', 'i jus talk to her.she ridin wit us',
                 'Whts papppin tho happy new years to u an ya fam', 
                 "Be sure 2 say HI to Wanda she's flying in from Toronto ;) 2 give a seminar on the art of correction, she'll b @ our booth",
                 "LOL i kno rite?", "Trying t fnd out if it does hav at as a word"]

#    test_confusion_set = [[(0.4, "w1"), (0.6, "w2")], [(0.3, "w3"),(0.3, "w4"), (0.4, "w5")]]
#    gen = Generator()
#    decdr = Decoder()
    
    for s in testSents:
        #c = gen.sent_generate_candidates(s)
        print "Sentence: ", s
        #print "Candidate list: ", c
        #word_lattice = gen.generate_word_lattice(c)
        #print "Word lattice: ", word_lattice
        cleantext,err,replacements = tc.heuristic_cleanse(s)
        print "Decoding result: ", cleantext    
        
