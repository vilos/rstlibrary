'''
'''

import os, time
from paste.deploy.loadwsgi import appconfig
from zope.component import getUtility
from books import Book, register_source, register_store
from books.interfaces import ISource, IStore
from restructured import publish2doc
from timing import print_timing

#import cProfile as profile
#import pstats
from pympler.muppy import muppy, tracker, summary, refbrowser

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

@print_timing
def publish(bookid):
    src = getUtility(ISource)
    return publish2doc(src[bookid])

@print_timing
def store(bookid):
    store = getUtility(IStore)
    src = getUtility(ISource)
    try:
        node = store[bookid]
    except KeyError:
        node = publish2doc(src[bookid])
        store[bookid] = node
    return node
    
@print_timing
def title(bookid):
    book = Book(bookid, None)
    title = book.title

@print_timing
def run(func):
    src = getUtility(ISource)
    keys = sorted(src.keys())
    
    for i, bookid in enumerate(keys):
        if i<1000:
            continue
        if i>1010:
            break
        print i,
        func(bookid)
    
    
def run_same(func, n = 5):
    bookid = '1281'
    #tr = tracker.SummaryTracker()
    #tr.print_diff()
    #tr.print_diff()  
    for i in range(n):
        #t = time.time()
        print i,
        func(bookid)
        #tr.print_diff()
        #print "%d. %s (%0.3f s)" % (i, bookid, time.time()-t)
    #tr.print_diff()

def close():
    store = getUtility(IStore)
    store.close()
    
def collect():
    
    import gc
    gc.set_debug(gc.DEBUG_STATS)
    gc.collect()
    gc.collect()
    
    
if __name__=='__main__':
    init()
    tr = tracker.SummaryTracker()
    run(title)
    close()
    
    #profile.run("run_same(store, 5)", filename='vslib.profile')
    tr.print_diff()
    
    #p = pstats.Stats('vslib.profile')
    #p.sort_stats('cumulative').print_stats(20)
if 0:
    objects = muppy.get_objects(include_frames=True)
    print muppy.get_size(objects)
    sum1 = summary.summarize(objects)
    summary.print_(sum1)
if 0:
    root = ''
    ib = refbrowser.InteractiveBrowser(root)
    ib.main()
if 1:
    import objgraph, inspect
    objgraph.show_most_common_types(limit=30)
    if objgraph.count('document') > 0:
        print 'document:', objgraph.count('document')
        docs = objgraph.by_type('document')
        d = docs[0]
        objgraph.show_backrefs(docs, max_depth=10)
        #chain = objgraph.find_backref_chain(d, inspect.ismodule)
        #in_chain = lambda x, ids=set(map(id, chain)): id(x) in ids
        #objgraph.show_backrefs(chain[-1], len(chain), filter=in_chain)
        
    #print 'document n: %d' % objgraph.count('document')
    #print 'section n: %d' % objgraph.count('section')
    
#import pdb; pdb.set_trace()
    
    