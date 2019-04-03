
#run this code with "celery -A test_worker_2 worker --loglevel=info  --concurrency=2" on the 2nd worker machine
#Then this machine will become a worker, and will be able to run the app task, 

import celery
import numpy as np

from billiard import current_process
import json
import time
import math

app = celery.Celery('test_workers',
                        broker='amqp://myguest:myguestpwd@PROD-JOB-844fd7d2202ac4da.elb.us-east-2.amazonaws.com',
                        backend='amqp://myguest:myguestpwd@PROD-JOB-844fd7d2202ac4da.elb.us-east-2.amazonaws.com')


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
    results='file2_'+current_process()._name+'_'+str(current_process().index)
    results=results+'_'+msg+'_'+tmpvar+'_'+timestr()
    print(results)
    
    print(time.time())
    
    print('***************')
    messages.append(results)
    return messages
    
        
