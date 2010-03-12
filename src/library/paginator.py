# coding: UTF-8
'''
based on Christoph Haas' paginate module
'''
import re
from string import Template

def url_for(**kw):
    return kw['link_format'] + str(kw['page'])

class Tag(object):
    
    def __init__(self, tag_name, content='', **kw):
        self.tag_name = tag_name
        self.content = content
        self.attrs = kw
        
    def __unicode__(self):
        attrs = ' '.join(['%s="%s"' % (k, self.attrs[k]) for k in self.attrs])
        return "<%(tag_name)s %(attrs)s>%(content)s</%(tag_name)s>"  % dict(tag_name=self.tag_name, 
                                                                            attrs=attrs, 
                                                                            content=self.content) 

class Paginator(object):
    '''
    '''
    
    def __init__(self, page=1, items_per_page=20, item_count=0, **kwargs):

        # Safe the kwargs class-wide so they can be used in the pager() method
        self.kwargs = kwargs
        # The self.page is the number of the current page.
        # The first page has the number 1!
        try:
            self.page = int(page) # make it int() if we get it as a string
        except (ValueError, TypeError):
            self.page = 1

        self.items_per_page = items_per_page

        # Unless the user tells us how many items the collections has
        # we calculate that ourselves.

        self.item_count = item_count


        # Compute the number of the first and last available page
        if self.item_count > 0:
            self.first_page = 1
            self.page_count = ((self.item_count - 1) / self.items_per_page) + 1
            self.last_page = self.first_page + self.page_count - 1

            # Make sure that the requested page number is the range of valid pages
            if self.page > self.last_page:
                self.page = self.last_page
            elif self.page < self.first_page:
                self.page = self.first_page

            # Note: the number of items on this page can be less than
            #       items_per_page if the last page is not full
            self.first_item = (self.page - 1) * items_per_page + 1
            self.last_item = min(self.first_item + items_per_page - 1, self.item_count)

            # Links to previous and next page
            if self.page > self.first_page:
                self.previous_page = self.page-1
            else:
                self.previous_page = None

            if self.page < self.last_page:
                self.next_page = self.page+1
            else:
                self.next_page = None

        # No items available
        else:
            self.first_page = None
            self.page_count = 0
            self.last_page = None
            self.first_item = None
            self.last_item = None
            self.previous_page = None
            self.next_page = None

    def __repr__(self):
        return ("Page:\n"
            "Collection type:  %(type)s\n"
            "(Current) page:   %(page)s\n"
            "First item:       %(first_item)s\n"
            "Last item:        %(last_item)s\n"
            "First page:       %(first_page)s\n"
            "Last page:        %(last_page)s\n"
            "Previous page:    %(previous_page)s\n"
            "Next page:        %(next_page)s\n"
            "Items per page:   %(items_per_page)s\n"
            "Number of items:  %(item_count)s\n"
            "Number of pages:  %(page_count)s\n"
            % {
            'type':type(self.collection),
            'page':self.page,
            'first_item':self.first_item,
            'last_item':self.last_item,
            'first_page':self.first_page,
            'last_page':self.last_page,
            'previous_page':self.previous_page,
            'next_page':self.next_page,
            'items_per_page':self.items_per_page,
            'item_count':self.item_count,
            'page_count':self.page_count,
            })
        
    def pager(self, format='~2~', page_param='page', partial_param='partial',
        show_if_single_page=False, separator=' ', onclick=None,
        symbol_first=u'⪻', symbol_last=u'⪼',
        symbol_previous=u'≺', symbol_next=u'≻', symbol_dotdot=u'…',
        link_attr={'class':'pager_link'}, curpage_attr={'class':'pager_curpage'},
        dotdot_attr={'class':'pager_dotdot'}, **kwargs):
        """
        Return string with links to other pages (e.g. "1 2 [3] 4 5 6 7").

        format:
            Format string that defines how the pager is rendered. The string
            can contain the following $-tokens that are substituted by the
            string.Template module:

            - $first_page: number of first reachable page
            - $last_page: number of last reachable page
            - $page: number of currently selected page
            - $page_count: number of reachable pages
            - $items_per_page: maximal number of items per page
            - $first_item: index of first item on the current page
            - $last_item: index of last item on the current page
            - $item_count: total number of items
            - $link_first: link to first page (unless this is first page)
            - $link_last: link to last page (unless this is last page)
            - $link_previous: link to previous page (unless this is first page)
            - $link_next: link to next page (unless this is last page)

            To render a range of pages the token '~3~' can be used. The 
            number sets the radius of pages around the current page.
            Example for a range with radius 3:

            '1 .. 5 6 7 [8] 9 10 11 .. 500'

            Default: '~2~'

        symbol_first
            String to be displayed as the text for the %(link_first)s 
            link above.

            Default: '<<'

        symbol_last
            String to be displayed as the text for the %(link_last)s 
            link above.

            Default: '>>'

        symbol_previous
            String to be displayed as the text for the %(link_previous)s 
            link above.

            Default: '<'

        symbol_next
            String to be displayed as the text for the %(link_next)s 
            link above.

            Default: '>'

        separator:
            String that is used to seperate page links/numbers in the 
            above range of pages.

            Default: ' '

        page_param:
            The name of the parameter that will carry the number of the 
            page the user just clicked on. The parameter will be passed 
            to a url_for() call so if you stay with the default 
            ':controller/:action/:id' routing and set page_param='id' then 
            the :id part of the URL will be changed. If you set 
            page_param='page' then url_for() will make it an extra 
            parameters like ':controller/:action/:id?page=1'. 
            You need the page_param in your action to determine the page 
            number the user wants to see. If you do not specify anything 
            else the default will be a parameter called 'page'.

        partial_param:
            When using AJAX/AJAH to do partial updates of the page area the
            application has to know whether a partial update (only the
            area to be replaced) or a full update (reloading the whole
            page) is required. So this parameter is the name of the URL
            parameter that gets set to 1 if the 'onclick' parameter is
            used. So if the user requests a new page through a Javascript
            action (onclick) then this parameter gets set and the application
            is supposed to return a partial content. And without
            Javascript this parameter is not set. The application thus has
            to check for the existance of this parameter to determine
            whether only a partial or a full page needs to be returned.
            See also the examples in this modules docstring.

            Default: 'partial'

        show_if_single_page:
            if True the navigator will be shown even if there is only 
            one page
            
            Default: False

        link_attr (optional)
            A dictionary of attributes that get added to A-HREF links 
            pointing to other pages. Can be used to define a CSS style 
            or class to customize the look of links.

            Example: { 'style':'border: 1px solid green' }

            Default: { 'class':'pager_link' }

        curpage_attr (optional)
            A dictionary of attributes that get added to the current 
            page number in the pager (which is obviously not a link).
            If this dictionary is not empty then the elements
            will be wrapped in a SPAN tag with the given attributes.

            Example: { 'style':'border: 3px solid blue' }

            Default: { 'class':'pager_curpage' }

        dotdot_attr (optional)
            A dictionary of attributes that get added to the '..' string
            in the pager (which is obviously not a link). If this 
            dictionary is not empty then the elements will be wrapped in 
            a SPAN tag with the given attributes.

            Example: { 'style':'color: #808080' }

            Default: { 'class':'pager_dotdot' }

        onclick (optional)
            This paramter is a string containing optional Javascript code
            that will be used as the 'onclick' action of each pager link.
            It can be used to enhance your pager with AJAX actions loading another 
            page into a DOM object. 

            In this string the variable '$partial_url' will be replaced by
            the URL linking to the desired page with an added 'partial=1'
            parameter (or whatever you set 'partial_param' to).
            In addition the '$page' variable gets replaced by the
            respective page number.

            Note that the URL to the destination page contains a 'partial_param' 
            parameter so that you can distinguish between AJAX requests (just 
            refreshing the paginated area of your page) and full requests (loading 
            the whole new page).

            [Backward compatibility: you can use '%s' instead of '$partial_url']

            jQuery example:
                "$('#my-page-area').load('$partial_url'); return false;"

            Yahoo UI example:
                "YAHOO.util.Connect.asyncRequest('GET','$partial_url',{
                    success:function(o){YAHOO.util.Dom.get('#my-page-area').innerHTML=o.responseText;}
                    },null); return false;"

            scriptaculous example:
                "new Ajax.Updater('#my-page-area', '$partial_url',
                    {asynchronous:true, evalScripts:true}); return false;"

            ExtJS example:
                "Ext.get('#my-page-area').load({url:'$partial_url'}); return false;"
            
            Custom example:
                "my_load_page($page)"

        Additional keyword arguments are used as arguments in the links.
        Otherwise the link will be created with url_for() which points 
        to the page you are currently displaying.
        """
        self.curpage_attr = curpage_attr
        self.separator = separator
        self.pager_kwargs = kwargs
        self.page_param = page_param
        self.partial_param = partial_param
        self.onclick = onclick
        self.symbol_dotdot = symbol_dotdot
        self.link_attr = link_attr
        self.dotdot_attr = dotdot_attr

        # Don't show navigator if there is no more than one page
        if self.page_count == 0 or (self.page_count == 1 and not show_if_single_page):
            return ''


        # Replace ~...~ in token format by range of pages
        result = re.sub(r'~(\d+)~', self._range, format)

        # Interpolate '%' variables
        result = Template(result).safe_substitute({
            'first_page': self.first_page,
            'last_page': self.last_page,
            'page': self.page,
            'page_count': self.page_count,
            'items_per_page': self.items_per_page,
            'first_item': self.first_item,
            'last_item': self.last_item,
            'item_count': self.item_count,
            'link_first': self.page>self.first_page and \
                    self._pagerlink(self.first_page, symbol_first) or '',
            'link_last': self.page<self.last_page and \
                    self._pagerlink(self.last_page, symbol_last) or '',
            'link_previous': self.previous_page and \
                    self._pagerlink(self.previous_page, symbol_previous) or '',
            'link_next': self.next_page and \
                    self._pagerlink(self.next_page, symbol_next) or ''
        })

        return unicode(result)
    
    def _range(self, regexp_match):
        """
        Return range of linked pages (e.g. '1 2 [3] 4 5 6 7 8').

        Arguments:
            
        regexp_match
            A "re" (regular expressions) match object containing the
            radius of linked pages around the current page in
            regexp_match.group(1) as a string

        This funtion is supposed to be called as a callable in 
        re.sub.
        
        """
        radius = int(regexp_match.group(1))

        # Compute the first and last page number within the radius
        # e.g. '1 .. 5 6 [7] 8 9 .. 12'
        # -> leftmost_page  = 5
        # -> rightmost_page = 9
        leftmost_page = max(self.first_page, (self.page-radius))
        rightmost_page = min(self.last_page, (self.page+radius))

        nav_items = []

        # Create a link to the first page (unless we are on the first page
        # or there would be no need to insert '..' spacers)
        if self.page != self.first_page and self.first_page < leftmost_page:
            nav_items.append( self._pagerlink(self.first_page, self.first_page) )

        # Insert dots if there are pages between the first page
        # and the currently displayed page range
        if leftmost_page - self.first_page > 1:
            # Wrap in a SPAN tag if nolink_attr is set
            if self.dotdot_attr:
                text = unicode(Tag('span', self.symbol_dotdot, **self.dotdot_attr))
            nav_items.append(self.symbol_dotdot)

        for thispage in xrange(leftmost_page, rightmost_page+1):
            # Hilight the current page number and do not use a link
            if thispage == self.page:
                text = '%s' % (thispage,)
                # Wrap in a SPAN tag if nolink_attr is set
                if self.curpage_attr:
                    text = unicode(Tag('span', text, **self.curpage_attr))
                nav_items.append(text)
            # Otherwise create just a link to that page
            else:
                text = '%s' % (thispage,)
                nav_items.append( self._pagerlink(thispage, text) )

        # Insert dots if there are pages between the displayed
        # page numbers and the end of the page range
        if self.last_page - rightmost_page > 1:
            # Wrap in a SPAN tag if nolink_attr is set
            if self.dotdot_attr:
                text = unicode(Tag('span', self.symbol_dotdot, **self.dotdot_attr))
            nav_items.append(self.symbol_dotdot)

        # Create a link to the very last page (unless we are on the last
        # page or there would be no need to insert '..' spacers)
        if self.page != self.last_page and rightmost_page < self.last_page:
            nav_items.append( self._pagerlink(self.last_page, self.last_page) )

        return self.separator.join(nav_items)
    
    def _pagerlink(self, pagenr, text):
        """
        Create a URL that links to another page using url_for().

        Parameters:
            
        pagenr
            Number of the page that the link points to

        text
            Text to be printed in the A-HREF tag
        """
        #from routes import url_for, request_config
        
        # Let the url_for() from webhelpers create a new link and set
        # the variable called 'page_param'. Example:
        # You are in '/foo/bar' (controller='foo', action='bar')
        # and you want to add a parameter 'pagenr'. Then you
        # call the navigator method with page_param='pagenr' and
        # the url_for() call will create a link '/foo/bar?pagenr=...'
        # with the respective page number added.
        link_params = {}
        # Use the instance kwargs from Page.__init__ as URL parameters
        link_params.update(self.kwargs)
        # Add keyword arguments from pager() to the link as parameters
        link_params.update(self.pager_kwargs)
        link_params[self.page_param] = pagenr

        # get the configuration for the current request
        #config = request_config()
        # if the Mapper is configured with explicit=True we have to fetch
        # the controller and action manually
        #if config.mapper.explicit:
        #    if hasattr(config, 'mapper_dict'):
        #        for k, v in config.mapper_dict.items():
        #            link_params[k] = v

        # Create the URL to load a certain page
        link_url = url_for(**link_params)
        # Create the URL to load the page area part of a certain page (AJAX updates)
        link_params[self.partial_param] = 1
        partial_url = url_for(**link_params)

        if self.onclick: # create link with onclick action for AJAX
            try: # if '%s' is used in the 'onclick' parameter (backwards compatibility)
                onclick_action = self.onclick % (partial_url,)
            except TypeError:
                onclick_action = Template(self.onclick).safe_substitute({
                  "partial_url": partial_url,
                  "page": pagenr
                })
            return unicode(Tag('a', text, href=link_url, onclick=onclick_action, **self.link_attr))
        else: # return static link
            return unicode(Tag('a', text, href=link_url, **self.link_attr))