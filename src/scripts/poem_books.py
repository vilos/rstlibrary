#!/usr/bin/env python
''' find all books with poems
'''
import sys, re


from zope.component import getUtility
from books.interfaces import ISource, IStore
from books import configure

regenre = re.compile(r":genre:\ +poem") 
redirective = re.compile(r"..\ poem::")


def is_poems_missing_directive(bookid):
    src =  getUtility(ISource)
    text = src[bookid]
    
    if regenre.search(text):
        if not redirective.search(text):
            return True
    return False


def run():
    src = getUtility(ISource)
    keys = sorted(src.keys())
    
    for i, bookid in enumerate(keys):
        
        #print '%d.' % i,
        if is_poems_missing_directive(bookid):
            print bookid
        #else:
        #    print


def close():
    store = getUtility(IStore)
    store.close()
    
    
if __name__=='__main__':
    inifile = None
    if len(sys.argv) > 1:
        inifile = sys.argv[1]
        configure(inifile)
    else:
        configure()
    
    run()
    close()

    
    

    
    