# images are stored in
#  NCHW (cuDNN default)
# Transformation available for NHW and NHWC (TensorFlow default)

import future, builtins, past, six
from builtins import super

from .utils import imutil

try: #py3
    from urllib.parse import urlparse
    from urllib import request
except: #py2
    from urlparse import urlparse
    from six.moves.urllib import request
from io import BytesIO

from PIL import Image

import matplotlib.pyplot as plt

from . import util
from .dataset import Dataset
from .utils import nputil
import numpy as np
import cv2

class ImagesDataset(Dataset):
    def __init__(self):
        super().__init__()
        self.height=0
        self.width=0
        self.depth=0
        self.x_layout = imutil.LAYOUT_NP
        self.x_layout_file = imutil.LAYOUT_NHWC
        self.x_is_images = False

    @property
    def cv2_imread(self):
        if self.depth==0:
            return cv2.IMREAD_UNCHANGED
        elif self.depth==1:
            return cv2.IMREAD_GRAYSCALE
        elif self.depth==3:
            return cv2.IMREAD_COLOR
        else:
            raise Exception('Depth is set to {}, hence cant return cv2_imread'.format(self.depth))

    @property
    def x_layout(self):
        return self._x_layout

    @x_layout.setter
    def x_layout(self, x_layout):
        self._x_layout=x_layout

    def scale(self,x,xmin=0,xmax=255,min=0,max=1):
        assert (xmax-xmin) > 0, 'max and min can not be same'
        a = (max-min) / (xmax - xmin)
        return a * (x.astype(np.float32)-xmin) + min

    def scaleX(self, min=0, max=255):
        for x in self.X_list:
            self.part[x] = self.scale(self.part[x])


    def load_image(self,in_image):
        """ Load an image, returns PIL.Image. """
        # if the path appears to be an URL
        if urlparse(in_image).scheme in ('http', 'https',):
            # set up the byte stream
            img_stream = BytesIO(request.urlopen(in_image).read())
            # and read in as PIL image
            img = Image.open(img_stream)
        else:
            # else use it as local file path
            img = Image.open(in_image)
        return img

    def resize_image(self,in_image:Image, new_width, new_height, crop_or_pad=True):
        """ Resize an image.
        Arguments:
            in_image: `PIL.Image`. The image to resize.
            new_width: `int`. The image new width.
            new_height: `int`. The image new height.
            crop_or_pad: Whether to resize as per tensorflow's function
        Returns:
            `PIL.Image`. The resize image.
        """
        #img = in_image.copy()
        img = in_image

        if crop_or_pad:
            half_width = img.size[0] // 2
            half_height = img.size[1] // 2

            half_new_width = new_width // 2
            half_new_height = new_height // 2

            img = img.crop((half_width-half_new_width,
                            half_height-half_new_height,
                            half_width+half_new_width,
                            half_height+half_new_height
                            ))

        #img.size[1]=int(img.size[1])
        #img.size[0]=int(img.size[0])
        #print(img.size)

        img = img.resize(size=(new_width, new_height))

        return img

    def pil_to_nparray(self,pil_image:Image):
        """ Convert a PIL.Image to numpy array. """
        pil_image.load()
        return np.asarray(pil_image, dtype=np.float32)

    def next_batch(self, part='train', return_images=True):
        if self.x_is_images:
            return_images = True

        x_batch, y_batch = super().next_batch(part=part)

        if (not self.x_is_images) and return_images:
            x_batch = self.load_images(x_batch)
        # else just return the filenames
        return x_batch, y_batch

    def load_images(self, files):
        images = np.array([cv2.imread(i, self.cv2_imread) for i in files])
        if self.x_layout==imutil.LAYOUT_NP:
            images = nputil.image_nhwc2np(images, self.height, self.width, self.depth)
        else:
            images = nputil.image_layout(images,self.x_layout_file, self.x_layout)
        return images