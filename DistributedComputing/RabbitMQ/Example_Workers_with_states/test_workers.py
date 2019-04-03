
#run this code with "celery -A test_workers worker --loglevel=info  --concurrency=3" (or --concurrency=4) 
#Then this machine will become a worker, and will be able to run the app task, 

import celery
import numpy as np

from billiard import current_process
import json
import time
import math
import socket

#app = celery.Celery('test_workers',
#                        broker='amqp://barnabas:barnabaspwd@PROD-JOB-844fd7d2202ac4da.elb.us-east-2.amazonaws.com',
#                        backend='amqp://barnabas:barnabaspwd@PROD-JOB-844fd7d2202ac4da.elb.us-east-2.amazonaws.com')

app = celery.Celery('test_workers',
                        broker='amqp://barnabas:barnabaspwd@BarnabasBalancer-406f3065f2a02a86.elb.us-east-2.amazonaws.com',
                        backend='amqp://barnabas:barnabaspwd@BarnabasBalancer-406f3065f2a02a86.elb.us-east-2.amazonaws.com')


import os



messages=[]

def timestr():
    tmptime0=time.time()
    tmptime=tmptime0/1000
    return str(math.floor(100000*(tmptime-math.floor(tmptime))))

@app.task
def message_to_workers1(msg):
    global messages    
    
    p = current_process()
    print(current_process()._name)
    print(current_process().index)
    
    tmpvar= str(int(1000*np.random.rand()))
    tmpip= socket.gethostbyname(socket.gethostname())
    results=tmpip+'_'+current_process()._name+'_'+'**'+str(os.getpid())+'**'
    results=results+'_'+msg+'_'+tmpvar+'_'+timestr()+'_'+'****'
    print(results)
    
    print(time.time())
    print(os.getpid())
    print('***************')
    messages.insert(0, results)
    messages=messages[0:2]
    #messages.append(results)
    time.sleep(0.2)
    return messages

@app.task
def message_to_workers2(msg):
    global messages    
    
    p = current_process()
    print(current_process()._name)
    #print(current_process().index)
    
    old_messages = messages
    tmpvar= str(int(1000*np.random.rand()))
    tmpip= socket.gethostbyname(socket.gethostname())
    results=tmpip+'_'+current_process()._name+'_'+'**'+str(os.getpid())+'**'
    results=results+'_'+msg+'_'+tmpvar+'_'+timestr()+'_'+'****'
    print(results)
    
    print(time.time())
    
    print('***************')
    old_messages.insert(0, results)
    old_messages=old_messages[0:2]
    #messages.append(results)
    time.sleep(0.2)
    return old_messages

        
