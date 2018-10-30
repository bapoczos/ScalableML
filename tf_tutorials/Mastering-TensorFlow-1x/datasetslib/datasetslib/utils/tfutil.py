import tensorflow as tf

def image_layout(x, old, new):
    new = [old.index(char) for char in new]
    return tf.transpose(x,new)

def onehot(y, n_classes):
    return tf.one_hot(y,n_classes)

def argmax(x):
    return tf.argmax(x,axis=1)