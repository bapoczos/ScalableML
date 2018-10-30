from .timeseries import TimeSeriesDataset

import numpy as np

class IAP(TimeSeriesDataset):
    def __init__(self):
        TimeSeriesDataset.__init__(self)
        self.dataset_name='iap'
        self.source_url='https://datamarket.com/data/set/22u3/international-airline-passengers-monthly-totals-in-thousands-jan-49-dec-60#'
        self.source_files=['cifar-10-python.tar.gz']
        self.dataset_home=os.path.join(datasets_root,self.dataset_name)

    def load_data(self):

