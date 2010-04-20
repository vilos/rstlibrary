#!/usr/bin/env python -u

# An event listener that listens for process communications events
# from loop_eventgen.py and uses RPC to write data to the event
# generator's stdin.

import os, sys
from time import sleep
from supervisor import childutils

from updater import update
from jsonrpc import invalidate

conf = dict(SUPERVISOR_SERVER_URL='http://127.0.0.1:9001')

def log(msg, *args):
    if args:
        out = msg % args
    else:
        out = msg
    print >>sys.stderr, out
    
def main():
    #rpcinterface = childutils.getRPCInterface(conf)
    err = 0
    while 1:
        headers, payload = childutils.listener.wait()
        if headers['eventname'].startswith('REMOTE_COMMUNICATION'):
        
            if payload:
                pheaders, pdata = childutils.eventdata(payload)
                cmd = pheaders['type']
                args = pdata.strip()
                
                log("%s cmd: %s, args: %s", childutils.get_asctime(), cmd, args)
                try:
                    if cmd == 'update':
                        update(args)
                        
                    elif cmd == 'invalidate':
                        invalidate(args)
                
                    else:
                        log("unknown command: %s %s", cmd, args)
                except:
                    log(sys.exc_info()[0])
                    if err > 7:
                        sys.exit(1)
                    err += 1 
                    sleep(3)
                    
        childutils.listener.ok()

if __name__ == '__main__':
    main()
