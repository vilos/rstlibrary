import sys,  re  #, logging
import xappy

from sensible.loginit import logger

log = logger(__name__)

#log = logging.getLogger(__name__)

num_sort_regex = re.compile('\d+')

import books
config = books.configure()
index_path = config.get('database')


def zero_fill(matchobj):
    return matchobj.group().zfill(8)

def sortable(title):
    if title:
        sortabletitle = title.lower().strip()
        # Replace numbers with zero filled numbers
        sortabletitle = num_sort_regex.sub(zero_fill, sortabletitle)
        # Truncate to prevent bloat
        sortabletitle = sortabletitle[:30]
        return sortabletitle
    return ''


def indexer_connection(index_path=index_path, indexer=None):
    if not indexer:
        indexer = xappy.IndexerConnection(index_path)

    # indexes
    indexer.add_field_action('searchable_text', xappy.FieldActions.INDEX_FREETEXT, nopos=True)
    indexer.add_field_action('author', xappy.FieldActions.INDEX_EXACT)
    #indexer.add_field_action('keywords', xappy.FieldActions.FACET)
    indexer.add_field_action('type', xappy.FieldActions.INDEX_EXACT)
    indexer.add_field_action('alpha', xappy.FieldActions.INDEX_EXACT)
    indexer.add_field_action('language', xappy.FieldActions.INDEX_EXACT)
    indexer.add_field_action('sortable_title', xappy.FieldActions.SORTABLE)
    indexer.add_field_action('hidden', xappy.FieldActions.INDEX_EXACT)
    #indexer.add_field_action('modified', xappy.FieldActions.SORTABLE, type='data')

    # metadata
    indexer.add_field_action('title', xappy.FieldActions.STORE_CONTENT)
    indexer.add_field_action('alpha', xappy.FieldActions.STORE_CONTENT)
    indexer.add_field_action('language', xappy.FieldActions.STORE_CONTENT)
    indexer.add_field_action('type', xappy.FieldActions.STORE_CONTENT)
    indexer.add_field_action('searchable_text', xappy.FieldActions.STORE_CONTENT)
    #indexer.add_field_action('description', xappy.FieldActions.STORE_CONTENT)
    #indexer.add_field_action('author', xappy.FieldActions.STORE_CONTENT)

    return indexer


class BookIndexer(object):

    type = 'Book'
    
    def __init__( self, resource):
        self.resource = resource
        log.debug("%s - indexing %r", self.__class__.__name__, self.resource)

    def document(self, connection):
        doc = xappy.UnprocessedDocument()
        title = self.resource.title
        alpha = self.resource.alpha
        author = self.resource.author
        language = self.resource.language
        #keywords = self.resource.keywords
        #modified = self.resource.modified
        searchable_text = title

        #log.debug("st: %d\n%s\n" % (len(searchable_text), searchable_text[:500]) )
        doc.fields.append(xappy.Field('type', self.type))
        if title:
            doc.fields.append(xappy.Field('title', title))
            doc.fields.append(xappy.Field('sortable_title', sortable(title)))

        if alpha:
            doc.fields.append(xappy.Field('alpha', alpha))

        if language:
            doc.fields.append(xappy.Field('language', language))
            
        #if keywords:
        #    for keyword in keywords:
        #        doc.fields.append(xappy.Field('keywords', keyword))

        if author:
            doc.fields.append(xappy.Field('author', author))

#        if modified:
#            try:
#                #date = datetime.datetime(*time.strptime(creation_date[0], "%Y-%m-%d %H:%M:%S")[0:6])
#                doc.fields.append(xappy.Field('modified', modified))
#            except ValueError:
#                pass

        if searchable_text:
            doc.fields.append(xappy.Field('searchable_text', searchable_text))

        return doc


class SectionIndexer(object):

    type = 'Section'
     
    def __init__( self, resource):
        self.resource = resource
        log.debug("%s - indexing %r", self.__class__.__name__, self.resource)

    def document(self, connection):
        doc = xappy.UnprocessedDocument()

        if self.resource.hidden:
            hidden = '1'
        else: 
            hidden = '0'
            
        doc.fields.append(xappy.Field('type', self.type))
        doc.fields.append(xappy.Field('hidden', hidden))
                          
        if hidden == '0':
            title = self.resource.title
            searchable_text = self.resource.astext()

            if title:
                doc.fields.append(xappy.Field('title', title))
                doc.fields.append(xappy.Field('sortable_title', sortable(title)))
    
            if searchable_text:
                doc.fields.append(xappy.Field('searchable_text', searchable_text))

        return doc
    
def index(bookid):
    connection = indexer_connection(index_path)
    book = books.get_book(bookid)
    
    for obj in book.walk():
        indexer = globals().get("%sIndexer" % obj.__class__.__name__, None)
        if indexer is None:
            raise KeyError("Indexer for object %s not found." % obj.__class__.__name__)

        doc = indexer(obj).document(connection)
        doc.id = obj.__name__
    
        connection.replace(doc)
    
    connection.flush()
    connection.close()

if __name__ == '__main__':
    n = len(sys.argv)
    bookid = ''
    if n > 1:
        bookid = sys.argv[1]
    if bookid:
        print index(bookid)
    
