''' find all books with poems
'''

from books import  register_source, register_store
from books.interfaces import ISource, IStore
from paste.deploy.loadwsgi import appconfig
from zope.component import getUtility
import os



def init():
    config_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..','develop.ini'))
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
    
    if 'poem' in text:
        if not '.. poem::' in text:
            return True
    return False


def run():
    src = getUtility(ISource)
    keys = sorted(src.keys())
    
    for i, bookid in enumerate(keys):
        #if i<1000:
        #    continue
        #if i>1010:
        #    break
        
        #print '%d.' % i,
        if is_poems_missing_directive(bookid):
            print bookid
        #else:
        #    print


def close():
    store = getUtility(IStore)
    store.close()
    
    
if __name__=='__main__':
    init()
    run()
    close()
    
    

    
    