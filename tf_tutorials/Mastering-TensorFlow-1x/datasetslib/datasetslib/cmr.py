import os
import tarfile
import numpy as np
import string
from nltk.corpus import stopwords

from . import datasets_root
from .text import TextDataset
from . import util

class CornellMovieReviews(TextDataset):
    def __init__(self):
        TextDataset.__init__(self)
        self.dataset_name='cornell-movie-reviews'
        self.source_url='http://www.cs.cornell.edu/people/pabo/movie-review-data'
        self.source_files=['rt-polaritydata.tar.gz']
        self.dataset_home=os.path.join(datasets_root,self.dataset_name)

    def load_data(self,force=False):
        self.downloaded_files=util.download_dataset(source_url=self.source_url,
                                                    source_files=self.source_files,
                                                    dest_dir = self.dataset_home,
                                                    force=force,
                                                    extract=False)

        posfile ='./rt-polaritydata/rt-polarity.pos'
        negfile = './rt-polaritydata/rt-polarity.neg'

        positive_reviews = []
        negative_reviews = []

        with tarfile.open(self.downloaded_files[0]) as archfile:

            f = archfile.extractfile(posfile)
            for line in f:
                positive_reviews.append(line.decode('ISO-8859-1').encode('ascii',errors='ignore').decode())

            f = archfile.extractfile(negfile)
            for line in f:
                negative_reviews.append(line.decode('ISO-8859-1').encode('ascii',errors='ignore').decode())

            reviews = positive_reviews + negative_reviews
            sentiment = [1] * len(positive_reviews) + [0] * len(negative_reviews)


            # clean up reviews
            reviews = [x.lower() for x in reviews] # convert all to lower case
            reviews = [''.join(c for c in x if c not in string.punctuation) for x in reviews]
            reviews = [''.join(c for c in x if c not in '0123456789') for x in reviews]
            stops = stopwords.words('english')
            reviews = [' '.join([word for word in x.split() if word not in (stops)]) for x in reviews]
            reviews = [' '.join(x.split()) for x in reviews] # trim white space
            reviews = [x for x in reviews if len(x.split()) > 2] # remove reviews less than 3 words
            sentiment = [sentiment[ix] for ix, x in enumerate(reviews) if len(x.split()) > 2]

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