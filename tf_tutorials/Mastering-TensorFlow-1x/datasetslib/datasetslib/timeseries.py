from .dataset import Dataset
from . import util
import numpy as np

class TimeSeriesDataset(Dataset):
    def __init__(self, data=None):
        Dataset.__init__(self, data)

    # this function assumes there is no missing data
    # this function sets mldata and data to none after the split is done to save space
    #TODO: Implement valid dataset breakup
    def train_test_split_dayofweek(self, train_days:list=[0,1,2,3],test_days:list=[4], X_weeks=1,Y_weeks=1, col_names=None):

        if self._data is None:
            raise ValueError('No _data found')

        all_days = set(train_days) | set(test_days)
        # all_days.sort()
        # print(all_days)
        if col_names is None:
            col_names = self._data.columns.tolist() # get all the column names

        # get the days falling in the range
        min_date = self._data.index.min()
        max_date = self._data.index.max()
        first_day = util.next_weekday(min_date, min(all_days)) # 0 = Monday, 1=Tuesday, 2=Wednesday...
        last_day = util.next_weekday(max_date,max(all_days),next=False)
        # print('min_date:',min_date)
        # print('max_date:',max_date)
        # print('First Monday:',first_monday)
        # print('Last Friday:',last_friday)
        # print(col_names)
        # print(self._data.index.dayofweek in all_days)
        day_df = self._data.loc[(self._data.index.dayofweek.isin(all_days)) & (self._data.index >= first_day) &
                                (self._data.index <= last_day), col_names]

        # self.mldata = day_df.values.astype(np.float32)
        # self.mldata_col_names = col_names

        self.part['train'] = day_df.loc[day_df.index.dayofweek.isin(train_days)].values.astype(np.float32)
        self.part['test'] =  day_df.loc[day_df.index.dayofweek.isin(test_days)].values.astype(np.float32)
        self.part['valid'] = None

        #print(self.mldata_cols)
        #print(self.part['train'].dtype)
        #print('train shape:',self.part['train'].shape)
        results=[]
        results.append(self.part['train'])
        results.append(self.part['test'])

        #print(self.part['train'][:5])

        self.data=None
        self.mldata=None
        return results


    # in case of timeseries, always split test train first
    def train_test_split(self, train_size=0.75, val_size=0):

        results=[]
        if self._mldata is None:
                raise ValueError('No timeseries found')

        if train_size > 1 or train_size <=0:
            raise ValueError('train_size has to be between 0 and 1')

        if val_size >= 1 or val_size < 0:
            raise ValueError('val_size has to be between 0 and 1')

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


    # n_tx and n_ty are number of x and y timesteps respectively,
    # h is prediction horizon for direct strategy
    # returns input series : {t-n_tx,...,t}, output series : {t+h,...,t+h+n_ty}
    # x_idx is the list of columns that would be used as input or feature
    # y_idx is the list of columns that would be used as output or target
    def mvts_to_xy(self, n_tx=1, n_ty=1, x_idx=None, y_idx=None, h=1, ts_list=None):

        if ts_list is not None:
            if not self.check_part_list(ts_list):
                raise ValueError('the part you have asked to split is not available')
        else:
            ts_list = self.part_list
            if not ts_list:
                raise ValueError('Timeseries has not been split into train, valid, test. Run one of the train_test_split method first')

        ts_cols = 1 if self.part[ts_list[0]].ndim==1 else self.part[ts_list[0]].shape[1]

        if x_idx is None:
            x_idx = range(0,ts_cols)
        if y_idx is None:
            y_idx = range(0,ts_cols)

        self.x_idx = x_idx
        self.y_idx = y_idx
        self.y_cols_x_idx = [x_idx.index(i) for i in y_idx]

        n_x_vars = len(x_idx)
        n_y_vars = len(y_idx)




        #TODO: Validation of other options

        result = []

        # as of now we are only converting the training and test set
        # train set is to be converted based on strategy
        # for single step ahead prediction : input series : {t-n_tx,...,t}, output series : {t+1}
        # for multi step ahead :
        #   iterative : input series : {t-n_tx,...,t}, output series : {t+1} and columns of out_vec in input series
        #   direct : input series : {t-n_tx,...,t}, output series : {t+h}
        #   MIMO : input series : {t-n_tx,...,t}, output series : {t+1,...,t+n_ty}
        # test set is always going to be : input series : {t-n_tx,...,t}, output series : {t+1,...,t+n_ty}


        for ts_part in Dataset.part_all:
            if ts_part not in ts_list:
#                self.part['X_'+ts_part]=None
#                self.part['Y_'+ts_part]=None
                pass
            else:
                ts = self.part[ts_part]
                #print(ts)

                ts_rows = ts.shape[0]
                #print(ts_rows)
                n_rows = ts_rows - n_tx - (n_ty - 1) - (h - 1)
                #print(n_rows)
                dataX=np.empty(shape=(n_rows, n_x_vars * n_tx), dtype=np.float32)
                dataY=np.empty(shape=(n_rows, n_y_vars * n_ty), dtype=np.float32)

                #print(dataX.shape)
                #print(dataY.shape)

                #print(ts.shape)
                #print(x_idx)

                # input sequence x (t-n_tx, ... t)

                from_col = 0
                #print(from_col)
                #print(from_col+n_x_vars)

                for i in range(n_tx, 0, -1):
                    dataX[:,from_col:from_col+n_x_vars]= util.shift(ts[:,x_idx],i)[n_tx:n_rows+n_tx]
                    from_col = from_col+n_x_vars

                # forecast sequence (t+h, ... t+h+n_ty)
                from_col = 0
                for i in range(0, n_ty):
                    #y_cols.append(shift(ts,-i))
                    dataY[:,from_col:from_col+n_y_vars]= util.shift(ts[:,y_idx],-(i+h-1))[n_tx:n_rows+n_tx]
                    from_col = from_col + n_y_vars

                result.append(dataX)
                result.append(dataY)

                self.part['X_'+ts_part]=dataX
                self.part['Y_'+ts_part]=dataY

        return result


