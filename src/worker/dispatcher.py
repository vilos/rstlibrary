#!/usr/bin/env python

# An event listener that listens for process communications events
# from loop_eventgen.py and uses RPC to write data to the event
# generator's stdin.

import sys,os
from supervisor import childutils

import jsonrpc
from svnup import update
from invalidate import invalidate
from catalog import index
import socket

conf = dict(SUPERVISOR_SERVER_URL='http://127.0.0.1:9001')
broker_url = 'http://127.0.0.1:7007/get'

from sensible.loginit import logger
log = logger(os.path.basename(__file__))

class Dispatcher(object):
    
    def __init__(self, rpc):
        self.rpc = rpc
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        
    def run(self):
        cmd = None
        while not cmd:
            # we explicitly use self.stdin, self.stdout, and self.stderr
            # instead of sys.* so we can unit test this code
            headers, payload = childutils.listener.wait(self.stdin, self.stdout)
            
            if not headers['eventname'].startswith('TICK'):
                # do nothing with non-TICK events
                childutils.listener.ok(self.stdout)
                continue
                
            broker = jsonrpc.Client(broker_url)
            cmd = ''
            
            try:
                msg = broker.send()
                cmd, arg = msg.split(':')
            except socket.error:
                pass
            except Exception, e:
                log.exception(str(e))
                raise
            
            if cmd:
                cmd_name = 'do_%s' % cmd
                m = getattr(self, cmd_name, None)
                if m:
                    try:
                        msg = m(arg)
                    except Exception, e:
                        log.exception(str(e))
                    else:
                        log.info(msg)
                else:
                    log.error('unknown command: %s:%s' % (cmd, arg))
                    
            childutils.listener.ok(self.stdout)
            
    def do_update(self, arg, ini='production'):
        return '\n\t'.join(['', update(arg, ini), index(arg, ini), invalidate(arg, ini)])
        
    def do_invalidate(self, arg):
        return invalidate(arg)
        
    def do_index(self, arg):
        return index(arg)
        
        
def main():
    
    rpc = childutils.getRPCInterface(conf)
    prog = Dispatcher(rpc)
    prog.run()


if __name__ == '__main__':
    main()
