from zope.component import getSiteManager
from repoze.bfg.threadlocal import get_current_registry


def encode(var):
    if isinstance(var, unicode):
        return var.encode('utf-8')
    return var

def decode(var):
    if not isinstance(var, unicode):
        return var.decode('utf-8')
    return var


def debug_sm():
    
    print_utils(getSiteManager())    
    print_utils(get_current_registry())
    
def debug_asm():
    print_adapters(getSiteManager())    
    print_adapters(get_current_registry())
    
def print_utils(sm):
    
    print 'site manager: %r' % sm, id(sm)
    for u in sm.registeredUtilities():
        print '\t%s, %s, %s, %s' % (
            getattr(u.provided, '__name__', ''), u.name,
            getattr(u.component, '__name__', ''), u.info,
            )
        
def print_adapters(sm):
    print 'site manager: %r' % sm, id(sm)
    for a in sm.registeredAdapters():
        print   '\t%s, %s, %r, %s, %r' % (
                '[' + ", ".join([r.__name__ for r in a.required]) + ']',
                getattr(a.provided, '__name__', ''), a.name,
                getattr(a.factory, '__name__', ''), a.info,
                )