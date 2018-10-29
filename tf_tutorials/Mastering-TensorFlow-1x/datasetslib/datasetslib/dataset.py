import future, builtins, past, six
from builtins import super

from sklearn.preprocessing import StandardScaler as skpp_StandardScaler
import pandas as pd
import numpy as np

from .utils import nputil

class Dataset(object):
    def __init__(self,data=None):
        self.data = data
        self.y_onehot=False
        self.batch_size = 128
        self.batch_shuffle = False
        self.init_part()
        self.n_classes = 0

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data=data
        self.mldata = None  # if the data is refreshed, also init mldata to none

    @property
    def batch_size(self):
        return self._batch_size

    @batch_size.setter
    def batch_size(self, batch_size):
        self._batch_size=batch_size

    @property
    def batch_shuffle(self):
        return self._batch_shuffle

    @batch_shuffle.setter
    def batch_shuffle(self, batch_shuffle):
        self._batch_shuffle=batch_shuffle

    @property
    def y_onehot(self):
        return self._y_onehot

    @y_onehot.setter
    def y_onehot(self, y_onehot):
        self._y_onehot=y_onehot

    # this is where we store columnar data for ML
    @property
    def mldata(self):
        return self._mldata

    @mldata.setter
    def mldata(self, data=None):
        if data is None:
            self._mldata=None
        else:
            if isinstance(data,pd.DataFrame) or isinstance(data,pd.Series):
                self._mldata = data.values
            else:
                self._mldata = data
            self._mldata = self._mldata.astype(np.float32)
            if self._mldata.ndim==1:
                self._mldata = self._mldata.reshape(-1,1)
        self.scaler=None

    part_all = ['train','valid','test']

    @property
    def part_list(self):
        XY_list=[]
        for part in Dataset.part_all:
            if self.part[part] is not None:
                XY_list.append(part)
        return XY_list

    def check_part_list(self,parts = None):
        if parts is not None:
            for part in parts:
                if self.part[part] is None:
                    return False
        return True

    @property
    def X_list(self):
        X_list=[]
        for part in Dataset.part_all:
            if self.part['X_'+part] is not None:
                X_list.append('X_'+part)
        return X_list

    @property
    def Y_list(self):
        Y_list=[]
        for part in Dataset.part_all:
            if self.part['Y_'+part] is not None:
                Y_list.append('Y_'+part)
        return Y_list

    def part_print(self):
        for k, v in self.part.items():
            print(k, 'None' if v is None else v.shape)

    def init_part(self):
        self.part = {
            'X'        : None,
            'Y'        : None,
            'X_train'  : None,
            'Y_train'  : None,
            'X_valid'  : None,
            'Y_valid'  : None,
            'X_test'   : None,
            'Y_test'   : None,
            'train'    : None,
            'test'     : None,
            'valid'    : None,
        }
        self.index={
            'train'    : 0,
            'test'     : 0,
            'valid'    : 0,
        }

    @property
    def n_train(self):
        if self.part['Y_train'] is None:
            self._n_train = self.part['train'].shape[0]
        else:
            self._n_train = self.part['Y_train'].shape[0]
        return self._n_train

    @property
    def X_train(self):
        return self.part['X_train']

    @property
    def X_valid(self):
        return self.part['X_valid']

    @property
    def X_test(self):
        return self.part['X_test']

    @property
    def Y_train(self):
        retval = self.part['Y_train']
        if self.y_onehot:
            return nputil.onehot(retval)
        else:
            return retval

    @property
    def Y_valid(self):
        retval = self.part['Y_valid']
        if self.y_onehot:
            return nputil.onehot(retval)
        else:
            return retval

    @property
    def Y_test(self):
        retval = self.part['Y_test']
        if self.y_onehot:
            return nputil.onehot(retval)
        else:
            return retval

    @property
    def train(self):
        return self.part['train']

    @property
    def valid(self):
        return self.part['valid']

    @property
    def test(self):
        return self.part['test']

    def StandardizeX(self):
        X_list = self.X_list if self.part['X'] is None else self.X_list.append('X')

        if X_list:
            self.scaler=skpp_StandardScaler(copy=False)
            self.part[X_list[0]] = self.scaler.fit_transform(self.part[X_list[0]])
            for part in X_list[1:]:
                if self.part[part] is not None:
                    self.part[part] = self.scaler.transform(self.part[part])
        else:
            self.scaler=None

    def StandardizeInverseX(self,data=None):
        if data is None and self.scaler is not None:
            X_list = self.X_list if self.part['X'] is None else self.X_list.append('X')
            if X_list:
                for part in X_list:
                    if self.part[part] is not None:
                        self.part[part] = self.scaler.inverse_transform(self.part[part])
        else:
            return self.scaler.inverse_transform(data, copy=True)

    def reset_index(self, part='train'):
        self.index[part]=0

    # does not mutate x
    def shuffle_xy(self,x,y):
        assert len(x) == len(y), 'x and y are not of same length'
        indices = np.arange(len(x))
        np.random.shuffle(indices)
        if isinstance(x,list):
            x_ret = [x[i] for i in indices]
        elif isinstance(x,np.ndarray):
            x_ret = x[indices]
        else:
            print('Data type of X not understood in shuffle')
            x_ret = x

        if isinstance(y,list):
            y_ret = [y[i] for i in indices]
        elif isinstance(y,np.ndarray):
            y_ret = y[indices]
        else:
            print('Data type of Y not understood in shuffle')
            y_ret = y

        return x_ret, y_ret

    def next_batch(self, part='train'):
        if part in Dataset.part_all:
            xpart = 'X_'+part
            ypart = 'Y_'+part
            start = self.index[part] #self._index_in_batched_epoch
            n_rows = self.part[ypart].shape[0]

            # Shuffle for the first epoch
            if start == 0 and self.batch_shuffle:
                perm0 = np.arange(n_rows)

                #self.part[xpart] = self.part[xpart][perm0]
                self.part[xpart], self.part[ypart] = self.shuffle_xy(self.part[xpart], self.part[ypart])

            self.index[part] += self.batch_size
            if self.index[part] >= n_rows:
                self.reset_index(part)
                end = n_rows
            else:
                end = self.index[part]

            y_batch = self.part[ypart][start:end]

            if self.y_onehot:
                y_batch = nputil.onehot(y_batch, self.n_classes)
            else:
                y_batch = nputil.to2d(y_batch)

            return self.part[xpart][start:end], y_batch
        else:
            raise(ValueError('Invalid argument: ',part))

            # # Go to the next epoch
            # if start + batch_size > n_rows:
            #     # last epoch
            #     self._epochs_completed += 1
            #     # Get the rest examples in this epoch
            #     rest_num_examples = self._num_examples - start
            #     images_rest_part = self._images[start:self._num_examples]
            #     labels_rest_part = self._labels[start:self._num_examples]
            #     # Shuffle the data
            #     if shuffle:
            #         perm = np.arange(self._num_examples)
            #         np.random.shuffle(perm)
            #         self._images = self.images[perm]
            #         self._labels = self.labels[perm]
            #     # Start next epoch
            #     start = 0
            #     self._index_in_batched_epoch = batch_size - rest_num_examples
            #     end = self._index_in_batched_epoch
            #     images_new_part = self._images[start:end]
            #     labels_new_part = self._labels[start:end]
            #     return np.concatenate((images_rest_part, images_new_part), axis=0) , numpy.concatenate((labels_rest_part, labels_new_part), axis=0)
            # else:
            #
            #     return self._images[start:end], self._labels[start:end]

    def tvt_split(self, train_size=0.75, val_size=0):

        results=[]
        if self._mldata is None:
            raise ValueError('No ml data found')

        if train_size > 1 or train_size <=0:
            raise ValueError('train_size has to be between 0 and 1')

        if val_size >= 1 or val_size < 0:
            raise ValueError('val_size has to be between 0 and 1')

        if train_size + val_size > 1:
            raise ValueError('train_size + val_size has to be between 0 and 1')

        N = self._mldata.shape[0]

        train_size = int(N * train_size)
        val_size = int(N * val_size)
        test_size = N - train_size - val_size

        if(train_size>0):
            self.part['train'] = self._mldata[0:train_size]
            results.append(self.part['train'])
        else:
            self.part['train'] = None

        if(val_size>0):
            self.part['valid'] = self._mldata[train_size:train_size+val_size]
            results.append(self.part['valid'])
        else:
            self.part['valid'] = None

        if(test_size>0):
            self.part['test'] =  self._mldata[train_size+val_size:N]
            results.append(self.part['test'])
        else:
            self.part['test'] = None
        return results