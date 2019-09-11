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
    
    results=tmpip+' process_name: '+process_name+' process_index: '+process_index+' pid: '+str(os.getpid())+' message: '+message+' '+'**'
    print(results)
    
    time.sleep(random.uniform(0,7)) # Let us wait some random time to simulate that some jobs might take longer time
    
    return 'Response from worker: '+results


#run this code with "celery -A test worker --loglevel=info --concurrency=3". 
#Then this machine will become a worker, and will be able to run the app task, i.e. the echo function, whenever the broker requests it.

# The echo function will be run by these commands on a remote machine:

# from test import echo
# res = echo.delay('Python rocks!'); print(type(res)); print(res)
# res.result