from zope.interface import implements
from zope.component import getUtility
from repoze.bfg.interfaces import ILocation
from repoze.bfg.traversal import find_interface, model_path
from docutils import nodes
from interfaces import IBook, ISection, ISource, IStore
from restructured import publish2doc, publish, extract, get_info, is_hidden_section

class Section(object):
    
    implements(ISection, ILocation)
    
    def __init__(self, node, parent, name):
        self._node = node
        self.__parent__ = self.parent = parent
        self.__name__ = name    
    
    def __getitem__(self, name):
        """ repoze.bfg traversal support """
        try:
            key = int(name)
        except (TypeError, ValueError):
            #log.debug("Not found: %s in %s of %s" % (name, self.__name__, self.__parent__))
            raise KeyError
        if key == 0:
            raise IndexError
        i = key
        for child in self.node:
            if isinstance(child, nodes.section):
                i -= 1
            if i == 0:
                return Section(child, self, str(key))
        raise KeyError
        
    def __iter__(self):
        i = 1
        for child in self.node:
            if isinstance(child, nodes.section):
                yield Section(child, self, str(i))
                i += 1
    
    def __repr__(self):
        return "<Section %s>" % self.url
    
    @property
    def url(self):
        return model_path(self)

    @property
    def node(self):
        return self._node
    
    @property
    def book(self):
        return find_interface(self, Book)    
    
    def subsections(self):
        return list(self.__iter__())
    
    @property
    def title(self):
        if isinstance(self.node, nodes.section):
            return self.node[0].astext()     
        raise RuntimeError, "Wrong node for title: %r" % self.node

    @property
    def info(self):
        return get_info(self.node)
    
    @property
    def hidden(self):
        return is_hidden_section(self.node)
    
    @property
    def genre(self):
        return self.info.get('genre', None)
    
    @property
    def isleaf(self):
        for child in self:
            return False
        return True

    @property
    def classes(self):
        return " ".join(self.node.get('classes', []))
        
    def walk(self):
        yield self
        for section in self:
            for subsection in section.walk():
                yield subsection
    
    # page navigation
    def first_child_leaf(self):
        for section in self.walk():
            if section.isleaf:
                return section
        return None

    def last_child_leaf(self):
        section = self
        while not section.isleaf:
            section = section.subsections()[-1]
        return section

    def next_leaf(self):
        if self.parent == None or isinstance(self, Book):
            return None
        try:
            next = self.parent[int(self.__name__)+1]
            return next.first_child_leaf()
        except KeyError:
            return self.parent.next_leaf()

    def previous_leaf(self):
        if self.parent == None or isinstance(self, Book):
            return None
        i = int(self.__name__) - 1
        if i > 0:
            prev = self.parent[i]
            if not prev.isleaf:
                prev = prev.last_child_leaf()
            return prev
        else:
            return self.parent.previous_leaf()
    
    #serializations 
    def astext(self):
        if self.hidden:
            return u""
        doctree = self.book.doctree
        if not isinstance(self, Book):
            doctree = doctree.copy()
            doctree.append(self.node)
        return extract(doctree)
    
    def ashtml(self):
        if self.hidden:
            return u""
        doctree = self.book.doctree
        if not isinstance(self, Book):
            doctree = doctree.copy()
            doctree.append(self.node)
        return publish(doctree)
    
    def asxml(self):
        """ restructured pseudo xml """
        xml = self.node.pformat()
        from chameleon.core.utils import htmlescape
        xml = htmlescape(xml)
        xml = xml.replace('\n','<br/>\n')
        xml = xml.replace(' ', '&nbsp;')
        return xml

        
ARTICLES = ('A ', 'AN ', 'THE ')

class Book(Section):
    
    implements(IBook)
    
    def __init__(self, name, parent=None):
        Section.__init__(self, node=None, parent=parent, name=name)
        
        self.id = name
        
        self._src = getUtility(ISource)
        self._store = getUtility(IStore)
        
    def _src_get(self):
        return self._src[self.id]
    
    def _src_set(self, txt):
        self._src[self.id] = txt
        
    def _src_del(self):
        del self._src[self.id]
        
    source = property(_src_get, _src_set, _src_del)
    
    @property
    def doctree(self):
        try:
            node = self._store[self.id]
        except KeyError:
            node = publish2doc(self.source)
            self._store[self.id] = node
            
        return node
        
    node = doctree
    
    def __repr__(self):
        return u"<Book %s>" % self.id
    
    @property
    def title(self):
        return self.node[0].astext()
        
    # indexed properties
    @property
    def alpha(self):
        """ the first letter of a book title """
        title = self.title.upper()
        for an in ARTICLES:
            if title.startswith(an) and len(title) > len(an):
                return title[len(an):].lstrip()[0]
        return  title[0]
    
    @property
    def author(self):
        return self.info.get('author', None)        
    
    @property
    def language(self):
        return self.info.get('language', None)        

    @property
    def genre(self):
        return self.info.get('genre', None)        
    
    
def get_book(name, parent=None):
    if name in getUtility(ISource):
        return Book(name, parent)
    else:
        raise KeyError('Book not found: %s' % name)
