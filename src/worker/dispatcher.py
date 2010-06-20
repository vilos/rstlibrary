#!/usr/bin/env python -u

# An event listener that listens for process communications events
# from loop_eventgen.py and uses RPC to write data to the event
# generator's stdin.

import sys
from time import sleep
from supervisor import childutils

from updater import update
from jsonrpc import invalidate
from log import log

conf = dict(SUPERVISOR_SERVER_URL='http://127.0.0.1:9001')

    
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
                msg = ''
                log("%s cmd: %s, args: %s", childutils.get_asctime(), cmd, args)
                try:
                    if cmd == 'update':
                        msg = update(args)
                        
                    elif cmd == 'invalidate':
                        msg = invalidate(args)
                
                    else:
                        log("unknown command: %s %s", cmd, args)
                except:
                    log(sys.exc_info()[0])
                    if err > 7:
                        sys.exit(1)
                    err += 1 
                    sleep(3)
                if msg:
                    log(msg)
                    
        childutils.listener.ok()

if __name__ == '__main__':
    main()
