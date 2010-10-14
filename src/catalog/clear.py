import xappy
from conf import configure


def clear(index_path=None):
    if not index_path:
        index_path = configure()
    print 'Index at:', index_path
    conn = xappy.IndexerConnection(index_path)
    try:
        for id in conn.iterids():
            #print id
            conn.delete(id)
    finally:
        conn.flush()
        conn.close()
            
    
if __name__ == '__main__':
    clear()