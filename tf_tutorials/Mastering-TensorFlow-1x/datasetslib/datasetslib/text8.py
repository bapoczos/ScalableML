import os
import zipfile
import tensorflow as tf


from . import datasets_root
from .text import TextDataset
from . import util

class Text8(TextDataset):
    def __init__(self):
        TextDataset.__init__(self)
        self.dataset_name='text8'
        self.source_url='http://mattmahoney.net/dc/'
        self.source_files=['text8.zip']
        self.dataset_home=os.path.join(datasets_root,self.dataset_name)

    def load_data(self, force=False, clip_at=0):
        self.downloaded_files=util.download_dataset(source_url=self.source_url,
                                                    source_files=self.source_files,
                                                    dest_dir = self.dataset_home,
                                                    force=force,
                                                    extract=False)

        with zipfile.ZipFile(os.path.join(self.dataset_home,self.downloaded_files[0])) as archfile:
            text = tf.compat.as_str(archfile.read(archfile.namelist()[0])).split()
            if clip_at > 0:
                text = text[:clip_at]
            word2id = self.build_word2id(text)

            self.part['train'] = self.build_text2id(text,word2id)

            self.part['valid'] = None #self.build_file2id(f,word2id)

            self.part['test'] = None #self.build_file2id(f,word2id)

            self.vocab_len = len(word2id)
            self.id2word = self.build_id2word(word2id)
        return self.part['train'], self.part['valid'], self.part['test']
