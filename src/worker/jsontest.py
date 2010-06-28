import sys
from log import log
from jsonrpc import Client

host = "http://localhost:7007/"

def send(adr, **kw): 

    url = host + adr
    client = Client(url)
    log("jsonreq: %s", url)
    msg = client.send(kw)
    return msg
    
    
if __name__=='__main__':

    data = {}
    if len(sys.argv) > 2:
        msg = sys.argv[2]
        cmd, arg = msg.split(':') 
        data = dict(cmd=cmd, arg=arg)
    if len(sys.argv) > 1:
        jcmd = sys.argv[1]
        print send(jcmd, **data)
    else:
        print "Usage: %s cmd msg   /  cmd=(put/get) msg=cmd:arg" % sys.argv[0]
