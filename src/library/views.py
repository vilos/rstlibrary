from zope.component import getUtility
from repoze.bfg.url import route_url
from repoze.bfg.traversal import model_path
from repoze.bfg.chameleon_zpt import get_template
from interfaces import ICatalogSearch
from paginator import Paginator


class BaseView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.base_template = get_template('templates/base.pt')
        self.pagetitle='Welcome to Sri Chinmoy Library'
        
    def __call__(self, **kw):
        data = dict(base=self.base_template, 
                    pagetitle=self.pagetitle, 
                    base_url=self.base_url)
        data.update(kw)
        return data
    
    def base_url(self, model=''):
        path = model_path(model) if model  else ''
        return route_url('books', self.request, traverse=path)
    
class AlphaView(BaseView):
    def __call__(self, **kw):
        catalog = getUtility(ICatalogSearch)
        return super(AlphaView, self).__call__(alphas=catalog.alphas(), **kw)
                                                 
class ListView(AlphaView):
    def __call__(self):
        params = self.request.params
        alpha = params.get('alpha', '')
        catalog = getUtility(ICatalogSearch)
        books = catalog.books(alpha=alpha)
        return super(ListView, self).__call__(books=books, alpha=alpha)
        
class LibraryView(AlphaView):
    def __call__(self):
        return super(LibraryView, self).__call__()

class SearchView(BaseView):
    def __call__(self):
        text = self.request.params.get('text', '')
        page = int(self.request.params.get('page', 1))
        estimated = 0
        results = []
        pagebar = ""
        if text:
            catalog = getUtility(ICatalogSearch)
            estimated, results = catalog.search(text, page-1)
            link_format = route_url('search', self.request, _query=[('text',text), ('page', 1)])[:-1]
            pagebar = Paginator(page=page, 
                                items_per_page=20, 
                                item_count=estimated, 
                                link_format=link_format).pager(format='$link_previous $link_first ~9~ $link_next $link_last')
 
        return super(SearchView, self).__call__(text=text, 
                                                results=results,  
                                                pagebar=pagebar)

    
class NotFoundView(BaseView):
    def __call__(self):
        self.request.response_status = '404 Not Found'
        return super(NotFoundView, self).__call__(pagetitle="Not found.", 
                                                  msg=self.request.environ.get('repoze.bfg.message', ''))