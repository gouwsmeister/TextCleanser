"""
    Confusion lattice decoder for the TextCleanser. This module requires SRI-LM toolkit
    in order to function, see the README.
"""

import os
import subprocess
import sys
import re

LATTICE_TOOL_DIR = "/media/Data/work/Tools/srilm/bin/i686-m64/"
LM_DIR = "/media/Data/work/Development/EclipseWorkspace/TextCleanser/data/"
EMPTY_SYM = "EMPTYSYM"   # placeholder for empty symbol
NGRAM_SERVER_IP = "12345@127.0.0.1"  # put the port@ip of ngram server 
                                     # if it isn't running on the local machine

class Decoder():
    """This class decodes a word lattice in pfsg format as output by Generator module's
        generate_word_lattice() function to produce the most likely sentence."""
        
    def __init__(self):
        """ ngram now gets started outside of this module via start_ngram_server.sh script, 
        so start_ngram_server() has become obsolete, although it might be a better way.. 
        """
        # check for presence of "lattice-tool"
        assert(os.path.exists(LATTICE_TOOL_DIR + "lattice-tool"))
        # check that "ngram" exists (for serving the language model)
#        assert(os.path.exists(LATTICE_TOOL_DIR + "ngram"))
        # start ngram in server mode 
        # TODO: Improve this to wait until server starts up and 
        # is running. should also gracefully exit when server already running
#        self.start_ngram_server()

    def start_ngram_server(self):
#        print "Starting ngram server"        
        ngram_server_command = LATTICE_TOOL_DIR+"ngram -lm "+LM_DIR+"tweet-lm.gz -mix-lm "+LM_DIR+"latimes-lm.gz -lambda 0.7 -mix-lambda2 0.3 -server-port 12345 &"
        p = subprocess.Popen(ngram_server_command, shell=True, stdin=subprocess.PIPE, 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
        
        # TODO: proper way is to wait for ngram to output 
        # "starting prob server on port 12345" ???                   

           
    def decode(self, word_mesh):
        """ @param word_mesh string containing word mesh to decode in pfsg format
            @return (stdout,stderr)
        """
        
        command = "%slattice-tool -in-lattice - -read-mesh -posterior-decode -zeroprob-word blemish -use-server %s " % (LATTICE_TOOL_DIR, NGRAM_SERVER_IP)        
        try:
            p = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
            stdout,stderr  = p.communicate(word_mesh)
            sys.exc_clear()     # workaround where pipe sometimes breaks, by trying to force the freeing of resources (file descriptors)
            
            # if sentence initial marker '<s>' not found, indicates something went wrong
            # during decoding
            if stdout.find("<s>")==-1:
                print "Decoder error output: ", stdout
                print "word_mesh: ", word_mesh
                return "", "ERROR"
            
            # strip out the sentence
            clean_sent = re.sub("- <s>(.*?)</s>", r'\1', stdout)
            # replace empty symbol tokens with ''
            clean_sent = clean_sent.replace(EMPTY_SYM, '')
            
            # if 'SOMENAME' still present in string, it also indicates something went wrong..
            # NB: 'find' returns starting index of matching substring in str, -1 if not found
            #if clean_sent.find("SOMENAME")!=-1:
                # error
#                print "Second error."
            #    print "Decoder error output: ", stdout
            #    print "word_mesh: ", word_mesh
            #    return "", "ERROR"
            
            # workaround for bug where p (and its associated pipes) do not 
            # seem to be terminated/closed properly
            os.system("killall lattice-tool > /dev/null 2>&1")
            # another possible solution
            #os.close(p.fileno())
        
            return clean_sent,stderr
        
        except subprocess.CalledProcessError, ce:
            sys.stderr.write("Error executing command: '%s'\n\n" % (str(ce)))
            return
        except OSError as os_e:     # I think this might be due to ngram server dying
            print "Intercepted OSError => ", os_e
            # restart ngram server
            self.start_ngram_server()
        except ValueError:
            print "Intercepted ValueError."
            return "ValueError thrown.", "ERROR"
    
if __name__ == "__main__":
    print "Decoder module."
