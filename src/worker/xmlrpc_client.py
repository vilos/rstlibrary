#!/usr/bin/env python -u

# An event listener that sends some data as RemoteCommand to supervisord 

import os, sys
from supervisor import childutils

conf = dict(SUPERVISOR_SERVER_URL='http://127.0.0.1:9001')

flip = False

def main():
    rpcinterface = childutils.getRPCInterface(conf)
    while 1:
        headers, payload = childutils.listener.wait()
        if headers['eventname'].startswith('TICK'):
            global flip
            if flip:
                cmd = 'update' 
                args = '0011'
            else:
                cmd = 'invalidate'
                args = '0013'
            flip = not flip
            print >>sys.stderr, childutils.get_asctime(), ':', cmd, args
                
            rpcinterface.supervisor.sendRemoteCommEvent(cmd, args + '\n')
        
        childutils.listener.ok()

if __name__ == '__main__':
    main()