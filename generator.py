"""
    This module generates candidate words by comparing possibly noisy
    words against words in the lexicon and returning the words it considers
    most likely candidates.
    
    Author: Stephan Gouws
    Contact: stephan@ml.sun.ac.za
"""

import nltk
import collections, itertools
import shelve, cPickle
import heapq
import time, math
import re, string, csv
from phonetic_algorithms import PhoneticAlgorithms
from string_functions import StringFunctions

# constants
LEXICON_FILENAME = "data/combined_lex.pickl"
PHON_LEX_FILENAME = "data/phonetic_lex.pickl"
PHONE_LEX_KEYS_FILENAME = "data/phonetic_lex_keys.pickl"
SUB_LEX_FILENAME = "data/sub_lexicon.pickl"
STOPWORDS = cPickle.load(open("data/stopwords-set.pickl", "rb")) #set(nltk.corpus.stopwords.words())
ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
CONSONANTS = "bcdfghjklmnpqrstvwxyz"
PUNC = string.punctuation
#LATTICE_TOOL_DIR = "/media/Data/work/Tools/srilm/bin/i686-m64/"
EMPTY_SYM = "EMPTYSYM"   # placeholder for empty symbol, such that tokeniser doesn't split it

class Generator:
    
    # CLASS CONSTANTS
    # Candidate word selection methods
    IBM_SIM=0
    SSK_SIM=1
    PHONETIC_ED_SIM=2
        
    def __init__(self, lexicon=None):
        
        # load the lexicon from a pickled dump
        # we use the Top20K words in gigaword intersected with CMU
        # pronunciation dictionary, adapt this to your needs
        self.lexicon = cPickle.load(open(LEXICON_FILENAME, 'rb'))
        
        # load the phonetically indexed lexicon        
        try:
            self.phon_lex = cPickle.load(open(PHON_LEX_FILENAME, 'rb'))
#            print "Loaded phonetically indexed lexicon with %d partitions." % (len(self.phon_lex.keys()))
        except IOError:
            # build phonetic lexicon
            self.phon_lex = self.build_phonetic_index()
            cPickle.dump(self.phon_lex, open(PHON_LEX_FILENAME, 'wb'))
        # load the list of phonetic keys
        self.phonetic_keys = self.phon_lex.keys()
            
        # load lexicon sub-indexed by first consonant       
        try:
            self.sub_lexicon = cPickle.load(open(SUB_LEX_FILENAME, 'rb'))
#            print "Loaded sub-indexed lexicon with %d partitions." % (len(self.sub_lexicon.keys()))
        except IOError:
            # build sub-lexicon
#            self.lexicon = cPickle.load(open(LEXICON_FILENAME, 'rb'))
            #for w in self.lexicon:      # remove one-letter entries
            #    if len(w)<=1:
            #        del w
            self.sub_lexicon = self.build_sub_index()
            cPickle.dump(self.sub_lexicon, open(SUB_LEX_FILENAME, 'wb'))
        
        # load list of common abbreviations, adapt common_abbrs.csv to your own needs
        self.abbr_list = {}
        for row in csv.reader(open("data/common_abbrs.csv"), delimiter=","):
            self.abbr_list[row[0]] = row[1]
#        print "Loaded list of %d common abbreviations." % len(self.abbr_list)
        
        # initialise translit dictionary
        translit_inits = {'0': ['0','o'], 
                         '1':['1','l','one'], 
                         '2':['2','to', 'two'],
                         '3':['3','e', 'three'],
                         '4':['4','a', 'four', 'for'], 
                         '5':['5','s', 'five'], 
                         '6':['6','six','b'], 
                         '7':['7','t', 'seven'],
                         '8':['8','eight','ate'], 
                         '9':['9','nine','g'],
                         '@':['@', 'at'],
                         '&':['&', 'and']}
        self.translit = {}
        self.translit.update(translit_inits)        
     
