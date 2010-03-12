# coding: UTF-8

import unittest, os

#from repoze.bfg.configuration import Configurator
#from repoze.bfg import testing

src = """
Ďěľíčáťéžôšúů
=============

:bookID: 0000
:author: Somebody

Section 1
---------

:genre: talk

first
ěščřžýáíúů


Section 2
---------

Section 2.a
~~~~~~~~~~~

second alpha

Section 2.b
~~~~~~~~~~~

second beta

Section 3
---------

Section 3.a
~~~~~~~~~~~

third alpha

Section 3.a.1
+++++++++++++

third alpha.1


Section 3.b
~~~~~~~~~~~

third beta

"""

class TestBook(unittest.TestCase):

    def setUp(self):
        here = os.path.dirname(os.path.abspath(__file__))
        self.vardir = os.path.join(here, 'vslib-test-var') 
        
        #source
        srcdir = os.path.join(self.vardir, 'src')
        #os.makedirs(srcdir)
        from books.source import register_source
        register_source('file:/' + srcdir)
        
        #store
        storedir = os.path.join(self.vardir, 'store')
        #os.makedirs(storedir)
        from books.store import register_store
        self.store = register_store(store_url='file:/' + storedir, cache_url='memlru://', max_entries=10)
        
        from books.models import Book
        self.book = Book('0000', None)
        self.book.source = src
        
    def tearDown(self):
        from books.store import unregister_store
        unregister_store(self.store)
        from shutil import rmtree
        rmtree(self.vardir)
        
    def test_set_get(self):
        self.book.source = src
        usrc = src.decode('UTF-8')
        self.assertEqual(self.book.source, usrc)
        del self.book.source
        self.assertRaises(KeyError, self.book._src_get)
        
    def test_docinfo(self):
        self.book.source = src
        doc1 = self.book.doctree
        doc2 = self.book.doctree
        self.failUnless(doc1.pformat() == doc2.pformat())

    def test_section(self):
        book = self.book
        doc = book.doctree
        from docutils.nodes import document
        self.failUnless(isinstance(doc, document))
        self.failUnlessEqual(len(book.subsections()), 3)
        s1 = book['1']
        s2 = book['2']
        self.failUnless(s1.isleaf)
        self.failIf(s2.isleaf)

        self.failUnlessRaises(IndexError, book.__getitem__, '0')
        self.failUnlessRaises(KeyError, book.__getitem__, '7')
        self.failUnlessRaises(KeyError, book.__getitem__, 'x')
        
    def test_walk(self):

        from repoze.bfg.traversal import model_path
        from cStringIO import StringIO 
        out = StringIO()
        for section in self.book.walk():
            print >>out, model_path(section)
            #print >>out, section.astext()
        target = """0000
0000/1
0000/2
0000/2/1
0000/2/2
0000/3
0000/3/1
0000/3/1/1
0000/3/2
"""
        self.failUnlessEqual(out.getvalue(), target)

    def test_next(self):

        from repoze.bfg.traversal import model_path
        from cStringIO import StringIO 
        out = StringIO()
  
        next = self.book.first_child_leaf()
        while next:
            print >>out, model_path(next)
            next = next.next_leaf()
        target = """0000/1
0000/2/1
0000/2/2
0000/3/1/1
0000/3/2
""" 
        self.failUnlessEqual(out.getvalue(), target)
        
    def test_prev(self):

        from repoze.bfg.traversal import model_path
        from cStringIO import StringIO 
        out = StringIO()
          
        prev = self.book.last_child_leaf()
        while prev:
            print >>out, model_path(prev)
            prev = prev.previous_leaf()
        print out.getvalue()
        target = """0000/3/2
0000/3/1/1
0000/2/2
0000/2/1
0000/1
""" 
        self.failUnlessEqual(out.getvalue(), target)