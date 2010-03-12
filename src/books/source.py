'''
Storage for book sources 
mostly taken from shove
'''
import os, urllib
from zope.interface import implements
from zope.component import getSiteManager
from store import BaseStore
from interfaces import ISource
        
        
class SourceStore(BaseStore):
    """ stores source text in the file structure  ${bookid}/${bookid}.txt """

    implements(ISource)
    
    def __init__(self, basepath, **kw):
        super(SourceStore, self).__init__(basepath, **kw)
                
        if basepath.startswith('file://'):
            basepath = urllib.url2pathname(basepath.split(':/')[1])
        self._dir = os.path.realpath(os.path.abspath(basepath))
        # Create directory
        if not os.path.exists(self._dir): self._createdir()

    def __getitem__(self, key):
        # (per Larry Meyn)
        try:
            item = open(self._key_to_file(key), 'rb')
            data = item.read()
            item.close()
            return self.loads(data)
        except Exception:
            raise KeyError('%s' % key)

    def __setitem__(self, key, value):
        # (per Larry Meyn)
        try:
            parent = self._parent(key)
            if not os.path.exists(parent):
                os.makedirs(parent, 0755)
            item = open(self._key_to_file(key), 'wb')
            item.write(self.dumps(value))
            item.close()
        except (IOError, OSError):
            raise KeyError('%s' % key)

    def __delitem__(self, key):
        try:
            os.remove(self._key_to_file(key))
            p = self._parent(key)
            if os.path.exists(p):
                os.rmdir(p)
        except (IOError, OSError):
            raise KeyError('%s' % key)

    def __contains__(self, key):
        return os.path.exists(self._key_to_file(key))

    def __len__(self):
        return len(os.listdir(self._dir))

    def _createdir(self):
        '''Creates the store directory.'''
        try:
            os.makedirs(self._dir, 0755)
        except OSError:
            raise EnvironmentError('Directory "%s" does not exist and ' \
                'could not be created' % self._dir)

    def _parent(self, key):
        return os.path.join(self._dir, urllib.quote_plus(key))
    
    def _key_to_file(self, key):
        '''Gives the filesystem path for a key.'''
        
        return os.path.join(self._parent(key), urllib.quote_plus(key) + '.txt')

    def keys(self):
        '''Returns a list of keys in the store.'''
        return list(urllib.unquote_plus(name) for name in os.listdir(self._dir) if not name.startswith('.'))
    
    #def __repr__(self):
    #    return repr(super(SourceStore, self))
        #return "<Source @%s: %s>" % (self._dir, repr(dict(self.iteritems())))

def register_source(path, **kw):
    store = SourceStore(path, **kw) 
    gsm = getSiteManager()
    gsm.registerUtility(store)
    return store

def unregister_source(store, **kw):
    gsm = getSiteManager()
    gsm.unregisterUtility(store)
    
