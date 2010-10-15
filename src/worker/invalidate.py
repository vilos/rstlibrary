import sys
from sensible.loginit import logger
from jsonrpc import Client
from library import configure

log = logger(__name__)

def invalidate(bookid, ini='develop'):
    config = configure(ini)
    url = config.get('invalidate_url')
    data = dict(bookid=bookid)
    log.debug("sending invalidating request: %r to %s", data, url)
    client = Client(url)
    return client.send(data)
    
if __name__ == '__main__':
    bookid = ''
    if len(sys.argv) > 1:
        bookid = sys.argv[1]
        
    if bookid:
        print invalidate(bookid)
    else:
        print 'bookid ?'
