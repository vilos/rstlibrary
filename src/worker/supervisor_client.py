#!/usr/bin/env python -u

# An event listener that sends some data as RemoteCommand to supervisord 

import sys
from supervisor import childutils

conf = dict(SUPERVISOR_SERVER_URL='http://127.0.0.1:9001')


def main(cmd, arg):
    rpcinterface = childutils.getRPCInterface(conf)
    while 1:
        headers, payload = childutils.listener.wait()
        if headers['eventname'].startswith('TICK'):

            print >>sys.stderr, childutils.get_asctime(), ':', cmd, arg
                
            rpcinterface.supervisor.sendRemoteCommEvent(cmd, arg + '\n')
        
        childutils.listener.ok()

if __name__ == '__main__':
    n = len(sys.argv[1:])
    if n <> 2:
        sys.exit('usage: python %s cmd arg' % sys.argv[0])
    else:
        main(sys.argv[1], sys.argv[2])
