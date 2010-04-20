from supervisor.supervisorctl import ControllerPluginBase
import pprint
import shlex

class BrokerControllerPlugin(ControllerPluginBase):
    def __init__(self, controller):
        self.ctl   = controller     
        self.queue = controller.get_server_proxy('broker')

    # queue_clear

    def do_queue_clear(self, args):
        if args:
            return self.help_queue_clear()
        self.queue.clear()

    def help_queue_clear(self):
        self.ctl.output("queue_clear\t"
                        "Clear all items from the queue.")

    # queue_count

    def do_queue_size(self, args):
        if args:
            return self.help_queue_size()
        size = self.queue.size()
        self.ctl.output(str(size))

    def help_queue_size(self):
        self.ctl.output("queue_size\t"
                        "Get a count of all items in the queue.")

    # queue_get

    def do_queue_get(self, args):
        if args:
            return self.help_queue_get()       
        value = self.queue.get()
        self._pprint(value)

    def help_queue_get(self):
        self.ctl.output("queue_get \t"
                        "Remove and return an item from the queue..")

    # queue_put

    def do_queue_put(self, args):
        if not args:
            return self.help_queue_put()
        splitted = shlex.split(args)
        if len(splitted) > 2:
            return self.help_queue_put()
        #key, value = splitted
        self.queue.put(*splitted)        

    def help_queue_put(self): 
        self.ctl.output("queue_put <key> <value>\t"
                        "put <value> in the queue at <key>.")


    def _pprint(self, what):
        pprinted = pprint.pformat(what)
        self.ctl.output(pprinted)        


def make_broker_controllerplugin(controller, **config):
    return BrokerControllerPlugin(controller)
