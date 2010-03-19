import sys, psutil
from datetime import datetime

HUP = 1

def mb(size):
    return size/(1024*1024)

def get_ps(name, username=''):
    
    ps = []
    for p in psutil.process_iter():
        if p.name != name:
            continue
        if username and p.username != username:
            continue
        ps.append(p)
    return ps

    
def check(rsslimit):
    # sum rss of given processes
    rss = 0
    ps = get_ps(name='uwsgi', username='vslib')
    for p in ps:
        rss += int(p.get_memory_info()[0])
    
    dt = datetime.now()
    print dt.strftime("%d. %B %Y %H:%M:%S"),
    
    if rss > rsslimit*1024*1024:
        print '- %dMB' % mb(rss),
        # find the parent one
        for p in ps:
            pp = p.parent
            if pp and pp.name == p.name:
                # kill the parent
                pp.kill(HUP)
                print 'process %s restarted' % pp.pid
                return
    print '- %dMB, OK' % mb(rss)
                 
def info():
    ps = get_ps(name='uwsgi', username='vslib')
    print "PID,\tPPID,\tCPU,\tRSS - \tVMS"
    total = 0
    for p in ps:
        rss, vms = p.get_memory_info()
        total += rss 
        print "%s\t%s\t%0.2f%%\t%s - \t%s" % (p.pid, p.ppid, p.get_cpu_percent(), mb(rss), mb(vms)) 
    print 'total watched RSS: %d' % mb(total)
    used, all, avail = mb(psutil.used_phymem()), mb(psutil.TOTAL_PHYMEM), mb(psutil.avail_phymem())
    print 'Used memory %dMB out of %dMB' %  (used, all)
    print 'Available memory %dMB' % avail

    
if __name__=='__main__':
    info()
    if len(sys.argv)>1:
        limit = int(sys.argv[1])
        check(limit)
