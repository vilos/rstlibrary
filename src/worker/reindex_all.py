""" send books changed in svn repo but not updated in live wc """
import sys, os
import signal
#from svnup import SvnCommand
#from jsontest import send
from indexer import index

keep_processing = True

from sensible.loginit import logger
log = logger(os.path.basename(__file__))

# KeyboardInterrupt handler
def interrupt(signl, frme):
    global keep_processing
    keep_processing = False
    log.info('Catched signal %r. Processing will stop.', signl)
    return 0

signal.signal(signal.SIGINT, interrupt )

def getid(path):
    base = os.path.basename(path)
    name, ext = os.path.splitext(base)
    if ext and ext == '.txt':
        return name
    return None
    
    
if __name__=='__main__':
    arg = ''
    argc = len(sys.argv)
    if (argc > 1):
        
        path = sys.argv[1]
        
        ids = [n for n in os.listdir(path) if not n.startswith('.')]
        ids.sort()
        
#        svn = SvnCommand(path)
#        files = svn.st()
#        files = [f.path for f in svn.st()] # if str(f.repos_text_status) == 'modified']
#        
#        ids = [getid(p) for p in files]
#        ids.sort()
        
        for id in ids:
            #print 'Sending: put', id
            #send('put', cmd='index', arg=id)
            index(id)
            if not keep_processing:
                break
    else:
        print "Usage: %s repo_path " % sys.argv[0]