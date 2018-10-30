import urllib
import os

from .images import ImagesDataset
from . import datasets_root
from . import util

class imageNet(ImagesDataset):
    def __init__(self):
        ImagesDataset.__init__(self)
        self.dataset_name='imagenet'
        #self.source_url='http://cs231n.stanford.edu/'
        #self.source_files=['coco-animals.zip']
        self.dataset_home=os.path.join(datasets_root,self.dataset_name)

        self.x_shape = 'NCHW' ## other alternates are NHW and NHCW


    def load_data(self,n_classes=1000):
        assert n_classes in (1000,1001)
        self.n_classes = n_classes

        id2label = self.build_id2label()
        self.id2label=id2label

    def build_id2label(self):
        base_url = 'https://raw.githubusercontent.com/tensorflow/models/master/research/inception/inception/data/'
        synset_url = '{}/imagenet_lsvrc_2015_synsets.txt'.format(base_url)
        synset_to_human_url = '{}/imagenet_metadata.txt'.format(base_url)

        filename, _ = urllib.request.urlretrieve(synset_url)
        synset_list = [s.strip() for s in open(filename).readlines()]
        num_synsets_in_ilsvrc = len(synset_list)
        assert num_synsets_in_ilsvrc == 1000

        filename, _ = urllib.request.urlretrieve(synset_to_human_url)
        synset_to_human_list = open(filename).readlines()
        num_synsets_in_all_imagenet = len(synset_to_human_list)
        assert num_synsets_in_all_imagenet == 21842

    #    synset_to_human = {}
    #    for s in synset_to_human_list:
    #        parts = s.strip().split('\t')
    #        assert len(parts) == 2
    #        synset = parts[0]
    #        human = parts[1]
    #        synset_to_human[synset] = human

    #    label_index = 1
    #    id2name = {0: 'background'}
    #    for synset in synset_list:
    #        name = synset_to_human[synset]
    #        id2name[label_index] = name
    #        label_index += 1

        synset2name = {}
        for s in synset_to_human_list:
            parts = s.strip().split('\t')
            assert len(parts) == 2
            synset = parts[0]
            name = parts[1]
            synset2name[synset] = name

        if self.n_classes == 1001:
            id2label={0:'empty'}
            id=1
        else:
            id2label = {}
            id=0

        for synset in synset_list:
            label = synset2name[synset]
            id2label[id] = label
            id += 1

        return id2label