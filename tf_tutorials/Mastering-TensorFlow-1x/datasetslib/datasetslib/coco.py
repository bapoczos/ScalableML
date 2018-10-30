import os
import six
import imageio
from PIL import Image
import numpy as np

from .images import ImagesDataset
from . import datasets_root
from . import util
from .utils import nputil
from .utils import imutil


try:
    # Python 2
    from itertools import izip
except ImportError:
    # Python 3
    izip = zip

from tensorflow.contrib.slim.nets import inception, vgg

class coco_animals(ImagesDataset):
    def __init__(self):
        ImagesDataset.__init__(self)
        self.dataset_name='coco-animals'
        self.source_url='http://cs231n.stanford.edu/'
        self.source_files=['coco-animals.zip']
        self.dataset_home=os.path.join(datasets_root,self.dataset_name)
        self.height=None
        self.width=None
        self.depth=None

        self.x_layout =  imutil.LAYOUT_NCHW
        self.x_layout_file = imutil.LAYOUT_NCHW

        #self.x_shape = 'NCHW' ## other alternates are NHW and NHCW
        self.n_classes = 8

    def load_data(self,force=False, shuffle=True, x_is_images=False):
        self.dataset_home=os.path.join(datasets_root,self.dataset_name)

        self.downloaded_files=util.download_dataset(source_url=self.source_url,
                                                    source_files=self.source_files,
                                                    dest_dir = self.dataset_home,
                                                    force=force,
                                                    extract=True)

        # the archive contains the name of the coco-animals folder, hence this temporary fix for now
        self.dataset_home=os.path.join(self.dataset_home,self.dataset_name)
#        print('Extracting ',self.downloaded_files[0])
        ilabels = os.listdir(os.path.join(self.dataset_home,'train'))

        label2id = dict(zip(ilabels, range(len(ilabels))))
        #print(label2id)

        self.label2id=label2id
        id2label = dict(zip(label2id.values(), label2id.keys()))
        self.id2label = id2label

        n_train = 800
        n_valid = 200

        x_train_files=[]
        y_train = np.zeros((n_train,), dtype=np.uint8)
        x_valid_files=[]
        y_valid=np.zeros((n_valid,), dtype=np.uint8)
        #print(ilabels)

        for i in range(self.n_classes):
            label = id2label[i]
            ifolder = os.path.join(self.dataset_home,'train',label)
            #print(os.listdir(ifolder))
            files = [name for name in os.listdir(ifolder) if name.endswith('.jpg')]
            for f in files:
                x_train_files.append(os.path.join(ifolder,f))
                #y_train.append(labels2id[label])
            y_train[i * (n_train // self.n_classes): (i+1) * (n_train // self.n_classes)] = i

            ifolder = os.path.join(self.dataset_home,'val',label)
            files = [name for name in os.listdir(ifolder) if name.endswith('.jpg')]
            for f in files:
                x_valid_files.append(os.path.join(ifolder,f))
                #y_val.append(labels2id[label])
            y_valid[i * (n_valid // self.n_classes): (i+1) * (n_valid // self.n_classes)] = i


        if shuffle:
            x_train_files, y_train = self.shuffle_xy(x_train_files,y_train)

        if x_is_images:
            x_train = self.load_images(x_train_files)
            x_valid = self.load_images(x_valid_files)
        else:
            x_train = x_train_files
            x_valid = x_train_files
        self.x_is_images=x_is_images


        self.part['X_train']=x_train
        self.part['Y_train']=y_train

        self.part['X_valid']=x_valid
        self.part['Y_valid']=y_valid

        return x_train, y_train, x_valid, y_valid

    def preprocess_for_vgg(self,incoming):
        if isinstance(incoming, six.string_types):
            img = self.load_image(incoming)
        elif isinstance(incoming, imageio.core.util.Image ):
            img = Image.fromarray(incoming)
        else: #
            img=incoming

        #print(type(img))

        img_size = vgg.vgg_16.default_image_size

        height = img_size
        width = img_size

        img = self.resize_image(img,height,width)
        img = self.pil_to_nparray(img)
        if len(img.shape)==2:   # greyscale or no channels then add three channels
            h=img.shape[0]
            w=img.shape[1]
            img = np.dstack([img]*3)

        means = np.array([[[123.68, 116.78, 103.94]]]) #shape=[1, 1, 3]
        try:
            img = img - means
        except Exception as ex:
            print('Error preprocessing ',incoming)
            print(ex)

        return img

    def preprocess_for_inception(self,incoming):

        img_size = inception.inception_v3.default_image_size

        height = img_size
        width = img_size

        if isinstance(incoming, six.string_types):
            img = self.load_image(incoming)
        elif isinstance(incoming, imageio.core.util.Image ):
            img = Image.fromarray(incoming)
        else: #
            img=incoming

        #print(type(img))

        img = self.resize_image(img,height,width)
        img = self.pil_to_nparray(img)
        if len(img.shape)==2:   # greyscale or no channels then add three channels
            h=img.shape[0]
            w=img.shape[1]
            img = np.dstack([img]*3)

        img = ((img/255.0) - 0.5) * 2.0

        return img
