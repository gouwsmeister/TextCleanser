"""
Very simple HTTP-based server wrapper for the text normalisation system.

Author: Stephan Gouws
Contact: stephan@ml.sun.ac.za
Date: Jul 2011

"""

import cherrypy
from cherrypy import expose
from cleanser import TextCleanser

class CleanserWebService():
    
    def __init__(self):
        self.tc = TextCleanser()
    
    @expose
    def clean(self, text):
        cleantext, error, replacements = self.tc.ssk_cleanse(text)
        if error=="":
            return cleantext
        else:
            # an error occurred
            return error

if __name__ == "__main__":
    print  "Starting TextCleanser Web Service on localhost"
    cherrypy.quickstart(CleanserWebService())