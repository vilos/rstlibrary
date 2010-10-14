import os, sys
import xappy
import books

os.environ["LOGGING_DEBUG"] =  "1"
from sensible.loginit import logger

log = logger(__name__)


config = books.configure()
index_path = config.get('database')


class X(object):
    def __init__(self, index_path=index_path):
        self.connection = xappy.SearchConnection(index_path)
        
    def indexed(self):
        conn = self.connection
        q = conn.query_field('type', 'Book')
        return conn.search(q, 0, 10000)
        #return [x.id[-4:] for x in conn.search(q, 0, 10000)]
    
    def info(self):
        indexed = self.indexed()
        print "Number of indexed books: %d" % len(indexed)
        print '[',
        for obj in indexed:
            print obj.id
        print ']'
        #print repr(self.indexed)
        print 'Number of all indexed documents: %s' % self.connection.get_doccount()
        
    def list(self):
        q = self.connection.query_all()
        for doc in self.connection.search(q, 0, 1000):
            print doc.id
        
    def inspect(self, id):
        conn = self.connection
        doc = conn.get_document(id)
        print doc.data
        
if __name__ == '__main__':
    
    x = X()
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        m = getattr(x, arg, None) 
        if m and callable(m):
            m()
        else:
            x.inspect(arg)
    else:
        x.info()