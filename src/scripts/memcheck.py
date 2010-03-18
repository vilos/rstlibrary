import psutil

HUP = 1

def get_ps(name, username=''):
    
    for p in psutil.process_iter():
        if p.name != name:
            continue
        if username and p.username != username:
            continue
        yield p

    
def check(rsslimit=900*1024*1024):
    # sum rss of given processes
    rss = 0
    ps = get_ps(name='uwsgi', username='vslib')
    for p in ps:
        rss += p.get_memory_info()[0]
        
    if rss > rsslimit:
        # find the parent one
        for p in ps:
            pp = p.parent
            if pp and pp.name == p.name:
                # kill the parent
                pp.kill(HUP)
                print 'process %s restarted' % pp.id
                return
    print 'OK - %sMB' % rss/(1024*1024)
                 
def info():
    ps = get_ps(name='uwsgi', username='vslib')
    print "PID,\tPPID,\tCPU,\tMEM"
    for p in ps:
        rss, vms = p.get_memory_info()
        print "%s\t%s\t%s%%\t%s - %s" % (p.pid, p.ppid, p.get_cpu_percent(), rss, vms) 
    
if __name__=='__main__':
    info()
    check()