import numpy as np

_EPSILON = 1e-7

def image_layout(x, old, new):
    if old!=new:
        new = [old.index(char) for char in new]
        return np.transpose(x,new)
    else:
        return x

def image_np2nhwc(x,h,w,c):
    return np.reshape(x,[-1,h,w,c])

def image_nhwc2np(x, h, w, c):
    return np.reshape(x,[-1,h*w*c])

def onehot(y, n_classes=0):
    if n_classes<2:
        n_classes = np.max(y)+1
    assert n_classes>1, 'Number of classes can not be less than 2'
    return np.eye(n_classes)[y]

def argmax(x):
    return np.argmax(x,axis=1)

# unit_axis =1 means one column and unit_axis = 0 means one row
def to2d(x,unit_axis=1):
    if unit_axis==1: # one column
        col = 1
        row = -1
    else:
        col = -1
        row = 1
    return np.reshape(x,[row,col])


def smape(x, x_hat):
    diff = np.abs(((x - x_hat) * 2) / np.clip(np.abs(x + x_hat),
                                              _EPSILON,
                                              None)
                  )
    return 100. * np.mean(diff)

def mse(x, x_hat):
    return np.mean((x_hat - x) ** 2)


def mae(x, x_hat):
    return np.mean(np.abs(x_hat - x))


def mape(x, x_hat):
    diff = np.abs((x - x_hat) / np.clip(np.abs(x),
                                        _EPSILON,
                                        None))
    return 100. * np.mean(diff)