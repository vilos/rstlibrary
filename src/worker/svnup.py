import os, sys
import pysvn


class SvnCommand(object):
    
    def __init__(self, path):
        self.client = pysvn.Client()
        self.path = path
        self.client.callback_get_login = self.callback_getLogin
        self.client.callback_notify = self.callback_notify
        self.client.callback_cancel = self.callback_cancel
    
    def up(self, el):
        path = os.path.join(self.path, el)
        self.client.update(path)
        
    def status(self, el=''):
        path = os.path.join(self.path, el)
        all_files = self.client.status(path, recurse=True, get_all=False, update=True)
        for file in all_files:
            print( '%s%s  %s' % (file.text_status, file.prop_status, file.path))
    st = status
    def callback_notify(self, arg_dict):
        msg = '%s %s' % ( arg_dict['action'], arg_dict['path'])
        if arg_dict['action'] == pysvn.wc_notify_action.update_completed:
            msg += " revision: %s" % arg_dict['revision']
        msg += "\n"
        sys.stderr.write(msg)
        
    def callback_getLogin(self, realm, username, may_save):
        sys.stderr.write('Login required')
        
        username = password = ''
        return 1, username, password, False
    
    def callback_cancel(self):
        return False

base='var/vslib'

def update(bookid):
    
    svn = SvnCommand(base)
    svn.up(bookid)

if __name__=='__main__':
    arg = ''
    argc = len(sys.argv)
    if (argc > 2):
        arg = sys.argv[2]
    if (argc > 1):
        cmd = sys.argv[1]
        
        svn = SvnCommand(base)
        m = getattr(svn, cmd)
        
        m(arg)
        
        
    else:
        print "Usage: %s cmd [arg] " % sys.argv[0]
    
