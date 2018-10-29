import os
import gzip
import tarfile
from . import nputil

import numpy as np

from .images import ImagesDataset
from . import dsroot
from . import util
from . import images
from .utils import imutil
from .utils import nputil
try:
    # Python 2
    from itertools import izip
except ImportError:
    # Python 3
    izip = zip
#from scipy.misc import imsave
import cv2

class MNIST(ImagesDataset):

    def __init__(self):
        super().__init__()
        self.dataset_name='mnist'
        self.source_url='http://yann.lecun.com/exdb/mnist/'
        self.source_files=['train-images-idx3-ubyte.gz',
                           'train-labels-idx1-ubyte.gz',
                           't10k-images-idx3-ubyte.gz',
                           't10k-labels-idx1-ubyte.gz']
        self.dataset_home=os.path.join(dsroot,self.dataset_name)

        self.height=28
        self.width=28
        self.depth=1

        self.x_layout =  imutil.LAYOUT_NHW
        self.x_layout_file = imutil.LAYOUT_NHW

        self.n_features = self.height * self.width * self.depth
        self.n_classes = 10

    def load_data(self,force=False, shuffle=True, x_is_images=False, x_layout = None):

        n_train = 60000
        n_test = 10000
        if x_layout is not None:
            self.x_layout = x_layout

        self.downloaded_files=util.download_dataset(source_url=self.source_url,
                                                    source_files=self.source_files,
                                                    dest_dir = self.dataset_home,
                                                    force=force,
                                                    extract=False)

        modified_files = False
        print('Extracting and rearchiving as jpg files...')

        for x in ['train','test']:
            tt_folder = os.path.join(self.dataset_home,x)
            if not os.path.isdir(tt_folder):
                os.makedirs(tt_folder)
            for i in range(self.n_classes):
                class_folder = os.path.join(tt_folder,str(i))
                if not os.path.isdir(class_folder):
                    os.makedirs(class_folder)

            print(os.path.join(self.dataset_home,self.downloaded_files[0]))

            # Extract it into np arrays.
            if x=='train':
                data = self.read_data(filename=os.path.join(self.dataset_home,self.downloaded_files[0]),
                                           num=n_train
                                           )
                labels = self.read_labels(filename=os.path.join(self.dataset_home,self.downloaded_files[1]),
                                               num=n_train
                                               )
            else:
                data = self.read_data(filename=os.path.join(self.dataset_home,self.downloaded_files[2]),
                                      num=n_test
                                      )
                labels = self.read_labels(filename=os.path.join(self.dataset_home,self.downloaded_files[3]),
                                      num=n_test
                                          )
            print('Saving ', x)
            for i in range(len(data)):
                image_path = os.path.join(tt_folder,str(labels[i]),'{}.jpg'.format(i))
                if not os.path.isfile(image_path):
                    cv2.imwrite(image_path, data[i][:,:,0])
                    modified_files = True

            if modified_files:
                print('Zipping ', x)
                with tarfile.open(os.path.join(self.dataset_home,'mnist.tar.gz'), 'w:gz') as tar:
                    tar.add(tt_folder,arcname=x)
            else:
                print('Zip file not modified')

        print('Loading in x and y... start')
        x_train_files=[]
        y_train = []
        x_test_files=[]
        y_test=[]
        #print(ilabels)
        n_train_per_class = n_train // self.n_classes
        n_test_per_class = n_test // self.n_classes

        for i in range(self.n_classes):
            label = str(i)
            ifolder = os.path.join(self.dataset_home,'train',label)
            #print(os.listdir(ifolder))
            files = [name for name in os.listdir(ifolder) if name.endswith('.jpg')]
            for f in files:
                x_train_files.append(os.path.join(ifolder,f))
                y_train.append(i)

            #y_train[i * n_train_per_class: (i+1) * n_train_per_class] = i

            ifolder = os.path.join(self.dataset_home,'test',label)
            files = [name for name in os.listdir(ifolder) if name.endswith('.jpg')]
            for f in files:
                x_test_files.append(os.path.join(ifolder,f))
                y_test.append(i)

            #y_test[i * n_test_per_class: (i+1) * n_test_per_class] = i


        if shuffle:
            x_train_files, y_train = self.shuffle_xy(x_train_files,y_train)

        if x_is_images:
            x_train = self.load_images(x_train_files)
            x_test = self.load_images(x_test_files)
        else:
            x_train = x_train_files
            x_test = x_test_files
        self.x_is_images=x_is_images

        # no need to make onehot here as next batch returns as onehot
        y_train = np.asarray(y_train)
        y_test = np.asarray(y_test)

        self.part['X_train']=x_train
        self.part['Y_train']=y_train

        self.part['X_test']=x_test
        self.part['Y_test']=y_test

        print('Loading in x and y... done')
        return x_train,y_train,x_test,y_test

    def read_data(self,filename, num):
        """Extract the #num images into a 4D tensor [image index, y, x, channels].
        Values are rescaled from [0, 255] down to [-0.5, 0.5].
        """
        print('Reading from ', filename)
        with gzip.open(filename) as bytestream:
            bytestream.read(16)
            buf = bytestream.read(self.height * self.width * num)
            data = np.frombuffer(buf, dtype=np.uint8).astype(np.float32)
            #data = (data - (PIXEL_DEPTH / 2.0)) / PIXEL_DEPTH
            data = data.reshape(num, self.height * self.width, 1)
            return data


    def read_labels(self, filename, num):
        """Extract the labels into a vector of int64 label IDs."""
        print('Reading from ', filename)
        with gzip.open(filename) as bytestream:
            bytestream.read(8)
            buf = bytestream.read(1 * num)
            labels = np.frombuffer(buf, dtype=np.uint8).astype(np.uint8)
        return labels


