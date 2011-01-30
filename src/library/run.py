# coding: UTF-8
from repoze.bfg.configuration import Configurator
from books import register_source, register_store
from fscontent import ContentRoot
from catalog import register_catalog


     
def app(global_config, **settings):
    """ This function returns a WSGI application.
    
    It is usually called by the PasteDeploy framework during 
    ``paster serve``.
    """
    names = ('src_path', 'store_url', 'cache_url', 'max_entries', 'database', 'content_dir')
    values = []
    for name in names:
        val = settings.get(name)
        if val is None: 
            raise ValueError("No ’%s’ value in application configuration." % name) 
        values.append(val)
        
    src_path, store_url, cache_url, max_entries, database, content_dir = values
    
    zcml_file = settings.get('configure_zcml', 'configure.zcml')
    config = Configurator(settings=settings, root_factory=ContentRoot(content_dir))
    # use local component registry
    config.hook_zca()
    config.begin()
    config.load_zcml(zcml_file)
    
    register_source(src_path,  encoding='utf_8_sig')
    register_store(store_url, cache_url, max_entries=max_entries)
    register_catalog(database)
    config.end()
    
    return config.make_wsgi_app()
