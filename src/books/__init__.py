import os
import library
from source import register_source
from store import register_store
from models import Book, get_book

#from sensible.loginit import logger
#log = logger(os.path.basename(__file__))

def configure(inifile=None):
    #log.info('Configuring books from %s', inifile)
    config = library.configure(inifile)
    src_path = config.get('src_path')
    store_url = config.get('store_url')
    cache_url = config.get('cache_url')
    max_entries = config.get('max_entries')
    # encoding utf_8_sig handles bom signature
    register_source(src_path, encoding='utf_8_sig') 
    register_store(store_url, cache_url, max_entries=max_entries)
    return config