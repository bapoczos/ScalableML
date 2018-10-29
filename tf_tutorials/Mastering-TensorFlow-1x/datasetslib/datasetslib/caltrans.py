import os
import pandas as pd
import numpy as np
from datetime import datetime
import glob
from . import util

class CalTrans():

    orig_agg_col_names = ['dt','segment','district','freeway','direction_travel','lane_type',
                         'segment_length','samples','percent_observed','vcount','average_occupancy','vspeed']

    #df_agg_column_names = ['dt','segment','district','freeway','direction_travel','lane_type',
    #                       'segment_length','samples','percent_observed','vcount','average_occupancy','vspeed']

    orig_agg_col_dtypes = [np.str, np.str, np.str, np.str, np.str,         np.str,
                            np.str,           np.str,   np.float32,       np.float32, np.float32, np.float32]
    df_pp_agg_col_names=['dt','freeway','direction_travel','lane_type','segment_length','samples',
                            'percent_observed','vcount','average_occupancy','vspeed']
    df_pp_agg_col_dtypes = [np.str,np.str, np.str,         np.str,    np.float32,           np.float32,
                               np.float32,       np.float32, np.float32, np.float32]

    def __init__(self):
        from . import datasets_root
        super().__init__()
        self.dataset_name='caltrans'
        self.dataset_home=os.path.join(datasets_root,self.dataset_name)

    def preprocess_agg_files(self, source_folder, target_folder=None, col_names = None):
        """

        :param source_folder:
        :param target_folder:
        :param col_names:

        1. read the list of files

            The file names are in this format :
            d05_text_station_5min_2017_01_26.txt.gz
            d05_text_station_raw_2017_01_07.txt.gz
            d03_text_station_5min_2017_01_02.txt.gz

            d03 - district
            text_station - type, location
            5min, raw = 0,5,10,15 min
            yyy_mm_dd = YY,MM,DD

        2. filter by col_names if provided
        3. save by agg_period / district / segment / yy-mm-dd.gz

        :return:
        """

        if target_folder is None:
            target_folder = self.dataset_home

        if col_names is None:
            col_names = CalTrans.orig_agg_col_names

        col_idx=[CalTrans.orig_agg_col_names.index(i) for i in col_names]
        col_dtypes = dict([(CalTrans.orig_agg_col_names[i],CalTrans.orig_agg_col_dtypes[i]) for i in col_idx])

        #datafiles_df = self.list_original_datafiles(sourceFolder)

#        col_names=['dt','segment','freeway','direction_travel','lane_type','segment_length','samples','percent_observed','vcount','average_occupancy','vspeed']

