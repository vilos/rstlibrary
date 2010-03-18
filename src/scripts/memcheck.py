import psutil

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

    
def check(rsslimit=900*1024*1024):
    # sum rss of given processes
    rss = 0
    ps = get_ps(name='uwsgi', username='vslib')
    for p in ps:
        rss += int(p.get_memory_info()[0])
        
    if rss > rsslimit:
        print '%dMB' % mb(rss)
        # find the parent one
        for p in ps:
            pp = p.parent
            if pp and pp.name == p.name:
                # kill the parent
                pp.kill(HUP)
                print 'process %s restarted' % pp.pid
                return
    print 'OK - %dMB' % mb(rss)
                 
def info():
    ps = get_ps(name='uwsgi', username='vslib')
    print "PID,\tPPID,\tCPU,\tRSS - \tVMS"
    for p in ps:
        rss, vms = p.get_memory_info()
        print "%s\t%s\t%s%%\t%s - \t%s" % (p.pid, p.ppid, p.get_cpu_percent(), mb(rss), mb(vms)) 
    
if __name__=='__main__':
    info()
    check()
