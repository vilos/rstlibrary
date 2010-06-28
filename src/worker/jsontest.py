from log import log
from jsonrpc import Client

host = "http://localhost:6543/"

def send(adr, **kw): 

    url = host + adr
    client = Client(url)
    log("jsonreq: %s", url)
    msg = client.send(kw)
    return msg
    
    
if __name__=='__main__':
    
    data = dict(cmd='update', arg='0000')
    #print send('put', **data)
    print send('get')