'''
'''
#import copy
from collections import deque
import threading
from store import Base

        
def synchronized(func):
    '''Decorator to lock and unlock a method (Phillip J. Eby).

    @param func Method to decorate
    '''
    def wrapper(self, *__args, **__kw):
        self._lock.acquire()
        try:
            return func(self, *__args, **__kw)
        finally:
            self._lock.release()
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    return wrapper

class SimpleBase(Base):

    '''Single-process in-memory store base class.'''

    def __init__(self, engine, **kw):
        super(SimpleBase, self).__init__(engine, **kw)
        self._store = dict()

    def __getitem__(self, key):
        try:
            return self._store[key]
        except:
            raise KeyError('%s' % key)

    def __setitem__(self, key, value):
        self._store[key] = value

    def __delitem__(self, key):
        try:
            del self._store[key]
        except:
            raise KeyError('%s' % key)

    def __len__(self):
        return len(self._store)

    def keys(self):
        '''Returns a list of keys in the store.'''
        return self._store.keys()
    
class LRUBase(SimpleBase):
    
    def __init__(self, engine, **kw):
        super(LRUBase, self).__init__(engine, **kw)
        self._max_entries = kw.get('max_entries', 30)
        self._hits = 0
        self._misses = 0
        self._queue = deque()
        self._refcount = dict()

    def __getitem__(self, key):
        try:
            value = super(LRUBase, self).__getitem__(key)
            self._hits += 1
        except KeyError:
            self._misses +=1
            raise
        self._housekeep(key)
        return value
            
    def __setitem__(self, key, value):
        super(LRUBase, self).__setitem__(key, value)
        self._housekeep(key)
        if len(self._store) > self._max_entries:
            while len(self._store) > self._max_entries:
                k = self._queue.popleft()
                self._refcount[k] -= 1
                if not self._refcount[k]:
                    super(LRUBase, self).__delitem__(k)
                    del self._refcount[k]

    def _housekeep(self,key):
        self._queue.append(key)
        self._refcount[key] = self._refcount.get(key, 0) + 1
        if len(self._queue) > self._max_entries * 4: self._purge_queue()

    def _purge_queue(self):
        for i in [None] * len(self._queue):
            k = self._queue.popleft()
            if self._refcount[k] == 1:
                self._queue.append(k)
            else:
                self._refcount[k] -= 1  
                
class MemoryLRUCache(LRUBase):

    '''Thread-safe in-memory cache backend using LRU.'''    

    def __init__(self, engine, **kw):
        super(MemoryLRUCache, self).__init__(engine, **kw)
        self._lock = threading.Condition()

    @synchronized
    def __setitem__(self, key, value):
        super(MemoryLRUCache, self).__setitem__(key, value)

    @synchronized        
    def __getitem__(self, key):
        return super(MemoryLRUCache, self).__getitem__(key)
        #return copy.deepcopy(super(MemoryLRUCache, self).__getitem__(key))

    @synchronized
    def __delitem__(self, key):
        super(MemoryLRUCache, self).__delitem__(key)
        