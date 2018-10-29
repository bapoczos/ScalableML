import os
import tarfile
import numpy as np


from . import datasets_root
from .text import TextDataset
from . import util

class PTBSimple(TextDataset):
    def __init__(self):
        TextDataset.__init__(self)
        self.dataset_name='ptb-simple'
        self.source_url='http://www.fit.vutbr.cz/~imikolov/rnnlm/'
        self.source_files=['simple-examples.tgz']
        self.dataset_home=os.path.join(datasets_root,self.dataset_name)

    def load_data(self,force=False):
        self.downloaded_files=util.download_dataset(source_url=self.source_url,
                                                    source_files=self.source_files,
                                                    dest_dir = self.dataset_home,
                                                    force=force,
                                                    extract=False)

        trainfile ='./simple-examples/data/ptb.train.txt'
        validfile = './simple-examples/data/ptb.valid.txt'
        testfile = './simple-examples/data/ptb.test.txt'

        with tarfile.open(os.path.join(self.dataset_home,self.downloaded_files[0])) as archfile:
            f = archfile.extractfile(trainfile)
            word2id = self.build_word2id(self.read_words(f))

            f.seek(0)
            self.part['train'] = self.build_file2id(f,word2id)

            f = archfile.extractfile(validfile)
            self.part['valid'] = self.build_file2id(f,word2id)

            f = archfile.extractfile(testfile)
            self.part['test'] = self.build_file2id(f,word2id)

            self.vocab_len = len(word2id)
            self.id2word = self.build_id2word(word2id)
        return self.part['train'], self.part['valid'], self.part['test']