from pathlib import Path
import numpy as np
from database.h5_db import H5DB
from database.sqlite_db import SqliteDB
from database.keyholder import KeyHolder
from logging import info
from communication import ResponseObject, DEFAULT_IMAGE
from cv2.cv2 import imwrite, imread
from uuid import uuid1
from os import remove


class _EuclideanDistDB:
    def __init__(self, data_path, threshold=0.85):
        self.root_path = self.ensure_file_struct(data_path)

        self.data_path = self.root_path / "databases"
        self.data_path.mkdir(parents=True, exist_ok=True)

        info(f"making sqlite to {self.data_path.absolute()}")
        self.sqlite_db = SqliteDB(self.data_path)
        info(f"making h5py to {self.data_path.absolute()}")
        self.h5_db = H5DB(self.data_path, threshold)
        self.key_holder = KeyHolder(self.h5_db.data_path)

    @staticmethod
    def ensure_file_struct(path=None):
        try:
            path = Path(path)
            assert path.is_dir()
        except (TypeError, AssertionError):
            path = Path(".") / "data"

        for folder in ("databases",  "images"):
            dbs_path = path / folder
            Path(dbs_path).mkdir(parents=True, exist_ok=True)
        return path.absolute()

    def make_response(self, sqlite_resp=None, euc=None):
        res = ResponseObject()
        res.credentials = str(uuid1())
        if sqlite_resp is not None:
            res.unique_id,\
            res.name,\
            res.searches,\
            res.image,\
            res.added,\
            res.last_query = sqlite_resp
            res.confidence = f"{(1 - euc) * 100:.3f}%" if euc else None
        res.image = self.read_sample(res.image)
        return res

    @staticmethod
    def to_str_key(key):
        return str(key).zfill(8)

    def key_to_image_path(self, key):
        key = self.to_str_key(key)
        return f"{key}.png"

    def write_sample(self, sample, sample_path):
        path = self.root_path / "images" / sample_path
        imwrite(str(path), sample)

    def read_sample(self, sample_path=DEFAULT_IMAGE):
        if sample_path == DEFAULT_IMAGE:
            path = sample_path
        else:
            path = self.root_path / "images" / sample_path
        return imread(str(path))

    def delete_sample(self, sample_path):
        path = self.root_path / "images" / sample_path
        remove(path)

    def query(self, array):
        if not self.pre_operation_check(array):
            return self.make_response()

        key, index, val = self.h5_db.query(array)
        if key is not None:
            key = self.to_str_key(key)
            sqlite_resp = self.sqlite_db.read(key)
            return self.make_response(sqlite_resp, val)
        return self.make_response(None)

    def insert(self, array, name, sample_img):
        if not self.pre_operation_check(array):
            return self.make_response()

        key, index, val = self.h5_db.query(array)
        if key is None:
            int_key = next(self.key_holder)
            self.h5_db.append(array, int_key)
            str_key = self.to_str_key(int_key)
            sample_path = self.key_to_image_path(str_key)
            self.write_sample(sample_img, sample_path)
            sqlite_resp = self.sqlite_db.write(name, str_key, sample_path)
            return self.make_response(sqlite_resp)
        return self.make_response(None)

    def remove(self, key):

        int_key = int(key)
        str_key = self.to_str_key(key)

        index = self.h5_db.index_query(int_key)
        if index is not None:
            int_key = self.h5_db.remove(index)
            self.key_holder.add_unused(int_key)
            sqlite_resp = self.sqlite_db.remove(str_key)
            sample_path = self.key_to_image_path(str_key)
            response = self.make_response(sqlite_resp)
            self.delete_sample(sample_path)
            return response
        return self.make_response(None)

    @staticmethod
    def pre_operation_check(x):
        if type(x) is np.ndarray:
            # shape compatible with database
            if x.size == 256:
                return True
        return False



