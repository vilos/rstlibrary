#!/usr/bin/env python
""" script to update library 
    input: bookid
    action: 
        svn update working copy of the book
        delete pickle cache
        (create new pickle)
"""
import sys, os, subprocess

from sensible.loginit import logger

log = logger(__name__)

parent = os.path.dirname
base = parent(parent(parent(parent(parent(__file__)))))
wcbase = os.path.join(base, 'var', 'vslib')



class WorkingCopy(object):
    
    def __init__(self, path=wcbase):
        
        if not os.path.exists(path):
            raise IOError('Path %s not found.' % wcbase)
        self.wcbase = path
        
    def wc_path(self, bookid):
        return os.path.join(self.wcbase, bookid)
    
    def svn_up(self, bookid):
        path = self.wc_path(bookid)
        cmd = ["svn", "up", path]
        #subprocess.check_call(cmd)  #, stdout=sys.stdout, stderr=sys.stderr)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
    
        return "\n".join([stdout, stderr]) 
        
        
def update(bookid):
    wc = WorkingCopy() 
    log.debug("svn up: %s", wc.wc_path(bookid))
    return wc.svn_up(bookid)
    #Cache(cachebase).invalidate(bookid)


if __name__ == '__main__':
    
    n = len(sys.argv)
    bookid = ''
    if n > 2:
        wcbase, bookid = sys.argv[1:]
    elif n > 1:
        bookid = sys.argv[1]
    if bookid:
        print update(bookid)
