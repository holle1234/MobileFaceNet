import h5py
from pathlib import Path


class KeyHolder:
    """
    Returns keys in ascending order from 0 to infinity
    Returns previously used keys first if any are available
    """

    def __init__(self, h5py_path):
        self.data_path = Path(h5py_path)
        self.missing_keys = []
        self.it_value = 0
        self._init_iterator()

    def add_unused(self, index):
        self.missing_keys.append(index)

    def _init_iterator(self):
        if self.data_path.exists():
            with h5py.File(self.data_path, 'r') as hf:
                data = hf["arrays"][:,-1]
                try:
                    self.it_value = data.max()
                    self.missing_keys = self._find_missing_keys(data)
                except ValueError:
                    pass

    def _find_missing_keys(self, data):
        missing = []
        for i in range(1, self.it_value):
            if i not in data:
                missing.append(i)
        return missing[::-1]

    def __iter__(self):
        return self

    def __next__(self):
        if self.missing_keys:
            return int(self.missing_keys.pop())
        else:
            ret = self.it_value
            self.it_value += 1
            return ret