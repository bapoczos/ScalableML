

#run this code with "celery -A linear_regression_workers worker --loglevel=info --concurrency=1" on the 4 worker machines

#Then these machines become workers, and will be able to run the app task, 
#i.e. the kmeans_tasks function, whenever the broker requests it.

import celery
import numpy as np
from copy import deepcopy
import json
import random
import matplotlib.pyplot as plt

import os

 
# Make sure that the 'myguest' user exists with 'myguestpwd' on the RabbitMQ server and your load balancer has been set up correctly.
# My load balancer address is'RabbitMQLB-8e09cd48a60c9a1e.elb.us-east-2.amazonaws.com'. 
# Below you will need to change it to your load balancer's address.

app = celery.Celery('kmeans_workers',
                       broker='amqp://myguest:myguestpwd@RabbitMQLB-8e09cd48a60c9a1e.elb.us-east-2.amazonaws.com',
                       backend='rpc://myguest:myguestpwd@RabbitMQLB-8e09cd48a60c9a1e.elb.us-east-2.amazonaws.com')


@app.task
def lin_regression_tasks(**kwargs):
    json_dump=kwargs['json_dump']
    json_load = json.loads(json_dump)
    
    XY = np.asarray(json_load["XY"]) 
    x = XY[0]
    y = XY[1]
    
    A = calc_A(x)
    
    term1 = calc_AT_times_A(A)
    term2 = calc_AT_times_y(A,y)
    
    return json.dumps({'term1':term1, 'term2':term2},cls=NumpyEncoder)
    
        
def calc_A(x):
    A = np.hstack([x,np.ones_like(x)])
    return A

def calc_AT_times_A(A):
    term1 = np.matmul(A.T,A)
    return term1

def calc_AT_times_y(A,y):
    term2 = np.matmul(A.T,y)
    return term2

def solve_lin_regession(x,y):
    
    A = calc_A(x)
    
    term1 = calc_AT_times_A(A)
    term2 = calc_AT_times_y(A,y)
    theta = np.matmul(np.linalg.inv(term1),term2)
    
    yhat=np.matmul(A,theta)
    return yhat
    
        
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.int64): 
            return int(obj)
        return json.JSONEncoder.default(self, obj)

