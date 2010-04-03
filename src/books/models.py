from zope.interface import implements
from zope.component import getUtility
from repoze.bfg.interfaces import ILocation
from repoze.bfg.traversal import find_interface, model_path
from docutils import nodes
from interfaces import IBook, ISection, ISource, IStore
from restructured import publish2doc, publish, extract

class Section(object):
    
    implements(ISection, ILocation)
    
    def __init__(self, node, parent, name):
        self._node = node
        self.__parent__ = self.parent = parent
        self.__name__ = name
    
    @property
    def node(self):
        return self._node
    
    @property
    def book(self):
        return find_interface(self, Book)        
    
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
    
    def subsections(self):
        return list(self.__iter__())
    
    @property
    def title(self):
        if isinstance(self.node, nodes.section):
            return self.node[0].astext()     
        raise RuntimeError, "Wrong node for title: %r" % self.node

    @property
    def classes(self):
        return " ".join(self.node.get('classes', []))
        
    @property
    def hidden(self):
        return 'hidden' in self.node.get('classes', [])
    
    @property
    def isleaf(self):
        for child in self:
            return False
        return True
    
    def walk(self):
        yield self
        for section in self:
            for subsection in section.walk():
                yield subsection
                
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
            
    def astext(self):
        if self.hidden:
            return u""
        doctree = self.root.doctree
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
    
    @property
    def url(self):
        return model_path(self)
    
    def __repr__(self):
        return "<Section %s>" % model_path(self)
        
class Book(Section):
    
    implements(IBook)
    
    def __init__(self, name, parent=None):
        Section.__init__(self, node=None, parent=parent, name=name)
        
        self.id = name
        
        self._src = getUtility(ISource)
        self._store = getUtility(IStore)
        
        self._n = None  #TODO remove
        
        #if not self.id in self._src:
        #    raise KeyError('%s' % self.id)
        
    def _src_get(self):
        return self._src[self.id]
    
    def _src_set(self, txt):
        self._src[self.id] = txt
        
    def _src_del(self):
        del self._src[self.id]
        
    source = property(_src_get, _src_set, _src_del)
    
    @property
    def doctree(self):
        
        #if not self._n:
        #    self._n = publish2doc(self.source)
        #return self._n
        
        
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
    
    @property
    def docinfo(self):
        result = {}
        docinfo = first_child(self.doctree, nodes.docinfo)
        if docinfo:
            for field in docinfo:
                if isinstance(field, nodes.field):
                    key = first_child(field, nodes.field_name).astext()
                    value = first_child(field, nodes.field_body).astext()
                else:
                    key = field.tagname
                    value = field.astext()
                result[key] = value
        return result
    
def get_book(name, parent=None):
    if name in getUtility(ISource):
        return Book(name, parent)
    else:
        raise KeyError('Book not found: %s' % name)
    
def first_child(node, child_class):
    return node[node.first_child_matching_class(child_class)]
