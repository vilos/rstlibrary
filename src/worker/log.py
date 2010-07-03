import sys, datetime

def log(msg, *args):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")   
    if args:
        out = msg % args
    else:
        out = msg
    print >>sys.stderr, "#%s - %s" % (now, out)