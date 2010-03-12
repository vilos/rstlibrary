'''
Library interfaces
'''

from zope.interface import Interface

class ILibrary(Interface):
    """ Library manager of books """

    def __getitem__(name):
        """ get named book """
        
    def keys():
        """ all book names """

class ICatalogSearch(Interface):
    """Central search point"""
    
    def search(**kw):
        """ fulltext search """
        
    def alphas():
        """ alpha index """
        
    def books():
        """ all book items """