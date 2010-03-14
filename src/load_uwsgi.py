from os.path import realpath, dirname, join 
from paste.deploy import loadapp

ini = join(dirname(dirname(realpath(__file__))), 'production.ini')
application = loadapp('config:%s' % ini)

#def application(environ, start_response):
#    start_response('200 OK', [('Content-Type', 'text/plain')])
#    yield 'Hello World\n'
