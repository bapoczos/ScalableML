
# source activate tensorflow_p27

#run this code with "celery -A imagesearch_workers worker --loglevel=info" on the worker machines

#Then this machine will become a worker, and will be able to run the app task, 
#i.e., the imagesearch_tasks or upload_data functions, whenever the server requests it.

import celery
import numpy as np
from copy import deepcopy
import json
from pyflann import * # I use pyflann data structure. You any that you like
import time
from scipy.spatial import distance

# change this to your load balancers!!!

app = celery.Celery('imagesearch_workers',
                        broker='amqp://myguest:myguestpwd@PROD-JOB-844fd7d2202ac4da.elb.us-east-2.amazonaws.com',
                        backend='amqp://myguest:myguestpwd@PROD-JOB-844fd7d2202ac4da.elb.us-east-2.amazonaws.com')

#Global variables
#Use any global variables that you will need

flann_kdtree = FLANN()
flann_linear = FLANN()
features_train=[]
params_linear =[]
params_kdtree =[]
mydata_loaded =[]
 
@app.task
def upload_data(**kwargs):
    global upload_nums
    global params_kdtree
    global params_linear
    global features_train
    global flann_linear
    global flann_kdtree
    global mydata_loaded
    
    json_dump=kwargs['json_dump']
    json_load = json.loads(json_dump)
    mydata_loaded = np.asarray(json_load["mydata"])
    print(len(mydata_loaded))
    print(mydata_loaded[0]['path'])
    
    print('*** data uploaded ***')
    
   
    dim=len(mydata_loaded[0]['features'])
    features_train=np.zeros([len(mydata_loaded),dim])
    for iter in range(len(mydata_loaded)):
        features_train[iter,:]=mydata_loaded[iter]['features']

    # ****************************************
    #    *** you will need to complete this part ***
    # Create a near neighbour data structure here from the feature_train feature vectors!
    # ********************************************
    
    return

@app.task
def imagesearch_tasks(**kwargs):
    global upload_nums
    global params_kdtree
    global params_linear
    global features_train
    global flann_linear
    global flann_kdtree
    global mydata_loaded
    
    num_results=5
    
    json_dump=kwargs['json_dump']
    json_load = json.loads(json_dump)
    
    query_feature = np.asarray(json_load["query_feature"])
    
    results=[]
    
    # ****************************************
    #    *** you will need to complete this part ***
    # Find k nearest neighbours that are closest to your query vector
    # ********************************************
    
    
    return results

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


