#!/usr/bin/env python
from apscheduler.scheduler import Scheduler
from datetime import datetime
from time import sleep
from memcheck import check

import signal

# Start the scheduler
sched = Scheduler()
options = {'misfire_grace_time': '2',
           'daemonic': 'false'}
sched.configure(options)

stop = 0
# KeyboardInterrupt handler
def shutdown(signl, frme):
    global stop
    global sched
    stop = 1
    sched.shutdown(10)
    #log.info('Catched signal %r. Processing will stop.', signl)
    return 0

signal.signal(signal.SIGINT, shutdown )


def job_function():
    #print "Hello World"
    dt = datetime.now()
    print dt.strftime("%d. %B %Y %H:%M:%S")

# Schedule job_function to be called every two hours
#sched.add_interval_job(job_function, seconds=10, repeat=0)
sched.add_interval_job(check, seconds=180, repeat=0)
sched.start()

while (not stop):
    sleep(10)