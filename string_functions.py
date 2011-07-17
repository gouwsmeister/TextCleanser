'''
Created on 14 Apr 2011

@author: stephan
'''
import shelve

class StringFunctions():
    
    def __init__(self, lamb, p):
        self.ssk_cache = shelve.open('ssk_lamb%.2f_p%d_cache' % (lamb, p))
        self.lamb=lamb
        self.p=p        
    
    def SSK(self, xi, xj):
        """Return subsequence kernel"""
        cache = self.ssk_cache
        lamb=self.lamb
        p=self.p        
        if len(xi)<p:
            p=len(xi)
        if len(xj)<p:
            p=len(xj)
        
        def SSKernel(xi,xj,lamb,p):
            mykey = str((xi, xj)) if xi>xj else str((xj, xi))
            if not mykey in cache:
                dps = []
                for i in xrange(len(xi)):
                    dps.append([lamb**2 if xi[i] == xj[j] else 0 for j in xrange(len(xj))])
                dp = []
                for i in xrange(len(xi)+1):
                    dp.append([0]*(len(xj)+1))
                k = [0]*(p+1)
                for l in xrange(2, p + 1):
                    for i in xrange(len(xi)):
                        for j in xrange(len(xj)):
                            dp[i+1][j+1] = dps[i][j] + lamb * dp[i][j+1] + lamb * dp[i+1][j] - lamb**2 * dp[i][j]
                            if xi[i] == xj[j]:
                                dps[i][j] = lamb**2 * dp[i][j]
                                k[l] = k[l] + dps[i][j]
                cache[mykey] = k[p]
            return cache[mykey]
        #return lambda xi, xj: SSKernel(xi,xj,lamb,p)/(SSKernel(xi,xi,lamb,p) * SSKernel(xj,xj,lamb,p))**0.5
        num=SSKernel(xi,xj,lamb,p)
        den=(SSKernel(xi,xi,lamb,p) * SSKernel(xj,xj,lamb,p))**0.5
        
        if den==0:
#            print "SSK ERROR: den==0!! xi=%s, xj=%s" % (xi, xj)
            # special case
            if len(xi)==1 or len(xj)==1:
#                print 'entering loop1'
                s=xi
                t=xj
                if len(xi)>len(xj):
                    s=xj
                    t=xi
                for i,c in enumerate(t):
                    if c==s[0]:
#                        print 'in loop 2'
                        return lamb**i/float(len(t))
            return 0.01    # crude override, return low similarity
        
        return num/den
 
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

    
if __name__=="__main__":
    print "String kernel module. Test case output:"
    kern = StringKernels(lamb=0.9, p=2)
    test_list = [['today', 'today'], ['today', '2day'], ['today', 'tdy'], ['today', 'tomorrow'], 
                 ['with', 'wth'], ['today', 'yesterday'], ['with', 'wif']]
    test_list2 = [('today', 'tdy'), ('today', 't'), ('today', 'd')]
    for test_case in test_list2:
        w1 = test_case[0]
        w2 = test_case[1]
        kern_sim = kern.SSK(w1,w2)
#        print kern_sim
        print "<%s, %s> = %.4f" % (w1, w2, kern_sim)