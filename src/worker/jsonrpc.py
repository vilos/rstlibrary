#!/usr/bin/env python
# A reaction to: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/552751
import sys
from webob import Request, Response
from webob import exc
from simplejson import loads, dumps
from wsgiproxy.exactproxy import proxy_exact_request
from log import log

class ServerProxy(object):
    """
    JSON proxy to a remote service.
    """

    def __init__(self, url, proxy=None):
        self._url = url
        if proxy is None:
            from wsgiproxy.exactproxy import proxy_exact_request
            proxy = proxy_exact_request
        self.proxy = proxy

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        return _Method(self, name)
    
    def __repr__(self):
        return '<%s for %s>' % (self.__class__.__name__, self._url)

class _Method(object):

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

    def __call__(self, *args):
        json = dict(method=self.name,
                    id=None,
                    params=list(args))
        req = Request.blank(self.parent._url)
        req.method = 'POST'
        req.content_type = 'application/json'
        req.body = dumps(json)
        resp = req.get_response(self.parent.proxy)
        if resp.status_int != 200 and not (
            resp.status_int == 500
            and resp.content_type == 'application/json'):
            raise ProxyError(
                "Error from JSON-RPC client %s: %s"
                % (self.parent._url, resp.status),
                resp)
        json = loads(resp.body)
        if json.get('error') is not None:
            e = Fault(
                json['error'].get('message'),
                json['error'].get('code'),
                json['error'].get('error'),
                resp)
            raise e
        return json['result']

class Client(object):
    def __init__(self, url):
        self.url = url
        
    def send(self, data={}):
        
        req = Request.blank(self.url)
        req.method = 'POST'
        req.content_type = 'application/json'
        req.body = dumps(data)
        resp = req.get_response(proxy_exact_request)
        if resp.status_int != 200 and not (
            resp.status_int == 500
            and resp.content_type == 'application/json'):
            raise ProxyError("Error from JSON-RPC client %s: %s" 
                             % (self.url, resp.status), resp)
        try:
            json = loads(resp.body)
        #except ValueError:
        except:
            print >>sys.stderr, resp.body
            raise
            
        if json.get('error') is not None:
            e = Fault(json.get('error'),
#                json['error'].get('message'),
#                json['error'].get('code'),
#                json['error'].get('error'),
                resp)
            raise e
        return json.get('result', None)
    
class ProxyError(Exception):
    """
    Raised when a request via ServerProxy breaks
    """
    def __init__(self, message, response):
        Exception.__init__(self, message)
        self.response = response

class Fault(Exception):
    """
    Raised when there is a remote error
    """
    def __init__(self, message, response):
        Exception.__init__(self, message)
        self.response = response
    def __str__(self):
        return 'Error calling %s: %s' % (self.response.request.url, self.args[0])
         
