import numpy as np
import unittest
from datasetslib.timeseries import TimeSeriesDataset
from ddt import ddt,data,unpack


# def mvts_to_xy(self, n_x=1, n_y=1, x_idx=None, y_idx=None, h=1):
#    def test_mvts_to_xy_1(self):
#        print('Testing mvts_to_xy_1')
#        self.tsd.data = self.data1
#        self.tsd.train_test_split(train_size=1)
#        self.tsd.mvts_to_xy(n_x=1,n_y=1)
#        X_data1 = np.ndarray([0, 1, 2, 3, 4, 5, 6, 7, 8],dtype=np.float32)
#        Y_data1 = np.ndarray([1, 2, 3, 4, 5, 6, 7, 8, 9],dtype=np.float32)
#        print(X_data1)
#        print(self.tsd.X_train)
#        assert np.allclose(X_data1,self.tsd.X_train)

data1D = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]).reshape(-1,1)
data2D = np.array([[0,1,2,3,4,5,6,7,8,9],[10,11,12,13,14,15,16,17,18,19]]).transpose()

@ddt
class TestTimeSeriesDataset(unittest.TestCase):

    def setUp(self):
        print(self._testMethodName)
        print(self.id())
        self.tsd = TimeSeriesDataset()

    def tearDown(self):
        pass

    @data(data1D, data2D)
    def test_train_test_split_train1(self,value):
        self.tsd.mldata = value
        self.tsd.train_test_split(train_size=1)
        train_data = np.array(value)
        #print(train_data1D,self.tsd.train)
        assert np.allclose(train_data,self.tsd.train)


  #def mvts_to_xy(self, n_x=1, n_y=1, x_idx=None, y_idx=None, h=1):
    @unpack
    @data(
          # iterative or recursive strategy n_x = input window
          {'data': data1D, 'n_x': 1, 'n_y': 1, 'h':1,
           'X': np.array([0, 1, 2, 3, 4, 5, 6, 7, 8],dtype=np.float32).reshape(-1,1),
           'Y': np.array([1, 2, 3, 4, 5, 6, 7, 8, 9],dtype=np.float32).reshape(-1,1)
           },
          {'data': data2D, 'n_x': 1, 'n_y': 1, 'h':1,
           'X': np.array([[0, 10],[1,11], [2,12], [3,13],[4,14],[5,15], [6,16], [7,17],[8,18]],dtype=np.float32),
           'Y': np.array([[1,11], [2,12], [3,13],[4,14],[5,15], [6,16], [7,17],[8,18],[9,19]],dtype=np.float32)
           },
          {'data': data2D, 'n_x': 2, 'n_y': 1, 'h':1,
           'X': np.array([[0, 10,1,11],[1,11,2,12], [2,12,3,13], [3,13,4,14],[4,14,5,15],[5,15,6,16], [6,16,7,17], [7,17,8,18]],dtype=np.float32),
           'Y': np.array([[2,12], [3,13],[4,14],[5,15], [6,16], [7,17],[8,18],[9,19]],dtype=np.float32)
           },
          # MO strategy n_y = output window
          {'data': data2D, 'n_x': 1, 'n_y': 2, 'h':1,
           'X': np.array([[0, 10],[1,11], [2,12], [3,13],[4,14],[5,15], [6,16], [7,17]],dtype=np.float32),
           'Y': np.array([[1,11,2,12], [2,12,3,13], [3,13,4,14],[4,14,5,15],[5,15,6,16], [6,16,7,17], [7,17,8,18],[8,18,9,19]],dtype=np.float32)
           },
          {'data': data2D, 'n_x': 2, 'n_y': 2, 'h':1,
           'X': np.array([[0, 10,1,11],[1,11,2,12], [2,12,3,13], [3,13,4,14],[4,14,5,15],[5,15,6,16], [6,16,7,17]],dtype=np.float32),
           'Y': np.array([[2,12,3,13], [3,13,4,14],[4,14,5,15],[5,15,6,16], [6,16,7,17], [7,17,8,18],[8,18,9,19]],dtype=np.float32)
           },
          # increase h for direct strategy i.e. h=2 here
          {'data': data2D, 'n_x': 2, 'n_y': 2, 'h':2,
           'X': np.array([[0, 10,1,11],[1,11,2,12], [2,12,3,13], [3,13,4,14],[4,14,5,15],[5,15,6,16]],dtype=np.float32),
           'Y': np.array([[3,13,4,14],[4,14,5,15],[5,15,6,16], [6,16,7,17], [7,17,8,18],[8,18,9,19]],dtype=np.float32)
           },
          {'data': data1D, 'n_x': 1, 'n_y': 1, 'h':2,
           'X': np.array([0, 1, 2, 3, 4, 5, 6, 7],dtype=np.float32).reshape(-1,1),
           'Y': np.array([2, 3, 4, 5, 6, 7, 8, 9],dtype=np.float32).reshape(-1,1)
           },
          {'data': data2D, 'n_x': 1, 'n_y': 1, 'h':2,
           'X': np.array([[0, 10],[1,11], [2,12], [3,13],[4,14],[5,15], [6,16], [7,17]],dtype=np.float32),
           'Y': np.array([[2,12], [3,13],[4,14],[5,15], [6,16], [7,17],[8,18],[9,19]],dtype=np.float32)
          }
          )
    def test_mvts_to_xy(self,data,X,Y,n_x,n_y,h):
        self.tsd.mldata = data
        self.tsd.train_test_split(train_size=1)
        self.tsd.mvts_to_xy(n_tx=n_x, n_ty=n_y, h=h)
        print('Y\n',Y)
        print('X_train\n',self.tsd.X_train)
        print('Y_train\n',self.tsd.Y_train)
        assert np.allclose(X,self.tsd.X_train)
        assert np.allclose(Y,self.tsd.Y_train)