#        print "Loaded lexicon of size: ", len(self.lexicon)
        
        # generate K possible noisy expansions per word.
        self.topK = 10
        
        # load phonetic similarity function
        self.phon_sim = PhoneticAlgorithms().double_metaphone
        # load subsequence-kernel similarity function
        ssk=StringFunctions(lamb=0.8, p=2)
        self.ssk_sim = ssk.SSK
        
        # smiley regex
        self.smiley_regex = re.compile("[:;]-?[DP()\\\|bpoO0]{1,2}")     # recognise emoticons
        self.lt_gt_regex = re.compile("\&[lr]t;[\d]?")
        #pnc = ''.join(l for l in [string.punctuation]) + " \t"  # remove double punctuation and spaces
        # regexes for detecting usernames, hashtags, rt's and urls at the token level
        self.hashTags = re.compile("^#(.*)")    
        self.username = re.compile("@\w+")
        self.rt  = re.compile("^rt")
        # this regex from: http://snipplr.com/view/36992/improvement-of-url-interpretation-with-regex/
        # I made the http required (+) since otherwise it matches things like 'River.With'
        # where users did not put a space between the end of sentence and next word
        self.urls = re.compile("((https?://)+([-\w]+\.[-\w\.]+)+\w(:\d+)?(/([-\w/_\.]*(\?\S+)?)?)*)")
        #self.sim_cache = shelve.open('sim_cache')
        
    def build_phonetic_index(self):
        """Index the lexicon phonetically to reduce lookup time. However this failed 
            epically and only reduced search space by half on average..."""        
        print "Building phonetic index over %d words." % (len(self.lexicon))
        t1 = time.time()        
        phon_lex = collections.defaultdict(list)
        dbl_metaphone = PhoneticAlgorithms().doubleMetaphone
        for w in self.lexicon:
            m = dbl_metaphone(w)
            phon_lex[m[0]].append(w)
            if m[1] != None:
                phon_lex[m[1]].append(w)            
        print "Finished building phonetic index in %d seconds." % (time.time() - t1)
        return phon_lex
    
    def build_sub_index(self):
        """Index the lexicon by the first consonant, or first letter if no 
            consonant found, for faster lookup"""
        cons_lex = collections.defaultdict(list)
        for w in self.lexicon:
            first_letter = self.get_first_cons(w)                
            cons_lex[first_letter].append(w)
        return cons_lex
    
    #@profile
    def lcs_len1(self, xs, ys):
        '''
        from: http://wordaligned.org/articles/longest-common-subsequence
        Return the length of the LCS of xs and ys.
    
        Example:
        >>> lcs_length("HUMAN", "CHIMPANZEE")
        4
        '''
        ny = len(ys)
        curr = list(itertools.repeat(0, 1 + ny))
        for x in xs:
            prev = list(curr)
            for i, y in enumerate(ys):
                if x == y:
                    curr[i+1] = prev[i] + 1
                else:
                    curr[i+1] = max(curr[i], prev[i+1])
        return curr[ny]
    
    #@profile
    def lcs_len2(self, X, Y):
        '''
            http://en.wikibooks.org/wiki/Algorithm_implementation/Strings/Longest_common_subsequence#Computing_the_length_of_the_LCS
        '''
        m = len(X)
        n = len(Y)
        
        # An (m+1) times (n+1) matrix
        C = [[0] * (n+1) for i in range(m+1)]
        for i in range(1, m+1):
            for j in range(1, n+1):
                if X[i-1] == Y[j-1]: 
                    C[i][j] = C[i-1][j-1] + 1
                else:
                    C[i][j] = max(C[i][j-1], C[i-1][j])
        return C[i][j]

    #@profile
    def cs(self, s):
        '''
            generates the consonant skeleton of a word, 'shop' -> 'shp'
        '''
        return ''.join([l for l in s.lower() if l not in 'aeiou'])

    #@profile
    def edit_dist(self, s1, s2):
        if len(s1) < len(s2):
            return self.edit_dist(s2, s1)
        if not s1:
            return len(s2)
     
        previous_row = xrange(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
                deletions = current_row[j] + 1       # than s2
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
     
        return previous_row[-1]

    #@profile
    def lcs_ratio(self, word1, word2):
        '''
            Return the LCS / max(len(w1),len(w2))
        '''
        return float(self.lcs_len1(word1,word2)) / max(len(word1),len(word2))    

    #@profile
    def contractor_sim(self, s1, s2):
        '''
            Implementation of Contractor et al.'s similarity function
        '''
        """# Cache results
        key = s1+'.'+s2
        key = key.encode("utf-8")
        sim_val = 0.0
        if key not in self.sim_cache:
            lcs_ratio = self.lcs_ratio(s1,s2)
            sim_val = self.sim_cache[key] = float(lcs_ratio / (self.edit_dist(self.cs(s1), self.cs(s2))+1))
        else:
            sim_val = self.sim_cache[key]"""
        lcs_ratio = self.lcs_ratio(s1,s2)
        sim_val = float(lcs_ratio / (self.edit_dist(self.cs(s1), self.cs(s2))+1))
        return sim_val
    
    def phonetic_ed_sim(self, s1, s2):
        """Computes the phonetic edit distance SIMILARITY between two strings"""
        return math.exp(-(self.edit_dist(s1, s2)))

    #@profile
    def expand_word(self, noisyWord):
        '''
            Expand 1) transliterate letters 2) ??...
        '''
        expTmp = ['']   # .. and empty candidate strings

        # generate possible transliterations
        for l in noisyWord:
            expansions = []
            try:
                translits = self.translit[l]
            except KeyError:
                translits = [l]
            for e in expTmp:
                for c in translits:
                    expansions.append(e + c)
            expTmp = expansions[:]
        return expTmp  #.append(self.expand_token(noisyWord)) 

    def get_first_cons(self, word):
        """Get first consonant or just first letter if no consonant found"""
        for l in word:
            if l in CONSONANTS:
                return l
        return word[0]
   
    def word_edits(self, word):
        """Norvig's spelling corrector code for generating off-by-one candidates"""
        splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes    = [a + b[1:] for a, b in splits if b]
        transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
        replaces   = [a + c + b[1:] for a, b in splits for c in ALPHABET if b]
        inserts    = [a + c + b     for a, b in splits for c in ALPHABET]
        return set(deletes + transposes + replaces + inserts)
    
    def expand_abbrs(self, tok):
        """Look for and expand commonly occurring Internet and other abbreviations.
            Edit the list in data/common_abbrs.csv. 
            Note that it is a deterministic replacement.
        """        
        try:
            return self.abbr_list[tok]
        except KeyError:
            return None
    
    def rank_candidates(self, candidates, lexicon_list, sim_function, gen_off_by_ones):
        """Rank all tokens in candidates with tokens found in lexicon. To make the use
            of sub-lexicons possible, it uses lexicon_list[i] for i,token in enumerate(candidates), 
            i.e. you pass a lexicon_list[i] for each token
            TODO: Might use lexicon and sub_lex parameters instead?
            """
        # Generate all 'off-by-one' variants
        if gen_off_by_ones:
            off_by_ones = []
            for candidate in candidates:
                off_by_ones.extend([w for w in self.word_edits(candidate)])  # if w in lexicon]
            candidates.extend(list(set(off_by_ones)))
            #print len(noisyWords), " after adding edits."
        
        # compute scores with words in lexicon
        K = self.topK
        topK = []    # top K heap of candidate words
        
        curW = 0
        for i,cand_token in enumerate(candidates):
            #for w in self.lexicon:
            lexicon=lexicon_list[i]
            for w in lexicon:
                #if len(w)>=len(cand_token):
                sim = sim_function(cand_token, w)
                if sim==0:      # don't add zero-prob words
                    continue
                if curW < K:        # first K, just insert into heap
                    heapq.heappush(topK, (sim, w))
                else:           # next (N-K), insert if sim>smallest sim in heap (root)
                    try:
                        if (sim > topK[0][0]):
                            heapq.heapreplace(topK, (sim,w))
                    except IndexError:
                        heapq.heappush(topK, (sim, w))
                curW += 1
        
        #return heapq.nlargest(K, topK, key=lambda x:x[0])
        conf_set = heapq.nlargest(K-1, topK, key=lambda x:x[0])
        # remove all 0-prob elements
        for elem in conf_set:
            if elem[0]==0:
                del elem
        return conf_set

    def hash_user_rt_url(self, tok):
        #if noisyWord in ['rt', 'hshtg', 'usr', 'url', EMPTY_SYM]:
        hashTags=self.hashTags
        username=self.username
        rt=self.rt
        urls=self.urls
        if hashTags.search(tok) or username.search(tok) or rt.search(tok) or urls.search(tok):
            return True
        else:
            return False

    
    def check_oov_but_valid(self, noisyWord):
        # check if it is a common abbreviation or contracted form
        # TODO: Is this the right place to do this?
        abbr = self.expand_abbrs(noisyWord.strip("'"))
        if abbr != None:
            # TODO: this never replaces lol, etc with EMPTY_SYM after decoding
#            return [(0.8, abbr), (0.2, noisyWord)]
            return [(1.0, abbr)]
        
        # check if it's a number, longer than 1 char
        # TODO: Do better detection to catch any token with no letters
        # e.g. "9/11" (dates), "4-4" (scores), etc. and ignore
        # Simple first idea, if it contains _no letters_, ignore
        
        if not re.search("[a-z]", noisyWord):         
            return [(1.0, noisyWord)]
        
        # check for punctuation
        if noisyWord in PUNC:
            return [(1.0, noisyWord)]
        
        # check for USR or URL or EMPTY_SYM  special tokens
#            noisy=hashTags.sub('hshtg', username.sub('usr', rt.sub('rt', urls.sub('url', noisy))))
        if self.hash_user_rt_url(noisyWord) or noisyWord in [EMPTY_SYM]:
            return [(1.0, noisyWord)]
        
        # otherwise
        return None

    
    #@profile
    def word_generate_candidates(self, noisyWord, rank_method, off_by_ones=False):
        """Generate a confusion set of possible candidates for a word using some rank_method,
            currently supported methods include:
            Generator.IBM_SIM - implementation of the heuristic used in Contractor et al. 2010
            Generator.SSK_SIM - a 2-char string subsequence similarity function
            Generator.PHONET_ED_SIM - a phonetic edit distance"""
        
        oov_but_valid = self.check_oov_but_valid(noisyWord)
        if oov_but_valid:
            return oov_but_valid
        
        # TODO: This seems clumsy, lexicon should include STOPWORDS by default
        if noisyWord not in self.lexicon and noisyWord not in STOPWORDS:       # O(1) for sets            
            # expand noisy word 
            noisyWords = self.expand_word(noisyWord)
            
            # 1) IBM_SIMILARITY and SUBSEQUENCE-KERNEL SIMILARITY
            if rank_method in [Generator.IBM_SIM, Generator.SSK_SIM]:
                first_letters = [self.get_first_cons(w) for w in noisyWords]
                lexicon=[self.sub_lexicon[first_letter] for first_letter in first_letters]
                if rank_method == Generator.IBM_SIM:
                    sim_function=self.contractor_sim
                else:
                    sim_function=self.ssk_sim
                candidates=noisyWords
                conf_set = self.rank_candidates(candidates, lexicon, sim_function, off_by_ones)
                
            # 2) PHONETIC EDIT DISTANCE SIMILARITY
            elif rank_method==Generator.PHONETIC_ED_SIM:
                # candidates=set([self.phon_sim(c)[0] for c in noisyWords])
                # Include both primary and secondary codes!
                candidates=[]
                for c in noisyWords:
                    phonetic_c = self.phon_sim(c)
                    if phonetic_c[0]:
                        candidates.append(phonetic_c[0])
                    if phonetic_c[1]:
                        candidates.append(phonetic_c[1])                    
#                sim_function=self.edit_dist
                lexicon=[self.phonetic_keys for i in range(len(candidates))]                
                sim_function=self.phonetic_ed_sim
                phon_conf_set = self.rank_candidates(candidates, lexicon, sim_function, off_by_ones)
#                print "noisyWords: ", noisyWords
#                print "phonetic codes: ", candidates
#                print "phonetic confusion set: ", phon_conf_set
                # expand phonetic codes into their likely candidate words
                conf_set = []
                for sim,phonetic_code in phon_conf_set:
                    conf_set.extend([(sim,w) for w in self.phon_lex[phonetic_code]])
                # retain the top 20
                conf_set = conf_set[:10]
                
            else:
                raise NotImplementedError("Unknown rank_method supplied as argument.")         

            # heuristic: add original word with same prob as lowest prob word in case it's a valid OOV word!
            try:
                weight = conf_set[-1][0]
            except IndexError:
                weight = 1.0        # there's nothing in the confusion set
            if weight==0:
                weight = 0.2        # add original word with some low probability
            conf_set.append((weight, noisyWord))
            return conf_set                                      
            
        else:
            # this is a valid word in the lexicon
            # NOTE: This would miss (i) (special case) accidental homophilous misspellings, such as 'rite' and 'right'
            # also (ii) (the general case) spelling errors where a spelling error leads to a valid word in the lexicon
            # 'it' -> 'is', 'are' -> 'art', 'party' -> 'part', etc.
            # only way to get (ii) is to use a spelling error approach and include all 'off-by-one' errors in the
            # confusion set, e.g. as computed by Norvig's spelling corrector. For (i) need to use phonetic lookup.
            return [(1.0, noisyWord)]
 
    def get_OOV(self, noisyWord):
        if self.check_oov_but_valid(noisyWord) or noisyWord in self.lexicon or noisyWord in STOPWORDS:
            return []
        else:
            return self.expand_word(noisyWord)
 
    def sent_preprocess(self, sent):
        # collapse punctuation marks occurring > 1 into one
        #rem_dbl_punc = re.compile(r"([%s])\1+" % (pnc))       # remove punctuation chars repeated > once
        pass
 
    def fix_bad_tokenisation(self, tokens):
        """Fix some general tokenisation issues"""
        
        # Split run-on tokens where we have two words separated by a punctuation mark, 
        # or one word with leading or trailing punctuation
        punc = [p for p in PUNC if p not in ("'", "@", "#")]
        split_runon_tokens = re.compile("(\w*)([%s]*)(\w*)" % (punc))
        out_tokens = []
        for tok in tokens:
            if self.hash_user_rt_url(tok):
                # keep as is so we don't split '@user'->['@', 'user'], or urls into god knows what
                out_tokens.append(tok)
            else:
                out_tokens.extend([tok for tok in split_runon_tokens.sub(r'\1 \2 \3', tok).split(' ') if tok!=''])
        return out_tokens
 
    def sent_generate_candidates(self, sent, rank_method, off_by_ones=False, log_OOV=False):
        """Generate 'confusion set' from a sentence.
            Return (r,w,c) replacements made (smileys), words after tokenisation and confusion set."""        
        # perform some simple pre-processing
        # 1) remove emoticons
        # for bookkeeping, keep track of all replacements
        replacements = []
        
        # For the evaluation task, do not remove smileys
        """for change in self.smiley_regex.findall(sent):
            replacements.append((change, ''))      # (x,y) for x->y
        # TODO: Handle 'left-handed' emoticons..
        sent = self.smiley_regex.sub('', sent)
        """
        
        # replace all spurious &lt; and &gt; html artifacts..
        sent = self.lt_gt_regex.sub('', sent)
        
        # split into words
        # TODO: Get a better tokeniser...
        words = sent.split()
        # fix bad tokenisation issues
        words = self.fix_bad_tokenisation(words)
        
        if log_OOV:
            confusion_set=[self.get_OOV(nw.lower()) for nw in words]
        else:
            # get candidates for each word
            confusion_set = [self.word_generate_candidates(nw.lower(), rank_method, off_by_ones) for nw in words]
        
        return replacements, words, confusion_set
    
    def generate_word_mesh(self, confusion_net):
        """
            A word mesh is a more constrained form of a word lattice.
            It follows much more readily given the confusion network input,
            and lets SRI-LM create the lattice itself.
        """
        
        conf_net = []
        for nodes in confusion_net:
            # remove zero probability words and empty words
            keepnodes = [n for n in nodes if n[0]>0 and n[1]!='']
            if len(keepnodes)>0:
                conf_net.append(keepnodes) 
            else:
#                print "NODES: ", nodes
                conf_net.append([(1.0, '*E*')])
        
        pfsg_out = ["name SOMENAME\n"]          
        pfsg_out.append("numaligns " + str(len(conf_net)) + "\n")
        pfsg_out.append("posterior 1\n")
        for i,nodes in enumerate(conf_net):
            align_str = "align " + str(i)
            
            # normalising constant for nodes' probabilities
#            print to_nodes            
            nodes_total = sum([n[0] for n in nodes])
            
            for node in nodes:
                p=node[0]
                w=node[1]
                align_str += " %s %f" % (w, p/nodes_total)
            align_str += "\n"
            pfsg_out.append(align_str)
            
        return ''.join(pfsg_out)                  
        
"""
 TODO ideas list:
 1) pre-process and normalise letters occurring more than 2 consecutive times..
 2) Implement a recaser, using the original sentence as guide for recasing clean sentence
 3) Find suitable heuristic to avoid 'normalising' words which are correct e.g. 
     neologisms, names, etc. This is tougher and might require training a classifier to 
     detect OOV words, as in (Han and Baldwin, 2011). 
"""
                     
if __name__ == "__main__":
    
    testWords = ['t0day', 'today', 't0d4y', 'w0t', 'wh4t']
    testSents = ['test sentence one', 'test s3ntens tw0', 't0day iz awssam']
    test_confusion_set = [[(0.4, "w1"), (0.6, "w2")], [(0.3, "w3"),(0.3, "w4"), (0.4, "w5")]]
    
    gen = Generator()
    
    for w in testWords:
#        print gen.expand_word(w)
        print gen.word_generate_candidates(w)
    
    for s in testSents:
        c = gen.sent_generate_candidates(s)
        print "Sentence: ", s
        print "Candidate list: ", c
        word_lattice = gen.generate_word_mesh(c)
        print "Word mesh: ", word_mesh
        
        
