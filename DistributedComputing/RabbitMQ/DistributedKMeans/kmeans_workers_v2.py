

#run this code with "celery -A kmeans_workers_v2 worker --loglevel=info --concurrency=4" on the worker machines

#Then this machine will become a worker, and will be able to run the app task, 
#i.e. the kmeans_tasks function, whenever the broker requests it.

import celery
import numpy as np
from copy import deepcopy
import json
import random

import os

 
# Make sure that the 'myguest' user exists with 'myguestpwd' on the RabbitMQ server and your load balancer has been set up correctly.
# My load balancer address is'RabbitMQLB-8e09cd48a60c9a1e.elb.us-east-2.amazonaws.com'. 
# Below you will need to change it to your load balancer's address.

app = celery.Celery('kmeans_workers',
                       broker='amqp://myguest:myguestpwd@RabbitMQLB-8e09cd48a60c9a1e.elb.us-east-2.amazonaws.com',
                       backend='rpc://myguest:myguestpwd@RabbitMQLB-8e09cd48a60c9a1e.elb.us-east-2.amazonaws.com')

iter =0
C=[]
X=[]
n_clusters = 0
n_features = 0
#worker_name='worker_'+str(random.randint(1, 10000))
#worker_name = os.getpid()

@app.task
def kmeans_tasks(task, **kwargs):
    json_dump=kwargs['json_dump']
    json_load = json.loads(json_dump)
    global C, X, n_clusters, n_features
    if task=='EM_step':
        C = np.asarray(json_load["C"])
        results=EM_step(C,X)
        return results
    elif task =='data_to_workers':
        C = np.asarray(json_load["C"])
        X = np.asarray(json_load["X"])
        n_clusters = json_load["n_clusters"]
        n_features = json_load["n_features"]
        print('n_clusters:', n_clusters)
        print('n_features:', n_features)
        return 'success'
    else:
        raise ValueError('undefined task')

# Euclidean Distance Caculator
def dist(a, b, ax=1):
    return np.linalg.norm(a - b, axis=ax)
        
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.int64): 
            return int(obj)
        return json.JSONEncoder.default(self, obj)

def data_to_workers(C,X):
    print('*** we are sending data to the workers ***')
    #print('C',C)
    #print("shape of X:", len(X))
    for i in range(len(X)):
        #print(X[i])
        distances = dist(X[i]["points"], C)
        cluster = np.argmin(distances)
        X[i]["label"] = cluster
        #print(X[i].label)
    print(" *** Labels updated. E-step done ***")    
    return json.dumps({'X':deepcopy(X)},cls=NumpyEncoder)    
    
def EM_step(C,X):
    global iter
    print('*** we are in the E-Step ***')
    iter=iter+1
    print("E step iter:",iter)
    
    for i in range(len(X)):
        #print(X[i])
        distances = dist(X[i]["points"], C)
        cluster = np.argmin(distances)
        X[i]["label"] = cluster
        #print(X[i].label)
    print(" *** Labels updated. E-step done ***")    
    
    print('*** we are in the M-Step ***')
    C = [None]*np.int(n_clusters)
    num_points=[None]*np.int(n_clusters)
    
    for i in range(n_clusters):
        points = [X[j]["points"] for j in range(len(X)) if X[j]["label"] == i]
        C[i] = np.mean(points, axis=0) 
        num_points[i]=len(points)
        
        if (np.any(np.isnan(C[i]))):
            C[i]=np.zeros(n_features)
            num_points[i]=0
    
    print(" *** Cluster centers updated. M-step done ***")        
    return json.dumps({'C':deepcopy(C), 'num_points':deepcopy(num_points)},cls=NumpyEncoder)


