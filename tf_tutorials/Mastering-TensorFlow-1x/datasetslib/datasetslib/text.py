from .dataset import Dataset
from . import util
from . import nputil


import collections
import numpy as np

class TextDataset(Dataset):
    def __init__(self):
        Dataset.__init__(self)
        self.skip_window=1     # [ skip_window target skip_window ]
        self.vocab_len = 0
        self.id2word = {}

    def read_words(self, filehandle):
        #with tf.gfile.GFile(filename, "r") as f:
        #with open(filename,'r') as f:
            return filehandle.read().decode("utf-8").replace("\n", "<eos>").split()

    def save_word2id(self, filename):
        with open(filename,'w') as vfile:
            vfile.write('word\tid\n')
            for k,v in self.id2word.items():
                vfile.write('{0:}\t{1:}\n'.format(v,k))

    def build_word2id(self, text):
        #data = self._read_words(filehandle)

        counter = collections.Counter(text)
        count_pairs = sorted(counter.items(), key=lambda x: (-x[1], x[0]))

        words, _ = list(zip(*count_pairs))
        word2id = dict(zip(words, range(len(words))))

        return word2id

    def build_text2id(self, text, word2id):
        return np.array([word2id[word] for word in text if word in word2id])

    def build_file2id(self, filehandle, word2id):
        text = self.read_words(filehandle)
        return self.build_text2id(text,word2id)

    def build_id2word(self, word2id):
        id2word = dict(zip(word2id.values(), word2id.keys()))
        return id2word

    def n_batches_seq(self, n_tx = 5, n_ty = 5):
        n_ts = n_tx + n_ty
        n_possible_seq = self.vocab_len - n_ts + 1
        n_batches = n_possible_seq // self.batch_size
        if n_possible_seq % self.batch_size > 0:
            n_batches += 1
        return n_batches

    def n_batches_wv(self):
        skip2 = self.skip_window * 2
        span = skip2 + 1
        return ((self.vocab_len - skip2) * skip2) // self.batch_size

    # returns input series : {t-n_tx,...,t}, output series : {t+1,...,t+1+n_ty}
    def seq_to_xy(self, seq=None, n_tx = 5, n_ty = 5 ):
        #convert seq to x and y
        if seq is None:
            seq = self.part['train']
        ts = nputil.to2d(seq)  # let us make it a time series with each time step as row

        ts_rows = ts.shape[0]
        n_rows = ts_rows - n_tx - n_ty + 1

        dataX=np.empty(shape=[n_rows, n_tx], dtype=np.int)
        dataY=np.empty(shape=[n_rows, n_ty], dtype=np.int)

        x_idx = range(0,1)
        y_idx = range(0,1)

        # input sequence x (t-n_tx, ... t)
        from_col = 0
        for i in range(n_tx, 0, -1):
            dataX[:,from_col:from_col+1]= util.shift(ts[:,x_idx],i)[n_tx:n_rows+n_tx]
            from_col = from_col+1

        # forecast sequence (t+h, ... t+h+n_ty)
        from_col = 0
        for i in range(0, n_ty):
            #y_cols.append(shift(ts,-i))
            dataY[:,from_col:from_col+1]= util.shift(ts[:,y_idx],-(i-1))[n_tx:n_rows+n_tx]
            from_col = from_col + 1

        return dataX, dataY

    def next_batch_seq(self, part='train', n_tx = 5, n_ty = 5, shuffle=True):
        sliding_window = 1
        n_ts = n_tx + n_ty
        span = self.batch_size + n_ts - 1 # assuming each batch item is sliding window of 1
        seq = np.empty(shape=[span], dtype=np)
        size = len(self.part[part])

        assert size > span

        idx = self.index[part]

        if idx + span >= size:
            part_batches = (size - idx) // n_ts
            part_span = part_batches * n_ts
            seq[:part_span] = self.part[part][idx:idx+part_span]
            rest_span = span - part_span
            seq[part_span:span]=self.part[part][:rest_span]
        else:
            seq[:span] = self.part[part][idx:idx+span]

        if (idx == size-span):
            self.reset_index(part)  # restart from beginning if finished
        else:
            self.index[part] += sliding_window

        # now convert seq to x and y

        dataX, dataY = self.seq_to_xy(seq=seq,n_tx=n_tx,n_ty=n_ty)

        return dataX, dataY

    def next_batch_sg(self, part='train', shuffle=True):
        skip2 = self.skip_window * 2
        assert self.batch_size % skip2 == 0
        span = skip2 + 1
        assert len(self.part[part]) > span
        target = np.ndarray(shape=[self.batch_size], dtype=np.int32)
        context = np.ndarray(shape=[self.batch_size], dtype=np.int32)

        for i in range(self.batch_size // skip2):
            if self.index[part] + span >= len(self.part[part]):
                self.reset_index(part)  # restart from beginning if finished
            for j in range(self.skip_window):
                target[i * skip2 + j]=self.part[part][self.index[part] + self.skip_window]
                context[i * skip2 + j]=self.part[part][self.index[part] + j]
                target[i * skip2 + (j+self.skip_window)]=self.part[part][self.index[part] + self.skip_window]
                context[i * skip2 + (j+self.skip_window)]=self.part[part][self.index[part] + self.skip_window + 1 + j]
            self.index[part] += 1
        return target,context

    def next_batch_cbow(self, part='train', shuffle=True):
        skip2 = self.skip_window * 2
        assert self.batch_size % skip2 == 0
        span = skip2 + 1
        assert len(self.part[part]) > span
        target = np.ndarray(shape=[self.batch_size], dtype=np.int32)
        context = np.ndarray(shape=[self.batch_size,skip2], dtype=np.int32)

        for i in range(self.batch_size):
            if self.index[part] + span >= len(self.part[part]):
                self.reset_index(part)  # restart from beginning if finished
            target[i]=self.part[part][self.index[part] + self.skip_window]
            for j in range(self.skip_window):
                context[i, j]=self.part[part][self.index[part] + j]
                context[i, (j+self.skip_window)]=self.part[part][self.index[part] + self.skip_window + 1 + j]
            self.index[part] += 1
        return target,context
