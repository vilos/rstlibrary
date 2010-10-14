import os
import xappy
import books

#os.environ["LOGGING_DEBUG"] =  "1"
#from sensible.loginit import logger
#log = logger(__name__)

config = books.configure()
index_path = config.get('database')


class X(object):
    def __init__(self, index_path=index_path):
        self.index_path = index_path
        
    def clear(self):
        conn = xappy.IndexerConnection(self.index_path)
        try:
            for id in conn.iterids():
                #print id
                conn.delete(id)
        finally:
            conn.flush()
            conn.close()
        
if __name__ == '__main__':
    x = X()
    x.clear()