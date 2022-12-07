from numpy import ndarray, float32
from numpy import sum, sqrt, square
from numpy.linalg import norm


def preprocess_images(images: ndarray):
    images = images.astype(float32)
    images /= 127.5
    images -= 1.
    return images

def normalized_sum_array(arrays):
    pointer = sum(arrays, 0).reshape((1, 256))
    normalized = pointer / norm(pointer, axis=-1).reshape(-1, 1)
    return normalized

def euclidean(p1, p2):
    return sum(square(p1 - p2), axis=-1) / 2.0