#        column_names = CalTrans.df_agg_column_names
#        column_dtypes = CalTrans.df_agg_column_dtypes

        #print(self.datafiles_df)
        root_files = [[root,files] for root,dirs,files in os.walk(source_folder) if files]

        for root,filenames in root_files:
            if filenames:
                # current logic only handles 5 min
                if ('5min' in root):
                    print('processing {} files from {}'.format(len(filenames),root))
                    datafiles_df = pd.DataFrame([x.split('_') for x in filenames],
                                                columns=['district','type','location','agg_period','yy','mm','dd']
                                                )
                    # remove 'min' from minutes
                    datafiles_df['agg_period']=datafiles_df['agg_period'].str.extract('(\d+)',expand=False).fillna(0)
                    # remove .txt.gz from the dd part
                    datafiles_df['dd']=datafiles_df['dd'].str[:2]


                    datafiles_df['filename']=filenames

                    for _,datafile in datafiles_df.iterrows():
                        filename = os.path.join(root, datafile['filename'])
                        df = pd.read_csv(filename, header=None, usecols = col_idx, parse_dates=[0],
                                         infer_datetime_format=True, names = col_names, dtype = col_dtypes)
                        df.drop(columns=['district'], axis=1, inplace=True)
                        segment_list = df['segment'].unique().tolist()

                        for segment in segment_list:
                            segment_df=df.loc[df['segment']==segment,df.columns != 'segment']

                            dirname = os.path.join(target_folder,
                                                   datafile['agg_period'],
                                                   datafile['district'],
                                                   segment
                                                   )
                            if not os.path.exists(dirname):
                                os.makedirs(dirname)
                            filename = os.path.join(dirname,'{0}_{1}_{2}.csv.gz'.format(datafile['yy'],
                                                                                        datafile['mm'],
                                                                                        datafile['dd']))
                            segment_df.to_csv(filename,
                                              header=False,
                                              index=False,
                                              compression='gzip'
                                              )
                    print('processed to {}'.format(target_folder))
            else:
                print('No files at {}'.format(root))

    def find_missing_data(self, data_folder):


        root_files = [[root,files] for root,dirs,files in os.walk(data_folder) if files]


    """
    days_list : 0 - Monday
    """
    def read_pp_data(self,date_from=None,date_to=None, days_list=[0,1,2,3,4,5,6], district='d03', segment_list=None, agg_period=5, col_list=['vspeed']):
        # first make a list of files to be read
        # check if district folder exists
        data_folder = os.path.join(self.dataset_home,
                               str(agg_period),
                               district)

        if not os.path.exists(data_folder):
            raise ValueError('{0} path does not exist'.format(data_folder))

        if segment_list is None:
            # build a list of all segments in the district
            fglob = data_folder + '/s*'
            segment_dirs = glob.glob(fglob)
            segment_list = [x.split('/')[-1] for x in segment_dirs]

        self.segment_list = segment_list

        segment_dirs=[]
        for segment in segment_list:
            seg_folder = os.path.join(data_folder,segment)
            if not os.path.exists(seg_folder):
                raise ValueError('{0} path does not exist'.format(seg_folder))
            else:
                segment_dirs.append(seg_folder)
                #print(segment_list)

        segfiles_dict={}

        for seg_folder,seg in zip(segment_dirs,segment_list):
            fglob = '{0}/*.gz'.format(seg_folder)
            filepaths = glob.glob(fglob)
            if filepaths:
                filepaths_df = pd.DataFrame([x.split('_') for x in filepaths],columns=['yy','mm','dd'])
                filepaths_df['filepath'] = filepaths
                # strip path from yy
                filepaths_df['yy']=filepaths_df['yy'].str.split('/').str[-1]
                # strip ext from dd
                filepaths_df['dd']=filepaths_df['dd'].str[:2]
                #print(filepaths_df)
                #        filepaths_df['date']= filepaths_df.apply(lambda x:datetime.strptime("{0} {1} {2}".format(x['yy'], x['mm'], x['dd']), "%Y %m %d"),axis=1)
                filepaths_df['date']= filepaths_df.apply(lambda x:datetime.strptime("{0} {1} {2}".format(x['yy'], x['mm'], x['dd']), "%Y %m %d"),axis=1)

                #filepaths_df.index= filepaths_df['date']
                filepaths_df.drop(['yy','mm','dd'],axis=1,inplace=True)

                # now select the files within the date range only
                if date_from is None:
                    date_from =filepaths_df.date.min()
                if date_to is None:
                    date_to =filepaths_df.date.max()

                min_day = min(days_list)
                max_day = max(days_list)

                first_day = util.next_weekday(date_from, min_day) # 0 = Monday, 1=Tuesday, 2=Wednesday...
                last_day = util.next_weekday(date_to,max_day,next=False)

                filepaths_df = filepaths_df[ (filepaths_df.date >= first_day) & (filepaths_df.date <= last_day) ]

                segfiles_dict[seg]=filepaths_df

            else:
                raise ValueError('No data files at {0}'.format(seg_folder))

        #print(segfiles_dict)

        col_names=['dt']+col_list

        column_names = CalTrans.df_pp_agg_col_names
        column_dtypes = CalTrans.df_pp_agg_col_dtypes

        col_idx=[column_names.index(i) for i in col_names]

        #print(col_names)
        #print(col_idx)

        col_dtypes = dict([(column_names[i],column_dtypes[i] ) for i in col_idx])

        self.col_names = col_names
        segdata_dict={}
        for seg,filepaths_df in segfiles_dict.items():
            dflist=[]
            for _,datafile in filepaths_df.iterrows():
                df = pd.read_csv(datafile['filepath'], header=None, usecols = col_idx, parse_dates=[0], infer_datetime_format=True, names = col_names, dtype = col_dtypes)
                dflist.append(df)
                #print(len(dflist))
            df = pd.concat(dflist)
            #        df['dt'] = pd.to_datetime(df.dt)
            #        df['speed']=pd.to_numeric(df.speed)
            #        df = df.set_index(['dt'])
            df_counts=df.count()
            df_rows = float(df.shape[0])
            df_missing = 1.0 - (df_counts/df_rows)
            if max(df_missing) > 0.3:
                print('warning: segment {0} not added as it had >30% missing values'.format(seg))
                self.segment_list.remove(seg)
            else:
                df.set_index(['dt'],inplace=True)
                df = df.resample('5T').ffill()   # this also fills the NA Values
                #add week of the day
                df.loc[:,'dow']=np.float32(df.index.dayofweek)
                #add minute of the day
                df.loc[:,'mod']=np.float32(((df.index.hour * 60) + df.index.minute)/agg_period)

                segdata_dict[seg]=df

        self.segdata_dict = segdata_dict

        return self.segdata_dict
