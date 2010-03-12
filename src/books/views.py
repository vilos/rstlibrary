from repoze.bfg.traversal import find_root
from repoze.bfg.url import model_url
from library.views import BaseView

class BookView(BaseView):
    
    def __call__(self):
        return super(BookView, self).__call__(book=self.context)
    
class PageView(BaseView):
    
    def __call__(self):
        section = self.context
        
        book = section.book
        
        contents = section.ashtml()

        next = section
        while next is not None:
            next = next.next_leaf()
            #log.debug('Next node: %r' % next)
            if next and not next.hidden:
                break
            
            
        previous = section
        while previous is not None:
            previous = previous.previous_leaf()
            #log.debug('Previous node: %r' % previous)
            if previous and not previous.hidden:
                break
            
            
        nextlink = next and dict(url=self.base_url(next), title=next.title) or {}
        prevlink = previous and dict(url=self.base_url(previous), title=previous.title) or {}
        uplink = dict(url=self.base_url(book), title=book.title, author = book.docinfo['author'])
        
        data =  dict(
            section=section,
            contents=contents,
            nextlink=nextlink,
            prevlink=prevlink,
            uplink=uplink
            )
        return super(PageView, self).__call__(**data)
    