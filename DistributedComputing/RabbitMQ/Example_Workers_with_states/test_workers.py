

#run this code with "celery -A test_workers worker --loglevel=info" on the worker machines

#Then this machine will become a worker, and will be able to run the app task, 

import celery
import numpy as np
#from copy import deepcopy

from billiard import current_process
import json
import time

app = celery.Celery('kmeans_workers',
                        broker='amqp://myguest:myguestpwd@PROD-JOB-844fd7d2202ac4da.elb.us-east-2.amazonaws.com',
                        backend='amqp://myguest:myguestpwd@PROD-JOB-844fd7d2202ac4da.elb.us-east-2.amazonaws.com')


@app.task
def message_to_workers1(msg):
    
    results = 'None'
    p = current_process()
    print(current_process()._name)
    print(current_process().index)
    
    tmpvar= str(int(1000*np.random.rand()))
    results=results+'_'+current_process()._name+'_'+str(current_process().index)
    
    results=results+'_'+msg+'_'+tmpvar+'_'+str(time.time())
    print(results)
    
    print(time.time())
    return results
    
        
