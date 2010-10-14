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

:hidden: 1

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
        
    def test_doctree(self):
        self.book.source = src
        doc1 = self.book.doctree
        doc2 = self.book.doctree
        self.failUnless(doc1.pformat() == doc2.pformat())
        
    def test_docinfo(self):
        info = self.book.info
        self.failUnlessEqual(info['bookID'], '0000')
        self.failUnlessEqual(info['author'], 'Somebody')
        
        info = self.book['1'].info
        self.failUnlessEqual(info['genre'], 'talk')

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
        
    def test_astext(self):
        s2a = self.book['2']['1']
        self.failUnlessEqual(s2a.astext(), "Section 2.a second alpha")

    def test_hidden(self):
        s3b = self.book['3']['2']
        
        self.failUnless(s3b.hidden)
        self.failUnlessEqual(s3b.astext(), "")
        
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
        target = """0000/3/2
0000/3/1/1
0000/2/2
0000/2/1
0000/1
""" 
        self.failUnlessEqual(out.getvalue(), target)
        
    def test_html(self):
        target = u"""<div class="genre_talk section" id="section-1">
<h1>Section 1</h1>
<p>first
ěščřžýáíúů</p>
</div>
<div class="section" id="section-2">
<h1>Section 2</h1>
<div class="section" id="section-2-a">
<h2>Section 2.a</h2>
<p>second alpha</p>
</div>
<div class="section" id="section-2-b">
<h2>Section 2.b</h2>
<p>second beta</p>
</div>
</div>
<div class="section" id="section-3">
<h1>Section 3</h1>
<div class="section" id="section-3-a">
<h2>Section 3.a</h2>
<p>third alpha</p>
<div class="section" id="section-3-a-1">
<h3>Section 3.a.1</h3>
<p>third alpha.1</p>
</div>
</div>
<div class="hidden section" id="section-3-b">
<h2>Section 3.b</h2>
</div>
</div>
"""
        output = self.book.ashtml()
        #self.failUnlessEqual(len(target), len(output))                
        self.failUnlessEqual( output, target, output)
        
        output = self.book.ashtml()
        self.failUnlessEqual( output, target, output)
        