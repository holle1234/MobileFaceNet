from .naive_nns import _EuclideanDistDB
from communication import ResponseObject
from numpy import ndarray


class DataBase(_EuclideanDistDB):
    def __init__(self, data_path, threshold=0.85):
        """
        Database for handling face ids
        Accepts numpy arrays of size (1, 256)
        Arrays should be l2-normalized for database to work as intended!
        Can Handle only one array at a time

        :param data_path: data path where databases and samples should be stored
        :param threshold: threshold over which samples are considered to be a match.
                ranges 0.0-1.0 and represents a percentile of normalized euclidean distance
        """
        super(DataBase, self).__init__(data_path, threshold)

    def query(self, array:ndarray) -> ResponseObject:
        """
        Performs a single query to the database
        :param array: l2 normalized input array of shape (1, 256)
        :return: returns a ResponseObject with match data
        """
        return super(DataBase, self).query(array)

    def remove(self, unique_id:int) -> ResponseObject:
        """
        Performs a single record removal request to the database
        :param unique_id: unique key returned by query method
        :return: returns a ResponseObject with data corresponding to the unique_id
        """
        return super(DataBase, self).remove(unique_id)

    def insert(self, array:int, name:str, sample_img:ndarray) -> ResponseObject:
        """
        Performs a single insertion to the database
        Queries database and does insertion if there are no matches within threshold
        :param array: l2 normalized input array of shape (1, 256)
        :param name: name of a person
        :param sample_img: sample image
        :return: returns a ResponseObject with inserted data to the database
        """
        return super(DataBase, self).insert(array, name, sample_img)
