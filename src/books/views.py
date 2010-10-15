from simplejson import loads
from library.views import BaseView
from models import get_book

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
        uplink = dict(url=self.base_url(book), title=book.title, author = book.author)
        
        data =  dict(
            section=section,
            contents=contents,
            nextlink=nextlink,
            prevlink=prevlink,
            uplink=uplink
            )
        return super(PageView, self).__call__(**data)


class XMLView(BaseView):
    def __call__(self):
        return super(XMLView, self).__call__(xml=self.context.asxml())
    

def update_view(request):
    json = loads(request.body)
    bookid = json.get('bookid', None)
    if not bookid:
        return dict(error="Missing bookid parameter.")

    try:
        book = get_book(bookid)
    except KeyError:
        return dict(error="Book %s not found." % bookid)

    try:
        del book._store[book.id]
    except KeyError:
        # not pickled - ignore
        pass
    # load from source
    book.doctree
    return {'result': '%s invalidated.' % book.id }
