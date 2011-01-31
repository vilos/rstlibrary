import os
import library
from source import register_source
from store import register_store
from models import Book, get_book


def configure(**kw):
    config = library.configure(**kw)
    src_path = config.get('src_path')
    store_url = config.get('store_url')
    cache_url = config.get('cache_url')
    max_entries = config.get('max_entries')
    register_source(src_path) 
    register_store(store_url, cache_url, max_entries=max_entries)
    return config