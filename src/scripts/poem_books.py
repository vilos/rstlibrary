#!/usr/bin/env python
''' find all books with poems
'''
import os,sys, re
from books import  register_source, register_store
from books.interfaces import ISource, IStore
from paste.deploy.loadwsgi import appconfig
from zope.component import getUtility

regenre = re.compile(r":genre:\ +poem") 
redirective = re.compile(r"..\ poem::")

def init(path):
    config_path = os.path.realpath(path)
    base, name = os.path.split(config_path)
    config = appconfig('config:%s' % name, name='vslibrary', relative_to=base)
    
    src_path = config.get('src_path')
    store_url = config.get('store_url')
    cache_url = config.get('cache_url')
    max_entries = 10
    
    register_source(src_path)
    register_store(store_url, cache_url, max_entries=max_entries)


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
    if len(sys.argv) > 1:
        init(sys.argv[1])
        run()
        close()
    else:
        print "Usage: %s path_to_paste_ini_file" % sys.argv[0]
    
    

    
    