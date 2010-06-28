import sys
from log import log
from jsonrpc import Client
         
def invalidate(bookid, url='http://www.srichinmoylibrary.com/invalidate'):
    data = dict(bookid=bookid)
    
    log("jsonrpc - sending: %r", data)
    client = Client(url)
    return client.send(data)
    
if __name__ == '__main__':
    url = ''
    if len(sys.argv) > 2:
        url, bookid = sys.argv[1:]
        
    elif len(sys.argv) > 1:
        bookid = sys.argv[1]
        
    if bookid:
        if url:
            print invalidate(bookid, url)
        else:
            print invalidate(bookid)
    else:
        print 'bookid ?'
