import os, sys
import pysvn
from log import log

class SvnCommand(object):
    
    def __init__(self, path):
        self.client = pysvn.Client()
        self.path = path
        self.client.callback_get_login = self.callback_getLogin
        self.client.callback_notify = self.callback_notify
        self.client.callback_cancel = self.callback_cancel
    
    def extend_path(self, path):
        if path:
            self.path = os.path.join(self.path, path)
            
        if not os.path.exists(self.path):
            raise ValueError('Path %s does not exist.' % self.path )
        
    def up(self, el=''):
        self.extend_path(el)
        self.client.update(self.path)
        
    def status(self, el=''):
        self.extend_path(el)
        all_files = self.client.status(self.path, recurse=True, get_all=False, update=True)
        for file in all_files:
            log( 'Status: %s %s %s - %s' % (file.text_status, file.prop_status, file.repos_text_status, file.path))
        return all_files
    
    st = status
    def callback_notify(self, arg_dict):
        msg = '%s %s' % ( arg_dict['action'], arg_dict['path'])
        if arg_dict['action'] == pysvn.wc_notify_action.update_completed:
            msg += " revision: %s" % arg_dict['revision']
        msg += "\n"
        log(msg)
        
    def callback_getLogin(self, realm, username, may_save):
        log('Login required')
        
        username = password = ''
        return 1, username, password, False
    
    def callback_cancel(self):
        return False


def update(bookid, base='var/vslib'):
    
    svn = SvnCommand(base)
    svn.up(bookid)

if __name__=='__main__':
    arg = ''
    argc = len(sys.argv)
    if (argc > 2):
        
        cmd = sys.argv[1]
        path = sys.argv[2]
        
        svn = SvnCommand(path)
        getattr(svn, cmd)()
        
    else:
        log("Usage: %s cmd path " % sys.argv[0])
    
