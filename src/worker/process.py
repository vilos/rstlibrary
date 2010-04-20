import xmlrpclib
#from indexer import index 
from updater import update
from jsonrpc import invalidate
import logging

log = logging.getLogger()

def run():
    url = 'http://localhost:9001'
    s = xmlrpclib.ServerProxy(url)

    while 1:
        try:
            response = s.broker.get()
        except Exception, e:
            log.exception('Problem connecting to %s: %s', url, e)
            break
        
        if not response:
            print log.info('Nothing to do.')
            break
        
        cmd, arg = response
        log.info('Received: %s %s', cmd, arg)
        
        if not arg:
            log.error('Missing argument for command %s.', cmd)
        
#        if cmd == 'index':
#            index(arg)
        
        elif cmd == 'update':
            update(arg)
            
        elif cmd == 'invalidate':
            invalidate(arg)
            
            
if __name__=='__main__':
    run()