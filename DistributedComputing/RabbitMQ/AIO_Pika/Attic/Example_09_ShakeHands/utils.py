import numpy as np
import json

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.int64): 
            return int(obj)
        elif isinstance(obj, np.float64):
            return float(obj)
        return json.JSONEncoder.default(self, obj)
