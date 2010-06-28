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
    
def update(bookid, path='./books'):
    
    svn = SvnCommand(path)
    svn.up(bookid)

if __name__=='__main__':
    update(sys.argv[1])