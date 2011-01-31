""" send books changed in svn repo but not updated in live wc """
import sys, os
import signal

from indexer import index_all
from conf import configure
from info import indexed

keep_processing = True

os.environ["LOGGING_DEBUG"] =  "1"
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
        
        index_path = configure()
        
        path = sys.argv[1]
        
        ids = [n for n in os.listdir(path) if not n.startswith('.')]
        
        indexed = [a.id for a in indexed(index_path)]
        
        ids = list(set(ids) - set(indexed))
        ids.sort()
        
        for id in ids:
            #print 'Sending: put', id
            #send('put', cmd='index', arg=id)
            msg = index_all(id, index_path)
            log.info(msg)
            if not keep_processing:
                break
    else:
        print "Usage: %s repo_path " % sys.argv[0]