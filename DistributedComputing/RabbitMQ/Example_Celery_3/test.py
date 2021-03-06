import celery
from billiard import current_process
import time
import math
import socket
import numpy as np
import os
import random
# First we setup a connection to the message broker:

# Make sure that the 'myguest' user exists with 'myguestpwd' on the RabbitMQ server, and the 
# 'PROD-JOB-844fd7d2202ac4da.elb.us-east-2.amazonaws.com' address from the load balancer has been set up correctly.

app = celery.Celery('test',
                        broker='amqp://myguest:myguestpwd@PROD-JOB-844fd7d2202ac4da.elb.us-east-2.amazonaws.com',
                        backend='amqp://myguest:myguestpwd@PROD-JOB-844fd7d2202ac4da.elb.us-east-2.amazonaws.com')

# Let us use the @app.task decorator on our echo function. It will allow us to call echo.delay() on the server remotely

@app.task
def echo(message):
    
    p = current_process()
    
    
    #print(current_process()._name)
    #print(current_process().index)
    
    process_name=current_process()._name
    try:
        process_index=str(current_process().index)
    except:
        process_index='_none_'
    
    tmpip= socket.gethostbyname(socket.gethostname())
    
    results=tmpip+' process_name: '+process_name+' process_index: '+process_index+' os_pid: '+str(os.getpid())+' message: '+message+' '+'**'
    print(results)
    
    time.sleep(random.uniform(0,7)) # Let us wait some random time to simulate that some jobs might take longer time
    
    return 'Response from worker: '+results

# One each of the worker machines you will need to run first:
#!sudo rabbitmqctl add_user myguest myguestpwd
#!sudo rabbitmqctl set_permissions -p / myguest "." "." ".*"


# then run this code with 
# "celery -A test worker --loglevel=info --concurrency=3" on worker machine 1
# "celery -A test worker --loglevel=info --concurrency=2" on worker machine 2
# We can set up different concurrency level on each worker machine
