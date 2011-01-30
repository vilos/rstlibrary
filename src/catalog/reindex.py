import sys, os
import signal

from indexer import index_books
from conf import configure

keep_processing = True

os.environ["LOGGING_DEBUG"] =  "1"
from sensible.loginit import logger
log = logger(os.path.basename(__file__))


def main(path):
    index_path = configure()
    ids = [n for n in os.listdir(path) if not n.startswith('.')]
    ids.sort()
    
    #for id in ids:
    msg = index_books(index_path, ids)
    log.info(msg)
    #if not keep_processing:
    #    break
    
if __name__=='__main__':
    if len(sys.argv)>1:
        main(sys.argv[1])
    else:
        print "Usage: %s repo_path " % sys.argv[0]