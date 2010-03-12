# coding: UTF-8

import unittest, os

#from repoze.bfg.configuration import Configurator
#from repoze.bfg import testing

class TestStore(unittest.TestCase):

    def setUp(self):
        here = os.path.dirname(os.path.abspath(__file__))
        self.vardir = os.path.join(here, 'vslib-test-var')

        #source
        self.srcdir = os.path.join(self.vardir, 'test')
        from books.store import Store
        self.store = Store('file:/' + self.srcdir, 'memlru://', binary=True)
        
    def tearDown(self):
        from shutil import rmtree
        if os.path.exists(self.vardir):
            rmtree(self.vardir)
                
    def test_set_get(self):
        self.assertEqual(repr(self.store), '{}')
        self.store['max'] = '3ěščřž'.decode('UTF-8')
        self.assertEqual(self.store['max'], '3ěščřž'.decode('UTF-8'))
        
    def test_binary(self):
        from books.source import SourceStore
        tstore = SourceStore(os.path.join(self.vardir, 'test2'), binary=True, compress=True)
        tstore['max'] = 3
        self.assertEqual(tstore['max'], 3)
        
    def test__delitem__(self):
        self.store['max'] = '3'
        del self.store['max']
        self.assertEqual('max' in self.store, False)

    def test_get(self):
        self.store['max'] = '3'
        self.assertEqual(self.store.get('min'), None)

    def test__cmp__(self):
        from books.source import SourceStore
        tstore = SourceStore(os.path.join(self.vardir, 'test2'))
        self.store['max'] = '3'
        tstore['max'] = '3'
        self.assertEqual(self.store, tstore)
        
    def test__len__(self):
        self.store['max'] = '3'
        self.store['min'] = '6'
        self.assertEqual(len(self.store), 2)

    def test_clear(self):
        self.store['max'] = '3'
        self.store['min'] = '6'
        self.store['pow'] = '7'
        self.store.clear()
        self.assertEqual(len(self.store), 0)
        #self.assertEqual(len(os.listdir(self.store._dir)), 0)

    def test_items(self):
        self.store['max'] = '3'
        self.store['min'] = '6'
        self.store['pow'] = '7'
        slist = list(self.store.items())
        self.assertEqual(('min', '6') in slist, True)

    def test_iteritems(self):
        self.store['max'] = '3'
        self.store['min'] = '6'
        self.store['pow'] = '7'
        slist = list(self.store.iteritems())
        self.assertEqual(('min', '6') in slist, True)

    def test_iterkeys(self):
        self.store['max'] = '3'
        self.store['min'] = '6'
        self.store['pow'] = '7'
        slist = list(self.store.iterkeys())
        self.assertEqual('min' in slist, True)

    def test_itervalues(self):
        self.store['max'] = '3'
        self.store['min'] = '6'
        self.store['pow'] = '7'
        slist = list(self.store.itervalues())
        self.assertEqual('6' in slist, True)

    def test_pop(self):
        self.store['max'] = '3'
        self.store['min'] = '6'
        item = self.store.pop('min')
        self.assertEqual(item, '6')

    def test_popitem(self):
        self.store['max'] = '3'
        self.store['min'] = '6'
        self.store['pow'] = '7'
        item = self.store.popitem()
        self.assertEqual(len(item) + len(self.store), 4)

    def test_setdefault(self):
        self.store['max'] = '3'
        self.store['min'] = '6'
        self.store['powl'] = '7'
        self.store.setdefault('pow', '8')
        self.assertEqual(self.store['pow'], '8')

    def test_update(self):
        from books.source import SourceStore
        tstore = SourceStore(os.path.join(self.vardir, 'test2'))
        tstore['max'] = '3'
        tstore['min'] = '6'
        tstore['pow'] = '7'
        self.store['max'] = '2'
        self.store['min'] = '3'
        self.store['pow'] = '7'
        self.store.update(tstore)
        self.assertEqual(self.store['min'], '6')

    def test_values(self):
        self.store['max'] = '3'
        self.store['min'] = '6'
        self.store['pow'] = '7'
        slist = self.store.values()
        self.assertEqual('6' in slist, True)

    def test_keys(self):
        self.store['max'] = '3'
        self.store['min'] = '6'
        self.store['pow'] = '7'
        slist = self.store.keys()
        self.assertEqual('min' in slist, True)



