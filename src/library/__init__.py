from paste.deploy.loadwsgi import appconfig
import os

DEFAULT_INIFILE = 'production'

def configure(inifile=None):
    if not inifile:
        inifile = DEFAULT_INIFILE
    path = '%s.ini' % inifile
    config_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', path))
    base, name = os.path.split(config_path)
    config = appconfig('config:%s' % name, name='vslibrary', relative_to=base)
    return config