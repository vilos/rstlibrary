from supervisor.supervisord import SupervisorStates
from supervisor.xmlrpc import Faults
from supervisor.xmlrpc import RPCError
from collections import deque

API_VERSION = '0.1'

SIZE_LIMIT = 1000

class BrokerNamespaceRPCInterface:
    """ A Supervisor RPC interface that provides the ability 
    to enqueue abritrary strings in the Supervisor instance.
    """

    def __init__(self, supervisord):
        self.supervisord = supervisord
        self.queue = deque()
        
    def _update(self, text):
        self.update_text = text # for unit tests, mainly

        state = self.supervisord.get_state()

        if state == SupervisorStates.SHUTDOWN:
            raise RPCError(Faults.SHUTDOWN_STATE)

        # XXX fatal state
        
    # RPC API methods

    def getAPIVersion(self):
        """ Return the version of the RPC API used by supervisor_broker

        @return string  version
        """
        self._update('getAPIVersion')
        return API_VERSION

    def size(self):
        """ Return a count of all items in the queue

        @return  integer   Count of items 
        """
        self._update('size')
        return len(self.queue)

    def put(self, cmd, arg=''):
        """ Put a tuple (cmd, arg) into the queue 

        @param  string cms   
        @param  string arg   
        @return boolean      true unless queue full
        """
        self._update('put')
        self._validateKey(cmd)

        if not isinstance(arg, str):
            why = 'Command arg must be a string'
            raise RPCError(Faults.INCORRECT_PARAMETERS, why)
        
        if self.size() >= SIZE_LIMIT:
            return False
        
        self.queue.appendleft([cmd, arg])
        return True

    def get(self):
        """ Remove and return a tuple from the queue.

        @return tuple   tuple of strings
        """
        self._update('get')
        if self.size() == 0:
            return False
        data = self.queue.pop()
        if data is None:
            raise RPCError(Faults.BAD_NAME)
        return data

    def clear(self):
        """ Clear the queue

        @return boolean  Always true unless error.
        """
        self._update('clear')
        self.queue.clear()
        return True

    def _validateKey(self, key):
        """ validate 'key' is suitable for a command name """
        if not isinstance(key, str) or (key == ''):
            why = 'cmd must be a non-empty string'
            raise RPCError(Faults.BAD_NAME, why)

def make_broker_rpcinterface(supervisord, **config):
    return BrokerNamespaceRPCInterface(supervisord)
