
import re
from generator import Generator
from cleanser import TextCleanser
import string
import glob
#import cleanse_tweets
import shelve
import os

class Evaluator(object):
    '''
    This module computes evaluation statistics on text normalisation performance
    '''

    def __init__(self):
        self.gen = Generator()
        self.cleanser = TextCleanser()
        gen=self.gen
        cln=self.cleanser
        self.cleanse_methods = {gen.IBM_SIM : cln.heuristic_cleanse, 
                                gen.SSK_SIM : cln.ssk_cleanse,
                                gen.PHONETIC_ED_SIM : cln.phonetic_ED_cleanse}
        
    def load_gold_standard(self, file, data_accessor=None):
        """ load a parallel noisy-clean gold standard dataset into (noisyword, cleaned_word) tuples"""
        
        self.gold_word_pairs = []
        self.gold_sent_pairs=[]
        
        if data_accessor==None:         # default
            # load Bo Han's dataset
            sent_tok_pairs=[]
            
            for line in file:
                # read nr of tokens
                if re.search("^[0-9]+?\n$", line):
                    # this shows how many consecutive tokens are printed next, we just discard this
                    if len(sent_tok_pairs)>0:
                        self.gold_sent_pairs.append(sent_tok_pairs)
                        sent_tok_pairs=[]                    
                    continue
                noisy,clean = [w.strip(' \n') for w in line.split('\t')]
                
                sent_tok_pairs.append((noisy,clean))
                self.gold_word_pairs.append((noisy,clean))
            
#            self.gold_sent_pairs = [self.gold_sent_pairs[73]]
            
            print "Loaded %d gold word pairs." % (len(self.gold_word_pairs))
            print "Loaded %d gold sentence pairs." % (len(self.gold_sent_pairs))
                    
        else:
            # TODO: include ability to handle input-output sentences, segment, align, load as pairs
            raise NotImplementedError("No other accessors implemented.")
        
    
    def log_oov_from_gold_pairs(self, oov_file):
        """ Log all OOV tokens in gold standard to log file"""
        for (noisy,clean) in self.gold_word_pairs:
            result = self.gen.get_OOV(noisy)
            if result!=[]:
                # write all expanded variants to file
                oov_file.write(','.join(result)+'\n')

    def log_repl(self, repl_log_f, tweet_id, repl):
        """Log all replacements made to disk"""
        if type(repl)==type([]):
            for r in repl:
                repl_log_f.write("%s\t%s\t%s\n" % (tweet_id, r[0], r[1]))
    
    def get_cleanser_output(self, rankmethod, input=None, log_replacements=False):
        """Expects input as [[(token 1, gold token 1), ..], ..] sentence pairs""" 
        # run the cleanser using the specified $rankmethod over all sentence pairs
        if rankmethod in self.cleanse_methods.keys():
            selectormethod = self.cleanse_methods[rankmethod]                
        else:
            print "$rankmethod is not valid."
            exit(2)
            
        if log_replacements:
            repl_log = open('replacements.log', 'w')
            
        if not input:
            input = self.gold_sent_pairs
            
        self.gold_sent_clean = []
                
        n=0
        for sent_num,sent_in_tok in enumerate(input):
            print "Processing sentence %d" % (n)
            n+=1
            
            # reconstruct sentence string, assuming it's in the form [(token 1, gold token 1), ..]
            sent_str = ' '.join([tok_pair[0] for tok_pair in sent_in_tok])
            
            gen=self.gen
            sent_clean, error, replacements = selectormethod(sent_str, gen_off_by_ones=False)
            if log_replacements:
                self.log_repl(repl_log, sent_num, replacements)
            
            if error:
                print "Error: ", error
                continue
            print "In: %s\nOut:%s" % (sent_str, sent_clean)
            sent_clean_tok = sent_clean.split()            
            # pack as (original token, cleaned token, gold token)
            in_out_gold = []
            for s,c in zip(sent_in_tok, sent_clean_tok):
                in_out_gold.append((s[0],c,s[1])) 
            self.gold_sent_clean.append(in_out_gold)
          
        print "self.gold_sent_clean has %d items" % (len(self.gold_sent_clean))   
    
    def clean_word(self, w):
        """
            compare output-gold pairs only based on the alphanumeric characters they contain. 
        """        
        return re.sub("[^a-z0-9]", "", w)
    
    def log_oracle_pairs(self, oracle_log_f): 
            oracle_log_f.write("====New oracle log\n")
            clean=self.clean_word
            oracle_in_out_gold = [(clean(w[0]), clean(w[1]), clean(w[2])) for sent in self.gold_sent_clean for w in sent if len(w)==3 and w[0]!=w[2]]
            for p in oracle_in_out_gold:
                oracle_log_f.write('\t'.join(p)+'\n')
                
            oracle_log_f.close()
            
            
    def compute_wer(self, sent_output_gold_pairs=None):  
        """flatten out the [[(word,gold), ...], ..] list, compute global word error rate"""      
        if not sent_output_gold_pairs:
            # take cleaned out + gold output from gold standard
            # i.e. run get_cleanser_output first
            print "Taking output,gold pairs."
            #sent_output_gold_pairs = [(w[1],w[2]) for sent in self.gold_sent_clean for w in sent if len(w)==3]
            # ORACLE EXPERIMENT: Compare only output when we know INPUT is incorrect when input!=gold
            # w == (in, out, gold), therefore check if w[0]==w[2]
            clean=self.clean_word
            sent_output_gold_pairs = [(clean(w[1]),clean(w[2])) for sent in self.gold_sent_clean for w in sent if clean(w[0])!=clean(w[2])]
                
        self.log_oracle_pairs(open('oracle_pairs.log', 'a'))   
#        print sent_output_gold_pairs
#        print self.gold_sent_clean

        num_incorrect=0
        # this computes N as ONLY the number of ORACLE pairs (known to be different)
#        N=len(sent_output_gold_pairs)
        # this computes N over ALL in-out tokens     
        N=sum([len(s) for s in self.gold_sent_clean])
        for out_gold_pair in sent_output_gold_pairs:
            if out_gold_pair[0]==out_gold_pair[1]: # or out_gold_pair[0]=="*E*": # out_gold_pair == (output, gold)
                continue
            else:
                num_incorrect += 1
        return float(num_incorrect) / float(N)
    
    def compute_p_r_f(self):
        """Compute precision, recall and f-score"""
        pass
    
    def compute_bleu(self, sentence_pair):
        """ Compute the bleu score"""
        pass
    
if __name__=="__main__":
    print "Evaluator module."
    
    for i in [1]:  # can e.g. cycle over rankmethod or other options to compare different parameter settings 
        ev=Evaluator()
        file=open('data/han_dataset/corpus.tweet2', 'r')
        ev.load_gold_standard(file)
        ev.get_cleanser_output(rankmethod=Generator.SSK_SIM, log_replacements=True)
        wer = ev.compute_wer()
        print "WER = %f" % (wer)
