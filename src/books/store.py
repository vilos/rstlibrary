'''
store for pickled data 
'''
import os, urllib, cPickle as pickle, zlib
from zope.component import getSiteManager
from zope.interface import implements
from interfaces import IStore

stores = dict(
    file=':FileStore',
)
# Static cache backend registry
caches = dict(
    memlru='books.cache:MemoryLRUCache',
)

def getbackend(uri, engines, **kw):
    '''Loads the right backend based on a URI.

    @param uri Instance or name string
    @param engines A dictionary of scheme/class pairs
    @param kw Keywords'''
    if isinstance(uri, basestring):
        mod = engines[uri.split('://', 1)[0]]
        # Load module if setuptools not present
        if isinstance(mod, basestring):
            # Isolate classname from dot path
            module, klass = mod.split(':')
            # Load module
            if not module:
                module =  getbackend.__module__
            mod = getattr(__import__(module, '', '', ['']), klass)

        # Load appropriate class from setuptools entry point
        else:
            mod = mod.load()
        # Return instance
        return mod(uri, **kw)
    # No-op for existing instances
    return uri

class Base(object):

    '''Base Mapping class.'''

    def __init__(self, engine, **kw):
        self._binary = kw.get('binary', False)
        self._encoding = kw.get('encoding', 'utf_8_sig')
        self._compress = kw.get('compress', False)

    def __getitem__(self, key):
        raise NotImplementedError()

    def __setitem__(self, key, value):
        raise NotImplementedError()

    def __delitem__(self, key):
        raise NotImplementedError()

    def __contains__(self, key):
        try:
            value = self[key]
        except KeyError:
            return False
        return True

    def get(self, key, default=None):
        '''Fetch a given key from the mapping. If the key does not exist,
        return the default.

        @param key Keyword of item in mapping.
        @param default Default value (default: None)
        '''
        try:
            return self[key]
        except KeyError:
            return default

    def dumps(self, value):
        '''Optionally serializes and compresses an object.'''
        
        if self._binary:
            # Serialize everything but ASCII strings        
            value = pickle.dumps(value)
            # Apply maximum compression
            if self._compress: value = zlib.compress(value, 9)
        else:
            if isinstance(value, unicode):
                value = value.encode(self._encoding)
            else: 
                value = str(value)
        return value

    def loads(self, value):
        '''Deserializes and optionally decompresses an object.'''
        
        if self._binary:
            if self._compress:
                try:
                    value = zlib.decompress(value)
                except zlib.error: pass                 # pragma: no cover
            value = pickle.loads(value)
        else:
            if not isinstance(value, unicode):
                value = value.decode(self._encoding)
        return value
        
class BaseStore(Base):

    '''Base Store class (based on UserDict.DictMixin).'''

    def __init__(self, engine, **kw):
        super(BaseStore, self).__init__(engine, **kw)

    def __cmp__(self, other):
        if other is None: return False
        if isinstance(other, BaseStore):
            return cmp(dict(self.iteritems()), dict(other.iteritems()))

    def __iter__(self):
        for k in self.keys(): yield k                   

    def __len__(self):
        return len(self.keys())

    def __repr__(self):
        return repr(dict(self.iteritems()))

    def clear(self):
        '''Removes all keys and values from a store.'''
        for key in self.keys(): del self[key]

    def items(self):
        '''Returns a list with all key/value pairs in the store.'''
        return list(self.iteritems())

    def iteritems(self):
        '''Lazily returns all key/value pairs in a store.'''
        for k in self: yield (k, self[k])

    def iterkeys(self):
        '''Lazy returns all keys in a store.'''
        return self.__iter__()

    def itervalues(self):
        '''Lazily returns all values in a store.'''
        for _, v in self.iteritems(): yield v

    def keys(self):                                         # pragma: no cover
        '''Returns a list with all keys in a store.'''
        raise NotImplementedError()

    def pop(self, key, *args):
        '''Removes and returns a value from a store.

        @param args Default to return if key not present.'''
        if len(args) > 1:
            raise TypeError('pop expected at most 2 arguments, got '\
                + repr(1 + len(args)))
        try:
            value = self[key]
        # Return default if key not in store
        except KeyError:
            if args: return args[0]
        del self[key]
        return value

    def popitem(self):
        '''Removes and returns a key, value pair from a store.'''
        try:
            k, v = self.iteritems().next()
        except StopIteration:
            raise KeyError('Store is empty.')
        del self[k]
        return (k, v)

    def setdefault(self, key, default=None):
        '''Returns the value corresponding to an existing key or sets the
        to key to the default and returns the default.

        @param default Default value (default: None)
        '''
        try:
            return self[key]
        except KeyError:
            self[key] = default
        return default

    def update(self, other=None, **kw):
        '''Adds to or overwrites the values in this store with values from
        another store.

        other Another store
        kw Additional keys and values to store
        '''
        if other is None: pass
        elif hasattr(other, 'iteritems'):
            for k, v in other.iteritems(): self[k] = v
        elif hasattr(other, 'keys'):
            for k in other.keys(): self[k] = other[k]
        else:
            for k, v in other: self[k] = v
        if kw: self.update(kw)

    def values(self):
        '''Returns a list with all values in a store.'''
        return list(v for _, v in self.iteritems())
                
