import numpy as np
from numpy import int32, float32, inf, append
from math_utils import euclidean
from h5py import File
from pathlib import Path
from logging import info

# insert
#   resize to +1
#   key = max() + 1
#   insert to last
# remove
#   swap deletable index with last index
#   resize to -1
# query
#   go trough all records, return best key, index and value


class H5DB:
    __dataset_name = "arrays"
    __database_name = "data.h5"
    __chunk_size = 10_000

    def __init__(self, data_path, threshold=0.85):
        self.threshold = 1 - threshold
        self.data_path = Path(data_path) / self.__database_name
        info(f"making h5py to {self.data_path.absolute()}")
        self._init_dataset()

    def _init_dataset(self):

        with File(self.data_path, 'a') as hf:
            try:
                hf.create_dataset(name=self.__dataset_name,
                                  shape=(0, 257),
                                  dtype=int32,
                                  chunks=(self.__chunk_size, 257),
                                  maxshape=(None, 257))
            except ValueError:
                pass

    def append(self, array, key):
        with File(self.data_path, 'a') as hf:
            dataset = hf[self.__dataset_name]

            array = append(array * 1000, key).astype(int32)
            array = array.reshape((1, 257))
            dataset.resize((dataset.shape[0] + 1), axis=0)
            dataset[-1:] = array

    def remove(self, index):
        with File(self.data_path, 'a') as hf:
            try:
                dataset = hf[self.__dataset_name]
                key = dataset[index, -1]
                dataset[index] = dataset[-1]
                dataset.resize((dataset.shape[0] - 1), axis=0)
                return key
            except IndexError:
                return None

    def query(self, array):
        best_match = [None, None, inf]
        with File(self.data_path, 'r') as hf:
            dataset = hf[self.__dataset_name]
            if dataset.shape[0] == 0:
                return best_match

            for ind, chunk in enumerate(dataset.iter_chunks()):
                chunk = dataset[chunk]
                data, keys = (chunk[:,:-1] / 1000).astype(float32), chunk[:,-1]
                e = euclidean(data, array)

                arg_min = e.argmin()
                val_min = e[arg_min]

                if best_match[-1] > val_min < self.threshold:
                    index = int((self.__chunk_size * ind) + arg_min)
                    best_match[:] = int(keys[arg_min]), index, val_min

        return best_match

    def index_query(self, key):
        with File(self.data_path, 'r') as hf:
            dataset = hf[self.__dataset_name]
            if dataset.shape[0] == 0:
                return None

            for ind, chunk in enumerate(dataset.iter_chunks()):
                keys = dataset[chunk][:,-1]
                best_ind = np.equal(keys, key).argmax()
                best_val = keys[best_ind]
                if best_val == key:
                    index = int((self.__chunk_size * ind) + best_ind)
                    return index


