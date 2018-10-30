import base

source_url = 'http://commondatastorage.googleapis.com/books1000/'
dataset_name = 'not-mnist'
dataset_dir = dataset_root + dataset_name

def load_data():
    train_filename = base.maybe_download('notMNIST_large.tar.gz',dataset_dir,source_url)
    test_filename = base.maybe_download('notMNIST_small.tar.gz',dataset_dir,source_url)
    train_folders = maybe_extract(train_filename)
    test_folders = maybe_extract(test_filename)