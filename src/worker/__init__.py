"""
worker implementation for vsbroker queue

vsbroker is a server that implements simple command queue

dispatcher is a process running under supervisord and
listening to TICK events, querying the queue and dispatching commands

invalidate, svnup - command executers
jsonrpc  - json client lib
indexer / future indexer

updater, process - deprecated
"""