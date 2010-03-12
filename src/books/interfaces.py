'''
Book interfaces
'''

from zope.interface import Interface, Attribute
from repoze.bfg.interfaces import ILocation

class IBook(ILocation):
    """ represents book object """
    
    id = Attribute(""" Book ID """)
    title = Attribute(""" Book title """)
    docinfo = Attribute(""" other book attributes """)
    source =  Attribute(""" raw text source in Restructured Text format""")
    
class ISection(ILocation):
    """ """
    
    node = Attribute(""" docutils section node """)
    parent = Attribute(""" parent section """)
    book = Attribute(""" parent book """)
    hidden = Attribute(""" true if section hidden """)
    isleaf = Attribute(""" true if no subsections """)
    nextleaf = Attribute(""" next leaf section """)
    previousleaf = Attribute(""" previous leaf section """)
    first_child_leaf = Attribute(""" first child leaf """)
    last_child_leaf = Attribute(""" last child leaf """)
    
    def __getitem__(self, name):
        """ repoze.bfg traversal support """
        
    def subsections():
        """ child nodes """
        
    def walk():
        """ traverse subtree generator """
        
    def astext():
        """ extract text from node """
        
    def ashtml():
        """ render content in html format """
        
class IStore(Interface):
    """ standard mapping interface """
    
    def __getitem__():
        """ """
    def __setitem__(value):
        """ """
    def __delitem__():
        """ """
        
class ISource(Interface):
    """ represents source text """
    
    def __getitem__():
        """ """
    def __setitem__(value):
        """ """
    def __delitem__():
        """ """    