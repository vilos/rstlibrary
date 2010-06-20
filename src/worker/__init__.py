"""
worker implementation for supervisor_broker queue

supervisor_broker is a plugin for supervisord that implements simple queue
input - xmlrpc or supervisorctl cli

dispatcher is a process running under supervisord and
listening to REMOTE_COMMUNICATION events

xmlrpc-client  - testing only

"""