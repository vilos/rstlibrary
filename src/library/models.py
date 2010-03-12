from zope.interface import implements
from repoze.bfg.interfaces import ILocation
from interfaces import ILibrary
from books.models import get_book

class Library(object):
    
    implements(ILibrary, ILocation)
    
    __name__ = ''
    __parent__ = None

    def __init__(self, request):
        pass
     
    def __getitem__(self, name):
        return get_book(name, self)

    

