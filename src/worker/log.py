import sys

def log(msg, *args):
    if args:
        out = msg % args
    else:
        out = msg
    print >>sys.stderr, out