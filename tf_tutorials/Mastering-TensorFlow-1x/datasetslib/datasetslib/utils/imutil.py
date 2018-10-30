from __future__ import division

from matplotlib import pyplot as plt
from . import nputil
import numpy as np

LAYOUT_NP = 'np'  #  n images of p pixes each
LAYOUT_NHW = 'nhw'
LAYOUT_NHWC = 'nhwc'
LAYOUT_NCHW = 'nchw'

#TODO doesnt work with odd number of subplots

def display_images(images, labels=None, n_cols=8):
    if labels is not None and labels.ndim>1:
        labels=nputil.argmax(labels)
    if images.ndim == 4 and images.shape[3]==1:
        images = np.reshape(images,images.shape[0:3])
    n_rows = -(-len(images) // n_cols)  # double minus is for upside down floor division to get ceiling division
    for i in range(len(images)):
        plt.subplot(n_rows, n_cols, i + 1)
        if labels is not None:
            plt.title(labels[i])
        plt.imshow(images[i])
        plt.axis('off')
    plt.tight_layout()
    plt.show()