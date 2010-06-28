import sys, os
from svnup import SvnCommand
from jsontest import send

def getid(path):
    base = os.path.basename(path)
    name, ext = os.path.splitext(base)
    if ext and ext == '.txt':
        return name
    return None
    
    
if __name__=='__main__':
    arg = ''
    argc = len(sys.argv)
    if (argc > 1):
        
        path = sys.argv[1]
        
        svn = SvnCommand(path)
        files = svn.st()
        outdated = [ f.path for f in files if str(f.repos_text_status) == 'modified']
        
        ids = [getid(p) for p in outdated]
        
        for id in ids:
            send('put', 'update:%s' % id)
            send('put', 'invalidate:%s' % id)
            
    else:
        print "Usage: %s repo_path " % sys.argv[0]