import os, sys
import pysvn

from sensible.loginit import logger

log = logger(__name__)

class SvnCommand(object):
    
    def __init__(self, path):
        self.client = pysvn.Client()
        self.path = path
        self.revision_update_complete = None
        self.client.callback_get_login = self.callback_getLogin
        self.client.callback_notify = self.callback_notify
        self.client.callback_cancel = self.callback_cancel
    
    def extend_path(self, path):
        if path:
            self.path = os.path.join(self.path, path)
            
    def get_url(self):
        path = self.path 
        if not os.path.exists(path):
            path = os.path.dirname(path)
            
        entries = self.client.info2(path, revision='head', recurse=False)
        p, info = entries[0]
        return info.URL
            
    def up(self, path=''):
        self.extend_path(path)
        if not os.path.exists(self.path):
            self.path = os.path.dirname(self.path)
            if not os.path.exists(self.path):
                raise ValueError('Path %s does not exist.' % self.path )

        self.revision_update_complete = None
        self.client.update(self.path)

        if self.revision_update_complete is not None:
            log.info('Checked out revision %s' % self.revision_update_complete.number)
        else:
            log.warning('Checked out unknown revision - checkout failed?')
        
    def checkout(self, path=''):
        self.extend_path(path)
        url = '/'.join([self.get_url(), path]) 
        
        self.revision_update_complete = None
        self.client.checkout(url, path, recurse=True)
        
        if self.revision_update_complete is not None:
            log.info('Checked out revision %s' % self.revision_update_complete.number)
        else:
            log.warning('Checked out unknown revision - checkout failed?')
            
    def status(self, el=''):
        self.extend_path(el)
        all_files = self.client.status(self.path, recurse=True, get_all=False, update=True)
        for file in all_files:
            log.info('Status: %s %s %s - %s' % (file.text_status, file.prop_status, file.repos_text_status, file.path))
        return all_files
    
    st = status
    
    def callback_notify(self, arg_dict):
        #msg = '%s %s' % ( arg_dict['action'], arg_dict['path'])
        #if arg_dict['action'] == pysvn.wc_notify_action.update_completed:
        #    msg += " revision: %s" % arg_dict['revision']
        #msg += "\n"
        #log(msg)
     
        if arg_dict['action'] == pysvn.wc_notify_action.update_completed:
            self.revision_update_complete = arg_dict['revision']
        elif arg_dict['path'] != '' and arg_dict['action']  is not None:
            msg = '%s %s\n' % ( arg_dict['action'], arg_dict['path'])
            log.info(msg)
                
    def callback_getLogin(self, realm, username, may_save):
        log.error('Login required')
        
        username = password = ''
        return 1, username, password, False
    
    def callback_cancel(self):
        return False


def update(bookid, base='var/vslib'):
    
    svn = SvnCommand(base)
    try:
        svn.up(bookid)
    except ValueError:
        svn.checkout(bookid)
        
    return ""

if __name__=='__main__':
    arg = ''
    argc = len(sys.argv)
    if (argc > 2):
        
        cmd = sys.argv[1]
        path = sys.argv[2]
        
        svn = SvnCommand(path)
        getattr(svn, cmd)()
        
    else:
        log.info("Usage: %s cmd path " % sys.argv[0])
    
