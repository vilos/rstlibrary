import os
from paste.deploy import loadapp

ini = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))), 'production.ini')
application = loadapp('config:%s' % ini)