class FileStore(Base):

    '''Base class for file based storage.'''

    def __init__(self, engine, **kw):
        kw.update(dict(binary=True))
        super(FileStore, self).__init__(engine, **kw)
        if engine.startswith('file://'):
            engine = urllib.url2pathname(engine.split(':/')[1])
        self._dir = os.path.normpath(os.path.realpath(os.path.abspath(engine)))
        # Create directory
        if not os.path.exists(self._dir): self._createdir()

    def __getitem__(self, key):
        # (per Larry Meyn)
        try:
            item = open(self._key_to_file(key), 'rb')
            data = item.read()
            item.close()
            return self.loads(data)
        except:
            raise KeyError('%s' % key)

    def __setitem__(self, key, value):
        # (per Larry Meyn)
        try:
            item = open(self._key_to_file(key), 'wb')
            item.write(self.dumps(value))
            item.close()
        except (IOError, OSError):
            raise KeyError('%s' % key)

    def __delitem__(self, key):
        try:
            os.remove(self._key_to_file(key))
        except (IOError, OSError):
            raise KeyError('%s' % key)

    def __contains__(self, key):
        return os.path.exists(self._key_to_file(key))

    def __len__(self):
        return len(os.listdir(self._dir))

    def _createdir(self):
        '''Creates the store directory.'''
        try:
            os.makedirs(self._dir)
        except OSError:
            raise EnvironmentError('Cache directory "%s" does not exist and ' \
                'could not be created' % self._dir)

    def _key_to_file(self, key):
        '''Gives the filesystem path for a key.'''
        return os.path.join(self._dir, urllib.quote_plus(key))

    def keys(self):
        '''Returns a list of keys in the store.'''
        return list(urllib.unquote_plus(name) for name in os.listdir(self._dir))
    
class Store(BaseStore):

    '''Common object frontend class.'''
    
    implements(IStore)

    def __init__(self, store='simple://', cache='simple://', **kw):
        super(Store, self).__init__(store, **kw)
        
        # Load store
        self._store = getbackend(store, stores, **kw)
        # Load cache
        self._cache = getbackend(cache, caches, **kw)
        # Buffer for lazy writing and setting for syncing frequency
        self._buffer, self._sync = dict(), kw.get('sync', 1)

    def __getitem__(self, key):
        '''Gets a item from shove.'''
        try:
            return self._cache[key]
        except KeyError:
            # Synchronize cache and store
            self.sync()
            value = self._store[key]
            self._cache[key] = value
            return value

    def __setitem__(self, key, value):
        '''Sets an item in shove.'''
        self._cache[key] = self._buffer[key] = value
        # When the buffer reaches self._limit, writes the buffer to the store
        if len(self._buffer) >= self._sync: 
            self.sync()

    def __delitem__(self, key):
        '''Deletes an item from shove.'''
        
        self.sync()
        del self._store[key]
        try:
            del self._cache[key]
        except KeyError: pass


    def keys(self):
        '''Returns a list of keys in shove.'''
        self.sync()
        return self._store.keys()

    def sync(self):
        '''Writes buffer to store.'''
        for k, v in self._buffer.iteritems(): 
            self._store[k] = v
        self._buffer.clear()

    def close(self):
        '''Finalizes and closes shove.'''
        # If close has been called, pass
        if self._store is not None:
            self.sync()
            try:
                self._store.close()
            except AttributeError:
                pass
            self._store = self._cache = self._buffer = None


def register_store(store_url, cache_url, **kw):
    store = Store(store_url, cache_url, **kw)
    #alsoProvides(store, IStore) 
    sm = getSiteManager()
    sm.registerUtility(store)
    return store

def unregister_store(store, **kw):
    gsm = getSiteManager()
    gsm.unregisterUtility(store)
    