import os
from interfaces import ICatalogSearch
from zope.interface import implements
from zope.component import getSiteManager
from ore.xapian.search import ConnectionHub
from utils import decode


class ConnectionPool(object):
#    implements(IXapianConnection)

    def __init__(self, database):
        self.database = database
        self.connections = ConnectionHub(database)

    def get_connection(self):
        return self.connections.get()



class CatalogSearch(object):
    
    implements(ICatalogSearch)
    
    start = 0
    limit = 9999
    
    def __init__(self, database, n=20):
        self.pool = ConnectionPool(database)
        self.n = n      # results per page
        
    def alphas(self, language='en'):
        conn = self.pool.get_connection()
        query = conn.query_field('type', 'Book')
        query = query and conn.query_field('language', language)
        aset = set()
        for brain in conn.search(query, self.start, self.limit, checkatleast=-1):
            if 'alpha' in brain.data:             
                aset.add(brain.data['alpha'][0])
                
        return sorted(aset)
    
    def books(self, alpha=''):
        conn = self.pool.get_connection()
        query = conn.query_field('type', 'Book')
        if alpha:
            filter = conn.query_field('alpha', alpha)
            query = conn.query_filter(query, filter)
        #query = searcher.query_parse(query)
        shelf = []
        for brain in conn.search(query, self.start, self.limit, sortby='sortable_title'):
            bookid = os.path.basename(brain.id)
            b = dict(id=brain.id, bookid=bookid, url=brain.id.replace('public','books'))  #TODO: fix index and remove replace
            for k in brain.data:
                b[k] = brain.data[k][0]
            #b.update(brain.data)
            shelf.append(b)
    
        return shelf
    
    def search(self, s, page=0, **kw):
        conn = self.pool.get_connection()
        q = conn.query_parse(s) #conn.spell_correct(s))
        brains = conn.search(q, page*self.n, page*self.n+self.n)
        results = [ dict(
                        id=x.id.replace('public','books'),
                        title=decode(x.data['title'][0]),
                        summary=decode(x.summarise('searchable_text', maxlen=240))
                        ) for x in brains ]
        
        return brains.matches_estimated, results 


def register_catalog(db):
    cat = CatalogSearch(db) 
    gsm = getSiteManager()
    gsm.registerUtility(cat)
    return cat